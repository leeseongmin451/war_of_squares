"""
----War of Squares----
This game currently has 3 regular stages, and 1 test stage.
The regular stages are defined as number(1, 2, 3) in "stage" variable.
The test stage is an incomplete level and defined as string "test" in
"stage" variable.
"""

import pygame
import random
import math
import time
from os import path

# image file path
char_dir = path.join(path.dirname(__file__), 'img', 'character')
expl_dir = path.join(path.dirname(__file__), 'img', 'explosion')
bullet_dir = path.join(path.dirname(__file__), 'img', 'bullets')
hit_dir = path.join(path.dirname(__file__), 'img', 'hit')

# define colors
BLACK = [0, 0, 0]
WHITE1 = [255, 255, 255]
WHITE2 = [127, 127, 127]
WHITE3 = [63, 63, 63]
RED1 = [255, 0, 0]
RED2 = [127, 0, 0]
RED3 = [63, 0, 0]
GREEN1 = [0, 255, 0]
GREEN2 = [0, 127, 0]
GREEN3 = [0, 63, 0]
BLUE1 = [63, 191, 255]
BLUE2 = [31, 95, 127]
BLUE3 = [15, 47, 63]
CYAN1 = [0, 255, 255]
CYAN2 = [0, 127, 127]
CYAN3 = [0, 63, 63]
MAGENTA1 = [255, 0, 255]
MAGENTA3 = [63, 0, 63]
YELLOW1 = [255, 255, 0]
YELLOW2 = [127, 127, 0]
YELLOW3 = [63, 63, 0]
ORANGE1 = [255, 102, 0]
ORANGE2 = [127, 51, 0]
ORANGE3 = [63, 25, 0]
PURPLE1 = [191, 95, 255]
PURPLE2 = [95, 47, 127]
PURPLE3 = [47, 23, 63]

# define screen size
screen_width = 1200
screen_height = 800

# define entire field size
map_size = 3
map_width = screen_width * map_size
map_height = screen_height * map_size

# location of current screen on the map
screen_center = [0, 0]
curspos = (0, 0)    # cursor


# defining all sprites and functions

def distance(pos_a, pos_b):
    """ returns distance between two positions """
    dist_x = pos_a[0] - pos_b[0]
    dist_y = pos_a[1] - pos_b[1]
    return math.sqrt(dist_x*dist_x + dist_y*dist_y)


def draw_text(surf, text, size, color, pos, x, y):
    """
    draw text at a specified position
    :param surf: surface on which text will be drawn(screen)
    :param text: text to be drawn
    :param size: font size
    :param color: text color
    :param pos: a fixed point of text defined by [x, y]
    :param x: x position
    :param y: y position
    :return: None
    """
    font = pygame.font.Font(text_font, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if pos == "topleft":
        text_rect.x = x
        text_rect.y = y
    elif pos == "midtop":
        text_rect.midtop = (x, y)
    elif pos == "topright":
        text_rect.topright = (x, y)
    elif pos == "center":
        text_rect.center = (x, y)
    surf.blit(text_surface, text_rect)


class Button(pygame.sprite.Sprite):
    def __init__(self, btn_pos_size, btn_color, text, text_size, btnbck_color=(0, 0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.btn_color = btn_color
        self.btnbck_color_orig = btnbck_color
        self.btnbck_color = btnbck_color
        self.mouse_on_color = []
        self.clicked_color = []
        self.rect = btn_pos_size
        self.text = text
        self.text_size = text_size
        self.pressed = False
        self.released = False
        self.operate = False
        for ind in range(3):
            self.mouse_on_color.append((self.btn_color[ind] + self.btnbck_color[ind]) // 2)
            self.clicked_color.append((self.mouse_on_color[ind] + self.btnbck_color[ind]) // 2)
        pygame.draw.rect(screen, self.btnbck_color, self.rect, 0)
        pygame.draw.rect(screen, self.btn_color, self.rect, 2)
        draw_text(screen, self.text, self.text_size, self.btn_color, "center", self.rect[0] + self.rect[2] // 2, self.rect[1] + self.rect[3] // 2)

    def update(self):
        if pygame.Rect(self.rect).collidepoint(curspos[0], curspos[1]):
            self.btnbck_color = self.mouse_on_color
            if click:
                self.pressed = True
            if self.pressed:
                self.btnbck_color = self.clicked_color
                if not click:
                    self.released = True
                    self.pressed = False
                    self.btnbck_color = self.mouse_on_color
            elif self.released:
                self.operate = True
                self.released = False
        else:
            self.btnbck_color = self.btnbck_color_orig
            self.pressed = False
            self.released = False
            self.operate = False
        pygame.draw.rect(screen, self.btnbck_color, self.rect, 0)
        pygame.draw.rect(screen, self.btn_color, self.rect, 2)
        draw_text(screen, self.text, self.text_size, self.btn_color, "center", self.rect[0] + self.rect[2] // 2, self.rect[1] + self.rect[3] // 2)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.center = [screen_width // 2, screen_height // 2]
        self.abs_x = screen_width // 2
        self.abs_y = screen_height // 2
        self.hp = 100
        self.hp_full = self.hp
        self.mp = 100
        self.mp_full = self.mp
        self.speed = 6
        self.x_speed = 0
        self.y_speed = 0
        self.pick_range = 100
        self.bullet_power = 1
        self.max_cannon_power = 120
        self.cannon_charge_rate = 3
        self.max_shock_range = 300
        self.weapon_lvl = 1
        self.shoot_interval = 0.1
        self.last_shoot = time.time()
        self.cannon_shoot = False
        self.cannon_cooltime = 2
        self.cannon_cooltime_rate = 0.2
        self.last_cannon_shoot = time.time()

    def update(self):
        self.x_speed = 0
        self.y_speed = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a] and self.rect.center[0] >= 0:
            if -(map_size - 1) * screen_width / 2 < screen_center[0] < (map_size - 1) * screen_width / 2:
                screen_center[0] -= self.speed
            elif screen_center[0] >= (map_size - 1) * screen_width / 2 and self.rect.center[0] <= screen_width / 2:
                screen_center[0] -= self.speed
            else:
                self.x_speed = -self.speed
            self.abs_x -= self.speed
        if keystate[pygame.K_d] and self.rect.center[0] <= screen_width:
            if -(map_size - 1) * screen_width / 2 < screen_center[0] < (map_size - 1) * screen_width / 2:
                screen_center[0] += self.speed
            elif screen_center[0] <= -(map_size - 1) * screen_width / 2 and self.rect.center[0] >= screen_width / 2:
                screen_center[0] += self.speed
            else:
                self.x_speed = self.speed
            self.abs_x += self.speed
        if keystate[pygame.K_w] and self.rect.center[1] >= 0:
            if -(map_size - 1) * screen_height / 2 < screen_center[1] < (map_size - 1) * screen_height / 2:
                screen_center[1] -= self.speed
            elif screen_center[1] >= (map_size - 1) * screen_height / 2 and self.rect.center[1] <= screen_height / 2:
                screen_center[1] -= self.speed
            else:
                self.y_speed = -self.speed
            self.abs_y -= self.speed
        if keystate[pygame.K_s] and self.rect.center[1] <= screen_height:
            if -(map_size - 1) * screen_height / 2 < screen_center[1] < (map_size - 1) * screen_height / 2:
                screen_center[1] += self.speed
            elif screen_center[1] <= -(map_size - 1) * screen_height / 2 and self.rect.center[1] >= screen_height / 2:
                screen_center[1] += self.speed
            else:
                self.y_speed = self.speed
            self.abs_y += self.speed
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed

        if time.time() - self.last_shoot >= self.shoot_interval and (not click or time.time() - self.last_cannon_shoot < self.cannon_cooltime):
            self.shoot(curspos)
            self.last_shoot = time.time()

        if not self.cannon_shoot and click and time.time() - self.last_cannon_shoot >= self.cannon_cooltime:
            self.cannon_cooltime = 2
            cannonball = PlayerCannonBall(self.max_cannon_power, self.cannon_charge_rate)
            all_sprites.add(cannonball)
            player_cannon_balls.add(cannonball)
            self.cannon_shoot = True

        # regeneration
        if self.hp <= self.hp_full:
            self.hp += self.hp_full / 3000
        if self.mp <= 0:
            self.mp = 0
        if self.mp <= self.mp_full:
            self.mp += self.mp_full / 2000

    def shoot(self, target_pos):
        dist_x = target_pos[0] - self.rect.center[0]
        dist_y = target_pos[1] - self.rect.center[1]
        angle = math.atan2(dist_y, dist_x)
        if dist_x != 0 or dist_y != 0:
            if self.weapon_lvl == 1:    # shoots 1 bullet per interval
                bullet = PlayerBullet(self.bullet_power, angle)
                all_sprites.add(bullet)
                player_bullets.add(bullet)
            elif self.weapon_lvl == 2:  # shoots 2 bullets per interval
                bullet_1 = PlayerBullet(self.bullet_power, angle + math.pi / 36)
                bullet_2 = PlayerBullet(self.bullet_power, angle - math.pi / 36)
                all_sprites.add(bullet_1)
                all_sprites.add(bullet_2)
                player_bullets.add(bullet_1)
                player_bullets.add(bullet_2)
            elif self.weapon_lvl == 3:  # shoots 2 bullets per interval
                bullet_1 = PlayerBullet(self.bullet_power, angle)
                bullet_2 = PlayerBullet(self.bullet_power, angle + math.pi / 18)
                bullet_3 = PlayerBullet(self.bullet_power, angle - math.pi / 18)
                all_sprites.add(bullet_1)
                all_sprites.add(bullet_2)
                all_sprites.add(bullet_3)
                player_bullets.add(bullet_1)
                player_bullets.add(bullet_2)
                player_bullets.add(bullet_3)
            elif self.weapon_lvl == 4:  # shoots 2 bullets per interval
                bullet_1 = PlayerBullet(self.bullet_power, angle + math.pi / 180)
                bullet_2 = PlayerBullet(self.bullet_power, angle - math.pi / 180)
                bullet_3 = PlayerBullet(self.bullet_power, angle + math.pi / 18)
                bullet_4 = PlayerBullet(self.bullet_power, angle - math.pi / 18)
                all_sprites.add(bullet_1)
                all_sprites.add(bullet_2)
                all_sprites.add(bullet_3)
                all_sprites.add(bullet_4)
                player_bullets.add(bullet_1)
                player_bullets.add(bullet_2)
                player_bullets.add(bullet_3)
                player_bullets.add(bullet_4)


class TargetPointer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(targetpointer_img, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.center = curspos

    def update(self):
        self.rect.center = curspos


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, power, angle):
        pygame.sprite.Sprite.__init__(self)
        self.size = [5, 5]
        self.color_orig = BLUE1
        self.color = self.color_orig
        self.image = pygame.Surface(self.size)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.power = power
        self.rect.center = player.rect.center
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.speed = 15
        self.speedx = self.speed * math.cos(angle)
        self.speedy = self.speed * math.sin(angle)

    def update(self):
        self.abs_x += self.speedx
        self.abs_y += self.speedy
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        if self.color == CYAN1:
            self.color = self.color_orig
            self.image.fill(self.color)
        else:
            self.color = CYAN1
            self.image.fill(self.color)
        if not (-(map_size / 2 - 0.5) * screen_width < self.rect.center[0] < (map_size / 2 + 0.5) * screen_width and
                -(map_size / 2 - 0.5) * screen_height < self.rect.center[1] < (map_size / 2 + 0.5) * screen_height):
            self.kill()


class MobBullet1(pygame.sprite.Sprite):     # used by specific mob (BossLv3)
    def __init__(self, power, speed, pos, angle):
        pygame.sprite.Sprite.__init__(self)
        self.size = [6, 6]
        self.color_orig = RED1
        self.color = self.color_orig
        self.image = pygame.Surface(self.size)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.power = power
        self.rect.center = pos
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.speed = speed
        self.speedx = self.speed * math.cos(angle)
        self.speedy = self.speed * math.sin(angle)

    def update(self):
        self.abs_x += self.speedx
        self.abs_y += self.speedy
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        if self.color == WHITE1:
            self.color = self.color_orig
            self.image.fill(self.color)
        else:
            self.color = WHITE1
            self.image.fill(self.color)
        if not (-(map_size / 2 - 0.5) * screen_width < self.rect.center[0] < (map_size / 2 + 0.5) * screen_width and
                -(map_size / 2 - 0.5) * screen_height < self.rect.center[1] < (map_size / 2 + 0.5) * screen_height):
            self.kill()


class Bullet(pygame.sprite.Sprite):     # can be used by any object
    def __init__(self, power, speed, size, color, pos, angle, glow=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.power = power
        self.rect.center = pos
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.speed = speed
        self.speedx = self.speed * math.cos(angle)
        self.speedy = self.speed * math.sin(angle)
        self.color_orig = color
        self.color = color
        self.glow = glow

    def update(self):
        self.abs_x += self.speedx
        self.abs_y += self.speedy
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        if self.glow:
            if self.color == WHITE1:
                self.color = self.color_orig
                self.image.fill(self.color)
            else:
                self.color = WHITE1
                self.image.fill(self.color)
        if not (-(map_size / 2 - 0.5) * screen_width < self.rect.center[0] < (map_size / 2 + 0.5) * screen_width and
                -(map_size / 2 - 0.5) * screen_height < self.rect.center[1] < (map_size / 2 + 0.5) * screen_height):
            self.kill()


class PlayerCannonBall(pygame.sprite.Sprite):
    def __init__(self, max_power, charge_rate):
        pygame.sprite.Sprite.__init__(self)
        self.size = [10, 10]
        self.area = 100
        self.imagenum = 0
        self.image = pygame.transform.scale(cannonball1_anim[self.imagenum], self.size)
        self.rect = self.image.get_rect()
        self.power = 0
        self.max_power = max_power
        self.charge_rate = charge_rate
        self.shock_range = 0
        self.rect.center = player.rect.center
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.speedx = 0
        self.speedy = 0
        self.angle = 0
        self.speed = 12
        self.released = False
        self.temp = 0

    def update(self):
        if not self.released:
            self.area += 60
            player.mp -= 1
            self.power += self.charge_rate
            self.size = [round(math.sqrt(self.area)), round(math.sqrt(self.area))]
            self.image = pygame.transform.scale(cannonball1_anim[self.imagenum], self.size)
            self.rect = self.image.get_rect()
            self.rect.center = player.rect.center
            self.temp += player.cannon_cooltime_rate
            player.cannon_cooltime = max(2.0, self.temp)
            if not click or player.mp <= 0 or self.power >= self.max_power:
                dist_x = curspos[0] - self.rect.center[0]
                dist_y = curspos[1] - self.rect.center[1]
                self.angle = math.atan2(dist_y, dist_x)
                self.released = True
                self.shock_range = player.max_shock_range * (self.power / self.max_power)
                self.abs_x = self.rect.x + screen_center[0]
                self.abs_y = self.rect.y + screen_center[1]
                player.last_cannon_shoot = time.time()
                player.cannon_shoot = False
        else:
            self.speedx = self.speed * math.cos(self.angle)
            self.speedy = self.speed * math.sin(self.angle)
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])

        if self.imagenum == 0:
            self.imagenum = 1
            self.image = pygame.transform.scale(cannonball1_anim[self.imagenum], self.size)
        else:
            self.imagenum = 0
            self.image = pygame.transform.scale(cannonball1_anim[self.imagenum], self.size)
        if not (-(map_size / 2 - 0.5) * screen_width < self.rect.center[0] < (map_size / 2 + 0.5) * screen_width and
                -(map_size / 2 - 0.5) * screen_height < self.rect.center[1] < (map_size / 2 + 0.5) * screen_height):
            self.kill()


class MobCannonBall1(pygame.sprite.Sprite):
    def __init__(self, pos, angle, power, speed):
        pygame.sprite.Sprite.__init__(self)
        self.size = [20, 20]
        self.imagenum = 0
        self.image = pygame.transform.scale(cannonball2_anim[self.imagenum], self.size)
        self.rect = self.image.get_rect()
        self.power = power
        self.rect.center = pos
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.speed = speed
        self.speedx = self.speed * math.cos(angle)
        self.speedy = self.speed * math.sin(angle)

    def update(self):
        self.abs_x += self.speedx
        self.abs_y += self.speedy
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        if self.imagenum == 0:
            self.imagenum = 1
            self.image = pygame.transform.scale(cannonball2_anim[self.imagenum], self.size)
        else:
            self.imagenum = 0
            self.image = pygame.transform.scale(cannonball2_anim[self.imagenum], self.size)
        if not (-(map_size / 2 - 0.5) * screen_width < self.rect.center[0] < (map_size / 2 + 0.5) * screen_width and
                -(map_size / 2 - 0.5) * screen_height < self.rect.center[1] < (map_size / 2 + 0.5) * screen_height):
            self.kill()


class BossPointer(pygame.sprite.Sprite):
    # points to boss's direction when boss spawned
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = pygame.transform.scale(bosspointer_img, (80, 15))
        self.image_orig.set_colorkey((255, 255, 255))
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center

    def update(self):
        self.rect.center = player.rect.center
        dist_x = boss.rect.center[0] - player.rect.center[0]
        dist_y = boss.rect.center[1] - player.rect.center[1]
        angle = math.atan2(dist_y, dist_x) * 180 / math.pi
        new_image = pygame.transform.rotate(self.image_orig, -angle)
        old_center = self.rect.center
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center


class MoveLineMob1(pygame.sprite.Sprite):
    """
    just moves through straight line with random direction and random speed
    does not attack player
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = [30, 30]
        self.debris_size = 16
        self.debris_speed = random.randrange(10, 15)
        self.norm_image = linemob1_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = linemob1_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(5, 10)
        self.damage = 15
        self.hit = False
        self.hitcount = 0
        self.hp = 1
        self.hp_full = self.hp
        self.dead = False
        self.points = 5
        self.no_points = False
        self.type = random.randrange(1, 5)
        if self.type == 1:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
            self.angle = random.uniform(0, math.pi)
        elif self.type == 2:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
            self.angle = random.uniform(-math.pi, 0)
        elif self.type == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.angle = random.uniform(-math.pi / 2, math.pi / 2)
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.angle = random.uniform(math.pi / 2, math.pi * 3 / 2)
        self.speedx = self.speed * math.cos(self.angle)
        self.speedy = self.speed * math.sin(self.angle)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            if not (-self.rect.width - (map_size / 2 - 0.5) * screen_width < self.abs_x < (map_size / 2 + 0.5) * screen_width and
                    -self.rect.height - (map_size / 2 - 0.5) * screen_height < self.abs_y < (map_size / 2 + 0.5) * screen_height):
                if self.abs_x <= -self.rect.width - (map_size / 2 - 0.5) * screen_width:
                    self.abs_x = (map_size / 2 + 0.5) * screen_width - 1
                elif self.abs_x >= (map_size / 2 + 0.5) * screen_width:
                    self.abs_x = -self.rect.width - (map_size / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -self.rect.height - (map_size / 2 - 0.5) * screen_height:
                    self.abs_y = (map_size / 2 + 0.5) * screen_height - 1
                else:
                    self.abs_y = -self.rect.height - (map_size / 2 - 0.5) * screen_height + 1
                self.speedx = self.speed * math.cos(self.angle)
                self.speedy = self.speed * math.sin(self.angle)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class MoveLineMob2(pygame.sprite.Sprite):
    """
    similar to MoveLineMob1, but has bigger size and higher hp
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = [40, 40]
        self.debris_size = 20
        self.debris_speed = random.randrange(12, 18)
        self.norm_image = linemob2_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = linemob2_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(3, 8)
        self.damage = 37
        self.hit = False
        self.hitcount = 0
        self.hp = 5
        self.hp_full = self.hp
        self.dead = False
        self.points = 35
        self.no_points = False
        self.type = random.randrange(1, 5)
        if self.type == 1:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
            self.angle = random.uniform(0, math.pi)
        elif self.type == 2:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
            self.angle = random.uniform(-math.pi, 0)
        elif self.type == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.angle = random.uniform(-math.pi / 2, math.pi / 2)
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.angle = random.uniform(math.pi / 2, math.pi * 3 / 2)
        self.speedx = self.speed * math.cos(self.angle)
        self.speedy = self.speed * math.sin(self.angle)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            if not (-self.rect.width - (map_size / 2 - 0.5) * screen_width < self.abs_x < (map_size / 2 + 0.5) * screen_width and
                    -self.rect.height - (map_size / 2 - 0.5) * screen_height < self.abs_y < (map_size / 2 + 0.5) * screen_height):
                if self.abs_x <= -self.rect.width - (map_size / 2 - 0.5) * screen_width:
                    self.abs_x = (map_size / 2 + 0.5) * screen_width - 1
                elif self.abs_x >= (map_size / 2 + 0.5) * screen_width:
                    self.abs_x = -self.rect.width - (map_size / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -self.rect.height - (map_size / 2 - 0.5) * screen_height:
                    self.abs_y = (map_size / 2 + 0.5) * screen_height - 1
                else:
                    self.abs_y = -self.rect.height - (map_size / 2 - 0.5) * screen_height + 1
                self.speedx = self.speed * math.cos(self.angle)
                self.speedy = self.speed * math.sin(self.angle)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class MoveLineMob3(pygame.sprite.Sprite):
    """
    similar to MoveLineMob1, but has bigger size and higher hp
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = [80, 80]
        self.debris_size = 26
        self.debris_speed = random.randrange(14, 20)
        self.norm_image = linemob3_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = linemob3_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(2, 5)
        self.damage = 300
        self.hit = False
        self.hitcount = 0
        self.hp = 20
        self.hp_full = self.hp
        self.dead = False
        self.points = 180
        self.no_points = False
        self.type = random.randrange(1, 5)
        if self.type == 1:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
            self.angle = random.uniform(0, math.pi)
        elif self.type == 2:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
            self.angle = random.uniform(-math.pi, 0)
        elif self.type == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.angle = random.uniform(-math.pi / 2, math.pi / 2)
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.angle = random.uniform(math.pi / 2, math.pi * 3 / 2)
        self.speedx = self.speed * math.cos(self.angle)
        self.speedy = self.speed * math.sin(self.angle)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            if not (-self.rect.width - (map_size / 2 - 0.5) * screen_width < self.abs_x < (map_size / 2 + 0.5) * screen_width and
                    -self.rect.height - (map_size / 2 - 0.5) * screen_height < self.abs_y < (map_size / 2 + 0.5) * screen_height):
                if self.abs_x <= -self.rect.width - (map_size / 2 - 0.5) * screen_width:
                    self.abs_x = (map_size / 2 + 0.5) * screen_width - 1
                elif self.abs_x >= (map_size / 2 + 0.5) * screen_width:
                    self.abs_x = -self.rect.width - (map_size / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -self.rect.height - (map_size / 2 - 0.5) * screen_height:
                    self.abs_y = (map_size / 2 + 0.5) * screen_height - 1
                else:
                    self.abs_y = -self.rect.height - (map_size / 2 - 0.5) * screen_height + 1
                self.speedx = self.speed * math.cos(self.angle)
                self.speedy = self.speed * math.sin(self.angle)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class WallMobUnit1(pygame.sprite.Sprite):
    """
    the single unit of wall
    make up a large wall with themselves and move up, down, left or right
    wall-generating function is defined separately
    """
    def __init__(self, movetype, pos, speed):
        pygame.sprite.Sprite.__init__(self)
        self.unitsize = [40, 40]
        self.debris_size = 18
        self.debris_speed = random.randrange(10, 15)
        self.norm_image = wallmob1_img
        self.image = pygame.transform.scale(self.norm_image, self.unitsize)
        self.hit_anim = wallmob1_hit_anim
        self.rect = self.image.get_rect()
        self.pos = pos
        self.abs_x = self.pos[0]
        self.abs_y = self.pos[1]
        self.speed = speed
        self.damage = 13
        self.hit = False
        self.hitcount = 0
        self.hp = 2
        self.hp_full = self.hp
        self.dead = False
        self.points = 10
        self.no_points = False
        self.movetype = movetype
        if self.movetype == 1:
            self.speedx = 0
            self.speedy = self.speed
        elif self.movetype == 2:
            self.speedx = 0
            self.speedy = -self.speed
        elif self.movetype == 3:
            self.speedx = self.speed
            self.speedy = 0
        else:
            self.speedx = -self.speed
            self.speedy = 0
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.unitsize)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            if (self.movetype == 1 and self.abs_y > (map_size / 2 + 0.5) * screen_height + self.rect.height)\
                    or (self.movetype == 2 and self.abs_y < -self.rect.height * 2 - (map_size / 2 - 0.5) * screen_height)\
                    or (self.movetype == 3 and self.abs_x > (map_size / 2 + 0.5) * screen_width + self.rect.width)\
                    or (self.movetype == 4 and self.abs_x < -self.rect.width * 2 - (map_size / 2 - 0.5) * screen_width):
                self.kill()
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.unitsize[0] + self.unitsize[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.unitsize[0] * 1.5), round(self.unitsize[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class WallMobUnit2(pygame.sprite.Sprite):
    """
    similar to WallMobUnit1, but has bigger size or higher hp
    """
    def __init__(self, movetype, pos, speed):
        pygame.sprite.Sprite.__init__(self)
        self.unitsize = [40, 40]
        self.debris_size = 20
        self.debris_speed = random.randrange(10, 15)
        self.norm_image = wallmob2_img
        self.image = pygame.transform.scale(self.norm_image, self.unitsize)
        self.hit_anim = wallmob2_hit_anim
        self.rect = self.image.get_rect()
        self.pos = pos
        self.abs_x = self.pos[0]
        self.abs_y = self.pos[1]
        self.speed = speed
        self.damage = 27
        self.hit = False
        self.hitcount = 0
        self.hp = 3
        self.hp_full = self.hp
        self.dead = False
        self.points = 30
        self.no_points = False
        self.movetype = movetype
        if self.movetype == 1:
            self.speedx = 0
            self.speedy = self.speed
        elif self.movetype == 2:
            self.speedx = 0
            self.speedy = -self.speed
        elif self.movetype == 3:
            self.speedx = self.speed
            self.speedy = 0
        else:
            self.speedx = -self.speed
            self.speedy = 0
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.unitsize)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            if (self.movetype == 1 and self.abs_y > (map_size / 2 + 0.5) * screen_height + self.rect.height)\
                    or (self.movetype == 2 and self.abs_y < -self.rect.height * 2 - (map_size / 2 - 0.5) * screen_height)\
                    or (self.movetype == 3 and self.abs_x > (map_size / 2 + 0.5) * screen_width + self.rect.width)\
                    or (self.movetype == 4 and self.abs_x < -self.rect.width * 2 - (map_size / 2 - 0.5) * screen_width):
                self.kill()
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.unitsize[0] + self.unitsize[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.unitsize[0] * 1.5), round(self.unitsize[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class WallMobUnit3(pygame.sprite.Sprite):
    """
    similar to WallMobUnit1, but has bigger size or higher hp
    """
    def __init__(self, movetype, pos, speed):
        pygame.sprite.Sprite.__init__(self)
        self.unitsize = [70, 70]
        self.debris_size = 24
        self.debris_speed = random.randrange(14, 20)
        self.norm_image = wallmob3_img
        self.image = pygame.transform.scale(self.norm_image, self.unitsize)
        self.hit_anim = wallmob3_hit_anim
        self.rect = self.image.get_rect()
        self.pos = pos
        self.abs_x = self.pos[0]
        self.abs_y = self.pos[1]
        self.speed = speed
        self.damage = 155
        self.hit = False
        self.hitcount = 0
        self.hp = 8
        self.hp_full = self.hp
        self.dead = False
        self.points = 130
        self.no_points = False
        self.movetype = movetype
        if self.movetype == 1:
            self.speedx = 0
            self.speedy = self.speed
        elif self.movetype == 2:
            self.speedx = 0
            self.speedy = -self.speed
        elif self.movetype == 3:
            self.speedx = self.speed
            self.speedy = 0
        else:
            self.speedx = -self.speed
            self.speedy = 0
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.unitsize)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            if (self.movetype == 1 and self.abs_y > (map_size / 2 + 0.5) * screen_height + self.rect.height)\
                    or (self.movetype == 2 and self.abs_y < -self.rect.height * 2 - (map_size / 2 - 0.5) * screen_height)\
                    or (self.movetype == 3 and self.abs_x > (map_size / 2 + 0.5) * screen_width + self.rect.width)\
                    or (self.movetype == 4 and self.abs_x < -self.rect.width * 2 - (map_size / 2 - 0.5) * screen_width):
                self.kill()
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.unitsize[0] + self.unitsize[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.unitsize[0] * 1.5), round(self.unitsize[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


def generate_wall(max_size, unitsize, mobtype, wallmobs):
    """
    generates a 'x by y' rectangular wall with WallMobUnit defined above
    value x,y are set randomly
    :param max_size: max value of x, y
    :param unitsize: the size of a single WallMobUnit
    :param mobtype: defines which type of unit to make wall (WallMobUnit1, 2, or 3)
    :param wallmobs: sprite group of WallMobUnit
    :return: None
    """

    # make a list of all possible [x, y] pairs bounded to max_size
    x = 1
    y = 1
    gridsize_list = []
    while x <= max_size[0]:
        if x <= max_size[1]:
            while y <= max_size[0]:
                gridsize_list.append([x, y])
                y += 1
        else:
            while y <= max_size[1]:
                gridsize_list.append([x, y])
                y += 1
        y = 1
        x += 1

    gridsize = random.choice(gridsize_list)     # select a size randomly from gridsize_list
    wall_width = gridsize[0] * unitsize[0]      # size of wall in pixels
    wall_height = gridsize[1] * unitsize[1]

    # select move direction and set spawn position randomly
    movetype = random.randrange(1, 5)
    if movetype == 1:       # moves from top to bottom
        xpos = random.randrange(round(-(map_size / 2 - 0.5) * screen_width), (map_size / 2 + 0.5) * screen_width - wall_width)
        ypos = random.randrange(-wall_height * 2, -wall_height) - (map_size / 2 - 0.5) * screen_height
    elif movetype == 2:     # moves from bottom to top
        xpos = random.randrange(round(-(map_size / 2 - 0.5) * screen_width), (map_size / 2 + 0.5) * screen_width - wall_width)
        ypos = random.randrange(0, wall_height) + (map_size / 2 + 0.5) * screen_height
    elif movetype == 3:     # moves from left to right
        xpos = random.randrange(-wall_width * 2, -wall_width) - (map_size / 2 - 0.5) * screen_width
        ypos = random.randrange(round(-(map_size / 2 - 0.5) * screen_height), (map_size / 2 + 0.5) * screen_height - wall_height)
    else:                   # moves from right to left
        xpos = random.randrange(0, wall_width) + (map_size / 2 + 0.5) * screen_width
        ypos = random.randrange(round(-(map_size / 2 - 0.5) * screen_height), (map_size / 2 + 0.5) * screen_height - wall_height)

    # generating wall
    if mobtype == 1:
        speed = random.randrange(2, 8)
        for q in range(0, gridsize[1]):
            for p in range(0, gridsize[0]):
                if p != 0 or q != 0:
                    w = WallMobUnit1(movetype, [xpos + p * unitsize[0], ypos + q * unitsize[1]], speed)
                    all_sprites.add(w)
                    mobs.add(w)
                    all_mobs.add(w)
                    wallmobs.add(w)
                else:
                    firstunit = WallMobUnit1(movetype, [xpos + p * unitsize[0], ypos + q * unitsize[1]], speed)
                    all_sprites.add(firstunit)
                    mobs.add(firstunit)
                    all_mobs.add(firstunit)
                    wallmobs.add(firstunit)
    elif mobtype == 2:
        speed = random.randrange(4, 10)
        for q in range(0, gridsize[1]):
            for p in range(0, gridsize[0]):
                if p != 0 or q != 0:
                    w = WallMobUnit2(movetype, [xpos + p * unitsize[0], ypos + q * unitsize[1]], speed)
                    all_sprites.add(w)
                    mobs.add(w)
                    all_mobs.add(w)
                    wallmobs.add(w)
                else:
                    firstunit = WallMobUnit2(movetype, [xpos + p * unitsize[0], ypos + q * unitsize[1]], speed)
                    all_sprites.add(firstunit)
                    mobs.add(firstunit)
                    all_mobs.add(firstunit)
                    wallmobs.add(firstunit)
    elif mobtype == 3:
        speed = random.randrange(1, 5)
        for q in range(0, gridsize[1]):
            for p in range(0, gridsize[0]):
                if p != 0 or q != 0:
                    w = WallMobUnit3(movetype, [xpos + p * unitsize[0], ypos + q * unitsize[1]], speed)
                    all_sprites.add(w)
                    mobs.add(w)
                    all_mobs.add(w)
                    wallmobs.add(w)
                else:
                    firstunit = WallMobUnit3(movetype, [xpos + p * unitsize[0], ypos + q * unitsize[1]], speed)
                    all_sprites.add(firstunit)
                    mobs.add(firstunit)
                    all_mobs.add(firstunit)
                    wallmobs.add(firstunit)


class FollowerMob1(pygame.sprite.Sprite):
    """
    moves toward player with random speed
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = [100, 100]
        self.debris_size = 30
        self.debris_speed = random.randrange(10, 22)
        self.norm_image = followermob1_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = followermob1_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(1, 6)
        self.damage = 100
        self.hit = False
        self.hitcount = 0
        self.hp = 30
        self.hp_full = self.hp
        self.dead = False
        self.points = 400
        self.no_points = False
        self.type = random.randrange(1, 5)
        if self.type == 1:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
        elif self.type == 2:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
        elif self.type == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        self.speedx = self.speed * (player.rect.center[0] - self.rect.center[0]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
        self.speedy = self.speed * (player.rect.center[1] - self.rect.center[1]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.speedx = self.speed * (player.rect.center[0] - self.rect.center[0]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
            self.speedy = self.speed * (player.rect.center[1] - self.rect.center[1]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class FollowerMob2(pygame.sprite.Sprite):
    """
    similaar to FollowerMob1, but generates a number of small mobs when killed
    small mobs will be defined in a separate sprite class named "FollowerMob2Child"
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = [140, 140]
        self.debris_size = 30
        self.debris_speed = random.randrange(12, 25)
        self.norm_image = followermob2_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = followermob2_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(1, 3)
        self.damage = 145
        self.hit = False
        self.hitcount = 0
        self.hp = 150
        self.hp_full = self.hp
        self.dead = False
        self.points = 900
        self.no_points = False
        self.type = random.randrange(1, 5)
        if self.type == 1:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
        elif self.type == 2:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
        elif self.type == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        self.speedx = self.speed * (player.rect.center[0] - self.rect.center[0]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
        self.speedy = self.speed * (player.rect.center[1] - self.rect.center[1]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.speedx = self.speed * (player.rect.center[0] - self.rect.center[0]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
            self.speedy = self.speed * (player.rect.center[1] - self.rect.center[1]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            dist_x = player.rect.center[0] - self.rect.center[0]
            dist_y = player.rect.center[1] - self.rect.center[1]
            angle = math.atan2(dist_y, dist_x)
            for c in range(random.randrange(70, 80)):
                direction = random.uniform(angle + math.pi / 6, angle + math.pi * 11 / 6)
                child = FollowerMob2Child((random.randrange(self.rect.width / 2) + self.abs_x + self.rect.width / 4, random.randrange(self.rect.height / 2) + self.abs_y + self.rect.height / 4), direction)
                all_sprites.add(child)
                all_mobs.add(child)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class FollowerMob2Child(pygame.sprite.Sprite):
    """
    small mobs generated from FollowerMob2
    also move towards player,
    but the "acceleration" direction is set to player, not "speed" direction
    acceleration constant and max speed are set randomly
    """
    def __init__(self, abs_pos, direction):
        pygame.sprite.Sprite.__init__(self)
        self.size = [15, 15]
        self.debris_size = 10
        self.debris_speed = random.randrange(4, 8)
        self.norm_image = followermob2child_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = followermob2child_hit_anim
        self.rect = self.image.get_rect()
        self.dir = direction
        self.max_speed = random.uniform(7, 13)
        self.speed = random.uniform(0, self.max_speed)
        self.damage = 7
        self.hit = False
        self.hitcount = 0
        self.hp = 1
        self.hp_full = self.hp
        self.dead = False
        self.points = 15
        self.no_points = False
        self.abs_x = abs_pos[0]
        self.abs_y = abs_pos[1]
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        self.speedx = self.speed * math.cos(self.dir)
        self.speedy = self.speed * math.sin(self.dir)
        dist_x = player.rect.center[0] - self.rect.center[0]
        dist_y = player.rect.center[1] - self.rect.center[1]
        self.acc_dir = math.atan2(dist_y, dist_x)
        self.acc = random.uniform(0.2, 0.4)
        self.acc_x = self.acc * math.cos(self.acc_dir)
        self.acc_y = self.acc * math.sin(self.acc_dir)

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            dist_x = player.rect.center[0] - self.rect.center[0]
            dist_y = player.rect.center[1] - self.rect.center[1]
            self.acc_dir = math.atan2(dist_y, dist_x)
            self.acc_x = self.acc * math.cos(self.acc_dir)
            self.acc_y = self.acc * math.sin(self.acc_dir)
            self.speedx = min(self.speedx + self.acc_x, self.max_speed)
            self.speedy = min(self.speedy + self.acc_y, self.max_speed)
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class MinigunMob1(pygame.sprite.Sprite):
    """
    shoots a bullet to player periodically
    moves up, down, left, or right,
    but the direction can be changed with a specific probability in every frame
    the "movetype" attribute defines only initial move direction of the mob
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (70, 70)
        self.debris_size = 28
        self.debris_speed = random.randrange(13, 19)
        self.norm_image = minigunmob1_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = minigunmob1_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(2, 7)
        self.damage = 143
        self.hit = False
        self.hitcount = 0
        self.hp = 40
        self.hp_full = self.hp
        self.dead = False
        self.points = 384
        self.no_points = False
        self.shoot_interval = 4
        self.last_shoot = time.time()
        self.trigger = False
        self.power = 8
        self.movetype = random.randrange(1, 5)
        if self.movetype == 1:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
            self.speedx = 0
            self.speedy = self.speed
        elif self.movetype == 2:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
            self.speedx = 0
            self.speedy = -self.speed
        elif self.movetype == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.speedx = self.speed
            self.speedy = 0
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.speedx = -self.speed
            self.speedy = 0
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if random.random() <= 0.01:
                turn = random.choice(["l", "r"])
                if self.movetype == 1:
                    if turn == "l":
                        self.movetype = 3
                        self.speedx = self.speed
                        self.speedy = 0
                    else:
                        self.movetype = 4
                        self.speedx = -self.speed
                        self.speedy = 0
                elif self.movetype == 2:
                    if turn == "l":
                        self.movetype = 4
                        self.speedx = -self.speed
                        self.speedy = 0
                    else:
                        self.movetype = 3
                        self.speedx = self.speed
                        self.speedy = 0
                elif self.movetype == 3:
                    if turn == "l":
                        self.movetype = 2
                        self.speedx = 0
                        self.speedy = -self.speed
                    else:
                        self.movetype = 1
                        self.speedx = 0
                        self.speedy = self.speed
                else:
                    if turn == "l":
                        self.movetype = 1
                        self.speedx = 0
                        self.speedy = self.speed
                    else:
                        self.movetype = 2
                        self.speedx = 0
                        self.speedy = -self.speed
            if not (-self.rect.width - (map_size / 2 - 0.5) * screen_width < self.abs_x < (map_size / 2 + 0.5) * screen_width and
                    -self.rect.height - (map_size / 2 - 0.5) * screen_height < self.abs_y < (map_size / 2 + 0.5) * screen_height):
                if self.abs_x <= -self.rect.width - (map_size / 2 - 0.5) * screen_width:
                    self.abs_x = (map_size / 2 + 0.5) * screen_width - 1
                elif self.abs_x >= (map_size / 2 + 0.5) * screen_width:
                    self.abs_x = -self.rect.width - (map_size / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -self.rect.height - (map_size / 2 - 0.5) * screen_height:
                    self.abs_y = (map_size / 2 + 0.5) * screen_height - 1
                else:
                    self.abs_y = -self.rect.height - (map_size / 2 - 0.5) * screen_height + 1
            if time.time() - self.last_shoot > self.shoot_interval and not self.trigger:
                self.trigger = True
            if self.trigger:
                if -200 <= self.rect.center[0] <= screen_width + 200 and -200 <= self.rect.center[1] <= screen_height + 200:
                    dist_x = player.rect.center[0] - self.rect.center[0]
                    dist_y = player.rect.center[1] - self.rect.center[1]
                    angle = math.atan2(dist_y, dist_x)
                    bullet = MobBullet1(self.power, 8, self.rect.center, angle)
                    all_sprites.add(bullet)
                    mob_bullets.add(bullet)
                    self.trigger = False
                    self.last_shoot = time.time()
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class MinigunMob2(pygame.sprite.Sprite):
    """
    similar to MinigunMob1, but has larger size, slower speed and higher hp
    spreads multiple bullets at a time
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (100, 100)
        self.debris_size = 28
        self.debris_speed = random.randrange(15, 23)
        self.norm_image = minigunmob2_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = minigunmob2_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(2, 5)
        self.damage = 201
        self.hit = False
        self.hitcount = 0
        self.hp = 65
        self.hp_full = self.hp
        self.dead = False
        self.points = 497
        self.no_points = False
        self.bullets_per_shoot = 7
        self.current_bullets = self.bullets_per_shoot
        self.shoot_interval = 6
        self.first_shoot = random.uniform(0, self.shoot_interval)
        self.interval = self.first_shoot
        self.last_shoot = time.time()
        self.trigger = False
        self.power = 8
        self.movetype = random.randrange(1, 5)
        self.shoot_dir = 0
        self.shoot_angle = 0
        if self.movetype == 1:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
            self.speedx = 0
            self.speedy = self.speed
        elif self.movetype == 2:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
            self.speedx = 0
            self.speedy = -self.speed
        elif self.movetype == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.speedx = self.speed
            self.speedy = 0
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.speedx = -self.speed
            self.speedy = 0
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if random.random() <= 0.01:
                turn = random.choice(["l", "r"])
                if self.movetype == 1:
                    if turn == "l":
                        self.movetype = 3
                        self.speedx = self.speed
                        self.speedy = 0
                    else:
                        self.movetype = 4
                        self.speedx = -self.speed
                        self.speedy = 0
                elif self.movetype == 2:
                    if turn == "l":
                        self.movetype = 4
                        self.speedx = -self.speed
                        self.speedy = 0
                    else:
                        self.movetype = 3
                        self.speedx = self.speed
                        self.speedy = 0
                elif self.movetype == 3:
                    if turn == "l":
                        self.movetype = 2
                        self.speedx = 0
                        self.speedy = -self.speed
                    else:
                        self.movetype = 1
                        self.speedx = 0
                        self.speedy = self.speed
                else:
                    if turn == "l":
                        self.movetype = 1
                        self.speedx = 0
                        self.speedy = self.speed
                    else:
                        self.movetype = 2
                        self.speedx = 0
                        self.speedy = -self.speed
            if not (-self.rect.width - (map_size / 2 - 0.5) * screen_width < self.abs_x < (map_size / 2 + 0.5) * screen_width and
                    -self.rect.height - (map_size / 2 - 0.5) * screen_height < self.abs_y < (map_size / 2 + 0.5) * screen_height):
                if self.abs_x <= -self.rect.width - (map_size / 2 - 0.5) * screen_width:
                    self.abs_x = (map_size / 2 + 0.5) * screen_width - 1
                elif self.abs_x >= (map_size / 2 + 0.5) * screen_width:
                    self.abs_x = -self.rect.width - (map_size / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -self.rect.height - (map_size / 2 - 0.5) * screen_height:
                    self.abs_y = (map_size / 2 + 0.5) * screen_height - 1
                else:
                    self.abs_y = -self.rect.height - (map_size / 2 - 0.5) * screen_height + 1

            dist_x = player.rect.center[0] - self.rect.center[0]
            dist_y = player.rect.center[1] - self.rect.center[1]
            self.shoot_dir = math.atan2(dist_y, dist_x)

            if time.time() - self.last_shoot > self.interval and not self.trigger:
                self.interval = self.shoot_interval
                self.current_bullets = self.bullets_per_shoot
                self.trigger = True
                self.shoot_angle = self.shoot_dir - math.pi / 2
            if self.trigger:
                if -200 <= self.rect.center[0] <= screen_width + 200 and -200 <= self.rect.center[1] <= screen_height + 200:
                    bullet = Bullet(self.power, 8, [6, 6], RED1, self.rect.center, self.shoot_angle, True)
                    all_sprites.add(bullet)
                    mob_bullets.add(bullet)
                self.shoot_angle += math.pi / 6
                self.current_bullets -= 1
                if self.current_bullets <= 0:
                    self.trigger = False
                    self.last_shoot = time.time()
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class MinigunMob3(pygame.sprite.Sprite):
    """
    similar to MinigunMob1, but has larger size, slower speed and higher hp
    shoots a chain of bullets to multiple directions like a short laser blast
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (150, 150)
        self.debris_size = 33
        self.debris_speed = random.randrange(17, 24)
        self.norm_image = minigunmob3_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = minigunmob3_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(1, 3)
        self.damage = 457
        self.hit = False
        self.hitcount = 0
        self.hp = 100
        self.hp_full = self.hp
        self.dead = False
        self.points = 795
        self.no_points = False
        self.shoot_interval = 7
        self.first_shoot = random.uniform(0, self.shoot_interval)
        self.interval = self.first_shoot
        self.last_shoot = time.time()
        self.trigger = False
        self.power = 8
        self.shoot_angle = 0
        self.bullets_per_shoot = 10
        self.current_bullets = 0
        self.movetype = random.randrange(1, 5)
        if self.movetype == 1:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
            self.speedx = 0
            self.speedy = self.speed
        elif self.movetype == 2:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
            self.speedx = 0
            self.speedy = -self.speed
        elif self.movetype == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.speedx = self.speed
            self.speedy = 0
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.speedx = -self.speed
            self.speedy = 0
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if random.random() <= 0.01:
                turn = random.choice(["l", "r"])
                if self.movetype == 1:
                    if turn == "l":
                        self.movetype = 3
                        self.speedx = self.speed
                        self.speedy = 0
                    else:
                        self.movetype = 4
                        self.speedx = -self.speed
                        self.speedy = 0
                elif self.movetype == 2:
                    if turn == "l":
                        self.movetype = 4
                        self.speedx = -self.speed
                        self.speedy = 0
                    else:
                        self.movetype = 3
                        self.speedx = self.speed
                        self.speedy = 0
                elif self.movetype == 3:
                    if turn == "l":
                        self.movetype = 2
                        self.speedx = 0
                        self.speedy = -self.speed
                    else:
                        self.movetype = 1
                        self.speedx = 0
                        self.speedy = self.speed
                else:
                    if turn == "l":
                        self.movetype = 1
                        self.speedx = 0
                        self.speedy = self.speed
                    else:
                        self.movetype = 2
                        self.speedx = 0
                        self.speedy = -self.speed
            if not (-self.rect.width - (map_size / 2 - 0.5) * screen_width < self.abs_x < (map_size / 2 + 0.5) * screen_width and
                    -self.rect.height - (map_size / 2 - 0.5) * screen_height < self.abs_y < (map_size / 2 + 0.5) * screen_height):
                if self.abs_x <= -self.rect.width - (map_size / 2 - 0.5) * screen_width:
                    self.abs_x = (map_size / 2 + 0.5) * screen_width - 1
                elif self.abs_x >= (map_size / 2 + 0.5) * screen_width:
                    self.abs_x = -self.rect.width - (map_size / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -self.rect.height - (map_size / 2 - 0.5) * screen_height:
                    self.abs_y = (map_size / 2 + 0.5) * screen_height - 1
                else:
                    self.abs_y = -self.rect.height - (map_size / 2 - 0.5) * screen_height + 1

            if time.time() - self.last_shoot > self.interval and not self.trigger:
                self.interval = self.shoot_interval
                self.shoot_angle = random.uniform(0, math.pi / 4)
                self.current_bullets = 0
                self.trigger = True
            if self.trigger:
                if -200 <= self.rect.center[0] <= screen_width + 200 and -200 <= self.rect.center[1] <= screen_height + 200:
                    angle = 0
                    while angle < 2 * math.pi * 0.999:
                        bullet = Bullet(self.power, 13, [6, 6], RED1, self.rect.center, self.shoot_angle + angle, True)
                        all_sprites.add(bullet)
                        mob_bullets.add(bullet)
                        angle += math.pi / 4
                    self.current_bullets += 1
                    if self.current_bullets >= self.bullets_per_shoot:
                        self.trigger = False
                        self.last_shoot = time.time()
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class ShellMob1(pygame.sprite.Sprite):
    """
    protects itself with 4 rigid "shell"s(will be defined in a separate sprite class)
    can open or close shells
    attacks player with cannon ball when shells are opened
    moving pattern is same as MinigunMobs
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = [100, 100]
        self.debris_size = 25
        self.debris_speed = random.randrange(13, 20)
        self.norm_image = shellmob1_core_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = shellmob1_core_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(3, 7)
        self.damage = 437
        self.hit = False
        self.hitcount = 0
        self.hp = 45
        self.hp_full = self.hp
        self.dead = False
        self.points = 532
        self.no_points = False
        self.cannon_attack = False
        self.cannon_opened = False
        self.cannon_open_time = 0
        self.opened_time = 0
        self.shell_moved = 0
        self.fire_time = 0
        self.fire_interval = 0.6
        self.cannon_fired = False
        self.movetype = random.randrange(1, 5)
        if self.movetype == 1:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
            self.speedx = 0
            self.speedy = self.speed
        elif self.movetype == 2:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
            self.speedx = 0
            self.speedy = -self.speed
        elif self.movetype == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.speedx = self.speed
            self.speedy = 0
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.speedx = -self.speed
            self.speedy = 0
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        # shells for each direction
        self.shell1 = Shell1(1, self.rect.center)
        self.shell2 = Shell1(2, self.rect.center)
        self.shell3 = Shell1(3, self.rect.center)
        self.shell4 = Shell1(4, self.rect.center)
        self.shells = [self.shell1, self.shell2, self.shell3, self.shell4]
        self.in_map = False
        self.i = 0

    def update(self):
        if self.i == 0:
            all_mobs.add(self.shell1)
            all_mobs.add(self.shell2)
            all_mobs.add(self.shell3)
            all_mobs.add(self.shell4)
            self.i += 1
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if -(map_size / 2 - 0.5) * screen_width < self.abs_x < (map_size / 2 + 0.5) * screen_width - self.rect.width \
                    and -(map_size / 2 - 0.5) * screen_height < self.abs_y < (map_size / 2 + 0.5) * screen_height - self.rect.height:
                self.in_map = True
            if self.in_map:
                if self.abs_x <= -(map_size / 2 - 0.5) * screen_width or self.abs_x >= (
                        map_size / 2 + 0.5) * screen_width - self.rect.width:
                    if self.movetype == 2:
                        self.movetype = 4
                    elif self.movetype == 4:
                        self.movetype = 2
                    self.speedx = -self.speedx
                elif self.abs_y <= -(map_size / 2 - 0.5) * screen_height or self.abs_y >= (
                        map_size / 2 + 0.5) * screen_height - self.rect.height:
                    if self.movetype == 1:
                        self.movetype = 3
                    elif self.movetype == 3:
                        self.movetype = 1
                    self.speedy = -self.speedy
                if random.random() <= 0.01:
                    turn = random.choice(["l", "r"])
                    if self.movetype == 1:
                        if turn == "l":
                            self.movetype = 3
                            self.speedx = self.speed
                            self.speedy = 0
                        else:
                            self.movetype = 4
                            self.speedx = -self.speed
                            self.speedy = 0
                    elif self.movetype == 2:
                        if turn == "l":
                            self.movetype = 4
                            self.speedx = -self.speed
                            self.speedy = 0
                        else:
                            self.movetype = 3
                            self.speedx = self.speed
                            self.speedy = 0
                    elif self.movetype == 3:
                        if turn == "l":
                            self.movetype = 2
                            self.speedx = 0
                            self.speedy = -self.speed
                        else:
                            self.movetype = 1
                            self.speedx = 0
                            self.speedy = self.speed
                    else:
                        if turn == "l":
                            self.movetype = 1
                            self.speedx = 0
                            self.speedy = self.speed
                        else:
                            self.movetype = 2
                            self.speedx = 0
                            self.speedy = -self.speed
            if not self.cannon_attack:
                self.abs_x += self.speedx
                self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])

            if not self.cannon_attack and random.random() < 0.003:
                self.cannon_attack = True
                self.cannon_opened = False
                self.shell_moved = 0
                self.cannon_open_time = random.uniform(0, 4)
            if self.cannon_attack:
                if not self.cannon_opened:
                    self.shell_moved += 1
                    for s in self.shells:
                        if not s.dead:
                            if s.shellnum == 1:
                                s.update([self.rect.center[0] - self.shell_moved, self.rect.center[1] - self.shell_moved])
                            elif s.shellnum == 2:
                                s.update([self.rect.center[0] + self.shell_moved, self.rect.center[1] - self.shell_moved])
                            elif s.shellnum == 3:
                                s.update([self.rect.center[0] - self.shell_moved, self.rect.center[1] + self.shell_moved])
                            elif s.shellnum == 4:
                                s.update([self.rect.center[0] + self.shell_moved, self.rect.center[1] + self.shell_moved])
                    if self.shell_moved == 30:
                        self.cannon_opened = True
                        self.opened_time = time.time()
                        self.fire_time = time.time()

                if self.cannon_opened:
                    for s in self.shells:
                        if not s.dead:
                            if s.shellnum == 1:
                                s.update([self.rect.center[0] - self.shell_moved, self.rect.center[1] - self.shell_moved])
                            elif s.shellnum == 2:
                                s.update([self.rect.center[0] + self.shell_moved, self.rect.center[1] - self.shell_moved])
                            elif s.shellnum == 3:
                                s.update([self.rect.center[0] - self.shell_moved, self.rect.center[1] + self.shell_moved])
                            elif s.shellnum == 4:
                                s.update([self.rect.center[0] + self.shell_moved, self.rect.center[1] + self.shell_moved])
                    if not self.cannon_fired:
                        if time.time() - self.fire_time >= self.fire_interval:
                            if -200 <= self.rect.center[0] <= screen_width + 200 and -200 <= self.rect.center[1] <= screen_height + 200:
                                dist_x = player.rect.center[0] - self.rect.center[0]
                                dist_y = player.rect.center[1] - self.rect.center[1]
                                angle = math.atan2(dist_y, dist_x) + random.uniform(-math.pi / 9, math.pi / 9)
                                cannonball = MobCannonBall1(self.rect.center, angle, 47, 12)
                                all_sprites.add(cannonball)
                                mob_cannon_balls.add(cannonball)
                            expl_type = random.randrange(1, 12)
                            expl = Explosion(self.rect.center, expl_type, (round(self.size[0]), round(self.size[1])))
                            all_sprites.add(expl)
                            explosions.add(expl)
                            self.fire_time = time.time()
                        if time.time() - self.opened_time >= self.cannon_open_time:
                            self.cannon_fired = True
                            self.cannon_opened = False

                if self.cannon_fired:
                    self.shell_moved -= 1
                    for s in self.shells:
                        if not s.dead:
                            if s.shellnum == 1:
                                s.update([self.rect.center[0] - self.shell_moved, self.rect.center[1] - self.shell_moved])
                            elif s.shellnum == 2:
                                s.update([self.rect.center[0] + self.shell_moved, self.rect.center[1] - self.shell_moved])
                            elif s.shellnum == 3:
                                s.update([self.rect.center[0] - self.shell_moved, self.rect.center[1] + self.shell_moved])
                            elif s.shellnum == 4:
                                s.update([self.rect.center[0] + self.shell_moved, self.rect.center[1] + self.shell_moved])
                    if self.shell_moved == 0:
                        self.cannon_fired = False
                        self.cannon_attack = False
            else:
                for s in self.shells:
                    if not s.dead:
                        s.update(self.rect.center)

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if len(self.shells) <= 0:
                if random.random() <= 0.02:
                    item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                    all_sprites.add(item)
                    items.add(item)
                expl_type = random.randrange(1, 12)
                expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
                all_sprites.add(expl)
                explosions.add(expl)
                self.kill()
            for s in self.shells:
                if not s.dead:
                    s.dead = True
                    s.update(self.rect.center)
            self.shells = []


class Shell1(pygame.sprite.Sprite):
    """
    shell sprite for ShellMob1 class
    """
    def __init__(self, shellnum, pos):
        pygame.sprite.Sprite.__init__(self)
        self.size = [70, 70]
        self.debris_size = 15
        self.debris_speed = random.randrange(12, 18)
        self.norm_image = shellmob1_shell_img[shellnum - 1][1]
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = shellmob1_shell_img[shellnum - 1]
        self.rect = self.image.get_rect()
        self.damage = 176
        self.hit = False
        self.hitcount = 0
        self.hp = 50
        self.hp_full = self.hp
        self.dead = False
        self.points = 132
        self.no_points = False
        self.shellnum = shellnum
        if self.shellnum == 1:
            self.abs_x = pos[0] - self.size[0]
            self.abs_y = pos[1] - self.size[1]
        elif self.shellnum == 2:
            self.abs_x = pos[0]
            self.abs_y = pos[1] - self.size[0]
        elif self.shellnum == 3:
            self.abs_x = pos[0] - self.size[1]
            self.abs_y = pos[1]
        elif self.shellnum == 4:
            self.abs_x = pos[0]
            self.abs_y = pos[1]

    def update(self, pos=(0, 0)):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            if self.shellnum == 1:
                self.abs_x = pos[0] - self.size[0]
                self.abs_y = pos[1] - self.size[1]
            if self.shellnum == 2:
                self.abs_x = pos[0]
                self.abs_y = pos[1] - self.size[0]
            if self.shellnum == 3:
                self.abs_x = pos[0] - self.size[1]
                self.abs_y = pos[1]
            if self.shellnum == 4:
                self.abs_x = pos[0]
                self.abs_y = pos[1]
            self.rect.x = self.abs_x
            self.rect.y = self.abs_y
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class ShellMob2(pygame.sprite.Sprite):
    """
    similar to ShellMob1, but its shells move in different direction
    and shoots cannon ball in different direction
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = [100, 100]
        self.debris_size = 25
        self.debris_speed = random.randrange(13, 20)
        self.norm_image = shellmob2_core_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = shellmob2_core_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(7, 11)
        self.damage = 513
        self.hit = False
        self.hitcount = 0
        self.hp = 65
        self.hp_full = self.hp
        self.dead = False
        self.points = 754
        self.no_points = False
        self.cannon_attack = False
        self.cannon_opened = False
        self.cannon_open_time = 0
        self.opened_time = 0
        self.shell_moved = 0
        self.fire_time = 0
        self.fire_interval = 0.1
        self.cannon_fired = False
        self.movetype = random.randrange(1, 5)
        if self.movetype == 1:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
            self.speedx = 0
            self.speedy = self.speed
        elif self.movetype == 2:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
            self.speedx = 0
            self.speedy = -self.speed
        elif self.movetype == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.speedx = self.speed
            self.speedy = 0
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
            self.speedx = -self.speed
            self.speedy = 0
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        # shells for each direction
        self.shell1 = Shell2(1, self.rect.center)
        self.shell2 = Shell2(2, self.rect.center)
        self.shell3 = Shell2(3, self.rect.center)
        self.shell4 = Shell2(4, self.rect.center)
        self.shells = [self.shell1, self.shell2, self.shell3, self.shell4]
        self.in_map = False
        self.i = 0

    def update(self):
        if self.i == 0:
            all_mobs.add(self.shell1)
            all_mobs.add(self.shell2)
            all_mobs.add(self.shell3)
            all_mobs.add(self.shell4)
            self.i += 1
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if -(map_size / 2 - 0.5) * screen_width < self.abs_x < (map_size / 2 + 0.5) * screen_width - self.rect.width \
                    and -(map_size / 2 - 0.5) * screen_height < self.abs_y < (map_size / 2 + 0.5) * screen_height - self.rect.height:
                self.in_map = True
            if self.in_map:
                if self.abs_x <= -(map_size / 2 - 0.5) * screen_width or self.abs_x >= (
                        map_size / 2 + 0.5) * screen_width - self.rect.width:
                    if self.movetype == 2:
                        self.movetype = 4
                    elif self.movetype == 4:
                        self.movetype = 2
                    self.speedx = -self.speedx
                elif self.abs_y <= -(map_size / 2 - 0.5) * screen_height or self.abs_y >= (
                        map_size / 2 + 0.5) * screen_height - self.rect.height:
                    if self.movetype == 1:
                        self.movetype = 3
                    elif self.movetype == 3:
                        self.movetype = 1
                    self.speedy = -self.speedy
                if random.random() <= 0.007:
                    turn = random.choice(["l", "r"])
                    if self.movetype == 1:
                        if turn == "l":
                            self.movetype = 3
                            self.speedx = self.speed
                            self.speedy = 0
                        else:
                            self.movetype = 4
                            self.speedx = -self.speed
                            self.speedy = 0
                    elif self.movetype == 2:
                        if turn == "l":
                            self.movetype = 4
                            self.speedx = -self.speed
                            self.speedy = 0
                        else:
                            self.movetype = 3
                            self.speedx = self.speed
                            self.speedy = 0
                    elif self.movetype == 3:
                        if turn == "l":
                            self.movetype = 2
                            self.speedx = 0
                            self.speedy = -self.speed
                        else:
                            self.movetype = 1
                            self.speedx = 0
                            self.speedy = self.speed
                    else:
                        if turn == "l":
                            self.movetype = 1
                            self.speedx = 0
                            self.speedy = self.speed
                        else:
                            self.movetype = 2
                            self.speedx = 0
                            self.speedy = -self.speed
            if not self.cannon_attack:
                self.abs_x += self.speedx
                self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])

            if not self.cannon_attack and random.random() < 0.003:
                self.cannon_attack = True
                self.cannon_opened = False
                self.shell_moved = 0
                self.cannon_open_time = random.uniform(0, 1)
            if self.cannon_attack:
                if not self.cannon_opened:
                    self.shell_moved += 1
                    for s in self.shells:
                        if not s.dead:
                            if s.shellnum == 1:
                                s.update([self.rect.center[0], self.rect.center[1] - self.shell_moved])
                            elif s.shellnum == 2:
                                s.update([self.rect.center[0] - self.shell_moved, self.rect.center[1]])
                            elif s.shellnum == 3:
                                s.update([self.rect.center[0], self.rect.center[1] + self.shell_moved])
                            elif s.shellnum == 4:
                                s.update([self.rect.center[0] + self.shell_moved, self.rect.center[1]])
                    if self.shell_moved == 20:
                        self.cannon_opened = True
                        self.opened_time = time.time()
                        self.fire_time = time.time()

                if self.cannon_opened:
                    for s in self.shells:
                        if not s.dead:
                            if s.shellnum == 1:
                                s.update([self.rect.center[0], self.rect.center[1] - self.shell_moved])
                            elif s.shellnum == 2:
                                s.update([self.rect.center[0] - self.shell_moved, self.rect.center[1]])
                            elif s.shellnum == 3:
                                s.update([self.rect.center[0], self.rect.center[1] + self.shell_moved])
                            elif s.shellnum == 4:
                                s.update([self.rect.center[0] + self.shell_moved, self.rect.center[1]])
                    if not self.cannon_fired:
                        if time.time() - self.fire_time >= self.fire_interval:
                            if -200 <= self.rect.center[0] <= screen_width + 200 and -200 <= self.rect.center[1] <= screen_height + 200:
                                angle = -math.pi * 3 / 4
                                for ang in range(4):
                                    cannonball = MobCannonBall1(self.rect.center, angle + ang * math.pi / 2, 55, 20)
                                    all_sprites.add(cannonball)
                                    mob_cannon_balls.add(cannonball)
                            expl_type = random.randrange(1, 12)
                            expl = Explosion(self.rect.center, expl_type, (round(self.size[0]), round(self.size[1])))
                            all_sprites.add(expl)
                            explosions.add(expl)
                            self.fire_time = time.time()
                        if time.time() - self.opened_time >= self.cannon_open_time:
                            self.cannon_fired = True
                            self.cannon_opened = False

                if self.cannon_fired:
                    self.shell_moved -= 1
                    for s in self.shells:
                        if not s.dead:
                            if s.shellnum == 1:
                                s.update([self.rect.center[0], self.rect.center[1] - self.shell_moved])
                            elif s.shellnum == 2:
                                s.update([self.rect.center[0] - self.shell_moved, self.rect.center[1]])
                            elif s.shellnum == 3:
                                s.update([self.rect.center[0], self.rect.center[1] + self.shell_moved])
                            elif s.shellnum == 4:
                                s.update([self.rect.center[0] + self.shell_moved, self.rect.center[1]])
                    if self.shell_moved == 0:
                        self.cannon_fired = False
                        self.cannon_attack = False
            else:
                for s in self.shells:
                    if not s.dead:
                        s.update(self.rect.center)

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if len(self.shells) <= 0:
                if random.random() <= 0.02:
                    item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                    all_sprites.add(item)
                    items.add(item)
                expl_type = random.randrange(1, 12)
                expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
                all_sprites.add(expl)
                explosions.add(expl)
                self.kill()
            for s in self.shells:
                if not s.dead:
                    s.dead = True
                    s.update(self.rect.center)
            self.shells = []


class Shell2(pygame.sprite.Sprite):
    """
    shell sprite for ShellMob2 class
    """
    def __init__(self, shellnum, pos):
        pygame.sprite.Sprite.__init__(self)
        self.shellnum = shellnum
        if self.shellnum == 1:
            self.size = [150, 50]
            self.abs_x = pos[0] - self.size[0] // 2
            self.abs_y = pos[1] - self.size[0] // 2
        elif self.shellnum == 2:
            self.size = [50, 150]
            self.abs_x = pos[0] - self.size[1] // 2
            self.abs_y = pos[1] - self.size[1] // 2
        elif self.shellnum == 3:
            self.size = [150, 50]
            self.abs_x = pos[0] - self.size[0] // 2
            self.abs_y = pos[1] + self.size[0] // 2 - self.size[1]
        elif self.shellnum == 4:
            self.size = [50, 150]
            self.abs_x = pos[0] + self.size[1] // 2 - self.size[0]
            self.abs_y = pos[1] - self.size[1] // 2
        self.debris_size = 15
        self.debris_speed = random.randrange(12, 18)
        self.norm_image = shellmob2_shell_img[shellnum - 1][1]
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = shellmob2_shell_img[shellnum - 1]
        self.rect = self.image.get_rect()
        self.damage = 132
        self.hit = False
        self.hitcount = 0
        self.hp = 60
        self.hp_full = self.hp
        self.dead = False
        self.points = 105
        self.no_points = False

    def update(self, pos=(0, 0)):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            if self.shellnum == 1:
                self.abs_x = pos[0] - self.size[0] // 2
                self.abs_y = pos[1] - self.size[0] // 2
            elif self.shellnum == 2:
                self.abs_x = pos[0] - self.size[1] // 2
                self.abs_y = pos[1] - self.size[1] // 2
            elif self.shellnum == 3:
                self.abs_x = pos[0] - self.size[0] // 2
                self.abs_y = pos[1] + self.size[0] // 2 - self.size[1]
            elif self.shellnum == 4:
                self.abs_x = pos[0] + self.size[1] // 2 - self.size[0]
                self.abs_y = pos[1] - self.size[1] // 2
            self.rect.x = self.abs_x
            self.rect.y = self.abs_y
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl_size = max(self.size)
            expl = Explosion(self.rect.center, expl_type, (round(expl_size * 1.5), round(expl_size * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class BossLV1(pygame.sprite.Sprite):
    """
    stage 1 boss
    similar to MoveLineMobs, but has very large size, very low speed, very high hp
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (200, 200)
        self.debris_size = 40
        self.debris_speed = 25
        self.norm_image = boss_lv1_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = boss_lv1_hit_anim
        self.rect = self.image.get_rect()
        self.speed = 2
        self.damage = 5000
        self.hit = False
        self.hitcount = 0
        self.hp = 300
        self.hp_full = 300
        self.dead = False
        self.points = 5000
        self.no_points = False
        self.type = random.randrange(1, 5)
        if self.type == 1:
            self.abs_x = random.randrange(-(map_size / 2 - 0.5) * screen_width + self.rect.width,
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width * 2)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
            self.angle = random.uniform(math.pi / 4, math.pi * 3 / 4)
        elif self.type == 2:
            self.abs_x = random.randrange(-(map_size / 2 - 0.5) * screen_width + self.rect.width,
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width * 2)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
            self.angle = random.uniform(-math.pi * 3 / 4, -math.pi / 4)
        elif self.type == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(-(map_size / 2 - 0.5) * screen_height + self.rect.height,
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height * 2)
            self.angle = random.uniform(-math.pi / 4, math.pi / 4)
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(-(map_size / 2 - 0.5) * screen_height + self.rect.height,
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height * 2)
            self.angle = random.uniform(math.pi * 3 / 4, math.pi * 5 / 4)
        self.speedx = self.speed * math.cos(self.angle)
        self.speedy = self.speed * math.sin(self.angle)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        self.in_map = False

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            if -(map_size / 2 - 0.5) * screen_width < self.abs_x < (map_size / 2 + 0.5) * screen_width - self.rect.width \
                    and -(map_size / 2 - 0.5) * screen_height < self.abs_y < (map_size / 2 + 0.5) * screen_height - self.rect.height:
                self.in_map = True
            if self.in_map:
                if self.abs_x <= -(map_size / 2 - 0.5) * screen_width or self.abs_x >= (map_size / 2 + 0.5) * screen_width - self.rect.width:
                    self.speedx = -self.speedx
                elif self.abs_y <= -(map_size / 2 - 0.5) * screen_height or self.abs_y >= (map_size / 2 + 0.5) * screen_height - self.rect.height:
                    self.speedy = -self.speedy
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "upgrade weapon")
            all_sprites.add(item)
            items.add(item)
            for e in range(random.randrange(5, 8)):
                expl_type = random.randrange(1, 12)
                expl = Explosion((random.randrange(self.rect.width) + self.rect.x, random.randrange(self.rect.height) + self.rect.y), expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
                all_sprites.add(expl)
                explosions.add(expl)
            global stage1_clear, stage1_boss_spawned, now_break_1, break_start, phase_text
            stage1_clear = True
            stage1_boss_spawned = False
            pointer.kill()
            for m in mobs:
                if random.random() < 0.7:
                    m.dead = True
            now_break_1 = True
            break_start = time.time()
            phase_text = "{}s BREAKTIME".format(breaktime)
            self.kill()


class BossLV2(pygame.sprite.Sprite):
    """
    stage 2 boss
    similar to FollowerMob, but has 3 layers of shield
    each shield is made up of "FollowerMobShieldUnit", which will be defined later
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (200, 200)
        self.debris_size = 35
        self.debris_speed = 28
        self.norm_image = boss_lv2_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = boss_lv2_hit_anim
        self.rect = self.image.get_rect()
        self.speed = 2
        self.damage = 7500
        self.hit = False
        self.hitcount = 0
        self.hp = 500
        self.hp_full = 500
        self.dead = False
        self.points = 7500
        self.no_points = False
        self.type = random.randrange(1, 5)
        if self.type == 1:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
        elif self.type == 2:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
        elif self.type == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        self.speedx = self.speed * (player.rect.center[0] - self.rect.center[0]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
        self.speedy = self.speed * (player.rect.center[1] - self.rect.center[1]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
        self.shield_group = pygame.sprite.Group()
        generate_shield((self.rect.x, self.rect.y), self.size, 5, (30, 30), (10, 10), 8, random.randrange(6, 13), shieldunit1_img, shieldunit1_hit_anim, 6, 2, 20, self.shield_group)
        generate_shield((self.rect.x, self.rect.y), self.size, 1, (8, 8), (50, 50), 20, random.randrange(10, 18), shieldunit2_img, shieldunit2_hit_anim, 110, 25, 200, self.shield_group)
        generate_shield((self.rect.x, self.rect.y), self.size, 3, (26, 26), (20, 20), 14, random.randrange(8, 16), shieldunit3_img, shieldunit3_hit_anim, 25, 10, 100, self.shield_group)

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.speedx = self.speed * (player.rect.center[0] - self.rect.center[0]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
            self.speedy = self.speed * (player.rect.center[1] - self.rect.center[1]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            self.shield_group.update((self.rect.x, self.rect.y))
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "upgrade weapon")
            all_sprites.add(item)
            items.add(item)
            for e in range(random.randrange(5, 8)):
                expl_type = random.randrange(1, 12)
                expl = Explosion((random.randrange(self.rect.width) + self.rect.x, random.randrange(self.rect.height) + self.rect.y), expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
                all_sprites.add(expl)
                explosions.add(expl)
            for s in self.shield_group:
                s.dead = True
            self.shield_group.update((self.rect.x, self.rect.y))
            global stage2_clear, stage2_boss_spawned, now_break_2, break_start, phase_text
            stage2_clear = True
            stage2_boss_spawned = False
            pointer.kill()
            for m in mobs:
                if random.random() < 0.7:
                    m.dead = True
            now_break_2 = True
            break_start = time.time()
            phase_text = "{}s BREAKTIME".format(breaktime)
            self.kill()


class BossLV3(pygame.sprite.Sprite):
    """
    stage 3 boss
    similar to MinigunMobs, but has 2 attack patterns: spiral, laser
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (400, 400)
        self.debris_size = 40
        self.debris_speed = 32
        self.norm_image = boss_lv3_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = boss_lv3_hit_anim
        self.rect = self.image.get_rect()
        self.speed = 3
        self.damage = 12000
        self.hit = False
        self.hitcount = 0
        self.hp = 3000
        self.hp_full = 3000
        self.dead = False
        self.points = 12500
        self.no_points = False
        self.minigun_attack = False
        self.attack_mode = 1
        self.now_shoot = True
        self.shoot_angle = 0
        self.bullets_per_shoot = 150
        self.current_bullets = self.bullets_per_shoot
        self.movetype = random.randrange(1, 5)
        if self.movetype == 1:
            self.abs_x = screen_width // 2 - self.size[0] // 2
            self.abs_y = -(map_size / 2 - 0.5) * screen_height - self.rect.height
            self.speedx = 0
            self.speedy = self.speed
        elif self.movetype == 2:
            self.abs_x = screen_width // 2 - self.size[0] // 2
            self.abs_y = (map_size / 2 + 0.5) * screen_height
            self.speedx = 0
            self.speedy = -self.speed
        elif self.movetype == 3:
            self.abs_x = -(map_size / 2 - 0.5) * screen_width - self.rect.width
            self.abs_y = screen_height // 2 - self.size[1] // 2
            self.speedx = self.speed
            self.speedy = 0
        else:
            self.abs_x = (map_size / 2 + 0.5) * screen_width
            self.abs_y = screen_height // 2 - self.size[1] // 2
            self.speedx = -self.speed
            self.speedy = 0
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        self.in_map = False

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            else:
                self.image = pygame.transform.scale(self.norm_image, self.size)

            if -(map_size / 2 - 0.5) * screen_width < self.abs_x < (map_size / 2 + 0.5) * screen_width - self.rect.width \
                    and -(map_size / 2 - 0.5) * screen_height < self.abs_y < (map_size / 2 + 0.5) * screen_height - self.rect.height:
                self.in_map = True
            if self.in_map:
                if self.abs_x <= -(map_size / 2 - 0.5) * screen_width or self.abs_x >= (
                        map_size / 2 + 0.5) * screen_width - self.rect.width:
                    self.speedx = -self.speedx
                elif self.abs_y <= -(map_size / 2 - 0.5) * screen_height or self.abs_y >= (
                        map_size / 2 + 0.5) * screen_height - self.rect.height:
                    self.speedy = -self.speedy
                if random.random() <= 0.005:
                    turn = random.choice(["l", "r"])
                    if self.movetype == 1:
                        if turn == "l":
                            self.movetype = 3
                            self.speedx = self.speed
                            self.speedy = 0
                        else:
                            self.movetype = 4
                            self.speedx = -self.speed
                            self.speedy = 0
                    elif self.movetype == 2:
                        if turn == "l":
                            self.movetype = 4
                            self.speedx = -self.speed
                            self.speedy = 0
                        else:
                            self.movetype = 3
                            self.speedx = self.speed
                            self.speedy = 0
                    elif self.movetype == 3:
                        if turn == "l":
                            self.movetype = 2
                            self.speedx = 0
                            self.speedy = -self.speed
                        else:
                            self.movetype = 1
                            self.speedx = 0
                            self.speedy = self.speed
                    else:
                        if turn == "l":
                            self.movetype = 1
                            self.speedx = 0
                            self.speedy = self.speed
                        else:
                            self.movetype = 2
                            self.speedx = 0
                            self.speedy = -self.speed
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])

            if not self.minigun_attack and random.random() < 0.005:
                self.minigun_attack = True
                if random.random() < 0.5:
                    self.attack_mode = 1
                    self.shoot_angle = 0
                else:
                    self.attack_mode = 2
                    self.current_bullets = self.bullets_per_shoot
            elif self.minigun_attack:
                if self.attack_mode == 1:
                    if self.shoot_angle <= 1800:
                        bullet = Bullet(13, 11.7, (7, 7), RED1, self.rect.center, self.shoot_angle * math.pi / 180, True)
                        all_sprites.add(bullet)
                        mob_bullets.add(bullet)
                        bullet = Bullet(13, 11.7, (7, 7), RED1, self.rect.center, (self.shoot_angle + 180) * math.pi / 180, True)
                        all_sprites.add(bullet)
                        mob_bullets.add(bullet)
                        self.shoot_angle += 13
                    else:
                        self.minigun_attack = False
                elif self.attack_mode == 2:
                    dist_x = player.rect.center[0] - self.rect.center[0]
                    dist_y = player.rect.center[1] - self.rect.center[1]
                    angle = math.atan2(dist_y, dist_x)
                    x = self.rect.center[0]
                    y = self.rect.center[1]
                    bullet = Bullet(13, 25, (7, 7), RED1, [x, y], angle, True)
                    all_sprites.add(bullet)
                    mob_bullets.add(bullet)
                    bullet = Bullet(13, 25, (7, 7), RED1, [x + 20, y], angle, True)
                    all_sprites.add(bullet)
                    mob_bullets.add(bullet)
                    bullet = Bullet(13, 25, (7, 7), RED1, [x - 20, y], angle, True)
                    all_sprites.add(bullet)
                    mob_bullets.add(bullet)
                    bullet = Bullet(13, 25, (7, 7), RED1, [x, y + 20], angle, True)
                    all_sprites.add(bullet)
                    mob_bullets.add(bullet)
                    bullet = Bullet(13, 25, (7, 7), RED1, [x, y - 20], angle, True)
                    all_sprites.add(bullet)
                    mob_bullets.add(bullet)
                    self.current_bullets -= 1
                    if self.current_bullets <= 0:
                        self.minigun_attack = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt,
                      self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]],
                        "upgrade weapon")
            all_sprites.add(item)
            items.add(item)
            for e in range(random.randrange(20, 25)):
                expl_type = random.randrange(1, 12)
                expl = Explosion((random.randrange(self.rect.width) + self.rect.x,
                                  random.randrange(self.rect.height) + self.rect.y), expl_type,
                                 (round(self.size[0]), round(self.size[1])))
                all_sprites.add(expl)
                explosions.add(expl)
            global stage3_clear, stage3_boss_spawned, now_break_3, break_start, phase_text
            stage3_clear = True
            stage3_boss_spawned = False
            pointer.kill()
            for m in mobs:
                if random.random() < 0.7:
                    m.dead = True
            now_break_3 = True
            break_start = time.time()
            phase_text = "{}s BREAKTIME".format(breaktime)
            self.kill()

    def generate_mobs(self):
        pass


class BossLV4(pygame.sprite.Sprite):
    """
    stage 4 boss
    moves toward player
    protected by 12 shells
    3 attack patterns: cannon, generating child mobs, boosting
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (300, 300)
        self.debris_size = 35
        self.debris_speed = 29
        self.norm_image = boss_lv4_core_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = boss_lv4_core_hit_anim
        self.rect = self.image.get_rect()
        self.speed_orig = 3
        self.speed_boost = 30
        self.boost_acc = self.speed_boost / 100
        self.boost_accx = 0
        self.boost_accy = 0
        self.speed = self.speed_orig
        self.damage = 18000
        self.hit = False
        self.hitcount = 0
        self.hp = 1500
        self.hp_full = self.hp
        self.dead = False
        self.points = 20000
        self.no_points = False
        self.cannon_interval = 0.7
        self.cannon_fired = time.time()
        self.attack_mode = "childs"
        self.attack_num = 4
        self.attacked = 0
        self.attack = True
        self.last_attacked = time.time()
        self.shell_opened = False
        self.shell_open_time = 0
        self.opened_time = 0
        self.shell_moved = 0
        self.attack_finished = False
        self.attack_childs = pygame.sprite.Group()
        self.shield_childs = pygame.sprite.Group()
        self.boost_dir = 0
        self.reflected = False
        self.shell_sel = [0] * 12
        self.type = random.randrange(1, 5)
        if self.type == 1:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (map_size / 2 - 0.5) * screen_height
        elif self.type == 2:
            self.abs_x = random.randrange(round(-(map_size / 2 - 0.5) * screen_width),
                                          (map_size / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (map_size / 2 + 0.5) * screen_height - self.rect.height
        elif self.type == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (map_size / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (map_size / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(map_size / 2 - 0.5) * screen_height),
                                          (map_size / 2 + 0.5) * screen_height - self.rect.height)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        self.speedx = self.speed * (player.rect.center[0] - self.rect.center[0]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
        self.speedy = self.speed * (player.rect.center[1] - self.rect.center[1]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
        self.in_map = False
        self.shell1 = BossLV4Shell([200, 200], 1, 600, self.rect.center)
        self.shell2 = BossLV4Shell([200, 200], 2, 600, self.rect.center)
        self.shell3 = BossLV4Shell([200, 200], 3, 600, self.rect.center)
        self.shell4 = BossLV4Shell([200, 200], 4, 600, self.rect.center)
        self.shell5 = BossLV4Shell([89, 178], 5, 400, self.rect.center)
        self.shell6 = BossLV4Shell([178, 178], 6, 500, self.rect.center)
        self.shell7 = BossLV4Shell([178, 89], 7, 400, self.rect.center)
        self.shell8 = BossLV4Shell([178, 178], 8, 500, self.rect.center)
        self.shell9 = BossLV4Shell([89, 178], 9, 400, self.rect.center)
        self.shell10 = BossLV4Shell([178, 178], 10, 500, self.rect.center)
        self.shell11 = BossLV4Shell([178, 89], 11, 400, self.rect.center)
        self.shell12 = BossLV4Shell([178, 178], 12, 500, self.rect.center)
        self.shells = [self.shell1, self.shell2, self.shell3, self.shell4, self.shell5, self.shell6, self.shell7, self.shell8, self.shell9, self.shell10, self.shell11, self.shell12]
        self.i = 0

    def update(self):
        if self.i == 0:
            all_mobs.add(self.shell1)
            all_mobs.add(self.shell2)
            all_mobs.add(self.shell3)
            all_mobs.add(self.shell4)
            all_mobs.add(self.shell5)
            all_mobs.add(self.shell6)
            all_mobs.add(self.shell7)
            all_mobs.add(self.shell8)
            all_mobs.add(self.shell9)
            all_mobs.add(self.shell10)
            all_mobs.add(self.shell11)
            all_mobs.add(self.shell12)
            self.i += 1
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if -(map_size / 2 - 0.5) * screen_width < self.abs_x < (map_size / 2 + 0.5) * screen_width - self.rect.width \
                    and -(map_size / 2 - 0.5) * screen_height < self.abs_y < (map_size / 2 + 0.5) * screen_height - self.rect.height:
                self.in_map = True
                self.reflected = False
            elif self.attack_mode == "boost":
                self.in_map = False
            if self.attack_mode != "boost":
                self.speedx = self.speed * (player.rect.center[0] - self.rect.center[0]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
                self.speedy = self.speed * (player.rect.center[1] - self.rect.center[1]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
            if not self.attack:
                self.abs_x += self.speedx
                self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])

            if not self.attack and random.random() < 0.005 and self.in_map:
                self.attack = True
                if len(self.shield_childs) + len(self.attack_childs) < 60:
                    self.attack_mode = "childs"
                else:
                    if random.random() < 0.25:
                        self.attack_mode = "childs"
                    elif random.random() < 0.7:
                        self.attack_mode = "cannon"
                    else:
                        self.attack_mode = "boost"
                    self.attack_mode = random.choice(["childs", "cannon", "boost"])
                if self.attack_mode == "boost":
                    dist_x = player.rect.center[0] - self.rect.center[0]
                    dist_y = player.rect.center[1] - self.rect.center[1]
                    angle = math.atan2(dist_y, dist_x)
                    self.boost_dir = round((-angle + math.pi * 9 / 8) // (math.pi / 4)) + 1
                    shell_sel_ind = []
                    if self.boost_dir == 1:
                        shell_sel_ind = [0, 3, 4, 5, 11]
                        if self.shells[0].dead and self.shells[3].dead and self.shells[4].dead:
                            self.attack = False
                            self.attack_mode = None
                    elif self.boost_dir == 2:
                        shell_sel_ind = [0, 4, 5, 6]
                        if self.shells[0].dead and self.shells[5].dead:
                            self.attack = False
                            self.attack_mode = None
                    elif self.boost_dir == 3:
                        shell_sel_ind = [0, 1, 5, 6, 7]
                        if self.shells[0].dead and self.shells[1].dead and self.shells[6].dead:
                            self.attack = False
                            self.attack_mode = None
                    elif self.boost_dir == 4:
                        shell_sel_ind = [1, 6, 7, 8]
                        if self.shells[1].dead and self.shells[7].dead:
                            self.attack = False
                            self.attack_mode = None
                    elif self.boost_dir == 5:
                        shell_sel_ind = [1, 2, 7, 8, 9]
                        if self.shells[1].dead and self.shells[2].dead and self.shells[8].dead:
                            self.attack = False
                            self.attack_mode = None
                    elif self.boost_dir == 6:
                        shell_sel_ind = [2, 8, 9, 10]
                        if self.shells[2].dead and self.shells[9].dead:
                            self.attack = False
                            self.attack_mode = None
                    elif self.boost_dir == 7:
                        shell_sel_ind = [2, 3, 9, 10, 11]
                        if self.shells[2].dead and self.shells[3].dead and self.shells[10].dead:
                            self.attack = False
                            self.attack_mode = None
                    elif self.boost_dir == 8:
                        shell_sel_ind = [3, 10, 11, 4]
                        if self.shells[3].dead and self.shells[11].dead:
                            self.attack = False
                            self.attack_mode = None
                    for ind in shell_sel_ind:
                        self.shell_sel[ind] = 1
                else:
                    self.shell_sel = [1] * 12
                self.shell_moved = 0
            if self.attack:
                if not self.shell_opened:
                    if self.attack_mode == "boost":
                        self.hit = True
                    self.shell_moved += 0.5
                    for s in self.shells:
                        if not s.dead:
                            if s.shellnum == 1:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[0], self.rect.center[1] - self.shell_moved * self.shell_sel[0]])
                            elif s.shellnum == 2:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[1], self.rect.center[1] - self.shell_moved * self.shell_sel[1]])
                            elif s.shellnum == 3:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[2], self.rect.center[1] + self.shell_moved * self.shell_sel[2]])
                            elif s.shellnum == 4:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[3], self.rect.center[1] + self.shell_moved * self.shell_sel[3]])
                            elif s.shellnum == 5:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[4], self.rect.center[1]])
                            elif s.shellnum == 6:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[5] * 2, self.rect.center[1] - self.shell_moved * self.shell_sel[5] * 2])
                            elif s.shellnum == 7:
                                s.update([self.rect.center[0], self.rect.center[1] - self.shell_moved * self.shell_sel[6]])
                            elif s.shellnum == 8:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[7] * 2, self.rect.center[1] - self.shell_moved * self.shell_sel[7] * 2])
                            elif s.shellnum == 9:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[8], self.rect.center[1]])
                            elif s.shellnum == 10:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[9] * 2, self.rect.center[1] + self.shell_moved * self.shell_sel[9] * 2])
                            elif s.shellnum == 11:
                                s.update([self.rect.center[0], self.rect.center[1] + self.shell_moved * self.shell_sel[10]])
                            elif s.shellnum == 12:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[11] * 2, self.rect.center[1] + self.shell_moved * self.shell_sel[11] * 2])
                    if self.shell_moved == 50:
                        self.shell_opened = True
                        self.opened_time = time.time()

                if self.shell_opened:
                    for s in self.shells:
                        if not s.dead:
                            if s.shellnum == 1:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[0], self.rect.center[1] - self.shell_moved * self.shell_sel[0]])
                            elif s.shellnum == 2:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[1], self.rect.center[1] - self.shell_moved * self.shell_sel[1]])
                            elif s.shellnum == 3:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[2], self.rect.center[1] + self.shell_moved * self.shell_sel[2]])
                            elif s.shellnum == 4:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[3], self.rect.center[1] + self.shell_moved * self.shell_sel[3]])
                            elif s.shellnum == 5:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[4], self.rect.center[1]])
                            elif s.shellnum == 6:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[5] * 2, self.rect.center[1] - self.shell_moved * self.shell_sel[5] * 2])
                            elif s.shellnum == 7:
                                s.update([self.rect.center[0], self.rect.center[1] - self.shell_moved * self.shell_sel[6]])
                            elif s.shellnum == 8:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[7] * 2, self.rect.center[1] - self.shell_moved * self.shell_sel[7] * 2])
                            elif s.shellnum == 9:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[8], self.rect.center[1]])
                            elif s.shellnum == 10:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[9] * 2, self.rect.center[1] + self.shell_moved * self.shell_sel[9] * 2])
                            elif s.shellnum == 11:
                                s.update([self.rect.center[0], self.rect.center[1] + self.shell_moved * self.shell_sel[10]])
                            elif s.shellnum == 12:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[11] * 2, self.rect.center[1] + self.shell_moved * self.shell_sel[11] * 2])
                    if not self.attack_finished:
                        if self.attack_mode == "childs":
                            self.attack_num = 6
                            if time.time() - self.last_attacked >= 1:
                                if (random.random() < 0.2 or len(self.shield_childs) >= 400) and len(self.attack_childs) < 50:
                                    dist_x = player.rect.center[0] - self.rect.center[0]
                                    dist_y = player.rect.center[1] - self.rect.center[1]
                                    angle = math.atan2(dist_y, dist_x)
                                    for c in range(random.randrange(30, 40)):
                                        direction = random.uniform(angle + math.pi / 6, angle + math.pi * 11 / 6)
                                        child = BossLV4Child((random.randrange(self.rect.width / 5) + self.abs_x + self.rect.width * 2 / 5, random.randrange(self.rect.height / 5) + self.abs_y + self.rect.height * 2 / 5), direction, "attack")
                                        all_sprites.add(child)
                                        all_mobs.add(child)
                                        self.attack_childs.add(child)
                                elif len(self.shield_childs) < 400:
                                    for c in range(random.randrange(100, 130)):
                                        direction = random.uniform(0, 2 * math.pi)
                                        child = BossLV4Child((random.randrange(self.rect.width / 5) + self.abs_x + self.rect.width * 2 / 5, random.randrange(self.rect.height / 5) + self.abs_y + self.rect.height * 2 / 5), direction, "shield")
                                        all_sprites.add(child)
                                        all_mobs.add(child)
                                        self.shield_childs.add(child)
                                expl_type = random.randrange(1, 12)
                                expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 0.4), round(self.size[1] * 0.4)))
                                all_sprites.add(expl)
                                explosions.add(expl)
                                self.last_attacked = time.time()
                                self.attacked += 1
                                if len(self.attack_childs) >= 50 and len(self.shield_childs) >= 400:
                                    self.attack_finished = True
                                    self.shell_opened = False
                                    self.attacked = 0
                        elif self.attack_mode == "cannon":
                            self.attack_num = 25
                            if time.time() - self.last_attacked >= 0.25:
                                dist_x = player.rect.center[0] - self.rect.center[0]
                                dist_y = player.rect.center[1] - self.rect.center[1]
                                angle = math.atan2(dist_y, dist_x) + random.uniform(-0.1, 0.1) * math.pi
                                start_angle = angle - math.pi / 2
                                while start_angle < angle + math.pi / 2:
                                    cannonball = MobCannonBall1(self.rect.center, start_angle, 47, 12)
                                    all_sprites.add(cannonball)
                                    mob_cannon_balls.add(cannonball)
                                    start_angle += math.pi / 14
                                expl_type = random.randrange(1, 12)
                                expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 0.4), round(self.size[1] * 0.4)))
                                all_sprites.add(expl)
                                explosions.add(expl)
                                self.attacked += 1
                                self.last_attacked = time.time()
                        else:   # boost mode
                            self.speed = self.speed_boost
                            if self.boost_dir == 1:
                                self.speedx = -self.speed_boost
                                self.speedy = 0
                                self.boost_accx = self.boost_acc
                                self.boost_accy = 0
                            elif self.boost_dir == 2:
                                self.speedx = -self.speed_boost / math.sqrt(2)
                                self.speedy = self.speed_boost / math.sqrt(2)
                                self.boost_accx = self.boost_acc / math.sqrt(2)
                                self.boost_accy = -self.boost_acc / math.sqrt(2)
                            elif self.boost_dir == 3:
                                self.speedx = 0
                                self.speedy = self.speed_boost
                                self.boost_accx = 0
                                self.boost_accy = -self.boost_acc
                            elif self.boost_dir == 4:
                                self.speedx = self.speed_boost / math.sqrt(2)
                                self.speedy = self.speed_boost / math.sqrt(2)
                                self.boost_accx = -self.boost_acc / math.sqrt(2)
                                self.boost_accy = -self.boost_acc / math.sqrt(2)
                            elif self.boost_dir == 5:
                                self.speedx = self.speed_boost
                                self.speedy = 0
                                self.boost_accx = -self.boost_acc
                                self.boost_accy = 0
                            elif self.boost_dir == 6:
                                self.speedx = self.speed_boost / math.sqrt(2)
                                self.speedy = -self.speed_boost / math.sqrt(2)
                                self.boost_accx = -self.boost_acc / math.sqrt(2)
                                self.boost_accy = self.boost_acc / math.sqrt(2)
                            elif self.boost_dir == 7:
                                self.speedx = 0
                                self.speedy = -self.speed_boost
                                self.boost_accx = 0
                                self.boost_accy = self.boost_acc
                            elif self.boost_dir == 8:
                                self.speedx = -self.speed_boost / math.sqrt(2)
                                self.speedy = -self.speed_boost / math.sqrt(2)
                                self.boost_accx = self.boost_acc / math.sqrt(2)
                                self.boost_accy = self.boost_acc / math.sqrt(2)
                            self.attack_finished = True
                            self.shell_opened = False
                            self.attacked = 0

                        if self.attacked >= self.attack_num:
                            self.attack_finished = True
                            self.shell_opened = False
                            self.attacked = 0

                if self.attack_finished:
                    if self.attack_mode == "boost":
                        self.speedx += self.boost_accx
                        self.speedy += self.boost_accy
                        self.abs_x += self.speedx
                        self.abs_y += self.speedy
                        self.rect.x = round(self.abs_x - screen_center[0])
                        self.rect.y = round(self.abs_y - screen_center[1])
                    if not self.in_map and not self.reflected:
                        if self.abs_x <= -(map_size / 2 - 0.5) * screen_width or self.abs_x >= (
                                map_size / 2 + 0.5) * screen_width - self.rect.width:
                            self.speedx = -self.speedx
                            self.boost_accx = -self.boost_accx
                            self.reflected = True
                        elif self.abs_y <= -(map_size / 2 - 0.5) * screen_height or self.abs_y >= (
                                map_size / 2 + 0.5) * screen_height - self.rect.height:
                            self.speedy = -self.speedy
                            self.boost_accy = -self.boost_accy
                            self.reflected = True
                    self.shell_moved -= 0.5
                    for s in self.shells:
                        if not s.dead:
                            if s.shellnum == 1:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[0], self.rect.center[1] - self.shell_moved * self.shell_sel[0]])
                            elif s.shellnum == 2:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[1], self.rect.center[1] - self.shell_moved * self.shell_sel[1]])
                            elif s.shellnum == 3:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[2], self.rect.center[1] + self.shell_moved * self.shell_sel[2]])
                            elif s.shellnum == 4:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[3], self.rect.center[1] + self.shell_moved * self.shell_sel[3]])
                            elif s.shellnum == 5:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[4], self.rect.center[1]])
                            elif s.shellnum == 6:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[5] * 2, self.rect.center[1] - self.shell_moved * self.shell_sel[5] * 2])
                            elif s.shellnum == 7:
                                s.update([self.rect.center[0], self.rect.center[1] - self.shell_moved * self.shell_sel[6]])
                            elif s.shellnum == 8:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[7] * 2, self.rect.center[1] - self.shell_moved * self.shell_sel[7] * 2])
                            elif s.shellnum == 9:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[8], self.rect.center[1]])
                            elif s.shellnum == 10:
                                s.update([self.rect.center[0] - self.shell_moved * self.shell_sel[9] * 2, self.rect.center[1] + self.shell_moved * self.shell_sel[9] * 2])
                            elif s.shellnum == 11:
                                s.update([self.rect.center[0], self.rect.center[1] + self.shell_moved * self.shell_sel[10]])
                            elif s.shellnum == 12:
                                s.update([self.rect.center[0] + self.shell_moved * self.shell_sel[11] * 2, self.rect.center[1] + self.shell_moved * self.shell_sel[11] * 2])
                    if self.shell_moved == 0:
                        self.attack_finished = False
                        self.shell_opened = False
                        self.shell_sel = [0] * 12
                        self.attack = False
                        self.attack_mode = None
                        self.speed = self.speed_orig
            else:
                self.cannon_interval = max(self.hp / self.hp_full, 0.1)
                if time.time() - self.cannon_fired >= self.cannon_interval:
                    dist_x = player.rect.center[0] - self.rect.center[0]
                    dist_y = player.rect.center[1] - self.rect.center[1]
                    angle = math.atan2(dist_y, dist_x) + random.uniform(-math.pi / 9, math.pi / 9)
                    cannonball = MobCannonBall1(self.rect.center, angle, 47, 12)
                    all_sprites.add(cannonball)
                    mob_cannon_balls.add(cannonball)
                    self.cannon_fired = time.time()
                for s in self.shells:
                    if not s.dead:
                        s.update(self.rect.center)

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt,
                      self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if len(self.shells) <= 0:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]],
                            "upgrade weapon")
                all_sprites.add(item)
                items.add(item)
                for e in range(random.randrange(20, 25)):
                    expl_type = random.randrange(1, 12)
                    expl = Explosion((random.randrange(self.rect.width) + self.rect.x,
                                      random.randrange(self.rect.height) + self.rect.y), expl_type,
                                     (round(self.size[0]), round(self.size[1])))
                    all_sprites.add(expl)
                    explosions.add(expl)
                global stage4_clear, stage4_boss_spawned, now_break_4, break_start, phase_text
                stage4_clear = True
                stage4_boss_spawned = False
                pointer.kill()
                for m in mobs:
                    if random.random() < 0.7:
                        m.dead = True
                now_break_4 = True
                break_start = time.time()
                phase_text = "{}s BREAKTIME".format(breaktime)
                self.kill()
            for s in self.shells:
                if not s.dead:
                    s.dead = True
                    s.update(self.rect.center)
            for c in self.attack_childs:
                c.dead = True
            for c in self.shield_childs:
                c.dead = True
            self.shells = []


class BossLV4Shell(pygame.sprite.Sprite):
    def __init__(self, size, shellnum, hp, pos):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.debris_size = 15
        self.debris_speed = random.randrange(12, 18)
        self.norm_image = boss_lv4_shell_img[shellnum - 1][1]
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = boss_lv4_shell_img[shellnum - 1]
        self.rect = self.image.get_rect()
        self.damage = 10000
        self.hit = False
        self.hitcount = 0
        self.hp = hp
        self.hp_full = self.hp
        self.dead = False
        self.points = 3000
        self.no_points = False
        self.shellnum = shellnum
        if self.shellnum == 1:
            self.abs_x = pos[0]
            self.abs_y = pos[1] - self.size[1]
        elif self.shellnum == 2:
            self.abs_x = pos[0] - self.size[0]
            self.abs_y = pos[1] - self.size[0]
        elif self.shellnum == 3:
            self.abs_x = pos[0] - self.size[1]
            self.abs_y = pos[1]
        elif self.shellnum == 4:
            self.abs_x = pos[0]
            self.abs_y = pos[1]
        elif self.shellnum == 5:
            self.abs_x = pos[0] + self.size[0] * 2
            self.abs_y = pos[1] - self.size[1] // 2
        elif self.shellnum == 6:
            self.abs_x = pos[0] + self.size[0] // 2
            self.abs_y = pos[1] - self.size[1] * 3 // 2
        elif self.shellnum == 7:
            self.abs_x = pos[0] - self.size[0] // 2
            self.abs_y = pos[1] - self.size[1] * 3
        elif self.shellnum == 8:
            self.abs_x = pos[0] - self.size[0] * 3 // 2
            self.abs_y = pos[1] - self.size[1] * 3 // 2
        elif self.shellnum == 9:
            self.abs_x = pos[0] - self.size[0] * 3
            self.abs_y = pos[1] - self.size[1] // 2
        elif self.shellnum == 10:
            self.abs_x = pos[0] - self.size[0] * 3 // 2
            self.abs_y = pos[1] + self.size[1] // 2
        elif self.shellnum == 11:
            self.abs_x = pos[0] - self.size[0] // 2
            self.abs_y = pos[1] + self.size[1] * 2
        elif self.shellnum == 12:
            self.abs_x = pos[0] + self.size[0] // 2
            self.abs_y = pos[1] + self.size[1] // 2

    def update(self, pos=(0, 0)):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            if self.shellnum == 1:
                self.abs_x = pos[0]
                self.abs_y = pos[1] - self.size[1]
            elif self.shellnum == 2:
                self.abs_x = pos[0] - self.size[0]
                self.abs_y = pos[1] - self.size[0]
            elif self.shellnum == 3:
                self.abs_x = pos[0] - self.size[1]
                self.abs_y = pos[1]
            elif self.shellnum == 4:
                self.abs_x = pos[0]
                self.abs_y = pos[1]
            elif self.shellnum == 5:
                self.abs_x = pos[0] + self.size[0] * 2
                self.abs_y = pos[1] - self.size[1] // 2
            elif self.shellnum == 6:
                self.abs_x = pos[0] + self.size[0] // 2
                self.abs_y = pos[1] - self.size[1] * 3 // 2
            elif self.shellnum == 7:
                self.abs_x = pos[0] - self.size[0] // 2
                self.abs_y = pos[1] - self.size[1] * 3
            elif self.shellnum == 8:
                self.abs_x = pos[0] - self.size[0] * 3 // 2
                self.abs_y = pos[1] - self.size[1] * 3 // 2
            elif self.shellnum == 9:
                self.abs_x = pos[0] - self.size[0] * 3
                self.abs_y = pos[1] - self.size[1] // 2
            elif self.shellnum == 10:
                self.abs_x = pos[0] - self.size[0] * 3 // 2
                self.abs_y = pos[1] + self.size[1] // 2
            elif self.shellnum == 11:
                self.abs_x = pos[0] - self.size[0] // 2
                self.abs_y = pos[1] + self.size[1] * 2
            elif self.shellnum == 12:
                self.abs_x = pos[0] + self.size[0] // 2
                self.abs_y = pos[1] + self.size[1] // 2
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(max(self.size) * 1.5), round(max(self.size) * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class BossLV4Child(pygame.sprite.Sprite):
    def __init__(self, abs_pos, direction, mode):
        pygame.sprite.Sprite.__init__(self)
        self.mode = mode
        self.size = [18, 18]
        self.debris_size = 13
        self.debris_speed = random.randrange(5, 10)
        self.norm_image = boss_lv4child_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = boss_lv4child_hit_anim
        self.rect = self.image.get_rect()
        self.dir = direction
        self.max_speed = random.uniform(7, 13)
        self.speed = random.uniform(0, self.max_speed)
        self.damage = 12
        self.hit = False
        self.hitcount = 0
        self.hp = 2
        self.hp_full = self.hp
        self.dead = False
        self.points = 40
        self.no_points = False
        self.abs_x = abs_pos[0]
        self.abs_y = abs_pos[1]
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1])
        self.speedx = self.speed * math.cos(self.dir)
        self.speedy = self.speed * math.sin(self.dir)
        self.dist_x = 0
        self.dist_y = 0
        if self.mode == "attack":
            self.dist_x = player.rect.center[0] - self.rect.center[0]
            self.dist_y = player.rect.center[1] - self.rect.center[1]
        elif self.mode == "shield":
            self.dist_x = boss.rect.center[0] - self.rect.center[0]
            self.dist_y = boss.rect.center[1] - self.rect.center[1]
        self.acc_dir = math.atan2(self.dist_y, self.dist_x)
        self.acc = random.uniform(0.2, 0.4)
        self.acc_x = self.acc * math.cos(self.acc_dir)
        self.acc_y = self.acc * math.sin(self.acc_dir)

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            if self.mode == "attack":
                self.dist_x = player.rect.center[0] - self.rect.center[0]
                self.dist_y = player.rect.center[1] - self.rect.center[1]
                self.acc_dir = math.atan2(self.dist_y, self.dist_x)
                self.acc_x = self.acc * math.cos(self.acc_dir)
                self.acc_y = self.acc * math.sin(self.acc_dir)
            elif self.mode == "shield":
                self.dist_x = boss.rect.center[0] - self.rect.center[0]
                self.dist_y = boss.rect.center[1] - self.rect.center[1]
                self.acc_dir = math.atan2(self.dist_y, self.dist_x)
                if distance(boss.rect.center, self.rect.center) <= 400:
                    self.acc_x = 0
                    self.acc_y = 0
                elif distance(boss.rect.center, self.rect.center) >= 400:
                    self.acc_x = self.acc * math.cos(self.acc_dir)
                    self.acc_y = self.acc * math.sin(self.acc_dir)
            self.speedx = min(self.speedx + self.acc_x, self.max_speed)
            self.speedy = min(self.speedy + self.acc_y, self.max_speed)
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


class FollowerMobShieldUnit(pygame.sprite.Sprite):
    def __init__(self, master_pos, pos, size, debris_size, debris_speed, image, hit_anim, damage, hp, points):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.size = size
        self.debris_size = debris_size
        self.debris_speed = debris_speed
        self.norm_image = image
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = hit_anim
        self.rect = self.image.get_rect()
        self.rect.x = master_pos[0] + self.pos[0]
        self.rect.y = master_pos[1] + self.pos[1]
        self.damage = damage
        self.hit = False
        self.hitcount = 0
        self.hp = hp
        self.hp_full = hp
        self.dead = False
        self.points = points
        self.no_points = False

    def update(self, master_pos=(0, 0)):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.rect.x = master_pos[0] + self.pos[0]
            self.rect.y = master_pos[1] + self.pos[1]
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            expl_type = random.randrange(1, 12)
            expl = Explosion(self.rect.center, expl_type, (round(self.size[0] * 1.5), round(self.size[1] * 1.5)))
            all_sprites.add(expl)
            explosions.add(expl)
            self.kill()


def generate_shield(master_pos, master_size, layer, shield_size, unit_size, debris_size, debris_speed, image, hit_anim, damage, hp, points, shield_group):
    shield_width = shield_size[0] * unit_size[0]
    shield_height = shield_size[1] * unit_size[1]
    pos = ((master_size[0] - shield_width) // 2, (master_size[1] - shield_height) // 2)
    for q in range(shield_size[1]):
        if q in range(layer, shield_size[1] - layer):
            for p in range(layer):
                shield_unit = FollowerMobShieldUnit(master_pos, (pos[0] + p * unit_size[0], pos[1] + q * unit_size[1]), unit_size, debris_size, debris_speed, image, hit_anim, damage, hp, points)
                shield_group.add(shield_unit)
                all_mobs.add(shield_unit)
            for p in range(shield_size[0] - layer, shield_size[0]):
                shield_unit = FollowerMobShieldUnit(master_pos, (pos[0] + p * unit_size[0], pos[1] + q * unit_size[1]), unit_size, debris_size, debris_speed, image, hit_anim, damage, hp, points)
                shield_group.add(shield_unit)
                all_mobs.add(shield_unit)
        else:
            for p in range(shield_size[0]):
                shield_unit = FollowerMobShieldUnit(master_pos, (pos[0] + p * unit_size[0], pos[1] + q * unit_size[1]), unit_size, debris_size, debris_speed, image, hit_anim, damage, hp, points)
                shield_group.add(shield_unit)
                all_mobs.add(shield_unit)


class HitEffect(pygame.sprite.Sprite):
    """
    appears when a bullet and a mob(or player) collide
    """
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = pygame.transform.scale(hiteffect_anim[0], self.size)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.frame = 0

    def update(self):
        self.frame += 1
        if self.frame == len(hiteffect_anim):
            self.kill()
        else:
            self.image = pygame.transform.scale(hiteffect_anim[self.frame], self.size)
            self.rect = self.image.get_rect()
            self.rect.x = self.abs_x - screen_center[0]
            self.rect.y = self.abs_y - screen_center[1]


class Explosion(pygame.sprite.Sprite):
    """
    explosion animation
    appears when a mob killed or a cannonball explodes
    """
    def __init__(self, center, expl_type, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.type = expl_type
        self.image = pygame.transform.scale(explosion_anim[str(self.type)][0], self.size)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.frame = 0

    def update(self):
        self.frame += 1
        if self.frame == len(explosion_anim[str(self.type)]):
            self.kill()
        else:
            self.image = pygame.transform.scale(explosion_anim[str(self.type)][self.frame], self.size)
            self.rect = self.image.get_rect()
            self.rect.x = self.abs_x - screen_center[0]
            self.rect.y = self.abs_y - screen_center[1]


class Debris(pygame.sprite.Sprite):
    """
    spreads with explosion when a mob is killed
    has random size, speed, and direction
    a player gets score by collecting debriz
    generated by "split" function
    """
    def __init__(self, size, pos, speed, points):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.randrange(16)
        self.orientation = random.randrange(360)
        self.direction = random.randrange(360) * math.pi / 180
        self.size = (size, size)
        self.image_orig = pygame.transform.scale(debriz_img[self.type], self.size)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.speed = speed
        self.speedx = self.speed * math.cos(self.direction)
        self.speedy = self.speed * math.sin(self.direction)
        self.points = points
        new_image = pygame.transform.rotate(self.image_orig, self.orientation)
        old_center = self.rect.center
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.gen_time = time.time()

    def update(self):
        # move toward player while in pick range
        if distance(self.rect.center, player.rect.center) <= player.pick_range:
            self.speed = 15
            dist_x = player.rect.center[0] - self.rect.center[0]
            dist_y = player.rect.center[1] - self.rect.center[1]
            angle = math.atan2(dist_y, dist_x)
            self.speedx = self.speed * math.cos(-angle)
            self.speedy = self.speed * math.sin(angle)
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if distance(self.rect.center, player.rect.center) <= 15:
                global score
                score += self.points
                self.kill()
        else:
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1])
            if self.speed > 0:
                self.speed -= 1
            self.speedx = self.speed * math.cos(self.direction)
            self.speedy = self.speed * math.sin(self.direction)
            now = time.time()
            if now - self.gen_time >= random.uniform(5, 8):
                self.kill()


def split(pos, avg_debris_cnt, avg_debris_size, avg_points, speed):
    """ spreads a number of debriz """
    debris_cnt = random.randrange(round(avg_debris_cnt * 0.8), round(avg_debris_cnt * 1.2) + 1)
    for d in range(debris_cnt):
        debris_size = random.randrange(round(avg_debris_size * 0.5), round(avg_debris_size * 1.5))
        points = random.uniform(avg_points * 0.5, avg_points * 1.5)
        debris = Debris(debris_size, pos, random.randrange(round(speed * 0.5), round(speed * 1.2)), points)
        all_sprites.add(debris)
        debriz.add(debris)


class Item(pygame.sprite.Sprite):
    """
    game item for player, disappears 10s after generated
    regenerate: heals player, dropped by mobs at 2% chance
    upgrade weaopn: upgrades player's shooting pattern, dropped by boss
    """
    def __init__(self, pos, item_type):
        pygame.sprite.Sprite.__init__(self)
        self.type = item_type
        if self.type == "regenerate":
            self.image = pygame.Surface((15, 15))
            self.image.fill(WHITE1)
        elif self.type == "upgrade weapon":
            self.image = pygame.Surface((20, 20))
            self.image.fill(CYAN1)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.abs_x = self.rect.x
        self.abs_y = self.rect.y
        self.rect.x -= screen_center[0]
        self.rect.y -= screen_center[1]
        self.droptime = time.time()

    def update(self):
        self.rect.x = self.abs_x - screen_center[0]
        self.rect.y = self.abs_y - screen_center[1]
        current_time = time.time()
        if current_time - self.droptime >= 10:
            self.kill()

    def buff(self):
        if self.type == "regenerate":
            player.hp += player.hp_full / 6
            if player.hp > player.hp_full:
                player.hp = player.hp_full
        elif self.type == "upgrade weapon":
            player.weapon_lvl += 1


pygame.init()

screen = pygame.display.set_mode([screen_width, screen_height])

pygame.display.set_caption("War of Squares")

done = False
click = False
clock = pygame.time.Clock()
fps = 30

num_font = pygame.font.SysFont("verdana", 20)
text_font = pygame.font.match_font("verdana")

""" load all images """
# anim: animation (blink 3 times)
player_img = pygame.image.load(path.join(char_dir, "player.png")).convert()
targetpointer_img = pygame.image.load(path.join(char_dir, "target_pointer.png")).convert()
targetpointer_img.set_colorkey(BLACK)
bosspointer_img = pygame.image.load(path.join(char_dir, "bosspointer.png")).convert()

linemob1_img = pygame.image.load(path.join(char_dir, "linemob1.png")).convert()
linemob1_hit_img = pygame.image.load(path.join(char_dir, "linemob1_hit.png")).convert()
linemob1_hit_anim = [linemob1_hit_img, linemob1_img] * 3
linemob2_img = pygame.image.load(path.join(char_dir, "linemob2.png")).convert()
linemob2_hit_img = pygame.image.load(path.join(char_dir, "linemob2_hit.png")).convert()
linemob2_hit_anim = [linemob2_hit_img, linemob2_img] * 3
linemob3_img = pygame.image.load(path.join(char_dir, "linemob3.png")).convert()
linemob3_hit_img = pygame.image.load(path.join(char_dir, "linemob3_hit.png")).convert()
linemob3_hit_anim = [linemob3_hit_img, linemob3_img] * 3
wallmob1_img = pygame.image.load(path.join(char_dir, "wallmob1.png")).convert()
wallmob1_hit_img = pygame.image.load(path.join(char_dir, "wallmob1_hit.png")).convert()
wallmob1_hit_anim = [wallmob1_hit_img, wallmob1_img] * 3
wallmob2_img = pygame.image.load(path.join(char_dir, "wallmob2.png")).convert()
wallmob2_hit_img = pygame.image.load(path.join(char_dir, "wallmob2_hit.png")).convert()
wallmob2_hit_anim = [wallmob2_hit_img, wallmob2_img] * 3
wallmob3_img = pygame.image.load(path.join(char_dir, "wallmob3.png")).convert()
wallmob3_hit_img = pygame.image.load(path.join(char_dir, "wallmob3_hit.png")).convert()
wallmob3_hit_anim = [wallmob3_hit_img, wallmob3_img] * 3
followermob1_img = pygame.image.load(path.join(char_dir, "followermob1.png")).convert()
followermob1_hit_img = pygame.image.load(path.join(char_dir, "followermob1_hit.png")).convert()
followermob1_hit_anim = [followermob1_hit_img, followermob1_img] * 3
followermob2_img = pygame.image.load(path.join(char_dir, "followermob2.png")).convert()
followermob2_hit_img = pygame.image.load(path.join(char_dir, "followermob2_hit.png")).convert()
followermob2_hit_anim = [followermob2_hit_img, followermob2_img] * 3
followermob2child_img = pygame.image.load(path.join(char_dir, "followermob2child.png")).convert()
followermob2child_hit_img = pygame.image.load(path.join(char_dir, "followermob2child_hit.png")).convert()
followermob2child_hit_anim = [followermob2child_hit_img, followermob2child_img] * 3
shieldunit1_img = pygame.image.load(path.join(char_dir, "shieldunit1.png")).convert()
shieldunit1_hit_img = pygame.image.load(path.join(char_dir, "shieldunit1_hit.png")).convert()
shieldunit1_hit_anim = [shieldunit1_hit_img, shieldunit1_img] * 3
shieldunit2_img = pygame.image.load(path.join(char_dir, "shieldunit2.png")).convert()
shieldunit2_hit_img = pygame.image.load(path.join(char_dir, "shieldunit2_hit.png")).convert()
shieldunit2_hit_anim = [shieldunit2_hit_img, shieldunit2_img] * 3
shieldunit3_img = pygame.image.load(path.join(char_dir, "shieldunit3.png")).convert()
shieldunit3_hit_img = pygame.image.load(path.join(char_dir, "shieldunit3_hit.png")).convert()
shieldunit3_hit_anim = [shieldunit3_hit_img, shieldunit3_img] * 3
minigunmob1_img = pygame.image.load(path.join(char_dir, "minigunmob1.png")).convert()
minigunmob1_hit_img = pygame.image.load(path.join(char_dir, "minigunmob1_hit.png")).convert()
minigunmob1_hit_anim = [minigunmob1_hit_img, minigunmob1_img] * 3
minigunmob2_img = pygame.image.load(path.join(char_dir, "minigunmob2.png")).convert()
minigunmob2_hit_img = pygame.image.load(path.join(char_dir, "minigunmob2_hit.png")).convert()
minigunmob2_hit_anim = [minigunmob2_hit_img, minigunmob2_img] * 3
minigunmob3_img = pygame.image.load(path.join(char_dir, "minigunmob3.png")).convert()
minigunmob3_hit_img = pygame.image.load(path.join(char_dir, "minigunmob3_hit.png")).convert()
minigunmob3_hit_anim = [minigunmob3_hit_img, minigunmob3_img] * 3
shellmob1_core_img = pygame.image.load(path.join(char_dir, "shellmob1_core.png")).convert()
shellmob1_core_hit_img = pygame.image.load(path.join(char_dir, "shellmob1_core_hit.png")).convert()
shellmob1_core_hit_anim = [shellmob1_core_hit_img, shellmob1_core_img] * 3
shellmob1_shell_img = []
for i in range(4):
    shell_img = pygame.image.load(path.join(char_dir, "shellmob1_shell{}.png".format(i + 1))).convert()
    shell_img.set_colorkey(WHITE1)
    shell_hit_img = pygame.image.load(path.join(char_dir, "shellmob1_shell{}_hit.png".format(i + 1))).convert()
    shell_hit_img.set_colorkey(WHITE1)
    shell_hit_anim = [shell_hit_img, shell_img] * 3
    shellmob1_shell_img.append(shell_hit_anim)
shellmob2_core_img = pygame.image.load(path.join(char_dir, "shellmob2_core.png")).convert()
shellmob2_core_hit_img = pygame.image.load(path.join(char_dir, "shellmob2_core_hit.png")).convert()
shellmob2_core_hit_anim = [shellmob2_core_hit_img, shellmob2_core_img] * 3
shellmob2_shell_img = []
for i in range(4):
    shell_img = pygame.image.load(path.join(char_dir, "shellmob2_shell{}.png".format(i + 1))).convert()
    shell_img.set_colorkey(WHITE1)
    shell_hit_img = pygame.image.load(path.join(char_dir, "shellmob2_shell{}_hit.png".format(i + 1))).convert()
    shell_hit_img.set_colorkey(WHITE1)
    shell_hit_anim = [shell_hit_img, shell_img] * 3
    shellmob2_shell_img.append(shell_hit_anim)
boss_lv1_img = pygame.image.load(path.join(char_dir, "boss_lv1.png")).convert()
boss_lv1_hit_img = pygame.image.load(path.join(char_dir, "boss_lv1_hit.png")).convert()
boss_lv1_hit_anim = [boss_lv1_hit_img, boss_lv1_img] * 3
boss_lv2_img = pygame.image.load(path.join(char_dir, "boss_lv2.png")).convert()
boss_lv2_hit_img = pygame.image.load(path.join(char_dir, "boss_lv2_hit.png")).convert()
boss_lv2_hit_anim = [boss_lv2_hit_img, boss_lv2_img] * 3
boss_lv3_img = pygame.image.load(path.join(char_dir, "boss_lv3.png")).convert()
boss_lv3_img.set_colorkey(WHITE1)
boss_lv3_hit_img = pygame.image.load(path.join(char_dir, "boss_lv3_hit.png")).convert()
boss_lv3_hit_img.set_colorkey(WHITE1)
boss_lv3_hit_anim = [boss_lv3_hit_img, boss_lv3_img] * 3
boss_lv4_core_img = pygame.image.load(path.join(char_dir, "boss_lv4_core.png")).convert()
boss_lv4_core_hit_img = pygame.image.load(path.join(char_dir, "boss_lv4_core_hit.png")).convert()
boss_lv4_core_hit_anim = [boss_lv4_core_hit_img, boss_lv4_core_img] * 3
boss_lv4_shell_img = []
for i in range(12):
    shell_img = pygame.image.load(path.join(char_dir, "boss_lv4_shell{}.png".format(i + 1))).convert()
    shell_img.set_colorkey(WHITE1)
    shell_hit_img = pygame.image.load(path.join(char_dir, "boss_lv4_shell{}_hit.png".format(i + 1))).convert()
    shell_hit_img.set_colorkey(WHITE1)
    shell_hit_anim = [shell_hit_img, shell_img] * 3
    boss_lv4_shell_img.append(shell_hit_anim)
boss_lv4child_img = pygame.image.load(path.join(char_dir, "boss_lv4child.png")).convert()
boss_lv4child_hit_img = pygame.image.load(path.join(char_dir, "boss_lv4child_hit.png")).convert()
boss_lv4child_hit_anim = [boss_lv4child_hit_img, boss_lv4child_img] * 3

cannonball1_img_0 = pygame.image.load(path.join(bullet_dir, "cannonball1_0.png")).convert()
cannonball1_img_0.set_colorkey(WHITE1)
cannonball1_img_1 = pygame.image.load(path.join(bullet_dir, "cannonball1_1.png")).convert()
cannonball1_img_1.set_colorkey(WHITE1)
cannonball1_anim = [cannonball1_img_0, cannonball1_img_1]
cannonball2_img_0 = pygame.image.load(path.join(bullet_dir, "cannonball2_0.png")).convert()
cannonball2_img_0.set_colorkey(WHITE1)
cannonball2_img_1 = pygame.image.load(path.join(bullet_dir, "cannonball2_1.png")).convert()
cannonball2_img_1.set_colorkey(WHITE1)
cannonball2_anim = [cannonball2_img_0, cannonball2_img_1]

hiteffect_anim = []
for i in range(9):
    filename = "hit_{:0>4}.png".format(i)
    filepath = path.join(hit_dir, filename)
    hit_img = pygame.image.load(filepath).convert()
    hit_img.set_colorkey(BLACK)
    hiteffect_anim.append(hit_img)

explosion_anim = dict()
for j in range(1, 12):
    explosion_anim[str(j)] = []
    for i in range(32):
        filename = "expl_{0:0>2}_{1:0>4}.png".format(j, i)
        filepath = path.join(expl_dir, filename)
        if path.isfile(filepath):
            expl_img = pygame.image.load(filepath).convert()
            expl_img.set_colorkey(BLACK)
            explosion_anim[str(j)].append(expl_img)

debriz_img = []
for i in range(16):
    filename = "debris_{}.png".format(i)
    filepath = path.join(expl_dir, filename)
    debris_img = pygame.image.load(filepath).convert()
    debris_img.set_colorkey(WHITE1)
    debriz_img.append(debris_img)

# define sprite groups
all_buttons = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
player = Player()
pointers = pygame.sprite.Group()
target_pointer = TargetPointer()
pointers.add(target_pointer)
players.add(player)
mobs = pygame.sprite.Group()
all_mobs = pygame.sprite.Group()    # including shield units
child_mobs = pygame.sprite.Group()  # for childmobs
linemobs1 = pygame.sprite.Group()
linemobs2 = pygame.sprite.Group()
linemobs3 = pygame.sprite.Group()
wallmobs1 = pygame.sprite.Group()
wallmobs2 = pygame.sprite.Group()
wallmobs3 = pygame.sprite.Group()
followermobs1 = pygame.sprite.Group()
followermobs2 = pygame.sprite.Group()
minigunmobs1 = pygame.sprite.Group()
minigunmobs2 = pygame.sprite.Group()
minigunmobs3 = pygame.sprite.Group()
shellmobs1 = pygame.sprite.Group()
shellmobs2 = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
player_cannon_balls = pygame.sprite.Group()
mob_bullets = pygame.sprite.Group()
mob_cannon_balls = pygame.sprite.Group()
explosions = pygame.sprite.Group()
debriz = pygame.sprite.Group()
items = pygame.sprite.Group()

# define level and phase
stage = 1
stage_initial_set = stage

phase_text = "LEVEL 1 / PHASE 1"
phase_bound = [0, 200, 600, 1600]
# phase_bound = [0, 6000, 12000, 18000]
phase_num = 0

max_mobs = 300  # max number of mobs on the field (except shield units)
stage1_boss_spawned = False
stage1_clear = False
stage2_boss_spawned = False
stage2_clear = False
stage3_boss_spawned = False
stage3_clear = False
stage4_boss_spawned = False
stage4_clear = False

# variables for breaktime between two stages
break_start = 0
breaktime = 20
now_break_1 = False
now_break_2 = False
now_break_3 = False
now_break_4 = False

all_sprites.add(player)
all_sprites.add(target_pointer)


def add_single_mob(mobtype, mobgroup):
    """ function for adding new mob """
    all_sprites.add(mobtype)
    mobs.add(mobtype)
    all_mobs.add(mobtype)
    mobgroup.add(mobtype)


score = 0

mainmenu_show = True
play = False
pause_ready = False
pause = False
paused_window_show = False
gameover_show = False

start_button = Button([450, 600, 300, 100], WHITE1, "START", 60)
restart_button = Button([450, 600, 300, 100], WHITE1, "RESTART", 60)
stage_select_buttons = []
for i in range(3):
    stage_select_button = Button([150 + 300 * i, 400, 300, 70], WHITE1, "Start from LEVEL {}".format(i + 2), 20)
    stage_select_buttons.append(stage_select_button)
    all_buttons.add(stage_select_button)
all_buttons.add(start_button)
all_buttons.add(restart_button)

# MAIN GAME LOOP#

while not done:
    # update screen at a specified frame rate
    clock.tick(fps)

    # EVENT CHECK #
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            click = True
        elif event.type == pygame.MOUSEBUTTONUP:
            click = False
        elif event.type == pygame.QUIT:
            done = True

    # get mouse position on screen
    curspos = pygame.mouse.get_pos()

    # showing main menu before starting
    if mainmenu_show:
        screen.fill(BLACK)
        draw_text(screen, "WAR OF SQUARES", 50, WHITE1, "midtop", screen_width // 2, 50)
        start_button.update()
        for button in stage_select_buttons:
            button.update()

        # initialize player status according to selected level
        if start_button.operate or any([button.operate for button in stage_select_buttons]):
            score = 0
            if start_button.operate:
                if stage == "test":
                    phase_bound = [0, 10000, 20000, 35000]
                    player.hp = 500
                    player.hp_full = 500
                    player.weapon_lvl = 4
                else:
                    stage = 1
                    phase_bound = [0, 200, 600, 1600]
                    player.hp = 100
                    player.hp_full = 100
                    player.weapon_lvl = 1
                start_button.operate = False
            elif stage_select_buttons[0].operate:
                stage = 2
                phase_bound = [0, 2000, 5000, 9000]
                player.hp = 150
                player.hp_full = 150
                player.weapon_lvl = 2
                stage_select_buttons[0].operate = False
            elif stage_select_buttons[1].operate:
                stage = 3
                phase_bound = [0, 4000, 10000, 18000]
                player.hp = 300
                player.hp_full = 300
                player.weapon_lvl = 3
                stage_select_buttons[1].operate = False
            elif stage_select_buttons[2].operate:
                stage = 4
                phase_bound = [0, 10000, 20000, 35000]
                player.hp = 500
                player.hp_full = 500
                player.weapon_lvl = 4
                stage_select_buttons[2].operate = False
            player.mp = 100
            player.mp_full = 100
            player.rect.center = (screen_width // 2, screen_height // 2)
            screen_center = [0, 0]
            mainmenu_show = False
            play = True
            start_button.kill()

    elif play:
        # LEVEL 1
        if stage == 1:
            if not stage1_clear:
                if score < phase_bound[1]:
                    phase_num = 0
                    phase_text = "LEVEL 1 / PHASE 1"
                    if len(mobs) < max_mobs:
                        add_single_mob(MoveLineMob1(), linemobs1)
                elif phase_bound[1] <= score < phase_bound[2]:
                    phase_num = 1
                    phase_text = "LEVEL 1 / PHASE 2"
                    max_mobs = 350
                    if len(mobs) < max_mobs:
                        if random.random() <= 0.7 and len(linemobs1) < 110:
                            add_single_mob(MoveLineMob1(), linemobs1)
                        elif len(linemobs2) < 50:
                            add_single_mob(MoveLineMob2(), linemobs2)
                elif phase_bound[2] <= score <= phase_bound[3]:
                    phase_num = 2
                    phase_text = "LEVEL 1 / PHASE 3"
                    max_mobs = 500
                    if len(mobs) < max_mobs:
                        if random.random() <= 0.6 and len(linemobs1) < 130:
                            add_single_mob(MoveLineMob1(), linemobs1)
                        elif random.random() <= 0.9 and len(linemobs2) < 60:
                            add_single_mob(MoveLineMob2(), linemobs2)
                        elif len(linemobs3) < 20:
                            add_single_mob(MoveLineMob3(), linemobs3)
                elif phase_bound[3] <= score:
                    phase_num = "boss"
                    phase_text = "LEVEL 1 / BOSS CHALLENGE"
                    if not stage1_boss_spawned:
                        boss = BossLV1()
                        all_sprites.add(boss)
                        mobs.add(boss)
                        all_mobs.add(boss)
                        stage1_boss_spawned = True
                        pointer = BossPointer()
                        all_sprites.add(pointer)
                        players.add(pointer)
                    if len(mobs) < max_mobs:
                        if random.random() <= 0.6 and len(linemobs1) < 130:
                            add_single_mob(MoveLineMob1(), linemobs1)
                        elif random.random() <= 0.9 and len(linemobs2) < 60:
                            add_single_mob(MoveLineMob2(), linemobs2)
                        elif len(linemobs3) < 20:
                            add_single_mob(MoveLineMob3(), linemobs3)

            elif now_break_1:
                if time.time() - break_start >= breaktime:
                    player.hp_full += 50
                    player.hp = player.hp_full
                    phase_bound = [0, 2000, 5000, 9000]
                    for i in range(len(phase_bound)):
                        phase_bound[i] += score
                    stage += 1
                    now_break_1 = False

        # LEVEL 2
        elif stage == 2:
            if not stage2_clear:
                if score < phase_bound[1]:
                    phase_num = 0
                    phase_text = "LEVEL 2 / PHASE 1"
                    max_mobs = 600
                    if len(mobs) < max_mobs:
                        if len(followermobs1) <= 2:
                            add_single_mob(FollowerMob1(), followermobs1)
                        generate_wall((40, 1), (40, 40), 1, wallmobs1)
                elif phase_bound[1] <= score < phase_bound[2]:
                    phase_num = 1
                    phase_text = "LEVEL 2 / PHASE 2"
                    max_mobs = 800
                    if len(mobs) < max_mobs:
                        if len(followermobs1) <= 2:
                            add_single_mob(FollowerMob1(), followermobs1)
                        if random.random() < 0.5 and len(wallmobs1) <= 500:
                            generate_wall((40, 1), (40, 40), 1, wallmobs1)
                        elif len(wallmobs2) <= 500:
                            generate_wall((40, 2), (40, 40), 2, wallmobs2)
                elif phase_bound[2] <= score <= phase_bound[3]:
                    phase_num = 2
                    phase_text = "LEVEL 2 / PHASE 3"
                    max_mobs = 1000
                    if len(mobs) < max_mobs:
                        if len(followermobs1) <= 2:
                            add_single_mob(FollowerMob1(), followermobs1)
                        if random.random() < 0.5 and len(wallmobs1) <= 300:
                            generate_wall((40, 1), (40, 40), 1, wallmobs1)
                        elif random.random() < 0.8 and len(wallmobs2) <= 200:
                            generate_wall((40, 2), (40, 40), 2, wallmobs2)
                        elif len(wallmobs3) <= 100:
                            generate_wall((20, 3), (70, 70), 3, wallmobs3)
                elif phase_bound[3] <= score:
                    phase_num = "boss"
                    phase_text = "LEVEL 2 / BOSS CHALLENGE"
                    max_mobs = 500
                    if not stage2_boss_spawned:
                        boss = BossLV2()
                        all_sprites.add(boss)
                        mobs.add(boss)
                        all_mobs.add(boss)
                        stage2_boss_spawned = True
                        pointer = BossPointer()
                        all_sprites.add(pointer)
                        players.add(pointer)
                    if len(mobs) < max_mobs:
                        if len(linemobs3) < max_mobs:
                            generate_wall((20, 3), (70, 70), 3, wallmobs3)

            elif now_break_2:
                if time.time() - break_start >= breaktime:
                    player.hp_full += 150
                    player.hp = player.hp_full
                    phase_bound = [0, 4000, 10000, 18000]
                    for i in range(len(phase_bound)):
                        phase_bound[i] += score
                    stage += 1
                    now_break_2 = False

        # LEVEL 3
        elif stage == 3:
            if stage == 3 and not stage3_clear:
                if score < phase_bound[1]:
                    phase_num = 0
                    phase_text = "LEVEL 3 / PHASE 1"
                    max_mobs = 250
                    if len(mobs) < max_mobs:
                        if random.random() <= 0.66 and len(linemobs2) < 60:
                            add_single_mob(MoveLineMob2(), linemobs2)
                        elif len(minigunmobs1) <= 30:
                            add_single_mob(MinigunMob1(), minigunmobs1)

                elif phase_bound[1] <= score < phase_bound[2]:
                    phase_num = 1
                    phase_text = "LEVEL 3 / PHASE 2"
                    max_mobs = 400
                    if len(mobs) < max_mobs:
                        if random.random() <= 0.8 and len(linemobs1) < 120:
                            add_single_mob(MoveLineMob1(), linemobs1)
                        elif len(minigunmobs1) <= 20:
                            add_single_mob(MinigunMob1(), minigunmobs1)
                        elif len(minigunmobs2) <= 15:
                            add_single_mob(MinigunMob2(), minigunmobs2)

                elif phase_bound[2] <= score <= phase_bound[3]:
                    phase_num = 2
                    phase_text = "LEVEL 3 / PHASE 3"
                    max_mobs = 450
                    if len(mobs) < max_mobs:
                        if random.random() <= 0.7 and len(linemobs1) < 120:
                            add_single_mob(MoveLineMob1(), linemobs1)
                        elif random.random() <= 0.83 and len(minigunmobs1) <= 25:
                            add_single_mob(MinigunMob1(), minigunmobs1)
                        elif random.random() <= 0.93 and len(minigunmobs2) <= 17:
                            add_single_mob(MinigunMob2(), minigunmobs2)
                        elif len(minigunmobs3) <= 13:
                            add_single_mob(MinigunMob3(), minigunmobs3)

                elif phase_bound[3] <= score:
                    phase_num = "boss"
                    phase_text = "LEVEL 3 / BOSS CHALLENGE"
                    max_mobs = 30
                    if not stage3_boss_spawned:
                        boss = BossLV3()
                        all_sprites.add(boss)
                        mobs.add(boss)
                        all_mobs.add(boss)
                        stage3_boss_spawned = True
                        pointer = BossPointer()
                        all_sprites.add(pointer)
                        players.add(pointer)
                        for mob in linemobs1:
                            mob.dead = True
                        for mob in linemobs2:
                            mob.dead = True
                        for mob in minigunmobs1:
                            mob.dead = True
                        for mob in minigunmobs2:
                            mob.dead = True
                    if len(minigunmobs3) <= max_mobs:
                        add_single_mob(MinigunMob3(), minigunmobs3)
                    if len(linemobs2) <= 200:
                        add_single_mob(MoveLineMob2(), linemobs2)

            elif now_break_3:
                if time.time() - break_start >= breaktime:
                    player.hp_full += 200
                    player.hp = player.hp_full
                    phase_bound = [0, 10000, 20000, 35000]
                    for i in range(len(phase_bound)):
                        phase_bound[i] += score
                    stage += 1
                    now_break_3 = False

        # LEVEL 4 (incomplete)
        elif stage == 4:
            if stage == 4 and not stage4_clear:
                if score < phase_bound[1]:
                    phase_num = 0
                    phase_text = "LEVEL 4 / PHASE 1"
                    max_mobs = 80
                    if len(mobs) < max_mobs:
                        if len(linemobs3) <= 77:
                            add_single_mob(MoveLineMob3(), linemobs3)
                        elif len(followermobs2) <= 3:
                            add_single_mob(FollowerMob2(), followermobs2)

                elif phase_bound[1] <= score < phase_bound[2]:
                    for mob in linemobs3:
                        mob.dead = True
                    phase_num = 1
                    phase_text = "LEVEL 4 / PHASE 2"
                    max_mobs = 100
                    if len(mobs) < max_mobs:
                        if random.random() <= 0.7 and len(linemobs2) < 70:
                            add_single_mob(MoveLineMob2(), linemobs2)
                        elif random.random() <= 0.8 and len(followermobs2) < 4:
                            add_single_mob(FollowerMob2(), followermobs2)
                        elif random.random() <= 0.925 and len(minigunmobs1) < 30:
                            add_single_mob(MinigunMob1(), minigunmobs1)
                        elif len(shellmobs1) < 18:
                            add_single_mob(ShellMob1(), shellmobs1)

                elif phase_bound[2] <= score <= phase_bound[3]:
                    for mob in linemobs2:
                        mob.dead = True
                    for mob in minigunmobs1:
                        mob.dead = True
                    phase_num = 2
                    phase_text = "LEVEL 4 / PHASE 3"
                    max_mobs = 60
                    if len(mobs) < max_mobs:
                        if random.random() <= 0.25 and len(minigunmobs3) < 15:
                            add_single_mob(MinigunMob3(), minigunmobs3)
                        elif random.random() <= 0.3 and len(followermobs2) < 4:
                            add_single_mob(FollowerMob2(), followermobs2)
                        elif random.random() <= 0.7 and len(shellmobs1) < 22:
                            add_single_mob(ShellMob1(), shellmobs1)
                        elif len(shellmobs2) < 15:
                            add_single_mob(ShellMob2(), shellmobs2)

                elif phase_bound[3] <= score:
                    phase_num = "boss"
                    phase_text = "LEVEL 4 / BOSS CHALLENGE"
                    max_mobs = 30
                    if not stage4_boss_spawned:
                        boss = BossLV4()
                        all_sprites.add(boss)
                        mobs.add(boss)
                        all_mobs.add(boss)
                        stage4_boss_spawned = True
                        pointer = BossPointer()
                        all_sprites.add(pointer)
                        players.add(pointer)
                        for mob in linemobs3:
                            mob.dead = True
                        for mob in followermobs2:
                            mob.dead = True
                        for mob in shellmobs1:
                            if random.random() < 0.5:
                                mob.dead = True
                        for mob in shellmobs2:
                            if random.random() < 0.5:
                                mob.dead = True
                        for mob in minigunmobs3:
                            if random.random() < 0.5:
                                mob.dead = True
                    if random.random() <= 0.33 and len(minigunmobs3) < 12:
                        add_single_mob(MinigunMob3(), minigunmobs3)
                    elif random.random() <= 0.66 and len(shellmobs1) < 12:
                        add_single_mob(ShellMob1(), shellmobs1)
                    elif len(shellmobs2) < 12:
                        add_single_mob(ShellMob2(), shellmobs2)

        # Stage for testing mobs (current: LEVEL 4)
        elif stage == "test":
            phase_text = "TEST"
            phase_bound = [0, 10000000000000000000]
            max_mobs = 30
            if not stage4_boss_spawned:
                boss = BossLV4()
                all_sprites.add(boss)
                mobs.add(boss)
                all_mobs.add(boss)
                stage4_boss_spawned = True
                pointer = BossPointer()
                all_sprites.add(pointer)
                players.add(pointer)
                for mob in linemobs3:
                    mob.dead = True
                for mob in followermobs2:
                    mob.dead = True
                for mob in shellmobs1:
                    if random.random() < 0.5:
                        mob.dead = True
                for mob in shellmobs2:
                    if random.random() < 0.5:
                        mob.dead = True
                for mob in minigunmobs3:
                    if random.random() < 0.5:
                        mob.dead = True
            if random.random() <= 0.33 and len(minigunmobs3) < 12:
                add_single_mob(MinigunMob3(), minigunmobs3)
            elif random.random() <= 0.66 and len(shellmobs1) < 12:
                add_single_mob(ShellMob1(), shellmobs1)
            elif len(shellmobs2) < 12:
                add_single_mob(ShellMob2(), shellmobs2)


        """ dealing with all collision events """
        # collision between player's bullets and all mobs
        hits = pygame.sprite.groupcollide(all_mobs, player_bullets, False, True)
        for hit in hits:
            hit.hit = True
            for b in hits[hit]:
                hiteff = HitEffect(b.rect.center, (round(b.rect.width * 32 / 5), round(b.rect.height * 32 / 5)))
                all_sprites.add(hiteff)
                players.add(hiteff)
                hit.hp -= b.power * random.uniform(0.5, 1.5)

        # collision between player's cannonball and all mobs
        hits = pygame.sprite.groupcollide(all_mobs, player_cannon_balls, False, True, pygame.sprite.collide_circle)
        for hit in hits:
            hit.hit = True
            for b in hits[hit]:
                explosion_type = random.randrange(1, 12)
                explosion = Explosion(b.rect.center, explosion_type, (round(b.size[0] * 4), round(b.size[1] * 4)))
                all_sprites.add(explosion)
                explosions.add(explosion)
                hit.hp -= b.power * random.uniform(0.8, 1.2)
                if not b.released:
                    b.shock_range = player.max_shock_range * (b.power / b.max_power)
                    player.last_cannon_shoot = time.time()
                    player.cannon_shoot = False
                for mo in all_mobs:
                    if mo != hit:
                        dist = distance(b.rect.center, mo.rect.center)
                        rang = b.shock_range
                        if dist <= rang:
                            mo.hit = True
                            splash_power = player.max_cannon_power * ((rang - dist) ** 2) / (1 * (rang ** 2))
                            mo.hp -= splash_power * random.uniform(0.8, 1.2)
                for ch in child_mobs:
                    if ch != hit:
                        dist = distance(b.rect.center, ch.rect.center)
                        rang = b.shock_range
                        if dist <= rang:
                            ch.hit = True
                            splash_power = player.max_cannon_power * ((rang - dist) ** 2) / (1 * (rang ** 2))
                            ch.hp -= splash_power * random.uniform(0.8, 1.2)

        # collision between player and mob bullets
        hits = pygame.sprite.spritecollide(player, mob_bullets, True)
        for hit in hits:
            hiteff = HitEffect(hit.rect.center, (round(hit.rect.width * 32 / 5), round(hit.rect.height * 32 / 5)))
            all_sprites.add(hiteff)
            players.add(hiteff)
            player.hp -= hit.power

        # collision between player and mob cannonballs
        hits = pygame.sprite.spritecollide(player, mob_cannon_balls, True, pygame.sprite.collide_circle)
        for hit in hits:
            explosion_type = random.randrange(1, 12)
            explosion = Explosion(hit.rect.center, explosion_type, (round(hit.size[0] * 5), round(hit.size[1] * 5)))
            all_sprites.add(explosion)
            explosions.add(explosion)
            player.hp -= hit.power

        # collision between player and all mobs
        hits = pygame.sprite.spritecollide(player, all_mobs, False)
        for hit in hits:
            if not hit.dead:
                if hit.damage < player.hp:
                    hit.dead = True
                hit.no_points = True
                hit.update()
                player.hp -= hit.damage

        # collision between player and all child mobs
        hits = pygame.sprite.spritecollide(player, child_mobs, False)
        for hit in hits:
            if not hit.dead:
                if hit.damage < player.hp:
                    hit.dead = True
                hit.no_points = True
                player.hp -= hit.damage

        # player dead and game over
        if player.hp <= 0:
            player.hp = 0
            play = False
            gameover_show = True

        # when player collect items
        hits = pygame.sprite.spritecollide(player, items, True)
        for hit in hits:
            hit.buff()


        """ pause control """
        p_pressed = pygame.key.get_pressed()[pygame.K_p]
        if p_pressed:
            pause_ready = True
        if pause_ready:
            if not p_pressed:
                pause_ready = False
                pause = not pause


        """ update all sprites per frame when not paused """
        if not pause:
            paused_window_show = False
            all_sprites.update()
        else:
            paused_window_show = True


        """ draw all objects on screen """
        screen.fill(BLACK)
        # draw background gridline
        for i in range(-round((map_size / 2 - 0.5) * screen_width), round((map_size / 2 + 0.5) * screen_width), 200):
            pygame.draw.line(screen, WHITE3,
                             [i - screen_center[0], -round((map_size / 2 - 0.5) * screen_height) - screen_center[1]],
                             [i - screen_center[0], round((map_size / 2 + 0.5) * screen_height) - screen_center[1]], 2)
        for i in range(-round((map_size / 2 - 0.5) * screen_height), round((map_size / 2 + 0.5) * screen_height), 200):
            pygame.draw.line(screen, WHITE3,
                             [-round((map_size / 2 - 0.5) * screen_width) - screen_center[0], i - screen_center[1]],
                             [round((map_size / 2 + 0.5) * screen_width) - screen_center[0], i - screen_center[1]], 2)

        # draw all sprites
        debriz.draw(screen)
        items.draw(screen)
        all_mobs.draw(screen)
        player_bullets.draw(screen)
        mob_bullets.draw(screen)
        mob_cannon_balls.draw(screen)
        players.draw(screen)
        player_cannon_balls.draw(screen)
        explosions.draw(screen)
        pointers.draw(screen)

        # draw player hp bar on topleft of screen
        pygame.draw.rect(screen, BLACK, [20, 10, 200, 15], 0)
        pygame.draw.rect(screen, GREEN1, [20, 10, round(200 * (max(player.hp / player.hp_full, 0))), 15], 0)
        pygame.draw.rect(screen, WHITE1, [20, 10, 200, 15], 2)

        # draw player mp bar and skill cooltime bar right under of hp bar
        pygame.draw.rect(screen, BLACK, [20, 35, 200, 15], 0)
        pygame.draw.rect(screen, BLUE1, [20, 35, round(200 * (max(player.mp / player.mp_full, 0))), 15], 0)
        if player.cannon_shoot:
            pygame.draw.rect(screen, RED1, [20, 45, round(200 * (max(player.cannon_cooltime / (player.cannon_cooltime_rate * player.max_cannon_power / player.cannon_charge_rate), 0))), 5], 0)
        else:
            pygame.draw.rect(screen, RED1, [20, 45, round(200 * (max((player.cannon_cooltime - (time.time() - player.last_cannon_shoot)) / (player.cannon_cooltime_rate * player.max_cannon_power / player.cannon_charge_rate), 0))), 5], 0)
        pygame.draw.rect(screen, WHITE1, [20, 35, 200, 15], 2)

        # draw yellow bar on top of screen
        # before boss challenge: displays phase progress
        # during boss challenge: always full
        # after boss challenge: displays breaktime
        if phase_num == "boss":
            if now_break_1 or now_break_2 or now_break_3:
                pygame.draw.rect(screen, YELLOW1, [screen_width // 2 - 100, 10, round(200 * (breaktime - time.time() + break_start) / breaktime), 15], 0)
            else:
                pygame.draw.rect(screen, YELLOW1, [screen_width // 2 - 100, 10, 200, 15], 0)
        else:
            pygame.draw.rect(screen, BLACK, [screen_width // 2 - 100, 10, 200, 15], 0)
            pygame.draw.rect(screen, YELLOW1, [screen_width // 2 - 100, 10, round(200 * (
                        (min(score - phase_bound[phase_num], phase_bound[phase_num + 1] - phase_bound[phase_num])) / (
                            phase_bound[phase_num + 1] - phase_bound[phase_num]))), 15], 0)
        pygame.draw.rect(screen, WHITE1, [screen_width // 2 - 100, 10, 200, 15], 2)

        # draw boss's hp only during boss challenge
        if stage1_boss_spawned or stage2_boss_spawned or stage3_boss_spawned or stage4_boss_spawned:
            pygame.draw.rect(screen, BLACK, [screen_width - 220, 10, 200, 15], 0)
            pygame.draw.rect(screen, RED1, [screen_width - 220, 10, round(200 * (boss.hp / boss.hp_full)), 15], 0)
            pygame.draw.rect(screen, WHITE1, [screen_width - 220, 10, 200, 15], 2)

        # draw score and phase text
        draw_text(screen, phase_text, 20, WHITE1, "midtop", screen_width // 2, 30)
        draw_text(screen, "SCORE : {}".format(round(score, 2)), 15, WHITE1, "topleft", 20, 65)

        # draw paused window when paused
        if paused_window_show:
            pygame.draw.rect(screen, BLACK, [200, 300, 800, 200], 0)
            pygame.draw.rect(screen, WHITE1, [200, 300, 800, 200], 4)
            draw_text(screen, "PAUSED", 50, WHITE1, "midtop", 600, 330)
            draw_text(screen, "Press 'P' to continue", 20, WHITE1, "midtop", 600, 430)

    # display gameover scene
    elif gameover_show:
        screen.fill(BLACK)
        draw_text(screen, "GAME OVER", 50, WHITE1, "midtop", screen_width // 2, 50)
        restart_button.update()

        # clear the entire map and initialize all progress
        if restart_button.operate:
            for pl in players:
                if pl != player:
                    pl.kill()
            for mo in all_mobs:
                mo.kill()
            for ch in child_mobs:
                ch.kill()
            for de in debriz:
                de.kill()
            for bu in player_bullets:
                bu.kill()
            for ca in player_cannon_balls:
                ca.kill()
            for bu in mob_bullets:
                bu.kill()
            for ca in mob_cannon_balls:
                ca.kill()
            for ex in explosions:
                ex.kill()
            for it in items:
                it.kill()
            stage1_boss_spawned = False
            stage1_clear = False
            stage2_boss_spawned = False
            stage2_clear = False
            stage3_boss_spawned = False
            stage3_clear = False
            stage4_boss_spawned = False
            stage4_clear = False
            stage = stage_initial_set
            gameover_show = False
            mainmenu_show = True
            restart_button.operate = False
            restart_button.kill()

    # apply all drawings
    pygame.display.flip()

pygame.quit()
exit()
