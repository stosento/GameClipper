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
from moviepy.editor import *
import enum
import argparse
import pathlib
from pathlib import Path
import configparser

# Set up pytesseract
def is_Windows():
    val = False
    if os.name == 'nt':
        val = True
    return val

if is_Windows():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:
    from pytesseract import *

# Using enum class create enumerations
class SEARCH_MODE(enum.Enum):
   FIND_GAME_TIME = 1
   USE_DIFF = 2
   SKIP_INTERMISSION = 3

# Global Variables
video_file = 'G13-Mary-GAME.mp4'
text_file = 'timestamps-maryland.txt'
game_words = ['Michigan', 'Maryland', 'FS1', 'fsi', 'half']
exp_dir = 'exp_clips'

file_expression = '(0?[1-9]|1[0-9]):[0-5][0-9]'
file_expression_zero = '0:[0-5][0-9]'
video_expression_zero = ':[0-5][0-9]'
decimal_expression = '[0-5][0-9]\.[0-9]'

f_pattern = re.compile(file_expression)
f0_pattern = re.compile(file_expression_zero)
v0_pattern = re.compile(video_expression_zero)
dec_pattern = re.compile(decimal_expression)

fps=60
frame_msec=0

box_x1=0
box_x2=0
box_y1=0
box_y2=0

time_box_defined = False
period = 1

def read_args():

    parser = argparse.ArgumentParser()

    #-s STARTTIME
    parser.add_argument("-s", "--starttime", dest = "starttime", default = None, help="Start time")
    #-t TEST
    parser.add_argument("-t", "--test", dest = "test", default = None, help = "Test time")

    return parser.parse_args()

def read_file(txt_file, starttime):
    times = []
    checkstart = False
    paststart = True

    if starttime:
        checkstart = True
        paststart = False

    with open(txt_file, 'r') as f:
        for line in f:
            m = re.search(f_pattern, line)
            m0 = re.search(f0_pattern, line)
            if (m or m0):
                if m:
                    m_string = m.group()
                else:
                    m_string = m0.group()
                if checkstart:
                    if m_string == starttime:
                        checkstart = False
                        paststart = True
                if paststart:
                    times.append(m_string)

    print("timestamps:", times)
    return times

def create_clip_dir(starttime):
    if os.path.exists(exp_dir) and not starttime:
        shutil.rmtree(exp_dir)
        os.makedirs(exp_dir)
    elif not os.path.exists(exp_dir):
        os.makedirs(exp_dir)

def is_game_screen(game_words, search_text):
    print("Search_text:", search_text)
    print("game_words:", game_words)
    for word in game_words:
        if word.lower() in search_text.lower():
            return True
    return False

def run_test(time_str):

    # Create our video capture object
    vidcap = cv2.VideoCapture(video_file)
    
    # How many MS per frame
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    global frame_msec
    frame_msec = 1000 / fps

    # Convert the input timestamp to ms
    total_msec = convert_long_timestamp(time_str)

    # Move to the position we are interested in
    vidcap.set(cv2.CAP_PROP_POS_MSEC,total_msec)
    success,image = vidcap.read()

    # Print our non-cropped image
    cv2.imwrite('test.png', image)

    # Read in the box coordinates
    box_x1 = 1352
    box_x2 = 1472
    box_y1 = 917
    box_y2 = 978

    # Take the cropped image
    crop_image = image[box_y1:box_y2, box_x1:box_x2]

    # Print our cropped image
    cv2.imwrite('test-crop.png', crop_image)

    # Call get_image_text() to appropriately transform it
    get_image_text(crop_image, True)


def get_image_text(image, save_image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted = np.invert(image)

    text = pytesseract.image_to_string(inverted,lang='eng',config='--psm 10 --oem 3')
    text = ' '.join(text.split())

    if save_image:
        print("Printing test image - CROPPED")
        cv2.imwrite('test-transformed.png', inverted)
    return text

def define_timebox_coords(image, game_time):
    screen_info = pytesseract.image_to_boxes(image)
    time_chars = list(game_time)
    time_len = len(game_time)

    global time_box_defined

    lines = screen_info.splitlines()
    i=0
    j=1
    buffer = 20
    match = False

    height, width, channels = image.shape

    print("Checking coords for timebox")
    print("time_chars: ", time_chars)
    for line in lines:
        if (line[0] == time_chars[0]):
            print("Match of first character")
            match = True
            while (j < time_len):
                print("j:", j)
                print("lines[i+j][0]:", lines[i+j][0])
                print("time_chars[j]:", time_chars[j])
                if (lines[i+j][0] != time_chars[j]):
                    match = False
                    j = 1
                    break
                j += 1
            if (match):
                print("Setting box coordinates")
                #set our coordinates
                test = lines[i].split()

                global box_x1, box_x2, box_y1, box_y2

                box_x1 = int(lines[i].split()[1]) - buffer
                box_x2 = int(lines[i+j-1].split()[3]) + buffer

                box_y1 = height - int(lines[i+j-1].split()[4]) - buffer
                box_y2 = height - int(lines[i].split()[2]) + buffer

                print("box_x1:", box_x1)
                print("box_x2:", box_x2)
                print("box_y1", box_y1)
                print("box_y2", box_y2)
                
                time_box_defined = True
                
                break

        i += 1
    return time_box_defined

def get_game_time(pattern, pattern0, dec_pattern, image):
    time = None
    global time_box_defined
    
    if (image.any()):

        if (time_box_defined):
            image = image[box_y1:box_y2, box_x1:box_x2]
            text = get_image_text(image, False)
            print("text:", text)
            game_time = re.search(pattern, text)
            game_time_0 = re.search(pattern0, text)
            game_time_dec = re.search(dec_pattern, text)
            print("game_time:", game_time)
            if game_time:
                game_time = game_time.group().strip()
                game_screen = f_pattern.match(game_time)
            elif game_time_0:
                game_time = game_time_0.group().strip()
                game_screen = v0_pattern.match(game_time)
            elif game_time_dec:
                game_time = game_time_dec.group().strip()
                game_screen = dec_pattern.match(game_time)
            else:
                game_screen = False
        else :
            print("time box not defined")
            text = pytesseract.image_to_string(image,lang='eng')
            text = ' '.join(text.split())
            print("text:", text)
            game_time = re.search(pattern, text)
            game_time_0 = re.search(pattern0, text)
            game_time_dec = re.search(dec_pattern, text)
            print("game_time:", game_time)
            if game_time:
                game_time = game_time.group().strip()
                print("text:", text)
            elif game_time_0:
                game_time = game_time_0.group().strip()
            elif game_time_dec:
                game_time = game_time_dec.group().strip()
            game_screen = is_game_screen(game_words, text)
            print("game_screen:", game_screen)

        if (game_time and game_screen):
            time = game_time

            if (not time_box_defined):
                time_box_defined = define_timebox_coords(image, time)

    return time

def get_str(time_sec):

    time_msec = time_sec * 1000
    total_frames = time_msec / frame_msec
    fph = fps**3
    fpm = fps**2

    hours_int = int(total_frames / fph)
    total_frames = total_frames - (hours_int*fph)

    minutes_int = int(total_frames / fpm)
    total_frames = total_frames - (minutes_int*fpm)

    seconds_int = int(total_frames / fps)
    frames = total_frames - (seconds_int*fps)

    return '%02d:%02d:%02d:%02d' % (hours_int, minutes_int, seconds_int, int(frames))

def get_sec(time_str):
    if (':' in time_str):
        m, s = time_str.split(':')
    else:
        m = None
        s = int(float(time_str))
    if m and s:
        total_sec = int(m) * 60 + int(s)
    else:
        total_sec = int(s)
    return total_sec

def convert_long_timestamp(time_str):
    global frame_msec
    h,m,s,f = time_str.split(':')

    h_msec = int(h) * 3600 * 1000
    m_msec = int(m) * 60 * 1000
    s_msec = int(s) * 1000
    f_msec = int(f) * frame_msec

    total_sec = h_msec + m_msec + s_msec + f_msec

    return total_sec

def escape_filename(filename):
    return filename.replace(":", "-")

def move_playhead(vidcap, time_diff, mode, prev_time, count):
    curr_time = vidcap.get(cv2.CAP_PROP_POS_MSEC)

    if (mode == SEARCH_MODE.FIND_GAME_TIME):
        if (time_diff >= 0):
            skip_time = 1/6
        elif (time_diff < 0):
            skip_time = -(1/6)

        if count >= 10:
            skip_time = skip_time * (count / 10)

    elif (mode == SEARCH_MODE.USE_DIFF):
        skip_time = time_diff
        if (abs(time_diff) <= 2):
            skip_time *= (1/6)
        if (skip_time < 0):
            skip_time -= 1

    elif (mode == SEARCH_MODE.SKIP_INTERMISSION):
        skip_time = prev_time + (60*30)

    new_time = curr_time + (skip_time * 1000)
    print ("skip_time : ", skip_time)
    vidcap.set(cv2.CAP_PROP_POS_MSEC, new_time)

def cut_clip(vidcap, game_time):
    clip = VideoFileClip(video_file)

    vidcap_pos = (vidcap.get(cv2.CAP_PROP_POS_MSEC) / 1000)

    #TODO - make this configurable
    start_ts = vidcap_pos - 7
    end_ts = vidcap_pos + 3

    clip = clip.subclip(start_ts, end_ts)
    filename = os.path.join(exp_dir, 'P' + str(period) + '_' + game_time.strip() + '_' + get_str(vidcap_pos) + '.mp4')
    escaped_filename = escape_filename(filename)
    clip.write_videofile(escaped_filename, temp_audiofile='temp.mp3')

def create_clips(timestamps, videoFile):

    # Create our video capture object
    vidcap = cv2.VideoCapture(videoFile)
    vidcap.set(cv2.CAP_PROP_POS_MSEC, 60*9*1000)
    success,image = vidcap.read()
    
    # Set up the initial target time
    target_time = get_sec(timestamps.pop(0))
    time_diff = 10
    prev_time = 0
    
    # How many MS per frame
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    print(fps)
    global frame_msec
    frame_msec = 1000 / fps

    # Set our mode to search for game time
    mode = SEARCH_MODE.FIND_GAME_TIME
    count = 0

    global time_box_defined
    global period

    while success:
        # Read in frame
        success, image = vidcap.read()
        pos = get_str(vidcap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
        print("Position: " + pos)
        print("Count: " + str(count))
        # Parse the time from the image ex. 19:34
        game_time = get_game_time(f_pattern, v0_pattern, dec_pattern, image)

        if (pos == '00:18:22:07'):
            print("Printing test image")
            cv2.imwrite('test.png', image)

        if (game_time):
            print ("Found game time: ", game_time)
            
            mode = SEARCH_MODE.USE_DIFF

            #Convert our timestamp (19:34) to seconds (543)
            game_time_sec = get_sec(game_time)

            if (game_time_sec == target_time):
                print("Matched time: ", game_time)
                cut_clip(vidcap, game_time)
                prev_time = target_time
                target_time = get_sec(timestamps.pop(0))
                
                if (target_time > prev_time):
                    mode = SEARCH_MODE.SKIP_INTERMISSION
                    period += 1
            
            #Calculate the difference needed to get to target
            time_diff = game_time_sec - target_time
            count=0
                
        else:
            mode = SEARCH_MODE.FIND_GAME_TIME
            count += 1

        move_playhead(vidcap, time_diff, mode, prev_time, count)
        print ("\n")

    vidcap.release()
    print("Complete")

def main():

    # Read in command line arguments
    args = read_args()

    if args.test:
        run_test(args.test)

    else:
        # Set up the directory for our exports
        create_clip_dir(args.starttime)

        # Read the tiemstamps into a list
        timestamps = read_file(text_file, args.starttime)

        # Create a clip for each timestamp
        create_clips(timestamps, video_file)



if __name__ == "__main__":
    main()