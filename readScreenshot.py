import cv2 as cv
import numpy as np
import os
import imutils
from dataclasses import dataclass
import pytesseract
from pytesseract.pytesseract import Output
from fight import Player, Fight
import time

iconNames = [
    'dead',
    'eni_m',
    'eni_f',
    'feca_m',
    'feca_f',
    'panda_m',
    'panda_f',
    'cra_m',
    'cra_f',
    'eca_m',
    'eca_f',
    'osa_m',
    'osa_f',
    'xel_m',
    'xel_f',
    'forge_m',
    'forge_f',
    'elio_m',
    'elio_f',
    'masq_m',
    'masq_f',
    'ougi_m',
    'ougi_f',
    'sacri_m',
    'sacri_f',
    'hup_m',
    'hup_f',
    'iop_m',
    'iop_f',
    'sadi_m',
    'sadi_f',
    'sram_m',
    'sram_f',
    'enu_m',
    'enu_f',
    'fog_m',
    'fog_f',
    'rogue_m',
    'rogue_f'
]

classColors = {
    'eni':      (128, 84,231),
    'feca':     (128,234,255),
    'panda':    (169,169,169),
    'cra':      (  0,102, 17),
    'eca':      ( 51,187,255),
    'osa':      (179, 60,  0),
    'xel':      (255,119, 51),
    'forge':    (230, 74, 25),
    'elio':     (153,128,  0),
    'masq':     (  0, 34,204),
    'ougi':     (  0, 64,128),
    'sacri':    (  0,255, 43),
    'hup':      (255,212,128),
    'iop':      ( 25,140,255),
    'sadi':     (  0, 77, 13),
    'sram':     (255,102,102),
    'enu':      ( 37,108,141),
    'fog':      (118,180,227),
    'rogue':    ( 80, 80, 80)
}

@dataclass
class LocatedIcon:
    name: str
    x: int
    y: int
    w: int
    h: int
    color: tuple = (255, 128, 0)

    def topLeft(self):
        return (self.x, self.y)
    
    def bottomRight(self):
        return ((self.x + self.w), (self.y + self.h))

@dataclass
class LocatedPlayer(LocatedIcon):
    playerName:str = 'unknown'
    isDead:int = 0

# TODO: combine both of these find template(s) functions, they're not different enough to be separate
def findTemplate(img, templateName, useEdges=False):
    # TODO: consider passing the template image itself, not the path

    # img2 = img.copy()
    img2 = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    if useEdges:
        img2 = cv.Canny(img2, 50, 200)

    template = cv.imread(templateName, 0)
    if useEdges:
        template = cv.Canny(template, 50, 200)
    w, h = template.shape[::-1]

    found = None # bookkeeping object to keep track of if we find the right spot
    # loop over scales of the image
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        # resize the image according to the scale, and keep track of the ratio of the resizing
        resized = imutils.resize(img2, width = int(img2.shape[1] * scale))
        r = img2.shape[1] / float(resized.shape[1])

        # if the resized image is smaller than the template, then break from the loop
        if resized.shape[0] < h or resized.shape[1] < w:
            break

        res = cv.matchTemplate(resized, template, eval('cv.TM_CCORR_NORMED'))
        # find bounding box of the best match
        _min_val, max_val, _min_loc, max_loc = cv.minMaxLoc(res)

        # if we have found a new maximum correlation value, then update the bookkeeping variable
        if found is None or max_val > found[0]:
            # cv.imshow('source', resized)
            # cv.imshow('template', template)
            # cv.imshow('result', res)
            # cv.waitKey(0)
            found = (max_val, max_loc, r)
    
    # DEBUG: show images
    # cv.imshow('source', resized)
    # cv.imshow('template', template)
    # cv.imshow('results', res)
    # cv.waitKey(0)

    # unpack the bookkeeping object and compute the (x, y) coordinates of the bounding box based on the resized ratio
    _max_val, maxLoc, r = found
    top = int(maxLoc[0] * r)
    left = int(maxLoc[1] * r)
    bottom = int((maxLoc[0] + h) * r)
    right = int((maxLoc[1] + w) * r)

    return ((top, left), (bottom, right))

def findTemplates(img, template, useGray=True, useEdges=False):
    # prep the source image
    img2 = img.copy()
    if useGray:
        img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
    if useEdges:
        img2 = cv.Canny(img2, 50, 200)
    
    # prep the template
    # TODO: make this work for a list/array (difference?) of templates
    # template = cv.imread(templateName, 0)
    if useGray:
        template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
    if useEdges:
        template = cv.Canny(template, 50, 200)
    tw = template.shape[1]
    th = template.shape[0]

    # DEBUG: show images
    # cv.imshow('source', img2)
    # cv.imshow('template', template)

    found = None # bookkeeping object to keep track through size iterations
    # loop over scales of the image
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        start_time2 = time.time()
        # resize the image according to the scale, and keep track of the ratio of the resizing
        resized = imutils.resize(img2, width = int(img2.shape[1] * scale))
        r = img2.shape[1] / float(resized.shape[1])
        # print(r)

        # if the resized image is smaller than the template, then break from the loop
        if resized.shape[0] < th or resized.shape[1] < tw:
            break

        start_time = time.time()
        result = cv.matchTemplate(resized, template, eval('cv.TM_CCORR_NORMED'))
        end_time = time.time()
        # print(f'time at {scale} scale: {end_time-start_time}')
        # find bounding box of the best match
        _min_val, max_val, _min_loc, _max_loc = cv.minMaxLoc(result)

        # if we have found a new maximum correlation value, then update the bookkeeping variable
        if found is None or max_val > found[0]:
            found = (max_val, result, r, scale)
        end_time2 = time.time()
        # print(f"at scale={scale} and r={r} : search time: {end_time-start_time}, total loop time: {end_time2-start_time2}")

    # unpack the bookkeeping object and return the results map with the resize factor
    _max_val, result, r, scale = found
    return (result, r, scale)

# TODO: optimize the template matching and scaling of the source image a bunch... pure brute force at the moment, needs performance improvements
def findDofusIcons(imgPath:str):
    """
    Takes a path to a dofus 5v5 screenshot and returns info (list of name and rectangle pairs)

    returns: list of LocatedIcon objects:
    (
        winners,
        losers,
        sword,
        (list of class icon LocatedObjects),
        (list of dead icon LocatedObjects)
    )
    """

    source = cv.imread(imgPath, cv.IMREAD_COLOR)
    if source is None:
        print(f'Could not read the image. {imgPath}')
        return None

    result = []

    # find icons that appear EXACTLY once:
    for templateName in ['winners', 'losers', 'sword']:
        top_left, bottom_right = findTemplate(source, f'ref/{templateName}.png', False)
        result.append(LocatedIcon(templateName, top_left[0], top_left[1], bottom_right[0]-top_left[0], bottom_right[1]-top_left[1]))
    
    classesResult = []
    deadResult = []
    # find class icons and dead icons, these can appear ANY number of times
    for iconName in iconNames:
        iconImg = cv.imread(f'ref/{iconName}.png', cv.IMREAD_COLOR)
        iconW = iconImg.shape[1]
        iconH = iconImg.shape[0]

        # template match for the current icon
        iconResult, r, scale = findTemplates(source, iconImg, False, False)
        temp = ''
        if np.max(iconResult) > 0.959:
            temp = '*'
        print(f'{iconName[0:3]}{iconName[-2::]} max: {np.max(iconResult):1.4f}, scale: {scale:1.3f}{temp}')

        # DEBUG: show template match results image
        # cv.imshow('icon results', iconResult)
        # cv.waitKey(0)

        # capture every pos above a threshold value
        # TODO: make that threshold value diffent for each icon, and tune it
        yloc, xloc = np.where(iconResult >= 0.959)

        # make rectangles from these results, and consolidate overlaping rectangles
        rectangles = []
        for (x, y) in zip(xloc, yloc):
            rectangles.append([int(x * r), int(y * r), int(iconW * r), int(iconH * r)])
            rectangles.append([int(x * r), int(y * r), int(iconW * r), int(iconH * r)]) # duplicate to avoid groupRectangles() bug
        rectangles, _weights = cv.groupRectangles(rectangles, 1, 0.2)
        for rect in rectangles:
            pt1 = (rect[0], rect[1])
            pt2 = (rect[0]+rect[2], rect[1]+rect[3])
            if iconName == 'dead':
                deadResult.append(LocatedIcon(iconName, pt1[0], pt1[1], pt2[0]-pt1[0], pt2[1]-pt1[1], (0,255,255)))
            else:
                classesResult.append(LocatedPlayer(iconName.split('_')[0], pt1[0], pt1[1], pt2[0]-pt1[0], pt2[1]-pt1[1], classColors.get(iconName.split('_')[0], (0,255,255))))

    result.append(classesResult)
    result.append(deadResult)
    return result

def applyLevels(image, inBlackD=[0,0,0], inWhiteD=[255,255,255], inGammaD=[1.0,1.0,1.0], outBlackD=[0,0,0], outWhiteD=[255,255,255]):
    # mimics photoshop's "adjustments -> levels" menu
    # see https://stackoverflow.com/questions/26912869/color-levels-in-opencv

    img = image.copy()

    inBlack  = np.array(inBlackD, dtype=np.float32)
    inWhite  = np.array(inWhiteD, dtype=np.float32)
    inGamma  = np.array(inGammaD, dtype=np.float32)
    outBlack = np.array(outBlackD, dtype=np.float32)
    outWhite = np.array(outWhiteD, dtype=np.float32)

    img = np.clip( (img - inBlack) / (inWhite - inBlack), 0, 255 )                            
    img = ( img ** (1/inGamma) ) *  (outWhite - outBlack) + outBlack
    img = np.clip( img, 0, 255).astype(np.uint8)

    return img

def readDofusScreenshot(filePath:str):
    # TODO: make a better docstring
    """
    give a image file path and have it's icons and text read by the script...
    return useful list of info gathered
    """
    print(f'-------- {filePath} --------')

    # load the image from path
    img = cv.imread(filePath)
    if img is None:
        print(f'error!!! this is not an image? {filePath}')
        return
    
    # find icons in screenshot
    start_time = time.time()
    winners, losers, sword, classesList, deadList = findDofusIcons(filePath)
    end_time = time.time()
    print(f"total icon lookup time: {end_time-start_time}")

    # find bounding box of where the player names are located
    imgH, imgW = img.shape[0:2]
    namesTop = winners.y + winners.h
    namesRight = sword.x

    # account for if classesList is empty (uh oh)
    namesLeft = 0
    namesBottom = imgH
    if len(classesList) > 0:
        namesLeft = int(np.max([(i.x + i.w) for i in classesList]))
        namesBottom = int(np.max([(i.y + i.h*1.2) for i in classesList]))

    losersTop = losers.y
    losersBottom = losers.y + losers.h

    # mask unwanted area and preprocess image for OCR
    ocrImg = img.copy()

    ocrImg = applyLevels(ocrImg, inBlackD=[50,50,50])

    ocrImg = cv.cvtColor(ocrImg, cv.COLOR_BGR2GRAY)
    kernelmatrix = np.ones((2, 2), np.uint8)
    # ocrImg = cv.erode(ocrImg, kernelmatrix)
    # ocrImg = cv.dilate(ocrImg, kernelmatrix)
    fillColor = (10, 10, 10)
    cv.rectangle(ocrImg, (0, 0), (namesLeft, imgH), fillColor, -1) # left box
    cv.rectangle(ocrImg, (0, 0), (imgW, namesTop), fillColor, -1) # top box
    cv.rectangle(ocrImg, (namesRight, 0), (imgW, imgH), fillColor, -1) # right box
    cv.rectangle(ocrImg, (0, losersTop), (imgW, losersBottom), fillColor, -1) # box in the middle (along "lowers" line)
    cv.rectangle(ocrImg, (0, namesBottom), (imgW, imgH), fillColor, -1) # bottom box
    # ocrImg = cv.threshold(ocrImg, 150, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]

    # use tesseract OCR to read names
    custom_config = r"-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-\'"
    # custom_config = r"-c tessedit_char_blacklist=‘!@#$%^&*(){}|?<>,.~`/1234567890+_\\"
    # custom_config = ''
    OCRdata = pytesseract.image_to_data(ocrImg, output_type=Output.DICT, config=custom_config)
    for i in range(len(OCRdata['text'])):
        if float(OCRdata['conf'][i]) > 0:
            (x, y, imgW, imgH) = (OCRdata['left'][i], OCRdata['top'][i], OCRdata['width'][i], OCRdata['height'][i])
            cv.rectangle(img, (x, y), (x + imgW, y + imgH), (0, 255, 0), 2)
    print(OCRdata)

    # show the pre-processed ocr input (for debug purposes)
    # cv.imshow('ocr img', ocrImg)
    # cv.imwrite(f"output/{filePath.split('/')[-1].split('.')[0]}_ocr.png", ocrImg)

    for icon in ([winners, losers, sword] + classesList + deadList):
        # draw boxes from each located icon
        cv.rectangle(img, icon.topLeft(), icon.bottomRight(), icon.color, 2)

        # find associated name text (TODO: more unoptimization here... someday rewrite a better way to do this and the above loop)
        foundName = ''
        for i in range(len(OCRdata['text'])):
            # find the text that is in the same line as the icon, horizontally
            (x, y, imgW, imgH) = (OCRdata['left'][i], OCRdata['top'][i], OCRdata['width'][i], OCRdata['height'][i])
            if (y > icon.y) and (y < (icon.y + icon.h)):
                foundName = foundName + OCRdata['text'][i]
            foundName = foundName.replace(' ', '') # remove any spaces
            foundName = foundName.replace('\'', '') # remove any quote marks (not blacklisted character because of perc names)
            # assign the text discovered to the located player, if anything was found
            if len(foundName) > 0:
                icon.playerName = foundName
        # print(icon)

    # sort class icons by y value
    classesList.sort(key=lambda x: x.y)

    # make final list of Players to return
    players = []
    i = 0
    winnerLoser = 'W'
    swordPlayer = ''
    for p in classesList:
        i = i + 1
        # once y>losersTop, then we're looking at losing team not winners
        if (winnerLoser == 'W') and (p.y > losersTop):
            winnerLoser = 'L'
            i = 1

        # see if the sword is associated with this character
        if ((sword.y + sword.h/2) > p.y) and ((sword.y + sword.h/2) < (p.y + p.h)):
            swordPlayer = f'{winnerLoser}{i}'
        
        # see if this character is dead or not
        for dicon in deadList:
            if ((dicon.y + dicon.h/2) > p.y) and ((dicon.y + dicon.h/2) < (p.y + p.h)):
                p.isDead = 1

        players.append(Player(f'{winnerLoser}{i}', p.playerName, p.name, p.isDead))

    # print(players)

    fight = Fight(-1, 0, -1, -1, None, filePath, swordPlayer, players)

    # return the marked up image and the fight object
    return (img, fight)

def main():
    # loop through the screenshots in this directory
    screenshotDir = 'image_set_02'
    for filename in os.listdir(screenshotDir):
        # skip this one if it's not the file with the specified name
        # if not filename.lower().endswith('01.png'):
            # continue
        # skip this one if it's not a png file
        if not filename.lower().endswith('.png'):
            continue

        path = f'{screenshotDir}/{filename}'
        img, fight = readDofusScreenshot(path)

        for p in fight.players:
            print(f"({p.characterClass}) {p.characterName} - {p.isDead}")

        print(f"Attacker is: {fight.sword}")

        # show results in a window
        cv.imshow('result', img)
        cv.waitKey(0)
        cv.destroyAllWindows()

        # save result
        # cv.imwrite(f"output/{filename}_processed.png", img)
        # status = cv.imwrite(f'output/{filename}', img)
        # print(status)
    return

if __name__ == '__main__':
    main()