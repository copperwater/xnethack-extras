import generator
from generator import Map
from generator import Path, Edge, Coord, d, rz2, rn2
from generator import terrain as terr
from generator import dirs
from generator import ROWNO, COLNO
import random
import sys


def generate_canyon(style):
    m = Map()
    p = Path()

    cx = int(COLNO/2)
    cy = int(ROWNO/2)

    w_over4 = int(COLNO/4)
    h_over4 = int(ROWNO/4)

    if style == 'corner_ul':
        p.append(Coord(0, cy))
        p.append(Coord(cx, cy-h_over4))
        p.append(Coord(cx + w_over4, cy + int(cy/3)))
        p.append(Coord(cx, ROWNO-1))
    if style == 'corner_ur':
        p.append(Coord(COLNO-1, cy))
        p.append(Coord(cx, cy-h_over4))
        p.append(Coord(w_over4, cy + int(cy/3)))
        p.append(Coord(cx, ROWNO-1))
    if style == 'corner_ll':
        p.append(Coord(0, cy))
        p.append(Coord(cx, cy+h_over4))
        p.append(Coord(cx + w_over4, cy - int(cy/3)))
        p.append(Coord(cx, 0))
    if style == 'corner_lr':
        p.append(Coord(COLNO-1, cy))
        p.append(Coord(cx, cy+h_over4))
        p.append(Coord(w_over4, cy - int(cy/3)))
        p.append(Coord(cx, 0))
    elif style == 'horizontal' or style == 'T_up' or style == 'T_down':
        p.append(Coord(0, cy))
        p.append(Coord(w_over4, cy-int(cy/3)))
        p.append(Coord(cx + w_over4, cy + int(cy/3)))
        p.append(Coord(COLNO-1, cy))
    elif style == 'vertical':
        p.append(Coord(cx, 0))
        p.append(Coord(cx + w_over4, h_over4))
        p.append(Coord(cx - w_over4, cy))
        p.append(Coord(cx, ROWNO-1))

    subdivided = p.subdivide_and_perturb().subdivide_and_perturb()

    def draw_path(path):
        for k in path.edges:
            line = generator.get_line(k.begin, k.end)
            for c in line:
                if c[0] == 0 or c[0] == COLNO-1 or c[1] == 0 or c[1] == ROWNO-1:
                    width = 2
                else:
                    width = d(3) + 1
                cross = k.perpendicular() * width
                crossLine = generator.get_line(round(Coord.of(c) - cross), round(Coord.of(c) + cross))
                for cl in crossLine:
                    if generator.isok(cl[0], cl[1]):
                        m[cl[0]][cl[1]] = terr.ROOM

    draw_path(subdivided)

    if style == 'T_up':
        spur = Path()
        spur.append(Coord(cx,cy))
        spur.append(Coord(cx,0))

        spur = spur.subdivide_and_perturb()
        draw_path(spur)

    m.fix_wall_spines()
    return m

maps = []

with open('canyon.txt', 'w') as f:
    for map_type in sys.argv[1:]:
        if map_type == 'b':
            maps.append(Map())
        elif map_type == 'x':
            for y in range(ROWNO):
                for m in maps:
                    m.print_row(y, f, '~')
                f.write('\n')

            for m in maps:
                m.print_border_line(f, '~')
            f.write('\n')
            maps.clear()
        else:
            maps.append(generate_canyon(map_type))
