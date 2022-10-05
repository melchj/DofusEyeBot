# base image ubuntu 20.04
FROM ubuntu:20.04

# update packages, add some custom repositories, install python and tesseract on image
RUN apt-get update \
    && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:alex-p/tesseract-ocr-devel \
    && apt-get update -y \
    && apt-get install -y \
    python3 \
    python3-pip \
    tesseract-ocr

# copy requirements.txt
COPY ./requirements.txt ./requirements.txt

# install python required packages
# COPY requirements.txt ./requirements.txt
# not sure why i need to do wheel and image before the rest of requirements.txt, but it fixes some errors...
RUN pip install wheel \
    && pip install image \
    && pip install -r requirements.txt

# copy over project
COPY . .

# define the command that's executes when the image is run
CMD [ "python3", "./bot.py" ]
# CMD [ "python3", "test_tesseract.py"]