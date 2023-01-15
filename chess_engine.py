import pygame
import os
import sys
from PyQt5.QtWidgets import QApplication
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QLCDNumber, QCheckBox, QInputDialog, QFileDialog
import random


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
        if ex.color:
            self.desk = Desk(self.time, ((153, 204, 255), (153, 51, 204)))
        else:
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
                    statistic = StatisticScreen()  # при попытке выхода в процессе игры открывается окно статистики
                    # именно оно будет играть роль финального окна для пользователя
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
            # self.pawn_on_last_point(figures_desk[1][0])

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
        # for elem in self.desk.kings[1:]:
        #     for p in elem.op_moves:
        #         pygame.draw.circle(screen, "red",
        #                            (p[0] * 62.5 + 51.5, p[1] * 62.5 + 51.5), 15, 5)
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
        con = sqlite3.connect("DATA/new.db")
        cur = con.cursor()
        font = pygame.font.Font(None, 50)
        text = font.render(f"Player {pl} win!", 1, (100, 255, 100))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - text.get_height() // 2
        pygame.draw.rect(screen, (50, 130, 250), pygame.Rect(text_x - 20, text_y - 10, 250, 55), 0)
        pygame.draw.rect(screen, (30, 30, 30), pygame.Rect(text_x - 20, text_y - 10, 250, 55), 3)
        screen.blit(text, (text_x, text_y))
        self.is_game_running = False
        if pl == 2 and ex.agree:
            result = cur.execute('''update play set loose = 
                                                        (select loose from play
                                                        where person like ?) + 1
                                                        where person like ?''', (ex.id_1, ex.id_1)).fetchall()
            result = str(cur.execute('''update play set win = 
                                        (select win from play
                                        where person like ?) + 1
                                        where person like ?''', (ex.id_2, ex.id_2)).fetchall())
        elif pl == 1 and ex.agree:
            result = str(cur.execute('''update play set win = 
                                                        (select win from play
                                                        where person like ?) + 1
                                                        where person like ?''', (ex.id_1, ex.id_1)).fetchall())
            result = cur.execute('''update play set loose = 
                                    (select loose from play
                                    where person like ?) + 1
                                    where person like ?''', (ex.id_2, ex.id_2)).fetchall()
        ex.agree = False
        con.commit()
        con.close()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    statistic = StatisticScreen()
            pygame.display.flip()
            clock.tick(FPS_start_screen)


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
            # if figures_desk[pnt[1]][pnt[0]] is not None:
            #     figures_desk[pnt[1]][pnt[0]].kill()
            figures_desk[grabbed[1]][grabbed[0]].pos = pnt[::-1]
            tmp = figures_desk[pnt[1]][pnt[0]]
            figures_desk[grabbed[1]][grabbed[0]], figures_desk[pnt[1]][pnt[0]] = None, \
                                                                                 figures_desk[grabbed[1]][grabbed[0]]
            b = [self.desk.kings[0].is_under_attack(), self.desk.kings[1].is_under_attack()]
            if b[self.desk.turn]:  # !проверить на ошибку
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
        #with open('def_else_desk.txt', 'r') as file:
        with open(ex.table, 'r') as file:
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


class AnimatedSprite(pygame.sprite.Sprite):  # класс для создания анимаций
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class InformationForm(QWidget):  # информационная форма
    def __init__(self):
        super().__init__()
        uic.loadUi('DATA/infornation_form.ui', self)
        self.setWindowTitle('Навигация')


class StartScreen():  # стартовое окно
    def __init__(self):
        information = InformationForm()  # вызов информационного окна
        information.show()
        font = pygame.font.Font(None, 30)
        intro_text = ["Шахматы - настоящая стратегия"]
        fon = pygame.transform.scale(load_image('start.jpg'), (530, 540))
        screen.blit(fon, (0, 0))
        text_coord = 30
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    game = Game()  # при нажатии на окно начинается игра
                    game.start()
            all_sprites.draw(screen)
            all_sprites.update()
            pygame.display.flip()
            clock.tick(FPS_start_screen)


def rating(id):  # функция для составлений рейтинга игрока, возвращает позицию игрока
    con = sqlite3.connect("DATA/new.db")
    cur = con.cursor()
    result = str(cur.execute('''select loose, win 
                                from play''').fetchall())[2:-2]
    result = result.split("), (")
    tabel = []
    for i in range(len(result)):
        tabel.append(int(result[i][-1]) - int(result[i][0]))
    tabel = sorted(tabel, reverse=True)
    result_person = str(cur.execute('''select loose, win 
                            from play
                            where person like ?''', (id,)).fetchall())[2:-2]
    numer = tabel.index(int(result_person[-1]) - int(result_person[0]))
    return numer + 1


class StatisticScreen():  # окно просмотра статистики
    # при желании пользователя выйти из игры, это окно играет роль финального
    def __init__(self):
        index_1, index_2 = rating(ex.id_1), rating(ex.id_2)  # поизиции игроков в рейтинге
        con = sqlite3.connect("DATA/new.db")
        cur = con.cursor()
        # далее из бд берется количество побед и проигршей первого и второго игроков
        result_1 = str(cur.execute('''select loose, win 
                                    from play
                                    where person like ?''', (ex.id_1,)).fetchall())[2:-2]
        result_2 = str(cur.execute('''select loose, win 
                                    from play
                                    where person like ?''', (ex.id_2,)).fetchall())[2:-2]
        intro_text = [f"Ваша статистика, {ex.name_1}: ", f'Поражений: {result_1[0]}', f'Побед: {result_1[-1]}',
                      f'Место в рейтинге: {index_1}', '', f"Ваша статистика, {ex.name_2}: ",
                      f'Поражений: {result_2[0]}', f'Побед: {result_2[-1]}',
                      f'Место в рейтинге: {index_2}']
        fon = pygame.transform.scale(load_image('statistic.jpg'), (530, 540))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 20
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()  # в этом моменте происходит окончательный выход из игры
                    sys.exit()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    game = Game()  # при нажатии на экран начинается игра
                    ex.agree = True  # снова становится возможна запись о победе/проигрыше
                    game.start()
            pygame.display.flip()
            clock.tick(FPS)


class Registration(QWidget):  # форма для регистрации
    def __init__(self):
        self.color = False
        super().__init__()
        uic.loadUi('DATA/registration.ui', self)
        self.setGeometry(200, 300, 541, 300)
        self.setWindowTitle('Авторизация')
        self.sms_label.hide()  # сообщение об успешном входе
        self.person_position_btn.hide()  # кнопка персональной стартовой расстановки
        self.person_position_btn.clicked.connect(self.personal_position)
        self.double_psw_lineedit.hide()
        self.double_psw_lineedit.setPlaceholderText('Введите пароль повторно')
        self.change_position_btn.clicked.connect(self.change_position)
        self.change_position_btn.hide()  # кнопка согласия
        self.change_color_btn.hide()  # кнопка для смены цвета игрового поля
        self.change_color_btn.clicked.connect(self.change_color)
        self.part = 1  # указывает на то, какой игрок 1/2 сейчас регистрируется
        self.agree = True  # возможность записи победы/проиграша
        # списки id и имен регистрирующихся пользователей
        self.id = ['', '']
        self.names = ['', '']
        self.table = "def_desk.txt"  # файл с базовой расстановкой фигур
        type_of_registration, ok_pressed = QInputDialog.getItem(
            self, "Выберите тип входа", "",
            ("Вход", "Регистрация"), 1, False)
        if ok_pressed:
            if type_of_registration == "Вход":
                self.double_psw_lineedit.hide()
                self.label_8.hide()
                self.voiti_btn.clicked.connect(self.get_id)
            else:
                self.double_psw_lineedit.show()
                self.voiti_btn.clicked.connect(self.add_id)
        self.voiti_btn.setText("Продолжить")

    def get_id(self):  # функция для входа в уже существующий аккаунт. для получения id пользователя из дб
        self.name = self.name_lineedit.text()
        self.password = self.password_lineedit.text()
        self.surname = self.surname_lineedit.text()
        con = sqlite3.connect("DATA/new.db")
        cur = con.cursor()
        result = str(cur.execute('''select psw from first
                            where name like ?
                            and surname like ?''', (self.name, self.surname)).fetchall())[3:-4]
        if result == self.password:
            self.id[self.part - 1] = str(cur.execute('''select id from first
                                        where name like ? and
                                        surname like ?
                                        and psw like ?''', (self.name, self.surname, self.password)).fetchall())[2:-3]
            self.names[self.part - 1] = self.name

            if self.part == 2:  # если авторизацию прошел второй игрок
                self.sms_label.setText("Вход произведен успешно")
                self.sms_label.show()
                self.voiti_btn.hide()
                self.change_color_btn.show()
                self.change_position_btn.show()
                self.change_position_btn.show()
                self.person_position_btn.show()
                # далее присваиваются id и имена пользователей
                self.id_1 = self.id[0]
                self.id_2 = self.id[1]
                self.name_1 = self.names[0]
                self.name_2 = self.names[1]
                con.close()
            else: # иначе процесс повторяется для второго игрока
                self.name_lineedit.clear()
                self.password_lineedit.clear()
                self.surname_lineedit.clear()
                self.voiti_btn.setText("Войти")
                type_of_registration, ok_pressed = QInputDialog.getItem(
                    self, "Выберите тип входа", "",
                    ("Вход", "Регистрация"), 1, False)
                if ok_pressed:
                    if type_of_registration == "Вход":
                        self.double_psw_lineedit.hide()
                        self.label_8.hide()
                        self.voiti_btn.clicked.connect(self.get_id)
                    else:
                        self.double_psw_lineedit.show()
                        self.voiti_btn.clicked.connect(self.add_id)
                self.part = 2  # фиксируем, что далее регистрацию будет проходить второй игрок
        else:
            self.sms_label.setText('Введены неверные данные')

    def add_id(self):  # функция для регистрации нового пользователя
        if self.password_lineedit.text() != self.double_psw_lineedit.text():
            self.double_psw_lineedit.setText("Пароли не совпадают")
        else:
            self.password = self.password_lineedit.text()
            self.name = self.name_lineedit.text()
            self.surname = self.surname_lineedit.text()
            con = sqlite3.connect("DATA/new.db")
            cur = con.cursor()
            cur.execute('''insert into first(name, surname, psw)
                               values (?, ?, ?)''', (self.name, self.surname, self.password))
            self.id[self.part - 1] = str(cur.execute('''select id from first
                                        where surname like ? and name like ? and psw like ?''',
                                                     (self.surname, self.name, self.password)).fetchall())[2:-3]
            self.names[self.part - 1] = self.name
            cur.execute('''insert into play(person, loose, win)
                               values (?,
                               '0', '0')''', (self.id[self.part - 1],))
            if self.part == 2:  # если регистрацию прошел второй игрок
                self.sms_label.setText('Регистрация прошла успешно')
                self.sms_label.show()
                self.change_color_btn.show()
                self.voiti_btn.hide()
                self.change_position_btn.show()
                self.person_position_btn.show()
                # далее присваиваются id и имена пользователей
                self.id_1 = self.id[0]
                self.id_2 = self.id[1]
                self.name_1 = self.names[0]
                self.name_2 = self.names[1]
                con.commit()
                con.close()
            else:  # иначе процесс повторяется для второго пользователя
                self.name_lineedit.clear()
                self.password_lineedit.clear()
                self.surname_lineedit.clear()
                self.double_psw_lineedit.clear()
                self.voiti_btn.setText("Войти")
                type_of_registration, ok_pressed = QInputDialog.getItem(
                    self, "Выберите тип входа", "",
                    ("Вход", "Регистрация"), 1, False)
                if ok_pressed:
                    if type_of_registration == "Вход":
                        self.double_psw_lineedit.hide()
                        self.voiti_btn.clicked.connect(self.get_id)
                    else:
                        self.double_psw_lineedit.show()
                        self.voiti_btn.clicked.connect(self.add_id)
                self.part = 2

    def change_color(self):  # функция смены цвета игрового поля
        self.color = True

    def change_position(self):  # функция, которая случайным образом выберет отличную от базовой расстановку
        n = random.randint(1, 3)
        self.table = ('def_desk-' + str(n) + '.txt')

    def personal_position(self):  # функция, которая позволяет начать с пользовательской расстановкой
        self.table = 'def_desk_person.txt'


clock = pygame.time.Clock()
FPS = 60
FPS_start_screen = 5  # более медленное fps для анимации на стартовом экране
all_sprites = pygame.sprite.Group()
figures = pygame.sprite.Group()
lord = AnimatedSprite(load_image("lord-2.png"), 7, 1, 380, 30)
pygame.init()
size = width, height = 530, 540
desk = []
figures_desk = []

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Registration()
    ex.show()

screen = pygame.display.set_mode((width, height))
start_screen = StartScreen()
