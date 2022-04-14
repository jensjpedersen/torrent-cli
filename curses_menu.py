import curses
from curses import textpad
import time
import sys
import logging
from torrent_info import TorrentInfo, ImdbInfo
import datetime



logging.basicConfig(filename='debug.log', encoding='utf-8', level=logging.DEBUG)

class CursesMenu: 

    def __init__(self, menu:list, info:dict=None, imdb:ImdbInfo=None): 
        self.imdb = imdb # Class instance of ImdbInfo class
        self.menu = menu # list with torrent names
        self.info = info # dict with torrent info
        self.list_idx = 0 # Current position in menu
        self.box1:list # Dimseions of box with content
        self.box2:list
        self.x_spacing:int # spacing between box1 and box2
        #self.w = curses.COLS # Terminal width
        #self.h = curses.LINES # Terminal height




    def print_menu(self, stdscr, x0:int, y0:int, lx:int, ly:int): 
        win1= curses.newwin(ly-1, lx-1, y0+1, x0+1)
        for i, e in enumerate(self.menu): 
            if self.list_idx == i:
                #win1.addstr(self.box1[0]+1+i, self.box1[1]+2, e[:self.box1[2]] + "\n", curses.A_STANDOUT)
                win1.addstr(1+i, 1, e[:lx-4] + "\n", curses.A_STANDOUT)
            else: 
                #win1.addstr(self.box1[0]+1+i, self.box1[1]+2, e[:self.box1[2]-4] + "\n")
                win1.addstr(1+i, 1, e[:lx-4] + "\n")
        #textpad.rectangle(win1, 0, 0, self.box1[2]-1, self.box1[3])
        #textpad.rectangle(win1, 0, 0, 10, 10)
        textpad.rectangle(stdscr, y0, x0, y0+ly, x0+lx)
        stdscr.refresh()
        win1.refresh()


    def print_info(self, stdscr, x0:int, y0:int, lx:int, ly:int): 
        win2= curses.newwin(ly-1, lx-1, y0+1, x0+1)

        #win2.clear()
        textpad.rectangle(stdscr, y0, x0, y0+ly, x0+lx)

        if self.info == None:
            stdscr.refresh()
            win2.refresh()
            return

        if self.info['title'][self.list_idx] != None:
            win2.addstr(1,1,self.info['title'][self.list_idx])

        # Print Season
        if self.info['season'][self.list_idx] != None:
            win2.addstr(2,1,'Season ' + self.info['season'][self.list_idx])

        # Print episode
        if self.info['episode'][self.list_idx] != None:
            win2.addstr(3,1,'Episode ' + self.info['episode'][self.list_idx])

        self.__print_plot(win2, 4)

        stdscr.refresh()
        win2.refresh()

    def __print_plot(self, win2, y_pos): 
        if self.imdb == None:
            return

        plot = self.imdb.get_plot(self.list_idx)

        if plot != None:
            win2.addstr(y_pos, 1, plot[:5])
            return
            win2.addstr(y_pos, 5, plot)
            


    def search_box(self, stdscr, x0:int, y0:int, lx:int, ly:int) -> str: 
        # TODO: good lxindolx size - use for box1 and box2
        curses.curs_set(1)
        search_box = curses.newwin(ly-1, lx-1, y0+1, x0+1)
        #search_box.addstr("ksd skdjjdf lyksdjf skfdj  skjfd lyly lysdkf ly skjfd lysdkjsd lyfskdjf lyskjf lysdjfkkjf ly s")

        textpad.rectangle(stdscr, y0, x0, y0+ly, x0+lx)
        stdscr.refresh()
        search_box.refresh()
        search_box.getch()

        text_box = textpad.Textbox(search_box)

        # Let tlye user edit until Ctrl-G is struck.
        text_box.edit()

        # Get resulting contents
        query = text_box.gather()

        curses.curs_set(0)

        stdscr.clear()
        #stdscr.addstr(query)
        #stdscr.refresh()
        #stdscr.getcly()
        return query




    def curses_menu(self, stdscr): 
        curses.curs_set(0)
        h, w = stdscr.getmaxyx()
        #stdscr.addstr(10, 10, str(h) + "   " + str(w))
        #self.box1 = [1, 1, h-2, w//2-2] # y0, x0, ly, lx 
        #self.box2 = [1, w//2-2, h-2, w//2-2]
        #self.box2 = [1, 90 , 10 , 20]

        #self.box1 = [1, 2,      h-2, w//2-1] # win dimesions relative to window. Use to add elements in win
        #self.x_spacing = 0
        #self.box2 = [1, w//2+self.x_spacing,   h-2, w//2-1]

        #self.search_box = [] # search box

        #win1 = curses.newwin(self.box1[2],self.box1[3], self.box1[0], self.box1[1])
        #win2 = curses.newwin(self.box2[2],self.box2[3], self.box2[0], self.box2[1])

        # Init menu

        box1 = [2, 1, w//2-3, h-4]
        self.print_menu(stdscr, *box1)
        
        box2 = [w//2+1, 1, w//2-3, h-4] # x0, y0, lx, ly
        self.print_info(stdscr, *box2)

        # Keyboard input
        while True: 
            #key = win1.getch()
            key = stdscr.getch()
            logging.debug(f'pressed key: {key}')
            #stdscr.addstr(20, 20, str(key))
            #stdscr.addstr(5, 5, str(key))
            if key == 104: # pressed h
                pass
            elif key == 106 and self.list_idx < len(self.menu)-1: # pressed j
                self.list_idx += 1
            elif key == 107 and self.list_idx > 0: # pressed k 
                self.list_idx -= 1 
            elif key == 108: #  pressed l
                stdscr.clear()
                stdscr.addstr(5, 5, "pressed eneter")
                stdscr.refresh()
                stdscr.getch()
                stdscr.clear()
            elif key == 47: # / 
                # Search box
                query = self.search_box(stdscr, w//2-5, h//2-5, 10, 10)
                logging.info(f'Search box query: {query}')
            elif key == 10: # pressed eneter
                logging.info("Pressed enter")




            elif key == 113: # pressed q 
                sys.exit(0)
                curses.curs_set(1)


            self.print_menu(stdscr, *box1)
            self.print_info(stdscr, *box2)

    def main(self): 
        logging.info(f'CursesMenu.main() - {datetime.datetime.now()}')
        curses.wrapper(self.curses_menu)



if __name__ == "__main__":
    test = ["hei kjsdf sdkjfh sdfkjadsfkj sakdjf skjfh sakfdjh sadkfjfkjsa fkjsad kjsa sakdhj sakjf sakd hsahj", "hva", "heter", "du", "jeg", "lurer"] 
    cm = CursesMenu(test)
    cm.main()
    #curses.wrapper(cm.curses_menu)

 
