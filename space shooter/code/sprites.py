from settings import *


class Sprite:
    def __init__(self, tex: Texture, pos, speed, direction):
        self.tex = tex
        self.source = Rectangle(0, 0, self.tex.width, self.tex.height)
        self.dest = Rectangle(pos.x, pos.y, self.source.width, self.source.height)
        self.rotation = 0

        self.speed = speed
        self.direction = direction

        self.discard: bool = False
        self.collision_radius = self.source.height / 2

    def move(self, delta_time):
        self.dest.x += self.direction.x * self.speed * delta_time
        self.dest.y += self.direction.y * self.speed * delta_time

    def check_discard(self):
        self.discard = not -300 < self.dest.y < get_screen_height() + 300

    def update(self, delta_time):
        self.check_discard()
        self.move(delta_time)

    def draw(self, debug: bool):
        draw_texture_pro(self.tex, self.source, self.dest, Vector2(self.source.width / 2, self.source.height / 2), self.rotation, WHITE)
        if debug:
            draw_circle_lines_v(Vector2(self.dest.x, self.dest.y), self.collision_radius, RED)


class Laser(Sprite):
    def __init__(self, tex: Texture, pos):
        super().__init__(tex, pos, LASER_SPEED, Vector2(0, -1))

    def draw(self, debug: bool):
        draw_texture_pro(self.tex, self.source, self.dest, Vector2(self.source.width / 2, self.source.height / 2), self.rotation, WHITE)
        collision_rect = Rectangle(self.dest.x - self.dest.width / 2, self.dest.y - self.dest.height / 2, self.dest.width, self.dest.height)
        if debug:
            draw_rectangle_lines_ex(collision_rect, 1, RED)


class Meteor(Sprite):
    def __init__(self, tex: Texture):
        pos = Vector2(randint(0, get_screen_width()), randint(-150, -50))
        speed = randint(*METEOR_SPEED_RANGE)
        direction = Vector2(uniform(-0.5, 0.5), 1)
        super().__init__(tex, pos, speed, direction)

    def update(self, delta_time):
        super().update(delta_time)
        self.rotation += 50 * delta_time


class ExplosionAnimation:
    def __init__(self, sprite_strip: Texture, pos, frame_size: Vector2):
        self.sprite_strip = sprite_strip
        self.index = 0
        self.frames = int(sprite_strip.width / frame_size.x)
        self.frame_size = frame_size

        self.source = Rectangle(self.frame_size.x * int(self.index), self.frame_size.y, self.frame_size.x, self.frame_size.y)
        self.dest = Rectangle(pos.x, pos.y, frame_size.x, frame_size.y)

        self.discard = False

    def update(self, delta_time):
        if self.index < self.frames - 1:
            self.index += 20 * delta_time
            self.source = Rectangle(self.frame_size.x * int(self.index), self.frame_size.y, self.frame_size.x, self.frame_size.y)
        else:
            self.discard = True

    def draw(self, debug: bool):
        draw_texture_pro(self.sprite_strip, self.source, self.dest, Vector2(self.source.width / 2, self.source.height / 2), 0, WHITE)


class Player(Sprite):
    def __init__(self, tex: Texture, pos, shoot_laser):
        super().__init__(tex, pos, PLAYER_SPEED, Vector2())
        self.shoot_laser = shoot_laser

    def constraint(self):
        self.dest.x = clamp(self.dest.x, self.dest.width / 2, get_screen_width() - self.dest.width / 2)
        self.dest.y = clamp(self.dest.y, self.dest.height / 2, get_screen_height() - self.dest.height / 2)

    def input(self):
        self.direction.x = is_key_down(KEY_RIGHT) - is_key_down(KEY_LEFT)
        self.direction.y = is_key_down(KEY_DOWN) - is_key_down(KEY_UP)
        self.direction = vector2_normalize(self.direction)

        if is_key_pressed(KEY_SPACE):
            self.shoot_laser(Vector2(self.dest.x, self.dest.y - 50))

    def update(self, delta_time):
        self.input()
        self.move(delta_time)
        self.constraint()
