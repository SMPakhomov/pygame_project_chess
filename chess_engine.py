import pygame
import os
import sys
from PyQt5.QtWidgets import QApplication
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QLCDNumber, QCheckBox, QInputDialog, QFileDialog



class Game:
    def __init__(self, tp=1, time=0.05):
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
        tp = "W" if nm == 0 else "B"
        for i in range(8):
            for j in range(8):
                if figures_desk[i][j] is not None and figures_desk[i][j].type == tp:
                    elem = figures_desk[i][j]
                    elem.check_possible()
                    for move in figures_desk[i][j].possible_move:
                        figures_desk[i][j].pos = move[::-1]
                        tmp = figures_desk[move[1]][move[0]]
                        figures_desk[i][j], figures_desk[move[1]][move[0]] = None, elem
                        b = [self.desk.kings[0].is_under_attack(), self.desk.kings[1].is_under_attack()]
                        if not b[nm]:
                            figures_desk[i][j], figures_desk[move[1]][move[0]] = elem, tmp
                            figures_desk[i][j].pos = (j, i)
                            return True
        return False

    def update(self, is_grabbed, grabbed, t):
        self.desk.draw_desk()
        if self.is_game_running:
            self.desk.draw_timer(t)
        if is_grabbed:
            for elem in figures_desk[grabbed[1]][grabbed[0]].possible_move:
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
                                                        where person like ?''', (ex.id, ex.id)).fetchall()
        elif pl == 1 and ex.agree:
            result = str(cur.execute('''update play set win = 
                                                        (select win from play
                                                        where person like ?) + 1
                                                        where person like ?''', (ex.id, ex.id)).fetchall())
        ex.agree = False
        con.commit()
        con.close()


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
        if pnt not in figures_desk[grabbed[1]][grabbed[0]].possible_move:
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
                if figures_desk[pnt[1]][pnt[0]].type[1] == "P":
                    figures_desk[pnt[1]][pnt[0]].first = False

    # def pawn_on_last_point(self, pawn):
    #     is_choosed = False
    #     pygame.draw.rect(screen, (250, 188, 90, 98), pygame.Rect(100, 80, 330, 55))
    #     pygame.draw.rect(screen, "black", pygame.Rect(100, 80, 330, 55), 3)
    #     font = pygame.font.Font(None, 25)
    #     text = font.render(f"Выберите фигуру на замену пешке", 1, (250, 250, 250))
    #     text_x = width // 2 - text.get_width() // 2
    #     text_y = height // 5 - text.get_height() // 2
    #     screen.blit(text, (text_x, text_y))
    #     pygame.display.flip()
    #     v = []
    #     while not is_choosed:
    #         if input() == 'q':
    #             exit()


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
        fullname = os.path.join('DATA', name + color)
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
                self.abs_moves.append(figures_desk[self.pos[0] + dl][self.pos[1] - 1])
                if (not (figures_desk[self.pos[0] + dl][self.pos[1] - 1] is None) and
                        figures_desk[self.pos[0] + dl][self.pos[1] - 1].type[0] != tp):
                    self.possible_move.append((self.pos[1] - 1, self.pos[0] + dl))
            if self.pos[1] + 1 < 8:
                self.abs_moves.append(figures_desk[self.pos[0] + dl][self.pos[1] + 1])
                if (not (figures_desk[self.pos[0] + dl][self.pos[1] + 1] is None) and
                        figures_desk[self.pos[0] + dl][self.pos[1] + 1].type[0] != tp):
                    self.possible_move.append((self.pos[1] + 1, self.pos[0] + dl))
        if self.first and 0 <= self.pos[0] + dl * 2 < 8 and figures_desk[self.pos[0] + dl * 2][self.pos[1]] is None:
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

    def is_under_attack(self):
        tp = self.type[0]
        self.op_moves.clear()
        for row in figures_desk:
            for elem in row:
                if not (elem is None) and elem.type[0] != tp:
                    elem.check_possible()
                    # if elem.type[1] == "P":
                    #     tmp = []
                    #     y, x = elem.pos
                    #     d = -1
                    #     if elem.type[0] == "D":
                    #         d = 1
                    #     if 8 > y + d >= 0:
                    #         if x - 1 >= 0:
                    #             tmp.append((x - 1, y + d))
                    #         if x + 1 < 8:
                    #             tmp.append((x + 1, y + d))
                    #     self.op_moves += tmp
                    # elif elem.type[1] == "K":
                    #     tmp = []
                    #     y, x = elem.pos
                    #     for i in (-1, 1, 0):
                    #         for j in (-1, 1, 0):
                    #             if 0 <= y + i < 8 and 0 <= x + j < 8:
                    #                 tmp.append((x + j, y + i))
                    #     self.op_moves += tmp
                    # else:
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
                tmp = (pos[0] + i, pos[1] + j)
                if 0 <= tmp[0] < 8 and 0 <= tmp[1] < 8:
                    self.abs_moves.append((tmp[::-1]))
                    if tmp[::-1] not in self.op_moves and (
                            figures_desk[tmp[0]][tmp[1]] is None or
                            figures_desk[tmp[0]][tmp[1]].type[0] != self.type[0]):
                        self.possible_move.append(tmp[::-1])


def load_image(name, color_key=None):
    fullname = os.path.join('DATA', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
  #  image = image.convert_alpha()
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class AnimatedSprite(pygame.sprite.Sprite):
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


def start_screen():
    intro_text = ["Шахматы - настоящая стратегия", 'Нажмите r, g или b для смены цвета']

    fon = pygame.transform.scale(load_image('start.jpg'), (530, 540))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
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
                return
            elif event.type == pygame.K_r:
                color = '-red'
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS_start_screen)


def rating(id):
    con = sqlite3.connect("DATA/new.db")
    cur = con.cursor()
    result = str(cur.execute('''select loose, win 
                                from play''').fetchall())[2:-2]
    print(result)
    result = result.split("), (")
    tabel = []
    print(result)
    for i in range(len(result)):
        print(result[i])
        tabel.append(int(result[i][-1]) - int(result[i][0]))
    tabel = sorted(tabel, reverse=True)
    print(tabel)
    result_person = str(cur.execute('''select loose, win 
                            from play
                            where person like ?''', (id,)).fetchall())[2:-2]
    print(result_person)
    numer = tabel.index(int(result_person[-1]) - int(result_person[0]))
    return numer + 1


def statistic_screen():
    index = rating(ex.id)
    con = sqlite3.connect("DATA/new.db")
    cur = con.cursor()
    result = str(cur.execute('''select loose, win 
                                from play
                                where person like ?''', (ex.id,)).fetchall())[2:-2]
    intro_text = ["Ваша статистика: ", '', f'Поражений: {result[0]}', f'Побед: {result[-1]}', '', f'Место в рейтинге: {index}']

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
                pygame.quit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                # game = Game()
                # game.start()
                pass
        pygame.display.flip()
        clock.tick(FPS_start_screen)


class Registration(QWidget):
    def __init__(self):
        global id
        super().__init__()
        uic.loadUi('DATA/registration.ui', self)
        self.sms_label.hide()
        self.double_psw_lineedit.hide()
        self.label_8.hide()
        self.vhod_btn.hide()
        self.agree = True
        self.registration_btn.hide()
        self.voiti_btn.setText(" ")
        self.setWindowTitle('Авторизация')
        type_of_registration, ok_pressed = QInputDialog.getItem(
            self, "Выберите тип входа", "",
            ("Вход", "Регистрация"), 1, False)
        if ok_pressed:
            if type_of_registration == "Вход":
                self.voiti_btn.setText("Войти")
                self.double_psw_lineedit.hide()
                self.label_8.hide()
                self.voiti_btn.clicked.connect(self.get_id)
            else:
                self.double_psw_lineedit.show()
                self.label_8.show()
                self.voiti_btn.setText("Зарегистрироваться")
                self.voiti_btn.clicked.connect(self.add_id)

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
            self.sms_label.hide()
            con = sqlite3.connect("DATA/new.db")
            cur = con.cursor()
            self.id = str(cur.execute('''select id from first
                                        where name like ? and
                                        surname like ?
                                        and psw like ?''', (self.name, self.surname, self.password)).fetchall())[2:-3]
            self.sms_label.setText("Вход произведен успешно, " + self.name)
            self.sms_label.show()
            self.voiti_btn.hide()
            con.close()
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

            self.id = str(cur.execute('''select id from first
                                        where surname like ? and name like ? and psw like ?''',
                                      (self.surname, self.name, self.password)).fetchall())[2:-3]

            cur.execute('''insert into play(person, loose, win)
                               values (?,
                               '0', '0')''', (self.id,))

            self.sms_label.setText('Регистрация прошла успешно, ' + self.name)
            self.sms_label.show()
            id = self.id
            con.commit()
            con.close()
            self.voiti_btn.hide()


clock = pygame.time.Clock()
FPS = 60

FPS_start_screen = 5
all_sprites = pygame.sprite.Group()
dragon = AnimatedSprite(load_image("lord-2.png"), 7, 1, 380, 30)
figures = pygame.sprite.Group()

desk = []
figures_desk = []

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Registration()
    ex.show()

pygame.init()
size = width, height = 530, 540
screen = pygame.display.set_mode((width, height))
start_screen()

game = Game()
game.start()
    # поправить пешки (доход до конца), ДОБАВИТЬ ОТКАТ НАЗАД

statistic_screen()