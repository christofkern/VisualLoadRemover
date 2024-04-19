import cv2
from PIL import Image
import pytesseract
import numpy as np

def detect_menues(tcs_boundaries, main_menu_area):

    #try to extract all colors near the blue of the menu
    #convert to HSV
    hsv = cv2.cvtColor(main_menu_area, cv2.COLOR_BGR2HSV)

    # Define the lower and upper threshold for blue color
    lower_blue = np.array([60, 35, 140]) 
    upper_blue = np.array([180, 255, 255]) 

    # Create a binary mask for blue regions
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Apply the mask to the original image to extract blue regions
    blue_regions = cv2.bitwise_and(main_menu_area, main_menu_area, mask=mask)
    pil_main_menu_area = Image.fromarray(cv2.cvtColor(blue_regions, cv2.COLOR_BGR2RGB))


    detection = pytesseract.image_to_string(pil_main_menu_area).upper()

    if ("NEW GAME" in detection):
        #print("Main Menu detected")
        return("Main Menu")
    elif ("EXTRAS" in detection):
        #print("Pause Menu detected")
        return("Pause Menu")
    return ""


''' if the above isnt reliable enough because of background

if (1 if "E" in detection else 0) + \
        (1 if "X" in detection else 0) + \
        (1 if "T" in detection else 0) + \
        (1 if "R" in detection else 0) + \
        (1 if "A" in detection else 0) + \
        (1 if "S" in detection else 0) >= 4:


'''