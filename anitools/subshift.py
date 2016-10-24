import argparse
import re
import sys

import chardet

from .utils import file_open, get_input, remove_bom


class SubShifter:
    def __init__(self):

        self.fps_change = 0
        self.milli_shift = 0
        self.centi_shift = 0

        # Valid instance of a SubRip Text (SRT) time code
        self.srt_timeCode = re.compile(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})')

        # Valid instance of a SubStation Alpha (SSA/ASS) time code
        self.ssa_timeCode = re.compile(r'(\d{1}):(\d{2}):(\d{2}).(\d{2})')

        # Set valid limits for modulus cycling units i.e.
        # milliseconds are allotted 3 characters so max 999
        # then 0-999 is 1000 distinct numbers. Alternatively,
        # simply 1000 milliseconds in 1 second.

        # SRT
        self.srt_milli_limit = 1000
        self.srt_second_limit = 60
        self.srt_minute_limit = 60
        self.srt_hour_limit = 100

        # SSA/ASS
        self.ssa_centi_limit = 100
        self.ssa_second_limit = 60
        self.ssa_minute_limit = 60
        self.ssa_hour_limit = 10

    def srt_shifter(self, match):

        (current_hour, current_minute,
         current_second, current_milli) = match.groups()

        if self.fps_change:
            total_milli = self.get_milli(match)
            self.milli_shift = int((total_milli / self.fps_change) - total_milli)

        # Find remaining shift values by cascading
        # right to left i.e. ms->sec->min->hour
        second_shift = (((self.milli_shift + int(current_milli))
                         // self.srt_milli_limit))
        minute_shift = (((second_shift + int(current_second))
                         // self.srt_second_limit))
        hour_shift = (((minute_shift + int(current_minute))
                       // self.srt_minute_limit))

        # Using the shift values, find proper
        # time code whilst staying within limits
        hours = (hour_shift + int(current_hour)) % self.srt_hour_limit
        minutes = (minute_shift + int(current_minute)) % self.srt_minute_limit
        seconds = (second_shift + int(current_second)) % self.srt_second_limit
        milliseconds = ((self.milli_shift + int(current_milli))
                        % self.srt_milli_limit)

        # Pad zeroes if needed, then return adjusted time code
        return '{:02d}:{:02d}:{:02d},{:03d}'.format(hours, minutes,
                                                    seconds, milliseconds)

    def ssa_shifter(self, match):

        (current_hour, current_minute,
         current_second, current_centi) = match.groups()

        if self.fps_change:
            total_milli = self.get_milli(match)
            self.centi_shift = (
                int((total_milli / self.fps_change) - total_milli) // 10
            )

        # Find remaining shift values by cascading
        # right to left i.e. cs->sec->min->hour
        second_shift = (((self.centi_shift + int(current_centi))
                         // self.ssa_centi_limit))
        minute_shift = (((second_shift + int(current_second))
                         // self.ssa_second_limit))
        hour_shift = (((minute_shift + int(current_minute))
                       // self.ssa_minute_limit))

        # Using the shift values, find proper
        # time code whilst staying within limits
        hours = (hour_shift + int(current_hour)) % self.ssa_hour_limit
        minutes = (minute_shift + int(current_minute)) % self.ssa_minute_limit
        seconds = (second_shift + int(current_second)) % self.ssa_second_limit
        centiseconds = ((self.centi_shift + int(current_centi))
                        % self.ssa_centi_limit)

        # Pad zeroes if needed, then return adjusted time code.
        return '{}:{:02d}:{:02d}.{:02d}'.format(hours, minutes,
                                                seconds, centiseconds)

    def apply_changes(self, input_sub, output_sub):
        for line in input_sub:

            new_line = line

            if len(self.srt().findall(new_line)) == 2:
                new_line = self.srt().sub(self.srt_shifter, new_line)

            elif len(self.ssa().findall(new_line)) == 2:
                new_line = self.ssa().sub(self.ssa_shifter, new_line)

            output_sub.write(new_line)

        output_sub.close()

    def get_milli(self, match):

        total = 0

        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))

        # Convert SSA/ASS centiseconds to milliseconds if needed
        if len(match.group(4)) == 2:
            milliseconds = int(match.group(4)) * 10
        else:
            milliseconds = int(match.group(4))

        total += hours * 3600000
        total += minutes * 60000
        total += seconds * 1000
        total += milliseconds

        return total

    def set_milli(self, ms):
        self.milli_shift = ms
        self.centi_shift = self.milli_shift // 10

    def change_fps(self, fps):
        self.fps_change = fps

    def srt(self):
        return self.srt_timeCode

    def ssa(self):
        return self.ssa_timeCode


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('--shift', default=None)
    parser.add_argument('--fps', nargs=2, default=None)
    c_args = vars(parser.parse_args())

    e = chardet.detect(open(sys.argv[1], 'rb').read())['encoding']
    input_sub = file_open(c_args['input'], 'r', encoding=e).readlines()
    output_sub = file_open(c_args['output'], 'w', encoding='utf-8')

    input_sub[0] = remove_bom(input_sub[0])
    shifter = SubShifter()

    if c_args.get('shift') is not None:
        shifter.set_milli(int(c_args['shift']))
        shifter.apply_changes(input_sub, output_sub)
        return
    elif c_args.get('fps') is not None:
        original_fps, new_fps = c_args['fps']
        shifter.change_fps(float(new_fps) / float(original_fps))
        shifter.apply_changes(input_sub, output_sub)
        return

    prompt = ('\nPlease choose an option number:\n\n'
              '\t1 - shift subtitle time codes\n'
              '\t2 - adjust for an FPS change\n\n'
              '\t==>  ')

    choice = get_input(r'^(1|2)$', prompt)

    # Time code shift
    if choice == '1':

        prompt = ('\nPlease enter the desired shift in '
                  'milliseconds (negatives\naccepted). For '
                  'formats dealing in centiseconds, input will\n'
                  'be rounded down to nearest 100 milliseconds.\n\n'
                  '\t==>  ')

        shifter.set_milli(int(get_input(r'^-?[0-9]{1,7}$', prompt)))

    # Adjust time for FPS change
    elif choice == '2':

        valid_frame_rate = r'^[0-9]{1,3}(\.[0-9]{1,4})?$'

        original_fps = get_input(
            valid_frame_rate, '\nPlease enter the original FPS\n\n\t==>  '
        )
        new_fps = get_input(
            valid_frame_rate, '\nPlease enter the new FPS\n\n\t==>  '
        )

        shifter.change_fps(float(new_fps) / float(original_fps))

    shifter.apply_changes(input_sub, output_sub)

if __name__ == '__main__':
    main()
