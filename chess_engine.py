import pygame
import os
import sys


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
            print(self.is_under_attacks)
            self.update(is_grabbed, grabbed, t)
            self.check_mat()

    def check_mat(self):
        for i in (0, 1):
            if self.is_under_attacks[i] == True and self.desk.kings[i].possible_move == []:
                self.end_table((i + 1) % 2)

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
        font = pygame.font.Font(None, 50)
        text = font.render(f"Player {pl} win!", 1, (100, 255, 100))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - text.get_height() // 2
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
        if pnt not in figures_desk[grabbed[1]][grabbed[0]].possible_move:
            figures_desk[grabbed[1]][grabbed[0]].rect.x = grabbed[0] * 62.5 + 20.25
            figures_desk[grabbed[1]][grabbed[0]].rect.y = grabbed[1] * 62.5 + 20.25
        else:
            if figures_desk[grabbed[1]][grabbed[0]].type[1] == "P":
                figures_desk[grabbed[1]][grabbed[0]].first = False
            figures_desk[grabbed[1]][grabbed[0]].rect.x = pnt[0] * 62.5 + 20.25
            figures_desk[grabbed[1]][grabbed[0]].rect.y = pnt[1] * 62.5 + 20.25
            figures_desk[grabbed[1]][grabbed[0]].pos = pnt[::-1]
            # if figures_desk[pnt[1]][pnt[0]] is not None:
            #     figures_desk[pnt[1]][pnt[0]].kill()
            figures_desk[grabbed[1]][grabbed[0]], figures_desk[pnt[1]][pnt[0]] = figures_desk[pnt[1]][pnt[0]], \
                                                                                 figures_desk[grabbed[1]][grabbed[0]]
            if self.is_under_attacks[self.desk.turn]:
                b = [self.desk.kings[0].is_under_attack(), self.desk.kings[1].is_under_attack()]
                if b[self.desk.turn]:
                    figures_desk[grabbed[1]][grabbed[0]], figures_desk[pnt[1]][pnt[0]] = figures_desk[pnt[1]][pnt[0]], \
                                                                                         figures_desk[grabbed[1]][
                                                                                             grabbed[0]]
                else:
                    if figures_desk[grabbed[1]][grabbed[0]] is not None:
                        figures_desk[grabbed[1]][grabbed[0]].kill()
                        figures_desk[grabbed[1]][grabbed[0]] = None
            else:
                if figures_desk[grabbed[1]][grabbed[0]] is not None:
                    figures_desk[grabbed[1]][grabbed[0]].kill()
                    figures_desk[grabbed[1]][grabbed[0]] = None
            # desk[grabbed[1]][grabbed[0]], desk[pnt[1]][pnt[0]] = '.', \
            #                                                      desk[grabbed[1]][grabbed[0]]
            self.desk.turn += 1
            self.desk.turn %= 2
            self.is_under_attacks = [self.desk.kings[0].is_under_attack(), self.desk.kings[1].is_under_attack()]


class Desk:
    def __init__(self, time, color=((240, 240, 240), (100, 100, 100))):
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

    # ДОБАВИТЬ ПЕРВОЙ ХОД НА ДВА
    def check_possible(self):
        self.possible_move.clear()
        tp = "W"
        dl = 1
        if self.type[0] == "D":
            tp = "D"
            dl = -1
        if 8 > self.pos[0] + dl >= 0:
            if figures_desk[self.pos[0] + dl][self.pos[1]] is None:
                self.possible_move.append((self.pos[1], self.pos[0] + dl))
            if self.pos[1] - 1 >= 0 and (not (figures_desk[self.pos[0] + dl][self.pos[1] - 1] is None) and
                                         figures_desk[self.pos[0] + dl][self.pos[1] - 1].type[0] != tp):
                self.possible_move.append((self.pos[1] - 1, self.pos[0] + dl))
            if self.pos[1] + 1 < 8 and (not (figures_desk[self.pos[0] + dl][self.pos[1] + 1] is None) and
                                        figures_desk[self.pos[0] + dl][self.pos[1] + 1].type[0] != tp):
                self.possible_move.append((self.pos[1] + 1, self.pos[0] + dl))
        if self.first:
            self.possible_move.append((self.pos[1], self.pos[0] + dl * 2))


class Horse(Figure):
    def __init__(self, *args):
        super().__init__(*args)

    def check_possible(self):
        self.possible_move.clear()
        tp = self.type[0]
        ar = ((1, 2), (1, -2), (-1, 2), (-1, -2))
        for elem in ar:
            self.check(elem, tp)
            self.check(elem[::-1], tp)

    def check(self, ar, tp):
        if 0 <= self.pos[0] + ar[0] < 8:
            if 8 > self.pos[1] + ar[1] >= 0 and (figures_desk[self.pos[0] + ar[0]][self.pos[1] + ar[1]] is None or
                                                 figures_desk[self.pos[0] + ar[0]][self.pos[1] + ar[1]].type[0] != tp):
                self.possible_move.append((self.pos[1] + ar[1], self.pos[0] + ar[0]))


class Rook(Figure):
    def __init__(self, *args):
        super().__init__(*args)

    def check_possible(self):
        self.possible_move.clear()
        self.check()

    def check(self):
        tp = self.type[0]
        i = self.pos[0] - 1
        while i >= 0:
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
        v = ((1, 1), (-1, -1), (-1, 1), (1, -1))
        for elem in v:
            self.check(elem)

    def check(self, v):
        tp = self.type[0]
        i = self.pos[0] + v[0]
        j = self.pos[1] + v[1]
        while 8 > i >= 0 and 8 > j >= 0:
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
                    if elem.type[1] == "P":
                        tmp = []
                        y, x = elem.pos
                        d = 1
                        if elem.type[0] == "D":
                            d = -1
                        if 8 > y + d >= 0:
                            if x - 1 >= 0:
                                tmp.append((x - 1, y + d))
                            if x + 1 < 8:
                                tmp.append((x + 1, y + d))
                        self.op_moves += tmp
                        # ПОФИКСИТЬ КОРОЛЯ
                    else:
                        self.op_moves += elem.possible_move
        if self.pos[::-1] in self.op_moves:
            return True
        return False

    def check_possible(self):
        pos = self.pos
        self.possible_move.clear()
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                tmp = (pos[0] + i, pos[1] + j)
                if 0 <= tmp[0] < 8 and 0 <= tmp[1] < 8:
                    if tmp[::-1] not in self.op_moves and (
                            figures_desk[tmp[0]][tmp[1]] is None or
                            figures_desk[tmp[0]][tmp[1]].type[0] != self.type[0]):
                        self.possible_move.append(tmp[::-1])


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
# поправить пешки (доход до конца, дабл шаг)
