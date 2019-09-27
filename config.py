#!/usr/bin/env python

import os

#
# application-wide consistent color definition
#

color = {
    'gray': (100, 100, 100),
    'black': (0, 0, 0),
    'red': (250, 0, 0),
    'green': (0, 250, 0),
    'light_green': (20, 60, 20),
    'background': (255, 255, 255),
    'urgent': (150, 50, 50),
    'white': (255, 255, 255),
    'help': (153, 255, 51),
    'info': (153, 255, 51),
    'danger': (60, 30, 30)
    }

instruction = "Press H to view help, SPACE to step, Q to quit"

help = """
  Wumpus World

   H: Display this help info
   Space: Step
   C: Toggle auto/manual step mode
   V: Toggle view all mode
   R: Reset the world
   Q: Quit
        programmer: X__X Ushair X__X
"""

# Frames per second
fps = 60

# status light
light_flick_ticks = 5

# In auto mode, how many ticks to wait before generating next step
# event
wait_ticks = 1


status_font = (os.path.join('font', 'Shadows.ttf'), 24)
help_font = status_font

