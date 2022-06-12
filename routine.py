import time
from datetime import datetime
import os
from playsound import playsound
import projectfilepath
import re

BELL_RING_FILE = 'bell-ringing-04.wav'
SHORT_TICK_FILE = 'tick-tock.mp3'
MIMIC_VOICE_BIN_PATH = "/home/harrison-hienp/mimic1/mimic" 


class Routine:

    def __init__(self, time, voice):
        self.time = time
        self.voice = voice
        
    def is_cmd(self):
        return self.voice.startswith("cmd")
    
    def execute(self):
        if (self.is_cmd()):
            find_separator = self.voice.find(":")
            if (find_separator > 0):
                cmd = self.voice[find_separator + 1:]
                os.system(cmd)
            else:
                print("Missing ':' in cmd routine. " + str(self))
        else:
            voice_cmd = MIMIC_VOICE_BIN_PATH + ' -t "' + self.voice + '" -voice slt'
            for i in range(0, 1):
                playsound(projectfilepath.get_abs_path(BELL_RING_FILE))
                os.system(voice_cmd)


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
    print("\n-------------------Day Planner---------------")
    for routine in routines:
        if (not routine.is_cmd()):
            print("At " + routine.time + ", do " + routine.voice)
    print("----------------------------------------------\n")


def transform_same_task(routine_from_dayplanner):
    idx = 1
    section_num = 2
    origin = None
    while idx < len(routine_from_dayplanner):
        if (routine_from_dayplanner[idx].voice == "." 
            and not routine_from_dayplanner[idx - 1].is_cmd()):
            if origin == None:
                origin = routine_from_dayplanner[idx - 1].voice
                routine_from_dayplanner[idx - 1].voice = "Section 1, " + routine_from_dayplanner[idx - 1].voice
            routine_from_dayplanner[idx].voice = "Section " + str(section_num) + ", " + origin
            section_num += 1
        else:
            origin = None
            section_num = 2
        idx += 1


def concate_voice_same_time_task(routines, pattern):
    idx = 0
    while idx < len(routines):
        if (idx == len(routines) - 1):
            idx += 1
        elif (pattern.match(routines[idx].time) == None):
            del routines[idx]
        else:
            next_idx = idx + 1
            while next_idx < len(routines) and routines[idx].time == routines[next_idx].time:
                routines[idx].voice += "; " + routines[next_idx].voice
                del routines[next_idx]
            idx += 1


class Duration:

    def __init__(self, start, end):
        self.start = start
        self.end = end

    
def check_time_in_flow(time):
    durations = []
    durations.append(Duration("07:00", "11:30"))
    durations.append(Duration("12:30", "17:20"))
    durations.append(Duration("19:00", "20:40"))
    for dur in durations: 
        if (time >= dur.start and time <= dur.end):
            return True
    return False


def frequent_notification(routines, projectfilepath, routine):
    NOTIFY_INTERVAL_MIN = 5
    while True:
        start_time = datetime.now().timestamp()
        time_use_process = 0
        now = datetime.now()
        now_time_format = now.strftime("%H:%M")
        for routine in routines:
            if (routine.time == now_time_format):
                routine.execute()
        if (now.minute != 0 and now.minute % NOTIFY_INTERVAL_MIN == 0 and check_time_in_flow(now_time_format)):
            playsound(projectfilepath.get_abs_path(SHORT_TICK_FILE))
        end_time = datetime.now().timestamp()
        time_use_process = end_time - start_time
        time.sleep(60 - time_use_process)  # make sure do 60 sec for single loop


def main():
    routines = load_routine_from_file(projectfilepath.get_abs_path("routine.txt"))
    routine_from_dayplanner = load_routine_from_day_planner()
    transform_same_task(routine_from_dayplanner)
    for routine in routine_from_dayplanner:
        routines.append(routine)
    routines.sort(key=lambda x: x.time, reverse=False)
    concate_voice_same_time_task(routines, re.compile("^\d\d:\d\d$"))
    print_routines(routines)
    frequent_notification(routines, projectfilepath, routine)

        
def test():
    return

# test()
# main()
