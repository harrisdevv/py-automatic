import time
def countdown():
	nsecs = int(input("Enter number of seconds: "))
	while nsecs:
		mins, secs = divmod(nsecs, 60)
		timer = '{:02d}:{:02d}'.format(mins, secs)
		print(timer, end="\r")
		time.sleep(1)
		nsecs -= 1
	notes = input("Notes? ")
	return {"secs": nsecs, "notes": notes}

countdown()



