import time
import re
import os
from cv2 import cv2

def read_file(txt_file):
    times = []
    expression = '^(0?[1-9]|1[0-9]):[0-5][0-9]'
    pattern = re.compile(expression)

    with open(txt_file, 'r') as f:
        for line in f:
            m = re.search(pattern, line)
            if (m):
                times.append(m.group())

    return times

def create_clips(timestamps, video):

    if not os.path.exists('img_frames'):
        os.makedirs('image_frames')

    test_vid = cv2.VideoCapture(video)

    prev_time = timestamps[0]
    time_diff = 0

    for time in timestamps:
        #Grab screenshot from video

        #Convert text from screenshot

        #See if screenshot contains 'time'


        print(time)

def main():
    # Define the files to work with
    filename = 'timestamps.txt'
    video = 'testvid.mp4'

    # Read the tiemstamps into a list
    timestamps = read_file(filename)

    # Create a clip for each timestamp
    create_clips(timestamps, video)

if __name__ == "__main__":
    main()