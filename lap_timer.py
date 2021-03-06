#!/usr/bin/python
import time
import json
from datetime import datetime, timedelta
import routine
import threading
from time import sleep
import projectfilepath
import threading
from pyrfc3339.generator import generate
import calendar
from playsound import playsound
import sys
from art import text2art
from colorama import Fore
from colorama import init as colorama_init
from tqdm import trange

DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = DATE_FORMAT + " " + "%H:%M:%S"
GLASS_SOUND_FILE = "35631__reinsamba__crystal-glass.wav"
COMPLETED_SOUND_FILE = "609336__kenneth-cooney__completed.wav"


def dump_to_file(filename, obj):
    with open(filename, "w") as file:
        json.dump(obj, file)


def load_from_file(filename):
    with open(filename, "r") as file:
        return json.load(file)

 
def countdown():
	nsecs = int(input("Enter number of seconds: "))
	now = datetime.now()
	date_str = now.strftime(DATETIME_FORMAT)
	while nsecs:
		mins, secs = divmod(nsecs, 60)
		timer = '{:02d}:{:02d}'.format(mins, secs)
		print(timer, end="\r")
		time.sleep(1)
		nsecs -= 1
    
	notes = input("Notes (e = exit)? ")
	if (notes == "e"):
		return None
	return {"date": date_str, "time": nsecs, "notes": notes}


def select_project(projects):
    maxIndex = 0
    print("Projects:")
    for p in projects:
        print(" {}. {}".format(p["index"], p["proj_name"]))
        if (maxIndex < p["index"]):
            maxIndex = p["index"]
    proj_input = color_input("Choose project: ")
    selected_project = None
    try:
        val = int(proj_input)
        for p in projects:
            if p["index"] == val:
                selected_project = p
        if (selected_project == None):
            print("Project index is not exist !")
            return None
    except ValueError:
        print("OK, create new project " + str(proj_input))
        selected_project = {"index": maxIndex + 1,
        "proj_name": proj_input, "tasks": []}
        projects.append(selected_project)
    print("Selected project: " + str(selected_project["proj_name"]))
    return selected_project


def run_countdown(projects, selected_project, task):
    countdown_obj = countdown()
    add_task_item(projects, selected_project, task, "countdown", date_time_str, laptime, notes);
    dump_to_file(projectfilepath.get_abs_path("projects.json"), projects)
    print("Done")


def is_same_day(date1, date2):
    if (date1.day == date2.day and date1.month == date2.month 
        and date1.year == date2.year):
        return True
    return False


def convert_to_minsec(laptime):
    laptime_round = int(round(laptime))
    mins, secs = divmod(laptime_round, 60)
    min_and_sec = '{:02d}:{:02d}'.format(mins, secs)
    return min_and_sec


def getch():
    import termios
    import sys, tty

    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch()


def run_laptime(projects, selected_project, task):
    starttime = time.time()
    lasttime = starttime
    pause_time = 0
    lapnum = 1
    while True:
        print("Start...")
        playsound(projectfilepath.get_abs_path(GLASS_SOUND_FILE))
        now = datetime.now()
        date_str = now.strftime(DATETIME_FORMAT)
        print("Want to stop ? (Enter to stop, p to pause, e to exit) ")
        continous = getch()
        if (continous == "p"):
            start_pause_time = time.time();
            input("Pausing!. Enter to un-pause.")
            pause_time += time.time() - start_pause_time
            print("Un-paused")
            continue
        if (continous == "e"):
            dump_to_file(projectfilepath.get_abs_path("projects.json"), projects)
            pause_time = 0
            print("Stop")
            break
        laptime = round((time.time() - lasttime - pause_time), 2)
        playsound(projectfilepath.get_abs_path(COMPLETED_SOUND_FILE))
        pause_time = 0
        print("Lap No. " + str(lapnum))
        print("Lap Time: " + str(laptime) + " ( " + convert_to_minsec(laptime) + " )")
        print("*"*20)
        notes = input("Notes (e = exit)? ")
        if (notes == "e"):
            return
        add_task_item(projects, selected_project, task, "lap", date_str, laptime, notes);
        dump_to_file(projectfilepath.get_abs_path("projects.json"), projects)
        lasttime = time.time()
        lapnum += 1    


def convert_sec_hour(nsecs):
    nsecs = int(round(nsecs))
    hours, minsecs = divmod(nsecs, 3600)
    mins, secs = divmod(minsecs, 60)
    timer = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)
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
    today_str = datetime.now().strftime(DATE_FORMAT)
    if (time_rec["date"].split()[0] == today_str):
        return True
    return False


def is_week_stat(time_rec):
    today = datetime.now()
    for idx in range(7):
        prev_time = today - timedelta(days=idx)
        day_str = prev_time.strftime(DATE_FORMAT)
        if (time_rec["date"].split()[0] == day_str):
            return True
    return False


def is_month_stat(time_rec):
    today = datetime.now()
    for idx in range(28):
        prev_time = today - timedelta(days=idx)
        day_str = prev_time.strftime(DATE_FORMAT)
        if (time_rec["date"].split()[0] == day_str):
            return True
    return False


def is_n_prev_day_stat(time_rec):
    today = datetime.now()
    for idx in range(28):
        prev_time = today - timedelta(days=idx)
        day_str = prev_time.strftime(DATE_FORMAT)
        if (time_rec["date"].split()[0] == day_str):
            return True
    return False


def date_and_delta_day(date_from_str, date_to):
    date_from = datetime.strptime(date_from_str, DATE_FORMAT)
    return date_from_str + " " + calendar.day_name[date_from.weekday()] + \
        " (" + str((date_to - date_from).days) + " day ago)"


def show_stats_laptime(predicate, tasks):
    laps = tasks["lap"]
    filtered_laps = list(filter(predicate, laps))
    result = ""
    if (len(filtered_laps) > 0):
        prev = filtered_laps[0]["time"]
        result += " Task: " + tasks["name"] + "\n"
        result += "  [Lap]:\n"
        avg = get_avg(filtered_laps)
        result += "   Average speed = " + str(avg) + " ( " + convert_sec_hour(avg) + " )\n"
        prev_date = None
        for lap in filtered_laps:
            date_str = lap["date"].split()[0]
            if (prev_date != None):
                if (prev_date != date_str):
                    prev_date = date_str
                    result += "\n   Date " + date_and_delta_day(prev_date, datetime.now()) + ": \n"
            else:
                prev_date = date_str
                result += "\n   Date " + date_and_delta_day(prev_date, datetime.now()) + ": \n"
            ratio = str(int(lap["time"] * 100 / prev)) + " %"
            ratio_avg = str(int(lap["time"] * 100 / avg)) + " %"
            result += "     At " + str(lap["date"].split()[1]) + ") " + \
             str(convert_sec_hour(int(round(lap["time"], 0)))) + " - " + \
              ratio + " - " + ratio_avg + " (" + str(lap["notes"]) + ")\n"
            prev = lap["time"]
        result += "\n"
    return result


def show_stats_countdown(predicate, tasks):
    countdowns = tasks["countdown"]
    filtered_countdowns = list(filter(predicate, countdowns))
    result = ""
    if (len(filtered_countdowns) > 0):
        prev = filtered_countdowns[0]["time"]
        result += "  [CountDown]:"
        avg = get_avg(filtered_countdowns)
        result += "   Average speed = " + str(avg) + " ( " + convert_sec_hour(avg) + " )\n"
        prev_date = None
        for countdown in filtered_countdowns:
            date_str = countdown["date"].split()[0]
            if (prev_date != None):
                if (prev_date != date_str):
                    prev_date = date_str
                    result += "\n   Date " + date_and_delta_day(prev_date, datetime.now()) + ": \n"
            else:
                prev_date = date_str
                result += "\n   Date " + date_and_delta_day(prev_date, datetime.now()) + ": \n"
            if (prev != 0):
                ratio = str(int(countdown["time"] * 100 / prev)) + " %"
                ratio_avg = str(int(countdown["time"] * 100 / avg)) + " %"
                result += "     At " + str(countdown["date"].split()[1]) + ") " + \
                 str(convert_sec_hour(int(round(countdown["time"], 0)))) + " - " + \
                 ratio + " - " + ratio_avg + " (" + str(countdown["notes"]) + ")\n"
            prev = countdown["time"]
        result += "\n"
    return result


def show_stats_pre(predicate, selected_project):
    result = ""
    for tasks in selected_project["tasks"]:
        result += show_stats_laptime(predicate, tasks)
        result += show_stats_countdown(predicate, tasks)
    return result


def print_strong_divider():
    print("\n##########################\n")


def show_all_project_stats(predicate, projects):
    print_strong_divider()
    for project in projects:
        result = show_stats_pre(predicate, project)
        if (result != ""):
            print("***Project: " + project["proj_name"])
            print(result)
    print_strong_divider()


def add_task_item(projects, selected_project, task, type, date_time_str, time, notes):
    for project in projects:
        if (project["proj_name"] == selected_project["proj_name"]):
            for task_iter in project["tasks"]:
                if (task_iter["name"] == task[1]["name"]):
                    task_iter[type].append({"date": date_time_str, "time":time, "notes": notes})
                    break


def add_task(projects, selected_project, task):
    print("Add task...")
    date_input = input("Date time? (format " + DATETIME_FORMAT + " or hh:mm:ss): ")
    date_time_str = ""
    if (date_input == ""):
        date_time_str = datetime.now().strftime(DATETIME_FORMAT)
    else:
        if (len(date_input.split()) == 1):
            date_str = datetime.now().strftime(DATE_FORMAT)
            time_str = date_input
            date_time_str = date_str + " " + time_str
        elif (len(date_input.split()) == 2): 
            date_time_str = date_input
        else:
            print("Wrong date format!")
            return
    notes = input("Notes (e = exit)? ")
    if (notes == "e"):
        return
    try:
        secs = int(input("Time in Secs? "))
        laptime = round(secs, 2)
        add_task_item(projects, selected_project, task, "lap", date_time_str, laptime, notes);
        dump_to_file(projectfilepath.get_abs_path("projects.json"), projects)
    except ValueError:
        print('Please enter an integer to represents seconds')


def print_option(options):
    for option in options:
        print (option["index"] + ". " + option["name"])


class Option:

    def __init__(self, index, name):
        self.index = index
        self.name = name


def color_input(str):
    return input(f"{Fore.LIGHTCYAN_EX}" + str + f"{Fore.WHITE}")


def color_line(str):
    print(f"{Fore.LIGHTCYAN_EX}" + str + f"{Fore.WHITE}", end='')


def choose_operator(projects, selected_project, selected_task):
    if (selected_project == None):
        print("Please choose project.")
        return
    if (selected_task == None):
        print("Please choose task.")
        return
    option = -2
    while (option > 4 or option < 0):
        try:
            print("Choose operator: \n "
            +"1. Lap time\n "
            +"2. Count down\n " 
            +"3. Show stats of selected project\n "
            +"4. Add task entry\n "
            +"0. Exit\n"
            +"Your choice: ")
            option = int(getch())
        except ValueError:
            print("Option must be integer")
    if (option == 1):
        run_laptime(projects, selected_project, selected_task)
    elif (option == 2):
        run_countdown(projects, selected_project, selected_task)
    elif (option == 3):
        show_stats_pre(lambda pred: True, selected_project)
    elif (option == 4):
        add_task(projects, selected_project, selected_task)
    elif (option == 0):
        return


def show_tasks_name(tasks):
    print()
    print("Select task in project: ")
    if (len(tasks) == 0):
        print ("There is NO task!")
    ind = 1
    for task in tasks:
        print(" " + str(ind) + ". " + task["name"])
        ind += 1


def select_task(projects, tasks):
    selected_task = None
    int_option = None
    Art = text2art("Task?", font='small')
    print(f"{Fore.BLUE}{Art}{Fore.WHITE}")
    while (selected_task == None):
        show_tasks_name(tasks)
        try:
            option = input("Your task: ")
            if (option.strip() == ""):
                return
            if (option == "e"):
                return
            int_option = int(option)
            if (int_option > len(tasks) or int_option < 1):
                print("Option must be integer in range 1.." + str(len(tasks)))
                continue
            selected_task = tasks[int_option - 1]
        except ValueError:
            print("Create new task: " + option)
            if (option.strip() != ""):
                tasks.append({"name": option, "lap": [], "countdown":[]})
                dump_to_file(projectfilepath.get_abs_path("projects.json"), projects)
            else:
                break
    if (selected_task != None):
        print("Selected task: " + selected_task["name"])
    return int_option, selected_task


def print_select_project_task(selected_project, selected_task):
    print("---")
    print(f"Selected project: {Fore.YELLOW}" + (selected_project["proj_name"] if selected_project != None else "None") + f"{Fore.WHITE}")
    print(f"Selected task: {Fore.RED}" + (selected_task[1]["name"] if selected_task != None else "None") + f"{Fore.RED}")


def write_line_file(file, content):
    file.write(content + "\n")
    

def write_stats_markdown_table_all_projects(projects, time_predicate, file):
    for project in projects:
        write_stats_markdown_table(project, time_predicate, file);


def write_stats_markdown_table(selected_project, time_predicate, file):
    write_line_file(file, "\n***Project: " + selected_project["proj_name"] + "***")
    for tasks in selected_project["tasks"]:
        laps = tasks["lap"]
        filtered_laps = list(filter(time_predicate, laps))
        if (len(filtered_laps) > 0):
            prev = filtered_laps[0]["time"]
            avg = get_avg(filtered_laps)
            write_line_file(file, "| Task: **" + tasks["name"] + "**| Average speed = " + str(avg) + " ( " + convert_sec_hour(avg) + " ) |")
            write_line_file(file, "|--|--|--|--|--|")
            write_line_file(file, "| Date | Time | Ratio vs Prev | Ratio vs Avg | Note |")
            for lap in filtered_laps:
                ratio = str(round(lap["time"] * 100 / prev, 1)) + "%"
                ratio_avg = str(round(lap["time"] * 100 / avg, 1)) + "%"
                write_line_file(file,
                    "| " + str(lap["date"]) + " | " + str(convert_sec_hour(int(round(lap["time"], 0)))) + " | +" + ratio + " | +" + ratio_avg + " | " + str(lap["notes"]) + " |")
                prev = lap["time"]
        
        countdowns = tasks["countdown"]
        filtered_countdowns = list(filter(time_predicate, countdowns))
        if (len(filtered_countdowns) > 0):
            prev = filtered_countdowns[0]["time"]
            avg = get_avg(filtered_countdowns)
            write_line_file(file, "| CountDown | Average speed = " + str(avg) + " ( " + convert_sec_hour(avg) + " ) |")
            write_line_file(file, "| Date | Time | Ratio vs Prev | Ratio vs Avg | Note |")
            for countdown in filtered_countdowns:
                if (prev != 0):
                    ratio = str(round(countdown["time"] * 100 / prev, 1)) + "%"
                    ratio_avg = str(round(countdown["time"] * 100 / avg, 1)) + "%"
                    write_line_file(file,
                        "| " + str(countdown["date"]) + " | " + str(convert_sec_hour(int(round(countdown["time"], 0)))) + " | +" + ratio + " | +" + ratio_avg + " | " + str(countdown["notes"]) + " |")
                prev = countdown["time"]


def confirmed_yes(confirm_str):
    return confirm_str == "y" or confirm_str == "Y"


def confirmed_yes_accept_empty(confirm_str):
    return confirmed_yes(confirm_str) or confirm_str == ""


def generate_markdown_table_to_file(projects, selected_project):
    opt = input("Select all projects ? (Y/N): ")
    if (not confirmed_yes(opt)):
        if (selected_project == None):
            print("Please select project first!")
            return
    to_file = input("Append to file path: ")
    if (to_file == ""):
        to_file = "/home/harrison-hienp/Desktop/code/script/py-automatic/resources/performance.md"
    gen_markdown_opt = input("Generate table markdown option: \n "
                        +"1. Generate week stat\n " 
                        +"2. Generate month stat\n "
                        +"3. Generate full stat\n "
                        +"4. Generate full stat group by date\n "
                        +"e. Exit\n"
                        +"Your Choice: ")
    if (gen_markdown_opt == "e"):
        return
    elif (gen_markdown_opt == "1"):
        with open(to_file, "a") as file:
            if (confirmed_yes(opt)):
                write_stats_markdown_table_all_projects(projects, is_week_stat, file)
            else: 
                write_stats_markdown_table(selected_project, is_week_stat, file)
    elif (gen_markdown_opt == "2"):
        with open(to_file, "a") as file:
            if (confirmed_yes(opt)):
                write_stats_markdown_table_all_projects(projects, is_month_stat, file)
            else: 
                write_stats_markdown_table(selected_project, is_month_stat, file)
    elif (gen_markdown_opt == "3"):
        with open(to_file, "a") as file:
            if (confirmed_yes(opt)):
                write_stats_markdown_table_all_projects(projects, lambda pred: True, file)
            else: 
                write_stats_markdown_table(selected_project, lambda pred: True, file)
    elif (gen_markdown_opt == "4"):
        try:
            ndays = int(input("Number of previous day: "))
            with open(to_file, "a") as file:
                write_stats_markdown_table_all_projects_by_date(projects, file, ndays)
        except ValueError:
            print("Number of previous day must be integer")
    file.close()
    print("Generated done.")


def write_stats_markdown_table_all_projects_by_date(projects, file, ndays):
    today = datetime.now()
    write_line_file(file, "| Performance Summary |||")
    write_line_file(file, "|--|--|--|--|")
    for idx in range(ndays + 1, 0, -1):
        prev_time = today - timedelta(days=idx)
        day_str = prev_time.strftime(DATE_FORMAT)
        same_date_tasks = []
        for project in projects:
            for task in project["tasks"]:
                for task_lap in task["lap"]:
                    if (task_lap["date"].split()[0] == day_str):
                        same_date_tasks.append({"project_name": project["proj_name"], "name": task["name"], "record": task_lap})
                for task_countdown in task["countdown"]:
                    if (task_countdown["date"].split()[0] == day_str):
                        same_date_tasks.append({"project_name": project["proj_name"], "name": task["name"], "record": task_countdown})
        if (len(same_date_tasks) > 0):
            write_line_file(file, "| " + date_and_delta_day(day_str, datetime.now()) + "||||")
            write_line_file(file, "| Time | Task | In | Note |")
            for task in same_date_tasks: 
                write_line_file(file, "| " + str(task["record"]["date"].split()[1]) + " | [" 
                                +task["project_name"] + "/" + task["name"] + "] | " 
                                +str(convert_sec_hour(int(round(task["record"]["time"], 0)))) 
                                +" | " + str(task["record"]["notes"]) + "|")
            write_line_file(file, "|||||")
   

def run_task_management():
    Art = text2art("MR. ROBOT !", font='big')
    print(f"{Fore.BLUE}{Art}{Fore.WHITE}")
 
    run_routine_notification = "y"
    if (len(sys.argv) > 1):
        run_routine_notification = sys.argv[1]
    if (confirmed_yes_accept_empty(run_routine_notification)):
        routine_thread = StoppableThread(target=routine.main, args=())
        routine_thread.start()
        sleep(1)
    selected_project = None
    selected_task = None
    while (True):
        Art = text2art("Operation?", font='small')
        print(f"{Fore.BLUE}{Art}{Fore.WHITE}")
        print_select_project_task(selected_project, selected_task)
        print(f"{Fore.WHITE}Overall option: \n "
                               +"1. Continue selected task\n " 
                               +"2. Choose task of current project\n "
                               +"3. Choose project\n "
                               +"4. Show statistics of all projects\n "
                               +"5. Show statistics of today\n "
                               +"6. Show statistics of week\n "
                               +"7. Show statistics of month\n "
                               +"8. Reload routines\n "
                               +"9. Generate statistics file (as Markdown table format)\n "
                               +"a. Show statistics of number of previous day\n "
                               +"b. Show statistics by day\n "
                               +"c. Stop routine notification\n "
                               +"e. Exit")
        color_line("Your Choice: ")
        overall_option = getch();
        projects = load_from_file(projectfilepath.get_abs_path("projects.json"))
        if (overall_option == "e"):
            print("Exit.")
            break
        elif (overall_option == "1"):
            print("Continue task")
            if (selected_task == None):
                print("No task selected! Please select task first.")
            else:
                choose_operator(projects, selected_project, selected_task)
        elif (overall_option == "2"):
            if (selected_project == None):
                print("Choose your project first.")
                continue
            selected_task = select_task(projects, selected_project["tasks"])
            choose_operator(projects, selected_project, selected_task)
        elif (overall_option == "3"):
            Art = text2art("Project?", font='small')
            print(f"{Fore.BLUE}{Art}{Fore.WHITE}")
            selected_project = select_project(projects)
            if (selected_project == None):
                print("Fail choosing project!")
                continue
            selected_task = select_task(projects, selected_project["tasks"])
            choose_operator(projects, selected_project, selected_task)
        elif (overall_option == "4"):
            show_all_project_stats(lambda pred: True, projects)
        elif (overall_option == "5"):
            show_all_project_stats(is_today_stat, projects)
        elif (overall_option == "6"):
            show_all_project_stats(is_week_stat, projects)
        elif (overall_option == "7"):
            show_all_project_stats(is_month_stat, projects)
        elif (overall_option == "8"):
            routine_thread.stop()
            routine_thread = StoppableThread(target=routine.main, args=())
            routine_thread.start()
            sleep(1)
        elif (overall_option == "9"):
            generate_markdown_table_to_file(projects, selected_project)
        elif (overall_option == "a"):
            print("Unsupported")
        elif (overall_option == "b"):
            date_stat_opt = input("Generate table markdown option: \n "
                        +"1. Show week stat\n " 
                        +"2. Show month stat\n "
                        +"3. Customized day\n ")
            if (date_stat_opt == "1"):
                show_stats_prev_day(projects, 7)
            if (date_stat_opt == "2"):
                show_stats_prev_day(projects, 30)
            if (date_stat_opt == "3"):
                try:
                    ndays = int(input("Number of previous day: "))
                    show_stats_prev_day(projects, ndays)
                except ValueError:
                    print("Number of previous day must be integer")
        elif (overall_option == "c"):
            routine_thread.stop()
        else:
            print ("Not supported")
    routine_thread.stop()
    routine_thread.join()
    print("Stopped all thread.")
    
    
def highlight_text(text):
    return f"{Fore.GREEN}{text}{Fore.WHITE}"


def sort_by_time(e):
    return str(e["record"]["date"].split()[1]);


def show_stats_prev_day(projects, ndays):
    print_strong_divider()
    today = datetime.now()
    for idx in range(ndays, -1, -1):
        prev_time = today - timedelta(days=idx)
        day_str = prev_time.strftime(DATE_FORMAT)
        same_date_tasks = []
        for project in projects:
            for task in project["tasks"]:
                for task_lap in task["lap"]:
                    if (task_lap["date"].split()[0] == day_str):
                        same_date_tasks.append({"project_name": project["proj_name"], "name": task["name"], "record": task_lap})
                for task_countdown in task["countdown"]:
                    if (task_countdown["date"].split()[0] == day_str):
                        same_date_tasks.append({"project_name": project["proj_name"], "name": task["name"], "record": task_countdown})
        if (len(same_date_tasks) > 0):
            print (" Date " + date_and_delta_day(day_str, datetime.now()) + ": ")
            total_time = 0
            same_date_tasks.sort(key=sort_by_time)
            for task in same_date_tasks: 
                total_time += int(round(task["record"]["time"], 0))
                print("  At " + highlight_text(str(task["record"]["date"].split()[1])) + " | [" + task["project_name"] + "/" + task["name"] + "] in " + 
                      str(convert_sec_hour(int(round(task["record"]["time"], 0)))) + " - " + 
                      str(task["record"]["notes"]))
            print(">> Total Time: " + str(convert_sec_hour(total_time)))
            print()
    print_strong_divider()
    

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
        task_manage_thread = threading.Thread(target=run_task_management, args=())
        task_manage_thread.start()
        task_manage_thread.join()
    except:
        task_manage_thread.join()


Main()

