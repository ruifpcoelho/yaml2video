# YAML2VIDEO

This software takes YAML files as input and converts into video sequences.

## Table of Contents

- [Usage](#usage)
- [Examples](#examples)
- [Documentation](#documenation)


## Usage

Follow these steps to use the CLI to create the videos from YAML files and images:

1. Setting up Images and Configuration

Begin by creating a dedicated folder containing the images and a YAML configuration file.

2. Running the Process

To initiate the process, run the following command, , replacing the file path as needed:

```
python main.py -c ./examples/simple/0-minimal.yaml
```

For batch processing of all YAML files within a selected folder, utilize the following command:

```
python main.py -c ./examples/simple/
```

The resulting videos output will be saved within the same original folder.

For batch processing of all YAML files within multiple folders, utilize the following command:

```
python main.py -c ./examples/simple/ ./examples/complex/
```

The resulting videos output will be saved within the same original folders.

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

## Issues

### png showed as blank image on video

Tip: convert using Gimp to:

* Image > Mode > RGB (already done in script for images withou alfa channel)
* Image > Precision > 8 bit Integer
* Layer > Transparency > Add Alfa Channel

## TODO

* SVG file format support
