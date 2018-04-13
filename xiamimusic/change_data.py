from threading import Thread,Lock
import pymysql

def change(song,comment_time,observer_id,observer_level,comment,comment_agree,phone):
    con = pymysql.connect(host="localhost",user="root",passwd="A19990701",db="xiami",port=3306,charset="utf8mb4")
    cur = con.cursor()
    lock = Lock()
    with lock:
        try:
            data = (song,comment_time,observer_id,observer_level,comment,comment_agree,phone)
            sql = "insert into song_info(\
            song,comment_time,observer_id,observer_level,comment,like_num,phone) values (%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sql,data)
        except Exception as e:
            print("发生了一个错误:",e)
        finally:
            cur.close()
            con.commit()
            con.close()
