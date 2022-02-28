import re
import tempfile
import subprocess
from bs4 import BeautifulSoup
import requests
import os 
import glob
import argparse
import tempfile
import shutil
import atexit

class Torrent: 
    def __init__(self): 
        self.query, self.download_dir = self.__get_command_line_args()
        self.list_index: int 
        self.soup = self.__request_soup()
        self.tmp_dir: str

    def __get_command_line_args(self): 
        parser = argparse.ArgumentParser(description='Arguments')
        parser.add_argument('-q', "--query", type=str, help="Search for torrent ")
        parser.add_argument('-d', "--dir", type=str, help="Download directory")
        args = parser.parse_args()

        query="the office"
        if args.query: 
            query=args.query
            
        download_dir = '/home/jensjp/Downloads'
        if args.dir: 
            download_dir = args.dir

        return query, download_dir

    def __request_soup(self): 
        query=self.query.replace(" ", "+")
        url="https://solidtorrents.net/search?q=" + query + "&sort=seeders" 
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    def print_vars(self):
        print(f"query: {self.query}")
        print(f"download_dir: {self.download_dir}")
        print(f"list_index: {self.list_index}")
        print(f"soup: {self.soup}")

    def get_titles(self): 
        title=self.soup.findAll('h5', {"class": "title w-100 truncate"})
        titles=[]
        for e in title: 
            titles.append(e.text)
        return titles

    def get_stats(self): 
        # TODO
        divs=self.soup.findAll('div', {'class': 'stats'})
        stats=[]
        for e in divs: 
            print(e)

    def get_torrent(self): 
        anchors=self.soup.findAll('a', {'class': 'dl-torrent'}, href=True)
        torrents = []
        for e in anchors:
            link=(e['href'])
            search=re.search('/torrent/.+torrent', link)
            x0,x1=search.span()
            x0=len('/torrent/') + x0
            torrent_file=link[x0:x1]
            torrents.append(torrent_file)
        return torrents[self.list_index]

    def get_magnet(self): 
        anchors=self.soup.findAll('a', {'class': 'dl-magnet'}, href=True)
        torrents = []
        for e in anchors:
            link=(e['href'])
            torrents.append(link)
        return torrents[self.list_index]

    def choose_title(self, titles: list):
        for i,e in enumerate(titles):
            print(f"{i+1:3}:{e}")

        try: 
            nr=int(input("\n Choose title: "))
        except ValueError:
            print(" Input should be an integer")

        self.list_index = nr-1


    def get_metadata(self):
        self.tmp_dir = tempfile.mkdtemp()
        magnet = self.get_magnet()
        subprocess.call(['aria2c', '--dir', self.tmp_dir, '--bt-metadata-only=true', '--bt-save-metadata=true', magnet])
        def rm_tmp(): shutil.rmtree(self.tmp_dir) # rmove tmp dir and content
        atexit.register(rm_tmp)
        # add direct download option

    def download_torrent(self):
        #self.tmp_dir = "/tmp/tmp9jdwfh6p"
        torrent_file=glob.glob(os.path.join(self.tmp_dir, '*torrent'))[0]
        subprocess.call(['aria2c', '--show-files', torrent_file]) # Only wokrs for torrent file or metalink (not magnet?)
        file_nr=input("enter file nr: ")
        magnet=self.get_magnet()
        subprocess.call(['aria2c', '--dir', self.download_dir, '--select-file', file_nr, magnet])


#dirpath = tempfile.mkdtemp() # make tmp dir


#print(get_magnets(soup)[0])
#print(get_torrents(soup)[0])
#print(get_titles(soup)[0])

    #print(get_titles()[0:3])

    #titles = get_titles(soup)
    #choose_title(titles)
#choose_title()

#choose_file(magnet)

        ## Print files to sto
        ## Choose filenr from list
        #read input_nr
        #download_dir="${HOME}/Downloads"
        ##subprocess.run(["ls", "-l"])
#print(get_titles())
#print(get_links())

#def get_title():
#    title_class = "title w-100 truncate"
#    return soup.findAll('div', {"class": title_class})



#torr=get_magnets()[0]
#download_torrent(torr)
if __name__ == "__main__":
    t = Torrent()
    titles = t.get_titles()
    t.choose_title(titles)
    magnet = t.get_magnet()
    #torrent = t.get_torrent()
    t.get_metadata()
    t.download_torrent()
    #t.download_torrent()

    
    #print(t.__get_command_line_args())
    #t.print_vars()
    #print(vars(t))


