from universal_clipboard.management.commands.cmd_handler_base.msg_process_cmd_base import MsgProcessCommandBase

__author__ = 'weijia'


import json

# # from background_task.tasks import tasks, autodiscover
from iconizer.iconizer_consts import ICONIZER_SERVICE_NAME
from obj_sys.models_ufs_obj import UfsObj


class GitMsgHandler(MsgProcessCommandBase):
    def register_to_service(self):
        clipboard_receive_channel_name = "clipboard_to_django"
        channel = self.ufs_msg_service.create_channel(clipboard_receive_channel_name)
        self.ufs_msg_service.send_to(ICONIZER_SERVICE_NAME, {"command": "register_to_clipboard",
                                                     "target": channel.get_channel_full_name()})
        return channel

    # noinspection PyMethodMayBeStatic
    def process_msg(self, msg):
        clipboard_msg = {"msg_type": "clipboard", "data": msg}
        UfsObj.objects.get_or_create(description_json=json.dumps(clipboard_msg["data"]), ufs_obj_type=3)


Command = GitMsgHandler