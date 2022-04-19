import csv
import os
import random
import subprocess
import sys
from thumb_generator import create_thumbnail
from youtube_uploader_selenium import YouTubeUploader
from datetime import datetime
import time

def upload_video(video_path, csv_data, thumb_path):
    metadata_path = './metadata.json'
    now = datetime.now() # current date and time

    description = str(csv_data[6])+ \
    '\\n\\n-- Episodio completo: '+str(csv_data[0])+ \
    '\\n-- Todos os dias 8am ao vivo em https://www.twitch.tv/eddieoztv'

    # youtubeuploader metadata
    metadata = '{ "title": "'+str(csv_data[5])+'", \
    "description": "'+description+'", \
    "tags": ["'+str(csv_data[7]).replace(' ','","')+'"], \
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
    
    # Go version
    command = "../youtubeuploader/youtubeuploader -filename "+video_path+" -metaJSON "+metadata_path+" -thumbnail "+thumb_path+""
    output_file = subprocess.call(command, shell=True)
    if (output_file != 0): exit(1)
    # Selenium version
    # YouTubeUploader(video_path, metadata_path, thumb_path).upload()
    # uploader = YouTubeUploader(video_path, metadata_path, thumb_path)
    # was_video_uploaded, video_id = uploader.upload()
    # assert was_video_uploaded

def thumb_generator(file, title):
    print('Generating thumbnails...')
    bg_dir = './thumbs/'
    # title = title.split('|')

    # print('generating default thumbnail...')
    # create_thumbnail('./assets/default_face.png', title[0], True)
    # print('generating video thumbnails...')
    # create_thumbnail(file, title[0])
        
    # if sucessfully copy the frame, check and create thumbnail
    command = "python ./thumb_generator.py --input './assets/default_face.png' --title '"+title+"'"
    output_file = subprocess.call(command, shell=True)
    
    command = "python ./thumb_generator.py --input "+file+" --title '"+title+"' -d False"
    output_file = subprocess.call(command, shell=True)
    ## create_thumbnail(src, args.title, False)
    
    if (len(os.listdir(bg_dir)) >= 1):
        bg = random.choice(os.listdir(bg_dir))
        return (bg_dir+bg)
    else:
        exit(1)

def main():
    with open('list.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        try:
            header = next(reader)
            print(header)
            for row in reader:
                print('%s' % (row))
                title = row[5].split("|")
                title = title[0]

                if (row[3] == '0'):
                    command = "python ./jumpcutter.py --sounded_speed 1 --silent_speed 999999 --frame_margin 2 --frame_rate 30 --frame_quality 1 --url "+str(row[0])+" --title '"+str(title)+"' --output_file output.mp4"
                    output_file = subprocess.call(command, shell=True)
                if (row[3] == '1'):
                    command = "python ./jumpcutter.py --sounded_speed 1 --silent_speed 999999 --frame_margin 2 --frame_rate 30 --frame_quality 1 --url "+str(row[0])+" --title '"+str(title)+"' --from_time "+str(row[1])+" --to_time "+str(row[2])+" --output_file output.mp4"
                    output_file = subprocess.call(command, shell=True)
                
                if (output_file == 0):
                    thumb = thumb_generator('./output.mp4', title)
                    print("Selected thumb: %s" % (thumb))
                    if (thumb != None):
                        upload_video('./output.mp4', row, thumb)
                
                if (os.path.exists('./output.mp4')):
                    os.remove('./output.mp4')
                time.sleep(5)

        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))

    csvfile.close()

if __name__ == "__main__":
    main()