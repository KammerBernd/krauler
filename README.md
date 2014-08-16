Krauler
=======

Krauler is a simple thread dumper to crawl all file links in a given thread on imageboards like krautchan.net or 4chan.org.

Krauler writes all files to a folder named in this scheme <board>-<threadID>.

##Usage
```sh
usage: krauler.py [-h] -b BOARD -t THREAD -c CHAN
```

## Example

```sh
python krauler.py -b gif -t 6440654 -c 4chan
[ ] Fetching "http://boards.4chan.org/gif/thread/6440654"
[+] Found 3 Files
[.]   3/  3 [=========================]        1408207479362.webm...
[+] Done :3
```
## Needed libs

* argparse
* gevent
* requests
