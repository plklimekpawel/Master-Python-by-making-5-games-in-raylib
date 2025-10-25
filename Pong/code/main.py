import os
from random import choice
import json
from settings import *
from sprites import Ball, Player, Opoonent

def get_score_path():
    # Build absolute path to Pong/data/score.txt
    script_dir = os.path.dirname(os.path.abspath(__file__))  # → Pong/code
    data_dir = os.path.join(script_dir, '..', 'data')  # → Pong/data
    os.makedirs(data_dir, exist_ok=True)

    score_path = os.path.join(data_dir, 'score.txt')
    return score_path

class Main:
    def __init__(self):
        init_window(WINDOW_WIDTH, WINDOW_HEIGHT, 'Pong')

        self.paddles = []

        ball_direction = Vector2(choice([1, -1]), uniform(0.7, 0.8) * choice([-1, 1]))
        self.ball = Ball(Vector2(get_screen_width() / 2, get_screen_height() / 2), SIZE['ball'][0], ball_direction, self.paddles, self.update_score)

        self.player = Player(Vector2(*POS['player']), Vector2(*SIZE['paddle']))
        self.opoonent = Opoonent(Vector2(*POS['opponent']), Vector2(*SIZE['paddle']), self.ball)
        self.paddles.append(self.player)
        self.paddles.append(self.opoonent)

        # score
        try:
            with open(get_score_path()) as score_file:
                self.score = json.load(score_file)
        except:
            self.score = {'player': 0, 'opponent': 0}

    def display_score(self):
        font_size = 160

        # player
        text = str(self.score['player'])
        text_size = measure_text_ex(get_font_default(), text, font_size, 0)
        draw_text(text, int(WINDOW_WIDTH / 2 + 100 - text_size.x / 2), int(WINDOW_HEIGHT / 2 - text_size.y / 2), 160, WHITE)

        # opponent
        text = str(self.score['opponent'])
        text_size = measure_text_ex(get_font_default(), text, font_size, 0)
        draw_text(text, int(WINDOW_WIDTH / 2 - 100 - text_size.x / 2), int(WINDOW_HEIGHT / 2 - text_size.y / 2), 160,
                  WHITE)

        # line separator
        draw_line_ex(Vector2(WINDOW_WIDTH / 2, 0), Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT), 6, WHITE)

    def update_score(self, side):
        self.score['player' if side == 'player' else 'opponent'] += 1

    def update(self):
        delta_time = get_frame_time()

        for sprite in self.paddles + [self.ball]:
            sprite.update(delta_time)

    def draw(self):
        begin_drawing()
        clear_background(COLORS['bg'])
        self.display_score()

        for sprite in self.paddles + [self.ball]:
            sprite.draw()
        end_drawing()

    def run(self):
        while not window_should_close():
            self.update()
            self.draw()

        with open(get_score_path(), 'w') as score_file:
            json.dump(self.score, score_file)

        close_window()


if __name__ == '__main__':
    Main().run()