import csv
import os
import random
import shutil
import subprocess
import sys
from youtube_uploader_selenium import YouTubeUploader
from datetime import datetime
import time

def upload_video(video_path, url, title, description, tags, thumb_path):
    
    metadata_path = './metadata.json'
    now = datetime.now() # current date and time

    description = str(description)+ \
    '\\n\\n-- Episodio completo: '+str(url)+ \
    '\\n-- Todos os dias 8am ao vivo em https://www.twitch.tv/eddieoztv'

    # youtubeuploader metadata
    metadata = '{ "title": "'+str(title)+'", \
    "description": "'+description+'", \
    "tags": ["'+str(tags).replace(' ','","')+'"], \
    "privacyStatus": "private", \
    "madeForKids": false, \
    "embeddable": true, \
    "license": "creativeCommon", \
    "publicStatsViewable": true, \
    "publishAt": "'+str(now.strftime("%Y-%m-%dT%H:%M:%S+03:00"))+'", \
    "categoryId": "28", \
    "playlistTitles": ["Cortes Morning Crypto"], \
    "language": "pt-BR" }'

    with open(metadata_path, 'w') as f:
        f.write(metadata)
        f.close()
    
    # Upload video to Youtube
    command = "./youtubeuploader -filename "+video_path+" -metaJSON "+metadata_path+" -thumbnail "+thumb_path+""
    output_file = subprocess.call(command, shell=True)
    if (output_file != 0): exit(1)

def thumb_generator(file, title):
    print('Generating thumbnails...')
    bg_dir = './thumbs/'
            
    # if sucessfully copy the frame, check and create thumbnail
    command = "python ./thumb_generator.py --input './assets/default_face.png' --title '"+title+"'"
    output_file = subprocess.call(command, shell=True)
    
    command = "python ./thumb_generator.py --input "+file+" --title '"+title+"' -d False"
    output_file = subprocess.call(command, shell=True)
    
    if (len(os.listdir(bg_dir)) >= 1):
        bg = random.choice(os.listdir(bg_dir))
        return (bg_dir+bg)
    else:
        exit(1)

def move_files(title):
    files = title.replace(' ','_')
    command = "mv "+files+"*.mp4 "+files+"/"
    output_file = subprocess.call(command, shell=True)

def main():
    with open('list.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')

        try:
            header = next(reader)
            print(header)
            for row in reader:
                print('%s' % (row))

                url             = row[0]
                cut_start       = row[1]
                cut_end         = row[2]
                podcast         = row[3]
                title           = row[4]
                description     = row[5]
                tags            = row[6]

                title = title.split("|")
                title = title[0]

                output_filename = title.replace(' ','_')+'_EDITED.mp4'

                if (len(str(cut_start)) > 0 and len(str(cut_end)) > 0):
                    print('Corta pra mim Marcelo Resenha')
                    command = "python ./jumpcutter.py --sounded_speed 1 --silent_speed 999999 --frame_margin 2 --frame_rate 30 --frame_quality 1 --url "+str(url)+" --title '"+str(title)+"' --from_time "+str(cut_start)+" --to_time "+str(cut_end)+" --output_file "+output_filename
                    output_file = subprocess.call(command, shell=True)
                else:
                    print('Sem ponto de Corta pra mim Marcelo Resenha')
                    command = "python ./jumpcutter.py --sounded_speed 1 --silent_speed 999999 --frame_margin 2 --frame_rate 30 --frame_quality 1 --url "+str(url)+" --title '"+str(title)+"' --output_file "+output_filename
                    output_file = subprocess.call(command, shell=True)
                
                if (output_file == 0):
                    thumb = thumb_generator('./'+output_filename, title)
                    print("Selected thumb: %s" % (thumb))
                    if (thumb != None):
                        upload_video('./'+output_filename, url, title, description, tags, thumb)
                
                # Move all video files to dir/
                move_files(title)
                time.sleep(5)

        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(output_filename, reader.line_num, e))

    csvfile.close()

if __name__ == "__main__":
    main()