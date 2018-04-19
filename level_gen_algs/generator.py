import colorama
import random
from enum import Enum
from colorama import Fore

ROWNO = 20
COLNO = 78  # actually 80 but there always seem to be buffers...

def isok(x, y):
    return (x >= 0 and y >= 0 and x < COLNO and y < ROWNO)

def onedge(x, y):
    return not (isok(x-1,y) and isok(x+1,y) and isok(x,y-1) and isok(x,y+1))

class terrain(Enum):
    STONE = 0
    WALL = 1
    VWALL = 2
    WATER = 3
    TREE = 4
    LAVA = 5
    ROOM = 6
    CORR = 7
    DOOR = 8
    USTAIR = 9
    DSTAIR = 10
    HILIGHT = 50

WALKABLE = [terrain.ROOM, terrain.CORR, terrain.DOOR, terrain.USTAIR, terrain.DSTAIR]

class dirs(Enum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3

class Map():
    syms = {
            terrain.STONE:   colorama.Style.RESET_ALL + ' ',
            terrain.WALL:    colorama.Style.RESET_ALL + '-',
            terrain.VWALL:   colorama.Style.RESET_ALL + '|',
            terrain.WATER:   Fore.BLUE + '~',
            terrain.TREE:    Fore.GREEN + '#',
            terrain.LAVA:    Fore.RED + '}',
            terrain.ROOM:    colorama.Style.RESET_ALL + '.',
            terrain.CORR:    colorama.Style.RESET_ALL + '#',
            terrain.DOOR:    Fore.YELLOW + '+',
            terrain.USTAIR:  colorama.Style.RESET_ALL + '<',
            terrain.DSTAIR:  colorama.Style.RESET_ALL + '>',
            terrain.HILIGHT: Fore.BLUE + colorama.Style.BRIGHT + '*',
            }

    def __init__(self):
        self._map = [[terrain.STONE for i in range(ROWNO)] for j in range(COLNO)]
        # hold a list of walls where a door could be placed
        self.doorwalls = set()

    def iswall(self, x, y):
        return (isok(x,y) and (self._map[x][y] == terrain.WALL or self._map[x][y] == terrain.VWALL))

    def iswallordoor(self, x, y):
        if not isok(x, y):
            return False
        if self.iswall(x, y):
            return True
        return (self._map[x][y] == terrain.DOOR)

    def adjacent_to(self, x, y, typ):
        if isok(x-1, y) and self._map[x-1][y] == typ:
            return (-1, 0)
        if isok(x+1, y) and self._map[x+1][y] == typ:
            return (1, 0)
        if isok(x, y-1) and self._map[x][y-1] == typ:
            return (0, -1)
        if isok(x, y+1) and self._map[x][y+1] == typ:
            return (0, 1)
        return None

    def count_adjacent(self, x, y, typlist, diag):
        # diag: 0 for either, -1 for orthogonal only, 1 for diagonal only
        c = 0
        for xx in range(x-1, x+2):
            for yy in range(y-1, y+2):
                if not (isok(xx, yy) and self._map[xx][yy] in typlist):
                    continue
                if diag > -1 and xx != x and yy != y:
                    # diagonals
                    c += 1
                if diag < 1 and ((xx == x) != (yy == y)): # XOR
                    # orthogonals
                    c += 1
        return c

    # Can we place something in the given rectangle?
    # If the entire rectangle is STONE, return True.
    def footprintok(self, lx, ly, hx, hy):
        if hx < lx:
            lx, hx = hx, lx
        if hy < ly:
            ly, hy = hy, ly
        strictStone = True
        if not isok(lx, ly) or not isok(hx, hy):
            return False
        for x in range(lx, hx+1):
            for y in range(ly, hy+1):
                if self._map[x][y] != terrain.STONE and (self._map[x][y] != terrain.WALL or strictStone):
                    return False
        return True

    def fix_wall_spines(self):
        for y in range(ROWNO):
            for x in range(COLNO):
                if self.iswall(x, y):
                    # vwalls only appear when a wall has more vertical neighbors than horizontal
                    vn = (1 if self.iswallordoor(x, y-1) else 0) + (1 if self.iswallordoor(x, y+1) else 0)
                    hn = (1 if self.iswallordoor(x-1, y) else 0) + (1 if self.iswallordoor(x+1, y) else 0)
                    if vn > hn and (self.count_adjacent(x, y, WALKABLE, 0) >= 2 or
                                    self.count_adjacent(x, y, [terrain.ROOM, terrain.DOOR], -1) >= 1):
                        self._map[x][y] = terrain.VWALL
                    else:
                        self._map[x][y] = terrain.WALL

    # Is the given location a suitable spot for a door?
    def valid_door_pos(self, x, y):
        if not isok(x, y) or onedge(x, y):
            # can't put a door on the edge
            return False
        if self._map[x][y] != terrain.WALL:
            return False
        if self.adjacent_to(x, y, terrain.DOOR) is not None:
            return False
        if self.adjacent_to(x, y, terrain.ROOM) is None:
            return False

        rmx, rmy = self.adjacent_to(x, y, terrain.ROOM)
        if rmx != 0 and not (self.iswall(x, y-1) and self.iswall(x, y+1)):
            return False
        if rmy != 0 and not (self.iswall(x-1, y) and self.iswall(x+1, y)):
            return False
        # everything seems good
        return True


    # Add any valid walls in the region that don't appear in the doorwalls set to it.
    def add_doorwalls(self, x1, y1, x2, y2, isCorridor):
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        for x in range(x1, x2+1):
            for y in range(y1, y2+1):
                if self.valid_door_pos(x, y):
                    self.doorwalls.add((x, y, isCorridor))


    def farthestfrom(self, ix, iy):
        visited = set()
        # TODO: unfinished


    def random_doorwall(self):
        # assume it's going to be used
        return random.sample(self.doorwalls, 1)


    def printmap(self):
        self.fix_wall_spines()
        for y in range(ROWNO):
            for x in range(COLNO):
                print(self.syms[self._map[x][y]], end=('\n' if x == COLNO-1 else ''), sep='')

    def __getitem__(self, x):
        return self._map[x]

    def __setitem__(self, x):
        return self._map[x]


