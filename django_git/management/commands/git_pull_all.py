import traceback
from UserDict import UserDict

import time

import thread

from iconizer.gui_client.notification_service_client import NotificationServiceClient
from iconizer.msg_service.msg_service_interface.msg_service_factory_interface import MsgServiceFactory
from tagging.models import Tag
from tagging.models import TaggedItem
from iconizer.iconizer_consts import ICONIZER_SERVICE_NAME
from iconizer.msg_service.msg_def.file_url_list_msg import FileUrlListMsg
from obj_sys.obj_tagging import get_or_create_objects_from_remote_or_local_url, append_tags_and_description_to_url
from universal_clipboard.management.commands.cmd_handler_base.msg_process_cmd_base import MsgProcessCommandBase
from django_git.management.commands.git_pull_utils.puller import Puller


def get_full_path_from_url(url):
    return url.replace("file:///", "")


def tag_enumerator(tag_name="git"):
    while True:
        tag = Tag.objects.get(name=tag_name)
        tagged_item_list = TaggedItem.objects.filter(tag__exact=tag.pk)
        for tagged_item in tagged_item_list:
            obj_tag = tagged_item.tag.name
            obj = tagged_item.object
            if obj is None:
                continue
            path = obj.full_path
            print "processing:", path
            p = Puller(path, NotificationServiceClient().notify)
            try:
                p.pull_all()
            except:
                traceback.print_exc()
                print "Pull error for: %s" % path
            print "auto pull and push done"
        time.sleep(60*5)


class GitMsgHandler(MsgProcessCommandBase):
    def register_to_service(self):
        channel = self.get_channel("git_puller")
        reg_msg = UserDict({"command": "DropWndV2", "tip": "GIT test", "target": channel.get_channel_full_name()})
        self.ufs_msg_service.send_to(ICONIZER_SERVICE_NAME, reg_msg.data)
        thread.start_new_thread(tag_enumerator, ())
        return channel

    # noinspection PyMethodMayBeStatic
    def process_msg(self, msg):
        file_msg = FileUrlListMsg(msg)
        file_url_list = file_msg.get_file_url_list()
        for url in file_url_list:
            # path = msg["path"]
            # path will be in file://xxxxx format
            append_tags_and_description_to_url(self.admin_user, url, "git", "GIT repository")
            path = get_full_path_from_url(url)
            print "processing:", path
            p = Puller(path, NotificationServiceClient().notify)
            try:
                p.pull_all()
                print "pull and push done"
            except:
                pass
                print "error when pull and push"


Command = GitMsgHandler
