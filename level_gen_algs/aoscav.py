import generator
from generator import Map
from generator import terrain as terr
from generator import ROWNO, COLNO
from mkmap import nethack_mkmap

# Caverns+rooms generator algorithm.
# Intended for Gehennom.
# Designed to make a cavernous level but which has rooms organically attached
# to the caverns, sometimes inside it.
#
# Algorithm works by first using nethack's regular cavern generation algorithm: run a modified
# Conway's Game of Life on a grid on which squares are either rock or floor randomly a couple times.

m = Map()

nethack_mkmap(m)
m.wallify()
m.printmap()
