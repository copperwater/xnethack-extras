import sys
import random

if len(sys.argv) != 3:
    print('wrong # of arguments')
    sys.exit(1)

scrolls = []
labels = []
maxscrolllen = 0

with open(sys.argv[1]) as f:
    for scroll in f:
        scrolls.append(scroll[:-1])
        maxscrolllen = max(maxscrolllen,len(scroll))

with open(sys.argv[2]) as f:
    for label in f:
        labels.append(label[:-1])

# insert random blank strings into scrolls until it matches the number of labels
excess = len(labels) - len(scrolls)

for i in range(excess):
    idx = random.randint(0,len(scrolls))
    scrolls.insert(idx, "");

# randomly bubble labels around a bit with a large trout
nbub = 600
for i in range(nbub):
    idx = random.randint(0,len(scrolls)-2)
    tmp = labels[idx]
    labels[idx] = labels[idx+1]
    labels[idx+1] = tmp

# print it all out
for i in range(len(labels)):
    print(scrolls[i].ljust(maxscrolllen), labels[i])
