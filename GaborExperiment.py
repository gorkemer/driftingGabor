"""
Updated: 8 March 2019
Changed the program description to a more 'readable' version.

Program outputs peripherilly presented drifting Gabor Gratings in varying sizes.
Drifting gratings freeze at a randomly chosen frame for a duration of 30 frames.
Each "trial" consists of GRATING and BLANK "blocks", and each block consists of
3 "rounds", and each round is timed for 3 seconds, as denoted with roundTime variable. 
And, I've put 2 iterations, thus divided the round in to two, and named
them as first and second interval. 

--- old description below --- from 2016-2018


It runs n times with each trial has 2 condition (gabor vs blank)
lasting 12 seconds each. Also the size of the gabor (small or large) changes in each trial. In each trial gabor patch
have upwards motion inverting direction at 2 seconds interval.

Behavioral task: press a button based on at which side (left or right) did the gabor freeze?
    At each round (4 seconds) both left and right gabor patches freezes at random intervals
    and at random order (right then left vs left and right).

Things to add:
    -(done)Behavioral task at the fixation
    -when right and left freezeFrames interval are equal, it freezes right. Make it random
    -collect response, keyboard press
        check whether presentOrder matches with the key presses
    -data&log saving
    -add 24 sec blank period at the beginning
    -add trigger box '6' = input event.waitKeys(keyList = ['6'])

01 MART: TIPS FOR DATA: -1 means the gabor was presented at LEFT, +1 means it was at RIGHT
                        1 means correct, -1 means false response
                        the third column reports the key press
"""
from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, sound, gui
from psychopy.constants import *  # things like STARTED, FINISHED
import numpy as np # whole numpy lib is available, prepend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import sys
from random import choice, randrange, shuffle
from psychopy.tools.coordinatetools import pol2cart, cart2pol
import time
from psychopy.tools.filetools import fromFile, toFile
import psychopy.gui
import csv

globalClock = core.Clock()

#Data Handling
try: #try to get a previous parameters file
    expInfo = fromFile('lastParams.pickle')
except:#if not there then use a default set
    expInfo = {'observer':'','practice': 1} #add more if you want
expInfo['dateStr']= data.getDateStr() #add the current time
#present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Gabor', fixed=['dateStr'])

#make a text file to save data
fileName = expInfo['observer'] + expInfo['dateStr']

win = visual.Window([600, 480], units = 'deg', monitor = 'testMonitor', color = 'gray',fullscr=True) #'Berhan'
win.setRecordFrameIntervals(True)



#disply and experiment options
refRate = 60 # 1 second
second = refRate
nTrials = 12
stimDur = refRate * 12 # 12 seconds
roundTime = 4 * 60 # 1 round equals 4 seconds motion, inverting after 2 second
smallStim = 1.67
largeStim = 8.05
posX = 8
posY = 0
durInitialBlank = 24 * second

halfSecIntervalsFirst = [range(10,39), range(20,49), range(30,59), range(40,69),
                        range(50,79), range(60,89), range(70,99), range(80, 109)]

halfSecIntervalsSecond = [range(130, 159), range(140, 169), range(150, 179), range (160, 189),
                        range(170, 199), range(180, 209), range(190, 219), range(200, 229), range(210,239)]

responses = []
keyList = []
freezeSide = []
response = None

#stimuli initializing
fixation = visual.GratingStim(win, size=0.2, pos=[0,0], sf=0,color = 'black')
targetGabor = visual.GratingStim(win, mask='gauss', sf=1, name='gabor', contrast = 0.2, color = 1, size=largeStim, pos = (posX,posY), ori = 90)
foilGabor = visual.GratingStim(win, mask='gauss', sf=1, name='gabor', contrast = 0.2, color = 1, size=largeStim, pos = (posX,posY), ori = 90)


##TRIGGER BOX
if expInfo['practice'] == 0:
    event.waitKeys(keyList = ['6'])

    ##24 sec wait
    for times in range(durInitialBlank):
        fixation.draw()
        win.flip()

#### TRIAL LOOP ####
for trials in range(nTrials):
    t0 = time.time()
    if trials % 2 == 0:
        targetGabor.size = largeStim
        foilGabor.size = largeStim
    else:
        targetGabor.size = smallStim
        foilGabor.size = smallStim

    ### BLOCK (gabor followed by blank)LOOP ###
    for block in range(2):
        b0 = time.time()

        ### 3x rounds each comprised of upwards&downwards moving gabor ###
        for rounds in range(3):
            r0 = time.time()
            #randomizing location
            targetLocation = choice([1,-1])
            targetGabor.setPos([posX*targetLocation, posY])
            foilGabor.setPos([posX*-targetLocation, posY])

            firstFreezer = choice(halfSecIntervalsFirst)
            secondFreezer = choice(halfSecIntervalsSecond)
            #print secondFreezer

            #### FRAME LOOP ####
            for frames in range(roundTime): # 4 seconds at each round
                if block == 0:
                   ### GABOR CONDITION ###
                   if frames < roundTime/2: # 0-120 # freezing the target (aka, first)
                       if frames in firstFreezer:
                           foilGabor.setPhase(0.5,'+')
                       else:
                           targetGabor.setPhase(0.5,'+')
                           foilGabor.setPhase(0.5,'+')
                   else: # 120 - 240, # freezing the foil (second)
                       if frames in secondFreezer:
                           targetGabor.setPhase(0.5,'-')
                       else:
                           targetGabor.setPhase(0.5,'-')
                           foilGabor.setPhase(0.5,'-')
                   targetGabor.draw()
                   foilGabor.draw()
                ### BLANK CONDITION ###
                else:
                    pass
                fixation.draw()
                win.flip()

            #registering responses
            keys = event.getKeys(keyList=["1", "4", "escape"])
            for key in keys:
                if key == '4': #left 445
                    keyList.append(key)
                    if targetLocation == -1: #first freezer (target) was at the left side (minus)
                       response = '1'
                    else:
                       response = '-1'
                    responses.append(response)
                    freezeSide.append(targetLocation)

                elif key == '1':
                    keyList.append(key)
                    if targetLocation == 1: #targetGabor presented at the right side
                       response = '1'
                    else:
                       response = '-1'
                    responses.append(response)
                    freezeSide.append(targetLocation)
                elif key == 'escape':
                       win.close()
                       core.quit()
                else:
                    response = None

            r1 = time.time()
            roundLasts = r1-r0 # it should be 4 seconds
            #print "round lasts:", roundLasts
        b1 = time.time()
        #blockTime = t1-t0
    t1 = time.time()
    trialLast = t1-t0
    #print "trial Lasts:", trialLast

#print responses
#print freezeSide

rows = zip(freezeSide,responses, keyList)
with open(fileName + 'Gabor.csv', 'wb') as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow(row)

win.close()
core.quit()
