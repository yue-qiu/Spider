from bs4 import BeautifulSoup
from download_html import download

def get_song_url_list(url):
    song_url_list = []
    soup = BeautifulSoup(download(url),"html.parser")
    song_ele_list = soup.find("div",id="artist_trends").find_all("tr")
    for song_ele in song_ele_list:
        song_url = "http://www.xiami.com" + song_ele.find("td",attrs={"class":"song_name"}).find("a")["href"]
        song_url_list.append(song_url)
    return song_url_list
