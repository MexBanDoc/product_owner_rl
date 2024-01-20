import pytesseract
from PIL import Image, ImageEnhance

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

image_123 = Image.open(r"C:\Users\tvb06\PycharmProjects\CV\data\img_8.png")
enhancer1 = ImageEnhance.Sharpness(image_123)
factor1 = 0.01 #чем меньше, тем больше резкость
im_s_1 = enhancer1.enhance(factor1)
# string = pytesseract.image_to_data(im_s_1, config='--psm 6 -c tessedit_char_whitelist=0123456789,. ', output_type=pytesseract.Output.DICT)
string = pytesseract.image_to_data(im_s_1, config='--psm 6 -c tessedit_char_whitelist=0123456789,. ', output_type=pytesseract.Output.DICT)
print(string)
string = pytesseract.image_to_string(im_s_1, config='--psm 6 -c tessedit_char_whitelist=0123456789,. ')
print(string)


# string = pytesseract.image_to_data(im_s_1, config='--psm 6 -c tessedit_char_whitelist=SMLX', output_type=pytesseract.Output.DICT)
# print(string)
# string = pytesseract.image_to_string(im_s_1, config='--psm 6 -c tessedit_char_whitelist=SMLX')
# print(string)
