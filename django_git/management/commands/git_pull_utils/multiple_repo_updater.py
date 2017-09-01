import os
import traceback
from django.utils import timezone
from django_git.management.commands.git_pull_utils.git_synchronizer import GitSynchronizer


def no_action(msg):
    pass


try:
    from iconizer.gui_client.notification_service_client import NotificationServiceClient
    notification_method = NotificationServiceClient().notify
except:
    notification_method = no_action


def pull_all_in_enumerable(enum_method):
    for repo in enum_method():
        if os.path.exists(repo.full_path):
            p = GitSynchronizer(repo.full_path, notification_method())
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
