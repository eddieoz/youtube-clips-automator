# set base image (host OS)
# FROM phusion/baseimage:focal-1.2.0 ## need some work here
FROM python:3.8

# set the working directory in the container
WORKDIR /app

# download and install dependencies
RUN apt-get -y update
RUN apt-get install -y ffmpeg wget python3 python3-pip
RUN wget https://github.com/porjo/youtubeuploader/releases/download/22.02/youtubeuploader_22.02_Linux_x86_64.tar.gz
RUN tar xvf ./youtubeuploader_22.02_Linux_x86_64.tar.gz 

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY . .
COPY ./patch/cipher.py /usr/local/lib/python3.8/site-packages/pytube/cipher.py

# command to run on container start
CMD [ "python3", "./marcelo.py" ]