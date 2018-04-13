import requests
import random

def _get_random_num():
    """
    产生一个17位的随机数
    :return: 17位随机数
    """
    string = ""
    length = 15
    for i in range(length):
        string += str(random.randint(0,10))

    return string

def get_json(page):
    """
    构造一页评论的json
    :param page:
    :return:
    """
    callback_num = _get_random_num()
    json_url = "https://c.y.qq.com/base/fcgi-bin/fcg_global_comment_h5.fcg\
?g_tk=5381&jsonpCallback=jsoncallback%s&loginUin=0&hostUin=0&format=jsonp&\
inCharset=utf8&outCharset=GB2312&notice=0&platform=yqq&needNewCode=0&cid=205360772&reqtype=2&\
biztype=1&topid=4830342&cmd=8&needmusiccrit=0&pagenum=%s\
&pagesize=25&lasthotcommentid=song_4830342_2212344582_1517749874&\
callback=jsoncallback%s&domain=qq.com&ct=24&cv=101010" % (callback_num,page,callback_num)
    return json_url