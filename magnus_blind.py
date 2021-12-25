#!/usr/bin/env python3

'''
Simple command line tool to play blind chess with Magnus Carlsen via Android app:
https://play.google.com/store/apps/details?id=pl.mw.playmagnus
This tool uses 'Clipper' app (https://github.com/majido/clipper) to communicate
with Magnus app via clipboard.
'''

ADB = 'adb'

def help():
    print('Usage: ')


import os
import time
from subprocess import Popen, PIPE

class Screen:
    '''make actions on a screen'''

    board_x0 = 0
    board_y0 = 412
    board_x1 = 1080
    board_y1 = 1492
    menu = 1000, 70
    close_menu = 80, 70
    save_game = 550, 580
    ok_button = 545, 1115

    def __init__(self):
        # statr clipboard service
        cmd = 'adb shell am startservice ca.zgrs.clipper/.ClipboardService &>/dev/null'
        p = Popen(cmd.split())
        print()
        # os.system('adb shell am startservice ca.zgrs.clipper/.ClipboardService &>/dev/null')
        self.field_size = (self.board_x1 - self.board_x0)/8

    def _copy_game(self):
        self._tap_screen(*self.menu)
        time.sleep(0.2)
        self._tap_screen(*self.save_game)
        time.sleep(0.2)
        self._tap_screen(*self.ok_button)
        time.sleep(0.2)
        self._tap_screen(*self.close_menu)
        time.sleep(0.2)
        cmd = f'{ADB} shell am broadcast -a clipper.get'
        p = Popen(cmd.split(), stdin=PIPE, stdout=PIPE)
        out = p.stdout.read().decode('utf-8')
        return out

    def move(self, mov):
        """make a mov on a board specified in string 'mov', i.e. 'e2e4'"""
        mov = mov.lower()    # make lower case
        s = 'abcdefgh'
        # split mov to start and end positions
        start_pos_x = int(s.find(mov[0]) * self.field_size + self.field_size/2)
        start_pos_y = int((int(mov[1])-1) * self.field_size + self.field_size/2)
        end_pos_x   = int(s.find(mov[2]) * self.field_size + self.field_size/2)
        end_pos_y   = int((int(mov[3])-1) * self.field_size + self.field_size/2)
        self._tap_board(start_pos_x, start_pos_y)
        time.sleep(0.2)
        self._tap_board(end_pos_x, end_pos_y)

    def answer(self):
        return self._copy_game().split()[-3]
        
    def _tap_screen(self, x, y):
        # screen coordinates starts from left top of a screen and grow buttom and right
        os.system(f'{ADB} shell input tap {x} {y}')

    def _tap_board(self, x, y):
        # coordinates on a board starts from a1 field and grow up and right
        x += self.board_x0
        y = self.board_y1 - y
        os.system(f'{ADB} shell input tap {x} {y}')


if __name__ == '__main__':
    s = Screen()
    time.sleep(0.5)
    answer = 'dumy'
    while '#' not in answer:
        move = input('Your move: ')
        s.move(move)
        time.sleep(2)
        answer = s.answer()
        print(f"Magnu's answer: {answer}")
