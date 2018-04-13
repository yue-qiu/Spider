import requests
import os
from bs4 import BeautifulSoup
from random import choice
from time import sleep
import re

url = "https://www.nvshens.com/rank/sum/"
Referer	= "https://www.nvshens.com/rank/"
i = 0 #统计写真组
p = 0 #统计图数

def get_girls():
    """从网站首页中提取各个女孩的图片"""
    Agent_list = [
        "Mozilla/5.0(window NT 10.0;WOW64) ApplWebKit/537.36(KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2107.204 Safari/537.36",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)"
        ] #更换UA，简单放防反爬
    header = {"User-Agent": choice(Agent_list),
              "Referer": "https://www.nvshens.com/rank/"}
    sleep_list = [i for i in range(1, 15)]
    try:
        get_web = requests.get(url,headers=header,timeout=30)
    except:
        get_web = requests.get(url, headers=header, timeout=30)

    get_web.encoding = "utf-8"
    soup = BeautifulSoup(get_web.text,"html.parser")
    all_a = soup.find("div",attrs={"class":"rankdiv"}).find("ul").find_all("a",href=re.compile(r'/girl/\d+/'))
    for a in all_a: #确定是哪一个女孩
        if choice(sleep_list) is 1:
            sleep(1)
        else:
            pass
        href = a.get("href")
        img_urls = url[0:-9] + href[1:] #补全url
        try:
            img_web = requests.get(img_urls,headers=header,timeout=30) #进入该女孩的总界面
        except:
            img_web = requests.get(img_urls, headers=header, timeout=30)

        img_web.encoding = "utf-8"
        img_soup = BeautifulSoup(img_web.text,"html.parser")
        all_img_a = img_soup.find("div",attrs={"class":"post_entry"}).find_all("a",attrs={"class":"igalleryli_link"})
        for img_a in all_img_a: #确定是该女孩的哪一组写真
            if choice(sleep_list) is 1:
                sleep(1)
            else:
                pass
            title2 = img_a.img.get("title")
            global i
            i += 1#对女孩的图组数进行统计
            if os.path.isdir(os.path.join("E:\zhai\\" + title2)): #如果文件夹已经存在，跳过
                print("the " + title2 + " is exist!")
                pass
            else:
                os.makedirs(os.path.join("E:\zhai\\" + title2))  # 创建文件夹
            os.chdir("E:\zhai\\" + title2)
            img_url = url[0:-10] + img_a.get("href") #获取一组写真的url
            try:
                jpg_url = requests.get(img_url,timeout=30)
            except:
                jpg_url = requests.get(img_url,timeout=30)
            jpg_url.encoding = "utf-8"
            jpg_soup = BeautifulSoup(jpg_url.text,"html.parser")
            max_pages = len(jpg_soup.find("div",id="pages").find_all("a"))-1 #获取该组写真的最大页数
            for page in range(1,max_pages+1): #对于该组写真的每一页，进行src的提取并保存
                if choice(sleep_list) is 1:
                    sleep(1)
                else:
                    pass
                jpg_href = img_url + str(page) + ".html"
                try:
                    jpg_href_get = requests.get(jpg_href,timeout=30)
                except:
                    jpg_href_get = requests.get(jpg_href,timeout=30)
                jpg_href_soup = BeautifulSoup(jpg_href_get.text,"html.parser")
                jpg_srcs = jpg_href_soup.find("div",attrs={"class":"gallery_wrapper"}).find_all("img")
                for jpg_src in jpg_srcs:
                    if choice(sleep_list) is 1:
                        sleep(1)
                    else:
                        pass
                    jpg_src = jpg_src["src"]
                    try:
                        jpg = requests.get(jpg_src,timeout=30)
                    except:
                        jpg = requests.get(jpg_src,timeout=30)
                    name = jpg_src[-9:].replace('/','')  # 截取倒数第九位至末尾为图片的名字
                    if os.path.isfile(name):  #如果图片已存在就跳过
                        print(name + " exist skip!")
                        pass
                    else:
                        global p
                        p += 1
                        with open(name,"ab") as f:
                            f.write(jpg.content)
                            print(name + " has been saved" + " This is the " + str(p) + " pages")

def main():
    get_girls()
    print("OK!")

if __name__ == "__main__":
    main()