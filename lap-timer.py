# importing libraries
import time
import json
from datetime import datetime

FILE_PROJECT_NAME = "projects.data"

def dump_to_file(filename, obj):
    with open(filename, "w") as file:
        my_json_object = json.dump(obj, file)

def load_from_file(filename):
    with open(filename, "r") as file:
        return json.load(file)
 
def countdown():
	nsecs = int(input("Enter number of seconds: "))
	now = datetime.now()
	date_str = now.strftime("%d/%m/%Y %H:%M:%S")
	while nsecs:
		mins, secs = divmod(nsecs, 60)
		timer = '{:02d}:{:02d}'.format(mins, secs)
		print(timer, end="\r")
		time.sleep(1)
		nsecs -= 1
	notes = input("Notes? ")
	return {"date": date_str, "time": nsecs, "notes": notes}

def select_project():
    projects = load_from_file(FILE_PROJECT_NAME)
    maxIndex = 0
    for p in projects:
        print("{}. {}".format(p["index"], p["proj_name"]))
        if (maxIndex < p["index"]):
            maxIndex = p["index"]
    proj_input = input("Choose project: ")
    selected_project = None
    try:
        val = int(proj_input)
        for p in projects:
            if p["index"] == val:
                selected_project = p
        if (selected_project == None):
            print("Project index is not exist !")
            exit()
    except ValueError:
        print("OK, create new project " + str(proj_input))
        selected_project = {"index": maxIndex + 1, 
        "proj_name": proj_input, "lap":[], "countdown":[]}
        projects.append(selected_project)
    print("Selected project: " + str(selected_project["proj_name"]))
    return projects,selected_project

def run_countdown(projects, selected_project):
    countdown_obj = countdown()
    selected_project["countdown"].append(countdown_obj)
    dump_to_file(FILE_PROJECT_NAME, projects)
    print("Done")


def run_laptime(projects, selected_project):
    starttime=time.time()
    lasttime=starttime
    lapnum=1
    print("Press ENTER to count laps.\nPress CTRL+C to stop")
    try:
        while True:
            print("Start...")
            now = datetime.now()
            date_str = now.strftime("%d/%m/%Y %H:%M:%S")
            input()
            totaltime=round((time.time() - starttime), 2)
            laptime=round((time.time() - lasttime), 2)
            print("Lap No. "+str(lapnum))
            print("Total Time: "+str(totaltime))
            print("Lap Time: "+str(laptime))
            print("*"*20)
            notes = input("Notes? ")
            selected_project["lap"].append({"date": date_str, "time":laptime, "notes": notes})
            lasttime=time.time()
            lapnum+=1
    # Stopping when CTRL+C is pressed
    except KeyboardInterrupt:
        dump_to_file(FILE_PROJECT_NAME, projects)
        print("Done")

def show_stats(selected_project):
    print("*** Project: " + selected_project["proj_name"])
    print("[Lap]:")
    laps = selected_project["lap"]
    if (len(laps) > 0):
        prev = laps[0]["time"]
    for lap in laps:
        ratio = str(round(lap["time"]*100/prev, 0)) + "%"
        print("Date " + str(lap["date"]) + ": " + str(lap["time"]) + " - +" + ratio + " (" + str(lap["notes"]) + ")")
        prev = lap["time"]
    print("[CountDown]:")
    countdowns = selected_project["countdown"]
    if (len(countdowns) > 0):
        prev = countdowns[0]["time"]
    for countdown in countdowns:
        ratio = str(round(countdown["time"]*100/prev, 0)) + "%"
        print("Date " + str(countdown["date"]) + ": " + str(countdown["time"]) + " - +" + ratio + " (" + str(countdown["notes"]) + ")")
        prev = countdown["time"]
    return

def show_all_project_stats(projects):
    for project in projects:
        show_stats(project)

def main():
    projects, selected_project = select_project()
    option = -1
    while (option > 4 or option < 1):
        try:
            option = int(input("Choose operator: \n1. Lap time\n2. Count down\n3. Show stats of selected project\n4. Show stats of all projects\n"))
        except ValueError:
            print("Option must be integer")
    if (option == 1):
        run_laptime(projects, selected_project)
    elif (option == 2):
        run_countdown(projects, selected_project)
    elif (option == 3):
        show_stats(selected_project)
    elif (option == 4):
        show_all_project_stats(projects)

main()