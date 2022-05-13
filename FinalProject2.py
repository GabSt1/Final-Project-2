# Original idea: https://github.com/clear-code-projects/Breakout
# Added features: GUI main menu, difficulty setting, and when you run out of lives, it takes you to the main menu instead of quitting the program

import pygame, sys, time
from settings import *
from sprites import Player, Ball, Block, Upgrade, Projectile
from surfacemaker import SurfaceMaker
from random import choice, randint
from tkinter import *


# class that will make the GUI main menu

class GUI:
    def __init__(self, window):
        # creates the window and title

        self.window = window
        self.frame_title = Frame(self.window)
        self.label_title = Label(self.frame_title, text='BREAKOUT')
        self.label_title.pack(padx=5, side='top')
        self.frame_title.pack()

        # creates the difficulty selection

        self.frame_diff = Frame(self.window)
        self.label_diff = Label(self.frame_diff, text='Difficulty: ')
        self.label_diff.pack(side='left')
        self.radio_1 = IntVar()
        self.radio_1.set(0)
        self.diff_easy = Radiobutton(self.frame_diff, text='Easy', variable=self.radio_1, value=0)
        self.diff_medium = Radiobutton(self.frame_diff, text='Medium', variable=self.radio_1, value=1)
        self.diff_hard = Radiobutton(self.frame_diff, text='Hard', variable=self.radio_1, value=2)
        self.diff_easy.pack(side='left')
        self.diff_medium.pack(side='left')
        self.diff_hard.pack(side='left')
        self.label_diff.pack(side='left')
        self.frame_diff.pack(side='top')

        # creates the start button, and the button to show the controls

        self.button_start = Button(self.window, text='START', command=window.destroy)
        self.button_start.pack(side='bottom', pady=40)

        self.button_controls = Button(self.window, text='CONTROLS', command=self.controls)
        self.button_controls.pack(side='bottom')

    # creates the text to show the controls
    def controls(self):
        self.frame_control = Frame(self.window)
        self.label_control = Label(self.frame_control, text='-Use the left and right arrow keys to move the paddle')
        self.frame_control2 = Frame(self.window)
        self.label_control2 = Label(self.frame_control, text='-Use the space bar to shoot lasers')
        self.frame_control2.pack(side='bottom')
        self.label_control2.pack(side='bottom')
        self.frame_control.pack(side='bottom')
        self.label_control.pack(side='bottom')

class Game:
    def __init__(self):

        # general setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Breakout')

        # background
        self.bg = self.create_bg()

        # sprite group setup
        self.all_sprites = pygame.sprite.Group()
        self.block_sprites = pygame.sprite.Group()
        self.upgrade_sprites = pygame.sprite.Group()
        self.projectile_sprites = pygame.sprite.Group()

        # setup
        self.surfacemaker = SurfaceMaker()
        self.player = Player(self.all_sprites, self.surfacemaker)
        self.stage_setup()
        self.ball = Ball(self.all_sprites, self.player, self.block_sprites)


        # hearts
        self.heart_surf = pygame.image.load('../graphics/other/heart.png').convert_alpha()

        # projectile
        self.projectile_surf = pygame.image.load('../graphics/other/projectile.png').convert_alpha()
        self.can_shoot = True
        self.shoot_time = 0

        # crt
        self.crt = CRT()

    def create_upgrade(self, pos):
        upgrade_type = choice(UPGRADES)
        Upgrade(pos, upgrade_type, [self.all_sprites, self.upgrade_sprites])

    def create_bg(self):
        bg_original = pygame.image.load('../graphics/other/bg.png').convert()
        scale_factor = WINDOW_HEIGHT / bg_original.get_height()
        scaled_width = bg_original.get_width() * scale_factor
        scaled_height = bg_original.get_height() * scale_factor
        scaled_bg = pygame.transform.scale(bg_original, (scaled_width, scaled_height))
        return scaled_bg

    def stage_setup(self):
        # cycle through all rows and columns of BLOCK MAP
        for row_index, row in enumerate(BLOCK_MAP):
            for col_index, col in enumerate(row):
                if col != ' ':
                    # find the x and y position for each individual block
                    x = col_index * (BLOCK_WIDTH + GAP_SIZE) + GAP_SIZE // 2
                    y = TOP_OFFSET + row_index * (BLOCK_HEIGHT + GAP_SIZE) + GAP_SIZE // 2
                    Block(col, (x, y), [self.all_sprites, self.block_sprites], self.surfacemaker, self.create_upgrade)

    def display_hearts(self):
        for i in range(self.player.hearts):
            x = 2 + i * (self.heart_surf.get_width() + 2)
            self.display_surface.blit(self.heart_surf, (x, 4))


    def upgrade_collision(self):
        overlap_sprites = pygame.sprite.spritecollide(self.player, self.upgrade_sprites, True)
        for sprite in overlap_sprites:
            self.player.upgrade(sprite.upgrade_type)

    def create_projectile(self):
        for projectile in self.player.laser_rects:
            Projectile(
                projectile.midtop - pygame.math.Vector2(0, 30),
                self.projectile_surf,
                [self.all_sprites, self.projectile_sprites])

    def laser_timer(self):
        if pygame.time.get_ticks() - self.shoot_time >= 500:
            self.can_shoot = True

    def projectile_block_collision(self):
        for projectile in self.projectile_sprites:
            overlap_sprites = pygame.sprite.spritecollide(projectile, self.block_sprites, False)
            if overlap_sprites:
                for sprite in overlap_sprites:
                    sprite.get_damage(1)
                projectile.kill()

    def run(self):
        last_time = time.time()
        while True:

            # delta time
            dt = time.time() - last_time
            last_time = time.time()

            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if self.player.hearts <= 0:
                    pygame.quit()
                    window = Tk()
                    window.title('Final Project 2')
                    window.geometry('400x400')
                    window.resizable(False, False)
                    widgets = GUI(window)
                    window.mainloop()
                    game = Game()
                    game.run()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.ball.active = True
                        if self.can_shoot:
                            self.create_projectile()
                            self.can_shoot = False
                            self.shoot_time = pygame.time.get_ticks()

            # draw bg
            self.display_surface.blit(self.bg, (0, 0))

            # update the game
            self.all_sprites.update(dt)
            self.upgrade_collision()
            self.laser_timer()
            self.projectile_block_collision()

            # draw the frame
            self.all_sprites.draw(self.display_surface)
            self.display_hearts()

            # crt styling
            self.crt.draw()

            # update window
            pygame.display.update()


class CRT:
    def __init__(self):
        vignette = pygame.image.load('../graphics/other/tv.png').convert_alpha()
        self.scaled_vignette = pygame.transform.scale(vignette, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.display_surface = pygame.display.get_surface()
        self.create_crt_lines()

    def create_crt_lines(self):
        line_height = 4
        line_amount = WINDOW_HEIGHT // line_height
        for line in range(line_amount):
            y = line * line_height
            pygame.draw.line(self.scaled_vignette, (20, 20, 20), (0, y), (WINDOW_WIDTH, y), 1)

    def draw(self):
        self.scaled_vignette.set_alpha(randint(60, 75))
        self.display_surface.blit(self.scaled_vignette, (0, 0))


if __name__ == '__main__':
    window = Tk()
    window.title('Final Project 2')
    window.geometry('400x300')
    window.resizable(False, False)
    widgets = GUI(window)
    window.mainloop()
    game = Game()

    # Depending on the difficulty you select in the main menu, the ball speed will change
    if widgets.radio_1.get() == 0:
        game.ball.speed = 100

    elif widgets.radio_1.get() == 1:
        game.ball.speed = 250

    else:
        game.ball.speed = 400

    game.run()
