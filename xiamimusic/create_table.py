import pymysql

def creat_dbtable():
    con = pymysql.connect(host="localhost",user="root",passwd="A19990701",db="xiami",port=3306)
    cur = con.cursor()
    cur.execute("CREATE TABLE song_info(song varchar(1000),comment_time varchar(1000),observer_id varchar(1000),\
    observer_level varchar(500),comment varchar(4000) null,like_num varchar(500),phone varchar(1000) null)")
    cur.close()
    con.commit()
    con.close()