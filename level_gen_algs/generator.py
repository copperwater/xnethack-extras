import math
import colorama
import random
from enum import Enum
from colorama import Fore
import sys

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

    def count_adjacent(self, x, y, func, diag):
        return len(self.matching_adjacent(x, y, func, diag))

    def matching_adjacent(self, x, y, func, diag):
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

    #
    # TODO: diagonal support, whenever it's needed.


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

    def wallify(self):
        for y in range(ROWNO):
            for x in range(COLNO):
                if self._map[x][y] == terrain.STONE and self.count_adjacent(x, y, [terrain.ROOM], 0):
                    self._map[x][y] = terrain.WALL

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

    # Do a flood fill from a start point, using the function shouldAdd to
    # determine what should be added. Return the final list of coordinates.
    def floodfill(self, x0, y0, doDiag, shouldAdd):
        upnext = [(x0, y0)]
        out = []
        while len(upnext) > 0:
            x, y = upnext.pop()
            out.append((x,y))
            for xx in range(x-1, x+2):
                for yy in range(y-1, y+2):
                    if not isok(xx, yy):
                        continue
                    if xx == x and yy == y:
                        continue
                    if not doDiag and (abs(x - xx) + abs(y - yy)) != 1:
                        continue
                    if not shouldAdd(xx, yy):
                        continue
                    if (xx, yy) in out or (xx, yy) in upnext:
                        continue
                    upnext.append((xx, yy))
        return out

    # Randomly convert the exact fraction of map squares into terr. Will not
    # choose squares next to the edges. Identical to nethack's algorithm.
    def nethack_init_map(self, terr, fraction):
        nsquares = (ROWNO-2) * (COLNO-2) * fraction
        count = 0
        while count < nsquares:
            x = rn2(COLNO-2)+1
            y = rn2(ROWNO-2)+1
            if self[x][y] != terr:
                count += 1
                self[x][y] = terr

    def print_row(self, y, to=sys.stdout, border=''):
        if border == 'numeric':
            to.write(str(y % 10))
        elif border != '':
            to.write(border)
        for x in range(COLNO):
            to.write(self.syms[self._map[x][y]])

    def print_border_line(self, to, border):
        if border == 'numeric':
            to.write(' ')
            for x in range(COLNO):
                to.write(str(x % 10))
            to.write('\n')
        elif border != '':
            for x in range(COLNO):
                to.write(border)
            to.write('\n')

    def printmap(self, to=sys.stdout, border=''):
        self.fix_wall_spines()
        self.print_border_line(to, border)

        for y in range(ROWNO):
            self.print_row(y, to, border)
            to.write('\n')

    def __getitem__(self, x):
        return self._map[x]

    def __setitem__(self, x):
        return self._map[x]


def get_line(start, end):
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end

    >>> points1 = get_line((0, 0), (3, 4))
    >>> points2 = get_line((3, 4), (0, 0))
    >>> assert(set(points1) == set(points2))
    >>> print points1
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
    >>> print points2
    [(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = start.x, start.y
    x2, y2 = end.x, end.y
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points

def rn2(x):
    return random.randint(0, x-1)
def d(x):
    return random.randint(1, x)
def rz2(x):
    return random.randint(0, x*2+1) - x

class Coord(object):
    __slots__ = 'x', 'y'

    @classmethod
    def of(cls, coord):
        if isinstance(coord, Coord):
            return Coord(coord.x, coord.y)
        elif hasattr(coord, '__getitem__'):
            return Coord(coord[0], coord[1])

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __getitem__(self, key):
        return self.x if key == 0 else self.y

    def distSq(self, o):
        dx = self.x - o.x
        dy = self.y - o.y
        return dx*dx + dy*dy

    def dist(self, o):
        return math.sqrt(self.distSq(o))

    def length(self):
        return math.sqrt(self.x*self.x + self.y*self.y)

    def __add__(self, o):
        return Coord(self.x + o.x, self.y + o.y)

    def __sub__(self, o):
        return Coord(self.x - o.x, self.y - o.y)

    def __mul__(self, by):
        return Coord(self.x * by, self.y * by)

    def __truediv__(self, by):
        return Coord(self.x / by, self.y / by)

    def __floordiv__(self, by):
        return Coord(self.x // by, self.y // by)

    def __str__(self):
        return '(%.1f,%.1f)' % (self.x, self.y)

    def __round__(self):
        return Coord(round(self.x), round(self.y))

    def normalized(self):
        if self.length() == 0:
            return Coord.of(self)
        return Coord(self.x / self.length(), self.y / self.length())


class Edge(object):
    __slots = 'begin', 'end'

    def mid_point(self):
        length = self.end - self.begin
        return self.begin + (length//2)

    def __init__(self, begin, end):
        self.begin = begin
        self.end = end

    def split(self, at = None):
        if not at:
            at = self.mid_point()
        return (Edge(self.begin, at), Edge(at, self.end))

    def perpendicular(self):
        slope = self.end - self.begin
        return Coord(slope.y, slope.x).normalized()

    def length(self):
        return self.begin.dist(self.end)


class Path(object):
    __slots__ = 'edges', 'last'

    def __init__(self):
        self.edges = []
        self.last = None

    def append(self, c):
        if self.last:
            self.edges.append(Edge(self.last, c))
        self.last = c

    def subdivide_and_perturb(self):
        p = Path()
        for e in self.edges:
            cross = round(e.perpendicular() * rz2(e.length() // 8))
            s = e.split()
            s[0].end += cross
            s[1].begin += cross
            p.edges.append(s[0])
            p.edges.append(s[1])
#
        return p

