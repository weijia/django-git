import traceback
import urllib2
import urlparse


class ConnectivityManager(object):
    cache = {}

    # def __init__(self):
    #     super(ConnectivityManager, self).__init__()
    #     self.cache = {}

    def is_connectable(self, url):
        # server_url = self.get_server(url)
        server_url = url
        if (server_url in self.cache) and (self.cache[server_url] == True):
            return self.cache[server_url]
        else:
            proxy = urllib2.ProxyHandler({})
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)
            try:
                response = urllib2.urlopen(server_url, timeout=20)
                self.cache[server_url] = True
                return True
            except Exception, e:
                pass
            self.cache[url] = False
            return False

