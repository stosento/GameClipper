import time
import re
import os
import shutil
import cv2
import math
import numpy as np
import PIL
from PIL import Image 
import pytesseract
import moviepy
from pytesseract import *
from moviepy.editor import *

def read_file(txt_file):
    times = []
    expression = '(0?[1-9]|1[0-9]):[0-5][0-9]'
    pattern = re.compile(expression)

    with open(txt_file, 'r') as f:
        for line in f:
            m = re.search(pattern, line)
            if (m):
                times.append(m.group())

    return times

def create_frame_dir():
    if not os.path.exists('image_frames'):
        os.makedirs('image_frames')
    else:
        shutil.rmtree('image_frames')
        os.makedirs('image_frames')

def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = Image.open(os.path.join(folder,filename))
        if img is not None:
            images.append(img)
    return images

def get_game_time(pattern, image):
    text = pytesseract.image_to_string(image,lang='eng')
    text = ' '.join(text.split())
    print(text)
    game_time = re.search(pattern, text)
    if (game_time):
        return game_time.group()
    else:
        return None

def get_sec(time_str):
    m, s = time_str.split(':')
    return int(m) * 60 + int(s)

def fast_forward(vidcap, time_diff, fps):
    curr_frame = int(vidcap.get(cv2.CAP_PROP_POS_FRAMES))
    new_frame = curr_frame + (time_diff * fps)
    print ("Curr_frame = ", curr_frame)
    print ("time_diff = ", time_diff)
    print ("new_frame = ", new_frame)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
    print('New Position:', int(vidcap.get(cv2.CAP_PROP_POS_FRAMES)))

def cut_clip(vidcap, game_time):
    print("Cuting the clip")
    clip = VideoFileClip("G14-Purdue-5min.mp4")

    vidcap_pos = (vidcap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
    start_ts = vidcap_pos - 7
    end_ts = vidcap_pos + 3

    clip = clip.subclip(start_ts, end_ts)
    filename = 'exp_' + game_time + '.mp4'
    clip.write_videofile(filename)

def create_clips(timestamps, videoFile):

    create_frame_dir()

    expression = '(0?[1-9]|1[0-9]):[0-5][0-9]'
    pattern = re.compile(expression)

    vidcap = cv2.VideoCapture(videoFile)
    success,image = vidcap.read()
    target_time = get_sec(timestamps.pop(0))
    time_diff = 0

    #Set to 5 seconds until we find a game time
    seconds = 5
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    multiplier = fps * seconds

    while success:
        frameId = int(round(vidcap.get(1)))
        success, image = vidcap.read()

        if frameId % multiplier == 0:
            game_time = get_game_time(pattern, image)
            
            if (game_time):
                print ("Found game time: ", game_time)
                game_time_sec = get_sec(game_time)
                
                if (game_time_sec == target_time):
                    print("Found time we want!", game_time)
                    #TODO - Cut video
                    cut_clip(vidcap, game_time)
                    target_time = get_sec(timestamps.pop(0))
                else:
                    multiplier = fps * 0.5 #We now have a game time, 
                
                time_diff = game_time_sec - target_time
                fast_forward(vidcap, time_diff, fps)

    vidcap.release()
    print("Complete")

def main():
    # Define the files to work with
    filename = 'timestamps.txt'
    video = 'G14-Purdue-5min.mp4'

    # Read the tiemstamps into a list
    timestamps = read_file(filename)

    # Create a clip for each timestamp
    create_clips(timestamps, video)

if __name__ == "__main__":
    main()