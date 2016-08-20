import logging
import os
import re
import urlparse
from subprocess import PIPE
import traceback
import git

from django_git.management.commands.git_pull_utils.connectivity_manager import ConnectivityManager
from djangoautoconf.local_key_manager import get_local_key
from ufs_tools.app_framework import find_app_in_folders
from ufs_tools.short_decorator.ignore_exception import ignore_exc

log = logging.getLogger(__name__)


class RemoteRepo(object):
    def __init__(self, remote_repo):
        self.remote_repo = remote_repo
        self.sync_msg = None

    @staticmethod
    def get_ref_name(ref):
        return ref.name.split('/')[-1]

    def sync_all_remote_branches(self, branch):
        for remote_ref in self.remote_repo.refs:
            log.info("remote ref: %s" % remote_ref)  # origin/master
            self.pull_and_push_changes(branch, remote_ref, self.remote_repo)

    def pull(self, remote_branch_name):
        print('pulling changes: %s' % remote_branch_name)
        # Added istream to avoid error: WindowsError: [Error 6] The handle is invalid
        try:
            self.remote_repo.pull(remote_branch_name, istream=PIPE)
        except AssertionError:
            log.error('assert error may be caused by inconsistent log format between git and gitpython')
        except git.GitCommandError, e:
            log.error("%s: GitCommandError: %s" % (self.remote_repo.url, str(e)))
        except Exception, e:
            traceback.print_exc()

    def push(self, branch, remote_ref):
        log.info('pushing changes')
        try:
            self.remote_repo.push(remote_ref.__str__().split('/')[-1],
                                  istream=PIPE)
        except Exception, e:
            traceback.print_exc()

    def pull_and_push_changes(self, branch, remote_ref):
        # print remote_ref#gitbucket/20130313_diagram_rewrite
        if branch.name in self.get_ref_name(remote_ref):
            old_commit_hexsha = branch.commit.hexsha
            log.info('remote commit: %s, %s' % (remote_ref.commit, remote_ref.commit.message))
            self.pull(self.get_ref_name(remote_ref))

            if branch.commit.hexsha != old_commit_hexsha:
                msg = '%s: new code pulled: %s' % (self.remote_repo.url, branch.commit.message)
                self.report_result(msg)

            if branch.commit.hexsha != remote_ref.commit.hexsha:
                log.info('different to remote')
                log.info('latest remote log: %s' % unicode(remote_ref.commit.message))
                self.push(branch, remote_ref)

                if branch.commit.hexsha == remote_ref.commit.hexsha:
                    msg = '%s sync done. Latest local log: %s' % (self.remote_repo.url, branch.commit.message)
                    self.report_result(msg)
                else:
                    msg = '%s sync failed.' % remote_ref.repo.working_dir

    def report_result(self, message):
        log.info(message)
        self.sync_msg = message


class GitSynchronizer(object):
    def __init__(self, full_path, callback=None):
        self.full_path = full_path
        self.https_proxy_server = get_local_key("proxy_setting.https_proxy_server", "django_git")
        self.connectivity_manager = ConnectivityManager()
        self.sync_msg = None
        self.call_back = callback

    def pull_all_branches(self):
        r = git.Repo(self.full_path)
        print "processing: ", self.full_path
        local_active_branch = r.active_branch
        log.info('current branch: %s, %s' % (local_active_branch.name, local_active_branch.commit))

        for remote_repo in r.remotes:
            log.info("remote repo: %s" % unicode(remote_repo))
            if self.is_proxy_needed(remote_repo):
                self.set_proxy_env()
            else:
                self.unset_proxy_env()
            self.process_remote_repo(local_active_branch, remote_repo)

    def process_remote_repo(self, branch, remote_repo):
        if self.is_valid_url(remote_repo.url) and (not self.is_ignored(remote_repo.url)):
            if self.is_repo_ref_valid(remote_repo):
                for remote_ref in remote_repo.refs:
                    log.info("remote branch:" + unicode(remote_ref).encode('utf8', 'replace'))
                    # self.pull_and_push_changes(branch, remote_branch, remote_repo)
                    pulling_repo = RemoteRepo(remote_repo)
                    pulling_repo.pull_and_push_changes(branch, remote_ref)
                    sync_message = pulling_repo.sync_msg
                    self.show_notification(sync_message)
        else:
            log.error("No valid pulling_repo url, repo is not synchronized")

    @ignore_exc
    def show_notification(self, sync_message):
        if (not (self.call_back is None)) and (not (sync_message is None)):
            self.call_back(u"%s: %s" % (self.full_path, sync_message))

    # noinspection PyMethodMayBeStatic
    def get_server(self, url):
        r = urlparse.urlparse(url)
        return "%s://%s" % (r.scheme, r.hostname)

    def is_proxy_needed(self, repo):
        server_url = self.get_server(repo.url)
        return not self.connectivity_manager.is_connectable(server_url)

    def set_proxy_env(self):
        os.environ["https_proxy"] = self.https_proxy_server

    @staticmethod
    def unset_proxy_env():
        try:
            del os.environ["https_proxy"]
        except:
            pass

    @staticmethod
    def is_repo_ref_valid(remote_repo):
        # if hasattr(i, "refs"):
        #     print 'no refs attr'
        # print "length:", len(i.refs)
        is_ref_valid = True
        try:
            len(remote_repo.refs)
        except AssertionError, e:
            import traceback
            traceback.print_exc()
            print remote_repo
            is_ref_valid = False
        return is_ref_valid

    @staticmethod
    def is_ignored(url):
        # if "https" in url:
        #     print 'ignoring :', url
        #     return True
        # else:
        #    return False
        return False

    @staticmethod
    def is_valid_url(url):
        if re.match("http(s)*://.+:.+@.+$", url) is None:
            return False
        return True


try:
    from repo import proj_list, git_path
except:
    repo = []
    git_path = 'C:\\Program Files (x86)\\Git\\bin'
    git_path = 'C:\\Users\\weijia\\AppData\\Local\\Programs\\Git\\bin'


def add_git_to_path():
    folders = get_local_key("git_path.git_folder", "django_git")
    folders.append('C:\\Program Files (x86)\\Git\\bin')
    os.environ['PATH'] += ";"+find_app_in_folders(folders, "git.exe")
    # print os.environ['PATH']


add_git_to_path()


def main():
    for path in proj_list:
        print "processing:", path
        p = GitSynchronizer(path)
        p.pull_all_branches()


if __name__ == '__main__':
    add_git_to_path()
    main()
