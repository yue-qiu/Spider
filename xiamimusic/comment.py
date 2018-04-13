from download_html import download
import requests
import re
from random import choice,random
import os
from bs4 import BeautifulSoup
from change_data import change
from time import sleep

def get_comment(url):
    html = download(url)
    html_soup = BeautifulSoup(html,"html5lib")
    song_id = re.search(r'\d+',html_soup.find("link",attrs={"rel":"canonical"})["href"]).group()
    comment_num = int(html_soup.find("div",attrs={"id":"main_wrapper"}).find("p",attrs={"class":"wall_list_count"}).find("span").string)
    song = html_soup.find("div", attrs={"data-needpay": "1"}).find("h1").next_element
    page = 1
    i = 0
    Agent_list = [
        "Mozilla/5.0(window NT 10.0;WOW64) ApplWebKit/537.36(KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2107.204 Safari/537.36",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)"
        "Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0 "
        " Opera/8.0 (Macintosh; PPC Mac OS X; U; en)"]
    header = {"User-Agent": choice(Agent_list)}
    data = {"type":4}
    # 虾米限制只能查看到第200页评论
    while page<200:
        comment_page_url = "http://www.xiami.com/commentlist/turnpage/id/%s/page/%s/ajax/1" % (song_id,str(page))
        try:
            res = requests.post(comment_page_url,headers=header,data=data,timeout=30)
        except Exception as e:
            with open(r"E:\error.txt","a") as fp:
                fp.write("%s在请求%s时发生一个错误%s" % (song,comment_page_url,e))
            page += 1
            continue
        comment_info_list = BeautifulSoup(res.text,"html.parser").find_all("li")
        for comment_info in comment_info_list:
            sleep(random())
            comment_time = comment_info.find("div",attrs={"class":"info"}).find("span",attrs={"class":"time"}).string
            observer_id = comment_info.find("div",attrs={"class":"info"}).find("span",attrs={"class":"author"}).find("a").string
            comment_ageree = comment_info.find("div",attrs={"class":"info"}).find("span",attrs={"class":"ageree"}).get_text()
            comment = comment_info.find("div",attrs={"class":"brief"}).get_text().strip().split("\n")[0]
            if comment_info.find("div",attrs={"class":"brief"}).find("a"):
                phone = comment_info.find("div",attrs={"class":"brief"}).find("a").string
            else:
                phone = None
            observer_url = comment_info.find("div",attrs={"class":"info"}).find("span",attrs={"class":"author"}).find("a")["href"]
            level = BeautifulSoup(download(observer_url),"html.parser").find("div",attrs={"class":"left"})
            if level:
                observer_level = level.get_text().split(":")[-1]
            else:
                observer_level = None
            print(song,comment_time,observer_id,observer_level,comment,comment_ageree,phone,"this is NO.%s process" % os.getpid())
            change(song,comment_time,observer_id,observer_level,comment,comment_ageree,phone)
            i += 1
            print("现在是%s的第%d条评论，共有%d条" % (song,i,comment_num))
        page += 1
