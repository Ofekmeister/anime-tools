import codecs
import re
import sys

input = input if sys.version[0] >= '3' else raw_input


def remove_bom(line):
    return line[3:] if line[:3] == codecs.BOM_UTF8 else line


def get_input(raw_string, message):
    temp = None
    while temp is None:
        temp = input(message)
        if not re.match(raw_string, temp):
            temp = None
        else:
            return temp
