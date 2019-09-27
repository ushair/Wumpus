import ai
import event

e = event.EventManager()
a = ai.Agent(e)

a._reset_world()
a.visited = [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (1, 2)]
a.pos = (2, 0)
goal = (1, 3)
path = a._shortest_path(goal)
plan = a._path2plan(path)

print "visited :", a.visited
print "cur_pos :", a.pos
print "goal :", goal
print "path :", path
print "plan :", plan
