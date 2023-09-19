import tkinter as tk
import recorder

# --- functions ---

def start():
    global running

    if running is not None:
        print('already running')
    else:
        running = rec.record(10, 'nonblocking.wav')
        running.start_recording()

def stop():
    global running

    if running is not None:
        running.stop_recording()
        running.close()
        running = None
    else:
        print('not running')

# --- main ---

rec = recorder.Recorder(channels=2)
running = None

root = tk.Tk()

button_rec = tk.Button(root, text='Start', command=start)
button_rec.pack()

button_stop = tk.Button(root, text='Stop', command=stop)
button_stop.pack()

root.mainloop() 