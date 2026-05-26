#!/usr/bin/python

# Given a des map, print all coordinates of the given mapchar.
# This is useful when marking out points of interest on a map to insert into a
# Lua table.

desmap = '''
                        }}}}}}}                 B                   B
                        }}}}}}              .... ...            .... .
                        }}}}}}      .......B        .. ........B     .
                        }}}}}      B        .         B       .      .
                        }}}}     ....        .. ...... ...    .      .
                        B }}    .  . ..        B          ............B
                         ..... .   .   .     ..               B        .
                              B    .    . ...                          .
                               .   .     B                              .
                        }}      .  .    . .                              .
                        }}}     .  .  ..   .                              B
                        }}}}     . . .      .                            .
                        }}}}      ...        .                          .
                        }}}}}      B          .                         .
                        }}}}}   ... ..         B                   ....B
                         } }....  .   ..    ......           .....B    .
                        }}}B      .     . ..   .  ... ......B      .   .
                        }}  ..   .       B     .     B      .       .  .
                        B     .  .   .... ..   .   .. ..... .        . .
                         ....... ....       .......        ............B
                                B              B            B
'''
mapchar = 'B'

y = 0
for line in desmap.splitlines():
    if len(line) < 1: # ignore initial line after '''
        continue
    indices = [i for i, letter in enumerate(line) if letter == mapchar]
    for x in indices:
        print(f'{{{x:02},{y:02}}}')
    y += 1

