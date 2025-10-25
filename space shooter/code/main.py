from settings import *
from custom_timer import Timer
from sprites import Player, Laser, Meteor, ExplosionAnimation


class Main:
    def __init__(self):
        init_window(WINDOW_WIDTH, WINDOW_HEIGHT, 'Space Shooter')
        self.debug: bool = False

        self.import_assets()
        self.meteors = []
        self.lasers = []
        self.explosions = []

        self.meteor_timer = Timer(METEOR_TIMER_DURATION, True, True, self.create_meteor)

        self.player = Player(self.assets['player'], Vector2(get_screen_width() / 2, get_screen_height() / 2), self.shoot_laser)

    def import_assets(self):
        self.assets = {
            'player': load_texture('../images/spaceship.png'),
            'star': load_texture('../images/star.png'),
            'laser': load_texture('../images/laser.png'),
            'meteor': load_texture('../images/meteor.png'),
            'explosion_animation': load_texture('../images/explosion/explosion_spritesheet.png'),
            'font': load_font_ex('../fonts/Pixellari.ttf', FONT_SIZE, ffi.NULL, 0)
        }

        self.star_data = [
            (
                Vector2(randint(0, get_screen_width()), randint(0, get_screen_height())),  # Pos
                uniform(0.5, 1.6)  # Size
            ) for i in range(30)
        ]

    def draw_stars(self):
        tex = self.assets['star']
        source = Rectangle(0, 0, tex.width, tex.height)
        for pos, scale in self.star_data:
            dest = Rectangle(pos.x, pos.y, tex.width * scale, tex.height * scale)

            draw_texture_pro(tex, source, dest, Vector2(), 0, WHITE)

    def draw_score(self):
        score = int(get_time())
        font_size = measure_text_ex(self.assets['font'], str(score), FONT_SIZE, 0)
        pos = Vector2(get_screen_width() / 2 - font_size.x / 2, 40)

        draw_text_ex(self.assets['font'], str(score), pos, FONT_SIZE, 0, WHITE)
        padding = Vector2(20, 10)
        offset_y = 5
        text_rect = Rectangle(pos.x - padding.x / 2, pos.y - padding.y / 2 - offset_y, font_size.x + padding.x, font_size.y + padding.y)
        draw_rectangle_rounded_lines_ex(text_rect, 0.1, 0, 8, WHITE)

    def shoot_laser(self, pos):
        self.lasers.append(Laser(self.assets['laser'], pos))

    def create_meteor(self):
        self.meteors.append(Meteor(self.assets['meteor']))

    def discard_sprites(self):
        self.lasers = [laser for laser in self.lasers if not laser.discard]
        self.meteors = [meteor for meteor in self.meteors if not meteor.discard]
        self.explosions = [explosion for explosion in self.explosions if not explosion.discard]

    def check_collisions(self):
        for meteor in self.meteors:
            player_center = Vector2(self.player.dest.x, self.player.dest.y)
            meteor_center = Vector2(meteor.dest.x, meteor.dest.y)
            if check_collision_circles(player_center, self.player.collision_radius, meteor_center, meteor.collision_radius):
                close_window()

        for laser in self.lasers:
            for meteor in self.meteors:
                if check_collision_circle_rec(Vector2(meteor.dest.x, meteor.dest.y), meteor.collision_radius, laser.dest):
                    laser.discard = True
                    meteor.discard = True

                    pos = Vector2(laser.dest.x, laser.dest.y)
                    self.explosions.append(ExplosionAnimation(self.assets['explosion_animation'], pos, Vector2(48, 46)))

    def update(self):
        delta_time = get_frame_time()
        if is_key_pressed(KEY_F1):
            self.debug = not self.debug

        self.meteor_timer.update()
        self.discard_sprites()

        for sprite in self.lasers + self.meteors + self.explosions:
            sprite.update(delta_time)
        self.player.update(delta_time)

        self.check_collisions()

    def draw(self):
        begin_drawing()
        clear_background(BG_COLOR)
        self.draw_stars()
        for sprite in self.lasers + self.meteors + self.explosions:
            sprite.draw(self.debug)

        self.player.draw(self.debug)
        self.draw_score()
        end_drawing()

    def run(self):
        while not window_should_close():
            self.update()
            self.draw()
        close_window()


if __name__ == '__main__':
    main = Main()
    main.run()
