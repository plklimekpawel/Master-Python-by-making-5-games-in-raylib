from random import choice

from settings import *


class Paddle:
    def __init__(self, pos: Vector2, size: Vector2):
        center_pos = Vector2(pos.x - size.x / 2, pos.y - size.y / 2)
        self.dest = Rectangle(center_pos.x, center_pos.y, size.x, size.y)
        self.old_dest = Rectangle(self.dest.x, self.dest.y, self.dest.width, self.dest.height)

        self.speed = SPEED['opponent']
        self.direction = Vector2()

    def constraint(self):
        if self.dest.y <= 0:
            self.dest.y = 0
        elif self.dest.y + self.dest.height >= get_screen_height():
            self.dest.y = get_screen_height() - self.dest.height

    def get_direction(self):
        self.direction.y = is_key_down(KEY_DOWN) - is_key_down(KEY_UP)

    def move(self, delta_time):
        self.dest.x += self.direction.x * self.speed * delta_time
        self.dest.y += self.direction.y * self.speed * delta_time

    def update(self, delta_time):
        self.old_dest = Rectangle(self.dest.x, self.dest.y, self.dest.width, self.dest.height)
        self.get_direction()

        self.constraint()
        self.move(delta_time)

    def draw(self):
        for i in range(5):
            shadow_offset = i
            shadow_dest = Rectangle(self.dest.x + shadow_offset, self.dest.y + shadow_offset, self.dest.width, self.dest.height)
            draw_rectangle_rounded(shadow_dest, .2, 16, COLORS['paddle shadow'])
        draw_rectangle_rounded(self.dest, .2, 16, COLORS['paddle'])

class Player(Paddle):
    def __init__(self, pos: Vector2, size: Vector2):
        super().__init__(pos, size)
        self.speed = SPEED['player']

class Opoonent(Paddle):
    def __init__(self, pos: Vector2, size: Vector2, ball: Ball):
        super().__init__(pos, size)
        self.speed = SPEED['opponent']
        self.ball = ball

    def get_direction(self):
        center_y = self.dest.y + self.dest.height / 2
        ball_center_y = self.ball.dest.y + self.ball.dest.height / 2
        self.direction.y = int(center_y < ball_center_y) - int(center_y > ball_center_y)
        self.direction = vector2_normalize(self.direction)

class Ball:
    def __init__(self, pos: Vector2, radius, direction, paddles, update_score):
        self.paddles = paddles
        self.speed = SPEED['ball']
        self.update_score = update_score

        center_pos = Vector2(pos.x - radius / 2, pos.y - radius / 2)
        self.dest = Rectangle(center_pos.x, center_pos.y, radius, radius)
        self.old_dest = Rectangle(self.dest.x, self.dest.y, self.dest.width, self.dest.height)
        self.direction = direction
        self.radius = radius

        # timer
        self.start_time = get_time()
        self.duration = 1
        self.speed_modifier = 1

    def collision(self, axis: str):
        for sprite in self.paddles:
            if check_collision_recs(self.dest, sprite.dest):
                if axis == 'x':
                    right = self.dest.x + self.dest.width
                    old_right = self.old_dest.x + self.old_dest.width
                    sprite_right = sprite.dest.x + sprite.dest.width
                    old_sprite_right = sprite.old_dest.x + sprite.old_dest.width
                    left = self.dest.x
                    old_left = self.old_dest.x
                    sprite_left = sprite.dest.x
                    old_sprite_left = sprite.old_dest.x

                    # Ball Right collision
                    if right >= sprite_left and old_right <= old_sprite_left:
                        self.dest.x = sprite.dest.x - self.dest.width   # Ball right to sprite left
                        self.direction.x *= -1

                    # Ball Left collision
                    if left <= sprite_right and old_left >= old_sprite_right:
                        self.dest.x = sprite_right  # Ball left to sprite right
                        self.direction.x *= -1
                else:
                    bottom = self.dest.y + self.dest.height
                    old_bottom = self.old_dest.y + self.old_dest.height
                    sprite_bottom = sprite.dest.y + sprite.dest.height
                    old_sprite_bottom = sprite.old_dest.y + sprite.old_dest.height
                    top = self.dest.y
                    old_top = self.old_dest.y
                    sprite_top = sprite.dest.y
                    old_sprite_top = sprite.old_dest.y

                    # Ball Bottom collision
                    if bottom >= sprite_top and old_bottom <= old_sprite_top:
                        self.dest.y = sprite.dest.y - self.dest.height  # Ball bottom to sprite top
                        self.direction.y *= -1

                    # Ball Top collision
                    if top <= sprite_bottom and old_top >= old_sprite_bottom:
                        self.dest.y = sprite_bottom   # Ball top to sprite bottom
                        self.direction.y *= - 1

    def constraint(self):
        if self.dest.y <= 0:
            self.dest.y = 0
            self.direction.y *= -1
        elif self.dest.y + self.radius >= get_screen_height():
            self.dest.y = get_screen_height() - self.radius
            self.direction.y *= -1

        elif self.dest.x + self.radius >= WINDOW_WIDTH or self.dest.x <= 0:
            self.update_score('player' if self.dest.x < WINDOW_WIDTH / 2 else 'opponent')
            self.reset()

    def reset(self):
        self.dest.x = WINDOW_WIDTH / 2 - self.dest.width / 2
        self.dest.y = WINDOW_HEIGHT / 2 - self.dest.height / 2
        self.direction = Vector2(choice([1, -1]), uniform(0.7, 0.8) * choice([-1, 1]))

        self.start_time = get_time()

    def timer(self):
        if get_time() - self.start_time >= self.duration:
            self.speed_modifier = 1
        else:
            self.speed_modifier = 0

    def move(self, delta_time):
        self.dest.x += self.direction.x * self.speed * self.speed_modifier * delta_time
        self.collision('x')
        self.dest.y += self.direction.y * self.speed * self.speed_modifier * delta_time
        self.collision('y')

    def update(self, delta_time):
        self.timer()
        self.old_dest = Rectangle(self.dest.x, self.dest.y, self.dest.width, self.dest.height)

        self.constraint()
        self.move(delta_time)

    def draw(self):
        center = Vector2(self.dest.x + self.radius / 2, self.dest.y + self.radius / 2)
        for i in range(5):
            shadow_offset = i
            draw_circle_v(Vector2(center.x + shadow_offset, center.y + shadow_offset), self.radius / 2,
                          COLORS['ball shadow'])
        draw_circle_v(center, self.radius / 2, COLORS['ball'])

