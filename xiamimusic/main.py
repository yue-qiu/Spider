from comment import get_comment
from create_table import creat_dbtable
from get_song_list import get_song_url_list
from multiprocessing import Pool

def run(url):
    creat_dbtable()
    song_url_list = get_song_url_list(url)
    p = Pool()
    for song_url in song_url_list:
        p.apply_async(get_comment,args=(song_url,))
    p.close()
    p.join()


if __name__ == "__main__":
    run("http://www.xiami.com/artist/O9fc383?spm=a1z1s.3057853.6862625.13.RZdRDN")