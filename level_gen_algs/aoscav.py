import generator
from generator import Map
from generator import terrain as terr
from generator import ROWNO, COLNO
from generator import isok
from mkmap import nethack_mkmap

# Caverns+rooms generator algorithm.
# Intended for Gehennom.
# Designed to make a cavernous level but which has rooms organically attached
# to the caverns, sometimes inside it.

m = Map()
nethack_mkmap(m, pass_iters=[3,1,2]) # do caverns

# Criteria: must be a room square that has exactly two orthogonal neighbors on opposite sides, and
# have no other orthogonal neighbors. Diagonal neighbors are irrelevant.
def is_chokepoint(x, y):
    if m[x][y] != terr.ROOM:
        return False
    neighborsNS = 0
    neighborsEW = 0
    if isok(x-1, y) and m[x-1][y] == terr.ROOM:
        neighborsEW += 1
    if isok(x+1, y) and m[x+1][y] == terr.ROOM:
        neighborsEW += 1
    if isok(x, y-1) and m[x][y-1] == terr.ROOM:
        neighborsNS += 1
    if isok(x, y+1) and m[x][y+1] == terr.ROOM:
        neighborsNS += 1
    return abs(neighborsNS - neighborsEW) == 2

'''
# Locate choke points: those which cordon off a section of map.
chokepts = []
for x in range(COLNO):
    for y in range(ROWNO):
        if is_chokepoint(x,y):
            chokepts.append((x,y))
'''

# Do a floodfill
m[40][9] = terr.ROOM
pts = m.floodfill(40, 9, False, (lambda x, y: m[x][y] == terr.ROOM and not is_chokepoint(x, y)))

# Idea:
# Try to make a square-like shape from an appropriately sized floodfill area
# by finding points of rock which are surrounded on at least two sides by the
# non-chokepoint ROOM tiles of this floodfill area, and are not touching any
# other ROOM tiles in any direction, even diagonally, and adding them to the floodfill area.
# Do this greedily a few times.

for x,y in pts:
    m[x][y] = terr.TREE

# m.wallify()
m.printmap()
