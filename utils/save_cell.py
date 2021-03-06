# Module to Save detected cells
import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
from PIL import Image, ImageEnhance, ImageFilter
import json


# Function to Check if Image/Cell is Empty
def check_empty_image(finalimage ,lang, config_tesseract, threshold_length_text, special_words):
    try:

        image = cv2.resize(finalimage, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        retval, threshold = cv2.threshold(image,127,255,cv2.THRESH_BINARY)
        blur = cv2.GaussianBlur(threshold, (3,3), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Morph open to remove noise and invert image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        invert = 255 - opening

        text = pytesseract.image_to_string(invert, lang = lang, config = config_tesseract)
        text = ''.join([i for i in text if i.isalpha()])

        if len(text) > threshold_length_text or text.lower() in special_words :
            return 1
        else :
            return 0
    except:
        return 0


def save_cell(finalboxes, bitnot, countcol, count_rows, filepath, lang, config_tesseract, threshold_length_text, json_save, special_words):
    outer = []
    row_nr = 0
    column_nr = 0


    try:
        for i in range(len(finalboxes)):
            for j in range(len(finalboxes[i])):
                inner = ''
                if len(finalboxes[i][j]) == 0:
                    outer.append(' ')
                else:
                    for k in range(len(finalboxes[i][j])):
                        (y, x, w, h) = (finalboxes[i][j][k][0],
                                finalboxes[i][j][k][1],
                                finalboxes[i][j][k][2],
                                finalboxes[i][j][k][3])
                        finalimage = bitnot[x:x + h, y:y + w]
                        if h < 80 or w < 100:
                            pass
                        else:
                            if column_nr == countcol:
                                row_nr = row_nr + 1
                                column_nr = 0

                            Folder_Path = 'results/' + filepath.split('\\')[-1].split('.')[0]
                            if not os.path.exists(Folder_Path):
                                print('Creating Results Folder : ', Folder_Path)
                                os.makedirs(Folder_Path)

                            file_to_be_saved = Folder_Path + '/' + 'cell_' + str(row_nr) + '_' + str(column_nr) + '.png'
                            empty_status = check_empty_image(finalimage, lang, config_tesseract, threshold_length_text, special_words)
                            if empty_status == 1:
                                cv2.imwrite(img=finalimage, filename=file_to_be_saved)
                                data = {"Image" : Folder_Path + '.png', "x": x, "y": y, "w": w, "h": h}
                                if json_save.lower() == "yes":
                                    with open("results/" + 'output.json', 'a', encoding='utf-8') as f:
                                        json.dump(data, f, ensure_ascii=False, indent=4)
                                    f.close()
                            column_nr = column_nr + 1  

        return 1
    except:
        return -1
