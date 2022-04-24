#####
## Original jumpcutter: https://github.com/carykh/jumpcutter
## Created by @carykh
## Modified by @eddieoz
#####

from contextlib import closing
from PIL import Image
import subprocess

from sympy import arg
from audiotsm import phasevocoder
from audiotsm.io.wav import WavReader, WavWriter
from scipy.io import wavfile
import numpy as np
import re
import math
from shutil import copyfile, rmtree
import os
from os.path import exists
import argparse
from pytube import YouTube
import sys
from thumb_generator import create_thumbnail
import shutil

## NVIDIA CUDA ffmpeg -hwaccel cuda -hwaccel_output_format cuda
## ref: https://docs.nvidia.com/video-technologies/video-codec-sdk/ffmpeg-with-nvidia-gpu/

TEMP_FOLDER = "TEMP"

def downloadFile(url, title):
    print('Dowloading file if it does not exist...')
    yt = YouTube(url).streams

    # retrieve the max resolution found on YouTube
    itag, frame_size, frame_rate = max_resolution(yt)
    name = yt.get_by_itag(itag).download(max_retries=5, skip_existing=True)
    print('Downloaded ' + name)

    print('Exists? '+str(os.path.exists(name)))
    newname = title.replace(' ','_')+'.mp4'
    print('Renaming '+name+' to '+newname)
    
    # os.rename(name,newname)
    shutil.copyfile(name, newname)
    
    return newname, frame_rate, frame_size

def max_resolution(yt):
    frame_rate = 30
    res = 720
    frame_size = ''
    itag = ''
    itag_audio = 0

    for i in yt:
        # print(i)
        if ((i.is_dash == False) and (i.resolution != None) and int(i.resolution[:-1]) >= res):
            if (i.resolution == '720p' and i.fps >= frame_rate):
                frame_size = '1280:720'
                itag = i.itag
                frame_rate = i.fps
                adaptive = i.is_dash
            
            if (i.resolution == '1080p' and i.fps >= frame_rate):
                frame_size = '1920:1080'
                itag = i.itag
                frame_rate = i.fps
                adaptive = i.is_dash

            res = int(i.resolution[:-1])
            # print ('Selected %s' % (str(res)))

    print("Found video itag: %s, frame: %s, frame rate: %s" % (str(itag), frame_size, str(frame_rate)))
    
    return (itag, frame_size, frame_rate)    

def getMaxVolume(s):
    maxv = float(np.max(s))
    minv = float(np.min(s))
    return max(maxv,-minv)

def copyFrame(inputFrame,outputFrame):
    
    src = TEMP_FOLDER+"/frame{:06d}".format(inputFrame+1)+".jpg"
    dst = TEMP_FOLDER+"/newFrame{:06d}".format(outputFrame+1)+".jpg"
    
    if not os.path.isfile(src):
        return False
    copyfile(src, dst)
    if outputFrame%20 == 19:
        print(str(outputFrame+1)+" time-altered frames saved.")
    return True


def inputToOutputFilename(filename):
    dotIndex = filename.rfind(".")
    return filename[:dotIndex]+"_ALTERED"+filename[dotIndex:]

def inputToCutFilename(filename):
    dotIndex = filename.rfind(".")
    return filename[:dotIndex]+"_CUT"+filename[dotIndex:]

def createPath(s):
    #assert (not os.path.exists(s)), "The filepath "+s+" already exists. Don't want to overwrite it. Aborting."

    try:  
        os.mkdir(s)
    except OSError:  
        assert False, "Creation of the directory %s failed. (The TEMP folder may already exist. Delete or rename it, and try again.)"

def deletePath(s): # Dangerous! Watch out!
    try:  
        rmtree(s,ignore_errors=False)
    except OSError:  
        print ("Deletion of the directory %s failed" % s)
        print(OSError)

parser = argparse.ArgumentParser(description='Modifies a video file to play at different speeds when there is sound vs. silence.')
parser.add_argument('--input_file', type=str,  help='the video file you want modified')
parser.add_argument('--url', type=str, help='A youtube url to download and process')
parser.add_argument('--output_file', type=str, default="", help="the output file. (optional. if not included, it'll just modify the input file name)")
parser.add_argument('--silent_threshold', type=float, default=0.03, help="the volume amount that frames' audio needs to surpass to be consider \"sounded\". It ranges from 0 (silence) to 1 (max volume)")
parser.add_argument('--sounded_speed', type=float, default=1.00, help="the speed that sounded (spoken) frames should be played at. Typically 1.")
parser.add_argument('--silent_speed', type=float, default=5.00, help="the speed that silent frames should be played at. 999999 for jumpcutting.")
parser.add_argument('--frame_margin', type=float, default=1, help="some silent frames adjacent to sounded frames are included to provide context. How many frames on either the side of speech should be included? That's this variable.")
parser.add_argument('--sample_rate', type=float, default=44100, help="sample rate of the input and output videos")
parser.add_argument('--frame_rate', type=float, default=30, help="frame rate of the input and output videos. optional... I try to find it out myself, but it doesn't always work.")
parser.add_argument('--frame_quality', type=int, default=3, help="quality of frames to be extracted from input video. 1 is highest, 31 is lowest, 3 is the default.")
parser.add_argument('--from_time', type=str, help="extract video starting from this time.")
parser.add_argument('--to_time', type=str, help="extract video ending to this time.")
parser.add_argument('--title', type=str, help="Video title for filename")

args = parser.parse_args()


createPath(TEMP_FOLDER)

frameRate = args.frame_rate
FRAME_SIZE = '1920:1080'
SAMPLE_RATE = args.sample_rate
SILENT_THRESHOLD = args.silent_threshold
FRAME_SPREADAGE = args.frame_margin
NEW_SPEED = [args.silent_speed, args.sounded_speed]
if args.url != None:
    INPUT_FILE, frameRate, FRAME_SIZE = downloadFile(args.url, args.title)
else:
    INPUT_FILE = args.input_file
URL = args.url
FRAME_QUALITY = args.frame_quality

# Force re-scale (not the original video size defined by parameter)
FRAME_SIZE = '1920:1080'

assert INPUT_FILE != None , "why u put no input file, that dum"
    
if len(args.output_file) >= 1:
    OUTPUT_FILE = args.output_file
else:
    OUTPUT_FILE = inputToOutputFilename(INPUT_FILE)

if args.to_time != None:
    assert args.from_time != None , 'if you are cutting a video, use --from_time AND --to_time'
if args.from_time != None:
    assert args.to_time != None , 'if you are cutting a video, use --from_time AND --to_time'


# if has a cut time, then cut the video before editing
if args.from_time != None and args.to_time != None:
    CUT_FILE = inputToCutFilename(INPUT_FILE)
    command = "ffmpeg -y -i "+INPUT_FILE+" -vf scale="+FRAME_SIZE+" -qscale:v "+str(FRAME_QUALITY)+" -b:v 6000k -ss "+str(args.from_time)+" -to "+str(args.to_time)+" "+CUT_FILE+""
    subprocess.call(command, shell=True)
    INPUT_FILE = CUT_FILE

AUDIO_FADE_ENVELOPE_SIZE = 400 # smooth out transition's audio by quickly fading in/out (arbitrary magic number whatever)
    
# split frames
command = "ffmpeg -i "+INPUT_FILE+" -vf scale="+FRAME_SIZE+" -qscale:v "+str(FRAME_QUALITY)+" -b:v 6000k "+TEMP_FOLDER+"/frame%06d.jpg -hide_banner"
subprocess.call(command, shell=True)

# split audio
command = "ffmpeg -i "+INPUT_FILE+" -ab 160k -ac 2 -ar "+str(SAMPLE_RATE)+" -vn "+TEMP_FOLDER+"/audio.wav"
subprocess.call(command, shell=True)

command = "ffmpeg -i "+TEMP_FOLDER+"/input.mp4 -vf scale="+FRAME_SIZE+" 2>&1"
f = open(TEMP_FOLDER+"/params.txt", "w")
subprocess.call(command, shell=True, stdout=f)



sampleRate, audioData = wavfile.read(TEMP_FOLDER+"/audio.wav")
audioSampleCount = audioData.shape[0]
maxAudioVolume = getMaxVolume(audioData)

f = open(TEMP_FOLDER+"/params.txt", 'r+')
pre_params = f.read()
f.close()
params = pre_params.split('\n')
for line in params:
    m = re.search('Stream #.*Video.* ([0-9]*) fps',line)
    if m is not None:
        frameRate = float(m.group(1))

samplesPerFrame = sampleRate/frameRate

audioFrameCount = int(math.ceil(audioSampleCount/samplesPerFrame))

hasLoudAudio = np.zeros((audioFrameCount))



for i in range(audioFrameCount):
    start = int(i*samplesPerFrame)
    end = min(int((i+1)*samplesPerFrame),audioSampleCount)
    audiochunks = audioData[start:end]
    maxchunksVolume = float(getMaxVolume(audiochunks))/maxAudioVolume
    if maxchunksVolume >= SILENT_THRESHOLD:
        hasLoudAudio[i] = 1

chunks = [[0,0,0]]
shouldIncludeFrame = np.zeros((audioFrameCount))
for i in range(audioFrameCount):
    start = int(max(0,i-FRAME_SPREADAGE))
    end = int(min(audioFrameCount,i+1+FRAME_SPREADAGE))
    shouldIncludeFrame[i] = np.max(hasLoudAudio[start:end])
    if (i >= 1 and shouldIncludeFrame[i] != shouldIncludeFrame[i-1]): # Did we flip?
        chunks.append([chunks[-1][1],i,shouldIncludeFrame[i-1]])

chunks.append([chunks[-1][1],audioFrameCount,shouldIncludeFrame[i-1]])
chunks = chunks[1:]

outputAudioData = np.zeros((0,audioData.shape[1]))
outputPointer = 0

lastExistingFrame = None
for chunk in chunks:
    audioChunk = audioData[int(chunk[0]*samplesPerFrame):int(chunk[1]*samplesPerFrame)]
    
    sFile = TEMP_FOLDER+"/tempStart.wav"
    eFile = TEMP_FOLDER+"/tempEnd.wav"
    wavfile.write(sFile,SAMPLE_RATE,audioChunk)
    with WavReader(sFile) as reader:
        with WavWriter(eFile, reader.channels, reader.samplerate) as writer:
            tsm = phasevocoder(reader.channels, speed=NEW_SPEED[int(chunk[2])])
            tsm.run(reader, writer)
    _, alteredAudioData = wavfile.read(eFile)
    leng = alteredAudioData.shape[0]
    endPointer = outputPointer+leng
    outputAudioData = np.concatenate((outputAudioData,alteredAudioData/maxAudioVolume))

    #outputAudioData[outputPointer:endPointer] = alteredAudioData/maxAudioVolume

    # smooth out transitiion's audio by quickly fading in/out
    
    if leng < AUDIO_FADE_ENVELOPE_SIZE:
        outputAudioData[outputPointer:endPointer] = 0 # audio is less than 0.01 sec, let's just remove it.
    else:
        premask = np.arange(AUDIO_FADE_ENVELOPE_SIZE)/AUDIO_FADE_ENVELOPE_SIZE
        mask = np.repeat(premask[:, np.newaxis],2,axis=1) # make the fade-envelope mask stereo
        outputAudioData[outputPointer:outputPointer+AUDIO_FADE_ENVELOPE_SIZE] *= mask
        outputAudioData[endPointer-AUDIO_FADE_ENVELOPE_SIZE:endPointer] *= 1-mask

    startOutputFrame = int(math.ceil(outputPointer/samplesPerFrame))
    endOutputFrame = int(math.ceil(endPointer/samplesPerFrame))
    for outputFrame in range(startOutputFrame, endOutputFrame):
        inputFrame = int(chunk[0]+NEW_SPEED[int(chunk[2])]*(outputFrame-startOutputFrame))
        didItWork = copyFrame(inputFrame,outputFrame)
        if didItWork:
            lastExistingFrame = inputFrame
        else:
            copyFrame(lastExistingFrame,outputFrame)

    outputPointer = endPointer

wavfile.write(TEMP_FOLDER+"/audioNew.wav",SAMPLE_RATE,outputAudioData)

'''
outputFrame = math.ceil(outputPointer/samplesPerFrame)
for endGap in range(outputFrame,audioFrameCount):
    copyFrame(int(audioSampleCount/samplesPerFrame)-1,endGap)
'''

# write the output video
command = "ffmpeg -y -framerate "+str(frameRate)+" -i "+TEMP_FOLDER+"/newFrame%06d.jpg -i "+TEMP_FOLDER+"/audioNew.wav -metadata handler_name='Produzido por @EddieOz youtube.com/eddieoz' -qscale:v "+str(FRAME_QUALITY)+" -b:v 6000k -strict -2 -vf scale="+FRAME_SIZE+" "+OUTPUT_FILE
subprocess.call(command, shell=True)

deletePath(TEMP_FOLDER)
