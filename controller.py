#!/usr/bin/env python


import pygame
from pygame.locals import *


import event
from config import wait_ticks, fps

class CPUSpinnerController:

    """CPU Spinner controller"""

    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)

        self.clock = pygame.time.Clock()
        self.keep_going = True
        self.auto_mode = False

    def run(self):
        count = 0
        while self.keep_going:
            self.clock.tick(fps)
            #print "fps: ", self.clock.get_fps()
            ev = event.TickEvent()
            self.ev_manager.post(ev)

            if count == 0:
                if self.auto_mode:
                    ev = event.StepEvent()
                    self.ev_manager.post(ev)
                count = wait_ticks
            count -= 1

    def notify(self, ev):
        if isinstance(ev, event.QuitEvent):
            # this will stop the while loop from running
            self.keep_going = False
        elif isinstance(ev, event.ToggleAutoEvent):
            if self.auto_mode:
                self.auto_mode = False
            else:
                self.auto_mode = True

class KeyboardController:
    
    """Keyboard Controller"""

    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)

    def notify(self, e):
        if isinstance(e, event.TickEvent):
            for e in pygame.event.get():
                ev = None
                if e.type == QUIT:
                    ev = event.QuitEvent()
                elif e.type == KEYDOWN:
                    if e.key == K_q:
                        ev = event.QuitEvent()
                    elif e.key == K_r:
                        ev = event.ResetEvent()
                    elif e.key == K_SPACE:
                        ev = event.StepEvent()
                    elif e.key == K_c:
                        ev = event.ToggleAutoEvent()
                    elif e.key == K_v:
                        ev = event.ToggleViewEvent()
                    elif e.key == K_h:
                        ev = event.HelpEvent()

                if ev:
                    self.ev_manager.post(ev)
                    
