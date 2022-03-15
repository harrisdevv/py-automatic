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


def main():
    routines = load_routine_from_file(projectfilepath.get_abs_path("routine.txt"))
    routine_from_dayplanner = load_routine_from_day_planner()
    for routine in routine_from_dayplanner:
        routines.append(routine)
   
    pattern = re.compile("^\d\d:\d\d$")
    routines.sort(key=lambda x: x.time, reverse=False)
    idx = 0
    while (idx < len(routines)):
        if (pattern.match(routines[idx].time) == None):
            del routines[idx]
            continue
        if (idx == len(routines) - 1): 
            idx += 1
            break
        i = idx + 1
        while (i < len(routines) and routines[idx].time == routines[i].time):
            routines[idx].voice += "; " + routines[i].voice
            del routines[i]
        idx += 1
    
    print_routines(routines)
    while (True):
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
                    playsound(projectfilepath.get_abs_path(BELL_RING_FILE))
                    for i in range(0, 3):
                        os.system(voice_cmd)
                    end_time = datetime.now().timestamp()
                    time_play_sound = end_time - start_time
                    break
        time.sleep(60 - time_play_sound)

        
def test():
    return

# test()
# main()
