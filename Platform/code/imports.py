import json
from settings import *

def import_spritesheet_animation(*path: str) -> tuple[Texture, dict[str, list[Rectangle]]]:
    path = join(*path)
    spritesheet = load_texture(path + '.png')
    frames = {}
    with open(path + '.json') as file:
        data = json.load(file)

    all_frames = list(data['frames'])
    for tag in data['meta']['frameTags']:
        animation_frames = []
        tag_name = tag['name']
        start, end = tag['from'], tag['to']
        for i in range(start, end + 1):
            data = all_frames[i]
            frame = data['frame']
            source = Rectangle(frame['x'], frame['y'], frame['w'], frame['h'])
            animation_frames.append(source)
        frames[tag_name] = animation_frames
    return spritesheet, frames

def import_spritestrip_animation(frame_width, *path: str) -> tuple[Texture, list[Rectangle]]:
    path = join(*path)
    spritestrip = load_texture(path + '.png')
    frames_amount = int(spritestrip.width / frame_width)

    frames_source = []
    for i in range(frames_amount):
        source = Rectangle(i * frame_width, i * spritestrip.height, frame_width, spritestrip.height)
        frames_source.append(source)

    return spritestrip, frames_source

