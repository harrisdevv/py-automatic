# importing libraries
import time
import json

def dump_to_file(filename, obj):
    with open(filename, "w") as file:
        my_json_object = json.dump(obj, file)
def load_from_file(filename):
    with open(filename, "r") as file:
        return json.load(file)
 
def main():
    FILE_PROJECT_NAME = "projects.data"
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
        selected_project = {"index": maxIndex + 1, "proj_name": proj_input, "lap_time":[]}
        projects.append(selected_project)
    print("Selected project: " + str(selected_project))
    starttime=time.time()
    lasttime=starttime
    lapnum=1
    print("Press ENTER to count laps.\nPress CTRL+C to stop")
    try:
        while True:
            input()
            totaltime=round((time.time() - starttime), 2)
            laptime=round((time.time() - lasttime), 2)
            print("Lap No. "+str(lapnum))
            print("Total Time: "+str(totaltime))
            print("Lap Time: "+str(laptime))
            print("*"*20)
            selected_project["lap_time"].append(laptime)
            lasttime=time.time()
            lapnum+=1
    # Stopping when CTRL+C is pressed
    except KeyboardInterrupt:
        dump_to_file(FILE_PROJECT_NAME, projects)
        print("Done")

main()