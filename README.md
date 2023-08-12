
# MUPIPY

This software takes YAML files as input and converts into video sequences.

## Table of Contents

- [Usage](#usage)
- [Examples](#examples)
- [Documentation](#documenation)

### Usage - Github Actions

Follow these steps to use the template and manage your repository using GitHub:

1. Create a Repository from Template

Start by creating a new repository using the template provided at: [yaml2video-template](https://github.com/ruifpcoelho/yaml2video-template):

* Locate the "Use this template" button positioned above the list of files.
* Choose the option labeled "Create a new repository."
* Utilize the dropdown menu labeled "Owner" to designate the GitHub account under which you wish to assume ownership of the repository.
* Provide a name for your repository, an optional description, and complete any other necessary parameters.
* Finalize the process by clicking the "Create repository from template" button.

For more detailed and up-to-date instructions, please refer to the official GitHub documentation: [Creating a repository from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).

2. Clone Your Repository

Once the new repository is created, clone it to your local machine using the following command:

````
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY-NAME
````

3. You can have the videos generated in two possible ways:

a) Placed in the repository alongside the respective YAML files, with matching names.
b) The created videos made available as artifacts.

Choose the option and update the [workflow](https://github.com/ruifpcoelho/yaml2video-template/blob/master/.github/workflows/build-video.yml) file accordingly:

a) If you choose to place videos in the repository, keep the "Upload Artifact" step and delete the "Update repo" step in the workflow file.
b) If you choose to make videos available as artifacts, keep the "Update repo" step and delete the "Upload Artifact" step in the workflow file.

4. Make Changes to YAML File and Replace Images

Navigate to the cloned repository on your local machine.
Modify the YAML file and replace the images according to your requirements.

5. Commit Your Changes

After making the necessary changes, stage the modified files, commit and push the committed changes to your GitHub repository:

```
git add .
git commit -m "Describe the changes you made"
git push
```

The videos will be generated based on the changes you made to the Gitflow file.
There are two possible outcomes:

* If you keep the section, the created videos will be placed in the repository alongside the respective YAML files, with matching names.

* Alternatively, the created videos might be available as artifacts, depending on the configuration in the Gitflow file.

That's it! You've successfully utilized GitHub and managed your repository following the outlined steps.

## Usage - CLI

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

## TODO

* SVG file format support
