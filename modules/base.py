from . import settings
from .animation import *

import argparse
import cv2
import numpy as np
import os
import shutil
import yamale


def apply_defaults_settings(input_dict, defaults_dict):
    for key, default_value in defaults_dict.items():
        input_dict[key] = input_dict.get(key, default_value)
    return input_dict


def validate_campaign_settings(campaign_settings):
    '''
    Validate yaml file syntax, structure and fields and apply defaults as necessary.
    '''
    # TODO: create feature to use yaml file as input parameter with different default values
    reference_dict = yamale.make_data(settings.default_yaml_path)
    reference_dict = reference_dict[0][0]
    merged_settings = apply_defaults_settings(campaign_settings, reference_dict)

    # Output file_path
    base_name, current_extension = os.path.splitext(campaign_settings['_process']['yaml_path'])
    alternative_output_file_path = base_name + '.mp4'
    campaign_settings['output_file_path'] = campaign_settings.get('output_file_path', alternative_output_file_path)

    # Load image from file, set missing parameters and translate images coordinates
    for segment in campaign_settings['film']:
        if segment['type'] == 'layers':
            for layer in segment['layers']:

                # Load image into campaign data structure
                if 'image_path' in layer:
                    image_path = os.path.join(campaign_settings['_process']['path'], layer['image_path'])
                    image = load_image(image_path=image_path)
                    if image is None:
                        return None
                elif 'image_name' in layer:
                    # TODO check if exists
                    image = campaign_settings['images'][layer['image_name']]
                else:
                    print('Error: Missing reference to layer image.')
                    if image is None:
                        return None

                # Set image dimensions if needed
                layer['width'] = layer.get('width', None)
                layer['height'] = layer.get('height', None)
                layer['width'], layer['height'] = calculate_resize_image(image, layer['width'], layer['height'])

                # Need to resize here, before convert_center_to_topleft

                last_positions = {'end_x': None, 'end_y': None}
                for scene in layer['scenes']:

                    # Apply position defaults
                    canvas_image_height = campaign_settings['canvas']['height']
                    canvas_image_width = campaign_settings['canvas']['width']

                    # Inherit initial positions or set defaults
                    if scene.get('start_x', None) is None:
                        if last_positions['end_x'] is not None:
                            scene['start_x'] = last_positions['end_x']
                        else:
                            scene['start_x'] = round(canvas_image_width / 2)

                    if scene.get('start_y', None) is None:
                        if last_positions['end_y'] is not None:
                            scene['start_y'] = last_positions['end_y']
                        else:
                            scene['start_y'] = round(canvas_image_height + layer['height'] / 2)

                    # Convert end position from image center to top-left
                    if scene.get('end_x', None) is None:
                        scene['end_x'] = scene['start_x']
                    if scene.get('end_y', None) is None:
                        scene['end_y'] = round((canvas_image_height - layer['height']) / 2)

                    last_positions['end_x'] = scene.get('end_x', None)
                    last_positions['end_y'] = scene.get('end_y', None)

                    # Translate reference point from center/middle to left/top
                    start_x, end_x, start_y, end_y = convert_center_to_topleft(layer['width'], layer['height'], scene)
                    scene['_processed'] = {}
                    scene['_processed']['start_x'] = start_x
                    scene['_processed']['end_x'] = end_x
                    scene['_processed']['start_y'] = start_y
                    scene['_processed']['end_y'] = end_y
        elif segment['type'] == 'video':
            video_path = os.path.join(campaign_settings['_process']['path'] , segment['video_path'])
            # Checks if video exists
            if not os.path.exists(video_path):
                print('Error: video file not found: ' + video_path)
                return None
            if not is_valid_video(video_path):
                print('Error: video file invalid format: ' + video_path)
                return None

    return merged_settings


def get_campaign_from_path(path):
    schema = yamale.make_schema('./schema.yaml')

    # Create a Data object
    data = yamale.make_data(path)

    # Validate data against the schema. Throws a ValueError if data is invalid.
    # TODO: better error handling
    yamale.validate(schema, data)

    # Add campaign path into campaign data
    for row in data:
        row[0]['_process'] = {}
        row[0]['_process']['yaml_path'] = row[1]
        row[0]['_process']['path'] = os.path.dirname(row[1])

    result = [c[0] for c in data]

    return result


def find_campaigns_in_folder(folder_path):
    '''
    Recursive function to ...
    '''
    campaigns = []

    if os.path.isfile(folder_path) and folder_path.lower().endswith(('.yaml', '.yml')):
        campaigns.append(folder_path)
    elif os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            if filename.startswith('.'):
                continue
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath) and filename.lower().endswith(('.yaml', '.yml')):
                campaigns.append(filepath)
            elif os.path.isdir(filepath):
                campaigns_list = find_campaigns_in_folder(filepath)
                campaigns.extend(campaigns_list)
    return campaigns


def get_campaigns_list(campaigns_args=[settings.campaigns_path]):
    '''
    Select campaigns to be processed.
    If no campaigns are provided in arg, all campaigns in settings.campaigns_path will be processed.
    '''

    campaigns = []
    for arg in campaigns_args:
        result = find_campaigns_in_folder(arg)
        campaigns.extend(result)

    return campaigns


def get_arguments():
    '''
    Get and parse input args.
    '''
    # TODO: create feature to use yaml file as input parameter with command line options
    parser = argparse.ArgumentParser(description="Create video from yaml file.")
    parser.add_argument('-c', '--campaigns', nargs='+',
                        help='List of campaigns yaml files to be processed. \
                            Must match the folder name after settings.campaigns_path.')

    args = parser.parse_args()
    arguments_dict = vars(args)
    return arguments_dict


def get_filesystem_campaigns(current_folder=settings.campaigns_path):
    '''
    Lists all YAML files (.yaml or .yml) within each folder.
    '''
    campaigns = []
    # Browse current folder
    for file_name in os.listdir(current_folder):
        if file_name.lower().endswith(('.yaml', '.yml')):
            campaigns.append(os.path.join(current_folder, file_name))
        elif os.path.isdir(file_name):
            folder_path = os.path.join(current_folder, file_name)
            result = get_filesystem_campaigns(folder_path)
            campaigns.extend(result)

    return campaigns


def create_temp_folder(folder_path):
    '''
    Create a temporary folder for temporary file storage.
    The delete_temp_folder() function is called, deleting all contents to
    ensure that any existing temporary folder is removed before creating a
    new one.

    Parameters:
        folder_name (str, optional): The name of the temporary folder to be
                                     created. The default is defined in
                                     settings.campaign_temp_path.

    Returns:
        str: The path of the created temporary folder.
    '''

    # Delete existing folder if exists
    delete_temp_folder(folder_path)

    # Create folder
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    return folder_path


def delete_temp_folder(folder_path):
    '''
    Delete the temporary folder.

    Parameters:
        folder_name (str, optional): The name of the temporary folder to be
                                     deleted. The default is defined in
                                     settings.campaign_temp_path.
    '''

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


def hexadecimal_color_to_RGB(color='#ffffff'):
    # Convert hexadecimal color code to RGB values
    color_rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
    return color_rgb


def hexadecimal_color_to_GBR(color='#ffffff'):
    # Convert hexadecimal color code to GBR values
    color_gbr = tuple(int(color[i:i + 2], 16) for i in (3, 5, 1))
    return color_gbr


def create_base_image(background_color='#ffffff', width=1080, height=1920):
    '''
    Create an image with specified dimensions and background color.

    Parameters:
        image_width (int): The width of the image to be created.
        image_height (int): The height of the image to be created.
        background_color_bgr (str): An hexadecimal color for the background color.
        ms (int): number of miliseconds to hold the image.

    Returns:
        image: Created image.

    Description:
        This function creates a new image with the given dimensions (image_width and image_height)
        and fills it with the specified background color represented as hexadecimal.

        Example usage:
        image, file_id = create_and_save_image(800, 600, '#ffffff)
    '''

    # Convert the color to the GBR, as used by cv2
    background_color_bgr = hexadecimal_color_to_GBR(background_color)

    # Create the image
    image_width = width
    image_height = height
    image = np.full((image_height, image_width, 3), background_color_bgr, dtype=np.uint8)

    return (image)


def create_text_image(text, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1.0, color='#000000'):
    '''
    Create an image with text.

    Parameters:
        text (str): The text to be rendered on the image. It can include multiple lines
                    separated by newline characters ('\n').
        font (int, optional): The font style for the text. Default is cv2.FONT_HERSHEY_SIMPLEX.
        font_scale (float, optional): The font scale factor.
        color (str, optional): The color of the text in hexadecimal format (e.g., '#RRGGBB').

    Returns:
        numpy.ndarray: The generated image as a NumPy array with dtype np.uint8.
    '''

    # Split the text into lines based on the newline character '\n'
    lines = text.split('\n')

    # Calculate the text size to determine the best-fit image width and height
    max_text_width = 0
    total_text_height = 0

    for line in lines:
        text_size = cv2.getTextSize(line, font, font_scale, 1)[0]
        text_width, text_height = text_size
        max_text_width = max(max_text_width, text_width)
        total_text_height += text_height

    # Calculate the image width and height to accommodate the text and center it
    line_spacing = 4  # Spacing between lines
    image_width = round(max_text_width * 1.1)

    image_height = round((total_text_height) * 1.1)
    line_spacing = round(text_height * 0.5)
    image_height += line_spacing * (len(lines))

    # Create a white image
    image = np.ones((image_height, image_width, 3), dtype=np.uint8) * 255

    # Draw the text on the image
    color = hexadecimal_color_to_GBR(color)

    # Draw the text on the image
    current_y = round(image_height * 0.05)
    for line in lines:
        text_size = cv2.getTextSize(line, font, font_scale, 1)[0]
        text_width, text_height = text_size

        # Calculate the position to center the text
        text_x = (image_width - text_width) // 2
        text_y = current_y + text_height

        cv2.putText(image, line, (text_x, text_y), font, font_scale, color, thickness=6, lineType=cv2.LINE_AA)

        current_y += text_height + line_spacing

    return image


def create_video_from_images(
        images_folder_path,
        frame_rate=settings.fps,
        video_filepath=None
):
    '''
    Create an MP4 video from images in the specified folder.

    Parameters:
        output_file (str): The path to the output video file (e.g., 'output_video.mp4').
        temp_folder_path (str): The path to the folder containing the images.
        frame_rate (int, optional): The frame rate (frames per second) of the output video.

    Returns:
        None
    '''

    # Define output_filepath
    # TODO: ...
    if video_filepath is None:
        video_filepath = images_folder_path + '/segment' + settings.file_format

    # Get a list of image files in the folder
    image_files = [os.path.join(images_folder_path, file) for file in os.listdir(images_folder_path) if file.endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort()

    # Check if there are any image files in the folder
    if not image_files:
        print('No image files found in the folder <' + images_folder_path + '>.')
        return

    # Get the dimensions of the first image
    image = cv2.imread(image_files[0])
    height, width, channels = image.shape

    # Create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_filepath, fourcc, frame_rate, (width, height))

    # Write each image to the video
    for image_file in image_files:
        image = cv2.imread(image_file)
        video.write(image)

    # Release the VideoWriter and close the video file
    video.release()

    return video_filepath


def load_image(
        image_path=None,
        image=None
):

    # Set image to be used in the animation
    if image_path is not None:
        # The image_filename input has precendence over the image object
        # Check if image exists
        if not os.path.exists(image_path):
            print('Error: image file not found: ' + image_path)
            return None

        # Read the image file
        image = cv2.imread(image_path)

    elif image is not None:
        # Using image as input
        pass

    else:
        print('Error: No image passed. Either image_filename or image must be passed as input.')

    return image


def calculate_resize_image(image, image_width, image_height):
    # Set default image sizes
    original_image_height, original_image_width, channels = image.shape
    if image_width is None:
        image_width = original_image_width
    if image_height is None:
        image_height = original_image_height

    # Resize image keeping the relative sizes
    if image_width != original_image_width:
        image_height = round(image_height * image_width / original_image_width)
    elif image_height != original_image_height:
        image_width = round(image_width * image_height / original_image_height)

    return image_width, image_height


def create_frames_from_layers(canvas, layers_images, layers_positions, images_path):

    background_image_height = canvas['height']
    background_image_width = canvas['width']
    base_image = create_base_image(canvas['background_color'], canvas['width'], canvas['height'])

    zipped_positions = zip(*layers_positions)

    # Loop every frame
    for frame_ix, frame in enumerate(zipped_positions):

        frame_image = base_image.copy()

        # Loop every layer
        for image_ix, image in enumerate(frame):

            # TODO: consider include inside positions
            image = layers_images[image_ix]
            image_height, image_width, channels = image.shape

            # Calculate the target region in the base image
            x = frame[image_ix][0]
            y = frame[image_ix][1]

            if x is not None and y is not None:
                # Control the overflow
                if (
                    y + image_height <= 0
                    or y >= background_image_height
                    or x + image_width <= 0
                    or x >= background_image_width
                ):
                    frame_y_start = 0
                    frame_y_end = 0
                    frame_x_start = 0
                    frame_x_end = 0

                    image_y_start = 0
                    image_y_end = 0
                    image_x_start = 0
                    image_x_end = 0
                else:
                    # Vertical overflow
                    if y < 0:
                        frame_y_start = 0
                        image_y_start = -y
                    else:
                        frame_y_start = y
                        image_y_start = 0
                    if y + image_height > background_image_height:
                        frame_y_end = background_image_height
                        image_y_end = background_image_height - y
                    else:
                        frame_y_end = y + image_height
                        image_y_end = image_height
                    # Horizontal overflow
                    if x < 0:
                        frame_x_start = 0
                        image_x_start = -x
                    else:
                        frame_x_start = x
                        image_x_start = 0
                    if x + image_width > background_image_width:
                        frame_x_end = background_image_width
                        image_x_end = background_image_width - x
                    else:
                        frame_x_end = x + image_width
                        image_x_end = image_width
                frame_image[frame_y_start:frame_y_end, frame_x_start:frame_x_end] = image[image_y_start:image_y_end, image_x_start:image_x_end]

        frame_name = 'F' + str(frame_ix).rjust(10, '0')
        output_file = os.path.join(images_path, frame_name + '.' + settings.file_format)
        cv2.imwrite(output_file, frame_image)


def concatenate_videos(video_paths, output_path):
    # Read the first video to get its properties
    first_video = cv2.VideoCapture(video_paths[0])
    frame_width = int(first_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(first_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = first_video.get(cv2.CAP_PROP_FPS)

    # Create a VideoWriter object to write the concatenated video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    # Iterate through each video and concatenate them
    for video_path in video_paths:
        video = cv2.VideoCapture(video_path)
        while True:
            ret, frame = video.read()
            if not ret:
                break
            out.write(frame)
        video.release()

    # Release the VideoWriter
    out.release()


def create_video_from_campaign_config(campaign_config):

    # TODO: enhance temp_folder options
    temp_folder_path = settings.temp_folder_path % str(campaign_config['_process']['id']).rjust(6, '0')
    create_temp_folder(temp_folder_path)

    # TODO: create function to create named images (named_image_from_file)
    named_images = {}
    if 'images' in campaign_config:
        for image in campaign_config['images']:
            print('image_name:', image['name'])
            pass

    # Create a list of all video segments to be concatenated
    campaign_config['_process']['segment_videos'] = []
    segment_id = 0
    for index, segment in enumerate(campaign_config['film']):

        # Name the segment
        segment['_process'] = {}
        segment['_process']['id'] = index

        # Create the segment temporary folder
        segment['_process']['path'] = temp_folder_path + '/S' + str(index).rjust(6, '0')
        create_temp_folder(segment['_process']['path'])

        # Define the output video file path
        segment['_process']['video_path'] = segment['_process']['path'] + '/output.mp4'

        # Create sequence of videos
        if segment['type'] == 'layers':
            # Video segment composed by a set of layers

            # Creating coordinates
            layers_images = []
            layers_positions = []
            for layer in segment['layers']:

                # Load image
                # TODO: consider using layer dict values and remove this code.
                # This is duplicated from validate_campaign_settings()
                if 'image_path' in layer:
                    image_path = os.path.join(campaign_config['_process']['path'], layer['image_path'])
                    image = load_image(image_path=image_path)
                elif 'image' in layer:
                    # TODO check if exists
                    image = named_images[layer['image_path']]

                # Resize image if needed
                image_width = layer['width']
                image_height = layer['height']
                original_image_height, original_image_width, channels = image.shape
                if image_width != original_image_width or image_height != original_image_height:
                    image = cv2.resize(image, (image_width, image_height))

                layers_images.append(image)

                layer_positions = calculate_image_positions(canvas=campaign_config['canvas'], image=image, scenes=layer['scenes'], layers_positions=layers_positions)
                layers_positions.append(layer_positions)

            # Padding to the end of each scene
            # Calculate the longest scene
            longest_length = max(len(sublist) for sublist in layers_positions)
            for index, layer in enumerate(layers_positions):
                last_position = layer[-1]
                sufix_len = longest_length - len(layer)
                sufix = [last_position] * sufix_len
                layer = layer + sufix
                layers_positions[index] = layer

            # Create individual images from layer images and positions
            create_frames_from_layers(
                canvas=campaign_config['canvas'],
                layers_images=layers_images,
                layers_positions=layers_positions,
                images_path=segment['_process']['path']
            )

            create_video_from_images(
                images_folder_path=segment['_process']['path'],
                frame_rate=campaign_config['fps'],
                video_filepath=segment['_process']['video_path']
            )
            campaign_config['_process']['segment_videos'].append(segment['_process']['video_path'])

        elif segment['type'] == 'video':
            video_path = os.path.join(campaign_config['_process']['path'], segment['video_path'])
            campaign_config['_process']['segment_videos'].append(video_path)
        else:
            print('WARNING: Unknown segment type')

        # TODO: append <layer_positions> to campaign dics

        segment_id += 1

    # TODO: concatenate segment videos
    concatenate_videos(
        video_paths=campaign_config['_process']['segment_videos'],
        output_path=campaign_config['output_file_path']
    )
    delete_temp_folder(temp_folder_path)


def is_valid_video(file_path):
    '''
    Check if a given file is a valid video file.
    '''
    try:
        # Open the video file
        cap = cv2.VideoCapture(file_path)
    except:
        print('erro')
        return False  # An error occurred

    try:
        # Check if the file was opened successfully and has valid frames
        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            return True
    except:
        return False  # An error occurred
