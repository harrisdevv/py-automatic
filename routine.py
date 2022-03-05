import time
from datetime import datetime
import os
from playsound import playsound

class Routine:
    def __init__(self, time, voice):
        self.time = time
        self.voice = voice

def main():
    routines = []
    routines.append(Routine("7:00", "Let's do the mission"))
    routines.append(Routine("11:30", "Eat Lunch! Yeah!"))
    routines.append(Routine("12:10", "Evening working session"))
    routines.append(Routine("17:10", "Off work, relaxing"))
    routines.append(Routine("20:50", "Sleep, Sleep, sleep"))
  
    nsec = 0
    while (nsec < 86400):
        nsec += 60
        now = datetime.now()
        date_str = now.strftime("%H:%M")
        for routine in routines:
            if (routine.time == date_str):
                voice_cmd = '/home/harrison-hienp/mimic1/mimic -t "' + routine.voice + '" -voice slt'
                playsound('bell-ringing-04.wav')
                for i in range(0, 3):
                    os.system(voice_cmd)
        time.sleep(60)