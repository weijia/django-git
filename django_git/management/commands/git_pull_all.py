from UserDict import UserDict

from iconizer.iconizer_consts import ICONIZER_SERVICE_NAME
from iconizer.msg_service.msg_def.file_url_list_msg import FileUrlListMsg
from universal_clipboard.management.commands.cmd_handler_base.msg_process_cmd_base import MsgProcessCommandBase
from django_git.management.commands.git_pull_utils.puller import Puller


def get_full_path_from_url(url):
    return url.replace("file:///", "")


class GitMsgHandler(MsgProcessCommandBase):
    def register_to_service(self):
        channel = self.get_channel("git_puller")
        reg_msg = UserDict({"command": "DropWndV2", "tip": "GIT test", "target": channel.get_channel_full_name()})
        self.ufs_msg_service.send_to(ICONIZER_SERVICE_NAME, reg_msg.data)
        return channel

    # noinspection PyMethodMayBeStatic
    def process_msg(self, msg):
        file_msg = FileUrlListMsg(msg)
        file_url_list = file_msg.get_file_url_list()
        for url in file_url_list:
            # path = msg["path"]
            # path will be in file://xxxxx format
            path = get_full_path_from_url(url)
            print "processing:", path
            p = Puller(path)
            p.pull_all()


Command = GitMsgHandler
