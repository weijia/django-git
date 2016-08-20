import os
import traceback

from django.utils import timezone

from django_git.management.commands.git_pull_utils.git_folder_enum import enum_git_repo
from django_git.management.commands.git_pull_utils.git_synchronizer import GitSynchronizer
from djangoautoconf.cmd_handler_base.msg_process_cmd_base import DjangoCmdBase
from iconizer.gui_client.notification_service_client import NotificationServiceClient


class GitPullOnce(DjangoCmdBase):
    git_tag_name = "git"

    def msg_loop(self):
        for repo in enum_git_repo():
            if os.path.exists(repo.full_path):
                p = GitSynchronizer(repo.full_path, NotificationServiceClient().notify)
                success = False
                try:
                    p.pull_all_branches()
                    print "pull and push done", p.sync_msg
                    success = True
                except:
                    traceback.print_exc()
                    print "Pull error for: %s" % repo.full_path
                repo.last_checked = timezone.now()
                repo.is_last_pull_success = success
                repo.save()


Command = GitPullOnce
