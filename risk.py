import squares

dice = {
    2: 0.027,
    3: 0.056,
    4: 0.08533,
    5: 0.1111,
    6: 0.1389,
    7: 0.1667,
    8: 0.1389,
    9: 0.1111,
    10: 0.08533,
    11: 0.056,
    12: 0.027
}


def rent(pos, dice, other=False):
    square = squares.squares[pos]
    if squares.bought[pos] in ((-1, 0) if not other else (-1,)):
        return 0
    if bool(int(square[squares.IUTIL])):
        if squares.bought[12] == squares.bought[28]:
            return 10 * dice
        return dice * 4
    elif bool(int(square[squares.IRAIL])):
        owner = squares.bought[pos]
        cowned = sum(
            (1 if (x[squares.IRAIL] and squares.bought[n] == owner) else 0) for n, x in enumerate(squares.squares)
        )
        return (25, 50, 100, 100)[cowned - 1]
    else:
        cowned = sum(int(x[squares.PGROUP] == square[squares.PGROUP]) for x in squares.properties(squares.bought[pos]))
        if cowned < squares.m_count[square[squares.PGROUP]]:
            return square[squares.RENT]
        else:
            return square[(
                squares.RENTSET,
                squares.RENT1H,
                squares.RENT2H,
                squares.RENT3H,
                squares.RENT4H,
                squares.RENTHOT
            )[squares.development[pos]-1]]


def assess_risk(pos):
    reasonable_risk = 20
    for i in dice:
        poss_pos = (pos + i) % 40
        square = squares.squares[poss_pos]
        reasonable_risk += int(square[18]) * dice[i] * 2
        reasonable_risk += (rent(poss_pos, i) * dice[i] * 2) if bool(int(square[squares.IPROP])) else 0
        if bool(int(square[squares.ICHANCE])):
            reasonable_risk += 50 * dice[i] * 3.5
    return reasonable_risk


def desire(pos, money):
    if not squares.squares[pos][squares.IPROP]:
        return 0
    if int(squares.squares[pos][squares.COST]) > money:
        return 0

    money_burden = ((money - squares.squares[pos][squares.COST] - 50) / money)
    rent_incentive = (squares.squares[pos][squares.RENTSET] / 22)
    owners = squares.owners(squares.squares[pos][squares.PGROUP])
    owner_incentive = 0
    if len(owners) == 2 and 0 in owners:
        owner_incentive = 2.5
    elif len(owners) == 1 and owners[0] == -1:
        owner_incentive = 2
    else:
        owner_incentive = 0.8
    add = 0
    if money > 1500:
        add = 0.5
    if len(owners) == 2 and 0 in owners:
        add += 0.6
    return (rent_incentive * money_burden * owner_incentive) + add


def hdesire(hcost, money, nrent, lrent, g):
    money_burden = ((money - hcost - 50) / money) - 0.2
    rent_incentive = nrent / lrent
    set_size = squares.m_count[g] / 2
    add = 0
    if money > 1500:
        add = 0.75
    return (money_burden * rent_incentive * set_size) + add