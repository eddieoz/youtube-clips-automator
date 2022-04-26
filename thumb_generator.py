# Import Libraries
from email.policy import default
import textwrap
from turtle import back
from sympy import true
import cv2
import time
import numpy as np
import time
from rembg import remove
from PIL import Image, ImageFont, ImageDraw 
import os, random
import argparse
import shutil


def find_smile(frame, text, count):
    # Load the cascade models
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    smile_cascade = cv2.CascadeClassifier("haarcascade_smile.xml")

    SCALE_FACTOR=40

    resizeimg = ''
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect the faces
    face = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in face:
        # Draw the rectangle around each face
        img = cv2.rectangle(frame, (x-SCALE_FACTOR, y-SCALE_FACTOR), (x+w+SCALE_FACTOR, y+h+SCALE_FACTOR), (255, 255, 255), 15)
        
        # Save image to detect smile
        croped_face = img[y-SCALE_FACTOR:y+h+SCALE_FACTOR, x-SCALE_FACTOR:x+w+SCALE_FACTOR]
        
        # print("[INFO] Face found. Saving locally.")
        # Store face
        # cv2.imwrite('./tmp/croped-'+str(count)+'.png', croped_face)

        if not isinstance(croped_face, (list, tuple, np.ndarray)) or croped_face is None:
            print('Failed to detect croped face')
            break
        
        # Display output
        # cv2.imshow('croped face', croped_face)
        
        img_gray = cv2.cvtColor(croped_face, cv2.COLOR_BGR2GRAY)
        
        if (not isinstance(img_gray, (list, tuple, np.ndarray)) or img_gray is None):
            print('Failed to detect face')
            break
        
        # Detect the smile
        smile = smile_cascade.detectMultiScale(img_gray, scaleFactor=1.8, minNeighbors=20)

        for x, y, w, h in smile:
            print("[INFO] Smile found. Saving locally.")
            # resize image
            resizeimg = cv2.resize(croped_face, (400, 400), interpolation = cv2.INTER_CUBIC)
            
            # Store smiling face
            # cv2.imwrite('./tmp/smiling-'+str(int(time.time()))+'.png', resizeimg)

            add_background(resizeimg, text)

def add_background(img, text):
    face = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(face)

    # merging files
    bg_dir = "./backgrounds/"
    mclogo = Image.open('./assets/mc.png')
    mclogo_width, mclogo_height = mclogo.size
    img1 = Image.new('RGBA', size=(700,700), color=(0, 0, 0, 0))
    
    img1.paste(img,(175,175))
    background = Image.open(bg_dir + random.choice(os.listdir(bg_dir)))
    W, H = (1280, 720)
    newimg = Image.new('RGBA', size=(W, H), color=(0, 0, 0, 0))

    # choose random to decide the side of image where face will be placed
    x = random.uniform(0, 1)

    if (x >= 0.5):
        img1 = img1.rotate(25)
    else:
        img1 = img1.transpose(method=Image.FLIP_LEFT_RIGHT)
        img1 = img1.rotate(-25)

    background = background.resize((W, H), Image.ANTIALIAS)
    newimg.paste(background,(0,0))
    
    if (x >= 0.5):
        newimg.paste(img1, (-120,-120), img1)
        newimg.paste(mclogo, (W-mclogo_width-5,5), mclogo)
    else:
        newimg.paste(img1, (W-700+120,-120), img1)
        newimg.paste(mclogo, (5,5), mclogo)
    add_text(newimg, W, H, text)

def add_text(bg, W, H, text):

    title_font = ImageFont.truetype('font/Arial_Black.ttf', 80)
    title_text = textwrap.fill(text, width=25)
    image_editable = ImageDraw.Draw(bg)

    # get text size
    w, h = image_editable.textsize(title_text, font=title_font)
    # write text in the middle
    image_editable.text(((W-w)/2,(H-h)-75), title_text, (255, 255, 255), font=title_font, stroke_width=10,stroke_fill=(0,0,0))
    save_thumbnail(bg)

def save_thumbnail(img):
    img.save('./thumbs/thumb-'+str(int(time.time()))+'.png',"PNG")

def remove_background(img):
    rembg = remove(img)
    return (rembg)

def draw_border(img):
    img2 = img.copy()            
    resizegray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(resizegray, 0, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img, contours, -1, (255,255,255), 8)
    return (img)

def create_thumbnail(img_path, text, clear_thumbs:bool=True):

    if clear_thumbs == True: remove_thumbs()

    video = cv2.VideoCapture(img_path)

    check = True
    count = 0
    while check:
        
        # check if there are enough thumbs then exit
        if (len(os.listdir('./thumbs')) > 10): break

        # Read the frame
        check, frame = video.read()
        if not check:
            #print("Stream end? Exiting...")
            break

        if not isinstance(frame, (list, tuple, np.ndarray)):
            #print("Frame not identified? Exiting...")
            break

        # 30 fps video, then checking for smile each n frames
        if (count >= 5): count = 0
        if (count == 0): 
            face = find_smile(frame,text, count)  
        
        count += 1

        # Display output
        #cv2.imshow('smile detect', frame)

        # Stop if escape key is pressed
        key = cv2.waitKey(30) & 0xff
        if key == 27:
            break

    # Release the VideoCapture object
    video.release()
    cv2.destroyAllWindows()
    return

def remove_thumbs():
    # remove previous thumbs
    dir = './thumbs'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))
    
def copy_thumbs(title):
    dir = './thumbs'
    newdir = title.replace(' ','_')
    shutil.copytree(dir, newdir, dirs_exist_ok=True)


def main(input: str, title: str, delete_thumbs: bool=True):
    create_thumbnail(input, title, delete_thumbs)
    copy_thumbs(title)

def str2bool(value):
    return value.lower() == 'true'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find a smiling face on image or video and generate a random thumbnail')
    parser.add_argument(
        "-i",
        "--input",
        help="Video input file.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-t",
        "--title",
        help="Video title description",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-d",
        "--no_delete_thumbs",
        type=str2bool,
        default = True,
        help="Delete previous Thumbs",
    )
    args = parser.parse_args()
    
    main(args.input, args.title, args.no_delete_thumbs)