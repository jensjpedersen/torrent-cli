import re
import imdb

def format_torrent_name(torrent_name:str):
    """
    Parmeters:
        torrent_name - Usula torrent name format 

    Funciton separates info from torrent_name

    Returns:
        dict with torrent info: title, release, season, episode
    """
    string = torrent_name 
    string = string.replace(".", " ")
    string = string.replace("-", " ")
    string = re.sub(r"[\([{})\]]", "", string)
    string = re.sub(r"[\([{})\]]", "", string)

    # Get relese year from title string
    year = None
    search=re.search('20[0-9]{2} | 19[5-9][0-9]', string)

    idx = len(string) # Used to determine length of title 
    if search: 
        year = search.group()
        idx = search.span()[0]

    # Get season information from title string  
    season = None
    season_formats = [" Season [0-9]+", " SEASON [0-9]+", " S[0-9]+", "s[0-9]"]
    for s in season_formats:
        search = re.search(s, string)
        if search:
            season = search.group() 
            season = re.search('[0-9]+', season).group()
            check_idx = search.span()[0]
            if check_idx < idx:
                idx = check_idx
            break

    # Get season information from title string  
    #episode = ""
    episode = None
    episode_formats = [" Episode [0-9]+", " EPISODE [0-9]+", " E[0-9]+", "e[0-9]"]
    for e in episode_formats:
        search = re.search(e, string)
        if search:
            episode = search.group() 
            episode = re.search('[0-9]+', episode).group()
            check_idx = search.span()[0]
            if check_idx < idx:
                idx = check_idx
            break

    # Used idx to determine name 
    name = string[:idx]

    # Return dict with info 
    #info.titles = name_list
    info = {}
    info["title"] = string[:idx] 
    info["release"] = year
    info["season"] = season
    info["episode"] = episode
    return info

def get_rating(title): 
    ia = imdb.Cinemagoer()
    series = ia.search_movie(title)
    assert(len(series)!=0)
    #series = ia.search_movie('madalorian')

    #series_id = series[0].movieID

    print(len(series))

def get_imdb_dict(title:str, season:int = None, episode:int = None):
    ia = imdb.Cinemagoer()
    series = ia.search_movie(title)[0]
    #series_id = series[0].movieID
    #series = ia.get_movie(series_id)
    ia.update(series, 'episodes')

    if season and episode:
        return series['episodes'][season][episode]
    elif season and not episode: 
        return series['episodes'][season]
    else: 
        return series

def format_titles(titles:list):
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
        episode_formats = [" Episode [0-9]+", " EPISODE [0-9]+", " E[0-9]+", "e[0-9]"]
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
    



