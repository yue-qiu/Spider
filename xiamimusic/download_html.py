import requests
import chardet
from random import choice

def download(url):
    """
    下载html文档
    :return: html
    """
    Agent_list = [
        "Mozilla/5.0(window NT 10.0;WOW64) ApplWebKit/537.36(KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2107.204 Safari/537.36",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)"]
    header = {"User-Agent":choice(Agent_list)}
    try:
        res = requests.get(url,headers=header,timeout=30)
    except:
        res = requests.get(url, headers=header, timeout=30)
    res.encoding = chardet.detect(res.content)["encoding"]
    return res.text