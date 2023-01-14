import pygame
import os
import sys


def load_image(name, color_key=None):
    fullname = os.path.join('DATA', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class Game:
    def __init__(self, tp=1, time=10):
        self.time = time  # время выделенное под игрока (игрок1, игрок2)
        self.tp = tp  # вариация игры: 1 - против локального игрока, 2 - против ИИ

    def start(self):
        self.desk = Desk(self.time)
        self.run()

    def run(self):
        running = True
        is_grabbed = False
        grabbed = (0, 0)
        pos = (0, 0)
        self.is_under_attacks = [False, False]
        self.is_game_running = True
        while running:
            screen.fill((250, 188, 90, 98))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and self.is_game_running:
                    is_grabbed, grabbed, pos = self.mousebuttondown(event, is_grabbed)
                if event.type == pygame.MOUSEBUTTONUP and self.is_game_running:
                    self.mousebuttonup(is_grabbed, grabbed, event)
                    is_grabbed = False
                if is_grabbed and event.type == pygame.MOUSEMOTION and self.is_game_running:
                    np = event.pos
                    figures_desk[grabbed[1]][grabbed[0]].rect.x += np[0] - pos[0]
                    figures_desk[grabbed[1]][grabbed[0]].rect.y += np[1] - pos[1]
                    pos = np
            t = clock.tick(FPS) / 100000
            self.update(is_grabbed, grabbed, t)

    def check_mat(self):
        for i in (0, 1):
            if self.is_under_attacks[i] and self.desk.kings[i].possible_move == []:
                if not self.check_possible_solve_mat(i):
                    if i == 0:
                        self.end_table(2)
                    else:
                        self.end_table(1)

    def check_possible_solve_mat(self, nm):
        tp = "W" if nm == 0 else "D"
        for i in range(8):
            for j in range(8):
                if not (figures_desk[i][j] is None) and figures_desk[i][j].type[0] == tp:
                    elem = figures_desk[i][j]
                    elem.check_possible()
                    for move in elem.possible_move:
                        elem.pos = move[::-1]
                        tmp = figures_desk[move[1]][move[0]]
                        figures_desk[i][j], figures_desk[move[1]][move[0]] = None, elem
                        b = [self.desk.kings[0].is_under_attack(), self.desk.kings[1].is_under_attack()]
                        figures_desk[i][j], figures_desk[move[1]][move[0]] = elem, tmp
                        figures_desk[i][j].pos = i, j
                        if not b[nm]:
                            print(figures_desk[i][j].type, move)
                            return True
        return False

    def update(self, is_grabbed, grabbed, t):
        self.desk.draw_desk()
        if self.is_game_running:
            self.desk.draw_timer(t)
        if is_grabbed:
            figures_desk[grabbed[1]][grabbed[0]].check_possible()
            psmv = figures_desk[grabbed[1]][grabbed[0]].possible_move
            if figures_desk[grabbed[1]][grabbed[0]].type[1] == 'K':
                psmv += figures_desk[grabbed[1]][grabbed[0]].castling()
            for elem in psmv:
                pygame.draw.circle(screen, (0, 255, 0, 100),
                                   (elem[0] * 62.5 + 51.5, elem[1] * 62.5 + 51.5), 15, 5)
        figures.update()
        figures.draw(screen)
        self.time_check()
        self.check_mat()
        pygame.display.flip()

    def time_check(self):
        b = 0
        if self.desk.time[0] < 0:
            b = 2
        elif self.desk.time[1] < 0:
            b = 1
        if b:
            self.end_table(b)

    def end_table(self, pl):
        font = pygame.font.Font(None, 50)
        text = font.render(f"Player {pl} win!", 1, (100, 255, 100))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - text.get_height() // 2
        pygame.draw.rect(screen, (50, 130, 250), pygame.Rect(text_x - 20, text_y - 10, 250, 55), 0)
        pygame.draw.rect(screen, (30, 30, 30), pygame.Rect(text_x - 20, text_y - 10, 250, 55), 3)
        screen.blit(text, (text_x, text_y))
        self.is_game_running = False

    def mousebuttondown(self, event, is_grabbed):
        pos = event.pos
        grabbed = (int((event.pos[0] - 10) / 62.5), int((event.pos[1] - 10) / 62.5))
        if 10 <= event.pos[0] <= 510 and 10 <= event.pos[1] <= 510 and not is_grabbed:
            if figures_desk[grabbed[1]][grabbed[0]] is None:
                return is_grabbed, grabbed, pos
            if figures_desk[grabbed[1]][grabbed[0]].type[0] == "D" and self.desk.turn != 1 or \
                    figures_desk[grabbed[1]][grabbed[0]].type[0] == "W" and self.desk.turn != 0:
                return is_grabbed, grabbed, pos
            figures_desk[grabbed[1]][grabbed[0]].check_possible()
            is_grabbed = True
        return is_grabbed, grabbed, pos

    def mousebuttonup(self, is_grabbed, grabbed, event):
        if not is_grabbed:
            return
        pnt = (int((event.pos[0] - 10) / 62.5), int((event.pos[1] - 10) / 62.5))
        figures_desk[grabbed[1]][grabbed[0]].check_possible()
        if figures_desk[grabbed[1]][grabbed[0]].type[1] == 'K' and \
                pnt in figures_desk[grabbed[1]][grabbed[0]].castling():
            d = 1
            rook = (pnt[1], 0)
            if pnt[0] == 6:
                d = -1
                rook = (pnt[1], 7)
            figures_desk[grabbed[1]][grabbed[0]].pos = pnt[::-1]
            figures_desk[grabbed[1]][grabbed[0]].first = False
            figures_desk[grabbed[1]][grabbed[0]], figures_desk[pnt[1]][pnt[0]] = None, \
                                                                                 figures_desk[grabbed[1]][grabbed[0]]
            figures_desk[pnt[1]][pnt[0]].rect.x = pnt[0] * 62.5 + 20.25
            figures_desk[rook[0]][rook[1]].pos = (pnt[1], pnt[0] + d)
            figures_desk[rook[0]][rook[1]], figures_desk[pnt[1]][pnt[0] + d] = \
                None, figures_desk[rook[0]][rook[1]]
            figures_desk[pnt[1]][pnt[0] + d].rect.x = (pnt[0] + d) * 62.5 + 20.25

            self.desk.turn += 1
            self.desk.turn %= 2
        elif pnt not in figures_desk[grabbed[1]][grabbed[0]].possible_move:
            figures_desk[grabbed[1]][grabbed[0]].rect.x = grabbed[0] * 62.5 + 20.25
            figures_desk[grabbed[1]][grabbed[0]].rect.y = grabbed[1] * 62.5 + 20.25
        else:
            figures_desk[grabbed[1]][grabbed[0]].pos = pnt[::-1]
            tmp = figures_desk[pnt[1]][pnt[0]]
            figures_desk[grabbed[1]][grabbed[0]], figures_desk[pnt[1]][pnt[0]] = None, \
                                                                                 figures_desk[grabbed[1]][grabbed[0]]
            b = [self.desk.kings[0].is_under_attack(), self.desk.kings[1].is_under_attack()]
            if b[self.desk.turn]:
                figures_desk[grabbed[1]][grabbed[0]], figures_desk[pnt[1]][pnt[0]] = figures_desk[pnt[1]][pnt[0]], \
                                                                                     tmp
                figures_desk[grabbed[1]][grabbed[0]].pos = (grabbed[1], grabbed[0])
                figures_desk[grabbed[1]][grabbed[0]].rect.x = grabbed[0] * 62.5 + 20.25
                figures_desk[grabbed[1]][grabbed[0]].rect.y = grabbed[1] * 62.5 + 20.25
            else:
                if tmp is not None:
                    tmp.kill()
                    figures_desk[grabbed[1]][grabbed[0]] = None
                figures_desk[pnt[1]][pnt[0]].rect.x = pnt[0] * 62.5 + 20.25
                figures_desk[pnt[1]][pnt[0]].rect.y = pnt[1] * 62.5 + 20.25
                self.desk.turn += 1
                self.desk.turn %= 2
                self.is_under_attacks = [self.desk.kings[0].is_under_attack(), self.desk.kings[1].is_under_attack()]
                if figures_desk[pnt[1]][pnt[0]].type[1] in ["P", "K", "R"]:
                    figures_desk[pnt[1]][pnt[0]].first = False
                    if (pnt[1] == 0 or pnt[1] == 7) and figures_desk[pnt[1]][pnt[0]].type[1] == "P":
                        self.pawn_on_last_point(figures_desk[pnt[1]][pnt[0]])

    def pawn_on_last_point(self, pawn):
        t = pawn.type[0]
        is_choosed = False
        pygame.draw.rect(screen, (250, 188, 90, 98), pygame.Rect(100, 80, 330, 55))
        pygame.draw.rect(screen, "black", pygame.Rect(100, 80, 330, 55), 3)
        font = pygame.font.Font(None, 25)
        text = font.render(f"Выберите фигуру на замену пешке", 1, (250, 250, 250))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 5 - text.get_height() // 2
        screen.blit(text, (text_x, text_y))
        v = ['Q', 'B', 'R', 'H']
        c = 0
        arrow_r = [(width // 4 * 3, height // 8 * 5), (width // 4 * 3, height // 8 * 3), (width // 10 * 9, height // 2)]
        arrow_l = [(width // 4, height // 8 * 5), (width // 4, height // 8 * 3), (width // 10, height // 2)]
        pygame.draw.polygon(screen, 'red', arrow_r, 0)
        pygame.draw.polygon(screen, 'red', arrow_l, 0)
        pygame.draw.rect(screen, (250, 188, 90, 98), pygame.Rect((width // 4 + 30, height // 8 * 3 + 30),
                                                                 (width // 4 * 2 - 60, height // 8 * 2 - 60)), 0)
        accept_bt = [(width // 4 + 70, height // 8 * 4 + 50),
                     (width // 4 + 70 + width // 4 * 2 - 140, height // 8 * 4 + 50 + height // 8 * 2 - 100)]
        while not is_choosed:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if arrow_r[0][0] <= pos[0] <= arrow_r[-1][0] and arrow_r[1][1] <= pos[1] <= arrow_r[0][1]:
                        c += 1
                    elif arrow_l[0][0] >= pos[0] >= arrow_l[-1][0] and arrow_l[1][1] <= pos[1] <= arrow_l[0][1]:
                        c -= 1
                    elif accept_bt[0][0] <= pos[0] <= accept_bt[1][0] and accept_bt[0][1] <= pos[1] <= accept_bt[1][1]:
                        chose = t + v[c]
                        ps = pawn.pos
                        figures_desk[ps[0]][ps[1]].kill()
                        is_choosed = True
                        fg = None
                        if c == 0:
                            fg = Queen(ps, chose)
                        if c == 1:
                            fg = Bishop(ps, chose)
                        if c == 2:
                            fg = Rook(ps, chose)
                        if c == 3:
                            fg = Horse(ps, chose)
                        figures_desk[ps[0]][ps[1]] = fg

            c %= len(v)
            if c < 0:
                c = len(v) - 1
            pygame.draw.rect(screen, (250, 188, 90, 98), pygame.Rect((width // 4 + 30, height // 8 * 3 + 30),
                                                                     (width // 4 * 2 - 60, height // 8 * 2 - 60)), 0)
            pygame.draw.rect(screen, 'green', pygame.Rect((width // 4 + 70, height // 8 * 4 + 50),
                                                          (width // 4 * 2 - 140, height // 8 * 2 - 100)), 0)
            text = font.render(f"Выбрать", 1, (250, 250, 250))
            screen.blit(text, (width // 4 + 100, height // 8 * 4 + 60))
            screen.blit(load_image(f'{t}{v[c]}.png'), (width // 2 - 32, height // 2 - 32))
            pygame.display.flip()


class Desk:
    def __init__(self, time, color=((240, 240, 240), (110, 110, 110))):
        global desk, figures_desk
        self.kings = []
        with open('def_desk.txt', 'r') as file:
            desk = [file.readline().split(' ') for _ in range(8)]
        figures_desk = []
        for i in range(8):
            tmp = []
            for j in range(8):
                if desk[i][j].rstrip('\n') != '.':
                    if desk[i][j].rstrip('\n')[1] == "P":
                        tmp.append(Pawn((i, j), desk[i][j]))
                    elif desk[i][j].rstrip('\n')[1] == "H":
                        tmp.append(Horse((i, j), desk[i][j]))
                    elif desk[i][j].rstrip('\n')[1] == "R":
                        tmp.append(Rook((i, j), desk[i][j]))
                    elif desk[i][j].rstrip('\n')[1] == "B":
                        tmp.append(Bishop((i, j), desk[i][j]))
                    elif desk[i][j].rstrip('\n')[1] == "Q":
                        tmp.append(Queen((i, j), desk[i][j]))
                    else:
                        tmp.append(King((i, j), desk[i][j]))
                        self.kings.append(tmp[-1])
                else:
                    tmp.append(None)
            figures_desk.append(tmp)
        self.kings = self.kings[::-1]
        self.color = color  # цвет доски - кореж из двух цветов в формате rgb
        self.time = [time, time]
        self.turn = 0  # чей ход

    def draw_timer(self, t):
        font = pygame.font.Font(None, 20)
        tm = self.time[0]
        txt = "Player 1 - " + str(int(tm)) + ':' + str(int((tm % 1) * 100))
        text = font.render(txt, 1, self.color[1])
        screen.blit(text, (120, 5))
        tm = self.time[1]
        txt = "Player 2 - " + str(int(tm)) + ':' + str(int((tm % 1) * 100))
        text = font.render(txt, 1, self.color[1])
        screen.blit(text, (320, 5))
        self.time[self.turn] -= t
        if self.time[self.turn] % 1 > 0.6:
            self.time[self.turn] -= 0.4

    def draw_desk(self):
        color = self.color[0]
        for i in range(8):
            for j in range(9):
                if j != 8:
                    screen.fill(pygame.Color(color), pygame.Rect(62.5 * j + 20, 62.5 * i + 20, 63, 63))
                if color == self.color[0]:
                    color = self.color[1]
                else:
                    color = self.color[0]

        font = pygame.font.Font(None, 20)
        for i in range(8):
            text = font.render(str(i + 1), 1, self.color[1])
            screen.blit(text, (5, 520 - (i * 62.5 + 42.25)))
            text = font.render(chr(i + 65), 1, self.color[1])
            screen.blit(text, ((i * 62.5 + 42.25), 520))


class Figure(pygame.sprite.Sprite):
    def __init__(self, pos, type):
        super().__init__(figures)
        self.pos = pos
        self.type = type.strip('\n')
        self.image = self.load_image(self.type + '.png')
        self.rect = self.image.get_rect()
        self.rect.x = pos[1] * 62.5 + 20.25
        self.rect.y = pos[0] * 62.5 + 20.25
        self.possible_move = []
        self.abs_moves = []

    def load_image(self, name):
        fullname = os.path.join('DATA', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        return image


class Pawn(Figure):
    def __init__(self, *args):
        super().__init__(*args)
        self.first = True

    def check_possible(self):
        self.abs_moves.clear()
        self.possible_move.clear()
        tp = "W"
        dl = -1
        if self.type[0] == "D":
            tp = "D"
            dl = 1
        if 8 > self.pos[0] + dl >= 0:
            if figures_desk[self.pos[0] + dl][self.pos[1]] is None:
                self.possible_move.append((self.pos[1], self.pos[0] + dl))
            if self.pos[1] - 1 >= 0:
                self.abs_moves.append((self.pos[1] - 1, self.pos[0] + dl))
                if (not (figures_desk[self.pos[0] + dl][self.pos[1] - 1] is None) and
                        figures_desk[self.pos[0] + dl][self.pos[1] - 1].type[0] != tp):
                    self.possible_move.append((self.pos[1] - 1, self.pos[0] + dl))
            if self.pos[1] + 1 < 8:
                self.abs_moves.append((self.pos[1] + 1, self.pos[0] + dl))
                if (not (figures_desk[self.pos[0] + dl][self.pos[1] + 1] is None) and
                        figures_desk[self.pos[0] + dl][self.pos[1] + 1].type[0] != tp):
                    self.possible_move.append((self.pos[1] + 1, self.pos[0] + dl))
        if self.first and figures_desk[self.pos[0] + dl * 2][self.pos[1]] is None and \
                figures_desk[self.pos[0] + dl][self.pos[1]] is None:
            self.possible_move.append((self.pos[1], self.pos[0] + dl * 2))


class Horse(Figure):
    def __init__(self, *args):
        super().__init__(*args)

    def check_possible(self):
        self.possible_move.clear()
        self.abs_moves.clear()
        tp = self.type[0]
        ar = ((1, 2), (1, -2), (-1, 2), (-1, -2))
        for elem in ar:
            self.check(elem, tp)
            self.check(elem[::-1], tp)

    def check(self, ar, tp):
        if 0 <= self.pos[0] + ar[0] < 8:
            if 8 > self.pos[1] + ar[1] >= 0:
                self.abs_moves.append((self.pos[1] + ar[1], self.pos[0] + ar[0]))
                if (figures_desk[self.pos[0] + ar[0]][self.pos[1] + ar[1]] is None or
                        figures_desk[self.pos[0] + ar[0]][self.pos[1] + ar[1]].type[0] != tp):
                    self.possible_move.append((self.pos[1] + ar[1], self.pos[0] + ar[0]))


class Rook(Figure):
    def __init__(self, *args):
        super().__init__(*args)
        self.first = True

    def check_possible(self):
        self.possible_move.clear()
        self.abs_moves.clear()
        self.check()

    def check(self):
        tp = self.type[0]
        i = self.pos[0] - 1
        while i >= 0:
            self.abs_moves.append((self.pos[1], i))
            if figures_desk[i][self.pos[1]] is not None:
                if figures_desk[i][self.pos[1]].type[0] == tp:
                    break
                else:
                    self.possible_move.append((self.pos[1], i))
                    break
            self.possible_move.append((self.pos[1], i))
            i -= 1
        i = self.pos[0] + 1
        while i < 8:
            self.abs_moves.append((self.pos[1], i))
            if figures_desk[i][self.pos[1]] is not None:
                if figures_desk[i][self.pos[1]].type[0] == tp:
                    break
                else:
                    self.possible_move.append((self.pos[1], i))
                    break
            self.possible_move.append((self.pos[1], i))
            i += 1
        i = self.pos[1] - 1
        while i >= 0:
            self.abs_moves.append((i, self.pos[0]))
            if figures_desk[self.pos[0]][i] is not None:
                if figures_desk[self.pos[0]][i].type[0] == tp:
                    break
                else:
                    self.possible_move.append((i, self.pos[0]))
                    break
            self.possible_move.append((i, self.pos[0]))
            i -= 1
        i = self.pos[1] + 1
        while i < 8:
            self.abs_moves.append((i, self.pos[0]))
            if figures_desk[self.pos[0]][i] is not None:
                if figures_desk[self.pos[0]][i].type[0] == tp:
                    break
                else:
                    self.possible_move.append((i, self.pos[0]))
                    break
            self.possible_move.append((i, self.pos[0]))
            i += 1


class Bishop(Figure):
    def __init__(self, *args):
        super().__init__(*args)

    def check_possible(self):
        self.possible_move.clear()
        self.abs_moves.clear()
        v = ((1, 1), (-1, -1), (-1, 1), (1, -1))
        for elem in v:
            self.check(elem)

    def check(self, v):
        tp = self.type[0]
        i = self.pos[0] + v[0]
        j = self.pos[1] + v[1]
        while 8 > i >= 0 and 8 > j >= 0:
            self.abs_moves.append((j, i))
            if figures_desk[i][j] is not None:
                if figures_desk[i][j].type[0] == tp:
                    break
                else:
                    self.possible_move.append((j, i))
                    break
            self.possible_move.append((j, i))
            i += v[0]
            j += v[1]


class Queen(Rook):
    def __init__(self, *args):
        super().__init__(*args)

    def check_possible(self):
        self.possible_move.clear()
        self.abs_moves.clear()
        self.check()
        v = ((1, 1), (-1, -1), (-1, 1), (1, -1))
        for elem in v:
            self.check_b(elem)

    def check(self):
        super().check()

    def check_b(self, v):
        tp = self.type[0]
        i = self.pos[0] + v[0]
        j = self.pos[1] + v[1]
        while 8 > i >= 0 and 8 > j >= 0:
            self.abs_moves.append((j, i))
            if figures_desk[i][j] is not None:
                if figures_desk[i][j].type[0] == tp:
                    break
                else:
                    self.possible_move.append((j, i))
                    break
            self.possible_move.append((j, i))
            i += v[0]
            j += v[1]


class King(Figure):
    def __init__(self, *args):
        super().__init__(*args)
        self.op_moves = []
        self.first = True

    def is_under_attack(self):
        tp = self.type[0]
        self.op_moves.clear()
        for row in figures_desk:
            for elem in row:
                if not (elem is None) and elem.type[0] != tp:
                    elem.check_possible()
                    self.op_moves += elem.abs_moves
        if self.pos[::-1] in self.op_moves:
            return True
        return False

    def check_possible(self):
        pos = self.pos
        self.possible_move.clear()
        self.abs_moves.clear()
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                y = pos[0] + i
                x = pos[1] + j
                if 0 <= y < 8 and 0 <= x < 8:
                    self.abs_moves.append((x, y))
                    if (x, y) not in self.op_moves and (figures_desk[y][x] is None or
                                                        figures_desk[y][x].type[0] != self.type[0]):
                        self.possible_move.append((x, y))

    def castling(self):
        y = 7 if self.type[0] == 'W' else 0
        res = []
        flag = True
        if self.first:
            if isinstance(figures_desk[y][0], Rook) and figures_desk[y][0].first:
                for i in range(1, self.pos[1]):
                    if figures_desk[y][i] is not None or (i, y) in self.op_moves:
                        flag = False
                if flag and (self.pos[1], y) not in self.op_moves:
                    res.append((2, y))
            flag = True
            if isinstance(figures_desk[y][-1], Rook) and figures_desk[y][-1].first:
                for i in range(self.pos[1] + 1, 7):
                    if figures_desk[y][i] is not None or (i, y) in self.op_moves:
                        flag = False
                if flag and (self.pos[1], y) not in self.op_moves:
                    res.append((6, y))
        return res


pygame.init()
size = width, height = 530, 540
screen = pygame.display.set_mode((width, height))

clock = pygame.time.Clock()
FPS = 60

figures = pygame.sprite.Group()

desk = []
figures_desk = []

game = Game()
game.start()
