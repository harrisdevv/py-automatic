#!/usr/bin/python

PREFIX_FILE_PATH = "/home/harrison-hienp/Desktop/code/script/py-automatic/"


def get_abs_path(path):
    if (path.startswith("/")):
        path = path[1:]
    return PREFIX_FILE_PATH + path
    
