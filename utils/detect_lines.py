# Module to detect Lines and Cells on an Image
import cv2
import numpy as np


def line_detector(img, img_bin, horizontal_kernel_len, vertical_kernal_len, horizontal_iterations, vertical_iterations):

    # Length(width) of kernel as 100th of total width
    hor_kernel_len = horizontal_kernel_len
    ver_kernel_len = vertical_kernal_len

    # Defining a vertical kernel to detect all vertical lines of image
    ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, ver_kernel_len))

    # Defining a horizontal kernel to detect all horizontal lines of image
    hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (hor_kernel_len, 1))

    # A kernel of 2x2
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

    # Use vertical kernel to detect and save the vertical lines in a jpg
    image_1 = cv2.erode(img_bin, ver_kernel, iterations=vertical_iterations)
    vertical_lines = cv2.dilate(image_1, ver_kernel, iterations=vertical_iterations)

    # Use horizontal kernel to detect and save the horizontal lines in a jpg
    image_2 = cv2.erode(img_bin, hor_kernel, iterations=horizontal_iterations)
    horizontal_lines = cv2.dilate(image_2, hor_kernel, iterations=horizontal_iterations)

    # Combine horizontal and vertical lines in a new third image, with both having same weight.
    img_vh = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)

    # Eroding and thesholding the image
    img_vh = cv2.erode(~img_vh, kernel, iterations=2)
    (thresh, img_vh) = cv2.threshold(img_vh, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) 

    return thresh, img_vh


def detect_lines(img, img_bin, no_columns):

    horizontal_kernel_len = np.array(img).shape[1] // 100
    vertical_kernal_len = np.array(img).shape[1] // 100
    thresh, img_vh = line_detector(img, img_bin, horizontal_kernel_len, vertical_kernal_len, 3, 5)
    (finalboxes, bitnot, countcol, count_rows, cell_detector_status) = detect_cells(img, img_vh, no_columns)
    
    if cell_detector_status == 1:
        return (finalboxes, bitnot, countcol, count_rows, cell_detector_status)
    else :
        try:
            horizontal_kernel_len = np.array(img).shape[1] // 20
            vertical_kernal_len = np.array(img).shape[0] // 11
            thresh, img_vh = line_detector(img, img_bin, horizontal_kernel_len, vertical_kernal_len, 3, 5)
            (finalboxes, bitnot, countcol, count_rows, cell_detector_status) = detect_cells(img, img_vh, no_columns)
        except:
            pass
        if cell_detector_status == 1:
            return (finalboxes, bitnot, countcol, count_rows, cell_detector_status)
        else :
            horizontal_kernel_len = np.array(img).shape[1] // 100
            vertical_kernal_len = np.array(img).shape[0] // 50 
            thresh, img_vh = line_detector(img, img_bin, horizontal_kernel_len, vertical_kernal_len, 3, 5)
            (finalboxes, bitnot, countcol, count_rows, cell_detector_status) = detect_cells(img, img_vh, no_columns)
            if cell_detector_status == 1:
                return (finalboxes, bitnot, countcol, count_rows, cell_detector_status)
            else :
                horizontal_kernel_len = np.array(img).shape[1] // 100
                vertical_kernal_len = np.array(img).shape[1] // 100
                thresh, img_vh = line_detector(img, img_bin, horizontal_kernel_len, vertical_kernal_len, 3, 3)
                (finalboxes, bitnot, countcol, count_rows, cell_detector_status) = detect_cells(img, img_vh, no_columns)
                return (finalboxes, bitnot, countcol, count_rows, cell_detector_status)


# Function to sort contours
def sort_contours(cnts, method='left-to-right'):

    # initialize the reverse flag and sort index
    reverse = False
    i = 0

    # handle if we need to sort in reverse
    if method == 'right-to-left' or method == 'bottom-to-top':
        reverse = True

    # handle if we are sorting against the y-coordinate rather than
    # the x-coordinate of the bounding box
    if method == 'top-to-bottom' or method == 'bottom-to-top':
        i = 1

    # construct the list of bounding boxes and sort them from top to
    # bottom
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key=lambda b: b[1][i], reverse=reverse))

    # return the list of sorted contours and bounding boxes
    return (cnts, boundingBoxes)


# Function to extract cells from Image on basis of OpenCV Contour Function
def detector(image, image_vh,contour_method, no_columns):
    # Detect contours for following box detection
    (contours, hierarchy) = cv2.findContours(image_vh, contour_method, cv2.CHAIN_APPROX_SIMPLE)

    # Sort all the contours by top to bottom.
    (contours, boundingBoxes) = sort_contours(contours, method='top-to-bottom')

    # Creating a list of heights for all detected boxes
    heights = [boundingBoxes[i][3] for i in range(len(boundingBoxes))]

    # Get mean of heights
    mean = np.mean(heights)

    # Create list box to store all boxes in
    box = []

    # Get position (x,y), width and height for every contour and show the contour on image
    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        if w < 1000 and h < 500:
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            box.append([x, y, w, h])
      
    # Creating two lists to define row and column in which cell is located
    row = []
    column = []
    j = 0

    # Sorting the boxes to their respective row and column
    for i in range(len(box)):
        if i == 0:
            column.append(box[i])
            previous = box[i]
        else:
            if box[i][1] <= previous[1] + mean / 2:
                column.append(box[i])
                previous = box[i]
                if i == len(box) - 1:
                    row.append(column)
            else:
                row.append(column)
                column = []
                previous = box[i]
                column.append(box[i])
    
    # calculating maximum number of cells
    countcol = 0
    for i in range(len(row)):
        countcol = len(row[i])
        if countcol > countcol:
            countcol = countcol
    count_rows = len(row)
    countcol_cal = round(len(box)/count_rows)
    
    if countcol != no_columns:
        countcol = countcol_cal

    # Check Possibility of Error in detecting columns
    if countcol != no_columns :
        cell_detector_status = -1
    else :
        cell_detector_status = 1
     
    # Retrieving the center of each column
    center = [int(row[i][j][0] + row[i][j][2] / 2) for j in range(len(row[i])) if row[0]]
    center = np.array(center)
    center.sort()

    # Regarding the distance to the columns center, the boxes are arranged in respective order
    finalboxes = []
    for i in range(len(row)):
        lis = []
        for k in range(countcol):
            lis.append([])
        for j in range(len(row[i])):
            diff = abs(center - (row[i][j][0] + row[i][j][2] / 4))
            minimum = min(diff)
            indexing = list(diff).index(minimum)
            try:
                lis[indexing].append(row[i][j])
            except:
                pass
        finalboxes.append(lis)
    
    return finalboxes, countcol, count_rows, cell_detector_status


def detect_cells(image, image_vh, no_columns):
    image = image
    image_temp = image
    no_columns = no_columns
    image_vh = image_vh
    bitxor = cv2.bitwise_xor(image, image_vh)
    bitnot = cv2.bitwise_not(bitxor)

    try:
        finalboxes, countcol, count_rows, cell_detector_status = detector(image, image_vh, cv2.RETR_EXTERNAL, no_columns)
    except:
       finalboxes, countcol, count_rows, cell_detector_status= detector(image_temp, image_vh, cv2.RETR_TREE, no_columns)

    return (finalboxes, bitnot, countcol, count_rows, cell_detector_status)
