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
spawn_dir = path.join(path.dirname(__file__), 'img', 'spawneffect')

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


# Constants

SCREEN_FIELD_SIZE_RATIO = 3         # screen_size * SCREEN_FIELD_SIZE_RATIO = field_size
MOB_HP_BAR_SHOW_DURATION = 3        # In seconds
# All projectiles shot from mobs(not bosses) can exist in this range of margin outside of screen
MOB_PROJECTILE_VALID_MARGIN = 200
EXPLOSION_TYPES = 11                # Number of kinds of explosion animations
ITEM_DROP_PROBABILITY = 0.02        # Probability of dropping an item when a mob is killed
MOB_EXPLOSION_SIZE_RATIO = 3        # mob_size * MOB_EXPLOSION_SIZE_RATIO = explosion_size
BULLET_HITEFFECT_SIZE_RATIO = 9     # bullet_size * BULLET_HITEFFECT_SIZE_RATIO = hiteffect_size

NONZERO = .00000000001              # This will be added to some variables to avoid ZerDivisionError


# define screen size
screen_width = 1200
screen_height = 800

# define entire field size
field_width = screen_width * SCREEN_FIELD_SIZE_RATIO
field_height = screen_height * SCREEN_FIELD_SIZE_RATIO

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


def is_aligned(pos_1, pos_2, pos_3, error):
    """
    checks whether pos_2 is aligned between pos_1 ans pos_3
    """
    coeff_a = pos_1[1] - pos_3[1]
    coeff_b = pos_3[0] - pos_1[0]
    coeff_c = pos_1[0] * pos_3[1] - pos_3[0] * pos_1[1]

    if coeff_a == 0 and coeff_b == 0:
        return False

    distance_from_line_to_point = abs(coeff_a * pos_2[0] + coeff_b * pos_2[1] + coeff_c) / math.sqrt(coeff_a ** 2 + coeff_b ** 2)

    return distance_from_line_to_point <= error and ((pos_1[0] <= pos_2[0] <= pos_3[0]) or (pos_3[0] <= pos_2[0] <= pos_1[0])) and ((pos_1[1] <= pos_2[1] <= pos_3[1]) or (pos_3[1] <= pos_2[1] <= pos_1[1]))


class Button(pygame.sprite.Sprite):
    def __init__(self, btn_pos_size, btn_color, text, text_size, btnbck_color=(0, 0, 0), active=True):
        pygame.sprite.Sprite.__init__(self)
        self.btn_color = btn_color
        self.btnbck_color_orig = btnbck_color
        self.btnbck_color = btnbck_color
        self.mouse_on_color = []
        self.clicked_color = []
        self.rect = btn_pos_size
        self.text = text
        self.text_size = text_size
        self.active = active
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
        if self.active:
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
        else:
            pygame.draw.rect(screen, self.btnbck_color, self.rect, 0)
            pygame.draw.rect(screen, self.clicked_color, self.rect, 2)
            draw_text(screen, self.text, self.text_size, self.clicked_color, "center", self.rect[0] + self.rect[2] // 2, self.rect[1] + self.rect[3] // 2)
            self.btnbck_color = self.btnbck_color_orig
            self.pressed = False
            self.released = False
            self.operate = False

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (30, 30)
        self.image = pygame.transform.scale(player_img, self.size)
        self.rect = self.image.get_rect()
        self.rect.center = [screen_width // 2, screen_height // 2]
        self.abs_x = screen_width // 2
        self.abs_y = screen_height // 2

        self.stat_points = 0

        # List of HP values sorted by upgrade level
        self.hp_list = [100, 150, 300, 500, 750, 1000, 1300, 1600, 2000, 2500]
        self.hp_lvl = 1
        self.hp = self.hp_list[self.hp_lvl - 1]
        self.hp_full = self.hp
        # HP will be regenerated by full HP divided by 'hp_regen_div' value at every frame
        self.hp_regen_div = 3000

        # List of MP values sorted by upgrade level
        self.mp_list = [100, 150, 200, 300, 400, 600, 800, 1100, 1400, 1800]
        self.mp_lvl = 1
        self.mp = self.mp_list[self.mp_lvl - 1]
        self.mp_full = self.mp
        # MP will be regenerated by full MP divided by 'mp_regen_div' value at every frame
        self.mp_regen_div = 2000

        # List of pickup range values sorted by upgrade level
        self.pick_range_list = [60, 80, 100, 120, 140, 160, 180, 200, 220, 240]
        self.pick_range_lvl = 1
        self.pick_range = self.pick_range_list[self.pick_range_lvl - 1]

        self.main_weapon_lvl = 1
        self.bullet_size_s = [5, 5]
        self.bullet_size_m = [7, 7]
        self.bullet_size_l = [9, 9]
        self.bullet_size_xl = [11, 11]

        # List of power of charging cannon values sorted by upgrade level
        self.charging_cannon_power_list = [120, 150, 180, 220, 270, 330, 400, 480, 580, 700]
        self.charging_cannon_lvl = 1
        self.max_cannon_power = self.charging_cannon_power_list[self.charging_cannon_lvl - 1]
        self.cannon_charge_rate = self.max_cannon_power / 40
        self.max_shock_range = 27 * math.sqrt(self.max_cannon_power)

        self.speed = 6
        self.x_speed = 0
        self.y_speed = 0
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
            if -(SCREEN_FIELD_SIZE_RATIO - 1) * screen_width / 2 < screen_center[0] < (SCREEN_FIELD_SIZE_RATIO - 1) * screen_width / 2:
                screen_center[0] -= self.speed
            elif screen_center[0] >= (SCREEN_FIELD_SIZE_RATIO - 1) * screen_width / 2 and self.rect.center[0] <= screen_width / 2:
                screen_center[0] -= self.speed
            else:
                self.x_speed = -self.speed
            self.abs_x -= self.speed
        if keystate[pygame.K_d] and self.rect.center[0] <= screen_width:
            if -(SCREEN_FIELD_SIZE_RATIO - 1) * screen_width / 2 < screen_center[0] < (SCREEN_FIELD_SIZE_RATIO - 1) * screen_width / 2:
                screen_center[0] += self.speed
            elif screen_center[0] <= -(SCREEN_FIELD_SIZE_RATIO - 1) * screen_width / 2 and self.rect.center[0] >= screen_width / 2:
                screen_center[0] += self.speed
            else:
                self.x_speed = self.speed
            self.abs_x += self.speed
        if keystate[pygame.K_w] and self.rect.center[1] >= 0:
            if -(SCREEN_FIELD_SIZE_RATIO - 1) * screen_height / 2 < screen_center[1] < (SCREEN_FIELD_SIZE_RATIO - 1) * screen_height / 2:
                screen_center[1] -= self.speed
            elif screen_center[1] >= (SCREEN_FIELD_SIZE_RATIO - 1) * screen_height / 2 and self.rect.center[1] <= screen_height / 2:
                screen_center[1] -= self.speed
            else:
                self.y_speed = -self.speed
            self.abs_y -= self.speed
        if keystate[pygame.K_s] and self.rect.center[1] <= screen_height:
            if -(SCREEN_FIELD_SIZE_RATIO - 1) * screen_height / 2 < screen_center[1] < (SCREEN_FIELD_SIZE_RATIO - 1) * screen_height / 2:
                screen_center[1] += self.speed
            elif screen_center[1] <= -(SCREEN_FIELD_SIZE_RATIO - 1) * screen_height / 2 and self.rect.center[1] >= screen_height / 2:
                screen_center[1] += self.speed
            else:
                self.y_speed = self.speed
            self.abs_y += self.speed
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed + round(field_shift_pos)

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
            self.hp += self.hp_full / self.hp_regen_div
        if self.mp <= 0:
            self.mp = 0
        if self.mp <= self.mp_full:
            self.mp += self.mp_full / self.mp_regen_div

    def shoot(self, target_pos):
        dist_x = target_pos[0] - self.rect.center[0]
        dist_y = target_pos[1] - self.rect.center[1]
        angle = math.atan2(dist_y, dist_x)
        if dist_x != 0 or dist_y != 0:
            # lvl 1: shoots 1 bullet with power 1 per interval
            if self.main_weapon_lvl == 1:
                PlayerBullet(1, self.bullet_size_s, angle, 15)

            # lvl 2: shoots 2 bullets with power 1 per interval
            elif self.main_weapon_lvl == 2:
                PlayerBullet(1, self.bullet_size_s, angle + math.radians(5), 15)
                PlayerBullet(1, self.bullet_size_s, angle - math.radians(5), 15)

            # lvl 3: shoots 3 bullets with power 1 per interval
            elif self.main_weapon_lvl == 3:
                PlayerBullet(1, self.bullet_size_s, angle, 15)
                PlayerBullet(1, self.bullet_size_s, angle + math.radians(10), 15)
                PlayerBullet(1, self.bullet_size_s, angle - math.radians(10), 15)

            # lvl 4: shoots 4 bullets with power 1 per interval
            elif self.main_weapon_lvl == 4:
                PlayerBullet(1, self.bullet_size_s, angle + math.radians(1), 15)
                PlayerBullet(1, self.bullet_size_s, angle - math.radians(1), 15)
                PlayerBullet(1, self.bullet_size_s, angle + math.radians(10), 15)
                PlayerBullet(1, self.bullet_size_s, angle - math.radians(10), 15)

            # lvl 5: shoots 2 bullets with power 2 and 2 bullets with power 1 per interval
            elif self.main_weapon_lvl == 5:
                PlayerBullet(2, self.bullet_size_m, angle + math.radians(1), 20)
                PlayerBullet(2, self.bullet_size_m, angle - math.radians(1), 20)
                PlayerBullet(1, self.bullet_size_s, angle + math.radians(10), 15)
                PlayerBullet(1, self.bullet_size_s, angle - math.radians(10), 15)

            # lvl 6: 2x3 + 1x2 per interval
            elif self.main_weapon_lvl == 6:
                PlayerBullet(2, self.bullet_size_m, angle, 20)
                PlayerBullet(2, self.bullet_size_m, angle + math.radians(2), 20)
                PlayerBullet(2, self.bullet_size_m, angle - math.radians(2), 20)
                PlayerBullet(1, self.bullet_size_s, angle + math.radians(10), 15)
                PlayerBullet(1, self.bullet_size_s, angle - math.radians(10), 15)

            # lvl 7: 4x1 + 2x2 + 1x2 per interval
            elif self.main_weapon_lvl == 7:
                PlayerBullet(4, self.bullet_size_l, angle, 30)
                PlayerBullet(2, self.bullet_size_m, angle + math.radians(6), 20)
                PlayerBullet(2, self.bullet_size_m, angle - math.radians(6), 20)
                PlayerBullet(1, self.bullet_size_s, angle + math.radians(10), 15)
                PlayerBullet(1, self.bullet_size_s, angle - math.radians(10), 15)

            # lvl 8: 4x2 + 2x2 + 1x2 per interval
            elif self.main_weapon_lvl == 8:
                PlayerBullet(4, self.bullet_size_l, angle + math.radians(1), 30)
                PlayerBullet(4, self.bullet_size_l, angle - math.radians(1), 30)
                PlayerBullet(2, self.bullet_size_m, angle + math.radians(6), 20)
                PlayerBullet(2, self.bullet_size_m, angle - math.radians(6), 20)
                PlayerBullet(1, self.bullet_size_s, angle + math.radians(10), 15)
                PlayerBullet(1, self.bullet_size_s, angle - math.radians(10), 15)

            # lvl 9: 4x2 + 2x4 per interval
            elif self.main_weapon_lvl == 9:
                PlayerBullet(4, self.bullet_size_l, angle + math.radians(1), 30)
                PlayerBullet(4, self.bullet_size_l, angle - math.radians(1), 30)
                PlayerBullet(2, self.bullet_size_m, angle + math.radians(6), 20)
                PlayerBullet(2, self.bullet_size_m, angle - math.radians(6), 20)
                PlayerBullet(2, self.bullet_size_m, angle + math.radians(10), 20)
                PlayerBullet(2, self.bullet_size_m, angle - math.radians(10), 20)

            # lvl 10: 8x2 + 4x2 + 2x2 per interval
            elif self.main_weapon_lvl == 10:
                PlayerBullet(8, self.bullet_size_xl, angle + math.radians(2), 40)
                PlayerBullet(8, self.bullet_size_xl, angle - math.radians(2), 40)
                PlayerBullet(4, self.bullet_size_l, angle + math.radians(6), 30)
                PlayerBullet(4, self.bullet_size_l, angle - math.radians(6), 30)
                PlayerBullet(2, self.bullet_size_m, angle + math.radians(10), 20)
                PlayerBullet(2, self.bullet_size_m, angle - math.radians(10), 20)


class TargetPointer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (30, 30)
        self.image = pygame.transform.scale(targetpointer_img, self.size)
        self.rect = self.image.get_rect()
        self.rect.center = curspos

    def update(self):
        self.rect.center = curspos


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, power, size, angle, speed):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.color_orig = BLUE1
        self.color = self.color_orig
        self.image = pygame.Surface(self.size)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.power = power
        self.rect.center = player.rect.center
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.speed = speed
        self.speedx = self.speed * math.cos(angle)
        self.speedy = self.speed * math.sin(angle)

        all_sprites.add(self)
        player_bullets.add(self)

    def update(self):
        self.abs_x += self.speedx
        self.abs_y += self.speedy
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        if self.color == CYAN1:
            self.color = self.color_orig
            self.image.fill(self.color)
        else:
            self.color = CYAN1
            self.image.fill(self.color)
        if not (-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.rect.center[0] < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width and
                -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.rect.center[1] < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height):
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
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        if self.color == WHITE1:
            self.color = self.color_orig
            self.image.fill(self.color)
        else:
            self.color = WHITE1
            self.image.fill(self.color)
        if not (-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.rect.center[0] < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width and
                -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.rect.center[1] < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height):
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
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        if self.glow:
            if self.color == WHITE1:
                self.color = self.color_orig
                self.image.fill(self.color)
            else:
                self.color = WHITE1
                self.image.fill(self.color)
        if not (-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.rect.center[0] < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width and
                -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.rect.center[1] < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height):
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
        self.mp_usage = self.max_power / 100
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
            player.mp -= self.mp_usage
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
                self.power = round(self.power)
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
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

        if self.imagenum == 0:
            self.imagenum = 1
            self.image = pygame.transform.scale(cannonball1_anim[self.imagenum], self.size)
        else:
            self.imagenum = 0
            self.image = pygame.transform.scale(cannonball1_anim[self.imagenum], self.size)
        if not (-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.rect.center[0] < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width and
                -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.rect.center[1] < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height):
            self.kill()


class MobExplodingCannonBall1(pygame.sprite.Sprite):
    def __init__(self, pos, angle, power, speed, size=(20, 20)):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
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
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        if self.imagenum == 0:
            self.imagenum = 1
            self.image = pygame.transform.scale(cannonball2_anim[self.imagenum], self.size)
        else:
            self.imagenum = 0
            self.image = pygame.transform.scale(cannonball2_anim[self.imagenum], self.size)
        if not (-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.rect.center[0] < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width and
                -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.rect.center[1] < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height):
            self.kill()


class MobChargingCannonBall1(pygame.sprite.Sprite):
    def __init__(self, pos, power, speed, parent):
        pygame.sprite.Sprite.__init__(self)
        self.size = [1, 1]
        self.imagenum = 0
        self.image = pygame.transform.scale(cannonball3_anim[self.imagenum], self.size)
        self.rect = self.image.get_rect()
        self.power = power
        self.rect.center = pos
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.angle = 0
        self.speed = speed
        self.speedx = 0
        self.speedy = 0
        self.released = False
        self.parent = parent

    def update(self):
        self.imagenum = not self.imagenum
        self.image = pygame.transform.scale(cannonball3_anim[self.imagenum], self.size)

        if not self.released:
            if self.parent.dead:
                self.kill()

            self.size = [s + 1 for s in self.size]
            self.rect = self.image.get_rect()
            self.rect.center = self.parent.rect.center
            if self.size[0] == 20:
                self.abs_x = self.rect.x + screen_center[0]
                self.abs_y = self.rect.y + screen_center[1]
                dist_x = player.rect.center[0] - self.parent.rect.center[0]
                dist_y = player.rect.center[1] - self.parent.rect.center[1]
                self.angle = math.atan2(dist_y, dist_x)

                self.speedx = self.speed * math.cos(self.angle)
                self.speedy = self.speed * math.sin(self.angle)
                self.released = True

        else:
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

        if not (-MOB_PROJECTILE_VALID_MARGIN < self.rect.center[0] < screen_width + MOB_PROJECTILE_VALID_MARGIN and
                -MOB_PROJECTILE_VALID_MARGIN < self.rect.center[1] < screen_height + MOB_PROJECTILE_VALID_MARGIN):
            self.kill()


class MobChargingCannonBall2(pygame.sprite.Sprite):
    def __init__(self, pos, max_size, charge_time, power, speed, parent, relative_pos=(0, 0), aim_to_player=True, angle=0.0):
        pygame.sprite.Sprite.__init__(self)
        self.size = [1, 1]
        self.max_size = max_size
        self.imagenum = 0
        self.image = pygame.transform.scale(cannonball2_anim[self.imagenum], self.size)
        self.rect = self.image.get_rect()
        self.charge_time = charge_time
        self.charge_frames = round(self.charge_time * fps)
        self.charged_frames = 0
        self.power = power
        self.relative_pos = relative_pos
        self.rect.center = [pos[0] + self.relative_pos[0], pos[1] + self.relative_pos[1]]
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.angle = angle
        self.speed = speed
        self.speedx = 0
        self.speedy = 0
        self.released = False
        self.parent = parent
        self.aim_to_player = aim_to_player

    def update(self):
        self.imagenum = not self.imagenum
        self.image = pygame.transform.scale(cannonball2_anim[self.imagenum], self.size)

        if not self.released:
            if self.parent.dead:
                self.kill()

            if self.size[0] < self.max_size:
                self.size = [s + 1 for s in self.size]
                self.rect = self.image.get_rect()
            self.rect.center = [self.parent.rect.centerx + self.relative_pos[0], self.parent.rect.centery + self.relative_pos[1]]
            self.charged_frames += 1
            if self.size[0] == self.max_size and self.charged_frames >= self.charge_frames:
                self.abs_x = self.rect.x + screen_center[0]
                self.abs_y = self.rect.y + screen_center[1]
                if self.aim_to_player:
                    dist_x = player.rect.center[0] - self.parent.rect.center[0]
                    dist_y = player.rect.center[1] - self.parent.rect.center[1]
                    self.angle = math.atan2(dist_y, dist_x)

                self.speedx = self.speed * math.cos(self.angle)
                self.speedy = self.speed * math.sin(self.angle)
                self.released = True

        else:
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

        if not (-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.rect.center[0] < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width and
                -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.rect.center[1] < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height):
            self.kill()


class BossPointer(pygame.sprite.Sprite):
    # points to boss's direction when boss spawned
    def __init__(self, boss):
        pygame.sprite.Sprite.__init__(self)
        self.size = (80, 15)
        self.image_orig = pygame.transform.scale(bosspointer_img, self.size)
        self.image_orig.set_colorkey(WHITE1)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center
        self.targeting_boss = boss

    def update(self):
        self.rect.center = player.rect.center
        dist_x = self.targeting_boss.rect.center[0] - player.rect.center[0]
        dist_y = self.targeting_boss.rect.center[1] - player.rect.center[1]
        angle = math.degrees(math.atan2(dist_y, dist_x))
        new_image = pygame.transform.rotate(self.image_orig, -angle)
        old_center = self.rect.center
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center


class MoveLineMob(pygame.sprite.Sprite):
    """
    The parent sprite of all `MoveLineMob` type enemies
    """
    def __init__(self, size, debris_size, debris_speed, norm_image, hit_anim, speed, damage, hp, points):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.debris_size = debris_size
        self.debris_speed = debris_speed
        self.norm_image = norm_image
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = hit_anim
        self.rect = self.image.get_rect()
        self.speed = speed
        self.damage = damage
        self.hit = False
        self.hitcount = 0
        self.hp = hp
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = points
        self.no_points = False

        self.abs_x = self.abs_y = 0

        self.spawned = False
        self.spawn_effect = None

        self.angle = random.uniform(-math.pi, math.pi)
        self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
        self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        self.speedx = self.speed * math.cos(self.angle)
        self.speedy = self.speed * math.sin(self.angle)

        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

        self.spawned = False
        self.spawn_effect = SpawnEffect(self.rect.center, self.size)
        all_sprites.add(self.spawn_effect)
        spawns.add(self.spawn_effect)

    def update(self):
        if not self.spawned:
            if self.spawn_effect.complete:
                self.spawned = True
                self.spawn_effect.kill()
                all_mobs.add(self)
                self.rect.x = round(self.abs_x - screen_center[0])
                self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            return
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        if not self.dead and self.spawned:
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            if not (-self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width and
                    -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height):
                if self.abs_x <= -self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width:
                    self.abs_x = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - 1
                elif self.abs_x >= (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width:
                    self.abs_x = -self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height:
                    self.abs_y = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - 1
                else:
                    self.abs_y = -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height + 1
                self.speedx = self.speed * math.cos(self.angle)
                self.speedy = self.speed * math.sin(self.angle)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class MoveLineMob1(MoveLineMob):
    """
    just moves through straight line with random direction and random speed
    does not attack player
    """
    group = pygame.sprite.Group()

    def __init__(self):
        MoveLineMob.__init__(self, [30, 30], 16, random.randrange(10, 15), linemob1_img, linemob1_hit_anim, random.randrange(5, 10), 15, 1, 5)

        self.group.add(self)


class MoveLineMob2(MoveLineMob):
    """
    just moves through straight line with random direction and random speed
    does not attack player
    """
    group = pygame.sprite.Group()

    def __init__(self):
        MoveLineMob.__init__(self, [40, 40], 20, random.randrange(12, 18), linemob2_img, linemob2_hit_anim, random.randrange(3, 8), 37, 5, 35)

        self.group.add(self)


class MoveLineMob3(MoveLineMob):
    """
    just moves through straight line with random direction and random speed
    does not attack player
    """
    group = pygame.sprite.Group()

    def __init__(self):
        MoveLineMob.__init__(self, [80, 80], 26, random.randrange(14, 20), linemob3_img, linemob3_hit_anim, random.randrange(2, 5), 134, 20, 180)

        self.group.add(self)


class WallMobUnit(pygame.sprite.Sprite):
    """
    The parent sprite of all `WallMobUnit` type enemies

    the single unit of wall
    make up a large wall with themselves and move up, down, left or right
    wall-generating function is defined separately
    """

    def __init__(self, unitsize, debris_size, debris_speed, norm_image, hit_anim, movetype, pos, speed, damage, hp, points):
        pygame.sprite.Sprite.__init__(self)
        self.unitsize = unitsize
        self.debris_size = debris_size
        self.debris_speed = debris_speed
        self.norm_image = norm_image
        self.image = pygame.transform.scale(self.norm_image, self.unitsize)
        self.hit_anim = hit_anim
        self.rect = self.image.get_rect()
        self.pos = pos
        self.abs_x = self.pos[0]
        self.abs_y = self.pos[1]
        self.speed = speed
        self.damage = damage
        self.hit = False
        self.hitcount = 0
        self.hp = hp
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = points
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
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.unitsize)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            if (self.movetype == 1 and self.abs_y > (
                    SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height + self.rect.height) \
                    or (self.movetype == 2 and self.abs_y < -self.rect.height * 2 - (
                    SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height) \
                    or (self.movetype == 3 and self.abs_x > (
                    SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width + self.rect.width) \
                    or (self.movetype == 4 and self.abs_x < -self.rect.width * 2 - (
                    SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width):
                self.kill()
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.unitsize[0] + self.unitsize[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt,
                      self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]],
                            get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.unitsize[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.unitsize[1] * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class WallMobUnit1(WallMobUnit):
    """
    A child class of `WallMobUnit`
    """
    group = pygame.sprite.Group()

    def __init__(self, movetype, pos, speed):
        WallMobUnit.__init__(self, [40, 40], 18, random.randrange(10, 15), wallmob1_img, wallmob1_hit_anim, movetype, pos, speed, 13, 2, 10)

        self.group.add(self)


class WallMobUnit2(WallMobUnit):
    """
    A child class of `WallMobUnit`
    """
    group = pygame.sprite.Group()

    def __init__(self, movetype, pos, speed):
        WallMobUnit.__init__(self, [40, 40], 20, random.randrange(10, 15), wallmob2_img, wallmob2_hit_anim, movetype, pos, speed, 27, 3, 17)

        self.group.add(self)


class WallMobUnit3(WallMobUnit):
    """
    A child class of `WallMobUnit`
    """
    group = pygame.sprite.Group()

    def __init__(self, movetype, pos, speed):
        WallMobUnit.__init__(self, [70, 70], 24, random.randrange(14, 20), wallmob3_img, wallmob3_hit_anim, movetype, pos, speed, 57, 8, 50)

        self.group.add(self)


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
        xpos = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width), (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - wall_width)
        ypos = random.randrange(-wall_height * 2, -wall_height) - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height
    elif movetype == 2:     # moves from bottom to top
        xpos = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width), (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - wall_width)
        ypos = random.randrange(0, wall_height) + (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height
    elif movetype == 3:     # moves from left to right
        xpos = random.randrange(-wall_width * 2, -wall_width) - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width
        ypos = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height), (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - wall_height)
    else:                   # moves from right to left
        xpos = random.randrange(0, wall_width) + (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width
        ypos = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height), (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - wall_height)

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


class FollowerMob(pygame.sprite.Sprite):
    """
    The parent sprite of all `FollowerMob` type enemies

    moves toward player with random speed
    """

    def __init__(self, size, debris_size, debris_speed, norm_image, hit_anim, speed, damage, hp, points):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.debris_size = debris_size
        self.debris_speed = debris_speed
        self.norm_image = norm_image
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = hit_anim
        self.rect = self.image.get_rect()
        self.speed = speed
        self.damage = damage
        self.hit = False
        self.hitcount = 0
        self.hp = hp
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = points
        self.no_points = False
        self.type = random.randrange(1, 5)
        if self.type == 1:
            self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height
        elif self.type == 2:
            self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height
        elif self.type == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.speedx = self.speed * (player.rect.center[0] - self.rect.center[0]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
        self.speedy = self.speed * (player.rect.center[1] - self.rect.center[1]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
        all_mobs.add(self)

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
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
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class FollowerMob1(FollowerMob):
    """
    moves toward player with random speed
    """
    group = pygame.sprite.Group()

    def __init__(self):
        FollowerMob.__init__(self, [100, 100], 30, random.randrange(10, 22), followermob1_img, followermob1_hit_anim, random.randrange(1, 6), 100, 30, 400)

        self.group.add(self)


class FollowerMob2(FollowerMob):
    """
    similaar to FollowerMob1, but generates a number of small mobs when killed
    small mobs will be defined in a separate sprite class named "FollowerMob2Child"
    """
    group = pygame.sprite.Group()

    def __init__(self):
        FollowerMob.__init__(self, [140, 140], 30, random.randrange(12, 25), followermob2_img, followermob2_hit_anim, random.randrange(1, 3), 345, 150, 900)

        self.group.add(self)

    def update(self):
        FollowerMob.update(self)

        if self.dead and not self.no_points:
            self.spread_children()

    def spread_children(self):
        dist_x = player.rect.center[0] - self.rect.center[0]
        dist_y = player.rect.center[1] - self.rect.center[1]
        angle = math.atan2(dist_y, dist_x)
        children_cnt = random.randrange(70, 80)
        for c in range(children_cnt):
            direction = random.uniform(angle + math.pi / 6, angle + math.pi * 11 / 6)
            child = FollowerMob2Child((random.randrange(self.rect.width / 2) + self.abs_x + self.rect.width / 4,
                                       random.randrange(self.rect.height / 2) + self.abs_y + self.rect.height / 4),
                                      direction)
            all_sprites.add(child)
            all_mobs.add(child)


class FollowerMob2Child(pygame.sprite.Sprite):
    """
    small mobs generated from FollowerMob2
    also move towards player,
    but the "acceleration" direction is set to player, not "speed" direction
    acceleration constant and max speed are set randomly
    """
    group = pygame.sprite.Group()

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
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 15
        self.no_points = False
        self.abs_x = abs_pos[0]
        self.abs_y = abs_pos[1]
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.speedx = self.speed * math.cos(self.dir)
        self.speedy = self.speed * math.sin(self.dir)
        dist_x = player.rect.center[0] - self.rect.center[0]
        dist_y = player.rect.center[1] - self.rect.center[1]
        self.acc_dir = math.atan2(dist_y, dist_x)
        self.acc = random.uniform(0.2, 0.4)
        self.acc_x = self.acc * math.cos(self.acc_dir)
        self.acc_y = self.acc * math.sin(self.acc_dir)

        self.group.add(self)

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
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
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class MinigunMob(pygame.sprite.Sprite):
    """
    The parent sprite of all `MinigunMob` type enemies

    shoots a bullet to player periodically
    moves up, down, left, or right,
    but the direction can be changed with a specific probability in every frame
    the "movetype" attribute defines only initial move direction of the mob
    """

    def __init__(self, size, debris_size, debris_speed, norm_image, hit_anim, speed, damage, hp, points, shoot_interval, power):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.debris_size = debris_size
        self.debris_speed = debris_speed
        self.norm_image = norm_image
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = hit_anim
        self.rect = self.image.get_rect()
        self.speed = speed
        self.damage = damage
        self.hit = False
        self.hitcount = 0
        self.hp = hp
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = points
        self.no_points = False
        self.shoot_interval = shoot_interval
        self.last_shoot = time.time()
        self.trigger = False
        self.power = power
        self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
        self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        self.movetype = random.randrange(1, 5)
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
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.spawned = False
        self.spawn_effect = SpawnEffect(self.rect.center, self.size)
        all_sprites.add(self.spawn_effect)
        spawns.add(self.spawn_effect)

    def update(self):
        if not self.spawned:
            if self.spawn_effect.complete:
                self.spawned = True
                self.spawn_effect.kill()
                all_mobs.add(self)
                self.rect.x = round(self.abs_x - screen_center[0])
                self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            return
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
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
            if not (-self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width and
                    -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height):
                if self.abs_x <= -self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width:
                    self.abs_x = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - 1
                elif self.abs_x >= (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width:
                    self.abs_x = -self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height:
                    self.abs_y = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - 1
                else:
                    self.abs_y = -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height + 1

            self.use_minigun()

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()

    def use_minigun(self):
        """
        This method will be overrided by its child classes
        :return: None
        """
        pass


class MinigunMob1(MinigunMob):
    """
    shoots a bullet to player periodically
    moves up, down, left, or right,
    but the direction can be changed with a specific probability in every frame
    the "movetype" attribute defines only initial move direction of the mob
    """
    group = pygame.sprite.Group()

    def __init__(self):
        MinigunMob.__init__(self, (70, 70), 28, random.randrange(13, 19), minigunmob1_img, minigunmob1_hit_anim, random.randrange(2, 7), 143, 40, 384, 4, 8)

        self.group.add(self)

    def use_minigun(self):
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


class MinigunMob2(MinigunMob):
    """
    similar to MinigunMob1, but has larger size, slower speed and higher hp
    spreads multiple bullets at a time
    """
    group = pygame.sprite.Group()

    def __init__(self):
        MinigunMob.__init__(self, (100, 100), 28, random.randrange(15, 23), minigunmob2_img, minigunmob2_hit_anim, random.randrange(2, 5), 201, 65, 497, 6, 8)

        self.bullets_per_shoot = 7
        self.current_bullets = self.bullets_per_shoot
        self.first_shoot = random.uniform(0, self.shoot_interval)
        self.interval = self.first_shoot
        self.shoot_dir = 0
        self.shoot_angle = 0

        self.group.add(self)

    def use_minigun(self):
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


class MinigunMob3(MinigunMob):
    """
    similar to MinigunMob1, but has larger size, slower speed and higher hp
    shoots a chain of bullets to multiple directions like a short laser blast
    """
    group = pygame.sprite.Group()

    def __init__(self):
        MinigunMob.__init__(self, (150, 150), 33, random.randrange(17, 24), minigunmob3_img, minigunmob3_hit_anim, random.randrange(1, 3), 457, 100, 795, 7, 8)

        self.first_shoot = random.uniform(0, self.shoot_interval)
        self.interval = self.first_shoot
        self.shoot_angle = 0
        self.bullets_per_shoot = 10
        self.current_bullets = 0

        self.group.add(self)

    def use_minigun(self):
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


class ShellMob1(pygame.sprite.Sprite):
    """
    protects itself with 4 rigid "shell"s(will be defined in a separate sprite class)
    can open or close shells
    attacks player with cannon ball when shells are opened
    moving pattern is same as MinigunMobs
    """
    group = pygame.sprite.Group()
    SHELL_TYPE_CNT = 4

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
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
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
        self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
        self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        self.movetype = random.randrange(1, 5)
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
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.spawned = False
        self.spawn_effect = SpawnEffect(self.rect.center, [self.size[0] + 40, self.size[1] + 40])
        all_sprites.add(self.spawn_effect)
        spawns.add(self.spawn_effect)
        # shells for each direction
        self.shell1 = Shell1(1, self.rect.center)
        self.shell2 = Shell1(2, self.rect.center)
        self.shell3 = Shell1(3, self.rect.center)
        self.shell4 = Shell1(4, self.rect.center)
        self.shells = [self.shell1, self.shell2, self.shell3, self.shell4]
        self.in_map = False
        self.i = 0

        self.group.add(self)

    def update(self):
        if not self.spawned:
            if self.spawn_effect.complete:
                self.spawned = True
                self.spawn_effect.kill()
                all_mobs.add(self)
                self.rect.x = round(self.abs_x - screen_center[0])
                self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            return
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
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width \
                    and -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height:
                self.in_map = True
            if self.in_map:
                if self.abs_x <= -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width or self.abs_x >= (
                        SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width:
                    if self.movetype == 2:
                        self.movetype = 4
                    elif self.movetype == 4:
                        self.movetype = 2
                    self.speedx = -self.speedx
                elif self.abs_y <= -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height or self.abs_y >= (
                        SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height:
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
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

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
                                cannonball = MobExplodingCannonBall1(self.rect.center, angle, 47, 12)
                                all_sprites.add(cannonball)
                                mob_cannon_balls.add(cannonball)
                            expl_type = random.randrange(1, 12)
                            Explosion(self.rect.center, expl_type, (round(self.size[0]), round(self.size[1])))
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

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if len(self.shells) <= 0:
                if random.random() <= ITEM_DROP_PROBABILITY:
                    item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                    all_sprites.add(item)
                    items.add(item)
                expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
                Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
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
    group = pygame.sprite.Group()

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
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
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

        self.group.add(self)

    def update(self, pos=(0, 0)):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
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

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class ShellMob2(pygame.sprite.Sprite):
    """
    similar to ShellMob1, but its shells move in different direction
    and shoots cannon ball in different direction
    """
    group = pygame.sprite.Group()
    SHELL_TYPE_CNT = 4

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = [100, 100]
        self.debris_size = 25
        self.debris_speed = random.randrange(13, 20)
        self.norm_image = shellmob2_core_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = shellmob2_core_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(3, 7)
        self.damage = 513
        self.hit = False
        self.hitcount = 0
        self.hp = 65
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
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
        self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
        self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        self.movetype = random.randrange(1, 5)
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
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.spawned = False
        self.spawn_effect = SpawnEffect(self.rect.center, [self.size[0] + 50, self.size[1] + 50])
        all_sprites.add(self.spawn_effect)
        spawns.add(self.spawn_effect)
        # shells for each direction
        self.shell1 = Shell2(1, self.rect.center)
        self.shell2 = Shell2(2, self.rect.center)
        self.shell3 = Shell2(3, self.rect.center)
        self.shell4 = Shell2(4, self.rect.center)
        self.shells = [self.shell1, self.shell2, self.shell3, self.shell4]
        self.in_map = False
        self.i = 0

        self.group.add(self)

    def update(self):
        if not self.spawned:
            if self.spawn_effect.complete:
                self.spawned = True
                self.spawn_effect.kill()
                all_mobs.add(self)
                self.rect.x = round(self.abs_x - screen_center[0])
                self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            return
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
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width \
                    and -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height:
                self.in_map = True
            if self.in_map:
                if self.abs_x <= -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width or self.abs_x >= (
                        SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width:
                    if self.movetype == 2:
                        self.movetype = 4
                    elif self.movetype == 4:
                        self.movetype = 2
                    self.speedx = -self.speedx
                elif self.abs_y <= -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height or self.abs_y >= (
                        SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height:
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
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

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
                                    cannonball = MobExplodingCannonBall1(self.rect.center, angle + ang * math.pi / 2, 55, 20)
                                    all_sprites.add(cannonball)
                                    mob_cannon_balls.add(cannonball)
                            expl_type = random.randrange(1, 12)
                            Explosion(self.rect.center, expl_type, (round(self.size[0]), round(self.size[1])))
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

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if len(self.shells) <= 0:
                if random.random() <= ITEM_DROP_PROBABILITY:
                    item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                    all_sprites.add(item)
                    items.add(item)
                expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
                Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
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
    group = pygame.sprite.Group()

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
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 105
        self.no_points = False

        self.group.add(self)

    def update(self, pos=(0, 0)):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
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

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            expl_size = max(self.size)
            Explosion(self.rect.center, expl_type, (round(expl_size * MOB_EXPLOSION_SIZE_RATIO), round(expl_size * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class BarricadeMob1(pygame.sprite.Sprite):
    """
    generates a barricade
    player cannot destroy barricade directly
    barricade will be destroyed only if BarricadeMob killed
    a BarricadeMob copies itself and widen their distance, generating barricade between them
    after generating barricade, it 'sweeps' the field on direction perpendicular to barricade
    """
    group = pygame.sprite.Group()

    def __init__(self, static=True, pos=(), duplicate=None):
        pygame.sprite.Sprite.__init__(self)
        self.size = (120, 120)
        self.debris_size = 28
        self.debris_speed = random.randrange(12, 20)
        self.charge0_image = barricademob1_charge0_img
        self.charge0_hit_anim = barricademob1_charge0_hit_anim
        self.charge1_image = barricademob1_charge1_img
        self.charge1_hit_anim = barricademob1_charge1_hit_anim
        self.charge2_image = barricademob1_charge2_img
        self.charge2_hit_anim = barricademob1_charge2_hit_anim
        self.charge3_image = barricademob1_charge3_img
        self.charge3_hit_anim = barricademob1_charge3_hit_anim
        self.charge4_image = barricademob1_charge4_img
        self.charge4_hit_anim = barricademob1_charge4_hit_anim
        self.current_image = self.charge0_image
        self.hit_anim = barricademob1_charge0_hit_anim
        self.image = pygame.transform.scale(self.current_image, self.size)
        self.rect = self.image.get_rect()
        self.speed = random.randrange(8, 12)
        self.damage = 372
        self.hit = False
        self.hitcount = 0
        self.hp = 100
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 314
        self.no_points = False
        self.static = static
        self.barricade_generated = 0
        self.direct_barricade = None        # barricade directly connected to self
        self.charge_start_time = time.time()
        self.elapsed_time_in_seconds = 0
        self.movetype_list = [1, 2, 3, 4]
        self.movetype = 0

        self.duplicate = duplicate

        self.change_mode = False
        self.start_generate_barricade = False
        self.current_barricade = None
        self.finished_generate_barricade = False

        self.number_of_barricades = random.randrange(5, 30)
        self.distance_to_move = 40 * self.number_of_barricades
        self.barricade_position = [40 * d for d in range(self.number_of_barricades)]
        self.moved_distance = 0

        self.sweep = False
        self.sweep_start = False
        self.sweep_speed = random.randrange(2, 5)

        if self.static:
            self.charge_mode = 0
            self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            self.start_pos_x = self.abs_x + self.rect.width // 2
            self.start_pos_y = self.abs_y + self.rect.height // 2
            self.speedx = 0
            self.speedy = 0

            self.generating_barricade = False
            self.has_duplicate = False
            self.has_barricade = False

            self.spawned = False
            self.spawn_effect = SpawnEffect(self.rect.center, self.size)
            all_sprites.add(self.spawn_effect)
            spawns.add(self.spawn_effect)

        else:
            self.charge_mode = 4
            self.abs_x = pos[0]
            self.abs_y = pos[1]

            if self.abs_y + self.distance_to_move > (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height:
                self.movetype_list.remove(1)
            if self.abs_y - self.distance_to_move < -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height:
                self.movetype_list.remove(2)
            if self.abs_x + self.distance_to_move > (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width:
                self.movetype_list.remove(3)
            if self.abs_x - self.distance_to_move < -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width:
                self.movetype_list.remove(4)

            self.movetype = random.choice(self.movetype_list)
            self.duplicate.movetype = self.movetype
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
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            self.start_pos_x = self.abs_x + self.rect.width // 2
            self.start_pos_y = self.abs_y + self.rect.height // 2

            self.duplicate = duplicate
            self.start_generate_barricade = True
            self.generating_barricade = True
            self.has_duplicate = True
            self.has_barricade = True

            self.spawned = False

        self.group.add(self)

    def update(self):
        global score
        # before spawned
        if self.static:
            if not self.spawned:
                if self.spawn_effect.complete:
                    self.spawn_effect.kill()
                    self.image = pygame.transform.scale(self.charge0_image, self.size)
                    self.hit_anim = self.charge0_hit_anim
                    all_mobs.add(self)
                    self.rect.x = round(self.abs_x - screen_center[0])
                    self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
                    self.charge_start_time = time.time()
                    self.spawned = True
                return
        else:
            if not self.spawned:
                self.image = pygame.transform.scale(self.charge4_image, self.size)
                self.hit_anim = self.charge4_hit_anim
                all_mobs.add(self)
                self.rect.x = round(self.abs_x - screen_center[0])
                self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
                self.charge_start_time = time.time()
                self.spawned = True

        # regular update before death
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            if not (-self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < (
                    SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width and
                    -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < (
                            SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height):
                if self.abs_x <= -self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width:
                    self.abs_x = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - 1
                elif self.abs_x >= (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width:
                    self.abs_x = -self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height:
                    self.abs_y = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - 1
                else:
                    self.abs_y = -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height + 1

            # change image accoring to each charge mode
            if self.change_mode:
                if self.charge_mode == 0:
                    self.current_image = self.charge0_image
                    if not self.hit:
                        self.image = pygame.transform.scale(self.current_image, self.size)
                    self.hit_anim = self.charge0_hit_anim
                elif self.charge_mode == 1:
                    self.current_image = self.charge1_image
                    if not self.hit:
                        self.image = pygame.transform.scale(self.current_image, self.size)
                    self.hit_anim = self.charge1_hit_anim
                elif self.charge_mode == 2:
                    self.current_image = self.charge2_image
                    if not self.hit:
                        self.image = pygame.transform.scale(self.current_image, self.size)
                    self.hit_anim = self.charge2_hit_anim
                elif self.charge_mode == 3:
                    self.current_image = self.charge3_image
                    if not self.hit:
                        self.image = pygame.transform.scale(self.current_image, self.size)
                    self.hit_anim = self.charge3_hit_anim
                else:
                    self.current_image = self.charge4_image
                    if not self.hit:
                        self.image = pygame.transform.scale(self.current_image, self.size)
                    self.hit_anim = self.charge4_hit_anim
                self.change_mode = False

            # when static
            if self.static:
                # charging
                if time.time() - self.charge_start_time >= 1 and self.charge_mode < 4:
                    self.charge_mode += 1
                    self.change_mode = True
                    self.charge_start_time += 1

                # charge complete, generate duplicate
                elif self.charge_mode == 4:
                    if not self.generating_barricade and not self.has_duplicate:
                        self.duplicate = BarricadeMob1(False, [self.abs_x, self.abs_y], self)
                        all_sprites.add(self.duplicate)
                        mobs.add(self.duplicate)
                        self.group.add(self.duplicate)
                        self.has_duplicate = True
                        self.has_barricade = True
                        self.generating_barricade = True

                    # when duplicate killed or disconnected
                    if self.has_barricade and not self.has_duplicate:
                        self.duplicate = None
                        self.has_barricade = False
                        self.generating_barricade = False
                        self.sweep = False
                        self.sweep_start = False
                        self.charge_start_time = time.time()
                        self.speedx = 0
                        self.speedy = 0
                        self.charge_mode = 0
                        self.change_mode = True

                # while sweep
                if self.sweep:
                    if not self.sweep_start:
                        if self.movetype in [1, 2]:
                            self.speedx = random.choice([-1, 1]) * self.sweep_speed
                            self.duplicate.speedx = self.speedx
                        else:
                            self.speedy = random.choice([-1, 1]) * self.sweep_speed
                            self.duplicate.speedy = self.speedy
                        self.sweep_start = True

            # when active
            else:
                # generate the first barricade
                if self.start_generate_barricade:
                    if self.movetype in [1, 2]:
                        first_barricade = Barricade("vertical", [self.start_pos_x, self.start_pos_y], self.duplicate, self, [self.duplicate, self], True, True)
                    else:
                        first_barricade = Barricade("horizontal", [self.start_pos_x, self.start_pos_y], self.duplicate, self, [self.duplicate, self], True, True)
                    all_sprites.add(first_barricade)
                    barricades.add(first_barricade)
                    self.current_barricade = first_barricade
                    self.direct_barricade = first_barricade
                    self.duplicate.direct_barricade = first_barricade
                    del self.barricade_position[0]
                    self.start_generate_barricade = False

                # generate successor barricades
                self.moved_distance += abs(self.speedx + self.speedy)
                if len(self.barricade_position) > 0:
                    if self.moved_distance >= self.barricade_position[0]:
                        if self.movetype in [1, 2]:
                            new_barricade = Barricade("vertical", [self.start_pos_x, self.start_pos_y - (2 * self.movetype - 3) * self.barricade_position[0]],
                                                      self.current_barricade, self, [self.duplicate, self], False, True)
                        else:
                            new_barricade = Barricade("horizontal", [self.start_pos_x - (2 * self.movetype - 7) * self.barricade_position[0], self.start_pos_y],
                                                      self.current_barricade, self, [self.duplicate, self], False, True)
                        all_sprites.add(new_barricade)
                        barricades.add(new_barricade)
                        self.current_barricade.next_barricade = new_barricade
                        self.current_barricade.is_next_parent = False
                        self.current_barricade = new_barricade
                        self.direct_barricade = new_barricade
                        del self.barricade_position[0]

                # change to static mode if barricade generation completes or duplicated killed
                if self.moved_distance >= self.distance_to_move:
                    self.static = True
                    self.speedx = 0
                    self.speedy = 0
                    self.finished_generate_barricade = True
                    self.duplicate.finished_generate_barricade = True
                    self.sweep = True
                    self.duplicate.sweep = True
                if self.has_barricade and not self.has_duplicate:
                    self.has_barricade = False
                    self.generating_barricade = False
                    self.finished_generate_barricade = False
                    self.sweep = False
                    self.sweep_start = False
                    self.static = True
                    self.speedx = 0
                    self.speedy = 0
                    self.charge_start_time = time.time()
                    self.charge_mode = 0
                    self.change_mode = True

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        # death
        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            if self.has_duplicate:
                self.duplicate.has_duplicate = False
            if self.has_barricade:
                if self.direct_barricade.is_next_parent:
                    self.direct_barricade.next_dead = True
                if self.direct_barricade.is_prev_parent:
                    self.direct_barricade.prev_dead = True
            self.kill()


class Barricade(pygame.sprite.Sprite):
    """
    a unit of barricade wall generated by BarricadeMob
    """
    group = pygame.sprite.Group()

    def __init__(self, dierction, pos, prev_barricade, next_barricade, parent_mobs, is_prev_parent=False, is_next_parent=False):
        pygame.sprite.Sprite.__init__(self)
        self.size = (40, 40)
        if dierction == "horizontal":
            self.image = pygame.transform.scale(barricade_horizontal_img, self.size)
        else:
            self.image = pygame.transform.scale(barricade_vertical_img, self.size)
        self.rect = self.image.get_rect()
        self.damage = 118
        self.hp = 150
        self.hp_full = self.hp
        self.dead = False
        self.death_count = 1
        self.points = 0
        self.no_points = False
        self.prev_barricade = prev_barricade
        self.next_barricade = next_barricade
        self.parent_mobs = parent_mobs
        self.is_prev_parent = is_prev_parent
        self.is_next_parent = is_next_parent
        self.prev_dead = False
        self.next_dead = False
        self.rect.center = pos
        self.relative_x = 0
        self.relative_y = 0
        self.abs_x = self.rect.x
        self.abs_y = self.rect.y
        self.rect.x -= screen_center[0]
        self.rect.y -= screen_center[1]

        self.position_fixed = False
        self.sweep = False

        self.group.add(self)

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
            if not self.is_next_parent:
                self.next_barricade.prev_dead = True
            if not self.is_prev_parent:
                self.prev_barricade.next_dead = True

        if not self.dead:
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            if not self.position_fixed and self.parent_mobs[0].sweep:
                self.relative_x = self.abs_x + self.rect.width // 2 - self.parent_mobs[0].abs_x - self.parent_mobs[0].rect.width // 2
                self.relative_y = self.abs_y + self.rect.height // 2 - self.parent_mobs[0].abs_y - self.parent_mobs[0].rect.height // 2
                self.sweep = True
                self.position_fixed = True

            if self.sweep:
                self.abs_x = self.parent_mobs[0].abs_x + self.parent_mobs[0].rect.width // 2 + self.relative_x - self.rect.width // 2
                self.abs_y = self.parent_mobs[0].abs_y + self.parent_mobs[0].rect.height // 2 + self.relative_y - self.rect.height // 2

            if self.prev_dead or self.next_dead:
                if self.death_count == 1:
                    self.death_count -= 1
                else:
                    self.dead = True
                    if not self.is_next_parent:
                        self.next_barricade.prev_dead = True
                    if not self.is_prev_parent:
                        self.prev_barricade.next_dead = True

        else:
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * 4), round(self.size[1] * 4)))
            for p in self.parent_mobs:
                p.static = True
                p.charge_mode = 0
                p.charge_start_time = time.time()
                p.change_mode = True
                p.has_duplicate = False
                p.has_barricade = False
                p.generating_barricade = False
                p.speedx = 0
                p.speedy = 0
            self.kill()


class OrbitMob(pygame.sprite.Sprite):
    """
    A parent class of all `OrbitMob` type of enemies

    orbitmob - mothership(or core)
    protects itself with "orbiters" orbiting itself.
    if orbiters are destroyed, the mother ship relaunches new orbiter to its orbit.
    orbiters attack player, and mothership just moves around.
    """

    def __init__(self, size, debris_size, debris_speed, norm_image, hit_anim, speed, damage, hp, points, orbiter_generating_time_interval, max_number_of_orbiters, attack_interval):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.debris_size = debris_size
        self.debris_speed = debris_speed
        self.norm_image = norm_image
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = hit_anim
        self.rect = self.image.get_rect()
        self.speed = speed
        self.damage = damage
        self.hit = False
        self.hitcount = 0
        self.hp = hp
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = points
        self.no_points = False

        self.orbiter_generating_time_interval = orbiter_generating_time_interval
        self.last_orbiter_generated_time = time.time()
        self.orbiter = None
        self.orbiters = pygame.sprite.Group()
        self.max_number_of_orbiters = max_number_of_orbiters
        self.number_of_orbiters = 0

        self.attack_interval = attack_interval
        self.last_attacked = time.time()

        self.angle = random.uniform(-math.pi, math.pi)
        self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
        self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        self.speedx = self.speed * math.cos(self.angle)
        self.speedy = self.speed * math.sin(self.angle)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.spawned = False
        self.spawn_effect = SpawnEffect(self.rect.center, [self.size[0], self.size[1]])
        all_sprites.add(self.spawn_effect)
        spawns.add(self.spawn_effect)

    def update(self):
        if not self.spawned:
            if self.spawn_effect.complete:
                self.spawned = True
                self.spawn_effect.kill()
                all_mobs.add(self)
                self.rect.x = round(self.abs_x - screen_center[0])
                self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            return
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if not (-3 * self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < (
                    SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width + 2 * self.rect.width and
                    -3 * self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < (
                            SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height + 2 * self.rect.height):
                if self.abs_x <= -3 * self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width:
                    self.abs_x = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width + self.rect.width
                elif self.abs_x >= (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width + 2 * self.rect.width:
                    self.abs_x = -2 * self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -3 * self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height:
                    self.abs_y = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height + self.rect.height
                else:
                    self.abs_y = -2 * self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height

            if random.random() <= 0.02:
                self.angle = random.uniform(self.angle - math.pi / 2, self.angle + math.pi / 2)
                self.speedx = self.speed * math.cos(self.angle)
                self.speedy = self.speed * math.sin(self.angle)
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            self.update_orbit()
            self.attack()

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            for orbiter in self.orbiters:
                orbiter.dead = True
                orbiter.update(self.rect.center)
            self.kill()

    def update_orbit(self):
        """
        This will be overrided by its child classes.
        :return: None
        """
        pass

    def attack(self):
        """
        This will be overrided by its child classes.
        :return: None
        """
        pass


class OrbitMob1(OrbitMob):
    """
    A child class which inherits OrbitMob class as parent.
    """
    group = pygame.sprite.Group()

    def __init__(self):
        OrbitMob.__init__(self, [150, 150], 20, random.randrange(15, 24), orbitmob1_mothership_img, orbitmob1_mothership_hit_anim, random.randrange(2, 5), 638, 180, 785, 1, 10, random.uniform(5, 10))

        self.group.add(self)

    def update_orbit(self):
        self.number_of_orbiters = len(self.orbiters)
        if time.time() - self.last_orbiter_generated_time >= self.orbiter_generating_time_interval and \
                self.number_of_orbiters < self.max_number_of_orbiters:
            self.orbiter = Orbiter1(self.rect.center)
            self.orbiters.add(self.orbiter)
            all_mobs.add(self.orbiter)
            self.number_of_orbiters += 1
            self.last_orbiter_generated_time = time.time()

        for orbiter in self.orbiters:
            orbiter.update(self.rect.center)

    def attack(self):
        if time.time() - self.last_attacked >= self.attack_interval:
            for orbiter in self.orbiters:
                orbiter.attack()
            self.last_attacked = time.time()
            self.attack_interval = random.uniform(5, 10)


class Orbiter1(pygame.sprite.Sprite):
    """
    orbitmob - orbiter
    circles around mothership and attacks player with cannonball
    """
    group = pygame.sprite.Group()

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.size = [35, 35]
        self.debris_size = 10
        self.debris_speed = random.randrange(5, 9)
        self.norm_image = orbitmob1_orbiter_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = orbitmob1_orbiter_hit_anim
        self.rect = self.image.get_rect()
        self.damage = 76
        self.hit = False
        self.hitcount = 0
        self.hp = 10
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 34
        self.no_points = False

        self.reached_max_angular_speed = False
        self.on_orbit = False
        self.max_distance_to_mothership = 150
        self.distance_to_mothership = 0
        self.angular_pos = random.uniform(-math.pi, math.pi)
        self.max_angular_speed = random.uniform(0.03, 0.1)
        self.angular_speed = 0
        self.relative_x = self.distance_to_mothership * math.cos(self.angular_pos)
        self.relative_y = self.distance_to_mothership * math.sin(self.angular_pos)

        self.abs_x = pos[0] + self.relative_x - self.rect.width // 2
        self.abs_y = pos[1] + self.relative_y - self.rect.height // 2
        self.rect.x = round(self.abs_x)
        self.rect.y = round(self.abs_y)

        self.group.add(self)

    def update(self, pos=(0, 0)):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if not self.reached_max_angular_speed:
                self.angular_speed += 0.001
                if self.angular_speed >= self.max_angular_speed:
                    self.reached_max_angular_speed = True

            if not self.on_orbit:
                self.distance_to_mothership += 3
                if self.distance_to_mothership >= self.max_distance_to_mothership:
                    self.on_orbit = True

            self.angular_pos += self.angular_speed
            self.relative_x = self.distance_to_mothership * math.cos(self.angular_pos)
            self.relative_y = self.distance_to_mothership * math.sin(self.angular_pos)
            self.abs_x = pos[0] + self.relative_x - self.rect.width // 2
            self.abs_y = pos[1] + self.relative_y - self.rect.height // 2
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            expl_size = max(self.size)
            Explosion(self.rect.center, expl_type, (round(expl_size * MOB_EXPLOSION_SIZE_RATIO), round(expl_size * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()

    def attack(self):
        cannonball = MobChargingCannonBall1(self.rect.center, 36, 12, self)
        all_sprites.add(cannonball)
        mob_cannon_balls.add(cannonball)


class OrbitMob2(OrbitMob):
    """
    similar to OrbitMob1
    but generates more orbiters that are smaller, faster than that of OrbiterMob1
    orbiters attack player with bullets
    """
    group = pygame.sprite.Group()

    def __init__(self):
        OrbitMob.__init__(self, [120, 120], 20, random.randrange(15, 24), orbitmob2_mothership_img, orbitmob2_mothership_hit_anim, random.randrange(4, 8), 478, 140, 655, .15, 30, random.uniform(5, 10))

        self.group.add(self)

    def update_orbit(self):
        self.number_of_orbiters = len(self.orbiters)
        if time.time() - self.last_orbiter_generated_time >= self.orbiter_generating_time_interval and \
                self.number_of_orbiters < self.max_number_of_orbiters:
            self.orbiter = Orbiter2(self.rect.center)
            self.orbiters.add(self.orbiter)
            all_mobs.add(self.orbiter)
            self.number_of_orbiters += 1
            self.last_orbiter_generated_time = time.time()

        for orbiter in self.orbiters:
            orbiter.update(self.rect.center)

    def attack(self):
        if time.time() - self.last_attacked >= self.attack_interval:
            dist_x = player.rect.center[0] - self.rect.center[0]
            dist_y = player.rect.center[1] - self.rect.center[1]
            angle = math.atan2(dist_y, dist_x)
            for orbiter in self.orbiters:
                orbiter.attack(angle)
            self.last_attacked = time.time()
            self.attack_interval = random.uniform(6, 12)


class Orbiter2(pygame.sprite.Sprite):
    """
    orbitmob - orbiter
    circles around mothership and attacks player with cannonball
    """
    group = pygame.sprite.Group()

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.size = [20, 20]
        self.debris_size = 7
        self.debris_speed = random.randrange(5, 9)
        self.norm_image = orbitmob2_orbiter_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = orbitmob2_orbiter_hit_anim
        self.rect = self.image.get_rect()
        self.damage = 42
        self.hit = False
        self.hitcount = 0
        self.hp = 5
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 17
        self.no_points = False

        self.reached_max_angular_speed = False
        self.on_orbit = False
        self.max_distance_to_mothership = 100
        self.distance_to_mothership = 0
        self.angular_pos = random.uniform(-math.pi, math.pi)
        self.opposite = random.choice([-1, 1])
        self.max_angular_speed = random.uniform(0.1, 0.2)
        self.angular_speed = 0
        self.angular_speed_inc = 0.001 * self.opposite
        self.relative_x = self.distance_to_mothership * math.cos(self.angular_pos)
        self.relative_y = self.distance_to_mothership * math.sin(self.angular_pos)

        self.abs_x = pos[0] + self.relative_x - self.rect.width // 2
        self.abs_y = pos[1] + self.relative_y - self.rect.height // 2
        self.rect.x = round(self.abs_x)
        self.rect.y = round(self.abs_y)

        self.group.add(self)

    def update(self, pos=(0, 0)):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if not self.reached_max_angular_speed:
                self.angular_speed += self.angular_speed_inc
                if abs(self.angular_speed) >= self.max_angular_speed:
                    self.reached_max_angular_speed = True

            if not self.on_orbit:
                self.distance_to_mothership += 3
                if self.distance_to_mothership >= self.max_distance_to_mothership:
                    self.on_orbit = True

            self.angular_pos += self.angular_speed
            self.relative_x = self.distance_to_mothership * math.cos(self.angular_pos)
            self.relative_y = self.distance_to_mothership * math.sin(self.angular_pos)
            self.abs_x = pos[0] + self.relative_x - self.rect.width // 2
            self.abs_y = pos[1] + self.relative_y - self.rect.height // 2
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            expl_size = max(self.size)
            Explosion(self.rect.center, expl_type, (round(expl_size * MOB_EXPLOSION_SIZE_RATIO), round(expl_size * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()

    def attack(self, angle):
        bullet = MobBullet1(5, 8, self.rect.center, angle)
        all_sprites.add(bullet)
        mob_bullets.add(bullet)


class OrbitMob3(OrbitMob):
    """
    similar to OrbitMob1
    has two-layered orbits
    """
    group = pygame.sprite.Group()

    def __init__(self):
        OrbitMob.__init__(self, [250, 250], 35, random.randrange(19, 28), orbitmob3_mothership_img, orbitmob3_mothership_hit_anim, random.randrange(1, 4), 1254, 360, 1548, .15, 30, random.uniform(5, 10))

        self.opposite = True
        self.orbit1_orbiters = pygame.sprite.Group()            # outer orbit
        self.orbit2_orbiters = pygame.sprite.Group()            # inner orbit

        self.group.add(self)

    def update_orbit(self):
        # generate outer orbit
        if len(self.orbit1_orbiters) <= 15:
            for num in range(30):
                self.orbiter = Orbiter3(self.rect.center, 250, 0.01, num * 2 * math.pi / 30, 3, self.opposite)
                self.orbit1_orbiters.add(self.orbiter)
                self.orbiters.add(self.orbiter)
                all_mobs.add(self.orbiter)
                self.opposite = not self.opposite

        # generate inner orbit
        if len(self.orbit2_orbiters) <= 10:
            for num in range(20):
                self.orbiter = Orbiter3(self.rect.center, 180, 0.02, num * 2 * math.pi / 20, 3, self.opposite)
                self.orbit2_orbiters.add(self.orbiter)
                self.orbiters.add(self.orbiter)
                all_mobs.add(self.orbiter)
                self.opposite = not self.opposite

        for orbiter in self.orbiters:
            orbiter.update(self.rect.center)

    def attack(self):
        pass


class Orbiter3(pygame.sprite.Sprite):
    """
    orbitmob - orbiter
    circles around mothership and attacks player with cannonball
    """
    group = pygame.sprite.Group()

    def __init__(self, pos, max_distance, max_angular_speed, angular_pos, orthogonal_speed, opposite=False):
        pygame.sprite.Sprite.__init__(self)
        self.size = [35, 35]
        self.debris_size = 10
        self.debris_speed = random.randrange(5, 9)
        self.norm_image = orbitmob3_orbiter_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = orbitmob3_orbiter_hit_anim
        self.rect = self.image.get_rect()
        self.damage = 45
        self.hit = False
        self.hitcount = 0
        self.hp = 12
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 41
        self.no_points = False

        self.reached_max_angular_speed = False
        self.on_orbit = False
        self.orthogonal_speed = orthogonal_speed
        self.max_distance_to_mothership = max_distance
        self.distance_to_mothership = 0
        self.angular_pos = angular_pos
        self.max_angular_speed = max_angular_speed
        self.angular_speed = 0
        self.relative_x = self.distance_to_mothership * math.cos(self.angular_pos)
        self.relative_y = self.distance_to_mothership * math.sin(self.angular_pos)
        self.opposite = -1 if opposite else 1

        self.abs_x = pos[0] + self.relative_x - self.rect.width // 2
        self.abs_y = pos[1] + self.relative_y - self.rect.height // 2
        self.rect.x = round(self.abs_x)
        self.rect.y = round(self.abs_y + field_shift_pos)

    def update(self, pos=(0, 0)):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if not self.reached_max_angular_speed:
                if self.angular_speed >= self.max_angular_speed:
                    self.reached_max_angular_speed = True
                self.angular_speed += 0.001

            if not self.on_orbit:
                self.distance_to_mothership += self.orthogonal_speed
                if self.distance_to_mothership >= self.max_distance_to_mothership:
                    self.on_orbit = True

            self.angular_pos += self.opposite * self.angular_speed
            self.relative_x = self.distance_to_mothership * math.cos(self.angular_pos)
            self.relative_y = self.distance_to_mothership * math.sin(self.angular_pos)
            self.abs_x = pos[0] + self.relative_x - self.rect.width // 2
            self.abs_y = pos[1] + self.relative_y - self.rect.height // 2
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)

            if random.random() < 0.002:
                cannonball = MobChargingCannonBall1(self.rect.center, 36, 12, self)
                all_sprites.add(cannonball)
                mob_cannon_balls.add(cannonball)

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            expl_size = max(self.size)
            Explosion(self.rect.center, expl_type, (round(expl_size * MOB_EXPLOSION_SIZE_RATIO), round(expl_size * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class BlockMob(pygame.sprite.Sprite):
    """
    just moves through straight line with random direction, random speed, and has random size
    does not attack player
    """
    group = pygame.sprite.Group()

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.factor = random.randrange(30, 121)
        self.size = [self.factor] * 2
        self.debris_size = 8 * self.factor // 30
        self.debris_speed = random.randrange(10, 15)
        self.norm_image = blockmob_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = blockmob_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(7, 12) / (self.factor / 30)
        self.damage = 76 * self.factor / 30
        self.hit = False
        self.hitcount = 0
        self.hp = round(13 * ((self.factor / 30) ** 2))
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = round(40 * ((self.factor / 30) ** 2))
        self.no_points = False
        self.angle = random.uniform(-math.pi, math.pi)
        self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
        self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        self.speedx = self.speed * math.cos(self.angle)
        self.speedy = self.speed * math.sin(self.angle)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.spawned = False
        self.spawn_effect = SpawnEffect(self.rect.center, self.size)
        all_sprites.add(self.spawn_effect)
        spawns.add(self.spawn_effect)

        self.group.add(self)

    def update(self):
        if not self.spawned:
            if self.spawn_effect.complete:
                self.spawned = True
                self.spawn_effect.kill()
                all_mobs.add(self)
                self.rect.x = round(self.abs_x - screen_center[0])
                self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            return
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            if not (-self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width and
                    -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height):
                if self.abs_x <= -self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width:
                    self.abs_x = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - 1
                elif self.abs_x >= (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width:
                    self.abs_x = -self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height:
                    self.abs_y = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - 1
                else:
                    self.abs_y = -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height + 1
                self.speedx = self.speed * math.cos(self.angle)
                self.speedy = self.speed * math.sin(self.angle)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class GhostMob(pygame.sprite.Sprite):
    """
    almost invisible to player
    similar to BlockMobs
    """
    group = pygame.sprite.Group()

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.factor = random.randrange(30, 121)
        self.size = [self.factor] * 2
        self.debris_size = 8 * self.factor // 30
        self.debris_speed = random.randrange(10, 15)
        self.norm_image = ghostmob_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = ghostmob_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(7, 12) / (self.factor / 30)
        self.damage = 76 * self.factor / 60
        self.hit = False
        self.hitcount = 0
        self.hp = round(13 * ((self.factor / 30) ** 2))
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = round(40 * ((self.factor / 30) ** 2))
        self.no_points = False
        self.angle = random.uniform(-math.pi, math.pi)
        self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
        self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        self.speedx = self.speed * math.cos(self.angle)
        self.speedy = self.speed * math.sin(self.angle)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.spawned = False
        self.spawn_effect = SpawnEffect(self.rect.center, self.size)
        all_sprites.add(self.spawn_effect)
        spawns.add(self.spawn_effect)

        self.group.add(self)

    def update(self):
        if not self.spawned:
            if self.spawn_effect.complete:
                self.spawned = True
                self.spawn_effect.kill()
                all_mobs.add(self)
                self.rect.x = round(self.abs_x - screen_center[0])
                self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            return
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                #self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            if not (-self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width and
                    -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height):
                if self.abs_x <= -self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width:
                    self.abs_x = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - 1
                elif self.abs_x >= (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width:
                    self.abs_x = -self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height:
                    self.abs_y = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - 1
                else:
                    self.abs_y = -self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height + 1
                self.speedx = self.speed * math.cos(self.angle)
                self.speedy = self.speed * math.sin(self.angle)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class NodeMob1(pygame.sprite.Sprite):
    """
    moves like linemob, but at lower speed
    generates a "laser wall" between any other NodeMob within a specific range
    player can be damaged by these walls
    """
    group = pygame.sprite.Group()

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = [100, 100]
        self.debris_size = 15
        self.debris_speed = random.randrange(13, 18)
        self.norm_image = nodemob1_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = nodemob1_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.uniform(4, 6)
        self.damage = 283
        self.hit = False
        self.hitcount = 0
        self.hp = 100
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 276
        self.no_points = False

        self.nodemob_laser_pairs = {}

        self.angle = random.uniform(-math.pi, math.pi)
        self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
        self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        self.speedx = self.speed * math.cos(self.angle)
        self.speedy = self.speed * math.sin(self.angle)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.spawned = False
        self.spawn_effect = SpawnEffect(self.rect.center, self.size)
        all_sprites.add(self.spawn_effect)
        spawns.add(self.spawn_effect)

        self.group.add(self)

    def update(self):
        if not self.spawned:
            if self.spawn_effect.complete:
                self.spawned = True
                self.spawn_effect.kill()
                all_mobs.add(self)
                self.rect.x = round(self.abs_x - screen_center[0])
                self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            return
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.abs_x += self.speedx
            self.abs_y += self.speedy

            if not (-2 * self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < self.rect.width + (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width and
                    -2 * self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < self.rect.height + (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height):
                self.dead = True
                self.no_points = True
                new_self = NodeMob1()
                new_self.hp = self.hp
                add_single_mob(new_self)

            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            for nodemob in self.group:
                if nodemob not in self.nodemob_laser_pairs and nodemob != self and nodemob.spawned:
                    if distance(self.rect.center, nodemob.rect.center) < 600:
                        laser = Nodemob1Laser([self, nodemob])
                        all_sprites.add(laser)
                        mob_lasers.append(laser)
                        self.nodemob_laser_pairs[nodemob] = laser

            nodemob_to_delete = []
            for nodemob in self.nodemob_laser_pairs.keys():
                if distance(self.rect.center, nodemob.rect.center) > 800:
                    laser = self.nodemob_laser_pairs[nodemob]
                    mob_lasers.remove(laser)
                    laser.kill()
                    nodemob.remove_by_call(self)
                    nodemob_to_delete.append(nodemob)

            for nodemob in nodemob_to_delete:
                del self.nodemob_laser_pairs[nodemob]

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))

            nodemob_to_delete = []
            for nodemob in self.nodemob_laser_pairs.keys():
                laser = self.nodemob_laser_pairs[nodemob]
                mob_lasers.remove(laser)
                laser.kill()
                nodemob.remove_by_call(self)
                nodemob_to_delete.append(nodemob)

            for nodemob in nodemob_to_delete:
                del self.nodemob_laser_pairs[nodemob]
            self.kill()

    def remove_by_call(self, sp):
        if sp in self.nodemob_laser_pairs.keys():
            laser = self.nodemob_laser_pairs[sp]
            mob_lasers.remove(laser)
            laser.kill()
            del self.nodemob_laser_pairs[sp]


class Nodemob1Laser(pygame.sprite.Sprite):
    """
    a laser wall generated between two Nodemobs
    attacks player continuously when being touched
    """
    group = pygame.sprite.Group()

    def __init__(self, nodes):
        pygame.sprite.Sprite.__init__(self)
        self.nodes = nodes
        self.color1 = GREEN1
        self.color2 = WHITE1
        self.color_list = [self.color1, self.color2]
        self.color_change = 0
        self.power = 5      # per frame
        self.range = 20

        self.group.add(self)

    def update(self):
        self.color_change = abs(self.color_change - 1)
        self.color1 = self.color_list[self.color_change]

        if self.nodes[0].dead or self.nodes[1].dead:
            self.kill()

    def draw(self):
        pygame.draw.line(screen, self.color1, self.nodes[0].rect.center, self.nodes[1].rect.center, 16)
        pygame.draw.line(screen, self.color2, self.nodes[0].rect.center, self.nodes[1].rect.center, 8)


class SwellerMob1(pygame.sprite.Sprite):
    """
    Acts like MoveLineMobs, but gets bigger when get damaged

    """
    group = pygame.sprite.Group()

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.min_size = 30
        self.full_swell_size = 300
        self.size = [self.min_size] * 2
        self.debris_size = 35
        self.debris_speed = random.randrange(13, 34)
        self.norm_image = swellermob1_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = swellermob1_hit_anim
        self.rect = self.image.get_rect()
        self.speed = random.randrange(4, 9)
        self.damage = 570
        self.hit = False
        self.hitcount = 0
        self.hp = 200
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 1115
        self.no_points = False

        self.angle = random.uniform(-math.pi, math.pi)
        self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
        self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                      (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        self.speedx = self.speed * math.cos(self.angle)
        self.speedy = self.speed * math.sin(self.angle)
        self.rect.centerx = round(self.abs_x - screen_center[0])
        self.rect.centery = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.spawned = False
        self.spawn_effect = SpawnEffect(self.rect.center, [self.size[0], self.size[1]])
        all_sprites.add(self.spawn_effect)
        spawns.add(self.spawn_effect)

        self.group.add(self)

    def update(self):
        if not self.spawned:
            if self.spawn_effect.complete:
                self.spawned = True
                self.spawn_effect.kill()
                all_mobs.add(self)
                self.rect.centerx = round(self.abs_x - screen_center[0])
                self.rect.centery = round(self.abs_y - screen_center[1] + field_shift_pos)
            return

        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.size = [round(self.min_size + (self.full_swell_size - self.min_size) * (1 - self.hp / self.hp_full))] * 2
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.rect = self.image.get_rect()
                    self.hitcount += 1

            if not (-3 * self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < (
                    SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width + 2 * self.rect.width and
                    -3 * self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < (
                            SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height + 2 * self.rect.height):
                if self.abs_x <= -3 * self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width:
                    self.abs_x = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width + self.rect.width
                elif self.abs_x >= (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width + 2 * self.rect.width:
                    self.abs_x = -2 * self.rect.width - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width + 1
                elif self.abs_y <= -3 * self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height:
                    self.abs_y = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height + self.rect.height
                else:
                    self.abs_y = -2 * self.rect.height - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height

            if random.random() <= 0.04:
                self.angle = random.uniform(self.angle - math.pi / 2, self.angle + math.pi / 2)
                self.speedx = self.speed * math.cos(self.angle)
                self.speedy = self.speed * math.sin(self.angle)
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.centerx = round(self.abs_x - screen_center[0])
            self.rect.centery = round(self.abs_y - screen_center[1] + field_shift_pos)

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.centerx = round(self.abs_x - screen_center[0])
            self.rect.centery = round(self.abs_y - screen_center[1] + field_shift_pos)
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class MineBomb(pygame.sprite.Sprite):
    group = pygame.sprite.Group()

    def __init__(self, pos, power, timer, shock_range, sensor_mode=False, hide=False):
        pygame.sprite.Sprite.__init__(self)
        self.size = (30, 30)
        self.debris_size = 10
        self.debris_speed = random.randrange(9, 15)
        self.off_image = minebomb_off_img
        self.on_image = minebomb_on_img
        self.image = pygame.transform.scale(self.off_image, self.size)
        self.off_hit_anim = minebomb_off_hit_anim
        self.on_hit_anim = minebomb_on_hit_anim
        self.hit_anim = minebomb_off_hit_anim
        self.rect = self.image.get_rect()
        self.damage = power
        self.hit = False
        self.hitcount = 0
        self.hp = 100
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 213
        self.no_points = False
        self.power = power
        self.abs_x, self.abs_y = pos

        self.on = False
        self.timer = timer
        self.frames = round(self.timer * fps)
        self.sensor_mode = sensor_mode
        self.timer_start = False if self.sensor_mode else True
        self.time_left = self.timer

        self.shock_range = shock_range
        self.hide = hide

        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.spawned = False
        self.spawn_effect = SpawnEffect(self.rect.center, self.size)
        all_sprites.add(self.spawn_effect)
        spawns.add(self.spawn_effect)

        all_sprites.add(self)
        self.group.add(self)

    def update(self):
        if not self.spawned:
            if self.spawn_effect.complete:
                self.spawned = True
                self.spawn_effect.kill()
                all_mobs.add(self)
                self.rect.x = round(self.abs_x - screen_center[0])
                self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            return
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            if self.sensor_mode:
                pass

            if self.timer_start:
                if self.frames % math.ceil(self.frames / fps) == 0:
                    self.on = not self.on
                    self.image = pygame.transform.scale(self.on_image if self.on else self.off_image, self.size)
                    self.hit_anim = self.on_hit_anim if self.on else self.off_hit_anim
                self.frames -= 1

            if self.frames == 0:
                self.dead = True
                self.no_points = True

        else:
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
                if random.random() <= ITEM_DROP_PROBABILITY:
                    item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                    all_sprites.add(item)
                    items.add(item)
                expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
                Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            else:
                Shockwave(self.rect.center, self.shock_range)
                expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
                Explosion(self.rect.center, expl_type, (round(self.size[0] * 6), round(self.size[1] * 6)))
                player_dist = distance(self.rect.center, player.rect.center)
                if player_dist <= self.shock_range:
                    player.hp -= self.power * (1 - player_dist / (2 * self.shock_range))
            self.kill()


class BossLV1(MoveLineMob):
    """
    level 1 boss
    similar to MoveLineMobs, but has very large size, very low speed, very high hp
    """
    def __init__(self):
        MoveLineMob.__init__(self, [200, 200], 40, 25, boss_lv1_img, boss_lv1_hit_anim, 2, 5000, 300, 5000)
        self.type = random.randrange(1, 5)
        if self.type == 1:
            self.abs_x = random.randrange(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width + self.rect.width,
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width * 2)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height
            self.angle = random.uniform(math.pi / 4, math.pi * 3 / 4)
        elif self.type == 2:
            self.abs_x = random.randrange(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width + self.rect.width,
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width * 2)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height
            self.angle = random.uniform(-math.pi * 3 / 4, -math.pi / 4)
        elif self.type == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height + self.rect.height,
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height * 2)
            self.angle = random.uniform(-math.pi / 4, math.pi / 4)
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height + self.rect.height,
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height * 2)
            self.angle = random.uniform(math.pi * 3 / 4, math.pi * 5 / 4)
        self.speedx = self.speed * math.cos(self.angle)
        self.speedy = self.speed * math.sin(self.angle)

        self.in_map = False

    def update(self):
        MoveLineMob.update(self)
        if not self.dead and self.spawned:
            if -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width \
                    and -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height:
                self.in_map = True
            if self.in_map:
                if self.abs_x <= -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width or self.abs_x >= (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width:
                    self.speedx = -self.speedx
                elif self.abs_y <= -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height or self.abs_y >= (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height:
                    self.speedy = -self.speedy
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

        elif self.dead:
            global field_shift_magnitude, field_shift_length, field_shake_start
            field_shift_magnitude = 20
            field_shift_length = 2
            field_shake_start = True


class BossLV2(pygame.sprite.Sprite):
    """
    level 2 boss
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
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 7500
        self.no_points = False
        self.type = random.randrange(1, 5)
        if self.type == 1:
            self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height
        elif self.type == 2:
            self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height
        elif self.type == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.speedx = self.speed * (player.rect.center[0] - self.rect.center[0]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
        self.speedy = self.speed * (player.rect.center[1] - self.rect.center[1]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
        self.shield_group = pygame.sprite.Group()
        self.generate_shield(5, (30, 30), (10, 10), 8, random.randrange(6, 13), shieldunit1_img, shieldunit1_hit_anim, 6, 2, 2)
        self.generate_shield(1, (8, 8), (50, 50), 20, random.randrange(10, 18), shieldunit2_img, shieldunit2_hit_anim, 110, 25, 20)
        self.generate_shield(3, (26, 26), (20, 20), 14, random.randrange(8, 16), shieldunit3_img, shieldunit3_hit_anim, 25, 10, 10)

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
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
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            self.shield_group.update((self.rect.x, self.rect.y))

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)

            global field_shift_magnitude, field_shift_length, field_shake_start
            field_shift_magnitude = 20
            field_shift_length = 2
            field_shake_start = True

            for e in range(random.randrange(5, 8)):
                expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
                Explosion((random.randrange(self.rect.width) + self.rect.x, random.randrange(self.rect.height) + self.rect.y), expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            for s in self.shield_group:
                s.dead = True
            self.shield_group.update((self.rect.x, self.rect.y))
            self.kill()

    def generate_shield(self, layer, shield_size, unit_size, debris_size, debris_speed, image, hit_anim, damage, hp, points):
        shield_width = shield_size[0] * unit_size[0]
        shield_height = shield_size[1] * unit_size[1]
        pos = ((self.size[0] - shield_width) // 2, (self.size[1] - shield_height) // 2)
        for q in range(shield_size[1]):
            if q in range(layer, shield_size[1] - layer):
                for p in range(layer):
                    shield_unit = FollowerMobShieldUnit((self.rect.x, self.rect.y),
                                                        (pos[0] + p * unit_size[0], pos[1] + q * unit_size[1]),
                                                        unit_size, debris_size, debris_speed, image, hit_anim, damage,
                                                        hp, points)
                    self.shield_group.add(shield_unit)
                    all_mobs.add(shield_unit)
                for p in range(shield_size[0] - layer, shield_size[0]):
                    shield_unit = FollowerMobShieldUnit((self.rect.x, self.rect.y),
                                                        (pos[0] + p * unit_size[0], pos[1] + q * unit_size[1]),
                                                        unit_size, debris_size, debris_speed, image, hit_anim, damage,
                                                        hp, points)
                    self.shield_group.add(shield_unit)
                    all_mobs.add(shield_unit)
            else:
                for p in range(shield_size[0]):
                    shield_unit = FollowerMobShieldUnit((self.rect.x, self.rect.y),
                                                        (pos[0] + p * unit_size[0], pos[1] + q * unit_size[1]),
                                                        unit_size, debris_size, debris_speed, image, hit_anim, damage,
                                                        hp, points)
                    self.shield_group.add(shield_unit)
                    all_mobs.add(shield_unit)


class BossLV3(pygame.sprite.Sprite):
    """
    level 3 boss
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
        self.hp = 4000
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
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
            self.abs_y = -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height - self.rect.height
            self.speedx = 0
            self.speedy = self.speed
        elif self.movetype == 2:
            self.abs_x = screen_width // 2 - self.size[0] // 2
            self.abs_y = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height
            self.speedx = 0
            self.speedy = -self.speed
        elif self.movetype == 3:
            self.abs_x = -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width - self.rect.width
            self.abs_y = screen_height // 2 - self.size[1] // 2
            self.speedx = self.speed
            self.speedy = 0
        else:
            self.abs_x = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width
            self.abs_y = screen_height // 2 - self.size[1] // 2
            self.speedx = -self.speed
            self.speedy = 0
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.in_map = False

    def update(self):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            else:
                self.image = pygame.transform.scale(self.norm_image, self.size)

            if -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width \
                    and -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height:
                self.in_map = True
            if self.in_map:
                if self.abs_x <= -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width or self.abs_x >= (
                        SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width:
                    self.speedx = -self.speedx
                elif self.abs_y <= -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height or self.abs_y >= (
                        SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height:
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
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

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
                        bullet = Bullet(13, 11.7, (7, 7), RED1, self.rect.center, math.radians(self.shoot_angle), True)
                        all_sprites.add(bullet)
                        mob_bullets.add(bullet)
                        bullet = Bullet(13, 11.7, (7, 7), RED1, self.rect.center, math.radians(self.shoot_angle + 180), True)
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

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt,
                      self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            global field_shift_magnitude, field_shift_length, field_shake_start
            field_shift_magnitude = 20
            field_shift_length = 2
            field_shake_start = True

            for e in range(random.randrange(20, 25)):
                expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
                Explosion((random.randrange(self.rect.width) + self.rect.x, random.randrange(self.rect.height) + self.rect.y), expl_type, (round(self.size[0]), round(self.size[1])))
            self.kill()

    def generate_mobs(self):
        pass


class BossLV4(pygame.sprite.Sprite):
    """
    level 4 boss
    moves toward player
    protected by 12 shells
    3 attack patterns: cannon, generating child mobs, boosting
    """
    SHELL_TYPE_CNT = 12

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
        self.hp = 3000
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
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
            self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(-self.rect.height * 2, -self.rect.height) - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height
        elif self.type == 2:
            self.abs_x = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width)
            self.abs_y = random.randrange(self.rect.height, self.rect.height * 2) + (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height
        elif self.type == 3:
            self.abs_x = random.randrange(-self.rect.width * 2, -self.rect.width) - (SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width
            self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        else:
            self.abs_x = random.randrange(self.rect.width, self.rect.width * 2) + (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width
            self.abs_y = random.randrange(round(-(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height),
                                          (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height)
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.speedx = self.speed * (player.rect.center[0] - self.rect.center[0]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
        self.speedy = self.speed * (player.rect.center[1] - self.rect.center[1]) / math.sqrt((player.rect.center[0] - self.rect.center[0]) * (player.rect.center[0] - self.rect.center[0]) + (player.rect.center[1] - self.rect.center[1]) * (player.rect.center[1] - self.rect.center[1]))
        self.in_map = False
        self.shell1 = BossLV4Shell([200, 200], 1, 900, self.rect.center)
        self.shell2 = BossLV4Shell([200, 200], 2, 900, self.rect.center)
        self.shell3 = BossLV4Shell([200, 200], 3, 900, self.rect.center)
        self.shell4 = BossLV4Shell([200, 200], 4, 900, self.rect.center)
        self.shell5 = BossLV4Shell([89, 178], 5, 600, self.rect.center)
        self.shell6 = BossLV4Shell([178, 178], 6, 800, self.rect.center)
        self.shell7 = BossLV4Shell([178, 89], 7, 600, self.rect.center)
        self.shell8 = BossLV4Shell([178, 178], 8, 800, self.rect.center)
        self.shell9 = BossLV4Shell([89, 178], 9, 600, self.rect.center)
        self.shell10 = BossLV4Shell([178, 178], 10, 800, self.rect.center)
        self.shell11 = BossLV4Shell([178, 89], 11, 600, self.rect.center)
        self.shell12 = BossLV4Shell([178, 178], 12, 800, self.rect.center)
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
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width < self.abs_x < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width \
                    and -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height < self.abs_y < (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height:
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
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

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
                                    children_cnt = random.randrange(30, 40)
                                    for c in range(children_cnt):
                                        direction = random.uniform(angle + math.pi / 6, angle + math.pi * 11 / 6)
                                        child = BossLV4Child((random.randrange(self.rect.width / 5) + self.abs_x + self.rect.width * 2 / 5, random.randrange(self.rect.height / 5) + self.abs_y + self.rect.height * 2 / 5), direction, "attack", self)
                                        all_sprites.add(child)
                                        all_mobs.add(child)
                                        self.attack_childs.add(child)
                                elif len(self.shield_childs) < 400:
                                    children_cnt = random.randrange(100, 130)
                                    for c in range(children_cnt):
                                        direction = random.uniform(0, 2 * math.pi)
                                        child = BossLV4Child((random.randrange(self.rect.width / 5) + self.abs_x + self.rect.width * 2 / 5, random.randrange(self.rect.height / 5) + self.abs_y + self.rect.height * 2 / 5), direction, "shield", self)
                                        all_sprites.add(child)
                                        all_mobs.add(child)
                                        self.shield_childs.add(child)
                                expl_type = random.randrange(1, 12)
                                Explosion(self.rect.center, expl_type, (round(self.size[0] * 0.4), round(self.size[1] * 0.4)))
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
                                    cannonball = MobExplodingCannonBall1(self.rect.center, start_angle, 47, 12)
                                    all_sprites.add(cannonball)
                                    mob_cannon_balls.add(cannonball)
                                    start_angle += math.pi / 14
                                expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
                                Explosion(self.rect.center, expl_type, (round(self.size[0] * 0.4), round(self.size[1] * 0.4)))
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
                        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
                    if not self.in_map and not self.reflected:
                        if self.abs_x <= -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width or self.abs_x >= (
                                SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width - self.rect.width:
                            self.speedx = -self.speedx
                            self.boost_accx = -self.boost_accx
                            self.reflected = True
                        elif self.abs_y <= -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height or self.abs_y >= (
                                SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height - self.rect.height:
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
                    cannonball = MobExplodingCannonBall1(self.rect.center, angle, 47, 12)
                    all_sprites.add(cannonball)
                    mob_cannon_balls.add(cannonball)
                    self.cannon_fired = time.time()
                for s in self.shells:
                    if not s.dead:
                        s.update(self.rect.center)

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt,
                      self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if len(self.shells) <= 0:

                global field_shift_magnitude, field_shift_length, field_shake_start
                field_shift_magnitude = 20
                field_shift_length = 2
                field_shake_start = True

                for e in range(random.randrange(20, 25)):
                    expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
                    Explosion((random.randrange(self.rect.width) + self.rect.x, random.randrange(self.rect.height) + self.rect.y), expl_type, (round(self.size[0]), round(self.size[1])))
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
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
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
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
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

            if time.time() - self.hp_bar_show_start_time > 3:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(max(self.size) * MOB_EXPLOSION_SIZE_RATIO), round(max(self.size) * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class BossLV4Child(pygame.sprite.Sprite):
    def __init__(self, abs_pos, direction, mode, mother_boss):
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
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 40
        self.no_points = False

        self.mother_boss = mother_boss
        self.abs_x = abs_pos[0]
        self.abs_y = abs_pos[1]
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        self.speedx = self.speed * math.cos(self.dir)
        self.speedy = self.speed * math.sin(self.dir)
        self.dist_x = 0
        self.dist_y = 0
        if self.mode == "attack":
            self.dist_x = player.rect.center[0] - self.rect.center[0]
            self.dist_y = player.rect.center[1] - self.rect.center[1]
        elif self.mode == "shield":
            self.dist_x = self.mother_boss.rect.center[0] - self.rect.center[0]
            self.dist_y = self.mother_boss.rect.center[1] - self.rect.center[1]
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
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
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
                self.dist_x = self.mother_boss.rect.center[0] - self.rect.center[0]
                self.dist_y = self.mother_boss.rect.center[1] - self.rect.center[1]
                self.acc_dir = math.atan2(self.dist_y, self.dist_x)
                if distance(self.mother_boss.rect.center, self.rect.center) <= 400:
                    self.acc_x = 0
                    self.acc_y = 0
                elif distance(self.mother_boss.rect.center, self.rect.center) >= 400:
                    self.acc_x = self.acc * math.cos(self.acc_dir)
                    self.acc_y = self.acc * math.sin(self.acc_dir)
            self.speedx = min(self.speedx + self.acc_x, self.max_speed)
            self.speedy = min(self.speedy + self.acc_y, self.max_speed)
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            if random.random() <= ITEM_DROP_PROBABILITY:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], "regenerate")
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class BossLV5(pygame.sprite.Sprite):
    """
    level 5 boss
    similar to orbitmobs
    always at the center
    has many orbits and orbitmobs
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (400, 400)
        self.debris_size = 40
        self.debris_speed = 25
        self.phase1_image = boss_lv5_phase1_img
        self.phase2_image = boss_lv5_phase2_img
        self.image = pygame.transform.scale(self.phase1_image, self.size)
        self.phase1_hit_anim = boss_lv5_phase1_hit_anim
        self.phase2_hit_anim = boss_lv5_phase2_hit_anim
        self.hit_anim = self.phase1_hit_anim
        self.rect = self.image.get_rect()
        self.speed = 4
        self.moving_frames = round(screen_width * 2.5 / self.speed)
        self.moved_frames = 0
        self.damage = 30000
        self.hit = False
        self.hitcount = 0
        self.hp = 6000
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 40000
        self.no_points = False
        self.phase = 1
        self.stop = False

        self.orbiter = None
        self.opposite = True
        self.orbit1_orbiters = pygame.sprite.Group()            # outer orbit
        self.orbit1_orbiter_cnt = 120
        self.orbit1_radius = 1200
        self.orbit2_orbiters = pygame.sprite.Group()            # middle1 orbit
        self.orbit2_orbiter_cnt = 90
        self.orbit2_radius = 900
        self.orbit3_orbiters = pygame.sprite.Group()            # middle2 orbit
        self.orbit3_orbiter_cnt = 60
        self.orbit3_radius = 600
        self.orbit4_orbiters = pygame.sprite.Group()            # inner orbit
        self.orbit4_orbiter_cnt = 30
        self.orbit4_radius = 300
        self.straight_line_orbiters = pygame.sprite.Group()     # straight-line orbit
        self.straight_line_orbiter_cnt = 25

        self.cannon_spread_attack = False
        self.cannon_spread_attack_time = 5
        self.cannon_spread_attack_start_time = 0

        self.cannon_circular_attack = False
        self.cannon_circular_attack_start_time = 0

        self.minebomb_attack = False
        self.minebomb_attack_start_time = 0
        self.minebomb_spawned_time = 0
        self.minebomb_spawn_interval = 0   # frames
        self.minebomb_spawned_frames = 0
        self.minebomb_distance = 0
        self.minebomb_distance_inc = 0
        self.minebomb_angle = 0
        self.minebomb_density = 0
        self.minebomb_density_inc = 0

        self.type = random.randrange(1, 5)
        if self.type == 1:
            self.abs_x = screen_width // 2 - self.rect.width // 2
            self.abs_y = -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height - 1800 - self.rect.height // 2
            self.speedx = 0
            self.speedy = self.speed
        elif self.type == 2:
            self.abs_x = screen_width // 2 - self.rect.width // 2
            self.abs_y = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height + 1800 - self.rect.height // 2
            self.speedx = 0
            self.speedy = -self.speed
        elif self.type == 3:
            self.abs_x = -(SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width - 1200 - self.rect.width // 2
            self.abs_y = screen_height // 2 - self.rect.height // 2
            self.speedx = self.speed
            self.speedy = 0
        else:
            self.abs_x = (SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width + 1200 - self.rect.width // 2
            self.abs_y = screen_height // 2 - self.rect.height // 2
            self.speedx = -self.speed
            self.speedy = 0
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

        for num in range(self.orbit1_orbiter_cnt):
            self.orbiter = BossLV5Orbiter(self.rect.center, self.orbit1_radius, 0.003, num * math.radians(3), 3, self.opposite)
            self.orbit1_orbiters.add(self.orbiter)
            all_mobs.add(self.orbiter)
            self.opposite = not self.opposite

        for num in range(self.orbit2_orbiter_cnt):
            self.orbiter = BossLV5Orbiter(self.rect.center, self.orbit2_radius, 0.005, num * math.radians(4), 3, self.opposite)
            self.orbit2_orbiters.add(self.orbiter)
            all_mobs.add(self.orbiter)
            self.opposite = not self.opposite

        for num in range(self.orbit3_orbiter_cnt):
            self.orbiter = BossLV5Orbiter(self.rect.center, self.orbit3_radius, 0.007, num * math.radians(6), 3, self.opposite)
            self.orbit3_orbiters.add(self.orbiter)
            all_mobs.add(self.orbiter)
            self.opposite = not self.opposite

        for num in range(self.orbit4_orbiter_cnt):
            self.orbiter = BossLV5Orbiter(self.rect.center, self.orbit4_radius, 0.01, num * math.radians(12), 3, self.opposite)
            self.orbit4_orbiters.add(self.orbiter)
            all_mobs.add(self.orbiter)
            self.opposite = not self.opposite

        self.spawned_time = time.time()


    def update(self):
        global score
        if self.hp <= 0:
            if self.phase == 2:
                self.dead = True
            else:
                self.phase += 1
                self.hp_full = 8000
                self.hp = self.hp_full
                self.image = pygame.transform.scale(self.phase2_image, self.size)
                self.hit_anim = self.phase2_hit_anim

                global field_shift_magnitude, field_shift_length, field_shake_start
                field_shift_magnitude = 20
                field_shift_length = 2
                field_shake_start = True

                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt,
                      self.debris_speed)

                for e in range(random.randrange(5, 8)):
                    expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
                    Explosion((random.randrange(self.rect.width) + self.rect.x, random.randrange(self.rect.height) + self.rect.y), expl_type, (self.size[0], self.size[1]))

        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if not self.stop:
                self.moved_frames += 1
                if self.moved_frames >= self.moving_frames:
                    self.speedx = 0
                    self.speedy = 0
                    self.stop = True

            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            # ganerate outer orbit
            if len(self.orbit1_orbiters) <= self.orbit1_orbiter_cnt // 2:
                for num in range(self.orbit1_orbiter_cnt):
                    self.orbiter = BossLV5Orbiter(self.rect.center, self.orbit1_radius, 0.003, num * 2 * math.pi / 120, 3, self.opposite)
                    self.orbit1_orbiters.add(self.orbiter)
                    all_mobs.add(self.orbiter)
                    self.opposite = not self.opposite
            for orbiter in self.orbit1_orbiters:
                orbiter.update(self.rect.center)

            # ganerate middle1 orbit
            if len(self.orbit2_orbiters) <= self.orbit2_orbiter_cnt // 2:
                for num in range(self.orbit2_orbiter_cnt):
                    self.orbiter = BossLV5Orbiter(self.rect.center, self.orbit2_radius, 0.005, num * math.radians(4), 3, self.opposite)
                    self.orbit2_orbiters.add(self.orbiter)
                    all_mobs.add(self.orbiter)
                    self.opposite = not self.opposite
            for orbiter in self.orbit2_orbiters:
                orbiter.update(self.rect.center)

            # ganerate middle2 orbit
            if len(self.orbit3_orbiters) <= self.orbit3_orbiter_cnt // 2:
                for num in range(self.orbit3_orbiter_cnt):
                    self.orbiter = BossLV5Orbiter(self.rect.center, self.orbit3_radius, 0.007, num * math.radians(6), 3, self.opposite)
                    self.orbit3_orbiters.add(self.orbiter)
                    all_mobs.add(self.orbiter)
                    self.opposite = not self.opposite
            for orbiter in self.orbit3_orbiters:
                orbiter.update(self.rect.center)

            # ganerate inner orbit
            if len(self.orbit4_orbiters) <= self.orbit4_orbiter_cnt // 2:
                for num in range(self.orbit4_orbiter_cnt):
                    self.orbiter = BossLV5Orbiter(self.rect.center, self.orbit4_radius, 0.01, num * math.radians(12), 3, self.opposite)
                    self.orbit4_orbiters.add(self.orbiter)
                    all_mobs.add(self.orbiter)
                    self.opposite = not self.opposite
            for orbiter in self.orbit4_orbiters:
                orbiter.update(self.rect.center)

            # generate straight-line orbit
            if len(self.straight_line_orbiters) <= 150 and random.random() < 0.002 and self.stop:
                self.opposite = random.choice([True, False])
                speed = random.uniform(0.006, 0.012)
                angle = random.uniform(-math.pi, math.pi)
                for num in range(self.straight_line_orbiter_cnt):
                    self.orbiter = BossLV5Orbiter(self.rect.center, 200 + num * 40, speed, angle, 2.5 + .3125 * num, self.opposite)
                    self.straight_line_orbiters.add(self.orbiter)
                    all_mobs.add(self.orbiter)
            for orbiter in self.straight_line_orbiters:
                orbiter.update(self.rect.center)

            # spread cannonballs
            if random.random() < 0.0007 and self.stop and not self.cannon_circular_attack:
                self.cannon_spread_attack = True
                self.cannon_spread_attack_start_time = time.time()
            if self.cannon_spread_attack:
                for num in range(3):
                    cannonball = MobExplodingCannonBall1(self.rect.center, random.uniform(-math.pi, math.pi), 46, 8)
                    all_sprites.add(cannonball)
                    mob_cannon_balls.add(cannonball)
                if time.time() - self.cannon_spread_attack_start_time >= self.cannon_spread_attack_time:
                    self.cannon_spread_attack = False

            # circular cannon attack
            if self.phase == 2 and random.random() < 0.001 and not self.cannon_spread_attack and not self.cannon_circular_attack:
                number_of_cannons = 18
                for c1 in range(5):
                    angle = -math.pi / 2 + c1 * 2 * math.pi / 5
                    cannonball_ganerate_pos = [round(152 * math.cos(angle)), round(152 * math.sin(angle))]
                    first_cannon_shoot_angle = random.uniform(-math.pi, math.pi)
                    for c2 in range(number_of_cannons):
                        cannonball = MobChargingCannonBall2(self.rect.center, 50, 3, 105, 13, self, cannonball_ganerate_pos, False, first_cannon_shoot_angle + c2 * 2 * math.pi / number_of_cannons)
                        all_sprites.add(cannonball)
                        mob_cannon_balls.add(cannonball)

                self.cannon_circular_attack = True
                self.cannon_circular_attack_start_time = time.time()

            if self.cannon_circular_attack and time.time() - self.cannon_circular_attack_start_time >= 3:
                self.cannon_circular_attack = False

            # minebomb attack
            if self.stop:
                if not self.minebomb_attack:
                    if self.phase == 1:
                        if random.random() < 0.0008:
                            self.minebomb_attack = True
                            self.minebomb_attack_start_time = time.time()
                            self.minebomb_spawn_interval = 15
                            self.minebomb_spawned_frames = 0
                            self.minebomb_distance = 300
                            self.minebomb_distance_inc = 150
                            self.minebomb_density = 8
                            self.minebomb_density_inc = 4
                    else:
                        if random.random() < 0.0012:
                            self.minebomb_attack = True
                            self.minebomb_attack_start_time = time.time()
                            self.minebomb_spawn_interval = 5
                            self.minebomb_spawned_frames = 0
                            self.minebomb_distance = 300
                            self.minebomb_distance_inc = 100
                            self.minebomb_density = 12
                            self.minebomb_density_inc = 4

                else:
                    if self.minebomb_distance <= 900:
                        if self.minebomb_spawned_frames % self.minebomb_spawn_interval == 0:
                            self.minebomb_angle = random.uniform(-math.pi, math.pi)
                            for m in range(self.minebomb_density):
                                spawn_angle = self.minebomb_angle + m * 2 * math.pi / self.minebomb_density
                                spawn_xpos = self.abs_x + self.rect.width // 2 + self.minebomb_distance * math.cos(spawn_angle)
                                spawn_ypos = self.abs_y + self.rect.height // 2 + self.minebomb_distance * math.sin(spawn_angle)
                                MineBomb([spawn_xpos, spawn_ypos], 100, 4, 200)
                            self.minebomb_distance += self.minebomb_distance_inc
                            self.minebomb_density += self.minebomb_density_inc
                        self.minebomb_spawned_frames += 1

                    if time.time() - self.minebomb_attack_start_time >= 10:
                        self.minebomb_attack = False

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

            field_shift_magnitude = 30
            field_shift_length = 3
            field_shake_start = True

            for e in range(random.randrange(5, 8)):
                expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
                Explosion((random.randrange(self.rect.width) + self.rect.x, random.randrange(self.rect.height) + self.rect.y), expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))

            for orb in self.orbit1_orbiters:
                orb.dead = True
                orb.update(self.rect.center)
            for orb in self.orbit2_orbiters:
                orb.dead = True
                orb.update(self.rect.center)
            for orb in self.orbit3_orbiters:
                orb.dead = True
                orb.update(self.rect.center)
            for orb in self.orbit4_orbiters:
                orb.dead = True
                orb.update(self.rect.center)
            self.kill()


class BossLV5Orbiter(pygame.sprite.Sprite):
    """
    orbiter of boss lv5
    circles around BossLV5
    """
    def __init__(self, pos, max_distance, max_angular_speed, angular_pos, orthogonal_speed, opposite=False):
        pygame.sprite.Sprite.__init__(self)
        self.size = [40, 40]
        self.debris_size = 10
        self.debris_speed = random.randrange(5, 9)
        self.norm_image = boss_lv5_orbiter_img
        self.image = pygame.transform.scale(self.norm_image, self.size)
        self.hit_anim = boss_lv5_orbiter_hit_anim
        self.rect = self.image.get_rect()
        self.damage = 90
        self.hit = False
        self.hitcount = 0
        self.hp = 20
        self.hp_full = self.hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = 56
        self.no_points = False

        self.reached_max_angular_speed = False
        self.on_orbit = False
        self.orthogonal_speed = orthogonal_speed
        self.max_distance_to_mothership = max_distance
        self.distance_to_mothership = 0
        self.angular_pos = angular_pos
        self.max_angular_speed = max_angular_speed
        self.angular_speed = 0
        self.relative_x = self.distance_to_mothership * math.cos(self.angular_pos)
        self.relative_y = self.distance_to_mothership * math.sin(self.angular_pos)
        self.opposite = -1 if opposite else 1

        self.abs_x = pos[0] + self.relative_x - self.rect.width // 2
        self.abs_y = pos[1] + self.relative_y - self.rect.height // 2
        self.rect.x = round(self.abs_x)
        self.rect.y = round(self.abs_y + field_shift_pos)

    def update(self, pos=(0, 0)):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1

            if not self.reached_max_angular_speed:
                if self.angular_speed >= self.max_angular_speed:
                    self.reached_max_angular_speed = True
                self.angular_speed += 0.001

            if not self.on_orbit:
                self.distance_to_mothership += self.orthogonal_speed
                if self.distance_to_mothership >= self.max_distance_to_mothership:
                    self.on_orbit = True

            self.angular_pos += self.opposite * self.angular_speed
            self.relative_x = self.distance_to_mothership * math.cos(self.angular_pos)
            self.relative_y = self.distance_to_mothership * math.sin(self.angular_pos)
            self.abs_x = pos[0] + self.relative_x - self.rect.width // 2
            self.abs_y = pos[1] + self.relative_y - self.rect.height // 2
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            self.rect.x = round(self.abs_x)
            self.rect.y = round(self.abs_y)
            if random.random() <= 0.02:
                item = Item([self.rect.center[0] + screen_center[0], self.rect.center[1] + screen_center[1]], get_item_type())
                all_sprites.add(item)
                items.add(item)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            expl_size = max(self.size)
            Explosion(self.rect.center, expl_type, (round(expl_size * MOB_EXPLOSION_SIZE_RATIO), round(expl_size * MOB_EXPLOSION_SIZE_RATIO)))
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
        self.rect.y = round(master_pos[1] + self.pos[1] + field_shift_pos)
        self.damage = damage
        self.hit = False
        self.hitcount = 0
        self.hp = hp
        self.hp_full = hp
        self.hp_bar_show = False
        self.hp_bar_show_start_time = 0
        self.dead = False
        self.points = points
        self.no_points = False

    def update(self, master_pos=(0, 0)):
        global score
        if self.hp <= 0:
            self.dead = True
        if not self.dead:
            if self.hit:
                self.hp_bar_show = True
                self.hp_bar_show_start_time = time.time()
                if self.hitcount >= len(self.hit_anim):
                    self.hitcount = 0
                    self.hit = False
                else:
                    self.image = pygame.transform.scale(self.hit_anim[self.hitcount], self.size)
                    self.hitcount += 1
            self.rect.x = master_pos[0] + self.pos[0]
            self.rect.y = master_pos[1] + self.pos[1]

            if time.time() - self.hp_bar_show_start_time > MOB_HP_BAR_SHOW_DURATION:
                self.hp_bar_show = False

        else:
            if not self.no_points:
                avg_debris_cnt = round((self.size[0] + self.size[1]) / 10)
                split(self.rect.center, avg_debris_cnt, self.debris_size, self.points / avg_debris_cnt, self.debris_speed)
            expl_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(self.rect.center, expl_type, (round(self.size[0] * MOB_EXPLOSION_SIZE_RATIO), round(self.size[1] * MOB_EXPLOSION_SIZE_RATIO)))
            self.kill()


class SpawnEffect(pygame.sprite.Sprite):
    """
    appears when a mob is spawned
    """
    ANIMATION_FRAME_CNT = 32

    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = pygame.transform.scale(spawneffect_anim[0], self.size)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.frame = 0
        self.complete = False

    def update(self):
        self.frame += 1
        if self.frame == len(spawneffect_anim):
            self.complete = True
        else:
            self.image = pygame.transform.scale(spawneffect_anim[self.frame], self.size)
            self.rect = self.image.get_rect()
            self.rect.x = self.abs_x - screen_center[0]
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)


class HitEffect(pygame.sprite.Sprite):
    """
    appears when a bullet and a mob(or player) collide
    """
    ANIMATION_FRAME_CNT = 9

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
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)


class Explosion(pygame.sprite.Sprite):
    """
    explosion animation
    appears when a mob killed or a cannonball explodes
    """
    MAX_ANIMATION_FRAME_CNT = 32

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

        all_sprites.add(self)
        explosions.add(self)

    def update(self):
        self.frame += 1
        if self.frame == len(explosion_anim[str(self.type)]):
            self.kill()
        else:
            self.image = pygame.transform.scale(explosion_anim[str(self.type)][self.frame], self.size)
            self.rect = self.image.get_rect()
            self.rect.x = self.abs_x - screen_center[0]
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)


class Shockwave(pygame.sprite.Sprite):
    def __init__(self, pos, shock_range):
        pygame.sprite.Sprite.__init__(self)
        self.shock_range = shock_range
        self.size = [self.shock_range * 2, self.shock_range * 2]
        self.image = pygame.Surface(self.size)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.abs_x = self.rect.x + screen_center[0]
        self.abs_y = self.rect.y + screen_center[1]
        self.frame = 6
        self.current_frame = 0

        all_sprites.add(self)

    def update(self):
        self.rect.x = round(self.abs_x - screen_center[0])
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)

        if self.current_frame % 2 == 0:
            pygame.draw.circle(screen, WHITE2, self.rect.center, self.shock_range)

        self.current_frame += 1
        if self.current_frame == self.frame:
            self.kill()


class Debris(pygame.sprite.Sprite):
    """
    spreads with explosion when a mob is killed
    has random size, speed, and direction
    a player gets score by collecting debriz
    generated by "split" function
    """
    TYPE_CNT = 16

    def __init__(self, size, pos, speed, points):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.randrange(16)
        self.orientation = random.randrange(360)
        self.direction = math.radians(random.randrange(360))
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
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
            if distance(self.rect.center, player.rect.center) <= 15:
                global score
                score += self.points
                self.kill()
        else:
            self.abs_x += self.speedx
            self.abs_y += self.speedy
            self.rect.x = round(self.abs_x - screen_center[0])
            self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
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
    game item for player, disappears 10s after generated, dropped by mobs at 2% chance
    regenerate: heals player
    recharge: charges player's mp
    """
    def __init__(self, pos, item_type):
        pygame.sprite.Sprite.__init__(self)
        self.type = item_type
        if self.type == "regenerate":
            self.image = pygame.Surface((15, 15))
            self.image.fill(GREEN1)
        elif self.type == "recharge":
            self.image = pygame.Surface((15, 15))
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
        self.rect.y = round(self.abs_y - screen_center[1] + field_shift_pos)
        current_time = time.time()
        if current_time - self.droptime >= 10:
            self.kill()

    def buff(self):
        if self.type == "regenerate":
            player.hp += player.hp_full / 6
            if player.hp > player.hp_full:
                player.hp = player.hp_full
        elif self.type == "recharge":
            player.mp += player.mp_full / 4
            if player.mp > player.mp_full:
                player.mp = player.mp_full


def get_item_type():
    return "regenerate" if random.random() < 0.7 else "recharge"


class Level:
    def __init__(self, level_num, buttonpos, boss_mob, boss_phase=None):
        self.level = level_num
        self.buttonpos = buttonpos
        self.boss_class = boss_mob
        self.boss = boss_mob
        self.boss_phase = boss_phase
        self.boss_with_mobs = False if str(type(self.boss_phase)) == "<class 'NoneType'>" else True
        self.pointer = None

        self.mob_score = 0
        self.mob_start_score = 0
        self.score = 0
        self.start_score = 0
        self.mob_playtime = 0
        self.mob_start_time = 0
        self.boss_playtime = 0
        self.boss_start_time = 0
        self.playtime = 0
        self.start_time = 0
        self.mob_avg_score = 0
        self.avg_score = 0

        self.break_start_time = 0

        self.phases = []
        self.phase_bound_orig = [0]
        self.phase_bound = [0]
        self.phase_num = 0
        self.phase_text = "LEVEL {} / PHASE {}".format(self.level, self.phase_num + 1)
        self.boss_challenging = False
        self.clear = False
        self.quit = False

        self.start_from_this_level = False

        self.start_button = Button(self.buttonpos, WHITE1, "Start from LEVEL {}".format(self.level), 20)
        all_buttons.add(self.start_button)

    def add_phase(self, moblist, mob_count_list, phase_bound_value, kill_all_after_phase=False):
        new_phase = Phase(moblist, mob_count_list, kill_all_after_phase)
        self.phases.append(new_phase)
        self.phase_bound_orig.append(phase_bound_value)
        self.phase_bound.append(phase_bound_value)

    def initialize_level(self):
        global score
        self.phase_bound = self.phase_bound_orig.copy()
        for phase_bound_value in range(len(self.phase_bound)):
            self.phase_bound[phase_bound_value] = self.phase_bound_orig[phase_bound_value] + score
        self.phase_num = 0
        self.phase_text = "LEVEL {} / PHASE {}".format(self.level, self.phase_num + 1)

        self.score = 0
        self.playtime = 0
        self.avg_score = 0
        self.mob_score = 0
        self.mob_playtime = 0
        self.mob_avg_score = 0
        self.boss_playtime = 0
        self.start_score = score
        self.mob_start_score = score
        self.start_time = time.time()
        self.mob_start_time = time.time()
        self.boss_challenging = False
        self.clear = False
        self.quit = False

        self.boss = self.boss_class

        global now_upgrading, paused_time
        paused_time = time.time()
        now_upgrading = True

    def update(self):
        global score
        self.score = score - self.start_score
        self.playtime = time.time() - self.start_time - total_paused_length + .00000000001
        self.avg_score = self.score / self.playtime

        if not self.clear:
            if self.phase_num < len(self.phase_bound) - 1:
                if score < self.phase_bound[self.phase_num + 1]:
                    self.phases[self.phase_num].update()
                else:
                    if self.phases[self.phase_num].kill_all_after_phase:
                        for mobgroup in self.phases[self.phase_num].mobgroup_list:
                            for objs in mobgroup:
                                objs.no_points = True
                                objs.dead = True
                    self.phase_num += 1
                    self.phase_text = "LEVEL {} / PHASE {}".format(self.level, self.phase_num + 1)
                    if self.phase_num == len(self.phase_bound) - 1:
                        self.mob_score = score - self.mob_start_score
                        self.mob_playtime = time.time() - self.mob_start_time
                        self.start_boss_challenge()
            else:
                if self.boss_with_mobs:
                    self.boss_phase.update()

                if random.random() < 0.004:
                    global field_shift_magnitude, field_shift_length, field_vibrate_start
                    field_shift_magnitude = 2
                    field_shift_length = 1.5
                    field_vibrate_start = True

                self.boss_playtime = time.time() - self.boss_start_time - total_paused_length
                if self.boss.dead:
                    self.boss_challenging = False
                    if self.boss_with_mobs:
                        for mobgroup in self.boss_phase.mobgroup_list:
                            for objs in mobgroup:
                                if random.random() < 0.8:
                                    objs.dead = True
                    self.clear = True
                    self.start_break()
        else:
            if time.time() - self.break_start_time >= breaktime:
                self.score = score - self.start_score
                self.playtime = time.time() - self.start_time
                self.avg_score = self.score / self.playtime
                self.quit = True

    def start_boss_challenge(self):
        self.mob_score = score - self.mob_start_score
        self.mob_playtime = time.time() - self.mob_start_time - total_paused_length
        self.mob_avg_score = self.mob_score / self.mob_playtime

        self.phase_text = "LEVEL {} / BOSS CHALLENGE".format(self.level)
        self.boss_start_time = time.time()
        self.boss = self.boss()
        all_sprites.add(self.boss)
        mobs.add(self.boss)
        all_mobs.add(self.boss)
        self.pointer = BossPointer(self.boss)
        all_sprites.add(self.pointer)
        players.add(self.pointer)
        self.boss_challenging = True

    def start_break(self):
        self.boss_playtime = time.time() - self.boss_start_time - total_paused_length

        self.phase_text = "{}s BREAKTIME".format(breaktime)
        self.break_start_time = time.time()
        self.pointer.kill()


class Phase:
    def __init__(self, moblist, mob_count_list, kill_all_after_phase=False):
        self.moblist = moblist
        self.mobgroup_list = [mob.group for mob in self.moblist]
        self.mob_count_list = mob_count_list
        self.kill_all_after_phase = kill_all_after_phase

    def update(self):
        for index in range(len(self.moblist)):
            if self.moblist[index] == WallMobUnit1:
                if len(WallMobUnit1.group) < self.mob_count_list[index]:
                    generate_wall((40, 1), (40, 40), 1, WallMobUnit1.group)
            elif self.moblist[index] == WallMobUnit2:
                if len(WallMobUnit2.group) < self.mob_count_list[index]:
                    generate_wall((40, 2), (40, 40), 2, WallMobUnit2.group)
            elif self.moblist[index] == WallMobUnit3:
                if len(WallMobUnit3.group) < self.mob_count_list[index]:
                    generate_wall((20, 3), (70, 70), 3, WallMobUnit3.group)

            elif len(self.mobgroup_list[index]) < self.mob_count_list[index]:
                add_single_mob(self.moblist[index]())


def draw_hp_bar(sprite):
    pygame.draw.rect(screen, GREEN1, [sprite.rect.x, sprite.rect.y - 10, max(0, round(sprite.rect.width * sprite.hp / sprite.hp_full)), 5])


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
linemob2_armored_img = pygame.image.load(path.join(char_dir, "linemob2_armored.png")).convert()
linemob2_armored_hit_img = pygame.image.load(path.join(char_dir, "linemob2_armored_hit.png")).convert()
linemob2_armored_hit_anim = [linemob2_armored_hit_img, linemob2_armored_img] * 3
linemob3_img = pygame.image.load(path.join(char_dir, "linemob3.png")).convert()
linemob3_hit_img = pygame.image.load(path.join(char_dir, "linemob3_hit.png")).convert()
linemob3_hit_anim = [linemob3_hit_img, linemob3_img] * 3
linemob3_armored_img = pygame.image.load(path.join(char_dir, "linemob3_armored.png")).convert()
linemob3_armored_hit_img = pygame.image.load(path.join(char_dir, "linemob3_armored_hit.png")).convert()
linemob3_armored_hit_anim = [linemob3_armored_hit_img, linemob3_armored_img] * 3

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
for i in range(ShellMob1.SHELL_TYPE_CNT):
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
for i in range(ShellMob2.SHELL_TYPE_CNT):
    shell_img = pygame.image.load(path.join(char_dir, "shellmob2_shell{}.png".format(i + 1))).convert()
    shell_img.set_colorkey(WHITE1)
    shell_hit_img = pygame.image.load(path.join(char_dir, "shellmob2_shell{}_hit.png".format(i + 1))).convert()
    shell_hit_img.set_colorkey(WHITE1)
    shell_hit_anim = [shell_hit_img, shell_img] * 3
    shellmob2_shell_img.append(shell_hit_anim)

barricademob1_charge0_img = pygame.image.load(path.join(char_dir, "barricademob1_charge0.png")).convert()
barricademob1_charge0_img.set_colorkey(WHITE1)
barricademob1_charge0_hit_img = pygame.image.load(path.join(char_dir, "barricademob1_charge0_hit.png")).convert()
barricademob1_charge0_hit_img.set_colorkey(WHITE1)
barricademob1_charge0_hit_anim = [barricademob1_charge0_hit_img, barricademob1_charge0_img] * 3
barricademob1_charge1_img = pygame.image.load(path.join(char_dir, "barricademob1_charge1.png")).convert()
barricademob1_charge1_img.set_colorkey(WHITE1)
barricademob1_charge1_hit_img = pygame.image.load(path.join(char_dir, "barricademob1_charge1_hit.png")).convert()
barricademob1_charge1_hit_img.set_colorkey(WHITE1)
barricademob1_charge1_hit_anim = [barricademob1_charge1_hit_img, barricademob1_charge1_img] * 3
barricademob1_charge2_img = pygame.image.load(path.join(char_dir, "barricademob1_charge2.png")).convert()
barricademob1_charge2_img.set_colorkey(WHITE1)
barricademob1_charge2_hit_img = pygame.image.load(path.join(char_dir, "barricademob1_charge2_hit.png")).convert()
barricademob1_charge2_hit_img.set_colorkey(WHITE1)
barricademob1_charge2_hit_anim = [barricademob1_charge2_hit_img, barricademob1_charge2_img] * 3
barricademob1_charge3_img = pygame.image.load(path.join(char_dir, "barricademob1_charge3.png")).convert()
barricademob1_charge3_img.set_colorkey(WHITE1)
barricademob1_charge3_hit_img = pygame.image.load(path.join(char_dir, "barricademob1_charge3_hit.png")).convert()
barricademob1_charge3_hit_img.set_colorkey(WHITE1)
barricademob1_charge3_hit_anim = [barricademob1_charge3_hit_img, barricademob1_charge3_img] * 3
barricademob1_charge4_img = pygame.image.load(path.join(char_dir, "barricademob1_charge4.png")).convert()
barricademob1_charge4_img.set_colorkey(WHITE1)
barricademob1_charge4_hit_img = pygame.image.load(path.join(char_dir, "barricademob1_charge4_hit.png")).convert()
barricademob1_charge4_hit_img.set_colorkey(WHITE1)
barricademob1_charge4_hit_anim = [barricademob1_charge4_hit_img, barricademob1_charge4_img] * 3
barricade_horizontal_img = pygame.image.load(path.join(char_dir, "barricade_horizontal.png")).convert()
barricade_vertical_img = pygame.image.load(path.join(char_dir, "barricade_vertical.png")).convert()

orbitmob1_mothership_img = pygame.image.load(path.join(char_dir, "orbitmob1_mothership.png")).convert()
orbitmob1_mothership_hit_img = pygame.image.load(path.join(char_dir, "orbitmob1_mothership_hit.png")).convert()
orbitmob1_mothership_hit_anim = [orbitmob1_mothership_hit_img, orbitmob1_mothership_img] * 3
orbitmob1_orbiter_img = pygame.image.load(path.join(char_dir, "orbitmob1_orbiter.png")).convert()
orbitmob1_orbiter_hit_img = pygame.image.load(path.join(char_dir, "orbitmob1_orbiter_hit.png")).convert()
orbitmob1_orbiter_hit_anim = [orbitmob1_orbiter_hit_img, orbitmob1_orbiter_img] * 3
orbitmob2_mothership_img = pygame.image.load(path.join(char_dir, "orbitmob2_mothership.png")).convert()
orbitmob2_mothership_hit_img = pygame.image.load(path.join(char_dir, "orbitmob2_mothership_hit.png")).convert()
orbitmob2_mothership_hit_anim = [orbitmob2_mothership_hit_img, orbitmob2_mothership_img] * 3
orbitmob2_orbiter_img = pygame.image.load(path.join(char_dir, "orbitmob2_orbiter.png")).convert()
orbitmob2_orbiter_hit_img = pygame.image.load(path.join(char_dir, "orbitmob2_orbiter_hit.png")).convert()
orbitmob2_orbiter_hit_anim = [orbitmob2_orbiter_hit_img, orbitmob2_orbiter_img] * 3
orbitmob3_mothership_img = pygame.image.load(path.join(char_dir, "orbitmob3_mothership.png")).convert()
orbitmob3_mothership_hit_img = pygame.image.load(path.join(char_dir, "orbitmob3_mothership_hit.png")).convert()
orbitmob3_mothership_hit_anim = [orbitmob3_mothership_hit_img, orbitmob3_mothership_img] * 3
orbitmob3_orbiter_img = pygame.image.load(path.join(char_dir, "orbitmob3_orbiter.png")).convert()
orbitmob3_orbiter_hit_img = pygame.image.load(path.join(char_dir, "orbitmob3_orbiter_hit.png")).convert()
orbitmob3_orbiter_hit_anim = [orbitmob3_orbiter_hit_img, orbitmob3_orbiter_img] * 3

blockmob_img = pygame.image.load(path.join(char_dir, "blockmob.png")).convert()
blockmob_hit_img = pygame.image.load(path.join(char_dir, "blockmob_hit.png")).convert()
blockmob_hit_anim = [blockmob_hit_img, blockmob_img] * 3

ghostmob_img = pygame.image.load(path.join(char_dir, "ghostmob.png")).convert()
ghostmob_hit_img = pygame.image.load(path.join(char_dir, "ghostmob_hit.png")).convert()
ghostmob_hit_anim = [ghostmob_hit_img, ghostmob_img] * 3

nodemob1_img = pygame.image.load(path.join(char_dir, "nodemob1.png")).convert()
nodemob1_img.set_colorkey(WHITE1)
nodemob1_hit_img = pygame.image.load(path.join(char_dir, "nodemob1_hit.png")).convert()
nodemob1_hit_img.set_colorkey(WHITE1)
nodemob1_hit_anim = [nodemob1_hit_img, nodemob1_img] * 3
swellermob1_img = pygame.image.load(path.join(char_dir, "swellermob1.png")).convert()
swellermob1_hit_img = pygame.image.load(path.join(char_dir, "swellermob1_hit.png")).convert()
swellermob1_hit_anim = [swellermob1_hit_img, swellermob1_img] * 3

minebomb_off_img = pygame.image.load(path.join(char_dir, "minebomb_off.png")).convert()
minebomb_off_img.set_colorkey(WHITE1)
minebomb_off_hit_img = pygame.image.load(path.join(char_dir, "minebomb_off_hit.png")).convert()
minebomb_off_hit_img.set_colorkey(WHITE1)
minebomb_off_hit_anim = [minebomb_off_hit_img, minebomb_off_img] * 3
minebomb_on_img = pygame.image.load(path.join(char_dir, "minebomb_on.png")).convert()
minebomb_on_img.set_colorkey(WHITE1)
minebomb_on_hit_img = pygame.image.load(path.join(char_dir, "minebomb_on_hit.png")).convert()
minebomb_on_hit_img.set_colorkey(WHITE1)
minebomb_on_hit_anim = [minebomb_on_hit_img, minebomb_on_img] * 3

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
for i in range(BossLV4.SHELL_TYPE_CNT):
    shell_img = pygame.image.load(path.join(char_dir, "boss_lv4_shell{}.png".format(i + 1))).convert()
    shell_img.set_colorkey(WHITE1)
    shell_hit_img = pygame.image.load(path.join(char_dir, "boss_lv4_shell{}_hit.png".format(i + 1))).convert()
    shell_hit_img.set_colorkey(WHITE1)
    shell_hit_anim = [shell_hit_img, shell_img] * 3
    boss_lv4_shell_img.append(shell_hit_anim)
boss_lv4child_img = pygame.image.load(path.join(char_dir, "boss_lv4child.png")).convert()
boss_lv4child_hit_img = pygame.image.load(path.join(char_dir, "boss_lv4child_hit.png")).convert()
boss_lv4child_hit_anim = [boss_lv4child_hit_img, boss_lv4child_img] * 3
boss_lv5_phase1_img = pygame.image.load(path.join(char_dir, "boss_lv5_phase1.png")).convert()
boss_lv5_phase1_hit_img = pygame.image.load(path.join(char_dir, "boss_lv5_phase1_hit.png")).convert()
boss_lv5_phase1_hit_anim = [boss_lv5_phase1_hit_img, boss_lv5_phase1_img] * 3
boss_lv5_phase2_img = pygame.image.load(path.join(char_dir, "boss_lv5_phase2.png")).convert()
boss_lv5_phase2_hit_img = pygame.image.load(path.join(char_dir, "boss_lv5_phase2_hit.png")).convert()
boss_lv5_phase2_hit_anim = [boss_lv5_phase2_hit_img, boss_lv5_phase2_img] * 3
boss_lv5_orbiter_img = pygame.image.load(path.join(char_dir, "boss_lv5_orbiter.png")).convert()
boss_lv5_orbiter_hit_img = pygame.image.load(path.join(char_dir, "boss_lv5_orbiter_hit.png")).convert()
boss_lv5_orbiter_hit_anim = [boss_lv5_orbiter_hit_img, boss_lv5_orbiter_img] * 3

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
cannonball3_img_0 = pygame.image.load(path.join(bullet_dir, "cannonball3_0.png")).convert()
cannonball3_img_0.set_colorkey(WHITE1)
cannonball3_img_1 = pygame.image.load(path.join(bullet_dir, "cannonball3_1.png")).convert()
cannonball3_img_1.set_colorkey(WHITE1)
cannonball3_anim = [cannonball3_img_0, cannonball3_img_1]

spawneffect_anim = []
for i in range(SpawnEffect.ANIMATION_FRAME_CNT):
    filename = "spawneffect_{}.png".format(i)
    filepath = path.join(spawn_dir, filename)
    spawn_img = pygame.image.load(filepath).convert()
    spawn_img.set_colorkey(BLACK)
    spawneffect_anim.append(spawn_img)

hiteffect_anim = []
for i in range(HitEffect.ANIMATION_FRAME_CNT):
    filename = "hit_{:0>4}.png".format(i)
    filepath = path.join(hit_dir, filename)
    hit_img = pygame.image.load(filepath).convert_alpha()
    hit_img.set_colorkey(BLACK)
    hiteffect_anim.append(hit_img)

explosion_anim = dict()
for j in range(1, EXPLOSION_TYPES + 1):
    explosion_anim[str(j)] = []
    for i in range(Explosion.MAX_ANIMATION_FRAME_CNT):
        filename = "expl_{0:0>2}_{1:0>4}.png".format(j, i)
        filepath = path.join(expl_dir, filename)
        if path.isfile(filepath):
            expl_img = pygame.image.load(filepath).convert_alpha()
            expl_img.set_colorkey(BLACK)
            explosion_anim[str(j)].append(expl_img)

debriz_img = []
for i in range(Debris.TYPE_CNT):
    filename = "debris_{}.png".format(i)
    filepath = path.join(expl_dir, filename)
    debris_img = pygame.image.load(filepath).convert()
    debris_img.set_colorkey(WHITE1)
    debriz_img.append(debris_img)

# define sprite groups
all_buttons = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
pointers = pygame.sprite.Group()
target_pointer = TargetPointer()
pointers.add(target_pointer)
mobs = pygame.sprite.Group()
all_mobs = pygame.sprite.Group()    # including shield units
child_mobs = pygame.sprite.Group()  # for childmobs
barricades = pygame.sprite.Group()
minebombs = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
player_cannon_balls = pygame.sprite.Group()
mob_bullets = pygame.sprite.Group()
mob_cannon_balls = pygame.sprite.Group()
mob_lasers = []
spawns = pygame.sprite.Group()
explosions = pygame.sprite.Group()
shockwaves = pygame.sprite.Group()
debriz = pygame.sprite.Group()
items = pygame.sprite.Group()

# define score and playtime
score = 0                           # overall score
start_score = 0
play_start_time = 0
playtime = 0                        # overall gameplay time
avg_score = 0                       # overall score earned per second

level = 1

max_mobs = 300  # max number of mobs on the field (except shield units)

# variables for breaktime between two stages
break_start = 0
breaktime = 20
now_break = False

player = Player()
players.add(player)
all_sprites.add(player)
all_sprites.add(target_pointer)

# variables and functions for shifting entire field
# shifts only vertically
field_shift_pos = 0     # for vibrating or shaking entire field
field_shift_magnitude = 1
field_shift_length = 0
field_vibrate_start = False
field_vibrate_max_framenum = 0
field_vibrate_framenum = 0
field_vibrate = False
field_shake_start = False
field_shake_magnitude_attenuation_ratio = 1
field_shake = False


# parameter "vibration_length" must be in secs
def vibrate_field(magnitude, vibration_length):
    global field_shift_pos, field_vibrate_start, field_vibrate_max_framenum, field_vibrate_framenum, field_vibrate

    if field_vibrate_start:
        field_vibrate = True
        field_vibrate_start = False
        field_shift_pos = magnitude
        field_vibrate_max_framenum = round(vibration_length * fps)

    field_shift_pos = -field_shift_pos
    field_vibrate_framenum += 1
    if field_vibrate_framenum >= field_vibrate_max_framenum:
        field_vibrate_framenum = 0
        field_shift_pos = 0
        field_vibrate = False


# parameter "shaking_length" must be in secs
def shake_field(magnitude, shaking_length):
    global field_shift_pos, field_shake_start, field_shake_magnitude_attenuation_ratio, field_shake

    if field_shake_start:
        field_shake = True
        field_shake_start = False
        field_shift_pos = magnitude

        frames = round(shaking_length * fps)
        field_shake_magnitude_attenuation_ratio = (1 / magnitude) ** (1 / frames)

    field_shift_pos *= -field_shake_magnitude_attenuation_ratio
    if abs(field_shift_pos) < 1:
        field_shift_pos = 0
        field_shake = False


def add_single_mob(mobtype):
    """ function for adding new mob """
    all_sprites.add(mobtype)
    mobs.add(mobtype)


def initialize_all_progress():
    global score, playtime, avg_score, start_score, play_start_time, \
        max_hp_upgrade_count, max_mp_upgrade_count, \
        pick_range_upgrade_count, main_weapon_upgrade_count, charging_cannon_power_upgrade_count

    score = 0
    start_score = score
    play_start_time = time.time()
    playtime = 0
    avg_score = 0

    max_hp_upgrade_count = 0
    max_mp_upgrade_count = 0
    pick_range_upgrade_count = 0
    main_weapon_upgrade_count = 0
    charging_cannon_power_upgrade_count = 0

    player.hp_lvl = 1
    player.mp_lvl = 1
    player.pick_range_lvl = 1
    player.main_weapon_lvl = 1
    player.charging_cannon_lvl = 1

    player.hp_full = player.hp_list[player.hp_lvl - 1]
    player.mp_full = player.mp_list[player.mp_lvl - 1]
    player.pick_range = player.pick_range_list[player.pick_range_lvl - 1]
    player.max_cannon_power = player.charging_cannon_power_list[player.charging_cannon_lvl - 1]
    player.cannon_charge_rate = player.max_cannon_power / 40
    player.max_shock_range = 27 * math.sqrt(player.max_cannon_power)

    for pl in players:
        if pl != player:
            pl.kill()
    for mb in all_mobs:
        mb.kill()
    for sp in spawns:
        sp.kill()
    for child in child_mobs:
        child.kill()
    for ba in barricades:
        ba.kill()
    mob_lasers.clear()
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


# for main menu screen
mainmenu_show = True
start_button = Button([450, 600, 300, 100], WHITE1, "START", 60)
stage_select_menu_show = False

# for play screen
play = False

# for paused window
pause_ready = False
pause = False
paused_time = 0
paused_length = 0
total_paused_length = 0
paused_window_show = False
quit_button = Button([screen_width - 450, screen_height // 2 - 35, 200, 70], WHITE1, "QUIT GAME", 20)

# for upgrade window
now_upgrading = False
upgrade_window_show = False
stat_points_per_level = 4
max_upgrade_count = 2

max_hp_upgrade_button = Button([530, 230, 20, 20], WHITE1, "+", 15)
max_hp_degrade_button = Button([550, 230, 20, 20], WHITE1, "-", 15, BLACK, False)
max_hp_upgrade_count = 0

max_mp_upgrade_button = Button([530, 280, 20, 20], WHITE1, "+", 15)
max_mp_degrade_button = Button([550, 280, 20, 20], WHITE1, "-", 15, BLACK, False)
max_mp_upgrade_count = 0

pick_range_upgrade_button = Button([530, 330, 20, 20], WHITE1, "+", 15)
pick_range_degrade_button = Button([550, 330, 20, 20], WHITE1, "-", 15, BLACK, False)
pick_range_upgrade_count = 0

main_weapon_upgrade_button = Button([1030, 230, 20, 20], WHITE1, "+", 15)
main_weapon_degrade_button = Button([1050, 230, 20, 20], WHITE1, "-", 15, BLACK, False)
main_weapon_upgrade_count = 0

charging_cannon_power_upgrade_button = Button([1030, 280, 20, 20], WHITE1, "+", 15)
charging_cannon_power_degrade_button = Button([1050, 280, 20, 20], WHITE1, "-", 15, BLACK, False)
charging_cannon_power_upgrade_count = 0

all_upgrade_buttons = [max_hp_upgrade_button, max_mp_upgrade_button, pick_range_upgrade_button, main_weapon_upgrade_button, charging_cannon_power_upgrade_button]
all_degrade_buttons = [max_hp_degrade_button, max_mp_degrade_button, pick_range_degrade_button, main_weapon_degrade_button, charging_cannon_power_degrade_button]

done_button = Button([880, 650, 220, 50], WHITE1, "APPLY & CONTINUE", 20)

# for gameover screen
gameover_show = False
restart_button = Button([450, 600, 300, 100], WHITE1, "RESTART", 60)

# define level and phases
level1 = Level(1, [screen_width // 2 - 150, 200, 300, 70], BossLV1, Phase([MoveLineMob1, MoveLineMob3, MoveLineMob3], [150, 70, 30]))
level2 = Level(2, [screen_width // 2 - 150, 280, 300, 70], BossLV2, Phase([WallMobUnit3], [500]))
level3 = Level(3, [screen_width // 2 - 150, 360, 300, 70], BossLV3, Phase([MoveLineMob2, MinigunMob3], [200, 25]))
level4 = Level(4, [screen_width // 2 - 150, 440, 300, 70], BossLV4, Phase([MinigunMob3, ShellMob1, ShellMob2], [8, 8, 8]))
level5 = Level(5, [screen_width // 2 - 150, 520, 300, 70], BossLV5)
test_level = Level(6, [screen_width // 2 - 150, 600, 300, 70], BossLV5)

all_levels = [level1, level2, level3, level4, level5, test_level]
current_level = all_levels[0]

level1.add_phase([MoveLineMob1], [150], 200)
level1.add_phase([MoveLineMob1, MoveLineMob2], [120, 55], 600)
level1.add_phase([MoveLineMob1, MoveLineMob3, MoveLineMob3], [150, 70, 30], 1600)

level2.add_phase([FollowerMob1, WallMobUnit1], [3, 600], 2000)
level2.add_phase([FollowerMob1, WallMobUnit1, WallMobUnit2], [3, 400, 400], 5000)
level2.add_phase([FollowerMob1, WallMobUnit1, WallMobUnit2, WallMobUnit3], [3, 300, 200, 100], 9000)

level3.add_phase([MoveLineMob2, MinigunMob1], [60, 30], 4000)
level3.add_phase([MoveLineMob1, MinigunMob1, MinigunMob2], [120, 30, 20], 10000)
level3.add_phase([MoveLineMob1, MinigunMob1, MinigunMob2, MinigunMob3], [120, 25, 17, 13], 18000, True)

level4.add_phase([MoveLineMob3, FollowerMob2], [77, 5], 10000, True)
level4.add_phase([MoveLineMob2, FollowerMob2, MinigunMob1, ShellMob1], [70, 3, 30, 18], 20000, True)
level4.add_phase([MinigunMob3, FollowerMob2, ShellMob1, ShellMob2], [12, 3, 20, 15], 35000, True)

level5.add_phase([OrbitMob1, MinigunMob2], [25, 40], 10000, True)
level5.add_phase([OrbitMob1, OrbitMob2, MinigunMob1], [18, 13, 60], 25000, True)
level5.add_phase([OrbitMob1, OrbitMob2, OrbitMob3, MinigunMob3], [15, 10, 3, 15], 40000, True)

#test_level.add_phase([BarricadeMob1], [30], 1000000000, True)
test_level.add_phase([BlockMob], [60], 5000, True)
test_level.add_phase([GhostMob], [120], 10000, True)
test_level.add_phase([NodeMob1], [40], 15000, True)
test_level.add_phase([SwellerMob1], [45], 20000, True)
test_level.add_phase([BarricadeMob1], [30], 1000000000, True)
"""
test_level.add_phase([OrbitMob1], [30], 100, True)
"""
stage_select_buttons = []
for i in range(len(all_levels)):
    stage_select_buttons.append(all_levels[i].start_button)
    all_buttons.add(all_levels[i].start_button)
all_buttons.add(start_button)
all_buttons.add(restart_button)
all_buttons.add(quit_button)

# MAIN GAME LOOP#

while not done:
    # update screen at a specified frame rate
    clock.tick(fps)

    # hide previous frame by filling the entire screen with black
    screen.fill(BLACK)

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
        draw_text(screen, "WAR OF SQUARES", 50, WHITE1, "midtop", screen_width // 2, 50)
        start_button.update()

        # initialize player status according to selected level
        if start_button.operate:
            mainmenu_show = False
            stage_select_menu_show = True
            start_button.operate = False

    elif stage_select_menu_show:
        draw_text(screen, "SELECT LEVEL", 50, WHITE1, "midtop", screen_width // 2, 50)
        for button in stage_select_buttons:
            button.update()

        # initialize player status according to selected level
        if any([button.operate for button in stage_select_buttons]):
            score = 0
            if stage_select_buttons[0].operate:
                level = 1
                player.stat_points = 0 * stat_points_per_level
                max_upgrade_count = 1
                stage_select_buttons[0].operate = False
            elif stage_select_buttons[1].operate:
                level = 2
                player.stat_points = 1 * stat_points_per_level
                max_upgrade_count = 1
                stage_select_buttons[1].operate = False
            elif stage_select_buttons[2].operate:
                level = 3
                player.stat_points = 2 * stat_points_per_level
                max_upgrade_count = 2
                stage_select_buttons[2].operate = False
            elif stage_select_buttons[3].operate:
                level = 4
                player.stat_points = 3 * stat_points_per_level
                max_upgrade_count = 3
                stage_select_buttons[3].operate = False
            elif stage_select_buttons[4].operate:
                level = 5
                player.stat_points = 4 * stat_points_per_level
                max_upgrade_count = 4
                stage_select_buttons[4].operate = False
            elif stage_select_buttons[5].operate:
                level = 6
                player.stat_points = 5 * stat_points_per_level
                max_upgrade_count = 5
                stage_select_buttons[5].operate = False

            current_level = all_levels[level - 1]
            current_level.initialize_level()
            current_level.start_from_this_level = True
            initialize_all_progress()
            total_paused_length = 0
            player.hp = 100
            player.hp_full = 100
            player.mp = 100
            player.mp_full = 100
            player.rect.center = (screen_width // 2, screen_height // 2)
            screen_center = [0, 0]
            stage_select_menu_show = False
            play = True

    elif play:
        """ update level and all sprites per frame when not paused """
        if not pause and not now_upgrading:
            paused_window_show = False
            upgrade_window_show = False

            """ field shift(vibration or shaking) control """
            if (field_vibrate_start or field_vibrate) and not field_shake:
                vibrate_field(field_shift_magnitude, field_shift_length)

            if field_shake_start or field_shake:
                shake_field(field_shift_magnitude, field_shift_length)
                if field_vibrate:
                    field_vibrate = False

            """ update current level """
            current_level.update()
            if current_level.quit:
                level += 1
                player.stat_points += 4
                current_level = all_levels[level - 1]
                current_level.initialize_level()

            """ update all sprites """
            all_sprites.update()

            playtime = time.time() - play_start_time - total_paused_length + NONZERO
            avg_score = score / playtime

            current_stage_score = score - start_score
            current_stage_playtime = time.time() - current_level.start_time + NONZERO - total_paused_length
            current_stage_avg_score = current_stage_score / current_stage_playtime
        elif pause:
            paused_length = time.time() - paused_time
            paused_window_show = True
        elif now_upgrading:
            upgrade_window_show = True


        """ dealing with all collision events """
        # collision between player's bullets and all mobs
        hits = pygame.sprite.groupcollide(all_mobs, player_bullets, False, True)
        for hit in hits:
            hit.hit = True
            for b in hits[hit]:
                hiteff = HitEffect(b.rect.center, (round(b.rect.width * BULLET_HITEFFECT_SIZE_RATIO), round(b.rect.height * BULLET_HITEFFECT_SIZE_RATIO)))
                all_sprites.add(hiteff)
                players.add(hiteff)
                hit.hp -= b.power * random.uniform(0.5, 1.5)

        # collision between player's cannonball and all mobs
        hits = pygame.sprite.groupcollide(all_mobs, player_cannon_balls, False, True, pygame.sprite.collide_circle)
        for hit in hits:
            hit.hit = True
            for b in hits[hit]:
                b.shock_range = player.max_shock_range * (b.power / b.max_power)

                if b.power / b.max_power > 0.8:
                    field_shift_magnitude = 10
                    field_shift_length = 1
                    field_shake_start = True

                explosion_type = random.randrange(1, EXPLOSION_TYPES + 1)
                Explosion(b.rect.center, explosion_type, (round(b.size[0] * 4), round(b.size[1] * 4)))
                for exps in range(random.randrange(4, 7)):
                    exp_dist = random.uniform(60, b.shock_range * 0.8)
                    exp_angle = random.uniform(-math.pi, math.pi)
                    explosion_xpos = round(exp_dist * math.cos(exp_angle))
                    explosion_ypos = round(exp_dist * math.sin(exp_angle))
                    explosion_type = random.randrange(1, 12)
                    Explosion([b.rect.centerx + explosion_xpos, b.rect.centery + explosion_ypos], explosion_type, (round(b.size[0] * 4), round(b.size[1] * 4)))
                hit.hp -= b.power * random.uniform(0.8, 1.2)
                if not b.released:
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

        # collision between player's bullets and barricades
        hits = pygame.sprite.groupcollide(barricades, player_bullets, False, True)
        for hit in hits:
            hit.hit = True
            for b in hits[hit]:
                hiteff = HitEffect(b.rect.center, (round(b.rect.width * BULLET_HITEFFECT_SIZE_RATIO), round(b.rect.height * BULLET_HITEFFECT_SIZE_RATIO)))
                all_sprites.add(hiteff)
                players.add(hiteff)
                hit.hp -= b.power * random.uniform(0.5, 1.5)

        # collision between player's cannonball and barricades
        hits = pygame.sprite.groupcollide(barricades, player_cannon_balls, False, True, pygame.sprite.collide_circle)
        for hit in hits:
            hit.hit = True
            for b in hits[hit]:
                explosion_type = random.randrange(1, EXPLOSION_TYPES + 1)
                Explosion(b.rect.center, explosion_type, (round(b.size[0] * 4), round(b.size[1] * 4)))
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
            hiteff = HitEffect(hit.rect.center, (round(hit.rect.width * BULLET_HITEFFECT_SIZE_RATIO), round(hit.rect.height * BULLET_HITEFFECT_SIZE_RATIO)))
            all_sprites.add(hiteff)
            players.add(hiteff)
            player.hp -= hit.power

        # collision between player and mob cannonballs
        hits = pygame.sprite.spritecollide(player, mob_cannon_balls, True, pygame.sprite.collide_circle)
        for hit in hits:
            explosion_type = random.randrange(1, EXPLOSION_TYPES + 1)
            Explosion(hit.rect.center, explosion_type, (round(hit.size[0] * 5), round(hit.size[1] * 5)))
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

        # collision between player and barricades
        hits = pygame.sprite.spritecollide(player, barricades, False)
        for hit in hits:
            if not hit.dead:
                if hit.damage < player.hp:
                    hit.prev_dead = True
                    hit.next_dead = True
                    hit.death_count = 0
                hit.no_points = True
                player.hp -= hit.damage

        # collision between player and lasers
        curr_pos = player.rect.center
        laser_hit = False
        for la in mob_lasers:
            if is_aligned(la.nodes[0].rect.center, curr_pos, la.nodes[1].rect.center, la.range):
                player.hp -= la.power
                laser_hit = True
        if laser_hit:
            player_x = player.rect.x
            player_y = player.rect.y
            hiteff = HitEffect((random.randrange(player_x, player_x + player.rect.width), random.randrange(player_y, player_y + player.rect.height)), (32, 32))
            all_sprites.add(hiteff)
            players.add(hiteff)

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
        if not now_upgrading:
            p_pressed = pygame.key.get_pressed()[pygame.K_p]
            if p_pressed:
                pause_ready = True
            if pause_ready:
                if not p_pressed:
                    paused_time = time.time()
                    total_paused_length += paused_length
                    paused_length = 0
                    pause_ready = False
                    pause = not pause


        """ draw all objects on screen """
        # draw background gridline
        for i in range(-round((SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width), round((SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width), 200):
            pygame.draw.line(screen, WHITE3,
                             [i - screen_center[0], -round((SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height) - screen_center[1]],
                             [i - screen_center[0], round((SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height) - screen_center[1]], 2)
        for i in range(-round((SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_height), round((SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_height), 200):
            pygame.draw.line(screen, WHITE3,
                             [-round((SCREEN_FIELD_SIZE_RATIO / 2 - 0.5) * screen_width) - screen_center[0], i - screen_center[1] + round(field_shift_pos)],
                             [round((SCREEN_FIELD_SIZE_RATIO / 2 + 0.5) * screen_width) - screen_center[0], i - screen_center[1] + round(field_shift_pos)], 2)

        # draw all sprites
        debriz.draw(screen)
        items.draw(screen)
        minebombs.draw(screen)
        spawns.draw(screen)

        barricades.draw(screen)
        all_mobs.draw(screen)

        for lasers in mob_lasers:
            lasers.draw()
        player_bullets.draw(screen)
        mob_bullets.draw(screen)
        mob_cannon_balls.draw(screen)
        players.draw(screen)
        player_cannon_balls.draw(screen)
        for spr in all_mobs:
            if spr.hp_bar_show:
                draw_hp_bar(spr)
        explosions.draw(screen)
        pointers.draw(screen)

        # draw player hp bar on topleft of screen
        pygame.draw.rect(screen, BLACK, [20, 10, 200, 15], 0)
        pygame.draw.rect(screen, GREEN1, [20, 10, round(200 * (max(player.hp / player.hp_full, 0))), 15], 0)
        pygame.draw.rect(screen, WHITE1, [20, 10, 200, 15], 2)
        draw_text(screen, "{} / {}".format(round(player.hp), player.hp_full), 15, WHITE1, "topleft", 230, 10)
        draw_text(screen, "{} / {}".format(round(player.mp), player.mp_full), 15, WHITE1, "topleft", 230, 35)

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
        pygame.draw.rect(screen, BLACK, [screen_width // 2 - 100, 10, 200, 15], 0)
        if current_level.boss_challenging:
            pygame.draw.rect(screen, YELLOW1, [screen_width // 2 - 100, 10, 200, 15], 0)
        elif current_level.clear:
            pygame.draw.rect(screen, YELLOW1, [screen_width // 2 - 100, 10, round(200 * (breaktime - time.time() + current_level.break_start_time) / breaktime), 15], 0)
        else:
            current_phase = current_level.phase_bound[current_level.phase_num]
            next_phase = current_level.phase_bound[current_level.phase_num + 1]
            pygame.draw.rect(screen, YELLOW1, [screen_width // 2 - 100, 10, round(200 * (
                        (min(score - current_phase, next_phase - current_phase)) / (
                            next_phase - current_phase))), 15], 0)
        pygame.draw.rect(screen, WHITE1, [screen_width // 2 - 100, 10, 200, 15], 2)

        # draw score, playtime and phase text
        draw_text(screen, current_level.phase_text, 20, WHITE1, "midtop", screen_width // 2, 30)
        draw_text(screen, "TOTAL SCORE : {}".format(round(score, 2)), 15, WHITE1, "topleft", 20, 65)
        draw_text(screen, "STAGE SCORE : {}".format(round(current_level.score, 2)), 15, WHITE1, "topleft", 20, 85)
        draw_text(screen, "PLAYTIME : {} seconds".format(round(playtime, 2)), 15, WHITE1, "topleft", 900, 10)
        draw_text(screen, "TOTAL T.A. SCORE : {}".format(round(avg_score, 4)), 15, WHITE1, "topleft", 900, 30)
        draw_text(screen, "STAGE T.A. SCORE : {}".format(round(current_level.avg_score, 4)), 15, WHITE1, "topleft", 900, 50)

        # draw paused window when paused
        if paused_window_show:
            pygame.draw.rect(screen, BLACK, [200, 300, 800, 200], 0)
            pygame.draw.rect(screen, WHITE1, [200, 300, 800, 200], 4)
            draw_text(screen, "PAUSED", 50, WHITE1, "midtop", 600, 330)
            draw_text(screen, "Press 'P' to continue", 20, WHITE1, "midtop", 600, 430)

            quit_button.update()
            if quit_button.operate:
                player.hp = 0
                play = False
                pause = False
                gameover_show = True
                paused_window_show = False
                quit_button.operate = False

        # draw upgrade window before starting a level
        if upgrade_window_show:
            pygame.draw.rect(screen, BLACK, [100, 100, 1000, 600], 0)
            pygame.draw.rect(screen, WHITE1, [100, 100, 1000, 600], 4)
            draw_text(screen, "UPGRADES", 50, WHITE1, "midtop", 600, 120)
            draw_text(screen, "CURRENT LEVEL : {}".format(level), 20, WHITE1, "midtop", 600, 180)
            draw_text(screen, "CURRENT STATS : {}".format(player.stat_points), 20, WHITE1, "topright", 1070, 180)

            # max player HP upgrade text
            draw_text(screen, "MAX HP", 20, WHITE1, "topleft", 130, 230)
            draw_text(screen, "Current : {}".format(player.hp_lvl), 20, WHITE1, "topleft", 130, 250)

            # max player MP upgrade text
            draw_text(screen, "MAX MP", 20, WHITE1, "topleft", 130, 280)
            draw_text(screen, "Current : {}".format(player.mp_lvl), 20, WHITE1, "topleft", 130, 300)

            # Pickup Range upgrade text
            draw_text(screen, "PICKUP RANGE", 20, WHITE1, "topleft", 130, 330)
            draw_text(screen, "Current : {}".format(player.pick_range_lvl), 20, WHITE1, "topleft", 130, 350)

            # Main Weapon Lv upgrade text
            draw_text(screen, "MAIN WEAPON LEVEL", 20, WHITE1, "topleft", 630, 230)
            draw_text(screen, "Current : {}".format(player.main_weapon_lvl), 20, WHITE1, "topleft", 630, 250)

            # Charging Cannon Lv upgrade text
            draw_text(screen, "CHARGING CANNON LEVEL", 20, WHITE1, "topleft", 630, 280)
            draw_text(screen, "Current : {}".format(player.charging_cannon_lvl), 20, WHITE1, "topleft", 630, 300)

            for button in all_upgrade_buttons:
                button.update()
            for button in all_degrade_buttons:
                button.update()
            done_button.update()

            # upgrade max hp
            if max_hp_upgrade_button.operate:
                player.hp_lvl += 1
                max_hp_upgrade_count += 1
                player.stat_points -= 1
                max_hp_upgrade_button.operate = False

            if max_hp_degrade_button.operate:
                player.hp_lvl -= 1
                max_hp_upgrade_count -= 1
                player.stat_points += 1
                max_hp_degrade_button.operate = False

            if max_hp_upgrade_count >= max_upgrade_count or player.stat_points <= 0:
                max_hp_upgrade_button.deactivate()
            else:
                max_hp_upgrade_button.activate()

            if max_hp_upgrade_count <= 0:
                max_hp_degrade_button.deactivate()
            else:
                max_hp_degrade_button.activate()

            # upgrade max mp
            if max_mp_upgrade_button.operate:
                player.mp_lvl += 1
                max_mp_upgrade_count += 1
                player.stat_points -= 1
                max_mp_upgrade_button.operate = False

            if max_mp_degrade_button.operate:
                player.mp_lvl -= 1
                max_mp_upgrade_count -= 1
                player.stat_points += 1
                max_mp_degrade_button.operate = False

            if max_mp_upgrade_count >= max_upgrade_count or player.stat_points <= 0:
                max_mp_upgrade_button.deactivate()
            else:
                max_mp_upgrade_button.activate()

            if max_mp_upgrade_count <= 0:
                max_mp_degrade_button.deactivate()
            else:
                max_mp_degrade_button.activate()

            # upgrade pickup range
            if pick_range_upgrade_button.operate:
                player.pick_range_lvl += 1
                pick_range_upgrade_count += 1
                player.stat_points -= 1
                pick_range_upgrade_button.operate = False

            if pick_range_degrade_button.operate:
                player.pick_range_lvl -= 1
                pick_range_upgrade_count -= 1
                player.stat_points += 1
                pick_range_degrade_button.operate = False

            if pick_range_upgrade_count >= max_upgrade_count or player.stat_points <= 0:
                pick_range_upgrade_button.deactivate()
            else:
                pick_range_upgrade_button.activate()

            if pick_range_upgrade_count <= 0:
                pick_range_degrade_button.deactivate()
            else:
                pick_range_degrade_button.activate()

            # upgrade main weapon
            if main_weapon_upgrade_button.operate:
                player.main_weapon_lvl += 1
                main_weapon_upgrade_count += 1
                player.stat_points -= 1
                main_weapon_upgrade_button.operate = False

            if main_weapon_degrade_button.operate:
                player.main_weapon_lvl -= 1
                main_weapon_upgrade_count -= 1
                player.stat_points += 1
                main_weapon_degrade_button.operate = False

            if main_weapon_upgrade_count >= max_upgrade_count or player.stat_points <= 0:
                main_weapon_upgrade_button.deactivate()
            else:
                main_weapon_upgrade_button.activate()

            if main_weapon_upgrade_count <= 0:
                main_weapon_degrade_button.deactivate()
            else:
                main_weapon_degrade_button.activate()

            # upgrade charging cannon
            if charging_cannon_power_upgrade_button.operate:
                player.charging_cannon_lvl += 1
                charging_cannon_power_upgrade_count += 1
                player.stat_points -= 1
                charging_cannon_power_upgrade_button.operate = False

            if charging_cannon_power_degrade_button.operate:
                player.charging_cannon_lvl -= 1
                charging_cannon_power_upgrade_count -= 1
                player.stat_points += 1
                charging_cannon_power_degrade_button.operate = False

            if charging_cannon_power_upgrade_count >= max_upgrade_count or player.stat_points <= 0:
                charging_cannon_power_upgrade_button.deactivate()
            else:
                charging_cannon_power_upgrade_button.activate()

            if charging_cannon_power_upgrade_count <= 0:
                charging_cannon_power_degrade_button.deactivate()
            else:
                charging_cannon_power_degrade_button.activate()

            if done_button.operate:
                player.hp_full = player.hp_list[player.hp_lvl - 1]
                player.mp_full = player.mp_list[player.mp_lvl - 1]
                player.pick_range = player.pick_range_list[player.pick_range_lvl - 1]
                player.max_cannon_power = player.charging_cannon_power_list[player.charging_cannon_lvl - 1]
                player.cannon_charge_rate = player.max_cannon_power / 40
                player.max_shock_range = 27 * math.sqrt(player.max_cannon_power)

                if current_level.start_from_this_level:
                    player.hp = player.hp_full
                    player.mp = player.mp_full
                    current_level.start_from_this_level = False

                max_upgrade_count = 2
                max_hp_upgrade_count = 0
                max_mp_upgrade_count = 0
                pick_range_upgrade_count = 0
                main_weapon_upgrade_count = 0
                charging_cannon_power_upgrade_count = 0

                total_paused_length = time.time() - paused_time
                playtime -= total_paused_length
                upgrade_window_show = False
                now_upgrading = False
                done_button.operate = False

    # display gameover scene
    elif gameover_show:
        draw_text(screen, "GAME OVER", 50, WHITE1, "midtop", screen_width // 2, 50)
        draw_text(screen, "TOTAL RESULT", 25, WHITE1, "midtop", screen_width // 2, 150)

        draw_text(screen, "TOTAL SCORE", 20, WHITE1, "topleft", 300, 200)
        draw_text(screen, "TOTAL PLAYTIME", 20, WHITE1, "topleft", 300, 225)
        draw_text(screen, "TIME-AVERAGE TOTAL SCORE", 20, WHITE1, "topleft", 300, 250)
        draw_text(screen, "{} pts".format(round(score, 2)), 20, WHITE1, "topright", screen_width - 300, 200)
        draw_text(screen, "{} sec".format(round(playtime, 2)), 20, WHITE1, "topright", screen_width - 300, 225)
        draw_text(screen, "{} pts/sec".format(round(avg_score, 4)), 20, WHITE1, "topright", screen_width - 300, 250)

        draw_text(screen, "RESULT FOR EACH LEVEL", 25, WHITE1, "midtop", screen_width // 2, 300)

        draw_text(screen, "SCORE", 15, WHITE1, "topleft", 150, 380)
        draw_text(screen, "PLAYTIME", 15, WHITE1, "topleft", 150, 405)
        draw_text(screen, "TIME-AVERAGE SCORE", 15, WHITE1, "topleft", 150, 430)
        draw_text(screen, "PHASE SCORE", 15, WHITE1, "topleft", 150, 460)
        draw_text(screen, "PHASE PLAYTIME", 15, WHITE1, "topleft", 150, 485)
        draw_text(screen, "TIME-AVERAGE PHASE SCORE", 15, WHITE1, "topleft", 150, 510)
        draw_text(screen, "BOSS CHALLENGE PLAYTIME", 15, WHITE1, "topleft", 150, 540)

        draw_text(screen, "LEVEL 1", 20, WHITE1, "topleft", 400, 340)
        draw_text(screen, "LEVEL 2", 20, WHITE1, "topleft", 520, 340)
        draw_text(screen, "LEVEL 3", 20, WHITE1, "topleft", 640, 340)
        draw_text(screen, "LEVEL 4", 20, WHITE1, "topleft", 760, 340)
        draw_text(screen, "LEVEL 5", 20, WHITE1, "topleft", 880, 340)

        for lvl in range(5):
            text_xpos = 500 + 120 * lvl
            draw_text(screen, str(round(all_levels[lvl].score, 2)), 15, WHITE1, "topright", text_xpos, 380)
            draw_text(screen, str(round(all_levels[lvl].playtime, 2)), 15, WHITE1, "topright", text_xpos, 405)
            draw_text(screen, str(round(all_levels[lvl].avg_score, 4)), 15, WHITE1, "topright", text_xpos, 430)
            draw_text(screen, str(round(all_levels[lvl].mob_score, 2)), 15, WHITE1, "topright", text_xpos, 460)
            draw_text(screen, str(round(all_levels[lvl].mob_playtime, 2)), 15, WHITE1, "topright", text_xpos, 485)
            draw_text(screen, str(round(all_levels[lvl].mob_avg_score, 4)), 15, WHITE1, "topright", text_xpos, 510)
            draw_text(screen, str(round(all_levels[lvl].boss_playtime, 2)), 15, WHITE1, "topright", text_xpos, 540)

        draw_text(screen, "pts", 15, WHITE1, "topright", screen_width - 150, 380)
        draw_text(screen, "sec", 15, WHITE1, "topright", screen_width - 150, 405)
        draw_text(screen, "pts/sec", 15, WHITE1, "topright", screen_width - 150, 430)
        draw_text(screen, "pts", 15, WHITE1, "topright", screen_width - 150, 460)
        draw_text(screen, "sec", 15, WHITE1, "topright", screen_width - 150, 485)
        draw_text(screen, "pts/sec", 15, WHITE1, "topright", screen_width - 150, 510)
        draw_text(screen, "sec", 15, WHITE1, "topright", screen_width - 150, 540)

        restart_button.update()

        # clear the entire map and initialize all progress
        if restart_button.operate:
            initialize_all_progress()
            gameover_show = False
            mainmenu_show = True
            restart_button.operate = False
            restart_button.kill()

    # apply all drawings
    pygame.display.flip()

pygame.quit()
exit()
