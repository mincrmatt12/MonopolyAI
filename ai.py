import time

import display
import risk
import squares
from display import playercount, money, pos, others_pos, jail, others_jail, others_dcount, dcount
import threading


def otherturn(player_n, roll=-1):
    display.display.print(f"player {player_n}'s turn")
    if roll:
        otherroll, gotdouble = display.display.roll()
        display.others_pos[player_n] += otherroll
        display.others_pos[player_n] %= 40
    else:
        otherroll = roll
        gotdouble = False

    if display.others_jail[player_n] > 1:
        if display.display.choice("Out of jail yet? 1 - yes 0 - no", 1) == 1:
            display.others_jail[player_n] = 0
            otherturn(player_n)

    display.display.print(f"currently on {squares.squares[others_pos[player_n]][squares.NAME]}.")
    pos = display.others_pos[player_n]
    if bool(int(squares.squares[pos][squares.IPROP])) and squares.bought[pos] == -1:
        result = display.display.choice("buyable square, who ended up buying it? ", display.playercount-1)
        squares.bought[pos] = result + 1
        squares.after_buy(result, pos)
    elif bool(int(squares.squares[pos][squares.IPROP])) and squares.bought[pos] == 0:
        rent = risk.rent(pos, otherroll, other=True)
        display.display.print(f"giving {rent} to the AI")
        display.money += rent
    elif bool(int(squares.squares[pos][squares.ICOMCHEST])) or bool(int(squares.squares[pos][squares.ICHANCE])):
        loc = display.display.choice("landed on chance/community chest, did they move anywhere (1 = yes, 0 = no)? ", 1)
        if loc == 1:
            display.others_pos[player_n] = display.display.square("where did they go? ")
            otherturn(player_n, otherroll)
            return

    if otherroll % 2 == 0:
        if gotdouble:
            if display.others_dcount[player_n] == 2:
                display.others_jail[player_n] = 1
                display.others_pos[player_n] = 10
                display.others_dcount[player_n] = 0
            display.others_dcount[player_n] += 1
            otherturn(player_n)
            return
        else:
            display.others_dcount[player_n] = 0
    else:
        display.others_dcount[player_n] = 0

    skip = True
    for i in squares.properties(player_n + 1):
        if squares.development[i[0]] == 6: continue
        if squares.development[i[0]] >= 1:
            display.display.print(f"player can develop {i[squares.NAME]} with id {i[0]}")
    else:
        skip = False
    if skip:
        houses = input("did they buy any houses (count:place)? ")
        if houses != "":
            for i in houses.split(","):
                t = [int(x) for x in i.split(":")]
                squares.development[t[1]] += t[0]

    display.money += display.display.number("did the ai get any money, and if so how much? ")


def myturn(roll=-1):
    #global pos
    if display.jail > 0:
        display.display.print('in jail... oh well')
        display.jail += 1
        _, doubles = display.display.roll()
        if doubles:
            display.jail = 0
            display.pos = 10
            display.display.print("out of jail via luck")
            myturn()
            return
        if display.jail == 3:
            display.display.print("out of jail via payment of 50")
            display.money -= 50
            display.pos = 10
        return
    if roll == -1:
        advance, gotdouble = display.display.roll()
        display.pos += advance
        lastpos = display.pos
        display.pos %= 40
    else:
        lastpos = display.pos
        advance = roll
        gotdouble = False

    if display.pos < lastpos:
        display.money += 200

    if display.pos == 30:
        display.display.print(f"i'm on {squares.squares[display.pos][squares.NAME]}!")
        display.jail = 1
        display.pos = 10
        return

    display.display.print(f"i'm on {squares.squares[display.pos][squares.NAME]}!")

    current_risk = risk.assess_risk(display.pos)
    display.display.print(f"current risk is {current_risk}")

    if bool(int(squares.squares[display.pos][squares.IPROP])) and squares.bought[display.pos] == -1:
        desire = risk.desire(display.pos, display.money)
        display.display.print(f"my desire to buy is {desire}")

        if display.money - current_risk < squares.squares[display.pos][squares.COST]:
            desire *= 0.6
        if desire > 0.5:
            display.display.print("!!! buying now !!!")
            squares.bought[display.pos] = 0
            display.money -= squares.squares[display.pos][squares.COST]
            squares.after_buy(0, display.pos)
        else:
            squares.bought[display.pos] = display.display.choice("!!! bidding war, which player won !!! ? ", display.playercount-1)
            squares.after_buy(squares.bought[display.pos], display.pos)
    elif bool(int(squares.squares[display.pos][squares.IPROP])) and squares.bought[display.pos] != 0:
        display.display.print(f"give {risk.rent(display.pos, advance)} to {squares.bought[display.pos]}")
        display.money -= risk.rent(display.pos, advance)
    elif bool(int(squares.squares[display.pos][squares.ICHANCE])) or bool(int(squares.squares[
                                                                                  display.pos][squares.ICOMCHEST])):
        action = display.display.choice("what happened, 0=money, 1=newpos, 2=jail? ", 2)
        if action == 0:
            display.money += display.display.number("how much?")
        elif action == 1:
            display.pos = display.display.square("where to? ")
            myturn(advance)
        else:
            display.jail = 1
            display.pos = 10
            display.display.print("crap")
            return

    display.money -= int(squares.squares[display.pos][squares.FINE])

    if advance % 2 == 0:
        if gotdouble:
            if display.dcount == 2:
                display.dcount = 0
                display.jail = 1
                display.pos = 10
                return
            display.dcount += 1
            myturn()
            return
        else:
            display.dcount = 0
    else:
        display.dcount = 0

    for property_ in squares.properties(0):
        if squares.development[property_[0]] == 6: continue
        if squares.development[property_[0]] >= 1:
            newrent = property_[(
                squares.RENTSET,
                squares.RENT1H,
                squares.RENT2H,
                squares.RENT3H,
                squares.RENT4H,
                squares.RENTHOT
            )[squares.development[property_[0]]]]
            lrent = property_[(
                squares.RENTSET,
                squares.RENT1H,
                squares.RENT2H,
                squares.RENT3H,
                squares.RENT4H,
                squares.RENTHOT
            )[squares.development[property_[0]] - 1]]
            incentive = risk.hdesire(int(property_[squares.HCOST]), display.money, newrent, lrent,
                                     property_[squares.PGROUP])
            display.display.print(f"my desire to improve {property_[squares.NAME]} is {incentive}")
            if squares.min_house(property_[squares.PGROUP]) - 1 == squares.development[property_[0]]:
                if incentive > 0.75:
                    if display.money - int(property_[squares.HCOST]) > current_risk:
                        display.display.print(f"!!! buy house on {property_[squares.NAME]}. !!!")
                        squares.development[property_[0]] += 1
                        display.money -= int(property_[squares.HCOST])


def run_ai():
    while True:
        myturn()
        for other in range(playercount):
            try:
                otherturn(other)
            except display.Bankrupt:
                display.display.print(f"##### OH CRAP! Player {other} is no more! #####")
            except display.SkipTurn:
                pass
            display.display.print("you have 2 seconds to do menu stuff")
            time.sleep(1)
            display.display.print("you have 1 seconds to do menu stuff")
            time.sleep(1)


ai_t = threading.Thread(target=run_ai)
ai_t.start()
display.display.run()
