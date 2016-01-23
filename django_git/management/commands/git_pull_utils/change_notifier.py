import threading
import os
import sys
import datetime
import time
import traceback
import win32file
import win32con
import cPickle
from stat import ST_SIZE

from iconizer.logsys.logSys import info

ACTIONS = {
    1: "Created",
    2: "Deleted",
    3: "Updated",
    4: "Renamed from something",
    5: "Renamed to something"
}


# Reference: http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
class ChangeNotifier(threading.Thread):
    def __init__(self, full_path):
        self.need_to_quit = False
        self.path_to_watch = full_path
        super(ChangeNotifier, self).__init__()

    def run(self):
        # threads_init()
        self.path_to_watch = os.path.abspath(self.path_to_watch)
        info("Watching %s at %s\n" % (self.path_to_watch, time.asctime()))
        self.notification_msg_loop()

    def notification_msg_loop(self):
        hDir = win32file.CreateFile(
            self.path_to_watch,
            win32con.GENERIC_READ,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS,
            None
        )
        cnt = 0
        while not self.need_to_quit:
            #            print "new watch\n"
            try:
                results = self.read_changes(hDir)
            except:
                # print "Read %s(%d) failed" % (self.path_to_watch, hDir)
                # continue
                raise
            if not self.need_to_quit:
                for action, file in results:
                    # full_filename = os.path.join (self.path_to_watch, file)
                    # print full_filename, ACTIONS.get (action, "Unknown")
                    self.callback(self.path_to_watch, file, ACTIONS.get(action, "Unknown"))

    def read_changes(self, hDir):
        results = win32file.ReadDirectoryChangesW(
            hDir,
            4096,
            True,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME
            | win32con.FILE_NOTIFY_CHANGE_DIR_NAME
            | win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES
            | win32con.FILE_NOTIFY_CHANGE_SIZE
            | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE
            | win32con.FILE_NOTIFY_CHANGE_SECURITY,
            None,
            None
        )
        return results

    def callback(self, path_to_watch, relative_path, action):
        pass

    def exit(self):
        self.need_to_quit = True
