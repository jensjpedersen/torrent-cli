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

class Torrent: 

    def __init__(self, query=None, download_dir='/home/jensjp/Downloads', page=1): 
        if len(sys.argv) > 1: 
            self.query, self.download_dir, self.page = self.__get_command_line_args(query, download_dir, page)
        else: 
            self.query, self.download_dir, self.page = query, download_dir, page

        if self.query==None:
            raise ValueError(f'Query is {self.query}. Not a vaild serach string')


        self.list_index = None 
        self.soup = self.__request_soup()
        self.tmp_dir:str
        self.url:str
        # TODO: -s --sort
        # TODO: unit testing? test if list index is defined 
        # TODO: command line arg for page number

    def __get_command_line_args(self, query, download_dir, page): 
        parser = argparse.ArgumentParser(description='Arguments')
        parser.add_argument('-q', "--query", type=str, help="Search for torrent ")
        parser.add_argument('-d', "--dir", type=str, help="Download directory")
        parser.add_argument('-p', "--page", type=str, help="Choose page nr")
        args = parser.parse_args()

        if args.query: 
            query=args.query
            
        if args.dir: 
            download_dir = args.dir

        if args.page:
            page = args.page

        return query, download_dir, page

    def __request_soup(self): 
        query=self.query.replace(" ", "+")
        #url="https://solidtorrents.net/search?q=" + query + "&sort=seeders" 
        self.url = "https://solidtorrents.to/search?q=" + query + "&sort=seeders&page=" + str(self.page)
        #url = "https://solidtorrents.to/search?q=" + query + "&page=" + self.page
        r = requests.get(self.url)
        if r.status_code == 522:
            raise TimeoutError('Request 522 Connection Timed Out')
        #try: 
        #    r = requests.get(self.url)
        #except requests.exceptions.Timeout as e:
        #    print('skdjfhsdkjf')
        #    SystemExit(f'Error:Get request Timout error: {e}')
        
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    def print_vars(self):
        print(f"query: {self.query}")
        print(f"page number: {self.page}")
        print(f"download_dir: {self.download_dir}")
        print(f"list_index: {self.list_index}")

    def get_titles(self): 
        title=self.soup.findAll('h5', {"class": "title w-100 truncate"})
        titles=[]
        for e in title: 
            titles.append(e.text)

        # If extra element is appearing on beginning of page, remove them
        if len(titles) > 20: # Number of tiltres per page
            idx_remove = len(titles)-20 # remove first element from list
            del titles[0:idx_remove] # Remove first element form list

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
        for i, e in enumerate(anchors):
            link=(e['href'])
            search=re.search('/torrent/.+torrent', link)
            x0,x1=search.span()
            x0=len('/torrent/') + x0
            torrent_file=link[x0:x1]
            torrents.append(torrent_file)

        assert(self.list_index != None) 
        if self.list_index > len(anchors)-1:
            raise(IndexError(f"Anchor element does not exisit, Nr. links = {len(anchors)}"))

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
        # Method sets list_index
        # For use in command line
        for i,e in enumerate(titles):
            print(f"{i+1:3}:{e}")
        try: 
            nr=int(input("\nChoose title: "))
        except ValueError:
            print(" Input should be an integer value")

        self.list_index = nr-1

    def set_list_index(self, idx:int):
        # Method sets list_index
        # For use in scripts 
        self.list_index = idx


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
        subprocess.call(['aria2c', '--dir', self.download_dir, '--select-file', file_nr, magnet, '--allow-overwrite=true'])
        shutil.rmtree(self.tmp_dir)

    def main_terminal(self): 
        titles = self.get_titles()
        self.choose_title(titles)
        self.get_metadata()
        self.download_torrent()
        #shutil.rmtree(self.tmp_dir)

    def main_curses(self, list_idx): 
        self.set_list_index(list_idx)
        self.get_metadata()
        self.download_torrent()

if __name__ == "__main__":
    t = Torrent()
    t.main_terminal()
    #t.print_vars()
    #t.list_index = 0
    #print(t.get_torrent_href())
    #t.get_metadata()


    



