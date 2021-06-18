from bs4 import BeautifulSoup
import hashlib
import time
import requests
from ssl import SSLCertVerificationError
import getopt
import urllib.robotparser
from multiprocessing.pool import ThreadPool
from collections import OrderedDict
from urllib.parse import urlparse
import sys
from queue import Queue
import threading
import json

def tld(url):
    s = '.'.join(str(urlparse(url).netloc).split('.')[-2:])
    return s

class host():
    def __init__(self, url:str, pages:int, level:int):
        self.tld = tld(url)
        self.rp = urllib.robotparser.RobotFileParser()
        self.rp.set_url(f"{url}robots.txt")
        self.rp.read()
        self.q = Queue()
        self.q.put((url, level))
        self.pages = pages
        self.cache = LRUCache(1000)
        self.hashes = LRUCache(1000)

def main():
    global OUTPUT
    seedfile, OUTPUT, pgs, lvls, numthreads = getargs()
    LEVEL = int(lvls)
    PAGES = int(pgs)
    seed = []
    hosts = []

    with open(OUTPUT, "w+") as f:
        pass
    
    try:
        with open(seedfile, 'r') as f:
            seed = f.read().split('\n')
    except FileExistsError:
        print(f"{seedfile} does not exist")
        exit()

    divpages = round(PAGES/len(seed))
    dif = PAGES - divpages*len(seed)

    # distribute pages across threads
    for s in seed:
        hosts.append(host(s, divpages, LEVEL))
    
    if dif > 0:
        for h in hosts:
            h.pages += 1
            dif -= 1
            if dif == 0:
                break
    elif dif < 0:
        for i in reversed(range(len(hosts))):
            hosts[i].pages -= 1
            dif += 1
            if dif == 0:
                break
    
    pool = ThreadPool(int(numthreads))
    result = pool.map(parse, hosts)
    pool.close()
    pool.join()
    print("Done!")

def getargs():
    # returns list of command line arguments in a specific order
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hn:i:l:o:p:", ["help", "output=", "input="])
    except getopt.GetoptError as e:
        print(e)
        usage()
    ret = ['','','','','1']

    def checkint(a, arg):
        try:
            int(a)
        except ValueError:
            print(f"{arg} must be an int")
            usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            print (
                "Optional Arguments:\n"
                "-h         show help\n"
                "-n         number of threads\n"
                "\nRequired Arguments:\n"
                "-i         input seed file\n"
                "-l         number of levels\n"
                "-o         output directory\n"
                "-p         number of pages"
            )
            exit()
        elif o in ("-i", "--input"):
            ret[0] = a
        elif o in ("-o", "--output"):
            ret[1] = a
        elif o in ("-p"):
            checkint(a, "pages")
            ret[2] = a
        elif o in ("-l"):
            checkint(a, "levels")
            ret[3] = a
        elif o in ("-n"):
            checkint(a, "threads")
            ret[4] = a
        else:
            assert False, "unhandled option"
    if all(len(r) for r in ret):
        return ret
    usage()

def usage():
    print("usage: crawler.py -i <seed> -o <output> -p <pages> -l <levels>")
    exit()

def parse(h):
    global OUTPUT
    while not h.q.empty():
        h.pages -= 1
        if h.pages < 0:
            return

        # check if page url is unique
        url, level = h.q.get()
        if h.cache.has(url):
            h.pages += 1
            return
        h.cache.put(url)
        
        # download page
        try:
            html = requests.get(url).content
        except requests.exceptions.ConnectionError:
            print(f'Cannot connect to {url}')
            h.pages += 1
            return

        # check if page contents are unique
        md5 = hashlib.md5(html).digest()
        if h.hashes.has(md5):
            h.pages += 1
            return
        h.hashes.put(md5)

        # -------------DO SOMETHING--------------
        j = {"html":html.decode('utf-8')}
        with open(OUTPUT, "a+") as f:
            f.write('{"index":{}}\n')
            f.write(json.dumps(j))
            f.write('\n')
        # ---------------------------------------

        # extract urls
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            u = link.get('href')
            if u is None or u.startswith('#'):
                continue
            elif u.startswith('/'):
                o = urlparse(url)
                u = o.scheme + o.netloc + u[1:]
            if (tld(u) == h.tld 
                and level >= 0
                and h.pages > 0
                and h.rp.can_fetch("*", u)):
                h.q.put((u, level-1))
        # delay
        time.sleep(3)

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def has(self, key: int) -> int:
        if key not in self.cache:
            return False
        else:
            self.cache.move_to_end(key)
            return True

    def put(self, key: int) -> None:
        self.cache[key] = 0
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last = False)

if __name__ == '__main__':
    main()