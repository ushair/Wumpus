#!/usr/bin/env python

"""
World map & Percept data sturcture
==================================

B: Breeze
G: Gold
P: Pit
S: Stench
W: Wumpus

Every sector in the world contains an indicator list [B, G, P, S, W]
2 indicates presence, 1 indicates uncertainty, 0 indicates absence
"""
import pdb

import random
import time
import copy
import numpy

import event
from kb import WumpusKB
from aima.logic import expr


action_list = {
    'forward': 0,
    'left': 1,
    'right': 2,
    'shoot': 3,
    'pick': 4,
    'noop': 5
    }

facing_list = {
    'up': 0,
    'right': 1,
    'down': 2,
    'left': 3
    }

map_list = ['B', 'G', 'P', 'S' , 'W']


def neighbors(i, j):
    li = set()
    if (i - 1) in range(4):
        li.add((i-1, j))
    if (i + 1) in range(4):
        li.add((i+1, j))
    if (j - 1) in range(4):
        li.add((i, j-1))
    if (j + 1) in range(4):
        li.add((i, j+1))
    return li

class Agent:

    """AI agent"""

    def __init__(self, ev_manager):
        self.ev_manager = ev_manager
        self.ev_manager.register_listener(self)
        self.alive = False
        self.gold_picked = False
        self.all_pos = set()
        for i in range(4):
            for j in range(4):
                self.all_pos.add((i, j))

    def _generate_world(self):
        self.alive = True
        self.gold_picked = False
        self.pos = (-1, 0)
        self.facing = facing_list['right']
        self.visited = set()
        self.danger = set()
        self.safe = set()
        self.fringe = set()
        self.plan = [action_list['forward']]
        
        self.world = numpy.zeros((4, 4, 5))
        self.known_world = numpy.ones((4, 4, 5))
        self.kb = WumpusKB()

        # choosing a sector for Gold
        i, j = self._random_ij()
        self.world[i][j][1] = 2

        # choosing a sector for Wumpus
        i, j = self._random_ij()
        self.world[i][j][4] = 2
        # generating Stench
        for pos in neighbors(i, j):
            self.world[pos[0]][pos[1]][3] = 2

        for i in range(4):
            for j in range(4):
                if not ((i == 0) and (j == 0)):
                    
                    # generating Pit for this sector with a
                    # Probability of 0.2
                    if random.randint(1, 10) <= 2:
                        self.world[i][j][2] = 2

                        # generating Breeze
                        for pos in neighbors(i, j):
                            self.world[pos[0]][pos[1]][0] = 2

        ev = event.WorldBuiltEvent(self.world)
        self.ev_manager.post(ev)

    def _random_ij(self):
        r = random.randint(1, 15)
        if r <= 3:
            i = 0
            j = r
        else:
            i = (r - 3) / 4
            j = (r + 1) % 4

        return (i, j)

    def _next(self):
        ev = event.BusyEvent()
        self.ev_manager.post(ev)

        if self.alive and (not self.gold_picked):
            if len(self.plan) > 0:
                action = self.plan.pop()
            else:
                i, j = (self.pos[0], self.pos[1])
                percept = self.world[i][j]
                action = self._pl_wumpus_agent(percept)

            self._do(action)
        else:
            ev = event.ResetEvent()
            self.ev_manager.post(ev)

        ev = event.ReadyEvent()
        self.ev_manager.post(ev)

    def _pl_wumpus_agent(self, percept):
        if len(self.safe) > 0:
            source = self.safe
        elif len(self.fringe) > 0:
            source = self.fringe
        else:
            source = self.danger
        goal = source.pop()
        self.plan = self._path2plan(self._shortest_path(goal))
        action = self.plan.pop()
        return action

    def _find_safe(self, i, j):
        new = neighbors(i, j) - self.visited
        new -= self.safe
        new -= self.danger

        new_safe = set()
        new_danger = set()

        if (self.world[i][j][0] == 0) and (self.world[i][j][3] == 0):
            self.fringe -= set((i, j))
            new_safe |= new
        else:
            self.fringe |= new

        print "fringe: ", self.fringe

        fringe = self.fringe.copy()
        if len(self.visited) > 1:
            for x in fringe:
                if self.kb.ask(expr('(P%s%s | W%s%s)' % (x*2))):
                    new_danger.add(x)
                    self.fringe.remove(x)
                    ev = event.FoundDangerEvent(x)
                    self.ev_manager.post(ev)
                elif self.kb.ask(expr('(~P%s%s & ~W%s%s)' % (x*2))):
                    new_safe.add(x)
                    self.fringe.remove(x)
        if len(new_safe) > 0:
            self.safe |= (new_safe)
        if len(new_danger) > 0:
            self.danger |= new_danger

        print "safe list: ", self.safe

    def _shortest_path(self, goal):
        g = self.visited
        v = {}
        for x in g:
            v[x] = 256
        v[goal] = 0

        def v_neighbors(i, j, s):
            li = []
            for t in neighbors(i, j):
                 if (t in self.visited) and (t not in s):
                    li.append(t)
            return li

        def get_path(v):
            path = []
            a = self.pos
            t = v[a]
            while t > 1:
                for x in v_neighbors(a[0], a[1], s):
                    if v[x] < t:
                        t = t - 1
                        path.append(x)
                        a = x
                        break
            return path

        s = [goal]
        while (len(s) > 0):
            u = s.pop()
            for x in v_neighbors(u[0], u[1], s):
                if v[x] > v[u] + 1:
                    v[x] = v[u] + 1
                    s.append(x)

        pa = get_path(v)
        pa.append(goal)
        return pa

    def _path2plan(self, path):
        plan = []
        prev = self.pos
        prev_facing = self.facing
        for pos in path:
            dx = pos[0] - prev[0]
            dy = pos[1] - prev[1]
            dy_dict = {
                -1: 'down',
                1: 'up',
                0: 'up' # dummy item
                }
            dx_dict = {
                -1: 'left',
                1: 'right',
                0: dy_dict[dy]
                }
            facing = facing_list[dx_dict[dx]]
            d = facing - prev_facing

            if d != 0:
                c = abs(d)
                if c > 2:
                    d = -d
                    c = c % 2
                if d < 0:
                    direction = action_list['left']
                elif d > 0:
                    direction = action_list['right']

                plan.extend([direction] * c)
                prev_facing = facing
            plan.append(action_list['forward'])
            prev = pos
        plan.reverse()
        return plan

    def _do(self, action):
        facing_dict = {
                facing_list['up']: (0, 1),
                facing_list['right']: (1, 0),
                facing_list['down']: (0, -1),
                facing_list['left']: (-1, 0),
                }
        if action is action_list['forward']:
            dx, dy = facing_dict[self.facing]
            new_pos = (self.pos[0]+dx, self.pos[1]+dy)
            if new_pos in neighbors(*self.pos):
                ev = event.PlayerForwardEvent(new_pos)
                self.ev_manager.post(ev)

                if new_pos not in self.visited:
                    i, j = new_pos
                    percept = self.world[i][j]
                    ev = event.PlayerPerceiveEvent(percept)
                    self.ev_manager.post(ev)

                    self.visited.add((i, j))
                    if (i, j) in self.safe:
                        self.safe.remove((i, j))
                    self.known_world[i][j] = percept

                    if percept[1] == 2:
                        self.gold_picked = True
                        self._do(action_list['pick'])
                    elif (percept[2] == 2) or (percept[4] == 2):
                        self.alive = False
                        ev = event.PlayerDieEvent()
                        self.ev_manager.post(ev)
                    else:
                        c = 0
                        know = []
                        for x in percept:
                            if x == 2:
                                know.append("%s%s%s" % (map_list[c], i, j))
                            elif x == 0:
                                know.append("~%s%s%s" % (map_list[c], i, j))
                            c += 1
                        if len(know) > 0:
                            print "tell kb: ", ' & '.join(know)
                            self.kb.tell(expr(' & '.join(know)))

                        self._find_safe(i, j)
                self.pos = new_pos
        elif action is action_list['left']:
            self.facing = (self.facing - 1) % 4
            
            ev = event.PlayerTurnEvent(
                event.PlayerTurnEvent.direction_list['left'], self.facing)
            self.ev_manager.post(ev)

        elif action is action_list['right']:
            self.facing = (self.facing + 1) % 4

            ev = event.PlayerTurnEvent(
                event.PlayerTurnEvent.direction_list['right'], self.facing)
            self.ev_manager.post(ev)

        elif action is action_list['shoot']:
            def all_along(pos, facing):
                all_pos = []
                dx, dy = facing_dict[facing]
                x, y = (self.pos[0] + dx, self.pos[1] + dy)
                while (x in range(4)) and (y in range(4)):
                    all_pos.append((x, y))
                    x, y = (x + dx, y + dy)
                return all_pos
            for i, j in all_along(self.pos, self.facing):
                if self.world[i][j][4]:
                    self._wumpus_die(i, j)
                    
                    ev = event.PlayerShootEvent()
                    self.ev_manager.post(ev)

        elif action is action_list['pick']:
            i, j = (self.pos[0], self.pos[1])
            self.world[i][j][1] = 0
            self.gold_picked = True

            ev = event.PlayerPickEvent(self.pos)
            self.ev_manager.post(ev)

    def _wumpus_die(self, i, j):
        self.world[i][j][4] = 0
        for pos in neighbors(i, j):
            self.world[pos[0]][pos[1]][3] = 0 # eliminate stench

        ev = event.WumpusDieEvent(pos)
        self.ev_manager.post(ev)

    def notify(self, e):
        if isinstance(e, event.GenerateRequestEvent):
            self._generate_world()
        elif isinstance(e, event.StepEvent):
            self._next()
