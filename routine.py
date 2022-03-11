import time
from datetime import datetime
import os
from playsound import playsound

class Routine:
    def __init__(self, time, voice):
        self.time = time
        self.voice = voice

ROUTINE_FILE = "/home/harrison-hienp/Desktop/code/script/py-automatic/routine.txt"
def load_routine_from_file(filename):
    routines = []
    with open(filename, "r") as file:
        for line in file.readlines():
            indexFirstSpace = line.find(" ")
            time = line[:indexFirstSpace];
            task = line[indexFirstSpace + 1:]
            routines.append(Routine(time, task))
    return routines
            
def load_routine_from_day_planner():
    now = datetime.now()
    DAYPLANNER_FILE= "/home/harrison-hienp/Desktop/notes/Day Planners/Day Planner-"+now.strftime("%Y%m%d") +".md"
    routines = []
    with open(DAYPLANNER_FILE, "r") as file:
        for line in file.readlines():
            if (len(line) < 9):
                continue
            if (line.startswith("- [ ] ") and line[8] == ':'):
                index_first_space = line.find(" ", 6, len(line))
                time = line[:index_first_space];
                task = line[index_first_space + 1:]
                routines.append(Routine(time, task))
    return routines
            
def main():
    routines = load_routine_from_file(ROUTINE_FILE)
    routine_from_dayplanner = load_routine_from_day_planner()
    for routine in routine_from_dayplanner:
        routines.append(routine)

    nsec = 0
    while (nsec < 86400):
        nsec += 60
        now = datetime.now()
        DAYPLANNER_FILE = now.strftime("%H:%M")
        for routine in routines:
            if (routine.time == DAYPLANNER_FILE):
                voice_cmd = '/home/harrison-hienp/mimic1/mimic -t "' + routine.voice + '" -voice slt'
                playsound('/home/harrison-hienp/Desktop/code/script/py-automatic/bell-ringing-04.wav')
                playsound('/home/harrison-hienp/Desktop/code/script/py-automatic/bell-ringing-04.wav')
                for i in range(0, 3):
                    os.system(voice_cmd)
        time.sleep(60)
        
main()