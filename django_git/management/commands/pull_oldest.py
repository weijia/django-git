from django.utils import timezone

from django_git.management.commands.git_pull_all import pull_and_notify_user
from django_git.management.commands.git_pull_utils.git_folder_enum import enum_git_repo
from djangoautoconf.cmd_handler_base.msg_process_cmd_base import DjangoCmdBase


class GitPullOnce(DjangoCmdBase):
    git_tag_name = "git"

    def msg_loop(self):
        for repo in enum_git_repo():
            pull_and_notify_user(repo.full_path)
            repo.last_checked = timezone.now()
            repo.save()


Command = GitPullOnce
