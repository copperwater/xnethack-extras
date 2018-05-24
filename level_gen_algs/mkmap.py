import generator
from generator import Map
from generator import terrain as terr
from generator import ROWNO, COLNO
from generator import isok
from generator import rn2
import random
import copy

# NetHack's "cavernous" generator algorithm, found in places like the Mines
# filler levels.
# This file provides one routine, nethack_mkmap(), that does it all: it is
# supposed to be an exact reimplementation of the mkmap() function found in
# NetHack, with nothing else added.  This is so it can be used as a base by
# other things.
#
# Algorithm works by generating a grid where squares may be rock or floor
# randomly, and then running a modified Conway's Game of Life and a couple
# other basic cellular automata. Lastly, all disconnected regions are connected
# by digging corridors between them.

class IrregularRoom():
    def __init__(self):
        self.coords = []
    def size(self):
        return len(self.coords)
    def somexy(self):
        return random.choice(self.coords)
    def lx(self):
        return min([x for x, y in self.coords])
    def hx(self):
        return max([x for x, y in self.coords])
    def ly(self):
        return min([y for x, y in self.coords])
    def hy(self):
        return max([y for x, y in self.coords])

# identical to nethack's pass_one, except it uses a backup buffer:
# cells with < 3 neighbors die, with > 4 come to life, 3 or 4 stay the same
def nethack_pass_one(m):
    # For some reason, in actual nethack, pass_one doesn't use a backup buffer,
    # and this has a significant effect on the shape of the output map.
    # To emulate this behavior, use the following line:
    backup_buffer = m._map
    # To use a backup buffer, use the following line:
    # backup_buffer = copy.deepcopy(m._map)
    for x in range(1,COLNO-1):
        for y in range(1,ROWNO-1):
            count = m.count_adjacent(x, y, [terr.ROOM], 0)
            if count < 3:
                backup_buffer[x][y] = terr.STONE
            elif count > 4:
                backup_buffer[x][y] = terr.ROOM

    m._map = backup_buffer

# identical to nethack's pass_two: cells with exactly 5 neighbors die
def nethack_pass_two(m):
    backup_buffer = copy.deepcopy(m._map)
    for x in range(1,COLNO-1):
        for y in range(1,ROWNO-1):
            count = m.count_adjacent(x, y, [terr.ROOM], 0)
            if count == 5:
                backup_buffer[x][y] = terr.STONE

    m._map = backup_buffer

# identical to nethack's pass_three: cells with less than 3 neighbors die
def nethack_pass_three(m):
    backup_buffer = copy.deepcopy(m._map)
    for x in range(1,COLNO-1):
        for y in range(1,ROWNO-1):
            count = m.count_adjacent(x, y, [terr.ROOM], 0)
            if count < 3:
                backup_buffer[x][y] = terr.STONE

    m._map = backup_buffer

# flood fill to find small rooms; return IrregularRoom structure
def init_irreg_room(m, x0, y0):
    ir = IrregularRoom()
    upnext = [(x0, y0)]
    while len(upnext) > 0:
        x, y = upnext.pop()
        ir.coords.append((x, y))
        for xx in range(x-1, x+2):
            for yy in range(y-1, y+2):
                if isok(xx, yy) and m[xx][yy] == terr.ROOM and (xx, yy) not in ir.coords and (xx, yy) not in upnext:
                    upnext.append((xx, yy))
    return ir

# Not currently _exactly_ the way nethack does it. But close. Should probably
# make it an exact reimplementation before folding it into the core generator.
# Doesn't check foreground or background, for one.
def nethack_dig_corridor(m, sx, sy, tx, ty):
    # weird logic, but this is how nethack does it...
    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif ty > sy:
        dy = 1
    elif tx < sx:
        dx = -1
    else:
        dy = -1
    xx = sx - dx
    yy = sy - dy
    while xx != tx or yy != ty:
        xx += dx
        yy += dy
        m[xx][yy] = terr.ROOM
        dix = abs(xx - tx)
        diy = abs(yy - ty)
        # maybe move at a tangent (but still closer) rather than take the most direct route
        if dix > diy and diy != 0 and rn2(dix-diy) == 0:
            dix = 0
        elif diy > dix and dix != 0 and rn2(diy-dix) == 0:
            diy = 0
        # if more than a certain distance from a point, take the most direct route towards it
        if dy != 0 and dix > diy:
            # omitting conditionals here that check for btyp/ftyp
            dy = 0
            dx = -1 if xx > tx else 1
        elif dx != 0 and diy > dix:
            dx = 0
            dy = -1 if yy > ty else 1

def create_irreg_rooms(m):
    irreg_rooms = []
    for x in range(COLNO):
        for y in range(ROWNO):
            if m[x][y] == terr.ROOM:
                should_add_room = True
                for ir in irreg_rooms:
                    if (x, y) in ir.coords:
                        should_add_room = False
                        break
                if should_add_room:
                    ir = init_irreg_room(m, x, y)
                    # remove tiny rooms
                    if ir.size() < 4:
                        for x, y in ir.coords:
                            m[x][y] = terr.STONE
                    else:
                        irreg_rooms.append(ir)
    return irreg_rooms

# Ensure the entire level is connected by digging corridors between all rooms.
def join_rooms(m, irreg_rooms):
    r1 = 0
    r2 = 1
    while r2 < len(irreg_rooms):
        ir1 = irreg_rooms[r1]
        ir2 = irreg_rooms[r2]
        sx, sy = ir1.somexy()
        tx, ty = ir2.somexy()
        nethack_dig_corridor(m, sx, sy, tx, ty)
        if ir2.lx() > ir1.hx() or ((ir2.ly() > ir1.hy() or ir2.hy() < ir1.ly()) and rn2(3) == 0):
            r1 = r2
        r2 += 1

# intended to be equivalent to nethack's entire mkmap(), except that it doesn't wallify.
# The number of times it calls pass_* can be changed via pass_iters. By
# default, it uses the values of N_P1_ITER, etc, from nethack.
def nethack_mkmap(m, pass_iters=[1,1,2]):
    m.nethack_init_map(terr.ROOM, 0.4)
    for x in range(pass_iters[0]):
        nethack_pass_one(m)
    for x in range(pass_iters[1]):
        nethack_pass_two(m)
    for x in range(pass_iters[2]):
        nethack_pass_three(m)
    nethack_pass_three(m)
    irreg_rooms = create_irreg_rooms(m)
    join_rooms(m, irreg_rooms)
