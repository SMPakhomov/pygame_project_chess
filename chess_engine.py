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
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 10 <= event.pos[0] <= 510 and 10 <= event.pos[1] <= 510 and not is_grabbed:
                        grabbed = (int((event.pos[0] - 10) / 62.5), int((event.pos[1] - 10) / 62.5))
                        figures_desk[grabbed[1]][grabbed[0]].check_possible()
                        print(figures_desk[grabbed[1]][grabbed[0]].possible_move)
                        pos = event.pos
                        is_grabbed = True
                if event.type == pygame.MOUSEBUTTONUP:
                    is_grabbed = False
                    pnt = (int((event.pos[0] - 10) / 62.5), int((event.pos[1] - 10) / 62.5))
                    print(pnt)
                    if pnt not in figures_desk[grabbed[1]][grabbed[0]].possible_move:
                        figures_desk[grabbed[1]][grabbed[0]].rect.x = grabbed[0] * 62.5 + 22.25
                        figures_desk[grabbed[1]][grabbed[0]].rect.y = grabbed[1] * 62.5 + 22.25
                    else:
                        figures_desk[grabbed[1]][grabbed[0]].rect.x = pnt[0] * 62.5 + 22.25
                        figures_desk[grabbed[1]][grabbed[0]].rect.y = pnt[1] * 62.5 + 22.25
                        figures_desk[grabbed[1]][grabbed[0]].pos = pnt[::-1]
                        if figures_desk[pnt[1]][pnt[0]] is not None:
                            figures_desk[pnt[1]][pnt[0]].kill()
                        figures_desk[grabbed[1]][grabbed[0]], figures_desk[pnt[1]][pnt[0]] = None, \
                                                                                             figures_desk[grabbed[1]][
                                                                                                 grabbed[0]]
                        desk[grabbed[1]][grabbed[0]], desk[pnt[1]][pnt[0]] = '.', \
                                                                             desk[grabbed[1]][
                                                                                 grabbed[0]]
                if is_grabbed:
                    np = pygame.mouse.get_pos()
                    figures_desk[grabbed[1]][grabbed[0]].rect.x += np[0] - pos[0]
                    figures_desk[grabbed[1]][grabbed[0]].rect.y += np[1] - pos[1]
                    pos = np

            screen.fill((250, 188, 90, 98))
            t = clock.tick(FPS) / 100000
            self.desk.update(t)
            pygame.display.flip()


class Desk:
    def __init__(self, time, color=((240, 240, 240), (100, 100, 100))):
        global desk, figures_desk
        with open('def_desk.txt', 'r') as file:
            desk = [file.readline().split(' ') for _ in range(8)]
        figures_desk = []
        for i in range(8):
            tmp = []
            for j in range(8):
                if desk[i][j].rstrip('\n') != '.':
                    if desk[i][j].rstrip('\n')[1] == "P":
                        tmp.append(Pawn((i, j), desk[i][j]))
                    else:
                        tmp.append(Figure((i, j), desk[i][j]))
                else:
                    tmp.append(None)
            figures_desk.append(tmp)
        self.color = color  # цвет доски - кореж из двух цветов в формате rgb
        self.time = [time, time]
        self.turn = 0  # чей ход

    def update(self, t):
        self.draw_desk()
        self.draw_timer(t)
        figures.update()
        figures.draw(screen)

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
                    screen.fill(pygame.Color(color), pygame.Rect(62.5 * j + 20, 62.5 * i + 20, 62.5, 62.5))
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
        self.rect.x = pos[1] * 62.5 + 22.25
        self.rect.y = pos[0] * 62.5 + 22.25
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
    #ДОБАВИТЬ ПЕРВОЙ ХОД НА ДВА
    def check_possible(self):
        self.possible_move.clear()
        tp = "W"
        dl = 1
        if self.type[0] == "D":
            tp = "D"
            dl = -1
        if self.pos[0] + dl >= 0:
            if figures_desk[self.pos[0] + dl][self.pos[1]] is None:
                self.possible_move.append((self.pos[1], self.pos[0] + dl))
            if self.pos[1] - 1 >= 0 and (not(figures_desk[self.pos[0] + dl][self.pos[1] - 1] is None) and
                                         figures_desk[self.pos[0] + dl][self.pos[1] - 1].type[0] != tp):
                self.possible_move.append((self.pos[1] - 1, self.pos[0] + dl))
            if self.pos[1] + 1 < 8 and (not(figures_desk[self.pos[0] + dl][self.pos[1] + 1] is None) and
                                        figures_desk[self.pos[0] + dl][self.pos[1] + 1].type[0] != tp):
                self.possible_move.append((self.pos[1] + 1, self.pos[0] + dl))


pygame.init()
size = width, height = 540, 540
screen = pygame.display.set_mode((width, height))

clock = pygame.time.Clock()
FPS = 60

figures = pygame.sprite.Group()

desk = []
figures_desk = []

game = Game()
game.start()
