from dataclasses import dataclass
from math import atan2, degrees
from settings import *
import json

@dataclass
class Tile:
    position: Vector2
    source_rect: Rectangle

class Collider:
    def __init__(self, pos: Vector2, size: Vector2):
        self.dest = Rectangle(pos.x, pos.y, size.x, size.y)

    def update(self, delta_time):
        pass

    def draw(self, debug: bool = False):
        if debug: draw_rectangle_lines_ex(self.dest, 2, RED)

class Sprite:
    def __init__(self, tex: Texture, pos: Vector2, source_rect=None):
        self.tex = tex
        if source_rect:
            self.source = source_rect
        else:
            self.source = Rectangle(0, 0, tex.width, tex.height)
        self.dest = Rectangle(pos.x, pos.y, self.source.width, self.source.height)

        self.discard: bool = False

    def get_center(self):
        return Vector2(self.dest.x + self.source.width / 2, self.dest.y + self.source.height / 2)

    def update(self, delta_time):
        pass

    def draw(self, debug: bool = False):
        draw_texture_pro(self.tex, self.source, self.dest, Vector2(), 0, WHITE)
        if debug: draw_rectangle_lines_ex(self.dest, 2, RED)

class Player(Sprite):
    def __init__(self, spritesheet: Texture, pos: Vector2, collision_sprites: list):
        self.state, self.frame_index = 'down', 0
        self.frames = {}
        self.load_animation()

        super().__init__(spritesheet, pos, self.frames[self.state][self.frame_index])

        self.direction = Vector2()
        self.speed = 400

        self.hitbox_shrink = Vector2(60, 90)
        self.hitbox_rect = Rectangle(
            pos.x + self.hitbox_shrink.x / 2,
            pos.y + self.hitbox_shrink.y / 2,
            self.source.width - self.hitbox_shrink.x,
            self.source.height - self.hitbox_shrink.y
        )
        self.collision_sprites = collision_sprites

    def load_animation(self):
        with open('../images/player/character_sheet.json') as file:
            data = json.load(file)

        tags = {tag['name']: (tag['from'], tag['to']) for tag in data['meta']['frameTags']}
        all_frames = list(data['frames'].items())

        for tag_name, (start, end) in tags.items():
            animation_frames = []
            for i in range(start, end + 1):
                frame_name, frame_data = all_frames[i]
                f = frame_data['frame']
                rect = Rectangle(f['x'], f['y'], f['w'], f['h'])
                animation_frames.append(rect)
            self.frames[tag_name] = animation_frames

    def animate(self, delta_time):
        # State
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'

        # Animate
        self.frame_index = self.frame_index + 5 * delta_time if (self.direction.x or self.direction.y) else 0
        self.source = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def collision(self, axis: str):
        for sprite in self.collision_sprites:
            if check_collision_recs(self.hitbox_rect, sprite.dest):
                if axis == 'x':
                    if self.direction.x > 0:
                        self.hitbox_rect.x = sprite.dest.x - self.hitbox_rect.width
                    elif self.direction.x < 0:
                        self.hitbox_rect.x = sprite.dest.x + sprite.dest.width
                else:
                    if self.direction.y > 0:
                        self.hitbox_rect.y = sprite.dest.y - self.hitbox_rect.height
                    elif self.direction.y < 0:
                        self.hitbox_rect.y = sprite.dest.y + sprite.dest.height

    def input(self):
        self.direction.x = is_key_down(KEY_RIGHT) - is_key_down(KEY_LEFT)
        self.direction.y = is_key_down(KEY_DOWN) - is_key_down(KEY_UP)
        self.direction = vector2_normalize(self.direction)

    def move(self, delta_time):
        self.hitbox_rect.x += self.direction.x * self.speed * delta_time
        self.collision('x')
        self.hitbox_rect.y += self.direction.y * self.speed * delta_time
        self.collision('y')

        self.dest.x = self.hitbox_rect.x - self.hitbox_shrink.x / 2
        self.dest.y = self.hitbox_rect.y - self.hitbox_shrink.y / 2

    def update(self, delta_time):
        super().update(delta_time)
        self.input()
        self.move(delta_time)
        self.animate(delta_time)

    def draw(self, debug: bool = False):
        # Draw player texture
        draw_texture_pro(self.tex, self.source, self.dest, Vector2(), 0, WHITE)

        # Debug outlines
        if debug:
            draw_rectangle_lines_ex(self.dest, 2, BLUE)  # sprite boundary
            draw_rectangle_lines_ex(self.hitbox_rect, 2, RED)  # hitbox

class Enemy(Sprite):
    def __init__(self, tex: Texture, pos: Vector2, collision_sprites: list, player: Player):
        self.frame_index = 0
        self.frame_size = Vector2(tex.width / 4, tex.height)
        self.animation_speed = 6
        source = Rectangle(self.frame_size.x * self.frame_index, 0, self.frame_size.x, self.frame_size.y)
        super().__init__(tex, pos, source)

        self.player = player
        self.direction = Vector2(self.player.get_center().x - self.get_center().x, self.player.get_center().y - self.get_center().y)
        self.speed = 350

        self.hitbox_shrink = Vector2(20, 40)
        self.hitbox_rect = Rectangle(
            pos.x + self.hitbox_shrink.x / 2,
            pos.y + self.hitbox_shrink.y / 2,
            self.source.width - self.hitbox_shrink.x,
            self.source.height - self.hitbox_shrink.y
        )
        self.collision_sprites = collision_sprites

    def collision(self, axis: str):
        for sprite in self.collision_sprites:
            if check_collision_recs(self.hitbox_rect, sprite.dest):
                if axis == 'x':
                    if self.direction.x > 0:
                        self.hitbox_rect.x = sprite.dest.x - self.hitbox_rect.width
                    elif self.direction.x < 0:
                        self.hitbox_rect.x = sprite.dest.x + sprite.dest.width
                else:
                    if self.direction.y > 0:
                        self.hitbox_rect.y = sprite.dest.y - self.hitbox_rect.height
                    elif self.direction.y < 0:
                        self.hitbox_rect.y = sprite.dest.y + sprite.dest.height

    def move(self, delta_time):
        self.direction = vector2_normalize(vector2_subtract(self.player.get_center(), self.get_center()))

        self.hitbox_rect.x += self.direction.x * self.speed * delta_time
        self.collision('x')
        self.hitbox_rect.y += self.direction.y * self.speed * delta_time
        self.collision('y')

        self.dest.x = self.hitbox_rect.x - self.hitbox_shrink.x / 2
        self.dest.y = self.hitbox_rect.y - self.hitbox_shrink.y / 2

    def update(self, delta_time):
        # Animate
        self.frame_index = self.frame_index + self.animation_speed * delta_time
        self.source = Rectangle(self.frame_size.x * int(self.frame_index % 4), 0, self.frame_size.x, self.frame_size.y)

        self.move(delta_time)

    def draw(self, debug: bool = False):
        # Draw player texture
        draw_texture_pro(self.tex, self.source, self.dest, Vector2(), 0, WHITE)

        # Debug outlines
        if debug:
            draw_rectangle_lines_ex(self.dest, 2, BLUE)  # sprite boundary
            draw_rectangle_lines_ex(self.hitbox_rect, 2, RED)  # hitbox

class Gun(Sprite):
    def __init__(self, tex: Texture, player: Player):
        self.player = player
        self.distance = 140
        self.player_direction = Vector2(1, 0)
        self.rotation = 0

        gun_pos = vector2_add(vector2_scale(self.player_direction, self.distance), self.player.get_center())
        super().__init__(tex, gun_pos)

    def get_direction(self):
        mouse_pos = get_mouse_position()
        player_pos = Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.player_direction = vector2_normalize(vector2_subtract(mouse_pos, player_pos))

    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.y, self.player_direction.x))
        self.rotation = angle

        if self.player_direction.x < 0:
            self.rotation = angle - 180  # gun on the left side
        else:
            self.rotation = angle   # gun on the right side

    def update(self, delta_time):
        self.get_direction()
        self.rotate_gun()

        gun_pos = vector2_add(vector2_scale(self.player_direction, self.distance), self.player.get_center())
        self.dest.x = gun_pos.x
        self.dest.y = gun_pos.y

    def draw(self, debug: bool = False):
        flip = self.player_direction.x < 0

        source = Rectangle(self.source.x, self.source.y, self.source.width, self.source.height)
        if flip:
            source.width *= -1
        draw_texture_pro(self.tex, source, self.dest, Vector2(self.source.width / 2, self.source.height / 2), self.rotation, WHITE)
        if debug:
            draw_rectangle_rec(self.dest, Color(0, 0, 0, 125))

class Bullet(Sprite):
    def __init__(self, tex: Texture, pos: Vector2, direction: Vector2):
        super().__init__(tex, pos)
        self.direction = direction
        self.speed = 800

        self.origin = Vector2(self.source.width / 2, self.source.height / 2)

        self.spawn_time = get_time()
        self.lifetime = 1   # 1 sec

    def get_collision_rect(self):
        return Rectangle(self.dest.x - self.origin.x, self.dest.y - self.origin.y, self.dest.width, self.dest.height)

    def should_discard(self):
        if get_time() - self.spawn_time >= self.lifetime:
            self.discard = True

    def move(self, delta_time):
        self.dest.x += self.speed * self.direction.x * delta_time
        self.dest.y += self.speed * self.direction.y * delta_time

    def update(self, delta_time):
        self.should_discard()
        self.move(delta_time)

    def draw(self, debug: bool = False):
        draw_texture_pro(self.tex, self.source, self.dest, self.origin, 0, WHITE)
        if debug: draw_rectangle_lines_ex(self.get_collision_rect(), 2, RED)
