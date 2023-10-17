import os
import argparse
import pytube
from moviepy.editor import *

#os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"
# Create an argument parser
parser = argparse.ArgumentParser(description='Convert YouTube videos to MP4 video files')
parser.add_argument('file', metavar='FILE', type=str, help='the path to the file containing YouTube video URLs')

# Parse the arguments
args = parser.parse_args()

# Get the path of the Videos folder in the user's home directory
video_folder = os.path.join(os.path.expanduser('~/Desktop'), 'Sport')

# Read the file containing YouTube video URLs
with open(args.file, 'r') as f:
    urls = f.readlines()

# Loop through each URL and convert the corresponding video to MP4
for url in urls:
    try:
        # Download the video using pytube
        yt = pytube.YouTube(url.strip())
        stream = yt.streams.filter(file_extension='mp4').first()
        output_file = stream.download()

        # Move the video file to the Videos folder
        video_path = os.path.join(video_folder, os.path.basename(output_file))
        os.replace(output_file, video_path)

        # Print the path of the saved MP4 file
        print(f"MP4 file saved as {video_path}")
    except Exception as e:
        print(f"Failed to convert video at {url.strip()}: {str(e)}")
