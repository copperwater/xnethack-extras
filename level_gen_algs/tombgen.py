import generator
from generator import Map
from generator import terrain as terr
from generator import dirs
from generator import ROWNO, COLNO
import random

# "Tomb" generator algorithm.
# Intended for the Archeologist quest lower filler levels.
# Designed to make a complex series of rooms and corridors that, if some of the doors are secret,
# is very hard to discover everything.
#
# Algorithm works by placing an initial, central room, then repeatedly selecting
# a valid position to place a door and extend a corridor from its edge. If a position on a corridor
# is selected, it must attempt to build a room; if a position on a room is selected, it must attempt
# to build a corridor.
# Corridors are walled in and contain floor tiles, rather than being dug-from-stone corridor tiles.
# They currently do not branch.

m = Map()

# make room in the given rectangle; walls are 1 space around it
def placeroom(x1, y1, x2, y2):
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    if not generator.isok(x1-1, y1-1):
        raise IndexError("Bad coordinate to placeroom: " + str(x1-1) + ' ' + str(y1-1))
    if not generator.isok(x2+1, y2+1):
        raise IndexError("Bad coordinate to placeroom: " + str(x2+1) + ' ' + str(y2+1))

    for x in range(x1, x2+1):
        for y in range(y1, y2+1):
            m[x][y] = terr.ROOM

    for x in range(x1-1, x2+2):
        m[x][y1-1] = terr.WALL
        m[x][y2+1] = terr.WALL

    for y in range(y1-1, y2+2):
        m[x1-1][y] = terr.WALL
        m[x2+1][y] = terr.WALL

    m.add_doorwalls(x1-1, y1-1, x2+1, y2+1, False)

# Note: corridor-making functions hardcode walls at either end to avoid having to pass
# which way they are intended to go.
# TODO: allow corridors to be placed if their walls would only overwrite other walls.
def placevertcorr(y1, y2, x):
    # y2 is intended to be the "end" of the corridor and should get a wall placed on it
    saved_y2 = y2
    if y1 > y2:
        y1, y2 = y2, y1
    for y in range(y1, y2+1):
        m[x-1][y] = terr.WALL
        m[x][y] = terr.ROOM
        m[x+1][y] = terr.WALL
    m[x][saved_y2] = terr.WALL
    m.add_doorwalls(x-1, y1, x+1, y2, True)

def placehorizcorr(x1, x2, y):
    saved_x2 = x2
    if x1 > x2:
        x1, x2 = x2, x1
    for x in range(x1, x2+1):
        m[x][y-1] = terr.WALL
        m[x][y] = terr.ROOM
        m[x][y+1] = terr.WALL
    m[saved_x2][y] = terr.WALL
    m.add_doorwalls(x1, y-1, x2, y+1, True)

# Place a random corridor extending some length from a selected door position.
def mkrandcorr(doorx, doory):
    dx, dy = m.adjacent_to(doorx, doory, terr.ROOM)
    cx = doorx - dx
    cy = doory - dy
    if dx != 0:
        # horizontal corridor
        # corrlen represents the amount of space this will go beyond the door,
        # counting the end wall (total width is corrlen)
        # TODO: bias corrlen towards creating longer corridors
        corrlen = random.randint(2, 10)
        if (corrlen < 4):
            corrlen = random.randint(2,10)
        endx = doorx + (-dx * corrlen)
        print("trying horiz corr:", cx, endx, doory)
        if m.footprintok(cx, doory-1, endx-dx, doory+1):
            placehorizcorr(cx, endx, doory)
            m[doorx][doory] = terr.DOOR
            return True
    else:
        # vertical corridor
        corrlen = random.randint(2, 4)
        endy = doory + (-dy * corrlen)
        print("trying vert corr:", cy, endy, doorx)
        if m.footprintok(doorx-1, cy, doorx+1, endy-dy):
            placevertcorr(cy, endy, doorx)
            m[doorx][doory] = terr.DOOR
            return True
    return False


def mkrandroom(doorx, doory):
    area = random.randint(20, 60)
    h = random.randint(2, 6)
    w = area // h
    if (w > 12):
        w = random.randint(4, 12)

    dx, dy = m.adjacent_to(doorx, doory, terr.ROOM)
    cx = doorx - dx
    cy = doory - dy
    if dx != 0:
        endx = doorx + (-dx * w)
        hy = doory + random.randint(0, h-1)
        ly = hy - (h - 1)
        if m.footprintok(cx, ly-1, endx-dx, hy+1):
            placeroom(cx, ly, endx, hy)
            m[doorx][doory] = terr.DOOR
            return True
    else:
        endy = doory + (-dy * h)
        hx = doorx + random.randint(0, w - 1)
        lx = hx - (w - 1)
        if m.footprintok(lx-1, cy, hx+1, endy-dy):
            placeroom(lx, cy, hx, endy)
            m[doorx][doory] = terr.DOOR
            return True
    return False

# Initial central-ish room, square.
room_w = 5 + random.randint(0,3)
sx = (COLNO - room_w) // 2
sy = (ROWNO - room_w) // 2
placeroom(sx, sy, sx + room_w - 1, sy + room_w - 1)
print("Init room:", sx, sy, sx + room_w - 1, sy + room_w - 1)

def rn2(x):
    return random.randint(0, x-1)

ndoors = 0
while ndoors < 25 and len(m.doorwalls) > 0:
    doorx, doory, isCorr = m.random_doorwall()[0]

    if not m.valid_door_pos(doorx, doory):
        # maybe it was already used for some previous door
        m.doorwalls.remove((doorx, doory, isCorr))
        continue

    if isCorr: #random.randint(0,9) < 5:
        if rn2(2) == 0:
            if mkrandroom(doorx, doory):
                ndoors += 1
        else:
            if mkrandcorr(doorx, doory):
                if rn2(3) > 0:
                    # test: count as door for ndoors, but actually don't place a door...
                    m[doorx][doory] = terr.ROOM
                    ndoors += 1
    else:
        if rn2(3) == 0:
            continue
        if mkrandcorr(doorx, doory):
            ndoors += 1
    print("ndoors", ndoors)

# place upstairs in starting room
ustairx = random.randint(sx, sx + room_w - 1)
ustairy = random.randint(sy, sy + room_w - 1)
m[ustairx][ustairy] = terr.USTAIR

# place downstairs somewhere far away from upstairs
xx = ustairx
yy = ustairy
LIMIT = 24
while (xx-ustairx)**2 + (yy-ustairy)**2 < LIMIT ** 2 or m[xx][yy] != terr.ROOM:
    xx = random.randint(0, generator.COLNO-1)
    yy = random.randint(0, generator.ROWNO-1)
print(ustairx, ustairy, xx, yy)
m[xx][yy] = terr.DSTAIR

# m[12][11] = terr.LAVA

m.printmap()

