# This script was written before I loved comments, and is
# therefore magic to me now. Please don't ask about it.

import os
import pyperclip
import re
from .utils import get_input

ABSOLUTE = re.compile(r"(?:^|(?<=[^a-z0-9]))(?:ep?(?<=e|p)[^a-z0-9]?)?([0-9]+)x?([0-9]*)(?:(?=[^a-z0-9])|$)", re.I)
SEASON = re.compile(r"(?:^|(?<=[^a-z0-9]))se?([0-9]+).?ep?([0-9]+)(?:(?=[^a-z0-9])|$)", re.I)


def get_match(s):
    m = None

    for i in SEASON.finditer(s):
        if m is None:
            m = i
        elif i.span()[1] - i.span()[0] > m.span()[1] - m.span()[0]:
            m = i

    if m is not None:
        return m

    for i in ABSOLUTE.finditer(s):
        if m is None:
            m = i
        elif i.span()[1] - i.span()[0] > m.span()[1] - m.span()[0]:
            m = i

    return m


def main():

    valid_file = re.compile(r'\.(mkv|mp4|m4v|avi|srt|ssa|ass|txt|aac|ac3|h264|m4a)$')

    clipboard_dir = pyperclip.paste()
    s = '\nIs this the correct directory:\n\n{}\n\n(y/n) ==>'.format(clipboard_dir)

    if get_input(r'^(y|n)$', s) == 'y':
        d = clipboard_dir
    else:
        d = get_input(r'.+', '\nEnter target directory:\n\n\t==>  ')

    os.chdir(d)
    current_dir = os.getcwd()

    title = get_input(r'^[^\"\\/*<>|:]+$', '\nEnter title:\n\n\t==>  ')

    sub_format = get_input(r'^(a|e|s|x)$',
                           ('\nEnter format:\n\n'
                            '\ta - \"Title 105\"\n'
                            '\te - \"Title ep77\"\n'
                            '\ts - \"Title S03E22\"\n'
                            '\tx - preserve original structure\n\n'
                            '\t==>  '))

    for file in os.listdir(current_dir):

        valid_search = valid_file.search(file)

        if valid_search is not None:

            match = get_match(file)

            if match is not None:

                ext = valid_search.group(0)
                season = None
                episode = None

                if match.group(2):
                    season = int(match.group(1))
                    episode = int(match.group(2))
                    absolute = int('{0}{1:02d}'.format(season, episode))
                else:
                    absolute = int(match.group(1))

                if sub_format == 'x':
                    os.rename(file, '{0} {1}{2}'.format(title, match.group(0), ext))
                elif sub_format == 'a':
                    os.rename(file, '{0} {1:02d}{2}'.format(title, absolute, ext))
                elif sub_format == 'e':
                    os.rename(file, '{0} EP{1:02d}{2}'.format(title, absolute, ext))
                elif sub_format == 's':
                    if season is not None:
                        os.rename(file, '{0} S{1:02d}E{2:02d}{3}'.format(title, season, episode, ext))
                    elif absolute < 100:
                        os.rename(file, '{0} S01E{1:02d}{2}'.format(title, absolute, ext))
                    else:
                        t = str(absolute)
                        for i in range(1, len(t)):
                            se = int(t[:i])
                            ep = int(t[i:])
                            new_name = '{0} S{1:02d}E{2:02d}{3}'.format(title, se, ep, ext)
                            choice = get_input(r'^(y|n)$',
                                               ('\n\n{0}\n\nto\n\n'.format(file) +
                                                '{0}'.format(new_name) +
                                                '\n\nCorrect? (y/n):\n\n\t==>  '))

                            if choice == 'y':
                                os.rename(file, new_name)
                                break
