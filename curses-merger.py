from os import listdir, path
from curses import wrapper
from curses.textpad import rectangle
from PyPDF2 import PdfWriter
import curses


def main(stdscr):
    directory = "./"
    curses.curs_set(False)

    # init
    hl = 0
    offset = 0
    mode = "navigate"

    # TRUE CONSTANTS
    DIAG_BUFFER = 3
    BEGIN_WRITING = DIAG_BUFFER+1
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    GREEN = curses.color_pair(1)
    RED = curses.color_pair(2)

    # draw_rect to draw rectangles

    def draw_rect():
        # RECTANGLE DYNAMIC CONSTANTS
        # (afaik, should be "constant" unless terminal dimension changes)
        # assume terminal dimension does not change. But code to except it is
        # here just in case. Must be updated by curses.update_lines_cols()
        curses.update_lines_cols()
        global RECT_HEIGHT
        global RECT_WIDTH
        global TEXT_HEIGHT
        global TEXT_WIDTH

        curses.update_lines_cols()
        RECT_HEIGHT = curses.LINES-6
        RECT_WIDTH = curses.COLS-6
        TEXT_HEIGHT, TEXT_WIDTH = RECT_HEIGHT - 2, RECT_WIDTH - 2

        # draw rectangle.
        rectangle(stdscr, DIAG_BUFFER, DIAG_BUFFER, curses.LINES -
                  DIAG_BUFFER, curses.COLS-DIAG_BUFFER-1)

    def refresh_ls(mode):
        # Organize the ls list into directories, files when starting.
        global ls
        global dirs
        global files
        global disp_ls
        dirs = []
        files = []
        # Sort both dirs and files if not in sort mode.
        if mode == "navigate":
            ls = listdir(directory)
            for item in ls:
                if path.isdir(directory+item):
                    dirs.append(item+'/')
                else:
                    files.append(item)
            dirs.sort()
            files.sort()
            ls = dirs + files

        # Truncate appropriately based on RECT_HEIGHT
        # Take away 1 to fit IN the rectangle.
        disp_ls = ls[offset:RECT_HEIGHT-1+offset]
        stdscr.addstr(1, 1, str(mode))  # debug DELETE.

    def draw_highlight(mode=False):
        global ls
        stdscr.addstr(
            2, 1, f"{hl} {TEXT_HEIGHT} {offset} {directory}")  # debug DELETE.
        for i in range(len(disp_ls)):
            if mode == "pre-compile":
                stdscr.addstr(BEGIN_WRITING+i, BEGIN_WRITING,
                              str(i+1) + ". " + disp_ls[i])
            else:
                stdscr.addstr(BEGIN_WRITING+i, BEGIN_WRITING,
                              disp_ls[i], curses.A_STANDOUT if i == hl else curses.A_NORMAL)

                # Adds space padding (to the right) after the displayed the text
                stdscr.addstr(BEGIN_WRITING+i, BEGIN_WRITING+len(disp_ls[i]), ' '*(TEXT_WIDTH-len(disp_ls[i])))

        # adds spacing below last element, if there are still more elements.
        if len(disp_ls) < RECT_HEIGHT:
            for i in range(BEGIN_WRITING+len(disp_ls), BEGIN_WRITING+TEXT_HEIGHT+1):
                stdscr.addstr(i, BEGIN_WRITING, ' '*TEXT_WIDTH)
        # More files below!
        if offset <= len(ls)-TEXT_HEIGHT-2:
            stdscr.addstr(BEGIN_WRITING+RECT_HEIGHT-2,
                          BEGIN_WRITING-2, "⋁", RED)
        else:
            stdscr.addstr(BEGIN_WRITING+RECT_HEIGHT-2,
                          BEGIN_WRITING-2, " ")

        # More files above!
        if offset != 0:
            stdscr.addstr(BEGIN_WRITING, BEGIN_WRITING -
                          2, "⋀", GREEN)
        else:
            stdscr.addstr(BEGIN_WRITING, BEGIN_WRITING -
                          2, " ")
    def show_instructions(mode):
        # Instructions:
        if mode == "navigate":
            stdscr.addstr(RECT_HEIGHT+BEGIN_WRITING, BEGIN_WRITING,
                          "^X to PDF\t ^A Sort mode \t ✥(navigate)")
        elif mode == "sort":
            stdscr.addstr(RECT_HEIGHT+BEGIN_WRITING, BEGIN_WRITING,
                          "^X to PDF.\t^A Navigate mode\t⇄(sort) ⇅(select)\t[D] (omit file from PDF)")
        elif mode == "pre-compile":
            stdscr.addstr(RECT_HEIGHT+BEGIN_WRITING, BEGIN_WRITING,
                          "^X to continue\t^A Sort mode")

    draw_rect()
    refresh_ls(mode)
    draw_highlight()
    show_instructions(mode)
    # Init display
    stdscr.refresh()

    #

    #

    #

    # LOOP
    while True:
        global ls
        # New frame

        # Keypress handler
        key = stdscr.getch()

        # If key is pressed, update the screen.
        if key != -1: 
            if key == 113:  # If q is pressed, forget everything, just quit.
                break
            # Navigate mode
            if mode == "navigate":
                # Key controls to navigate through the file system
                if key == 258:  # DOWN
                    # If hl is on the bottom, and there are more files
                    if (hl == TEXT_HEIGHT) and offset <= len(ls)-TEXT_HEIGHT-2:
                        offset += 1
                    # hl is not on the bottom and there are more files
                    elif (hl < TEXT_HEIGHT) and offset+hl+1 < len(ls):
                        hl += 1
                elif key == 259:  # UP
                    # If hl is on the top, and there are more files
                    if (hl == 0) and offset != 0:
                        offset -= 1
                    # hl is not on the top
                    elif (hl != 0):
                        hl -= 1
                elif key == 261 and hl+offset < len(dirs):  # RIGHT
                    # Right key pressed, and selecting directory
                    directory += ls[hl+offset]
                    hl = 0
                    offset = 0
                elif key == 260 and directory != "./":  # LEFT
                    # Left key pressed, not ./
                    hl = 0
                    offset = 0
                    directory = '/'.join(directory.split('/')[:-2])+'/'
                elif key == 1:  # ^A
                    # Sort mode to init sort mode
                    # start by setting ls to only files.
                    ls = files
                    mode = "sort"
            elif mode == "sort":
                if key == 1:  # ^A
                    # Back to navigate mode (everything will return)
                    mode = "navigate"
                elif key == 261 and hl+offset+1 < len(ls):  # RIGHT
                    temp = ls[hl+offset+1]
                    ls[hl+offset+1] = ls[hl+offset]
                    ls[hl+offset] = temp
                    if hl == RECT_HEIGHT-2:
                        offset += 1
                    else:
                        hl += 1

                elif key == 260 and hl+offset-1 != -1:  # LEFT
                    temp = ls[hl+offset-1]
                    ls[hl+offset-1] = ls[hl+offset]
                    ls[hl+offset] = temp
                    if hl == 0:
                        offset -= 1
                    else:
                        hl -= 1
                elif key == 258:  # DOWN
                    # If hl is on the bottom, and there are more files
                    if (hl == TEXT_HEIGHT) and offset <= len(ls)-TEXT_HEIGHT-2:
                        offset += 1
                    # hl is not on the bottom and there are more files
                    elif (hl < TEXT_HEIGHT) and offset+hl+1 < len(ls):
                        hl += 1
                elif key == 259:  # UP
                    # If hl is on the top, and there are more files
                    if (hl == 0) and offset != 0:
                        offset -= 1
                    # hl is not on the top
                    elif (hl != 0):
                        hl -= 1
                elif key == 100:
                    del ls[offset+hl]
                elif key == 24:  # compile
                    mode = "pre-compile"
            elif mode == "pre-compile":
                if key == 1:  # ^A
                    # Back to sort mode (everything will return)
                    mode = "sort"
                if key == 24:
                    # ACTUALLY COMPILE THIS TIME.
                    merger = PdfWriter()
                    for pdf in ls:
                        merger.append(directory+pdf)
                    merger.write(directory+"merged.pdf")
                    merger.close()
                    break
                    pass

            stdscr.addstr(2, 57, f"[{key}]")
            # Redraw rectangle every time.
            draw_rect()
            refresh_ls(mode)
            draw_highlight(mode)
            show_instructions(mode)
            stdscr.refresh()


wrapper(main)
