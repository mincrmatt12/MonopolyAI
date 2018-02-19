import collections

import pygame
import pygame.freetype
import threading
import queue
import squares
import math
import functools

pygame.init()
q = queue.Queue()

playercount = int(input("players? "))
money = 1500
pos = 0
others_pos = [0] * playercount
jail = 0
others_jail = [0] * playercount
dcount = 0
others_dcount = [0] * playercount


class DisplayObj(object):
    def __init__(self, q: queue.Queue):
        super().__init__()

        self.prints = []
        self.prompts = []
        self.window = pygame.display.set_mode([750, 750])  # type: pygame.Surface
        self.q = q
        self.bg = pygame.image.load("board.jpg")
        self.input_state = 0
        self.result = queue.Queue()
        self.fnt = pygame.freetype.Font(None)
        self.temp_roll = 0
        self.input_number = 0
        self.input_payload = None

        self.menu = Menu(self.window, collections.OrderedDict((
            ("Exit", exit),
            ("Edit player", collections.OrderedDict((
                ("Edit properties", functools.partial(self.edit_player, 0)),
                ("Edit houses", functools.partial(self.edit_player, 1)),
                ("Edit position", functools.partial(self.edit_player, 2)),
                ("Edit jail", functools.partial(self.edit_player, 3))
            ))),
            ("Edit AI", collections.OrderedDict((
                ("Edit money", functools.partial(self.edit_ai, 0)),
                ("Edit properties", functools.partial(self.edit_ai, 1)),
                ("Edit houses", functools.partial(self.edit_ai, 2)),
                ("Edit position", functools.partial(self.edit_ai, 3)),
                ("Edit jail", functools.partial(self.edit_ai, 4))
            ))),
            ("Skip Turn", lambda: None)
        )), self.fnt)

    def draw_playboard(self):
        self.window.fill((255, 255, 255))
        self.window.blit(self.bg, [0, 0])
        crowd = [0] * 40
        square = squares.squares[pos]
        x, y = square[squares.S_X:]
        y += crowd[square[squares.POS]] * 25
        pygame.draw.circle(self.window, (240, 20, 20), (x, y), 10)
        crowd[square[squares.POS]] += 1
        for player in range(playercount):
            square = squares.squares[others_pos[player]]
            x, y = square[squares.S_X:]
            x += crowd[square[squares.POS]] * 7
            pygame.draw.circle(self.window, (10 * player, 10 * player, 10 * player), (x, y), 10)
            crowd[square[squares.POS]] += 1

        self.fnt.size = 12
        for square in squares.squares:
            if squares.development[square[0]] > 1:
                houses = squares.development[square[0]] - 1
                x, y = square[squares.S_X:]
                x -= 20
                self.fnt.render_to(self.window, (x, y), "H" + str(houses), fgcolor=(10, 10, 10), bgcolor=(255, 255, 255, 200))
            x, y = square[squares.S_X:]
            y -= 20
            self.fnt.render_to(self.window, (x, y), str(square[0]), fgcolor=(10, 10, 10),
                               bgcolor=(255, 255, 255, 200))
            y += 40
            if squares.bought[square[0]] == 0:
                self.window.fill((50, 200, 50), (x-15, y-4, 30, 7))

    def draw_money(self):
        self.fnt.size = 14
        aistr = f'### Monopoly AI ###'
        moneystr = f'!!! Currently got $M{money} !!!'
        strs = [aistr, moneystr] + self.prints + self.prompts
        ticker = 275
        for str_ in strs:
            surf, rect = self.fnt.render(str_, fgcolor=(10, 10, 10) if str_ not in self.prompts else (100, 100, 255),
                                         bgcolor=(255, 255, 255, 230))
            x, y = 375 - (rect.width / 2), ticker - (rect.height / 2)
            ticker += rect.height + 5
            self.window.blit(surf, (x, y))

    def prompt_input(self):
        if self.input_state == 1:
            self.prompts = ["Input roll"]
            if self.temp_roll != 0:
                self.prompts.append(f"First roll ok, got {self.temp_roll}")
        elif self.input_state == 2:
            self.prompts = ["Please choose", self.input_payload[0]]
        elif self.input_state == 3:
            self.prompts = [self.input_payload[0], f"> {self.input_number}"]
        elif self.input_state == 4:
            self.prompts = [self.input_payload[0], "Click the square to choose it"]
        else:
            self.prompts = []

    def print(self, str_):
        self.q.put((1, str_, None))

    def roll(self):
        while self.input_state != 0:
            pass
        self.q.put((0, 1, None))
        res = self.result.get()
        if res is None: return self.roll()
        return res

    def choice(self, prompt, maxnum):
        while self.input_state != 0:
            pass
        self.q.put((0, 2, (prompt, maxnum)))
        res = self.result.get()
        if res is None: return self.choice(prompt, maxnum)
        return res

    def number(self, prompt):
        while self.input_state != 0:
            pass
        self.q.put((0, 3, (prompt,)))
        res = self.result.get()
        if res is None: return self.number(prompt)
        return res

    def square(self, prompt):
        while self.input_state != 0:
            pass
        self.q.put((0, 4, (prompt,)))
        res = self.result.get()
        if res is None: return self.square(prompt)
        return res

    def run(self):
        while True:
            if not self.q.empty():
                r, d, asdf = q.get_nowait()
                if r == 0:
                    if self.input_state != 0:
                        q.put((r, d, asdf))
                    self.input_state = d
                    self.input_payload = asdf
                else:
                    self.prints.append(str(d))
                    if len(self.prints) > 8:
                        del self.prints[0]
            self.draw_playboard()
            self.draw_money()
            self.prompt_input()
            if self.menu.up:
                self.menu.display()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                elif self.menu.blocking:
                    self.menu.input(event)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F12:
                        #self.result.put(None)
                        #self.menu.up_()
                        continue
                    if self.input_state == 1:
                        k = pygame.key.name(event.key)
                        try:
                            k = int(k)
                            if k not in range(1, 7):
                                raise ValueError
                            if self.temp_roll == 0:
                                self.temp_roll = k
                            else:
                                self.result.put((k + self.temp_roll, k == self.temp_roll))
                                self.print(f"Got roll {k + self.temp_roll}")
                                self.temp_roll = 0
                                self.input_state = 0
                        except ValueError:
                            pass
                    elif self.input_state == 2:
                        k = pygame.key.name(event.key)
                        try:
                            k = int(k)
                            if k not in range(self.input_payload[1] + 1):
                                raise ValueError
                            self.result.put(k)
                            self.input_state = 0
                        except ValueError:
                            pass
                    elif self.input_state == 3:
                        k = pygame.key.name(event.key)
                        try:
                            k = int(k)
                            pos = len(str(self.input_number))
                            if self.input_number == 0:
                                pos = 0
                            self.input_number *= 10 ** pos
                            self.input_number += k
                        except ValueError:
                            if event.key == pygame.K_RETURN:
                                self.result.put(self.input_number)
                                self.input_number = 0
                                self.input_state = 0
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_state == 4:
                        d = []
                        x0, y0 = event.pos
                        for square in squares.squares:
                            x, y = square[squares.S_X:]
                            d.append(math.sqrt((x0 - x) ** 2 + (y0 - y) ** 2))
                        self.result.put(d.index(min(d)))
                        self.input_state = 0
                        self.print(f"Using square {d.index(min(d))}")

            pygame.display.flip()

    def edit_player(self, param):
        if param == 2:
            others_pos[self.number("Which player to modify?")] = self.square("Where to put them?")

    def edit_ai(self, param):
        pass


class Menu:
    def __init__(self, window, tree: collections.OrderedDict, fnt):
        self.up = False
        self.blocking = False
        self.tree = tree
        self.selection = self.tree
        self.window = window
        self.fnt = fnt

    def up_(self):
        self.up = True
        self.blocking = True

    def display(self):
        pygame.draw.rect(self.window, (255, 255, 255, 190), (0, 0, 750, 750))
        y = 0
        self.fnt.size = 14
        for j, i in enumerate(self.selection):
            surf, rect = self.fnt.render(f"{j}: {i}", fgcolor=(10, 10, 10))
            x = 0
            self.window.blit(surf, (x, y))
            y += rect.height + 5

    def input(self, evt):
        if evt.type == pygame.KEYDOWN:
            try:
                k = int(pygame.key.name(evt.key))
                if 0 <= k < len(self.selection):
                    select = self.selection[tuple(self.selection.keys())[k]]
                    if type(select) is not collections.OrderedDict:
                        self.up = False

                        def cb():
                            select()
                            self.blocking = False
                            self.selection = self.tree
                        thread = threading.Thread(target=cb)
                        thread.start()
                    else:
                        self.selection = select

            except ValueError:
                return


display = DisplayObj(q)


class Bankrupt(Exception):
    pass


class SkipTurn(Exception):
    pass