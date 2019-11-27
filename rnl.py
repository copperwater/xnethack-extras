# Short script to test average values of !rnl(4) being TRUE.

import random

def rnl(x, luck):
    R = random.randint(0, x-1)
    if luck == 0:
        return R

    if x <= 15:
        A = (luck + (1 if luck > 0 else -1)) // 3
    else:
        A = luck

    if A == 0:
        return R

    elif random.randint(1,37+abs(A)) == 1:
        return R

    R = R-A
    if R < 0:
        return 0
    elif R >= x:
        return x-1
    else:
        return R
