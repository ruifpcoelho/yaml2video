import os
# TODO: use different strategy for globals

# Default path for yaml defaults
current_dir = os.path.dirname(os.path.abspath(__file__))
default_yaml_path = os.path.join(current_dir, '../defaults.yaml')

# Number of frames per second
fps = 25

# Foldr with the campaigns tobe proessed
campaigns_path = './campaigns/'

# Temporary folder to temporarly store the images generated to create the video
temp_folder_path = 'temp_folder_%s'

# Tempoary images file format
file_format = 'png'

# Output file name
output_filename = 'output.mp4'
