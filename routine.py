import time
from datetime import datetime
import os
from playsound import playsound
import projectfilepath
import re

BELL_RING_FILE = 'bell-ringing-04.wav'


class Routine:

    def __init__(self, time, voice):
        self.time = time
        self.voice = voice


def load_routine_from_file(filename):
    routines = []
    with open(filename, "r") as file:
        for line in file.readlines():
            index_first_space = line.find(" ")
            time = line[:index_first_space];
            task = line[index_first_space + 1:].rstrip()
            routines.append(Routine(time, task))
    return routines

            
def load_routine_from_day_planner():
    now = datetime.now()
    DAYPLANNER_FILE = "/home/harrison-hienp/Desktop/notes/Day Planners/Day Planner-" + now.strftime("%Y%m%d") + ".md"
    routines = []
    with open(DAYPLANNER_FILE, "r") as file:
        for line in file.readlines():
            if (len(line) < 9):
                continue
            if (line.startswith("- [ ] ") and line[8] == ':'):
                index_first_space = line.find(" ", 6, len(line))
                time = line[6:11]
                task = line[12:].rstrip()
                routines.append(Routine(time, task))
    return routines
            

def print_routines(routines):
    print("-------------------Day Planner --------------")
    for routine in routines:
        print("At " + routine.time + ", do " + routine.voice)
    print("----------------------------------------------")


def transform_same_task(routine_from_dayplanner):
    idx = 1
    num = 2
    origin = None
    while idx < len(routine_from_dayplanner):
        if (routine_from_dayplanner[idx].voice == "." and not routine_from_dayplanner[idx - 1].voice.startswith("cmd")):
            if origin == None:
                origin = routine_from_dayplanner[idx - 1].voice
                routine_from_dayplanner[idx - 1].voice = "Section 1, " + routine_from_dayplanner[idx - 1].voice
            routine_from_dayplanner[idx].voice = "Section " + str(num) + ", " + origin
            num += 1
        else:
            origin = None
            num = 2
        idx += 1


def concate_voicce_same_time_task(routines, pattern):
    idx = 0
    while idx < len(routines):
        if (idx == len(routines) - 1):
            idx += 1
        elif (pattern.match(routines[idx].time) == None):
            del routines[idx]
        else:
            i = idx + 1
            while i < len(routines) and routines[idx].time == routines[i].time:
                routines[idx].voice += "; " + routines[i].voice
                del routines[i]
            idx += 1


def frequent_notification(routines, projectfilepath, routine):
    while True:
        time_play_sound = 0
        now = datetime.now()
        now_time_format = now.strftime("%H:%M")
        for routine in routines:
            if (routine.time == now_time_format):
                if (routine.voice.startswith("cmd")):
                    find_separator = routine.voice.find(":")
                    if (find_separator > 0):
                        cmd = routine.voice[find_separator + 1:]
                        os.system(cmd)
                    else:
                        print("Missing ':' in cmd routine")
                else:
                    voice_cmd = '/home/harrison-hienp/mimic1/mimic -t "' + routine.voice + '" -voice slt'
                    start_time = datetime.now().timestamp()
                    playsound(projectfilepath.get_abs_path(BELL_RING_FILE))
                    for i in range(0, 3):
                        os.system(voice_cmd)
                    
                    end_time = datetime.now().timestamp()
                    time_play_sound = end_time - start_time
        
                    # break
        time.sleep(60 - time_play_sound)


def main():
    routines = load_routine_from_file(projectfilepath.get_abs_path("routine.txt"))
    routine_from_dayplanner = load_routine_from_day_planner()
    transform_same_task(routine_from_dayplanner)
    for routine in routine_from_dayplanner:
        routines.append(routine)
    routines.sort(key=lambda x: x.time, reverse=False)
    pattern = re.compile("^\d\d:\d\d$")
    concate_voicce_same_time_task(routines, pattern)
    print_routines(routines)
    frequent_notification(routines, projectfilepath, routine)

        
def test():
    return


# test()
main()
