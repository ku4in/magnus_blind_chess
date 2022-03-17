#!/usr/bin/env python3

'''
Simple command line tool to play blind chess with Magnus Carlsen via Android app:
https://play.google.com/store/apps/details?id=pl.mw.playmagnus
This tool uses 'Clipper' app (https://github.com/majido/clipper) to communicate
with Magnus app via clipboard.
'''

ADB = 'adb'   # path to 'adb' command in your system

def help():
    print(f'Usage: {sys.argv[0]} [-b | --black] [-h | --help]')
    print()
    print(f'  -b, --black: specify this parameter to play for black, you play for white by default')
    print(f'  -h, --help:  show this help and exit')
    print()


import os
import sys
import time
from subprocess import Popen, PIPE


class Screen:
    '''make actions on a screen'''

    # parameters below are specific for each device
    # you should define them according to your screen resulution 
    board_x0 = 0              # x coordinate (in pixel) of left top edge of a chess board on a screen
    board_y0 = 412            # y coordinate (in pixel) of left top edge of a chess board on a screen
    board_x1 = 1080           # x coordinate (in pixel) of right buttom edge of a chess board on a screen
    board_y1 = 1492           # y coordinate (in pixel) of right buttom edge of a chess board on a screen
    menu = 1000, 70           # menu button position on screen
    close_menu = 80, 70       # position of a cross to close menu
    save_game = 550, 580      # position of 'save game' button in menu
    ok_button = 545, 1115     # position of 'OK' button
    back_button = 860, 1870   # position of 'back' button
    pawn = [(450, 830), (450, 1020),
    (450, 1200), (450, 1380)] # positions of Queen, Rook, Bishop, Knight buttons for pawn replacement
    game = ''                 # The game in pgn notation will be stored here
    TAP_SLEEP = 0.2           # Delay between taps
    MOVE_SLEEP = 3            # Delay after move (increase it if an error 'ILLEGAL MOVE' occurs when right move)


    def __init__(self):
        '''start 'Clipper' service to have access to clipboard'''
        cmd = f'{ADB} shell am startservice ca.zgrs.clipper/.ClipboardService &>/dev/null'
        p = Popen(cmd.split())
        # set the size of a field on a chess board
        self.field_size = (self.board_x1 - self.board_x0)/8
        
    def _tap_screen(self, x, y):
        # screen coordinates start from left top of a screen and grow buttom and right
        os.system(f'{ADB} shell input tap {x} {y}')
        time.sleep(self.TAP_SLEEP)

    def _tap_board(self, x, y):
        # coordinates on a board start from a1 field and grow up and right
        x += self.board_x0
        y = self.board_y1 - y
        os.system(f'{ADB} shell input tap {x} {y}')
        time.sleep(self.TAP_SLEEP)

    def _copy_game(self):
        '''returns game progress in pgn format'''
        self._tap_screen(*self.menu)
        self._tap_screen(*self.save_game)
        self._tap_screen(*self.ok_button)
        self._tap_screen(*self.close_menu)
        cmd = f'{ADB} shell am broadcast -a clipper.get'
        p = Popen(cmd.split(), stdin=PIPE, stdout=PIPE)
        out = p.stdout.read().decode('utf-8')
        out = out.split('data=')[1]    # clear data from adb stuff
        out = out[1:-2]                # clear data from adb stuff
        return out                     # return clear pgn notation

    def move(self, mov):
        """make a mov on a board specified in a string 'mov', i.e. 'e2e4'"""
        mov = mov.lower()    # make lower case
        if mov == 'back':
            self._tap_screen(*self.back_button)
            time.sleep(self.MOVE_SLEEP/2)
            return
        c = 'abcdefgh'
        n = '12345678'
        p = 'qrbk'
        if is_black:
            c = c[::-1]
            n = n[::-1]
        # split mov to start and end positions
        start_pos_x = int(c.find(mov[0]) * self.field_size + self.field_size/2)
        start_pos_y = int(n.find(mov[1]) * self.field_size + self.field_size/2)
        end_pos_x   = int(c.find(mov[2]) * self.field_size + self.field_size/2)
        end_pos_y   = int(n.find(mov[3]) * self.field_size + self.field_size/2)
        self._tap_board(start_pos_x, start_pos_y)
        self._tap_board(end_pos_x, end_pos_y)
        if mov[4:]:
            self._tap_screen(*self.pawn[p.find(mov[4])])
        time.sleep(self.MOVE_SLEEP)

    def answer(self):
        '''get last move of opponent'''
        new_game = self._copy_game()
        if new_game == self.game:
            answer = 'illegal move!'.upper()
            state  = self.game.split()[-1]
        else:
            answer, state = new_game.split()[-2:]
        self.game = new_game
        return answer, state


if __name__ == '__main__':
    if len(sys.argv) < 2:
        is_black = False
    else:
        if sys.argv[1] in ['-h', '--help']:
            help()
            sys.exit()
        is_black = '-b' in sys.argv[1]
    if is_black:
        print('You play for black')
    else:
        print('You play for white')

    s = Screen()
    if is_black:
        answer, state = s.answer()
        print(f"Magnus' move: {answer}")

    # Loop untill mate
    while True:
        try:
            move = input('Your move: ')
            # optional clear command to delete previous moves if you want to be completely 'blind'
            # os.system('clear')
            s.move(move)
            if move != 'back':
                answer, state = s.answer()
                if '*' in state:
                    print(f"Magnus' move: {answer}")
                else:
                    print(f"Last move: {answer}")
                    print(f"Result: {state}")
                    break
        except KeyboardInterrupt:
            print()
            sys.exit()
