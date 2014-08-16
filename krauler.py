import gevent
from gevent import monkey
monkey.patch_all()  # get HTTP working
monkey.patch_thread()
from gevent.queue import Queue



import argparse
import requests
import re

import os
import sys


class Krauler:
    def __init__(self, threadcount=4, chunksize=1024, chan='krautchan'):

        self.threadcount = threadcount
        self.threads = []
        self.chunksize = chunksize
        self.tasks = Queue()
        self.dir = ''
        self.fetchedFiles = 0
        self.totalFiles = 0
        self.chan = chan

        self.urls = {'krautchan':['http://krautchan.net/%s/thread-%s.html',
                                 'http://krautchan.net/download/%s/%s',
                                 r'href="/download/(?P<file>.*?)/(?P<name>.*?)"'],
                     '4chan':['http://boards.4chan.org/%s/thread/%s',
                              'http://i.4cdn.org/%s/%s',
                              r'File: <a href="//i.4cdn.org/(?P<board>.*?)/(?P<file>.*?)"']}

        self.regex = re.compile(self.urls[chan][2])


    def fetch(self, pid):

        while not self.tasks.empty():
            task = self.tasks.get_nowait()

            url = self.urls[self.chan][1] % (task[0], task[1])
            with open(self.dir+task[1],'wb') as img:
                res = requests.get(url, stream=True)
                if not res.ok:
                    print('[-] Failed getting File :/')
                for block in res.iter_content(1024):
                    if not block:
                        break
                    img.write(block)
                self.fetchedFiles += 1

                sys.stdout.write('\r')
                sys.stdout.write('[.] %3i/%3i [%-25s] %25s...' % (self.fetchedFiles, self.totalFiles, int((float(self.fetchedFiles)/self.totalFiles)*25)*'=', task[1][:25]))
                sys.stdout.flush()

        return



    def parse(self, board, thread):
        url = self.urls[self.chan][0] % (board, thread)
        print('[ ] Fetching "%s"' % url)
        data = requests.get(url)
        matches = self.regex.findall(data.text)

        return matches

    def run(self, board, thread):

        self.dir = '%s-%s/' % (board, thread)
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

        matches = self.parse(board, thread)
        self.totalFiles = len(matches)

        print('[+] Found %i Files' % self.totalFiles)


        for m in matches:
            self.tasks.put_nowait(m)

        for i in range(self.threadcount):
            self.threads.append(gevent.spawn(self.fetch, i))
        gevent.joinall(self.threads)
        print('\n[+] Done :3')



if __name__ == '__main__':

    arg = argparse.ArgumentParser()
    arg.add_argument('-b', required=True, dest='board', action='store', help='Board name e.g. "s","b",...')
    arg.add_argument('-t', required=True, dest='thread', action='store', help='Thread ID')
    arg.add_argument('-c', required=True, dest='chan', action='store', help='Chan mode "krautchan"/"4chan" ')

    args = vars(arg.parse_args())

    k = Krauler(chan=args['chan'])
    k.run(args['board'], args['thread'])

