#!/usr/bin/python

# importing libraries
import time
import json
from datetime import datetime
import routine
import threading

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
    print("Projects:")
    for p in projects:
        print("\t{}. {}".format(p["index"], p["proj_name"]))
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
        "proj_name": proj_input, "tasks": []}
        # task = {"lap": [], "countdown": []}
        projects.append(selected_project)
    print("Selected project: " + str(selected_project["proj_name"]))
    return projects,selected_project

def run_countdown(projects, task):
    countdown_obj = countdown()
    task[1]["countdown"].append(countdown_obj)
    dump_to_file(FILE_PROJECT_NAME, projects)
    print("Done")


def run_laptime(projects, task):
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
            task[1]["lap"].append({"date": date_str, "time":laptime, "notes": notes})
            lasttime=time.time()
            lapnum+=1
    # Stopping when CTRL+C is pressed
    except KeyboardInterrupt:
        dump_to_file(FILE_PROJECT_NAME, projects)
        print("Done")

def show_stats(selected_project):
    print()
    print("*** Project: " + selected_project["proj_name"])
    for tasks in selected_project["tasks"]:
        print("\tTask: " + tasks["name"])
        laps = tasks["lap"]
        print("\t\t[Lap]:")
        if (len(laps) > 0):
            prev = laps[0]["time"]
        for lap in laps:
            ratio = str(round(lap["time"]*100/prev, 0)) + "%"
            print("\t\t\tDate " + str(lap["date"]) + ": " + str(lap["time"]) + " - +" + ratio + " (" + str(lap["notes"]) + ")")
            prev = lap["time"]
        print("\t\t[CountDown]:")
        countdowns = tasks["countdown"]
        if (len(countdowns) > 0):
            prev = countdowns[0]["time"]
        for countdown in countdowns:
            ratio = str(round(countdown["time"]*100/prev, 0)) + "%"
            print("\t\t\tDate " + str(countdown["date"]) + ": " + str(countdown["time"]) + " - +" + ratio + " (" + str(countdown["notes"]) + ")")
            prev = countdown["time"]
    return

def show_all_project_stats(projects):
    for project in projects:
        show_stats(project)

def choose_operator(projects, selected_project, selected_task):
    option = -1
    while (option > 4 or option < 1):
        try:
            option = int(input("Choose operator: \n\t1. Lap time\n\t2. Count down\n\t3. Show stats of selected project\n\t4. Show stats of all projects\n"))
        except ValueError:
            print("Option must be integer")
    if (option == 1):
        run_laptime(projects, selected_task)
    elif (option == 2):
        run_countdown(projects, selected_task)
    elif (option == 3):
        show_stats(selected_project)
    elif (option == 4):
        show_all_project_stats(projects)

def show_tasks_name(tasks):
    print()
    print("Select task in project: ")
    if (len(tasks) == 0):
        print ("There is NO task!")
    ind = 1
    for task in tasks:
        print("\t" + str(ind) + ". " + task["name"])
        ind+=1

def select_task(tasks, selected_task):
    while (selected_task == None):
        show_tasks_name(tasks)
        try:
            option = input("Your task: ")
            int_option = int(option)
            if (int_option > len(tasks) or int_option < 1):
                print("Option must be integer in range 1.." + len(tasks))
                continue
            selected_task= tasks[int_option - 1]
        except ValueError:
            print("Create new task: " + option)
            tasks.append({"name": option, "lap": [], "countdown":[]})
    print("Selected task: " + selected_task["name"])
    return int_option,selected_task

def run_task_manage():
    while (True):
        overall_option = input("Overall option: \n\t1. Continue task\n\t2. New task\n\t3. New project\n\te. Exit\n")
        if (overall_option == "e"):
            break
        elif (overall_option == "1"):
            print("Continue task")
            if (selected_task == None):
                print("No task selected!")
                break
        elif (overall_option == "2"):
            selected_task = None
            selected_task = select_task(selected_project["tasks"], selected_task)
        elif (overall_option == "3"):
            projects, selected_project = select_project()
            selected_task = None
            selected_task = select_task(selected_project["tasks"], selected_task)
        choose_operator(projects, selected_project, selected_task)

def Main():
    try:
        routine_thread = threading.Thread(target=routine.main, args=())
        routine_thread.start()
        task_manage_thread = threading.Thread(target=run_task_manage, args=())
        task_manage_thread.start()
        routine_thread.join()
        task_manage_thread.join()
    except:
        routine_thread.join()
        task_manage_thread.join()

Main()

