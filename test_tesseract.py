import pytesseract

print("---- testing tesseract-ocr (and pytesseract) installation ----")

print('-- command --')
print(pytesseract.pytesseract.tesseract_cmd)

print('-- version --')
try:
    print(pytesseract.pytesseract.get_tesseract_version())
except pytesseract.TesseractNotFoundError:
    print('Tesseract not found!!!')
except Exception:
    print('didnt work! some exception :(')

print('-- languages --')
try:
    print(pytesseract.pytesseract.get_languages())
except pytesseract.TesseractNotFoundError:
    print('Tesseract not found!!!')
except Exception:
    print('didnt work! some exception :(')


# print('-- tessdata prefix? --')
# print(os.environ)

print('trying again with a different path to tesseract command??')

pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'

print('-- command --')
print(pytesseract.pytesseract.tesseract_cmd)

print('-- version --')
try:
    print(pytesseract.pytesseract.get_tesseract_version())
except pytesseract.TesseractNotFoundError:
    print('Tesseract not found!!!')
except Exception:
    print('didnt work! some exception :(')


print('-- languages --')
try:
    print(pytesseract.pytesseract.get_languages())
except pytesseract.TesseractNotFoundError:
    print('Tesseract not found!!!')
except Exception:
    print('didnt work! some exception :(')
