## goodbye
July 27th, 2023

This was a fun project that I started about 2 (3?) years ago. I learned a lot and had fun making it. I haven't made progress on it for a long time, and now I admit that I will likely not make progress on it again in the future. Thanks everyone who enjoyed it. I miss playing Dofus lol.

-Chonk (Jack)


# Dofus Eye Discord Bot
This discord bot is a re-creation of the Free Ringtone's "Perc Screenshot Reader" discord bot, which looks Dofus 5v5 screenshots posted in discord channels and extracts data. That project was so messy and inflated that when I wanted to integrate it with the DofusEye backend/frontend, it seemed easier to just start from scratch, keeping only some valuable bits.

### There is zero optimization and this runs slow AF!
but that's ok, this is still experimental

## Python Virtual Environment

Set up Python virtual environment and install dependancies:

create virtual environment:
```bash
$ python3 -m venv venv
```

activate virtual environment:
```bash
$ . venv/bin/activate
```

(or this one for windows)
```bash
$ .\venv\Scripts\activate
```

install/update dependencies:
```bash
$ pip install -r requirements.txt
```

## Teseract OCR
one of the dependacies is tesseract ocr. have to install it on the OS and then add it to PATH variable for pytesseract to work...

Also, I believe only certain versions of tesseract OCR work. Currently, I have this working with tesseract version v5.0.0-alpha.20210811.

Installing tesseract (on linux):
```
$ sudo apt-get install tesseract-ocr
```

Verify that tesseract installed and is in PATH:
```
$ tesseract -v
```

For future implementation of cyrillic letters:

If the bot is trying to get the cyrillic letters (greek and russion) in some character names, this requires two things:

1. The rus.traineddata and grc.traineddata need to be added to the tesseract directory
2. The tesseract calls within the script need to have `-l eng+rus` in there (so far, only needed russian set of letters, not greek... so perhaps the greek is optional)
