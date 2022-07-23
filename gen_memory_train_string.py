import requests
import random
from playsound import playsound
import projectfilepath
from datetime import datetime, timedelta
import time
from ctypes.wintypes import WORD

COMPLETED_SOUND_FILE = "609336__kenneth-cooney__completed.wav"
DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = DATE_FORMAT + " " + "%H:%M:%S"
GLASS_SOUND_FILE = "35631__reinsamba__crystal-glass.wav"
number_chars = "0123456789"
card_number_chars = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
card_quality_chars = ["C", "D", "H", "S"]
word_file = "wordlist10000.txt"
n_item_per_row = 10
n_row_per_paragraph = 10


def print_line_separator(n_item_per_row, n_row_per_paragraph, i):
    if (i % n_item_per_row == 0):
        print()
    if (i > 0 and i % (n_item_per_row * n_row_per_paragraph) == 0):
        print()


def start_lap_time():
    playsound(projectfilepath.get_abs_path(GLASS_SOUND_FILE))
    print("\nWant to stop ? (s to stop, p to pause, e to exit) ")
    starttime = time.time()
    pause_time = 0
    while(True):
        continous = getch()
        if (continous == "s"):
            break
        if (continous == "p"):
            start_pause_time = time.time();
            input("Pausing!. Enter to un-pause.")
            pause_time += time.time() - start_pause_time
            print("Un-paused")
            continue
        if (continous == "e"):
            # dump_to_file(projectfilepath.get_abs_path("projects.json"), projects)
            pause_time = 0
            print("Stop")
            break
    laptime = round((time.time() - starttime - pause_time), 2)
    playsound(projectfilepath.get_abs_path(COMPLETED_SOUND_FILE))
    print("Lap Time: " + str(laptime) + " ( " + convert_to_minsec(laptime) + " )")
    print("*"*20)


def getch():
    import termios
    import sys, tty

    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch()


def load_from_file_lines(filename):
    with open(filename, "r") as file:
        return file.readlines();


def Main():
    while (True):
        print("\n\n1. Gen random string of number\n2. Gen random deck of cars\n3. Gen random word\ne. Exit\nYour choice: ")
        choice = getch()
        print ("Choose " + choice)
        if (choice == "1"):
            nnumber = input("Number of number? ")
            for i in range(0, int(nnumber)):
                print_line_separator(n_item_per_row, n_row_per_paragraph, i)
                print (random.randint(0, 9), end="")
            start_lap_time()
        elif (choice == "2"):
            nnumber = input("Number of card? ")
            for i in range(0, int(nnumber)):
                print_line_separator(n_item_per_row, n_row_per_paragraph, i)
                print (card_number_chars[random.randint(0, len(card_number_chars) - 1)] + card_quality_chars[random.randint(0, len(card_quality_chars) - 1)] + " ", end="")
            start_lap_time()
        elif (choice == "3"):
            WORDS = load_from_file_lines(projectfilepath.get_abs_path(word_file));
            print("**" + str(len(WORDS)));
            nnumber = input("Number of word? ")
            for i in range(0, int(nnumber)):
                print_line_separator(n_item_per_row, n_row_per_paragraph, i)
                print(WORDS[random.randint(0, len(WORDS) - 1)].decode() + ",", end="")
            start_lap_time()
        elif (choice == "e"):
            break
        else:
            print("Unsupported operator.")


def convert_to_minsec(laptime):
    laptime_round = int(round(laptime))
    mins, secs = divmod(laptime_round, 60)
    min_and_sec = '{:02d}:{:02d}'.format(mins, secs)
    return min_and_sec


Main()
