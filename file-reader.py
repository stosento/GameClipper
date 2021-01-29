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
import enum

# Using enum class create enumerations
class SEARCH_MODE(enum.Enum):
   FIND_GAME_TIME = 1
   USE_DIFF = 2

#Global Variables
video_file = 'G14-Purdue-5min.mp4'
text_file = 'timestamps.txt'
game_words = ['Michigan', 'Purdue', 'FS1', 'fsi', 'half']

file_expression = '(0?[1-9]|1[0-9]):[0-5][0-9]'
video_expression = '\s(0?[1-9]|1[0-9]):[0-5][0-9]'
f_pattern = re.compile(file_expression)
v_pattern = re.compile(video_expression)

exp_dir = 'exp_clips'

fps = 30
frame_msec = 0

def read_file(txt_file):
    times = []

    with open(txt_file, 'r') as f:
        for line in f:
            m = re.search(f_pattern, line)
            if (m):
                times.append(m.group())

    return times

def create_clip_dir():
    if not os.path.exists(exp_dir):
        os.makedirs(exp_dir)
    else:
        shutil.rmtree(exp_dir)
        os.makedirs(exp_dir)

def is_game_screen(game_words, search_text):
    for word in game_words:
        if word.lower() in search_text.lower():
            return True
    return False

def get_game_time(pattern, image):
    time = None
    
    if (image.any()):
        text = pytesseract.image_to_string(image,lang='eng')
        text = ' '.join(text.split())
        print(text)
        game_time = re.search(pattern, text)
        if (game_time and is_game_screen(game_words, text)):
            time = game_time.group()

    return time

def get_sec(time_str):
    m, s = time_str.split(':')
    return int(m) * 60 + int(s)

def move_playhead(vidcap, time_diff, mode):
    curr_time = vidcap.get(cv2.CAP_PROP_POS_MSEC)

    if (mode == SEARCH_MODE.FIND_GAME_TIME):
        if (time_diff >= 0):
            skip_time = 1
        elif (time_diff < 0):
            skip_time = -1

        if (abs(time_diff) <= 2):
            skip_time *= (1/6)

    elif (mode == SEARCH_MODE.USE_DIFF):
        skip_time = time_diff
        
    new_time = curr_time + (skip_time * 1000)
    print ("Current time : ", curr_time / 1000)
    print ("time_diff : ", time_diff)
    vidcap.set(cv2.CAP_PROP_POS_MSEC, new_time)
    print( 'Set New Position to : ', (new_time / 1000))

def cut_clip(vidcap, game_time):
    clip = VideoFileClip("G14-Purdue-5min.mp4")

    vidcap_pos = (vidcap.get(cv2.CAP_PROP_POS_MSEC) / 1000)

    #TODO - make this configurable
    start_ts = vidcap_pos - 7
    end_ts = vidcap_pos + 3

    clip = clip.subclip(start_ts, end_ts)
    filename = exp_dir + '/exp_' + game_time.strip() + '_' + str(int(vidcap_pos)) + '.mp4'
    clip.write_videofile(filename)

def create_clips(timestamps, videoFile):

    # Set up the directory for our exports
    create_clip_dir()

    # Create our video capture object
    vidcap = cv2.VideoCapture(videoFile)
    success,image = vidcap.read()
    
    # Set up the initial target time
    target_time = get_sec(timestamps.pop(0))
    time_diff = 0
    
    # How many MS per frame
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_msec = 1000 / fps

    # Set our mode to search for game time
    mode = SEARCH_MODE.FIND_GAME_TIME

    while success:
        # Read in frame
        success, image = vidcap.read()
        print("Position: " + str(vidcap.get(cv2.CAP_PROP_POS_MSEC) / 1000))

        # Parse the time from the image ex. 19:34
        game_time = get_game_time(v_pattern, image)

        if (game_time):
            print ("Found game time: ", game_time)
            
            mode = SEARCH_MODE.USE_DIFF

            #Convert our timestamp (19:34) to seconds (543)
            game_time_sec = get_sec(game_time)

            if (game_time_sec == target_time):
                print("Matched time: ", game_time)
                cut_clip(vidcap, game_time)
                target_time = get_sec(timestamps.pop(0))
            
            #Calculate the difference needed to get to target
            time_diff = game_time_sec - target_time
                
        else:
            mode = SEARCH_MODE.FIND_GAME_TIME
                
        move_playhead(vidcap, time_diff, mode)
        print ("\n")

    vidcap.release()
    print("Complete")

def main():

    # Read the tiemstamps into a list
    timestamps = read_file(text_file)

    # Create a clip for each timestamp
    create_clips(timestamps, video_file)

if __name__ == "__main__":
    main()