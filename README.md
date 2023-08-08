
# MUPIPY

This software takes YAML files as input and converts into video sequences.

## Table of Contents

- [Usage](#usage)
- [Examples](#examples)
- [Documentation](#documenation)

## Usage

Create a folder with .png images and an yaml file.

Run for example:

`
python main.py -c ./examples/simple/0-minimal.yaml
`

If you select a folder, all yaml files will be processed:

`
python main.py -c ./examples/simple/
`

Output video is stored in the original folder.

## Examples

* [simplest yaml](./examples/simple/0-minimal.yaml)
* [sequence of images](./examples/simple/1-sequence.yaml)
* [multiple images](./examples/simple/0-multiple.yaml)
* [multiple scenes of same image](./examples/simple/0-scenes.yaml)

## Documentation

### Supported file formats

All file formats suppported by [opencv2/imread](https://docs.opencv.org/3.4/d4/da8/group__imgcodecs.html#ga288b8b3da0892bd651fce07b3bbd3a56), including:

* png
* jpg

SVG is not supported.

### YAML validator

This application uses [yamale](https://pypi.org/project/yamale/) for yaml files validation.

The YAML schema is defined in [schema.yaml](./schema.yaml).

## TODO

* SVG file format support
