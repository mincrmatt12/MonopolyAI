squares = []
import csv

with open("board.tsv") as f:
    read = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    rows = list(read)[1:]
    for row in rows:
        squares.append(row)

for square in range(len(squares)):
    for n in range(21):
        if n == 1: continue
        squares[square][n] = int(squares[square][n])

bought = [-1 for n in squares]
development = [0 for n in squares]

POS = 0
NAME = 1
PGROUP = 2
COST = 3
MORTGAGE = 4
RENT = 5
RENTSET = 6
RENT1H = 7
RENT2H = 8
RENT3H = 9
RENT4H = 10
RENTHOT = 11
HCOST = 12
IPROP = 13
ICHANCE = 14
ICOMCHEST = 15
IRAIL = 16
IUTIL = 17
FINE = 18
S_X = 19
S_Y = 20

m_own = set(x[PGROUP] for x in squares)
m_count = list(sum(1 if x[PGROUP] == n else 0 for x in squares) for n in range(len(m_own)))


def properties(o):
    return [x for n, x in enumerate(squares) if bought[n] == o]


def owners(g):
    return list(set(bought[n] for n, x in enumerate(squares) if x[PGROUP] == g))


def min_house(g):
    mhouse = 0
    lastprop = -1
    add = True
    for p in squares:
        if p[PGROUP] != g: continue
        mhouse = max(mhouse, development[p[0]])
        if lastprop == -1:
            lastprop = development[p[0]]
        if lastprop != development[p[0]]:
            add = False
    return mhouse + int(add)


def after_buy(p, pos):
    if all(
            bought[n_[0]] == p for n_ in squares if
            n_[PGROUP] == squares[pos][PGROUP]
    ):
        for i in squares:
            if i[PGROUP] == squares[pos][PGROUP]:
                development[i[0]] = 1