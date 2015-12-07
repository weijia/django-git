import urllib2


class ConnectivityManager(object):
    def __init__(self):
        super(ConnectivityManager, self).__init__()
        self.cache = {}

    def is_connectable(self, url):
        if url in self.cache:
            return self.cache[url]
        else:
            try:
                response = urllib2.urlopen(url, timeout=10)
                self.cache[url] = True
                return True
            except Exception:
                pass
            self.cache[url] = False
            return False

