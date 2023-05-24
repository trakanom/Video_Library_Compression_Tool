# VideoCompressor

Bursting at the seams with high bitrate streaming footage? Overwhelmed by countless files that need individual processing? Hard drive running out of space but you still have so much more to record? Look no further than VideoCompressor!

## About

VideoCompressor is a powerful Python tool that utilizes the power of FFmpeg to compress your video files seamlessly. It does all the hard work so you don't have to. Set it up, let it run, and come back to a hard drive that's lighter and happier than ever.

## Features

- Automatically find and compress all video files in a directory
- Adjust the compression quality with a simple setting
- Choose to overwrite original files or save compressed files separately
- Monitor the progress with a friendly progress bar
- Get a summary of how much space you've saved

## Installation

Before using VideoCompressor, make sure you have `ffmpeg` and `ffprobe` installed on your system. They are required for the program to function.

Next, clone this repository and navigate into the directory:

```sh
git clone https://github.com/user/repo.git
cd repo
```

Then, install the necessary Python dependencies:

```sh
pip install -r requirements.txt
```

## Usage

To start compressing your video files, simply run the script with the directory, CRF value (0-51), and whether you want to overwrite the original files (true/false) as command line arguments:

```sh
python main.py /path/to/directory 28 true
```

If no arguments are provided, the script will use default values: current directory, CRF=28, and no overwriting.

## Troubleshooting

If you encounter any issues while using VideoCompressor, please open an issue on this repository. We appreciate your feedback and will do our best to assist you.

## Disclaimer

VideoCompressor is provided as-is, and while we do our best to ensure its functioning, we can't guarantee it will be entirely free of bugs or issues. Be sure to backup your videos before using VideoCompressor, especially if you choose to overwrite your original files. 

## Setup and Install Script

We've included a setup and install script for your convenience. This script handles the installation of `ffmpeg` and `ffprobe`, sets up the environment, and opens the program. Here's how you can use it:

```sh
./setup_and_run.sh
```

This script is intended to be used on Unix-like systems. If you're on Windows, you may need to manually install the dependencies and set up the environment. 

## Contribute

We welcome contributions! If you'd like to improve VideoCompressor, feel free to fork the repository and open a pull request. We appreciate any help in making VideoCompressor the best it can be.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
