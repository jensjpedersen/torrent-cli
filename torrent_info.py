import re
from torrent import Torrent
import imdb
import numpy as np
import logging
from threading import Thread
from time import perf_counter

#  _____                         _   ___        __       
# |_   _|__  _ __ _ __ ___ _ __ | |_|_ _|_ __  / _| ___  
#   | |/ _ \| '__| '__/ _ \ '_ \| __|| || '_ \| |_ / _ \ 
#   | | (_) | |  | | |  __/ | | | |_ | || | | |  _| (_) |
#   |_|\___/|_|  |_|  \___|_| |_|\__|___|_| |_|_|  \___/ 

class TorrentInfo: 
    """
    Create dict with torrent info 

    Parmeters:
        torrent_names - List with torrent names as fetched from website
                        Each list item is of type str
        info - dict with info (name, year, season, episode) extracted from torrent_names
    """
    def __init__(self, torrent_names:list): 
        self.torrent_names = torrent_names
        self.info = {}

    def format_titles(self, titles:list):
        name_list = []
        year_list = []
        season_list = []
        episode_list = []
        #info = {"titles":None, "release":None, "season":None, "episode":None}
        info = {}
        for string in titles:
            string = string.replace(".", " ")
            string = string.replace("-", " ")
            string = re.sub(r"[\([{})\]]", "", string)
            string = re.sub(r"[\([{})\]]", "", string)

            # Get relese year from title string
            year = ""
            search=re.search('20[0-9]{2} | 19[5-9][0-9]', string)

            idx = len(string) # Used to determine length of title 
            if search: 
                year = search.group()
                idx = search.span()[0]
            year_list.append(year)

            # Get season information from title string  
            season = ""
            season_formats = [" Season [0-9]+", " SEASON [0-9]+", " S[0-9]+", "s[0-9]"]
            for s in season_formats:
                search = re.search(s, string)
                if search:
                    season = search.group() 
                    check_idx = search.span()[0]
                    if check_idx < idx:
                        idx = check_idx
                    break
            season_list.append(season)

            # Get season information from title string  
            episode = ""
            episode_formats = [" Episode [0-9]+", " EPISODE [0-9]+", "E[0-9]+", "e[0-9]"]
            for e in episode_formats:
                search = re.search(e, string)
                if search:
                    episode = search.group() 
                    check_idx = search.span()[0]
                    if check_idx < idx:
                        idx = check_idx
                    break
            episode_list.append(episode)

            # Used idx to determine name 
            name_list.append(string[:idx])

        # Return dict with info 
        #info.titles = name_list
        info["title"] = name_list
        info["release"] = year_list
        info["season"] = season_list
        info["episode"] = episode_list
        return info
        

    def strip_num_from_char(self, episodes:list):
        """
        Use to remove list number from string. 

        Parameters:
            episodes - list with episodes or seasons
        """
        ep_list = []
        for i in range(len(episodes)): 
            try: 
                ep = str(re.search('[1-9][0-9]*',episodes[i]).group())

            except AttributeError: 
                ep = None
            finally:
                ep_list.append(ep)

        return ep_list

    def get_info_dict(self): 
        """
        Create and return dict with info
        """

        torr_dict = self.format_titles(self.torrent_names)

        self.info['title'] = torr_dict['title']
        self.info['episode'] = self.strip_num_from_char(torr_dict['episode'])
        self.info['season'] = self.strip_num_from_char(torr_dict['season'])

        return self.info

# ___               _ _    ___        __       
# _ _|_ __ ___   __| | |__|_ _|_ __  / _| ___  
# | || '_ ` _ \ / _` | '_ \| || '_ \| |_ / _ \ 
# | || | | | | | (_| | |_) | || | | |  _| (_) |
# ___|_| |_| |_|\__,_|_.__/___|_| |_|_|  \___/ 
                                              
class ImdbInfo:
    def __init__(self, info:dict): 
        self.info = info 
        self.imdb_uniq:list = []
        self.imdb_series_list:list = [] # list with imdb series metadata
        #self.imdb_season_list:list = [] # list with imdb season metadta
        self.imdb_episode_list:list = [] # list with imdb episode metadta

    #def update_imdb_dicts(self): 
    #    print(self.info)
    #    #titles = self.info['title']
    #    #print(titles)


    #def get_imdb_dict(self, idx):
    #    # title - exact title of show
    #    # TODO: fix if title is speeled wrong

    #    title = self.info['title'][idx]
    #    season = int(self.info['season'][idx])
    #    episode = int(self.info['episode'][idx])
    #    ia = imdb.Cinemagoer()

    #    try: 
    #        series = ia.search_movie(title)[0]
    #    except IndexError:
    #        logging.warning(f"No title with name {title}")
    #        series = None


    #    #series_id = series[0].movieID
    #    #series = ia.get_movie(series_id)
    #    ia.update(series, 'episodes')

    #    #if season and episode:
    #    #    return series['episodes'][season][episode]
    #    #elif season and not episode: 
    #    #    return series['episodes'][season]
    #    #else: 
    #    #    return series

    #    return series

    def __get_imdb_ep_info(self, imdb_dict, season, episode):
        try:
            season = int(season)
            episode = int(episode)
        except:
            return None

        return imdb_dict['episodes'][season][episode]

    #def __get_imdb_se_info(self, imdb_dict, season): 
    #    try:
    #        season = int(season)
    #    except:
    #        return None

    #    return imdb_dict['episodes'][season]




    def __imdb_dict_thread(self, title, i): 
        ia = imdb.Cinemagoer()
        try: 
            series = ia.search_movie(title)[0]
            ia.update(series, 'episodes')
            self.imdb_uniq[i] = series
        except IndexError:
            logging.error(f"No title with name {title}")
            self.imdb_uniq[i] = None

    def update_imdb_info(self): 
        titles_list = self.info['title']
        uniq_titles = list(set(titles_list))
        uniq_imdb = [None]*len(uniq_titles)

        imdb_series_list = len(titles_list)*[None]
        imdb_episode_list = len(titles_list)*[None]

        threads = [None]*len(uniq_titles) 
        self.imdb_uniq = [None]*len(uniq_titles)

        # Fetch data from IMDB api
        start = perf_counter()
        for i, title in enumerate(uniq_titles):
            t = Thread(target=self.__imdb_dict_thread, args=(title, i)) 
            t.start()
            threads[i] = t
        
        for t in threads:
            t.join()
        end = perf_counter()
        logging.info(f'{len(uniq_titles)} finsished in {end-start} seconds')

        # Create list with imdb info dicts
        for j in range(len(uniq_titles)):
            for i in range(len(titles_list)): 
                if uniq_titles[j] == titles_list[i]:
                    imdb_series_list[i] = self.imdb_uniq[j]

        # Create list with imdb episode info
        for i in range(len(titles_list)):
            season = self.info['season'][i]
            episode = self.info['episode'][i]
            imdb_episode_list[i] = self.__get_imdb_ep_info(imdb_series_list[i], season, episode)

        self.imdb_series_list = imdb_series_list
        self.imdb_episode_list = imdb_episode_list

    def get_plot(self, idx):
        #if self.imdb_episode_list[idx] != None:
        #    return self.imdb_episode_list[idx]['plot']
        if self.imdb_episode_list[idx] != None:
            return self.imdb_episode_list[idx]['plot']
        else:
            return None

    def get_rating(self, idx):
        if self.imdb_episode_list[idx] != None:
            return self.imdb_episode_list[idx]['rating']
        else:
            return None
        # https://www.shanelynn.ie/using-python-threading-for-multiple-results-queue/

                
if __name__ == "__main__":
    t = Torrent(query="Mandalorian")
    titles = t.get_titles()

    ti = TorrentInfo(titles)
    dic = ti.get_info_dict()

    print(dic)

    im = ImdbInfo(dic)
    exit()
    im.update_imdb_info()

    #im.get_plot(1)
    #print(im.imdb_episode_list[1]['plot'])

    print(im.get_plot(2))
    print(im.get_rating(2))


    #ti.main()


    




