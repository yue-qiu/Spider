# coding:utf-8
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import time
import pymysql
from multiprocessing import Pool
import os

class get_song_list():
    def __init__(self,url):
        self.url = url
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def get_list(self):
        """
        用selenium切换frame，解析frame的html，找出榜上的歌曲
        :return:包含了榜上歌曲url的set
        """
        song_url_list = []
        self.driver.implicitly_wait(5)
        self.driver.get(self.url)
        self.driver.switch_to.frame("g_iframe")
        soup = BeautifulSoup(self.driver.page_source,"html.parser")
        song_list = soup.find("div",attrs={"id":"song-list-pre-cache"}).find("tbody").find_all("a",attrs={"href":re.compile(r'/song\?id=\d+')})
        for song in song_list[0:30]:
            url = "http://music.163.com/#" + song.get("href")
            song_url_list.append(url)
        return set(song_url_list)

class get_song_info():
    def __init__(self,url):
        self.url = url
        self.driver = webdriver.Chrome()

    def _save_info(self,song,singer,comment,comment_time,comment_like_num,observer_id,observer_sex,observer_level,observer_location):
        con = pymysql.connect(host="localhost",user="root",passwd="A19990701",db="wangyiyun",port=3306,charset="utf8mb4")
        cur = con.cursor()
        try:
            cur.execute("insert into song_info (\
            song,singer,comment,comment_time,like_num,observer_id,observer_sex,observer_level,observer_location)\
             values (%s,%s,%s,%s,%s,%s,%s,%s,%s)" ,(song,singer,comment,comment_time,comment_like_num,observer_id,observer_sex,observer_level,observer_location))
            cur.close()
            con.commit()
            con.close()
        except:
            cur.close()
            con.commit()
            con.close()
            print("一个错误")

    def _auto_scroll_to_bottom(self):
        """
        下拉到窗口最下端
        :return
        """
        js = "window.scrollTo(0,document.body.scrollHeight);"
        self.driver.execute_script(js)
        time.sleep(2)

    def _get_observer_info(self,observer_home_url):
        """
        获得评论者的性别
        :param observer_home_url: 评论者的个人主页
        :return:
        """
        driver = webdriver.Chrome()
        driver.get(observer_home_url)
        driver.implicitly_wait(20)
        driver.switch_to.frame("g_iframe")
        observer_soup = BeautifulSoup(driver.page_source, "html5lib")
        observer_level = observer_soup.find("h2", attrs={"id": "j-name-wrap"}).find("span",attrs={"class":"lev u-lev u-icn2 u-icn2-lev"}).get_text()
        observer_loca = observer_soup.find("div",attrs={"class":"inf s-fc3"}).find("span")
        if observer_loca is not None:
            observer_location = observer_loca.get_text().split("：")[1]
        else:
            observer_location = None
        sex = observer_soup.find("h2", attrs={"id": "j-name-wrap"}).find("i", attrs={
            "class": re.compile(r'icn u-icn u-icn-')})["class"][2]
        if sex == "u-icn-02":
            observer_sex = "女"
            driver.close()
            return observer_sex,observer_level,observer_location
        else:
            observer_sex = "男"
            driver.close()
            return observer_sex,observer_level,observer_location

    def down_info(self):
        """
        获取歌曲名字，歌手，歌曲的评论，评论时间，评论点赞数，评论者id与性别
        :return:
        """
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.driver.implicitly_wait(20)
        self.driver.switch_to.frame("g_iframe")
        self._auto_scroll_to_bottom()
        soup = BeautifulSoup(self.driver.page_source,"html5lib")
        song = soup.find("div",attrs={"class":"tit"}).find("em").string
        singer = soup.find("p",attrs={"class":"des s-fc4"}).get_text().split("：")[1]
        comments_info_box = soup.find("div",attrs={"id":"comment-box"}).find("div",attrs={"class":"cmmts j-flag"}).find_all("div",attrs={"class":"itm"})
        i = 0
        while i <= 50:
            for comment_info in comments_info_box:
                comment = comment_info.find("div",attrs={"class":"cnt f-brk"}).get_text().split("：")[1]
                observer_id = comment_info.find("div",attrs={"class":"cnt f-brk"}).get_text().split("：")[0]
                observer_home_url = "http://music.163.com/#" + comment_info.find("div",attrs={"class":"cnt f-brk"}).find("a",attrs={"class":"s-fc7"})["href"]
                observer_sex,observer_level,observer_location = self._get_observer_info(observer_home_url)
                comment_time = comment_info.find("div",attrs={"class":"rp"}).find("div",attrs={"class":"time s-fc4"}).get_text()
                comment_like_num = comment_info.find("div",attrs={"class":"rp"}).find("a",attrs={"data-type":"like"}).get_text()[2:-1]
                print("%s %s %s %s %s %s %s %s %s THIS IS PROCESS NO.%s" % (song,singer,comment,comment_time,comment_like_num,observer_id,observer_sex,observer_level,observer_location,os.getpid()))
                self._save_info(song,singer,comment,comment_time,comment_like_num,observer_id,observer_sex,observer_level,observer_location)
            i += 1
            self.driver.find_element_by_xpath("/html/body/div[3]/div[1]/div/div/div[2]/div/div[2]/div[3]/div").find_elements_by_tag_name("a")[-1].click()
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("g_iframe")
            self._auto_scroll_to_bottom()
            soup = BeautifulSoup(self.driver.page_source, "html5lib")
            song = soup.find("div", attrs={"class": "tit"}).find("em").string
            singer = soup.find("p", attrs={"class": "des s-fc4"}).get_text().split("：")[1]
            comments_info_box = soup.find("div", attrs={"id": "comment-box"}).find("div", attrs={
                "class": "cmmts j-flag"}).find_all("div", attrs={"class": "itm"})
        self.driver.close()

def run(song_url):
    song_info = get_song_info(song_url)
    song_info.down_info()

def create_data_table():
    con = pymysql.connect(host="localhost",user="root",passwd="A19990701",db="wangyiyun",port=3306)
    cur = con.cursor()
    cur.execute("CREATE TABLE song_info(\
    song varchar(500),singer varchar(100),observer_id varchar(100),observer_sex varchar(50),observer_level varchar(20),\
    observer_location varchar(200),comment varchar(3000),comment_time varchar(200),like_num varchar(100))")
    cur.close()
    con.commit()
    con.close()

if __name__ == "__main__":
    p = Pool()
    get_song_list = get_song_list("http://music.163.com/#/discover/toplist?id=3778678")
    song_url_list = get_song_list.get_list()
    create_data_table()
    for song_url in song_url_list:
        p.apply_async(run,args=(song_url,))
    p.close()
    p.join()
    print("完成！")


