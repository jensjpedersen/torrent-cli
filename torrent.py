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
import signal
import sys
import wget
#import urllib3

class torrent: 
    def __init__(self): 
        self.query, self.download_dir = self.__get_command_line_args()
        self.list_index = None 
        self.soup = self.__request_soup()
        self.tmp_dir: str
        # TODO: -s --sort
        # TODO: unit testing? test if list index is defined 

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
        #print(f"soup: {self.soup}")

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

    def get_torrent_name(self): 
        # Returns name of .torrent file, retived from website
        anchors=self.soup.findAll('a', {'class': 'dl-torrent'}, href=True)
        torrents = []
        for e in anchors:
            link=(e['href'])
            search=re.search('/torrent/.+torrent', link)
            x0,x1=search.span()
            x0=len('/torrent/') + x0
            torrent_file=link[x0:x1]
            torrents.append(torrent_file)

        assert(self.list_index != None) 
        return torrents[self.list_index]

    def get_torrent_href(self): 
        # Returns list of hrefs to torrent 
        anchors=self.soup.findAll('a', {'class': 'dl-torrent'}, href=True)
        hrefs = []
        for e in anchors:
            link=(e['href'])
            hrefs.append(link)

        assert(self.list_index != None) 
        return hrefs[self.list_index]

    def get_magnet(self): 
        # Returns magnet link retirved from website
        anchors=self.soup.findAll('a', {'class': 'dl-magnet'}, href=True)
        torrents = []
        for e in anchors:
            link=(e['href'])
            torrents.append(link)

        assert(self.list_index != None) 
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

        def rm_tmp(signum, frame): 
            shutil.rmtree(self.tmp_dir)
            sys.exit(0) # rmove tmp dir and content

        signal.signal(signal.SIGINT, rm_tmp) 

        if True: 
            # TODO: download .torrent https://stackabuse.com/download-files-with-python/
            #wget.download(hrefs[0], self.get_torrent_name())

            tmp_path = self.tmp_dir + "/" + self.get_torrent_name()
            subprocess.call(['wget', '-O', tmp_path, self.get_torrent_href()])
            #wget.download(hrefs[0], self.get_torrent_name())

            # Downloads html ...
            #r = requests.get(self.get_torrent_href())
            #open(self.get_torrent_name() , 'wb').write(r.content)

        else: 
            magnet = self.get_magnet()
            subprocess.call(['aria2c', '--dir', self.tmp_dir, '--bt-metadata-only=true', '--bt-save-metadata=true', magnet])




        # add direct download option

    def download_torrent(self):
        #self.tmp_dir = "/tmp/tmp9jdwfh6p"
        torrent_file=glob.glob(os.path.join(self.tmp_dir, '*torrent'))[0]
        subprocess.call(['aria2c', '--show-files', torrent_file]) # Only wokrs for torrent file or metalink (not magnet?)
        file_nr=input("enter file nr: ")
        magnet=self.get_magnet()
        subprocess.call(['aria2c', '--dir', self.download_dir, '--select-file', file_nr, magnet])

    def main(self): 
        titles = self.get_titles()
        self.choose_title(titles)
        self.get_metadata()
        self.download_torrent()
        shutil.rmtree(self.tmp_dir)

if __name__ == "__main__":
    t = torrent()
    t.main()
    #t.print_vars()
    #t.list_index = 0
    #print(t.get_torrent_href())
    #t.get_metadata()


    


