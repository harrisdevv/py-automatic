import time
from datetime import datetime, timedelta
import os
from playsound import playsound
import projectfilepath
import re
from colorama import Fore
import multiprocessing
from pydub import AudioSegment
from pydub.playback import play
import random
import threading
import json
from threading import Timer
import sys, select
from tkinter import *
import recorder
import tkinter.ttk as ttk
import textwrap
import pygame
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from routine import (
    speak,
    append_to_dayplanner,
    record,
    playsound_random,
    COMPLETED_SOUND_FILES,
)

LOOT_SOUND_FILES = [
    "chest-opening-87569.mp3",
    "harp-glissando-descending-short-103886.mp3",
    "happy-harp-sound-103882.mp3",
    "short-success-sound-glockenspiel-treasure-video-game-6346.mp3",
]

datetimes = []

is_sound_on = True


def convert_to_minsec(laptime):
    laptime_round = int(round(laptime))
    hours, mins = divmod(laptime_round, 3600)
    mins, secs = divmod(mins, 60)
    min_and_sec = (
        "{:d}:{:d}".format(mins, secs)
        if hours == 0
        else "{:d}:{:d}:{:d}".format(hours, mins, secs)
    )
    return min_and_sec


def small_window(prompt=""):
    global is_sound_on

    def trigger_record(event=None):
        path = str(datetime.now()) + ".wav"
        text = record(path, 30)
        append_to_dayplanner("?] " + text + " " + path, datetime.now())
        play_sound(COMPLETED_SOUND_FILES)

    def loot(event=None):
        num_loot.set(str(int(num_loot.get()) + 1))
        global datetimes
        datetimes.append(datetime.now().timestamp())
        play_sound(COMPLETED_SOUND_FILES)

    def reset_loot(event=None):
        num_loot.set(str(0))
        global datetimes
        line_str = ""
        local_avg = 0
        if len(datetimes) > 0:
            line_str += (
                str(datetime.fromtimestamp(int(datetimes[0])).strftime("%H:%M:%S"))
                + ","
            )
        for i in range(1, len(datetimes)):
            diff = datetimes[i] - datetimes[i - 1]
            local_avg += diff
            # line_str += str("{:2.1f}".format(diff)) + ", "
        if len(datetimes) > 1:
            line_str += " avg: " + str(
                "{:2.1f}".format(local_avg / (len(datetimes) - 1)) + " s"
            )
        if len(datetimes) > 0:
            append_to_dayplanner(
                "Total: "
                + str(len(datetimes))
                + ", detail: "
                + line_str
                + ", end: "
                + str(datetime.fromtimestamp(int(datetimes[-1])).strftime("%H:%M:%S"))
                + ", len: "
                + ((convert_to_minsec(datetimes[-1] - datetimes[0])) if len(datetimes) > 1 else "0")
                ,
                datetime.now(),
            )
        datetimes = []
        play_sound(LOOT_SOUND_FILES)

    def play_sound(list):
        if is_sound_on:
            threading.Thread(target=playsound_random, args=(list,)).start()

    def reset_loot_no_save(event=None):
        global datetimes
        num_loot.set(str(0))
        datetimes = []

    def toogle_turn_sound(event=None):
        # global sound_lbl
        global is_sound_on
        is_sound_on = not is_sound_on
        sound_lbl.set("🎵" if is_sound_on else "🔇")

    root = Tk(className=prompt)
    root.overrideredirect(True)
    root.withdraw()
    window = Toplevel(root)
    img = PhotoImage(
        file="/home/hienphan/Desktop/code/script/py-automatic/resources/app_icon.png"
    )
    window.iconphoto(False, img)

    window.resizable(False, False)

    window_height = 35
    window_width = 210

    screen_width = window.winfo_screenwidth()

    x_cordinate = screen_width - 50
    y_cordinate = 50

    window.geometry(
        "{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate)
    )
    num_loot = StringVar()
    label = Label(window, textvariable=num_loot, relief=RAISED)
    label.config(font=("Helvetica bold", 14))
    num_loot.set(str(0))
    label.pack(side="left")

    def check_loot(event):
        if event.char == " ":
            loot(event)

    # master.bind("<Button-1>", record)
    window.bind("<Return>", loot)
    window.bind("<KeyPress>", check_loot)
    window.bind("<Shift_L>", reset_loot)

    Button(window, width=1, text="📣", command=trigger_record).pack(side="left")
    Button(window, width=2, text="✅E,Sp", command=loot).pack(side="left")
    Button(window, width=2, text="💾Sh", command=reset_loot).pack(side="left")
    Button(window, width=1, text="❌", command=reset_loot_no_save).pack(side="left")
    sound_lbl = StringVar()
    sound_lbl.set("🎵" if is_sound_on else "🔇")
    Button(window, width=1, textvariable=sound_lbl, command=toogle_turn_sound).pack(
        side="left"
    )

    root.mainloop()


def window(prompt=""):
    def record(event=None):
        speak("Start")
        path, text = recording(40)
        append_to_dayplanner("?] " + text + " " + path, datetime.now())
        threading.Thread(target=playsound_random, args=(COMPLETED_SOUND_FILES,)).start()

    def loot(event=None):
        num_loot.set(str(int(num_loot.get()) + 1))
        global datetimes
        datetimes.append(datetime.now().timestamp())

        t_list_str = ""
        MAX_REC_DISPLAY = 1
        min_index = (
            len(datetimes) - MAX_REC_DISPLAY
            if len(datetimes) - MAX_REC_DISPLAY > 0
            else 0
        )
        for id in range(min_index, len(datetimes)):
            t = datetimes[id]
            t_list_str += datetime.fromtimestamp(int(t)).strftime("%M:%S")
            if id > 0:
                t_list_str += (
                    " (" + str("{:2.1f}".format(t - datetimes[id - 1])) + " s)"
                )
            t_list_str += "\n"
        history_timestamp_loot.set(t_list_str)
        threading.Thread(target=playsound_random, args=(LOOT_SOUND_FILES,)).start()

    def reset_loot(event=None):
        num_loot.set(str(0))
        global datetimes

        line_str = ""
        local_avg = 0
        if len(datetimes) > 0:
            line_str += (
                str(datetime.fromtimestamp(int(datetimes[0])).strftime("%H:%M:%S"))
                + ","
            )
        for i in range(1, len(datetimes)):
            diff = datetimes[i] - datetimes[i - 1]
            local_avg += diff
            line_str += str("{:2.1f}".format(diff)) + ", "
        if len(datetimes) > 1:
            line_str += ", avg: " + str(
                "{:2.1f}".format(local_avg / (len(datetimes) - 1)) + " s"
            )
        if len(datetimes) > 0:
            append_to_dayplanner(
                +"Total: "
                + str(len(datetimes))
                + ", detail: "
                + line_str
                + ", end: "
                + str(datetime.fromtimestamp(int(datetimes[-1])).strftime("%H:%M:%S"))
                + ", len: "
                + (str(datetimes[-1] - datetimes[0]) if len(datetimes) > 1 else "0"),
                datetime.now(),
            )
        datetimes = []
        history_timestamp_loot.set("")
        threading.Thread(target=playsound_random, args=(LOOT_SOUND_FILES,)).start()

    master = Tk(className=prompt)
    master.resizable(False, False)

    window_height = 130
    window_width = 350

    screen_width = master.winfo_screenwidth()

    x_cordinate = screen_width - 50
    y_cordinate = 50

    master.geometry(
        "{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate)
    )
    num_loot = StringVar()
    label = Label(master, textvariable=num_loot, relief=RAISED)
    label.config(font=("Helvetica bold", 17))
    num_loot.set(str(0))
    label.pack(side="left")

    master.bind("<Return>", record)
    master.bind("<Alt_L>", loot)
    master.bind("<Shift_L>", reset_loot)

    history_timestamp_loot = StringVar()
    label2 = Label(master, textvariable=history_timestamp_loot, relief=RAISED)
    label2.config(font=("Helvetica bold", 15))
    label2.pack(side="bottom")

    Button(master, width=10, text="Record(Enter)", command=record).pack(side="left")
    Button(master, width=10, text="Loot(Alt)", command=loot).pack(side="left")
    Button(master, width=10, text="Reset(Shift)", command=reset_loot).pack(side="left")

    master.mainloop()


if __name__ == "__main__":
    small_window("Looting")
