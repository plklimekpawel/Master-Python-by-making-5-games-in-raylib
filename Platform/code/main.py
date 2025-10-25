from timer import Timer
from settings import *
from pytmx import TiledMap
from sprites import Tile, Player, Bee, Worm, Bullet, Fire
from imports import import_spritesheet_animation, import_spritestrip_animation

class Game:
    def __init__(self):
        init_window(WINDOW_WIDTH, WINDOW_HEIGHT, 'Platformer')
        self.running = True
        self.debug = False

        self.assets = {
            'tilemap': load_texture('../data/graphics/tilemap.png'),
            'player_animation_data': import_spritesheet_animation('../images/player/player_sheet'),
            'worm_animation': import_spritestrip_animation(40, '../images/enemies/worm/worm_spritesheet'),
            'bee_animation': import_spritestrip_animation(40, '../images/enemies/bee/bee_spritesheet'),
            'bullet': load_texture('../images/gun/bullet.png'),
            'fire': load_texture('../images/gun/fire.png'),
            'flash_shader': load_shader(ffi.NULL, '../shaders/flash.glsl')
        }

        # Shaders
        self.flash_shader = self.assets['flash_shader']
        self.flash_loc = get_shader_location(self.flash_shader, 'flash')

        # groups
        self.all_sprites = []
        self.bullet_sprites = []
        self.enemy_sprites = []
        self.tiles = []
        self.collision_tiles = []

        self.setup()

        # Timers
        self.bee_timer = Timer(0.5, func=self.create_bee, repeat=True, autostart=True)

        # camera
        self.camera = Camera2D()
        self.camera.zoom = 1
        self.camera.target = self.player.center
        self.camera.offset = Vector2(get_screen_width() / 2, get_screen_height() / 2)
        self.camera.rotation = 0

    def setup(self):
        tmx_data = TiledMap('../data/maps/world.tmx')
        self.level_width = tmx_data.width * TILE_SIZE
        self.level_height = tmx_data.height * TILE_SIZE

        for x, y, gid_or_tuple in tmx_data.get_layer_by_name('Decoration').tiles():
            filename, rect, flags = gid_or_tuple
            source_rect = Rectangle(*rect)
            dest_rect = Rectangle(x * TILE_SIZE, y * TILE_SIZE, source_rect.width, source_rect.height)

            self.tiles.append(Tile(dest_rect, source_rect))

        for x, y, gid_or_tuple in tmx_data.get_layer_by_name('Main').tiles():
            filename, rect, flags = gid_or_tuple
            source_rect = Rectangle(*rect)
            dest_rect = Rectangle(x * TILE_SIZE, y * TILE_SIZE, source_rect.width, source_rect.height)

            self.collision_tiles.append(Tile(dest_rect, source_rect))

        for obj in tmx_data.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(self.assets['player_animation_data'], Vector2(obj.x, obj.y), self.collision_tiles, self.create_bullet)

                self.all_sprites.append(self.player)
            if obj.name == 'Worm':
                worm = Worm(
                    self.assets['worm_animation'][0],
                    self.assets['worm_animation'][1],
                    Rectangle(obj.x, obj.y, obj.width, obj.height),
                    shader=self.flash_shader,
                    flash_loc=self.flash_loc
                )
                self.enemy_sprites.append(worm)

    def collision(self):
        # Bullet -> Enenmies
        for bullet in self.bullet_sprites:
            for enemy in self.enemy_sprites:
                if check_collision_recs(bullet.dest, enemy.dest):
                    bullet.discard = True
                    enemy.destroy()

        # Enemies -> Player
        for enemy in self.enemy_sprites:
            if check_collision_recs(self.player.hitbox_rect, enemy.dest):
                self.running = False

    def create_bee(self):
        pos = Vector2(self.level_width + WINDOW_WIDTH, randint(0, self.level_height))
        self.enemy_sprites.append(
            Bee(self.assets['bee_animation'][0], self.assets['bee_animation'][1], pos, randint(300, 500), self.flash_shader, self.flash_loc))

    def create_bullet(self, pos, direction):
        offset_y = self.assets['bullet'].height / 2 - 5
        x = pos.x + direction.x * 34 if direction.x == 1 else pos.x + direction.x * 34 - self.assets['bullet'].width
        y = pos.y - offset_y
        self.bullet_sprites.append(Bullet(self.assets['bullet'], Vector2(x, y), direction))
        self.all_sprites.append(Fire(self.assets['fire'], Vector2(x, y), self.player))

    def discard_sprites(self):
        self.bullet_sprites = [bullet for bullet in self.bullet_sprites if not bullet.discard]
        self.all_sprites = [sprite for sprite in self.all_sprites if not sprite.discard]
        self.enemy_sprites = [enemy for enemy in self.enemy_sprites if not enemy.discard]

    def update(self):
        delta_time = get_frame_time()
        if is_key_pressed(KEY_F1):
            self.debug = not self.debug

        self.bee_timer.update()

        for sprite in self.all_sprites + self.bullet_sprites + self.enemy_sprites:
            sprite.update(delta_time)

        self.camera.target = self.player.center
        self.collision()
        self.discard_sprites()

    def draw(self):
        begin_drawing()
        begin_mode_2d(self.camera)
        clear_background(BG_COLOR)
        for tile in self.tiles + self.collision_tiles:
            draw_texture_pro(self.assets['tilemap'], tile.source, tile.dest, Vector2(), 0, WHITE)

            # Draw collider
            if tile in self.collision_tiles and self.debug:
                draw_rectangle_lines_ex(tile.dest, 1, RED)
        for sprite in self.all_sprites + self.bullet_sprites  + self.enemy_sprites:
            sprite.draw(self.debug)

        end_mode_2d()
        draw_fps(0, 0)
        end_drawing()

    def run(self):
        set_target_fps(FRAMERATE)
        while self.running and not window_should_close():
            self.update()
            self.draw()

        unload_shader(self.assets['flash_shader'])
        close_window()

if __name__ == '__main__':
    game = Game()
    game.run() 