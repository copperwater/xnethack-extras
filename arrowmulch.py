# Program that tries to plot the probability distribution of getting a certain
# number of uses out of a certain number of projectiles given a certain fixed
# probability of breakage.
#
# This is sort of obsolete as soon after writing this program I figured out the
# exact probability expression for a given number of starting projectiles n,
# breakage chance p, and total number of uses k (k >= n):
#  Prob[n, k, p] = (1-p)^(k-n) * p^(n) * (k-1 choose n-1)
#
# Eventually I intend to adapt this to use that expression so it can plot the
# probability curves for different p.

import random
import numpy as np
import matplotlib.pyplot as plt

ARROWS = 50

def trial(mulch):
    trials = 0
    arrows = ARROWS
    while arrows > 0:
        trials += 1
        x = random.uniform(0,1)
        if x < mulch:
            arrows -= 1

    return trials

# constant: 50 arrows
# independent variable: number of hits out of 50 arrows
# dependent variable: probability of 50 arrows getting exactly this many hits
# multiple line plots: different mulch rates

MAX = 15000
x = np.arange(0,MAX,1)
# mulch = [0.993, 2/3, 1/4, 0.12625, 0.0655, 0.0045]
mulch = [2/3, 1/4, 0.12625, 0.0655, 0.0045]
for m in mulch:
    data = [0]*MAX
    for i in range(1000):
        uses = trial(m)
        try:
            data[trial(m)] += 1
        except IndexError:
            print('Out of range! m=', m, 'uses =', uses)
    plt.plot(x, data)

plt.show()

