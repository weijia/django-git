import traceback
import urllib2
import urlparse


class ConnectivityManager(object):
    def __init__(self):
        super(ConnectivityManager, self).__init__()
        self.cache = {}

    def get_server(self, url):
        r = urlparse.urlparse(url)
        return "%s://%s" % (r.scheme, r.hostname)

    def is_connectable(self, url):
        if url in self.cache:
            return self.cache[url]
        else:
            try:
                server_url = self.get_server(url)
                proxy = urllib2.ProxyHandler({})
                opener = urllib2.build_opener(proxy)
                urllib2.install_opener(opener)
                response = urllib2.urlopen(server_url, timeout=20)
                self.cache[url] = True
                return True
            except Exception, e:
                traceback.print_exc()
            self.cache[url] = False
            return False

