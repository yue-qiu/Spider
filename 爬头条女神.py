import requests
from bs4 import BeautifulSoup
from random import choice
from time import sleep
import os
import re
from random import random
import chardet
import pickle
from multiprocessing import Pool

url = "https://www.aitaotu.com/tag/siwa.html"
Agent_list = [ "Mozilla/5.0(window NT 10.0;WOW64) ApplWebKit/537.36(KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2107.204 Safari/537.36",
         "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)"]
header = {"User-Agent":choice(Agent_list)}

"""*******开始抓取页面上的写真*********"""
try:
    get_web = requests.get(url,headers=header,timeout=30)
except:
    get_web = requests.get(url, headers=header, timeout=30)
get_web.encoding = chardet.detect(get_web.content)["encoding"]
web_soup = BeautifulSoup(get_web.text,"lxml")
i = 0 #统计图片张数

def Getpictures(num):
    url_AISS = re.search(r'https://www.aitaotu.com/tag/\w+',url).group() + "/" + str(num) + ".html"
    try:
        get_AISS_web = requests.get(url_AISS, headers={"User-Agent":choice(Agent_list)},timeout=30)
    except:
        get_AISS_web = requests.get(url_AISS, headers={"User-Agent":choice(Agent_list)},timeout=30)
    sleep(random())
    get_AISS_web.encoding = "utf-8"
    web_soup2 = BeautifulSoup(get_AISS_web.text, "lxml")
    get_pictures_a = web_soup2.find("div",attrs={"id":"mainbody"}).find_all("a",attrs={"class":"Pli-litpic"})
    for get_picture_a in get_pictures_a:
        titles = get_picture_a.get("title")
        title = re.search(r'[^(\[丽柜\])].+',titles).group() #获得写真名
        picture_url = get_picture_a.get("href")
        pictures_url = "https://www.aitaotu.com" + picture_url
        header = {"User-Agent": choice(Agent_list)}
        try:
            get_picture = requests.get(pictures_url,headers=header,timeou=30) #进入一组写真
        except:
            get_picture = requests.get(pictures_url,headers=header,timeout=30)
        sleep(random())
        get_picture.encoding = "utf-8"
        pictures_soup = BeautifulSoup(get_picture.text,"lxml")
        max_url = pictures_soup.find("div",attrs={"class":"pages"}).find_all("a")[-1].get("href")
        k = re.search(r'_\d+',max_url).group()
        max_pages = int(re.search(r'\d+',k).group()) #获取最大页数
        if os.path.isdir(os.path.join("E:\丽柜", title)):  # 判断文件夹是否存在
            print(title + " have existed!")
            pass
        else:
            os.makedirs(os.path.join("E:\丽柜", title))
            print("creat a document called " + title)
        for page in range(1,max_pages+1): #获取该写真的每一页中的图片
            pictures_page_url = "https://www.aitaotu.com" + picture_url[:-5] + "_" + str(page) + ".html"
            try:
                get_jpg = requests.get(pictures_page_url,headers=header,timeout=30)
            except:
                get_jpg = requests.get(pictures_page_url,headers=header,timeout=30)
            sleep(random())
            jpg_soup = BeautifulSoup(get_jpg.text,"lxml")
            jpg_urls = jpg_soup.find("div",attrs={"class":"big-pic"}).find("div",attrs={"id":"big-pic"}).find_all("img")
            for jpg_url in jpg_urls:#获取图片src
                jpg_url = jpg_url["src"]
                try:
                    jpg = requests.get(jpg_url,timeout=30)
                except:
                    jpg = requests.get(jpg_url,timeout=30)
                sleep(random())
                name = jpg_url[-6:]
                os.chdir("E:\丽柜\\" + title)
                global i
                if os.path.isfile(name): #判断图片是否存在
                    print(name + " have exited!")
                    i += 1
                else:
                    with open(name,"ab") as f:
                        i += 1
                        f.write(jpg.content)
                        print(name + " saved!This is the " + str(i) +" pages!The process id is %s" % os.getpid())

def Get_pictures_pages(start_page,end_page):
    """获得头条的总页数"""
    for num in range(start_page,end_page+1):
        Getpictures(num)
        page = {"page" : num}
        with open("E:\\Beautyleg_page.txt","w") as fp:
            pickle.dump(page,fp)

def main():
    """
    用pool开多进程
    利用range的进步值对总页数每4页进行一个分组，每个进程下载4页的图片
    :return:
    """
    p = Pool()
    all_pages_url = web_soup.find("div",attrs={"id":"pageNum"}).find_all("a",href=re.compile(r'.+'))[-1].get("href")
    all_pages = re.search(r'/\d+',all_pages_url)
    all_page = re.search(r'\d+',all_pages.group())
    max_AISS_pages = int(all_page.group())
    pages_list = list(range(1,max_AISS_pages+1))
    for i in range(0,len(pages_list),4):
        pages = pages_list[i:i+4]
        p.apply_async(Get_pictures_pages,(pages[0],pages[-1]))
    p.close()
    p.join()
    print("ok!")

if __name__ == '__main__':
    main()