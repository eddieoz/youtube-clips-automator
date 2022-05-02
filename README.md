# MARCELO: an AI bot to automate the editing and thumbnail creation for your Youtube clips channel

This project uses machine learning (AI) to automate the management of your Youtube clips channel by clipping, editing, creating of thumbnails and uploading to your YT channel

## Requirements

- Python 3
- [Youtube uploader](https://github.com/porjo/youtubeuploader/releases)
- OpenCV
- ffmpeg

## Setup

1. Download the latest version of [youtubeuploader](https://github.com/porjo/youtubeuploader/releases) and extract the executable go file in the project's `./` folder
2. Configure Youtube API v3 accordingly [Youtube Uploader instructions](https://github.com/porjo/youtubeuploader/blob/master/README.md)
3. Install python requirements
```
$ pip install -r requirements.txt
```
4. Populate the folder `./backgrounds` with images `.png` to be randomly selected to your thumbnail
5. Leave a `default_face.png` on `./assets` folder just in case the bot is not able to find a smiling face on your video
6. \[Optional] Leave a `opening.mp4` and `ending.mp4` videos (MP4 encoded, 1920x1080) on `assets/` dir to automatically insert an intro and ending sessions on your edited video

## Usage

1. Prepare a spreadsheet with the following fields (example ./list-sample.csv):
   
| url | time_from | time_to | podcast | title | description | tags | 
| --- | --- | --- | --- | --- | --- | --- | 
| https://www.youtube.com/watch?v=[VIDEO_ID] | 00:00:14 | 00:01:46 | 0 | TITLE | DESCRIPTION | tag1 tag2 tag3 tag4 | 
 https://www.youtube.com/watch?v=[VIDEO_ID2] |  |  | 0 | TITLE | DESCRIPTION | tag1 tag2 tag3 tag4 |

- **URL**: Youtube url
- **time_from**: Clip start time (leave it blank for the entire video)
- **time_to**: Clip end time (leave it blank for the entire video)
- **podcast**: it will extract the edited audio for a podcast (NOT IMPLEMENTED YET - leave it 0)
- **title**: Video clip title (don't use comma)
- **description**: Video clip description (don't use comma)
- **tags**: Video tags splitted by spaces (don't use comma)

1. Save the spreadsheet as a `csv` and place the `list.csv` file in the project folder

2. Run `marcelo.py`
```
$ python marcelo.py
```

## How it works

This project execute is executed in 4 phases:

1. **Download and cut**: Download and cut the video if needed
2. **Editing**: A bot will scan the entire video to find audio silences, to cut and edit the video automatically
3. **Thumbnail**: A bot will use machine learning through Computer Vision to find smiling faces in the video, to extract samples and build an unique thumbnail for your channel
4. **Upload**: Prepare the metadata and Upload the video to your Youtube channel
5. **Marcelo**: is a tribute to [Marcelo Rezende](https://en.wikipedia.org/wiki/Marcelo_Rezende), a Brazilian journalist and television presenter who used to say 'Corta pra mim'

## DEMO
This bot is live, producing the clips channel of the Morning Crypto show.
- Clips: https://www.youtube.com/channel/UCzwLEvNi0__N9BHbgTqJKeQ
- Full videos: https://youtube.com/eddieoz
- Live show on Twitch (every day, 8am BRT): https://twitch.tv/eddieoztv

## References

- [jumpcutter](https://github.com/carykh/jumpcutter)
- [Awesome Thumbnail Youtube Generator](https://github.com/CUAI-CAU/Awesome-Youtube-Thumbnail-Generator)

## Decentralised repo
This project can be found on [Radicle](https://app.radicle.network/seeds/pine.radicle.garden/rad:git:hnrkyonz47h6zb5mb5tb3xni3y4uwzqjn85gy)

## Known issues
- Issue on `cypher.py`
  Youtube changed some internal APIs, not fixed on pytube yet. Solution found on: https://stackoverflow.com/a/71922554
  Line 264:
  ```
  r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
  r'\([a-z]\s*=\s*([a-zA-Z0-9$]{2,3})(\[\d+\])?\([a-z]\)'
  ```
  Line 288:
  `nfunc=re.escape(function_match.group(1))),`

## TO-DO

- [ ] Automate the podcast creation
- [ ] Use ffmpeg GPU
- [ ] Select backgrounds based on title and description
- [ ] Indexing captions for searching specific spoken phrase on the video
- [ ] Automate the creation of the keywords (by using Watson or another NLP)

## Buy me a coffee
Did you like it? [Buy me a coffee](https://www.buymeacoffee.com/eddieoz)

[![Buy me a coffee](https://ipfs.io/ipfs/QmR6W4L3XiozMQc3EjfFeqSkcbu3cWnhZBn38z2W2FuTMZ?filename=buymeacoffee.webp)](https://www.buymeacoffee.com/eddieoz)

Or drop me a tip through Lightning Network: ⚡ [zbd.gg/eddieoz](https://zbd.gg/eddieoz)