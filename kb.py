#!/usr/bin/env python

import pdb

from aima.logic import expr, dpll_satisfiable
import ai


import time

try:
    import psyco
    psyco.bind(dpll_satisfiable)
except ImportError:
    print "psyco module not found."


class WumpusKB():
    """A KB for wumpus world"""

    def __init__(self, sentence=None):
        self.k = expr('~P00 & ~W00')

        li = []        
        for i in range(4):
            for j in range(4):
                for l, r in (('B', 'P'), ('S', 'W')):
                    left = "%s%s%s" % (l, i, j)
                    right_list = []
                    for s, t in ai.neighbors(i, j):
                        right_list.append("%s%s%s" % (r, s, t))
                    li.append("(%s <=> (%s))" % \
                              (left, ' | '.join(right_list)))
        e = expr(' & '.join(li))
        self.tell(e)

        # one and only one wumpus
        li = ['W%s%s' % (i, j) for i in range(4) for j in range(4)]
        e = expr(' | '.join(li))
        self.tell(e)


        li = ['(~W%s%s | ~W%s%s)' % \
              (i, j, x, y)
              for i in range(4) \
              for j in range(4) \
              for x in range(4) \
              for y in range(4) \
              if not ((i == x) and (j == y))]
        e = expr(' & '.join(li))
        self.tell(e)

    def tell(self, s):
        self.k &= s

    def ask(self, s):
        print "===================="
        print "ask about: ", s
        start = time.time()
        r = dpll_satisfiable(self.k & ~s)
        print "cost: ", time.time() - start
        if r is False:
            return True
        else:
            return False
