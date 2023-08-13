from . import settings

import cv2
import math
import numpy as np


def pause(background_image, duration=None, file_id=0):
    frame_image = background_image
    frames = round(duration * settings.fps / 1000)
    for i in range(0, frames):
        output_file = settings.campaign_temp_path + '/' + str(file_id + i).rjust(10, '0') + '.' + settings.file_format
        cv2.imwrite(output_file, frame_image)
    file_id += frames
    return frame_image, file_id


def convert_center_to_topleft(image_width, image_height, scene):

    # Convert start position from image center to top-left
    start_x = round(scene['start_x'] - image_width / 2)
    start_y = round(scene['start_y'] - image_height / 2)

    # Convert end position from image center to top-left
    end_x = round(scene['end_x'] - image_width / 2)
    end_y = round(scene['end_y'] - image_height / 2)

    return start_x, end_x, start_y, end_y


def calculate_image_positions(canvas, image, scenes, layers_positions=[]):

    positions = []
    for index, scene in enumerate(scenes):
        start_x = scene['_processed']['start_x']
        end_x = scene['_processed']['end_x']
        start_y = scene['_processed']['start_y']
        end_y = scene['_processed']['end_y']

        # Default number of miliseconds corresponds to 1 frame
        if scene.get('duration', None) is None:
            duration = round(1000 / settings.fps)
        else:
            duration = scene['duration']

        # Select the effect function based on the input parameter
        effect = scene.get('effect', None)
        if effect == 'ease-in':
            func = animate_ease_in
        elif effect == 'linear':
            func = animate_linear
        elif effect == 'still':
            func = animate_still
        elif effect == 'bounce':
            func = animate_bounce
        else:
            func = animate_ease_in

        # Create the list with positions
        scene_positions = apply_easing(start_x, start_y, end_x, end_y, duration, func)

        # Apply initial time of scene
        start_t = scene.get('start_t', None)
        empty_frames = 0

        if start_t is None and len(layers_positions) > 0 and index == 0:
            # Start with previous
            empty_frames = len(layers_positions[-1])
        elif start_t is not None and start_t > 0:
            # Start after start_t miliseconds
            empty_frames = round(start_t * settings.fps / 1000)

        prefix = [[None, None]] * empty_frames
        scene_positions = prefix + scene_positions
        positions = positions + scene_positions

    return positions


def apply_easing(start_x, start_y, end_x, end_y, duration, easing_function):

    # Calculate the number of frames for the animation event
    frames = round(duration * settings.fps / 1000)

    # Create normalized timeline
    timeline = np.linspace(0, 1, frames)

    # Convert to the easing function
    easing_steps = np.array(list(map(easing_function, timeline)))

    # Calculate the x path positions
    # Distance traveled in each frame
    distance_x = end_x - start_x
    position_x = np.round(easing_steps * distance_x, 0)
    # Offset for start position
    position_x = [start_x + x for x in position_x]

    # Calculate the y path positions
    # Distance traveled in each frame
    distance_y = end_y - start_y
    position_y = np.round(easing_steps * distance_y, 0)
    # Offset for start position
    position_y = [start_y + y for y in position_y]

    # Combine x and y positions
    positions = zip(position_x, position_y)
    positions = [[round(num[0]), round(num[1])] for num in positions]

    return positions


def animate_still(t):
    return 0


def animate_linear(t):
    return t


def animate_ease_in(t):
    if t == 1:
        return 1
    return 1 - math.pow(2, -10 * t)


def animate_bounce(t):
    # https://www.desmos.com/calculator/0t2a24dcrh
    if t < 0.3636:
        return 7.5625 * t ** 2
    elif t < 0.76:
        return (t - 0.55) ** 2 * 3.7 + 0.85
    elif t < 0.9:
        return (t - 0.87) ** 2 * 1.8 + 0.97
    return 1
