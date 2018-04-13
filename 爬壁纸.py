#encoding=utf-8
import requests
from bs4 import BeautifulSoup
import os
from random import choice
from time import sleep


url = "http://www.zhuoku.com/"
header_list = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)"]
header1 = {"User-Agent":"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)"}
try:
    r = requests.get(url,headers=header1,timeout=30)
except:
    r = requests.get(url,headers=header1,timeout=30)

res = r.content.decode("gb2312","ignore").encode("utf-8","ignore")
soup = BeautifulSoup(res,"html.parser")
all_a = soup.find("div",id="zuixin").find_all('a',attrs={"class":"title"})
for a in all_a:
    header = {"User-Agent": choice(header_list)}
    title  = a.get_text().replace("/",'')
    href = a.get("href")
    img_url = url + href[1:-4] + "(1).htm"#补第一张图片的全href
    if os.path.isdir(os.path.join("D:\zhuoku",title)): #如果存在文件夹
        print("exist" + title)
        pass
    else:
        os.makedirs(os.path.join("D:\zhuoku",title)) #创建文件夹
        print("makedir" + title)
    os.chdir("D:\zhuoku\\" + title) #切换到此文件夹
    try:
        img_url_get = requests.get(img_url,headers=header,timeout=30)
    except:
        img_url_get = requests.get(img_url,headers=header,timeout=30)

    sleep(0.5)
    img_url_soup = BeautifulSoup(img_url_get.text,"html.parser")
    max_img_page = img_url_soup.find('div',id="yema").find_all("a")[-1].get_text()
    for page in range(1,int(max_img_page)+1):
        jpg_href = url + href[1:-4] + "(" + str(page) + ").htm" + "#turn"
        try:
            jpg_href_get = requests.get(jpg_href,headers=header,timeout=30)
        except:
            jpg_href_get = requests.get(jpg_href,headers=header,timeout=30)

        sleep(0.5)
        jpg_soup = BeautifulSoup(jpg_href_get.text,"html.parser")
        jpg_url = jpg_soup.find("div",id="bizhiimg").find("img")["src"] #在find方法后面用方括号将属性括起来可以取出该属性的值
        name = jpg_url[-9:] #截取倒数第九位至末尾为图片的名字
        if os.path.isfile(name): #如果存在名为name的文件
            print(name + " exist  skip")
            pass #下面全跳过
        else:
            jpg_header = {
                "Referer": jpg_href,
                "User-Agent":choice(header_list)
            }
            try:
                jpg = requests.get(jpg_url,headers=jpg_header,timeout=30)
            except:
                jpg = requests.get(jpg_url,headers=header,timeout=30)

            sleep(0.5)
            with open(name,'wb') as f:
                f.write(jpg.content)
                print(name+" saved")

print("congratulations! all finished!")
