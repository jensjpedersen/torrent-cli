import curses
from curses import textpad
import time

class CursesMenu: 

    def __init__(self, menu:list): 
        self.menu = menu
        self.list_idx = 0 # Current position in menu
        #self.w = curses.COLS # Terminal width
        #self.h = curses.LINES # Terminal height


    def print_menu(self, stdscr): 
        for i, e in enumerate(self.menu): 
            if self.list_idx == i:
                stdscr.addstr(i, 1, e + "\n", curses.A_STANDOUT)
            else: 
                stdscr.addstr(i, 1, e + "\n")

    def main(self, stdscr): 
        curses.curs_set(0)
        self.print_menu(stdscr)

        while True: 
            key = stdscr.getch()
            if key == 104: # pressed h
                pass
            elif key == 106: # pressed j
                self.list_idx += 1
            elif key == 107: # pressed k 
                self.list_idx -= 1 
            elif key == 108: #  pressed l
                pass
            self.print_menu(stdscr)
            stdscr.refresh()

        exit()

        h, w = stdscr.getmaxyx()
        textpad.rectangle(stdscr, 1, 1, h-2, w-2)
        stdscr.refresh()
        stdscr.getch()

        curses.curs_set(1)




if __name__ == "__main__":
    test = ["hei", "hva", "heter", "du", "jeg", "lurer"] 
    cm = CursesMenu(test)
    curses.wrapper(cm.main)

 
