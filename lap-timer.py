#!/usr/bin/python
import time
import json
from datetime import datetime
import routine
import threading
from time import sleep
import projectfilepath
import threading


def dump_to_file(filename, obj):
    with open(filename, "w") as file:
        json.dump(obj, file)


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


def select_project(projects):
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
        projects.append(selected_project)
    print("Selected project: " + str(selected_project["proj_name"]))
    return selected_project


def run_countdown(projects, task):
    countdown_obj = countdown()
    task[1]["countdown"].append(countdown_obj)
    dump_to_file(projectfilepath.get_abs_path("projects.json"), projects)
    print("Done")


def is_same_day(date1, date2):
    if (date1.day == date2.day and date1.month == date2.month 
        and date1.year == date2.year):
        return True
    return False


def convert_to_minsec(laptime):
    mins, secs = divmod(laptime, 60)
    min_and_sec = '{:02d}m{:02d}s'.format(mins, secs)
    return min_and_sec


def run_laptime(projects, task):
    starttime = time.time()
    lasttime = starttime
    lapnum = 1
    print("Press ENTER to count laps.\nPress CTRL+C to stop")
    while True:
        print("Start...")
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y %H:%M:%S")
        continous = input("Want to stop ? (Enter to continue, e to exit)")
        if (continous == "e"):
            dump_to_file(projectfilepath.get_abs_path("projects.json"), projects)
            print("Done")
            break
        totaltime = round((time.time() - starttime), 2)
        laptime = round((time.time() - lasttime), 2)
        print("Lap No. " + str(lapnum))
        print("Total Time: " + str(totaltime) + " ( " + convert_to_minsec(totaltime) + " )")
        print("Lap Time: " + str(laptime) + " ( " + convert_to_minsec(laptime) + " )")
        print("*"*20)
        notes = input("Notes? ")
        task[1]["lap"].append({"date": date_str, "time":laptime, "notes": notes})
        lasttime = time.time()
        lapnum += 1


def convert_sec_hour(nsecs):
    nsecs = int(round(nsecs))
    hours, minsecs = divmod(nsecs, 3600)
    mins, secs = divmod(minsecs, 60)
    timer = '{:02d}h{:02d}m{:02d}s'.format(hours, mins, secs)
    return timer


def get_avg(arr):
    if (len(arr) == 0):
        return 0;
    sum = 0
    for item in arr:
        sum += item["time"]
    avg = sum / len(arr)
    return avg


def is_today_stat(time_rec):
    today_str = datetime.now().strftime("%d/%m/%Y")
    if (time_rec["date"].split()[0] == today_str):
        return True
    return False


def show_stats_pre(predicate, selected_project):
    for tasks in selected_project["tasks"]:
        laps = tasks["lap"]
        filtered_laps = list(filter(predicate, laps))
        if (len(filtered_laps) > 0):
            prev = filtered_laps[0]["time"]
            print("*** Project: " + selected_project["proj_name"])
            print("\tTask: " + tasks["name"])
            print("\t\t[Lap]:")
            avg = get_avg(filtered_laps)
            print ("\t\t\tAverage speed = " + str(avg) + " ( " + convert_sec_hour(avg) + " )")
            for lap in filtered_laps:
                ratio = str(round(lap["time"] * 100 / prev, 1)) + "%"
                ratio_avg = str(round(lap["time"] * 100 / avg, 1)) + "%"
                print("\t\t\tDate " + str(lap["date"]) + ": " 
                    +str(convert_sec_hour(int(round(lap["time"], 0)))) 
                    +" - +" + ratio + "(vs. prev)"
                    +" - +" + ratio_avg + "(vs. avg)"
                    +" (" + str(lap["notes"]) + ")")
                prev = lap["time"]

        countdowns = tasks["countdown"]
        filtered_countdowns = list(filter(predicate, countdowns))
        if (len(filtered_countdowns) > 0):
            prev = filtered_countdowns[0]["time"]
            print("\t\t[CountDown]:")
            avg = get_avg(filtered_countdowns)
            print ("\t\t\tAverage speed = " + str(avg) + " ( " + convert_sec_hour(avg) + " )")
            for countdown in filtered_countdowns:
                if (prev != 0):
                    ratio = str(round(countdown["time"] * 100 / prev, 1)) + "%"
                    ratio_avg = str(round(countdown["time"] * 100 / avg, 1)) + "%"
                    print("\t\t\tDate " + str(countdown["date"]) + ": " 
                        +str(convert_sec_hour(int(round(countdown["time"], 0)))) 
                        +" - +" + ratio + "(vs. prev)"
                        +" - +" + ratio_avg + "(vs. avg)"
                        +" (" + str(countdown["notes"]) + ")")
                prev = countdown["time"]


def show_all_project_stats(projects):
    print("\n##########################\n")
    for project in projects:
        show_stats(project)
    print("\n##########################\n")


def show_all_project_stats_pre(predicate, projects):
    print("\n##########################\n")
    for project in projects:
        show_stats_pre(predicate, project)
    print("\n##########################\n")


def choose_operator(projects, selected_project, selected_task):
    option = -1
    while (option > 3 or option < 1):
        try:
            option = int(input("Choose operator: \n\t"
            +"1. Lap time\n\t"
            +"2. Count down\n\t" 
            +"3. Show stats of selected project\n"
            +"Your choice: "))
        except ValueError:
            print("Option must be integer")
    if (option == 1):
        run_laptime(projects, selected_task)
    elif (option == 2):
        run_countdown(projects, selected_task)
    elif (option == 3):
        show_stats(selected_project)


def show_tasks_name(tasks):
    print()
    print("Select task in project: ")
    if (len(tasks) == 0):
        print ("There is NO task!")
    ind = 1
    for task in tasks:
        print("\t" + str(ind) + ". " + task["name"])
        ind += 1


def select_task(tasks, selected_task):
    while (selected_task == None):
        show_tasks_name(tasks)
        try:
            option = input("Your task: ")
            int_option = int(option)
            if (int_option > len(tasks) or int_option < 1):
                print("Option must be integer in range 1.." + str(len(tasks)))
                continue
            selected_task = tasks[int_option - 1]
        except ValueError:
            print("Create new task: " + option)
            tasks.append({"name": option, "lap": [], "countdown":[]})
    print("Selected task: " + selected_task["name"])
    return int_option, selected_task


def run_task_manage():
    routine_thread = StoppableThread(target=routine.main, args=())
    routine_thread.start()
    sleep(1)
    selected_task = None
    while (True):
        overall_option = input("Overall option: \n\t"
                               +"1. Continue selected task\n\t" 
                               +"2. Choose task\n\t"
                               +"3. Choose project\n\t"
                               +"4. Show statistics of all projects\n\t"
                               +"5. Show statistics of today\n\t"
                               +"6. Reload routines\n\t"
                               +"e. Exit\n"
                               +"Your Choice: ")
        projects = load_from_file(projectfilepath.get_abs_path("projects.json"))
        if (overall_option == "e"):
            break
        elif (overall_option == "1"):
            print("Continue task")
            if (selected_task == None):
                print("No task selected! Please select task first.")
            else:
                choose_operator(projects, selected_project, selected_task)
        elif (overall_option == "2"):
            selected_task = None
            selected_task = select_task(selected_project["tasks"], selected_task)
            choose_operator(projects, selected_project, selected_task)
        elif (overall_option == "3"):
            selected_project = select_project(projects)
            selected_task = None
            selected_task = select_task(selected_project["tasks"], selected_task)
            choose_operator(projects, selected_project, selected_task)
        elif (overall_option == "4"):
            show_all_project_stats_pre(lambda pre: True, projects)
        elif (overall_option == "5"):
            show_all_project_stats_pre(is_today_stat, projects)
        elif (overall_option == "6"):
            routine_thread.stop()
            routine_thread = StoppableThread(target=routine.main, args=())
            routine_thread.start()
            sleep(1)
    
    routine_thread.stop()
    routine_thread.join()


class StoppableThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def Main():
    try:
        task_manage_thread = threading.Thread(target=run_task_manage, args=())
        task_manage_thread.start()
        task_manage_thread.join()
    except:
        task_manage_thread.join()


Main()

