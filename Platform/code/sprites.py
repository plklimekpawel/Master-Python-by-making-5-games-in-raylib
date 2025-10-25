from dataclasses import dataclass
from math import sin
from Platform.code.timer import Timer
from settings import *

@dataclass
class Tile:
    dest: Rectangle
    source: Rectangle

class Sprite:
    def __init__(self, tex: Texture, pos: Vector2):
        self.tex = tex
        self.source = Rectangle(0, 0, tex.width, tex.height)
        self.dest = Rectangle(pos.x, pos.y, self.source.width, self.source.height)

        self.direction = Vector2()
        self.speed = 400

        self.discard: bool = False

    def check_discard(self):
        pass

    def move(self, delta_time):
        self.dest.x += self.direction.x * self.speed * delta_time
        self.dest.y += self.direction.y * self.speed * delta_time

    def update(self, delta_time):
        self.move(delta_time)
        self.check_discard()

    def draw(self, debug: bool):
        draw_texture_pro(self.tex, self.source, self.dest, Vector2(), 0, WHITE)
        if debug:
            draw_rectangle_lines_ex(self.dest, 1, RED)

class Bullet(Sprite):
    def __init__(self, tex: Texture, pos: Vector2, direction):
        super().__init__(tex, pos)

        # adjustment
        self.source.width *= -1 if direction.x == -1 else 1

        self.speed = 850
        self.direction = direction

class Fire(Sprite):
    def __init__(self, tex: Texture, pos: Vector2, player: Player):
        super().__init__(tex, pos)
        self.player = player
        self.facing_right = self.player.facing_right
        self.timer = Timer(0.1, autostart=True, func=self.kill)
        self.y_offset = 5

        if self.player.facing_right:
            self.dest.x = (self.player.dest.x + self.player.dest.width)
            self.dest.y = self.player.center.y - self.dest.height / 2 + self.y_offset
        else:
            self.dest.x = self.player.dest.x - self.dest.width
            self.dest.y = self.player.center.y - self.dest.height / 2 + self.y_offset
            self.source.width *= -1

    def kill(self):
        self.discard = True

    def update(self, delta_time):
        self.timer.update()
        super().update(delta_time)

        # Follow player
        if self.player.facing_right:
            self.dest.x = (self.player.dest.x + self.player.dest.width)
            self.dest.y = self.player.center.y - self.dest.height / 2 + self.y_offset
        else:
            self.dest.x = self.player.dest.x - self.dest.width
            self.dest.y = self.player.center.y - self.dest.height / 2 + self.y_offset

        # Destory on flip
        if self.facing_right != self.player.facing_right:
            self.kill()

class AnimatedSprite(Sprite):
    def __init__(self, tex: Texture, animation_rects: dict[str, list[Rectangle]] | list[Rectangle], pos: Vector2):
        super().__init__(tex, pos)
        self.animation_rects = animation_rects
        self.animation_speed: int = 10
        self.frame_index = 0
        self.state = ''

        if isinstance(self.animation_rects, dict):
            self.state = list(self.animation_rects.keys())[0]
            self.source = self.animation_rects[self.state][self.frame_index]
        elif isinstance(self.animation_rects, list):
            self.source = self.animation_rects[self.frame_index]
        self.dest = Rectangle(pos.x, pos.y, self.source.width, self.source.height)

    def set_state(self):
        pass

    def animate(self, delta_time):
        self.frame_index = self.frame_index + self.animation_speed * delta_time
        if isinstance(self.animation_rects, dict):
            self.source = self.animation_rects[self.state][int(self.frame_index) % len(self.animation_rects[self.state])]
        elif isinstance(self.animation_rects, list):
            self.source = self.animation_rects[int(self.frame_index) % len(self.animation_rects)]

    def update(self, delta_time):
        self.set_state()
        super().update(delta_time)
        self.animate(delta_time)

class Player(AnimatedSprite):
    def __init__(self, animation_data: tuple[Texture, dict[str, list[Rectangle]]], pos: Vector2, collision_tiles, create_bullet):
        super().__init__(animation_data[0], animation_data[1], pos)
        self.create_bullet = create_bullet

        # Hitbox
        self.hitbox_shrink = Vector2(20, 10)
        self.hitbox_visual_offset = Vector2(0, -5)
        self.hitbox_rect = Rectangle(
            pos.x + self.hitbox_shrink.x / 2 + self.hitbox_visual_offset.x,
            pos.y + self.hitbox_shrink.y / 2 + self.hitbox_visual_offset.y,
            self.source.width - self.hitbox_shrink.x,
            self.source.height - self.hitbox_shrink.y
        )

        # Collision
        self.collision_tiles = collision_tiles
        self.floor_rect = Rectangle(self.hitbox_rect.x, self.hitbox_rect.y + self.hitbox_rect.height,
                                    self.hitbox_rect.width, 2)

        # Jumping
        self.gravity = 50
        self.on_floor = False

        # Timer
        self.shoot_timer = Timer(0.5)

        self.facing_right = True

    @property
    def center(self) -> Vector2:
        return Vector2(self.hitbox_rect.x + self.hitbox_rect.width / 2, self.hitbox_rect.y + self.hitbox_rect.height/ 2)

    def animate(self, delta_time):
        self.frame_index = self.frame_index + self.animation_speed * delta_time if (self.direction.x or self.direction.y) else 0
        self.source = self.animation_rects[self.state][int(self.frame_index) % len(self.animation_rects[self.state])]

    def set_state(self):
        if not self.on_floor:
            self.state = 'jump'
        elif self.direction.x != 0:
            self.state = 'run'
        else:
            self.state = 'run'

    def collision(self, axis: str):
        for sprite in self.collision_tiles:
            if check_collision_recs(self.hitbox_rect, sprite.dest):
                if axis == 'x':
                    if self.direction.x > 0:
                        self.hitbox_rect.x = sprite.dest.x - self.hitbox_rect.width
                    elif self.direction.x < 0:
                        self.hitbox_rect.x = sprite.dest.x + sprite.dest.width
                else:
                    if self.direction.y > 0:
                        self.hitbox_rect.y = sprite.dest.y - self.hitbox_rect.height
                        self.direction.y = 0
                    elif self.direction.y < 0:
                        self.hitbox_rect.y = sprite.dest.y + sprite.dest.height
                        self.direction.y = 0

    def input(self):
        self.direction.x = is_key_down(KEY_RIGHT) - is_key_down(KEY_LEFT)
        if is_key_down(KEY_UP) and self.on_floor:
            self.direction.y = -20

        if is_key_down(KEY_S) and not self.shoot_timer:
            self.create_bullet(self.center, Vector2(1 if self.facing_right else -1, 0))
            self.shoot_timer.activate()

    def move(self, delta_time):
        # Horizontal
        self.hitbox_rect.x += self.direction.x * self.speed * delta_time
        self.collision('x')

        # Vertical
        self.direction.y += self.gravity * delta_time
        self.hitbox_rect.y += self.direction.y
        self.collision('y')

        self.dest.x = self.hitbox_rect.x - self.hitbox_shrink.x / 2 + self.hitbox_visual_offset.x
        self.dest.y = self.hitbox_rect.y - self.hitbox_shrink.y / 2 + self.hitbox_visual_offset.y

    def check_floor(self):
        self.floor_rect = Rectangle(self.hitbox_rect.x, self.hitbox_rect.y + self.hitbox_rect.height, self.hitbox_rect.width, 2)
        self.on_floor = False
        for sprite in self.collision_tiles:
            if check_collision_recs(self.floor_rect, sprite.dest):
                self.on_floor = True

    def update(self, delta_time):
        self.shoot_timer.update()

        self.input()
        super().update(delta_time)
        self.check_floor()
        # self.animate(delta_time)

    def draw(self, debug: bool):
        if self.direction.x > 0:
            self.facing_right = True
        elif self.direction.x < 0:
            self.facing_right = False
        else:
            self.facing_right = self.facing_right

        # Checks if it neeeds to flip current frame(source) of animation without it, it would just flip one frame of animation
        source = Rectangle(self.source.x, self.source.y, self.source.width, self.source.height)
        if not self.facing_right:
            source.width *= -1

        draw_texture_pro(self.tex, source, self.dest, Vector2(), 0, WHITE)
        if debug:
            draw_rectangle_lines_ex(self.dest, 1, BLUE)
            draw_rectangle_rec(self.floor_rect, RED)
            draw_rectangle_lines_ex(self.hitbox_rect, 1, ORANGE)

class Enemy(AnimatedSprite):
    def __init__(self, tex, animation_rects, pos, shader, flash_loc):
        super().__init__(tex, animation_rects, pos)
        self.death_timer = Timer(0.2, func=self.kill)
        self.shader = shader
        self.flash_loc = flash_loc

    def kill(self):
        self.discard = True

    def destroy(self):
        self.death_timer.activate()
        self.animation_speed = 0

    def move(self, delta_time):
        if self.death_timer: return
        super().move(delta_time)

    def update(self, delta_time):
        self.death_timer.update()
        super().update(delta_time)

    def draw(self, debug: bool):
        source = Rectangle(self.source.x, self.source.y, self.source.width, self.source.height)
        if hasattr(self, "facing_right") and not self.facing_right:
            source.width *= -1

        flash_strength = 0.0
        if self.death_timer.active:
            flash_strength = 1.0

        flash_val = ffi.new("float[2]", [flash_strength, 0.0])
        set_shader_value(self.shader, self.flash_loc, flash_val, SHADER_UNIFORM_VEC2)

        begin_shader_mode(self.shader)
        draw_texture_pro(self.tex, source, self.dest, Vector2(), 0, WHITE)
        end_shader_mode()

        if debug:
            draw_rectangle_lines_ex(self.dest, 1, RED)

class Bee(Enemy):
    def __init__(self, tex: Texture, animation_rects: dict[str, list[Rectangle]] | list[Rectangle], pos: Vector2, speed, shader, flash_loc):
        super().__init__(tex, animation_rects, pos, shader, flash_loc)
        self.speed = speed
        self.amplitude = randint(500, 600)
        self.frequency = randint(2, 4)

    def move(self, delta_time):
        if self.death_timer: return
        self.dest.x -= self.speed * delta_time
        self.dest.y += sin(get_time() * self.frequency) * self.amplitude * delta_time

    def check_discard(self):
        if self.dest.x <= 0:
            self.discard = True

class Worm(Enemy):
    def __init__(self, tex: Texture, animation_rects: dict[str, list[Rectangle]] | list[Rectangle], rect: Rectangle, shader, flash_loc):
        super().__init__(tex, animation_rects, Vector2(rect.x, rect.y), shader, flash_loc)
        self.dest.y = rect.y + rect.height - self.dest.height
        self.moveable_area = rect
        self.speed = randint(160, 200)
        self.direction.x = 1
        self.facing_right = True

    def constraint(self):
        if self.dest.x + self.dest.width > self.moveable_area.x + self.moveable_area.width:
            self.direction.x = -1
            self.facing_right = not self.facing_right
        elif self.dest.x < self.moveable_area.x:
            self.direction.x = 1
            self.facing_right = not self.facing_right

    def update(self, delta_time):
        super().update(delta_time)
        self.constraint()
