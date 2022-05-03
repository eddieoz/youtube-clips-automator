# set base image (host OS)
FROM python:3.8

RUN apt-get -y update
RUN apt-get install -y ffmpeg

# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY . .
COPY ./patch/cipher.py /usr/local/lib/python3.8/site-packages/pytube/cipher.py

# command to run on container start
CMD [ "python", "./marcelo.py" ]