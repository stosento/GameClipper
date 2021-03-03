# GameClipper

A python application to edit game footage into meaningful highlights.

Key Libraries: PyTesseract, OpenCV, MoviePy

## Background ##

If you've seen any of my work at MGoFish or MaizenBrew over the past few years, you'd know I edit a LOT of videos. I've updated the process throughout the years to speed up the process, but it usually goes like this:
1. Watch the game with my laptop, Notes open and at the ready
2. Take down important plays / highlights throughout the game
3. Go through the full game footage, cutting to the notes from my original watch.

This process is tedious and takes not only the hours to watch the game and energy to take the notes, but THEN going into Adobe Premiere Pro to cut the footage according to those notes.

On average, I would say the editing process takes anywhere from 30min-1hour, depending on how focused I am and/or how many highlights I jot down.

## Automating the Process ##

About 3 years later than I should have, I had the bright idea to look into OCR technology and how viable it would be to use my notes to cut the footage for me. After all, the notes had the *context* I needed, all I needed was to properly read the footage intelligently.

The approach can mainly be split up into a few steps:
1. Read in the text file into a list of timestamps that we need to find
2. Open the video file and find a meaningful game clock within the frame, save those coordinates 
3. With those coordinates, cycle through the footage to find the matching time to the first timestamp on our list from our notes.
4. Cut / Export the highlight around that time and move on to the next time in the list

Voila! If done perfectly, it still takes about 45 minutes (timestamp search & video exporting takes some time), but it frees me up to do other things while the program does the dirty work!

## How to run the Program ##

So, there are multiple flags / runtime options to run this. It's not perfect and definitely is still a WIP. Let's start with some assumptions:

### Assumptions ###
1. You have the entire game footage within a single video file. I haven't set-up the capability to set multiple video files, since that's kind of silly.
2. Your timestamp file only has one timestamp per line.
3. The timestamp actually exists on the game footage.
