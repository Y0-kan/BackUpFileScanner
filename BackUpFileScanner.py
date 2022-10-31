# -*- coding: UTF-8 -*-
from hurry.filesize import size
from fake_headers import Headers
from urllib.parse import urlparse
import requests
import logging
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
import time

requests.packages.urllib3.disable_warnings()

def dicts(url,fileDicts2):

    suffix = ['.zip','.rar','.tar.gz','.tgz','.tar.bz2','.tar','.jar','.war','.7z','.bak','.sql','.gz','.sql.gz','.tar.tgz']
    link =['-','_']
    prefix = ['1','127.0.0.1','admin','auth','back','backup','backups','bak','bin','code','database','data','users','db','dump','engine','error_log','test','htdocs','wz','files','home','html','index','local','localhost','master','new','old','orders','site','sql','store','beifen','wangzhan','web','website','temp','wp','www','wwwroot','root','log','temp']
    year = ['2015','2016','2017','2018','2019','2020','2021','2022']
    month = ['01','02','03','04','05','06','07','08','09','10','11','12']

    prefix2 = []

#解析一下url，将域名等关键字 加入到prefix2,用来生成社工字典，也可以在prefix2列表中自行补充一些关键字。
    netloc = urlparse(url).netloc
    prefix2.append(netloc)   #www.baidu.com   1.1.1.1

    l = netloc.split('.')
    flag =True  #判断是ip还是域名
    for i in l:
        if i.isdigit() and 0<=int(i)<=255:
            continue
        else:
            flag=False
            break
    if not flag:
        prefix2.append(l[1])     #baidu
        l.pop(0)
        prefix2.append('.'.join(l))     #baidu.com

    #print(prefix2)

    '''
#生成通用字典，生成一次就好，结果已保存在 universal.txt ，可以直接调用，不需要重复生成。
# prefix+suffix prefix+year+suffix prefix+year+month+suffix prefix+link+year+suffix
# year+suffix   year+month+suffix
    
    fileDicts=[]
    
    for m in month:
        for y in year:
            for s in suffix:
                fileDicts.extend([y + m + s])

    for y in year:
        for s in suffix:
            fileDicts.extend([y + s])

    for p in prefix:
        for s in suffix:
            fileDicts.extend([p + s])

    for p in prefix:
        for y in year:
            for s in suffix:
                fileDicts.extend([p + y + s])

    for p in prefix:
        for l in link:
            for y in year:
                for s in suffix:
                    fileDicts.extend([p + l + y + s])

    f = open("universal.txt","w")
    for s in fileDicts:
        f.writelines(s+'\n')
    f.close()
    '''
    #生成社工字典

    for p in prefix2:
        for s in suffix:
            fileDicts2.extend([p + s])

    for p in prefix2:
        for y in year:
            for s in suffix:
                fileDicts2.extend([p + y + s])

    for p in prefix2:
        for l in link:
            for y in year:
                for s in suffix:
                    fileDicts2.extend([p + l + y + s])

    wtxt = 'special_'+prefix2[0]+'.txt'
    f = open(wtxt,"w")
    for s in fileDicts2:
        f.writelines(s+'\n')
    f.close()


def BKFScan(url,flag,max_threads):
    fileDicts2=[]
    dicts(url,fileDicts2)
    #print(fileDicts2)
    if not flag:
        l=[]
        p = ThreadPoolExecutor(max_threads)
        for route in fileDicts2:
            urltarget = url+'/'+route
            #print(urltarget)
            obj = p.submit(FinalScan, urltarget)
            l.append(obj)

        for s in open("universal.txt", "r"):
            route = s.rstrip('\n')
            urltarget = url + '/' + route
            obj = p.submit(FinalScan, urltarget)
            l.append(obj)

        p.shutdown()

def FinalScan(urltarget):
    try:
        r = requests.get(url=urltarget, headers=header.generate(), timeout=timeout, allow_redirects=False, stream=True,
                         verify=False)
        if (r.status_code == 200) & ('html' not in r.headers.get('Content-Type')) & (
                'xml' not in r.headers.get('Content-Type')) & ('text' not in r.headers.get('Content-Type')) & (
                'json' not in r.headers.get('Content-Type')) & ('javascript' not in r.headers.get('Content-Type')):
            tmp_rarsize = int(r.headers.get('Content-Length'))
            rarsize = str(size(tmp_rarsize))
            if (int(rarsize[0:-1]) > 0):
                logging.warning('[ success ] {}  size:{}'.format(urltarget, rarsize))
                with open(outputfile, 'a') as f:
                    try:
                        f.write(str(urltarget) + '  ' + 'size:' + str(rarsize) + '\n')
                    except:
                        pass
            else:
                logging.warning('[ fail ] {}'.format(urltarget))
        else:
            logging.warning('[ fail ] {}'.format(urltarget))
    except Exception as e:
        logging.warning('[ fail ] {}'.format(urltarget))

if __name__ == '__main__':
    usageexample = '\n       Example: python3 BackUpFileScanner.py -t 10 -f url.txt -o result.txt\n'
    usageexample += '                '
    usageexample += 'python3 BackUpFileScanner.py -u https://www.example.com/ -o result.txt'

    parser = ArgumentParser(add_help=True, usage=usageexample, description='A Website Backup File Leak Scan Tool.')
    parser.add_argument('-f', '--url-file', dest="url_file", help="Example: url.txt")
    parser.add_argument('-t', '--thread', dest="max_threads", nargs='?', type=int, default=5, help="how many threads? default 5")
    parser.add_argument('-u', '--url', dest='url', nargs='?', type=str, help="Example: http://www.example.com/anything")
    parser.add_argument('-n', '--no-scan', dest='n', type=bool, default=0 ,help="no scan,just generate dicts,default 0")
    #parser.add_argument('-d', '--dict-file', dest='dict_file', nargs='?', help="Example: dict.txt")
    parser.add_argument('-o', '--output-file', dest="output_file", help="Example: result.txt")

    args = parser.parse_args()

    header = Headers(
        # generate any browser & os headeers
        headers=False  # don`t generate misc headers
    )

    timeout = 10

    global outputfile

    if (args.output_file):
        outputfile = args.output_file
    else:
        outputfile = 'result.txt'

    start=time.time()

    try:
        if args.url:
            BKFScan(url=args.url,flag=args.n,max_threads=args.max_threads)
            #BKFScan(url=args.url, max_thread=args.max_threads, dic=info_dic)
        elif args.url_file:
            for line in open(args.url_file, "r"):
                url = line.rstrip('\n')
                BKFScan(url,flag=args.n,max_threads=args.max_threads)
        else:
            print("[!] Please specify a URL or URL file name")
    except Exception as e:
        print(e)

    stop=time.time()
    print(stop-start)
