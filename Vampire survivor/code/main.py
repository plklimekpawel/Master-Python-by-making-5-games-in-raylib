from random import choice

from settings import *
from sprites import Player, Collider, Sprite, Tile, Gun, Bullet, Enemy
from pytmx import TiledMap
from pyray import *

class Main:
    def __init__(self):
        init_window(WINDOW_WIDTH, WINDOW_HEIGHT, 'Vampire Survivor')

        self.assets = {
            'player': load_texture('../images/player/character_sheet.png'),
            'world_tileset': load_texture('../data/graphics/tilesets/world_tileset.png'),
            'gun': load_texture('../images/gun/gun.png'),
            'bullet': load_texture('../images/gun/bullet.png'),
            'skeleton': load_texture('../images/enemies/skeleton/skeleton.png'),
            'bat': load_texture('../images/enemies/bat/bat.png'),
            'blob': load_texture('../images/enemies/blob/blob.png'),
        }
        self.debug: bool = False

        self.collision_sprites = []
        self.bullets = []
        self.ground_tiles = []
        self.enemies = []

        # enemy spawn timer
        self.spawn_positions = []
        self.enemy_spawn_rate = 0.5
        self.enemy_spawn_time = 0

        self.setup()

        # gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 0.1

        # camera
        self.camera = Camera2D()
        self.camera.zoom = 1
        self.camera.target = Vector2(self.player.dest.x + self.player.source.width / 2, self.player.dest.y + self.player.source.height / 2)
        self.camera.offset = Vector2(get_screen_width() / 2, get_screen_height() / 2)
        self.camera.rotation = 0

    def setup(self):
        tmx_data = TiledMap('../data/maps/world.tmx')

        object_texture_cache = {}

        for obj in tmx_data.get_layer_by_name('Objects'):
            filename = obj.image[0]
            if filename not in object_texture_cache:
                object_texture_cache[filename] = load_texture(str(filename))
            texture = object_texture_cache[filename]
            self.collision_sprites.append(Sprite(texture, Vector2(obj.x, obj.y)))

        for obj in tmx_data.get_layer_by_name('Collisions'):
            self.collision_sprites.append(Collider(Vector2(obj.x, obj.y), Vector2(obj.width, obj.height)))

        for x, y, gid_or_tuple in tmx_data.get_layer_by_name('Ground').tiles():
            filename, rect, flags = gid_or_tuple
            source_rect = Rectangle(*rect)
            position = Vector2(x * TILE_SIZE, y * TILE_SIZE)

            self.ground_tiles.append(Tile(position, source_rect))

        for obj in tmx_data.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(self.assets['player'], Vector2(obj.x - 64, obj.y), self.collision_sprites)
                self.gun = Gun(self.assets['gun'], self.player)
            else:
                self.spawn_positions.append(Vector2(obj.x, obj.y))

    def input(self):
        if is_key_pressed(KEY_F1):
            self.debug = not self.debug

        if is_mouse_button_down(0) and self.can_shoot:
            offset = 10
            if self.gun.player_direction.x > 0:
                offset *= -1
            bullet_y_offset = Vector2(-self.gun.player_direction.y * offset, self.gun.player_direction.x * offset)

            pos = Vector2(
                self.gun.dest.x + self.gun.player_direction.x * 65 + bullet_y_offset.x,
                self.gun.dest.y + self.gun.player_direction.y * 65 + bullet_y_offset.y
            )

            self.bullets.append(Bullet(self.assets['bullet'], pos, self.gun.player_direction))

            self.can_shoot = False
            self.shoot_time = get_time()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = get_time()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def spawn_timer(self):
        if get_time() - self.enemy_spawn_time >= self.enemy_spawn_rate:
            tex = choice([self.assets['skeleton'], self.assets['blob'], self.assets['bat']])
            pos = choice(self.spawn_positions)
            self.enemies.append(Enemy(tex, pos, self.collision_sprites, self.player))

            self.enemy_spawn_time = get_time()

    def bullet_collision(self):
        for bullet in self.bullets:
            for enemy in self.enemies:
                if check_collision_recs(bullet.get_collision_rect(), enemy.hitbox_rect):
                    bullet.discard, enemy.discard = True, True

    def discard_sprites(self):
        self.bullets = [bullet for bullet in self.bullets if not bullet.discard]
        self.enemies = [enemy for enemy in self.enemies if not enemy.discard]

    def update(self):
        delta_time = get_frame_time()
        self.discard_sprites()
        self.gun_timer()
        self.spawn_timer()
        self.bullet_collision()
        self.input()

        for sprite in self.collision_sprites + [self.player, self.gun] + self.bullets + self.enemies:
            sprite.update(delta_time)
        self.camera.target = Vector2(self.player.dest.x + self.player.source.width / 2, self.player.dest.y + self.player.source.height / 2)

    def draw(self):
        def y_sorting():
            sprites = self.collision_sprites + [self.player, self.gun] + self.bullets + self.enemies
            for sprite in sorted(sprites, key=lambda sprite: sprite.dest.y + sprite.dest.height / 2):
                sprite.draw(self.debug)

        begin_drawing()
        begin_mode_2d(self.camera)
        clear_background(GRAY)

        for tile in self.ground_tiles:
            draw_texture_rec(self.assets['world_tileset'], tile.source_rect, tile.position, WHITE)
        y_sorting()


        end_mode_2d()
        draw_fps(0, 0)
        end_drawing()

    def run(self):
        while not window_should_close():
            self.update()
            self.draw()
        close_window()

if __name__ == '__main__':
    Main().run()
