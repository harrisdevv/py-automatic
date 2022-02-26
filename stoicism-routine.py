from playsound import playsound
  
playsound('/path/note.wav')

# Python3 program to demonstrate the use of
# choice() method
 
# import random
import random
 
# prints a random value from the list
list1 = [1, 2, 3, 4, 5, 6]
print(random.choice(list1))
 
# prints a random item from the string
string = "striver"
print(random.choice(string))

print("A random number from range is : ", end="")
print(random.randrange(20, 50, 3))

print("The mapped random number with 5 is : ", end="")
print(random.random())
 
# using seed() to seed to 7 again
random.seed(7)
 
# printing mapped random number
print("The mapped random number with 7 is : ", end="")
print(random.random())



import datetime

x = datetime.datetime.now()
print(x)

x = datetime.datetime.now()

print(x.year)
print(x.strftime("%A"))

x = datetime.datetime(2020, 5, 17)
date_time = datetime.fromtimestamp(1887639468)

today = date.today()
   
# Converting the date to the string
Str = date.isoformat(today)
print("String Representation", Str)
print(type(Str))
timetuple()	Returns an object of type time.struct_time
weekday()	Returns the day of the week as integer where Monday is 0 and Sunday is 6


from datetime import time
 
# calling the constructor
my_time = time(13, 24, 56)
 
print("Entered time", my_time)
 
# calling constructor with 1
# argument
my_time = time(minute=12)
print("\nTime with one argument", my_time)
 
# Calling constructor with
# 0 argument
my_time = time()
print("\nTime without argument", my_time)



# Timedelta function demonstration
from datetime import datetime, timedelta
 
# Using current time
ini_time_for_now = datetime.now()
 
# printing initial_date
print("initial_date", str(ini_time_for_now))
 
# Some another datetime
new_final_time = ini_time_for_now + \
    timedelta(days=2)
 
# printing new final_date
print("new_final_time", str(new_final_time))
 
 
# printing calculated past_dates
print('Time difference:', str(new_final_time -
                              ini_time_for_now))


 
from datetime import datetime as dt
 
# Getting current date and time
now = dt.now()
print("Without formatting", now)
 
# Example 1
s = now.strftime("%A %m %-Y")
print('\nExample 1:', s)
 
# Example 2
s = now.strftime("%a %-m %y")
print('\nExample 2:', s)
 
# Example 3
s = now.strftime("%-I %p %S")
print('\nExample 3:', s)
 
# Example 4
s = now.strftime("%H:%M:%S")
print('\nExample 4:', s)


# import datetime module from datetime
from datetime import datetime
  
# consider the time stamps from a list  in string
# format DD/MM/YY H:M:S.micros
time_data = ["25/05/99 02:35:8.023", "26/05/99 12:45:0.003",
             "27/05/99 07:35:5.523", "28/05/99 05:15:55.523"]
  
# format the string in the given format : day/month/year 
# hours/minutes/seconds-micro seconds
format_data = "%d/%m/%y %H:%M:%S.%f"
  
# Using strptime with datetime we will format string
# into datetime
for i in time_data:
    print(datetime.strptime(i, format_data))


# 





