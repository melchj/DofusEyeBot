# base image ubuntu 20.04
FROM ubuntu:20.04

# update package manager and add some custom repositories (for python3.9 and tesseract)
RUN apt-get update
RUN apt-get install -y software-properties-common
# RUN add-apt-repository ppa:deadsnakes/ppa
RUN add-apt-repository ppa:alex-p/tesseract-ocr-devel
RUN apt-get update -y

# install python and tesseract on image
RUN apt-get install -y python3 python3-pip
RUN apt-get install tesseract-ocr -y

# copy over everything
COPY . .

# install python required packages
# COPY requirements.txt ./requirements.txt
# not sure why i need to do wheel and image before the rest of requirements.txt, but it fixes some errors...
RUN pip install wheel
RUN pip install image
RUN pip install -r requirements.txt

# define the command that's executes when the image is run
CMD [ "python3", "./bot.py" ]
# CMD [ "python3", "test_tesseract.py"]