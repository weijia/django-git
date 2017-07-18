from django_git.management.commands.git_pull_utils.git_folder_enum import enum_git_repo
from django_git.management.commands.git_pull_utils.multiple_repo_updater import pull_all_in_enumerable

from djangoautoconf.cmd_handler_base.msg_process_cmd_base import DjangoCmdBase


class GitPullOnce(DjangoCmdBase):
    git_tag_name = "git"

    def msg_loop(self):
        enum_method = enum_git_repo
        pull_all_in_enumerable(enum_method)


Command = GitPullOnce
