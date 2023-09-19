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
from tkinter import *
from tkinter import ttk
import math

# from lap_timer import doing
doing = False

# 5 x 5 = 25 min work then relax 5, count to 3 then relax 30
NOTIFY_INTERVAL_MIN = (
    5  # min to nofity to set 5-min block is Success, or fail (distracted)
)
SUCCESS_BEFORE_SHORT_RELAX = (
    8  # 5 # number of time 5-min block of success will Get short relaxing reward
)
SHORT_RELAX_BEFORE_LONG_RELAX = 2  # number of short relax to lead to 1 long relax
MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX = (
    int(round(SUCCESS_BEFORE_SHORT_RELAX / 2)) + 1
)
MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX = int(round(SUCCESS_BEFORE_SHORT_RELAX * 1.5))

SHORT_RELAX_MIN = 5
LONG_RELAX_MIN = 20

short_success_count = 0
consecutive_fail_count = 0
short_relax_consecutive_count = 0


class Bool(object):
    def __init__(self, start):
        self.lock = threading.Lock()
        self.value = start

    def makeTrue(self):
        self.lock.acquire()
        try:
            self.value = True
        finally:
            self.lock.release()

    def makeFalse(self):
        self.lock.acquire()
        try:
            self.value = False
        finally:
            self.lock.release()


relaxing = Bool(False)
BELL_RING_FILE = "bell-ringing-04.wav"
SHORT_TICK_FILE = "tick-tock2.mp3"
MIMIC_VOICE_BIN_PATH = "/home/hienphan/mimic1/mimic"
FUNNY_SONG = ["fun_tracks_combined.mp3", "fun_tracks_combined_2.mp3"]
COMPLETED_SOUND_FILES = [
    "609336__kenneth-cooney__completed.wav",
    "goodresult-82807.mp3",
    "yay-6120.mp3",
    "success-fanfare-trumpets-6185.mp3",
    "success-1-6297.mp3",
]
FAIL_SOUND_FILES = [
    "failure-drum-sound-effect-2-7184.mp3",
    "negative_beeps-6008.mp3",
    "fail-144746.mp3",
]
RELAX_SOUND_FILES = [
    "morning-garden-acoustic-chill-15013.mp3",
    "mindfulness-relaxation-amp-meditation-music-22174.mp3",
]
RELAX_SOUND_FILES_2 = [
    "relax.mp3",
]
r = sr.Recognizer()


class Duration:
    def __init__(self, start, end):
        self.start = start
        self.end = end


durations = [
    # Duration("06:01", "21:00")
    Duration("06:01", "10:45"),  # 4h45
    Duration("11:31", "16:45"),  # 4h45
    Duration("18:01", "20:00"),  # 1h
]

work_statuses = []

def highlight_text(text):
    return f"{Fore.GREEN}{text}{Fore.WHITE}"
class Routine:
    def __init__(self, time, voice):
        self.time = time
        self.voice = voice

    def is_cmd(self):
        return self.voice.startswith("cmd")

    def execute(self):
        if self.is_cmd():
            find_separator = self.voice.find(":")
            if find_separator > 0:
                cmd = self.voice[find_separator + 1 :]
                os.system(cmd)
            else:
                print("Missing ':' in cmd routine. " + str(self))
        else:
            print("🍅 " + self.time + ": " + self.voice)
            for i in range(0, 1):
                playsound(projectfilepath.get_abs_path(BELL_RING_FILE))
                speak(self.voice)

    def __str__(self) -> str:
        return highlight_text(self.time) + " " + self.voice


def playsound_random(songs):
    playsound(projectfilepath.get_abs_path(songs[random.randint(0, len(songs) - 1)]))


def playsound_random_times(songs, times):
    for i in range(0, times):
        playsound(
            projectfilepath.get_abs_path(songs[random.randint(0, len(songs) - 1)])
        )
    global relaxing
    relaxing.makeFalse()


def playsound_vol_random(songs, volumn=0.5):
    playsound_vol(
        projectfilepath.get_abs_path(songs[random.randint(0, len(songs) - 1)]), volumn
    )


def playsound_vol(path, volumn=0.5):
    pygame.init()
    pygame.mixer.init()
    sound = pygame.mixer.Sound(projectfilepath.get_abs_path(path))
    sound.set_volume(volumn)
    sound.play()


def transcribe_audio(path):
    try:
        with sr.AudioFile(path) as source:
            audio_listened = r.record(source)
            text = r.recognize_google(audio_listened)
        return text
    except Exception as e:
        # print("err: " + str(e))
        return ""


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def recording(time_rec, file_name=str(datetime.now()) + ".wav"):
    speak("start")
    abs_path = "/home/hienphan/Desktop/notes/voice/" + file_name
    obsidian_path = "![[voice/" + file_name + "]]"
    try:
        sys.stdout, sys.stderr = os.devnull, os.devnull
        rec = recorder.Recorder(channels=2)
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__

        rec.record(time_rec, abs_path)
        speak("stop")
        return obsidian_path, transcribe_audio(abs_path)
    except Exception as e:
        # print("err: " + str(e))
        return obsidian_path, ""


def input_restrict_time(prompt="", time=20, routine=""):
    global work_statuses
    global NOTIFY_INTERVAL_MIN

    def callback_success_record(event=None):
        record_path, text = recording(time)
        append_to_dayplanner(
            "+] " + e.get() + "/" + text + " " + record_path,
            datetime.today() - timedelta(hours=0, minutes=NOTIFY_INTERVAL_MIN),
        )
        print(time + "✅")
        work_statuses.append("+")
        window.quit()
        window.destroy()
        playsound_random(COMPLETED_SOUND_FILES)

    def callback_success_norecord(event=None):
        append_to_dayplanner(
            "+] " + e.get(),
            datetime.today() - timedelta(hours=0, minutes=NOTIFY_INTERVAL_MIN),
        )
        print(time + "✅")
        work_statuses.append("+")
        window.quit()
        window.destroy()
        playsound_random(COMPLETED_SOUND_FILES)

    def callback_fail_record(event=None):
        record_path, text = recording(time)
        append_to_dayplanner(
            "-] " + e.get() + "/" + text + " " + record_path,
            datetime.today() - timedelta(hours=0, minutes=NOTIFY_INTERVAL_MIN),
        )
        work_statuses.append("-")
        window.quit()
        window.destroy()
        playsound_random(FAIL_SOUND_FILES)

    def callback_fail_norecord(event=None):
        append_to_dayplanner(
            "-] " + e.get(),
            datetime.today() - timedelta(hours=0, minutes=NOTIFY_INTERVAL_MIN),
        )
        work_statuses.append("-")
        window.quit()
        window.destroy()
        playsound_random(FAIL_SOUND_FILES)

    def refresher():
        time_left.set(int(time_left.get()) - 1)
        window.after(1000, refresher)

    window = Tk(className=prompt)
    # img = PhotoImage(
    #     file="/home/hienphan/Desktop/code/script/py-automatic/resources/app_icon.png"
    # )
    # window.iconphoto(False, img)
    backbuttonimg = PhotoImage(
        file="/home/hienphan/Desktop/code/script/py-automatic/resources/app_icon.png",
        master=window,
    )
    speak(prompt)
    window.after(time * 1000, callback_fail_norecord)
    window.after(1000, refresher)
    window.resizable(False, False)

    window_height = 120
    window_width = 350

    screen_width = window.winfo_screenwidth()

    x_cordinate = screen_width - 50
    y_cordinate = 50

    window.geometry(
        "{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate)
    )

    cntS = cntF = 0
    for i in work_statuses:
        if i == "+":
            cntS += 1
        if i == "-":
            cntF += 1
    content = (
        "+"
        + str("{:2.1f}".format((cntS * NOTIFY_INTERVAL_MIN / 60)))
        + "h"
        + ", -"
        + str("{:2.1f}".format(cntF * NOTIFY_INTERVAL_MIN / 60))
        + "h | "
        + str(work_statuses[-3:])
        + " Do: "
        + routine
    )
    Label(window, text=content, relief=RAISED, wraplength=330).pack()

    time_left = StringVar()
    label_time_left = Label(window, textvariable=time_left, relief=RAISED)
    time_left.set(time)
    label_time_left.pack()

    e = Entry(window, width=350)
    e.pack()
    e.focus_set()
    e.bind("<Return>", callback_success_record)
    e.bind("<Tab>", callback_success_norecord)
    e.bind("<Shift_L>", callback_fail_record)
    e.bind("<Alt_L>", callback_fail_norecord)

    Button(window, width=7, text="S R(Enter)", command=callback_success_record).pack(
        side="left"
    )
    Button(window, width=8, text="S xR(Tab)", command=callback_success_norecord).pack(
        side="left"
    )
    Button(window, width=7, text="F R(Shift)", command=callback_fail_record).pack(
        side="left"
    )
    Button(window, width=9, text="F xR(Alt)", command=callback_fail_norecord).pack(
        side="left"
    )

    mainloop()


def record(abs_path, rec_time):
    try:
        # sys.stdout, sys.stderr = os.devnull, os.devnull
        old_stdout = sys.stdout  # backup current stdout
        sys.stdout = open(os.devnull, "w")

        rec = recorder.Recorder(channels=2)
        rec.record(rec_time, abs_path)

        sys.stdout = old_stdout  # reset old stdout

        # sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
        rec.close()
        return transcribe_audio(abs_path)
    except:
        return ""


def input_restrict_time_sound(prompt="", time=20, routine="", extra_time=30):
    global work_statuses
    global NOTIFY_INTERVAL_MIN

    def add_new_record(rec_time, get_more_sec):
        # playsound_thread(rec_time)
        threading.Thread(
            target=speak,
            args=(prompt,),
        ).start()
        if get_more_sec:
            threading.Thread(
                target=speak,
                args=("more " + str(rec_time) + " seconds",),
            ).start()
        # speak(prompt)
        # now = datetime.now()
        time = (
            datetime.today() - timedelta(hours=0, minutes=NOTIFY_INTERVAL_MIN)
        ).strftime("%H:%M")
        file_name = "5min_complete_rec.wav"
        abs_path = "/home/hienphan/Desktop/notes/voice/" + file_name
        obs_path = "![[voice/" + file_name + "]]"
        text = record(abs_path, rec_time)
        if text != "":
            print(", you said: " + text, end="\r")
        if len(text) == 0:
            if not get_more_sec:
                append_to_dayplanner(
                    "-] ",
                    datetime.today() - timedelta(hours=0, minutes=NOTIFY_INTERVAL_MIN),
                )
                print(time + "❌")
                work_statuses.append("-")
                threading.Thread(
                    target=playsound_random,
                    args=(FAIL_SOUND_FILES,),
                ).start()
            return False
        elif "done" in text.lower() or "yes" in text.lower() or "yeah" in text.lower():
            append_text = ("+] " if not get_more_sec else "") + " ".join(
                text.split(" ")[1:]
            )
            # if len(text.split(" ")) > 1:
            # append_text += " " + obs_path
            if not get_more_sec:
                append_to_dayplanner(
                    append_text,
                    datetime.today() - timedelta(hours=0, minutes=NOTIFY_INTERVAL_MIN),
                )
                print(time + "✅")
                work_statuses.append("+")
                # threading.Thread(
                #     target=playsound_random,
                #     args=(COMPLETED_SOUND_FILES,),
                # ).start()
            if "more second" in text.lower():
                add_new_record(extra_time, True)
            return True
        elif text.lower().startswith("no"):
            append_text = ("-] " if not get_more_sec else "") + " ".join(
                text.split(" ")[1:]
            )
            # if len(text.split(" ")) > 1:
            #     append_text += " " + obs_path
            if not get_more_sec:
                append_to_dayplanner(
                    append_text,
                    datetime.today() - timedelta(hours=0, minutes=NOTIFY_INTERVAL_MIN),
                )
                print(time + "❌")
                work_statuses.append("-")
                threading.Thread(
                    target=playsound_random,
                    args=(FAIL_SOUND_FILES,),
                ).start()
            if "more second" in text.lower():
                add_new_record(extra_time, True)
            return False
        else:
            if len(text.split(" ")) > 0:
                append_to_dayplanner(
                    ("-]? " if not get_more_sec else "") + text + " " + obs_path,
                    datetime.today() - timedelta(hours=0, minutes=NOTIFY_INTERVAL_MIN),
                )
                if not get_more_sec:
                    print(time + "❌")
                    work_statuses.append("-")
                    threading.Thread(
                        target=playsound_random,
                        args=(FAIL_SOUND_FILES,),
                    ).start()
            return False

    return add_new_record(time, False)


def printd(text, date):
    if date == None:
        date = datetime.now()
    print(date.strftime("%H:%M:%S") + " " + str(text))


def speaknprint(text):
    printd(text, None)
    speak(text)


def speak(text):
    text = str(text)
    voice_cmd = MIMIC_VOICE_BIN_PATH + ' -t "' + text + '" -voice slt'
    os.system(voice_cmd)


def highlight_text(text):
    return f"{Fore.GREEN}{text}{Fore.WHITE}"


def load_routine_from_file(filename):
    routines = []
    with open(filename, "r") as file:
        for line in file.readlines():
            index_first_space = line.find(" ")
            time = line[:index_first_space]
            task = line[index_first_space + 1 :].rstrip()
            routines.append(Routine(time, task))
    return routines


def load_routine_from_day_planner(text, is_print_routines=False):
    global work_statuses
    global short_success_count
    global short_relax_consecutive_count
    global consecutive_fail_count
    work_statuses = []
    now = datetime.now()
    DAYPLANNER_FILE = (
        "/home/hienphan/Desktop/notes/Day Planners/Day Planner-"
        + now.strftime("%Y%m%d")
        + ".md"
    )
    routines = []
    short_success_count = 0
    short_relax_consecutive_count = 0
    consecutive_fail_count = 0
    with open(DAYPLANNER_FILE, "r") as file:
        for line in file.readlines():
            if len(line) < 9:
                continue
            if line.startswith("- [ ] ") and line[8] == ":":
                time = line[6:11]
                task = line[12:].rstrip()
                routines.append(Routine(time, task))
            if "+]" in line:
                if is_print_routines:
                    print(line.strip()[0:5] + "✅")
                    if text != None:
                        text.insert(END, line.strip()[0:5] + "✅")
                work_statuses.append("+")

                short_success_count += 1
                if short_success_count >= SUCCESS_BEFORE_SHORT_RELAX:
                    short_success_count -= SUCCESS_BEFORE_SHORT_RELAX
                    if short_relax_consecutive_count >= SHORT_RELAX_BEFORE_LONG_RELAX:
                        short_relax_consecutive_count -= SHORT_RELAX_BEFORE_LONG_RELAX
                    else:
                        short_relax_consecutive_count += 1
                consecutive_fail_count = 0
            if "-]" in line:
                consecutive_fail_count += 1
                if is_print_routines:
                    print(line.strip()[0:5] + "❌")
                    if text != None:
                        text.insert(END, line.strip()[0:5] + "❌")
                work_statuses.append("-")
                if consecutive_fail_count >= MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX:
                    short_success_count = 0
                if consecutive_fail_count >= MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX:
                    short_relax_consecutive_count = 0
    return routines


def print_routines(routines):
    print("\n-------------------Day Planner---------------")
    for routine in routines:
        if not routine.is_cmd():
            print("At " + highlight_text(routine.time) + " | " + routine.voice)
    print("----------------------------------------------\n")


def transform_same_task(routine_from_dayplanner):
    idx = 1
    section_num = 2
    origin = None
    while idx < len(routine_from_dayplanner):
        if (
            routine_from_dayplanner[idx].voice == "."
            and not routine_from_dayplanner[idx - 1].is_cmd()
        ):
            if origin == None:
                origin = routine_from_dayplanner[idx - 1].voice
                routine_from_dayplanner[idx - 1].voice = (
                    # "1, " + routine_from_dayplanner[idx - 1].voice
                    routine_from_dayplanner[idx - 1].voice
                )
            # routine_from_dayplanner[idx].voice = str(section_num) + " Do " + origin
            routine_from_dayplanner[idx].voice = origin
            section_num += 1
        else:
            origin = None
            section_num = 2
        idx += 1


def concate_voice_same_time_task(routines, pattern):
    idx = 0
    while idx < len(routines):
        if idx == len(routines) - 1:
            idx += 1
        elif pattern.match(routines[idx].time) == None:
            del routines[idx]
        else:
            next_idx = idx + 1
            while (
                next_idx < len(routines)
                and routines[idx].time == routines[next_idx].time
            ):
                routines[idx].voice += "; " + routines[next_idx].voice
                del routines[next_idx]
            idx += 1


def check_time_in_flow(time):
    global durations
    for dur in durations:
        if time >= dur.start and time <= dur.end:
            return True
    return False


def update_time_execute():
    now = datetime.now()
    DAYPLANNER_FILE = (
        "/home/hienphan/Desktop/notes/Day Planners/Day Planner-"
        + now.strftime("%Y%m%d")
        + ".md"
    )
    global short_relax_consecutive_count
    global short_success_count
    with open(DAYPLANNER_FILE, "r") as in_file:
        buf = in_file.readlines()

    exist_relax_5_consecutive_count = False
    exist_count_success = False
    with open(DAYPLANNER_FILE, "w") as out_file:
        for line in buf:
            if "Time Do:" in line:
                out_file.write(
                    line.split(":")[0]
                    + ": "
                    + "{:2.1f}".format(len(work_statuses) * NOTIFY_INTERVAL_MIN / 60)
                    + " hour\n"
                )
            elif "Time Success:" in line:
                out_file.write(
                    line.split(":")[0]
                    + ": "
                    + "{:2.1f}".format(
                        work_statuses.count("+") * NOTIFY_INTERVAL_MIN / 60
                    )
                    + " hour\n"
                )
            elif "Time Fail:" in line:
                out_file.write(
                    line.split(":")[0]
                    + ": "
                    + "{:2.1f}".format(
                        work_statuses.count("-") * NOTIFY_INTERVAL_MIN / 60
                    )
                    + " hour\n"
                )
            elif "relax_5_consecutive_count:" in line:
                out_file.write(
                    line.split(":")[0]
                    + ": "
                    + str(short_relax_consecutive_count)
                    + "\n"
                )
                exist_relax_5_consecutive_count = True
            elif "count_success:" in line:
                out_file.write(
                    line.split(":")[0] + ": " + str(short_success_count) + "\n"
                )
                exist_count_success = True
            else:
                out_file.write(line)
        if not exist_relax_5_consecutive_count:
            out_file.write(
                "relax_5_consecutive_count: "
                + str(short_relax_consecutive_count)
                + "\n"
            )
        if not exist_count_success:
            out_file.write("count_success: " + str(short_success_count) + "\n")


def playsound_thread(time_sec):
    def playsound_wait(secs):
        time_do = 0
        SLEEP_TIME = 4
        max_ping = int(secs / (SLEEP_TIME + 0.1))
        cnt = 0
        while time_do < secs:
            time_start = datetime.now().timestamp()
            # playsound(projectfilepath.get_abs_path(SHORT_TICK_FILE))
            time.sleep(SLEEP_TIME)
            if max_ping - cnt > 0:
                speak(max_ping - cnt)
            cnt += 1
            time_do += datetime.now().timestamp() - time_start

    try:
        thread = threading.Thread(target=playsound_wait, args=(time_sec,))
        thread.start()
    except Exception as e:
        # print("err: " + str(e))
        thread.join()


class LabelEntry(ttk.Frame):
    def __init__(self, parent, text, button=None):
        super().__init__(parent)
        self.pack(fill=ttk.X)

        lbl = ttk.Label(self, text=text, width=14, anchor="w")
        lbl.pack(side=ttk.LEFT, padx=5, pady=5)


def gui_config():
    root = Tk(className="Configuration")
    root.withdraw()
    window = Toplevel(root)
    # img = PhotoImage(
    #     file="/home/hienphan/Desktop/code/script/py-automatic/resources/app_icon.png"
    # )
    # root.iconphoto(False, img)
    window.resizable(False, False)
    frame_width = 150
    window.geometry(str(frame_width) + "x470")

    def make_label(text, size=9):
        label = Label(
            window,
            text=str(text),
            relief=RAISED,
            wraplength=frame_width,
            justify="left",
            anchor="w",
            font="Georgia " + str(size),
            borderwidth=0,
            highlightthickness=0,
        )
        return label

    label_description = make_label("", 11)
    label_description.pack()

    def set_label_and_input(label_text):
        label = make_label(label_text)
        label.pack()
        entry = Entry(window, font="Georgia 9", width=5)
        return entry

    def reset_config_label():
        global NOTIFY_INTERVAL_MIN
        global SUCCESS_BEFORE_SHORT_RELAX
        global SHORT_RELAX_BEFORE_LONG_RELAX
        global MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX
        global MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX
        global SHORT_RELAX_MIN
        global LONG_RELAX_MIN

        def set_text_to_entry(entry, text):
            entry.delete(0, END)
            entry.insert(0, text)

        set_text_to_entry(input_NOTIFY_INTERVAL_MIN, str(NOTIFY_INTERVAL_MIN))
        set_text_to_entry(
            input_SUCCESS_BEFORE_SHORT_RELAX, str(SUCCESS_BEFORE_SHORT_RELAX)
        )
        set_text_to_entry(
            input_SHORT_RELAX_BEFORE_LONG_RELAX, str(SHORT_RELAX_BEFORE_LONG_RELAX)
        )
        set_text_to_entry(
            input_MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX,
            str(MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX),
        )
        set_text_to_entry(
            input_MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX,
            str(MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX),
        )
        set_text_to_entry(input_SHORT_RELAX_MIN, str(SHORT_RELAX_MIN))
        set_text_to_entry(input_LONG_RELAX_MIN, str(LONG_RELAX_MIN))
        global short_success_count
        global consecutive_fail_count
        global short_relax_consecutive_count
        label_description.configure(
            text="(Do "
            + str(SUCCESS_BEFORE_SHORT_RELAX * NOTIFY_INTERVAL_MIN)
            + "m then relax "
            + str(SHORT_RELAX_MIN)
            + "m) "
            + str(SHORT_RELAX_BEFORE_LONG_RELAX)
            + " times then long relax "
            + str(LONG_RELAX_MIN)
            + "m\n"
            + "s:"
            + str(short_success_count)
            + ",ss:"
            + str(short_relax_consecutive_count)
            + ",f:"
            + str(consecutive_fail_count)
        )

    input_SUCCESS_BEFORE_SHORT_RELAX = set_label_and_input("SUCCESS_BEFORE_SHORT_RELAX")
    input_SUCCESS_BEFORE_SHORT_RELAX.pack()
    input_NOTIFY_INTERVAL_MIN = set_label_and_input("NOTIFY_INTERVAL_MIN")
    input_NOTIFY_INTERVAL_MIN.pack()
    input_SHORT_RELAX_BEFORE_LONG_RELAX = set_label_and_input(
        "SHORT_RELAX_BEFORE_LONG_RELAX"
    )
    input_SHORT_RELAX_BEFORE_LONG_RELAX.pack()
    input_MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX = set_label_and_input(
        "MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX"
    )
    input_MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX.pack()
    input_MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX = set_label_and_input(
        "MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX"
    )
    input_MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX.pack()
    input_SHORT_RELAX_MIN = set_label_and_input("SHORT_RELAX_MIN")
    input_SHORT_RELAX_MIN.pack()
    input_LONG_RELAX_MIN = set_label_and_input("LONG_RELAX_MIN")
    input_LONG_RELAX_MIN.pack()
    reset_config_label()

    def set_config(event=None):
        global NOTIFY_INTERVAL_MIN
        global SUCCESS_BEFORE_SHORT_RELAX
        global SHORT_RELAX_BEFORE_LONG_RELAX
        global MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX
        global MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX
        global SHORT_RELAX_MIN
        global LONG_RELAX_MIN
        if input_NOTIFY_INTERVAL_MIN.get() != "":
            NOTIFY_INTERVAL_MIN = int(input_NOTIFY_INTERVAL_MIN.get())
        if input_SUCCESS_BEFORE_SHORT_RELAX.get() != "":
            SUCCESS_BEFORE_SHORT_RELAX = int(input_SUCCESS_BEFORE_SHORT_RELAX.get())
        if input_SHORT_RELAX_BEFORE_LONG_RELAX.get() != "":
            SHORT_RELAX_BEFORE_LONG_RELAX = int(
                input_SHORT_RELAX_BEFORE_LONG_RELAX.get()
            )
        if input_MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX.get() != "":
            MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX = int(
                input_MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX.get()
            )
        if input_MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX.get() != "":
            MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX = int(
                input_MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX.get()
            )
        if input_SHORT_RELAX_MIN.get() != "":
            SHORT_RELAX_MIN = int(input_SHORT_RELAX_MIN.get())
        if input_LONG_RELAX_MIN.get() != "":
            LONG_RELAX_MIN = int(input_LONG_RELAX_MIN.get())
        reset_config_label()

    Button(window, width=30, text="Set Config", command=set_config).pack()
    root.mainloop()


def frequent_notification(text, routines):
    global NOTIFY_INTERVAL_MIN
    global relaxing
    global short_relax_consecutive_count
    global doing
    global short_success_count
    global consecutive_fail_count
    global SUCCESS_BEFORE_SHORT_RELAX
    global SHORT_RELAX_BEFORE_LONG_RELAX
    global MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX

    cur_routine = next_routine = None
    time_prev = time_now = None

    while True:
        time_now = datetime.now().strftime("%H:%M")
        now = datetime.now()
        if time_prev == None or time_now != time_prev:
            if check_time_in_flow(time_now):
                now = datetime.now()
                if (
                    now.minute % NOTIFY_INTERVAL_MIN == 0
                    and not doing
                    and not relaxing.value
                ):
                    work_res = input_restrict_time_sound(
                        "Log",
                        3.5,
                        cur_routine.voice if cur_routine != None else "",
                    )
                    print(str(cur_routine) + " | next: " + str(next_routine))
                    if work_res:
                        short_success_count += 1
                        consecutive_fail_count = 0
                    else:
                        consecutive_fail_count += 1
                        if (
                            consecutive_fail_count
                            >= MAX_CONSECUTIVE_FAIL_TO_RESET_SHORT_RELAX
                        ):
                            speak("You miss " + str(consecutive_fail_count) + " blocks")
                            short_success_count = 0
                        if (
                            consecutive_fail_count
                            >= MAX_CONSECUTIVE_FAIL_TO_RESET_LONG_RELAX
                        ):
                            short_relax_consecutive_count = 0
                    if short_success_count >= SUCCESS_BEFORE_SHORT_RELAX:
                        short_success_count -= SUCCESS_BEFORE_SHORT_RELAX
                        if (
                            short_relax_consecutive_count
                            >= SHORT_RELAX_BEFORE_LONG_RELAX
                        ):
                            relax_long()
                            short_relax_consecutive_count -= (
                                SHORT_RELAX_BEFORE_LONG_RELAX
                            )
                        else:
                            short_relax_consecutive_count += 1
                            relax_short(short_relax_consecutive_count)
                    update_time_execute()
            new_routines = read_routines(text, False)
            routine_changed = False
            for nr in new_routines:
                for r in routines:
                    if nr.time == r.time and nr.voice != r.voice:
                        print("New: " + str(nr.time) + "- " + str(nr.voice))
                        routine_changed = True
            if routine_changed:
                routines = new_routines
            for index, routine in enumerate(routines):
                if cur_routine == None and routine.time > time_now:
                    cur_routine = routines[index - 1]
                    cur_routine.execute()
                    next_routine = routines[index]
                    break
                elif routine.time == time_now:
                    cur_routine = routine
                    cur_routine.execute()
                    next_routine = routines[index + 1]
                    break
            time_prev = time_now
        time.sleep(1)


def relax_short(short_relax_consecutive_count):
    global SHORT_RELAX_MIN
    relaxing.makeTrue()
    speak("Relax " + str(SHORT_RELAX_MIN) + " min")
    print(
        "Relax "
        + str(SHORT_RELAX_MIN)
        + " minutes ("
        + str(short_relax_consecutive_count)
        + ") till "
        + (datetime.today() + timedelta(hours=0, minutes=SHORT_RELAX_MIN)).strftime(
            "%H:%M:%S"
        )
    )
    append_to_dayplanner(
        "Relax "
        + str(SHORT_RELAX_MIN)
        + " minutes ("
        + str(short_relax_consecutive_count)
        + ") till "
        + (datetime.today() + timedelta(hours=0, minutes=SHORT_RELAX_MIN)).strftime(
            "%H:%M:%S"
        ),
        datetime.now(),
    )
    thread = threading.Thread(
        target=playsound_random_times,
        args=(
            RELAX_SOUND_FILES,
            int(math.floor(SHORT_RELAX_MIN / 5)),
        ),
    )
    thread.start()
    thread.join()
    time.sleep(150)


def relax_long():
    global LONG_RELAX_MIN
    relaxing.makeTrue()
    speak(
        "Relax " + str(LONG_RELAX_MIN) + " min, Relax " + str(LONG_RELAX_MIN) + " min"
    )
    print(
        "Relax "
        + str(LONG_RELAX_MIN)
        + " minutes till "
        + (datetime.today() + timedelta(hours=0, minutes=LONG_RELAX_MIN)).strftime(
            "%H:%M:%S"
        )
    )
    append_to_dayplanner(
        "Relax "
        + str(LONG_RELAX_MIN)
        + " minutes till "
        + (datetime.today() + timedelta(hours=0, minutes=LONG_RELAX_MIN)).strftime(
            "%H:%M:%S"
        ),
        datetime.now(),
    )
    thread = threading.Thread(
        target=playsound_random_times,
        args=(
            RELAX_SOUND_FILES,
            int(math.floor(LONG_RELAX_MIN / 5)),
        ),
    )
    thread.start()
    thread.join()
    time.sleep(230)


def load_from_file(filename):
    with open(filename, "r") as file:
        return json.load(file)


def append_to_dayplanner(text, time_now=datetime.now()):
    DAYPLANNER_FILE = (
        "/home/hienphan/Desktop/notes/Day Planners/Day Planner-"
        + time_now.strftime("%Y%m%d")
        + ".md"
    )

    with open(DAYPLANNER_FILE, "r") as in_file:
        buf = in_file.readlines()

    with open(DAYPLANNER_FILE, "w") as out_file:
        haveLine = False
        for line in buf:
            if line.startswith("- [ ] ") and line[8] == ":":
                hour = int(line[6:8])
                min = int(line[9:11])
                task_hour = time_now.hour
                task_min = time_now.minute
                if haveLine:
                    line = "\t" + time_now.strftime("%H:%M") + " " + text + "\n" + line
                    haveLine = False
                if task_hour == hour:
                    if task_min < 30:
                        if min == 0:
                            haveLine = True
                    elif task_min >= 30:
                        if min == 30:
                            haveLine = True
            out_file.write(line)


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def sync_to_dayplanner_obsidian(projects):
    now = datetime.now()
    DAYPLANNER_FILE = (
        "/home/hienphan/Desktop/notes/Day Planners/Day Planner-"
        + now.strftime("%Y%m%d")
        + ".md"
    )
    routines = []
    tasks = ""
    start_tasks_section = False
    with open(DAYPLANNER_FILE, "a") as file:
        for line in file.readlines():
            if len(line) < 9:
                continue
            if line.startswith("- [ ] ") and line[8] == ":":
                start_tasks_section = True
                time = line[6:11]
                task = line[12:].rstrip()
                routines.append(Routine(time, task))
                print("Task: " + tasks)
                tasks = ""
                tasks += task
            elif start_tasks_section:
                tasks += line
    return routines


def main():
    # try:
    # gui_config()
    threading.Thread(target=gui_config, args=()).start()
    gui_text = None
    routines = read_routines(gui_text, True)
    print_routines(routines)
    frequent_notification(gui_text, routines)
    projects = load_from_file(projectfilepath.get_abs_path("projects.json"))
    sync_to_dayplanner_obsidian(projects)


def read_routines(text, is_print_routines=False):
    routines = load_routine_from_file(projectfilepath.get_abs_path("routine.txt"))
    routine_from_dayplanner = load_routine_from_day_planner(text, is_print_routines)
    transform_same_task(routine_from_dayplanner)
    for routine in routine_from_dayplanner:
        routines.append(routine)
    routines.sort(key=lambda x: x.time, reverse=False)
    concate_voice_same_time_task(routines, re.compile("^\d\d:\d\d$"))
    return routines


def test():
    return


if __name__ == "__main__":
    main()
