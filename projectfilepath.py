#!/usr/bin/python

PREFIX_FILE_PATH = "/home/hienphan/Desktop/code/script/py-automatic/resources/"


def get_abs_path(path):
    if (path.startswith("/")):
        path = path[1:]
    return PREFIX_FILE_PATH + path
    
