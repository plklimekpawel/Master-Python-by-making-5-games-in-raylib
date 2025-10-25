from pyray import *
from raylib import *
from random import randint, uniform
from os.path import join
from utilities import hex_to_color

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720 
SIZE = {'paddle': (40,100), 'ball': (30,30)}
POS = {'player': (WINDOW_WIDTH - 50, WINDOW_HEIGHT / 2), 'opponent': (50, WINDOW_HEIGHT / 2)}
SPEED = {'player': 500, 'opponent': 250, 'ball': 450}
COLORS = {
    'paddle': hex_to_color('#ee322c'),
    'paddle shadow': hex_to_color('#b12521'),
    'ball': hex_to_color('#ee622c'),
    'ball shadow': hex_to_color('#c14f24'),
    'bg': hex_to_color('#002633'),
}
