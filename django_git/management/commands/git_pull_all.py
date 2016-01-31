import os
import traceback
from Queue import Queue
from UserDict import UserDict
import time
import thread
import datetime
from django_git.management.commands.git_pull_utils.change_notifier import ChangeNotifier
from iconizer.gui_client.notification_service_client import NotificationServiceClient
from libtool import format_path
from tagging.models import Tag
from tagging.models import TaggedItem
from iconizer.iconizer_consts import ICONIZER_SERVICE_NAME
from iconizer.msg_service.msg_def.file_url_list_msg import FileUrlListMsg, DelayedMsg, DropEventMsg, \
    TagEnumeratorMsg, FolderChangeNotification, send_delayed_msg
from obj_sys.obj_tagging import append_tags_and_description_to_url
from universal_clipboard.management.commands.cmd_handler_base.msg_process_cmd_base import MsgProcessCommandBase
from django_git.management.commands.git_pull_utils.puller import Puller


def get_full_path_from_url(url):
    return url.replace("file:///", "")


def tag_enumerator(channel, tag_name="git"):
    while True:
        tag_filter = Tag.objects.filter(name=tag_name)
        if tag_filter.exists():
            tag = tag_filter[0]
            tagged_item_list = TaggedItem.objects.filter(tag__exact=tag.pk)
            for tagged_item in tagged_item_list:
                obj_tag = tagged_item.tag.name
                obj = tagged_item.object
                if obj is None:
                    continue
                msg = TagEnumeratorMsg()
                path = obj.full_path
                msg["path"] = path
                channel.put_msg(msg)
        time.sleep(60 * 10)


def pull_and_notify_user(path):
    print "processing:", path
    p = Puller(path, NotificationServiceClient().notify)
    try:
        p.pull_all()
        print "pull and push done"
    except:
        traceback.print_exc()
        print "Pull error for: %s" % path


class GitFolderChangeNotifier(ChangeNotifier):
    def __init__(self, full_path):
        super(GitFolderChangeNotifier, self).__init__(full_path)
        self.channel = None

    def callback(self, path_to_watch, relative_path, action):
        # super(GitFolderChangeNotifier, self).callback(path_to_watch, relative_path, action)
        msg = FolderChangeNotification()
        msg["path"] = path_to_watch
        print path_to_watch, relative_path, action
        if True:  # relative_path == "heads":
            self.channel.put_msg(msg)


# noinspection PyAbstractClass
class GitMsgHandler(MsgProcessCommandBase):
    DELAY_PULL_SECONDS = 30

    def __init__(self):
        super(GitMsgHandler, self).__init__()
        # self.pull_queue = Queue()
        # self.is_more_folder_msg_received = False
        self.path_updated = {}
        self.change_notifiers = []
        # self.watching_folders = []
        self.watching_folder_to_git_folder = {}
        self.msg_handlers = {DropEventMsg.command: self.process_drop_msg,
                             FolderChangeNotification.command: self.process_dir_change_msg,
                             DelayedMsg.command: self.process_delayed_pull,
                             TagEnumeratorMsg.command: self.register_dir_change_notification
                             }

    def register_to_service(self):
        channel = self.get_channel("git_puller")
        reg_msg = UserDict({"command": "DropWndV2", "tip": "GIT auto pull and push",
                            "target": channel.get_channel_full_name()})
        try:
            self.ufs_msg_service.send_to(ICONIZER_SERVICE_NAME, reg_msg.data)
        except:
            pass
        thread.start_new_thread(tag_enumerator, (channel,))
        return channel

    # noinspection PyMethodMayBeStatic
    def process_msg(self, msg):
        self.msg_handlers[msg["command"]](msg)

    def process_delayed_pull(self, msg):
        remove = []
        for path in self.path_updated:
            if (datetime.datetime.now() - self.path_updated[path]).seconds > self.DELAY_PULL_SECONDS:
                self.update_git(self.get_git_folder_for_changed_folder_root(path))
                remove.append(path)
        for path in remove:
            del self.path_updated[path]

    def get_git_folder_for_changed_folder_root(self, git_config_folder):
        git_folder = format_path(git_config_folder)
        return self.watching_folder_to_git_folder[git_folder]

    def process_dir_change_msg(self, msg):
        changed_path = format_path(msg["path"])
        if not (changed_path in self.path_updated):
            self.path_updated[changed_path] = datetime.datetime.now()
        # self.is_more_folder_msg_received = True
        thread.start_new_thread(send_delayed_msg, (self.get_channel(),))

    @staticmethod
    def update_git(path):
        pull_and_notify_user(path)

    def process_drop_msg(self, msg):
        file_msg = FileUrlListMsg(msg)
        file_url_list = file_msg.get_file_url_list()
        for url in file_url_list:
            # path = msg["path"]
            # path will be in file://xxxxx format
            path = get_full_path_from_url(url)
            if os.path.exists(os.path.join(path, ".git")):
                append_tags_and_description_to_url(self.admin_user, url, "git", "GIT repository")
                self.update_git(path)

    def register_dir_change_notification(self, msg):
        git_folder = msg["path"]
        if not os.path.exists(git_folder):
            return
        pull_and_notify_user(git_folder)
        print "auto pull and push done"
        git_config_folder = os.path.join(git_folder, ".git")
        if os.path.exists(git_config_folder) and not os.path.isdir(git_config_folder):
            git_config_file = open(git_config_folder, 'r')
            real_git_config_folder = git_config_file.readline().split(": ")[1].replace("\r", "").replace("\n", "")
            git_config_folder = os.path.abspath(os.path.join(git_folder, real_git_config_folder))
        git_config_folder = os.path.join(git_config_folder, "refs/heads")
        git_config_folder = format_path(git_config_folder)
        if not (git_config_folder in self.watching_folder_to_git_folder):
            change_notifier = GitFolderChangeNotifier(git_config_folder)
            change_notifier.channel = self.get_channel()
            change_notifier.start()
            self.change_notifiers.append(change_notifier)
            self.watching_folder_to_git_folder[git_config_folder] = git_folder


Command = GitMsgHandler
