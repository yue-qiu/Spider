from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import requests
import os
import re
import time
from PIL import Image
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import  expected_conditions as EC
from selenium.webdriver.common.by import By


class ptoto_spider():
    def __init__(self,qq,pwd,target_qq):
        self.driver = webdriver.Chrome()
        self.target_qq = target_qq
        url = "https://user.qzone.qq.com/" + self.target_qq
        self.url = url
        self.qq = qq
        self.pwd = pwd
        self.driver.maximize_window() #最大化窗口
        self.driver.get(self.url)
        self.sleep_time = 3
        self.album_num = 0

        print('webdriver start init success!')

    def __del__(self):
        """
        结束爬虫
        :return
        """
        try:
            self.driver.close()
            self.driver.quit()
            print('webdriver close and quit success!')
        except:
            pass

    def _auto_scroll_to_bottom(self):
        """
        下拉到窗口最下端
        :return
        """
        js = "window.scrollTo(0,document.body.scrollHeight);"
        self.driver.execute_script(js)
        time.sleep(self.sleep_time)

    def _auto_scroll_to_top(self):
        """
        上拉窗口到顶部
        :return
        """
        js = "window.scrollTo(0,0);"
        self.driver.execute_script(js)
        time.sleep(self.sleep_time)

    def _auto_scroll_to_down(self):
        """
        下拉窗口
        :return
        """
        js = "var q=document.body.scrollTop=10000"
        self.driver.execute_script(js)
        time.sleep(self.sleep_time)

    def _need_login(self):
        '''
        通过判断页面是否存在 id 为 login_div 的元素来决定是否需要登录
        :return: 未登录返回 True，反之
        '''
        try:
            self.driver.find_element_by_id('login_div')
            return True
        except:
            return False

    def _login(self):
        '''
        登录 QQ 空间，先点击切换到 QQ 帐号密码登录方式，然后模拟输入 QQ 帐号密码登录，
        接着通过判断页面是否存在 id 为 QM_OwnerInfo_ModifyIcon 的元素来验证是否登录成功
        :return: 登录成功返回 True，反之
        '''
        self.driver.switch_to.frame('login_frame')
        self.driver.find_element_by_id('switcher_plogin').click()
        self.driver.find_element_by_id('u').clear()
        self.driver.find_element_by_id('u').send_keys(self.qq)
        self.driver.find_element_by_id('p').clear()
        self.driver.find_element_by_id('p').send_keys(self.pwd)
        self.driver.find_element_by_id('login_button').click()
        try:
            self.driver.find_element_by_id('QM_OwnerInfo_ModifyIcon')
            return True
        except:
            return False

    def get_in_main(self):
        """
        尝试进入目标用户的主页
        :return: 无法进入返回None,反之
        """
        time.sleep(self.sleep_time)
        if "申请访问" in self.driver.page_source:
            print("用户%s没有访问%s的权限！" % (self.qq,self.target_qq))
            return None
        else:
            print("成功进入%s的主页" % self.target_qq)
            return True

    def get_gallery_list(self):
        """
        获得列表中的每一个相册
        点击进入
        :return
        """
        self.driver.switch_to.default_content()
        album = WebDriverWait(self.driver,4).until(EC.presence_of_element_located((By.XPATH,"//a[@title='相册']")))
        time.sleep(self.sleep_time)
        album.click()
        self._auto_scroll_to_down()
        frame = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.ID,"tphoto")))
        self.driver.switch_to.frame(frame)

        elements = self.driver.find_elements_by_xpath("//a[@class='c-tx2 js-album-desc-a']")
        ele_num = len(elements)
        print("发现%d组相册" % ele_num)
        while (self.album_num<ele_num):
            self._auto_scroll_to_bottom()
            time.sleep(self.sleep_time)
            # 页面刷新之后要重定位元素，否则会出现元素失效
            elements = self.driver.find_elements_by_xpath("//a[@class='c-tx2 js-album-desc-a']")
            # 进入该相册
            elements[self.album_num].click()
            self._auto_scroll_to_down()
            # 下载相册里的图片和相册标题
            try:
                self.photos_deal()
            except:
                self.driver.refresh()
                self.album_num += 1
                time.sleep(self.sleep_time)
                self.get_gallery_list()
                break
            # switch_to.default_content()切回主文档才可以找到app_canvas_frame
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("app_canvas_frame")
            print("已保存%d组相册" % (self.album_num + 1))
            self.album_num += 1
        self.__del__()

    def photo_download(self,save_dir,title,pic_num):
        """
        开始下载相册里的图片
        :return:
        """
        time.sleep(self.sleep_time)
        self.driver.switch_to.default_content()
        url = self.driver.find_element_by_xpath("//div[@id='js-img-border']").find_element_by_tag_name("img").get_attribute("src")
        save_file = os.path.join(save_dir, str(hash(title)) + "_" + str(hash(url)))
        try:
            res = requests.get(url, timeout=10)
            with open(save_file, "wb") as f:
                f.write(res.content)
            # Image.open(imagepath).format探测图片格式
            new_stuffer_file = save_file + '.' + Image.open(save_file).format.lower()
            os.rename(save_file, new_stuffer_file)
            # 将webp格式图片转为jpg
            if Image.open(new_stuffer_file).format.lower() == 'webp':
                img = Image.open(new_stuffer_file)
                img.save(save_file + ".jpg")
                os.remove(new_stuffer_file)
            print("%s已保存%d张图片 " % (title, pic_num))
        except:
            pass

    def photos_deal(self):
        """
        开始爬取该相册内的图片与相册相关信息
        :return:
        """
        # 找出当前页面图片
        tags = self.driver.find_elements_by_xpath("//a[@class='item-cover j-pl-photoitem-imgctn']")
        # 找出相册名
        title = self.driver.find_element_by_class_name("j-pl-albuminfo-title").get_attribute("title")
        # 找出相册中的图片数量
        num = self.driver.find_element_by_xpath("//span[@class='count c-tx2 j-pl-albuminfo-total']").text
        pic_num_pattern = re.search(r'\d+',num)

        if pic_num_pattern is None:
            # 判断相册内是否有图片
            print("这是一个空相册!")
            self.driver.switch_to.default_content()
            frame = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.ID,"tphoto")))
            self.driver.switch_to.frame(frame)
            self.driver.find_element_by_xpath("//a[@class = 'c-tx2 js-select']").click()
            time.sleep(2)
        else:
            pic_numbers = int(pic_num_pattern.group())
            # 已保存的图片数
            pic_num = 1
            # 创建文件夹
            save_dir = os.path.join("E:\QQ空间\\" + self.target_qq, title)
            if os.path.isdir(save_dir):
                pass
            else:
                os.makedirs(save_dir)
            # 切换到此文件夹
            os.chdir(save_dir)
            # 点击第一张图片
            tags[0].click()
            if pic_numbers == 1:
                self.photo_download(save_dir,title,pic_num)
            else:
                while (pic_num<pic_numbers):
                    self.photo_download(save_dir,title,pic_num)
                    pic_num += 1
                    # 点击下一页按钮
                    pic = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,"//div[@id='js-img-border']")))
                    #鼠标悬停在图片上方，使出现下一页按钮
                    ActionChains(self.driver).move_to_element(pic).perform()
                    next_page = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "js-btn-nextPhoto")))
                    try:
                        next_page.click()
                    except:
                        break
            # 退出大图模式
            return_album = WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,"photo_layer_close")))
            return_album.click()
            # 点击相册按钮
            self._auto_scroll_to_top()
            frame = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.ID,"tphoto")))
            self.driver.switch_to.frame(frame)
            self.driver.find_element_by_xpath("//a[@class = 'c-tx2 js-select']").click()
            time.sleep(2)

    def run(self):
        """
        爬虫入口
        :return
        """
        if self._need_login():
            self._login()
            if self.get_in_main():
                self.get_gallery_list()
            else:
                return
        else:
            if self.get_in_main():
                self.get_gallery_list()
            else:
                return

if __name__ == "__main__":
    spider = ptoto_spider("1554525716","13544179558","1318063937")
    spider.run()