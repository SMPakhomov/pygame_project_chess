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
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((250, 188, 90, 98))
            t = clock.tick(FPS) / 100000
            self.desk.update(t)
            pygame.display.flip()


class Desk:
    def __init__(self, time, color=((240, 240, 240), (100, 100, 100))):
        with open('def_desk.txt', 'r') as file:
            self.desk = [file.readline().split(' ') for _ in range(8)]
            self.figures = []
            for i in range(8):
                tmp = []
                for j in range(8):
                    if self.desk[i][j].rstrip('\n') != '.':
                        tmp.append(Figure((i, j), self.desk[i][j]))
                    else:
                        tmp.append(None)
                self.figures.append(tmp)
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


pygame.init()
size = width, height = 540, 540
screen = pygame.display.set_mode((width, height))

clock = pygame.time.Clock()
FPS = 60

figures = pygame.sprite.Group()

game = Game()
game.start()
