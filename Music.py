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
video_folder = os.path.join(os.path.expanduser('/Users/esiounath/Desktop/'), 'Music')

# Read the file containing YouTube video URLs
with open(args.file, 'r') as f:
    urls = f.readlines()

# Loop through each URL and convert the corresponding video to MP4
for url in urls:
    try:
        # Download the video using pytube
        yt = pytube.YouTube(url.strip())
        stream = yt.streams.filter(only_audio=True).first()
        output_file = stream.download(output_path='/Users/esiounath/Desktop/Music')

        # Move the video file to the Videos folder
        base, ext = os.path.splitext(output_file) 
        new_file = base + '.mp3'
        os.rename(output_file, new_file)

        # Print the path of the saved MP4 file
        print(f"MP3 file saved as {yt.title}")
    except Exception as e:
        print(f"Failed to convert video at {url.strip()}: {str(e)}")
