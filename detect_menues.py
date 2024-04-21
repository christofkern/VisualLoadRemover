import pytesseract


def detect_main_menu(area):
    detection = pytesseract.image_to_string(area).upper()
    #print(detection)

    if ("NEW GAME" in detection):
        #print("Main Menu detected")
        return True
    return False


def detect_level_menu(area):
    detection = pytesseract.image_to_string(area).upper()
    #print(detection)

    if ("BACK" in detection and "SELECT" in detection):
        return "Story"
    elif ("EXIT" in detection and "SELECT" in detection):
        return "FP Stage 1"
    elif ("YES" in detection and "NO" in detection):
        return "FP Stage 2"
    return ""
    pass



#might need this for exit to cantina detection again
''' 
import cv2
from PIL import Image
import numpy as np

#try to extract all colors near the blue of the menu
    #convert to HSV
    hsv = cv2.cvtColor(main_menu_area, cv2.COLOR_BGR2HSV)

    # Define the lower and upper threshold for blue color
    lower_blue = np.array([30, 20, 140]) 
    upper_blue = np.array([180, 255, 255]) 

    # Create a binary mask for blue regions
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Apply the mask to the original image to extract blue regions
    blue_regions = cv2.bitwise_and(main_menu_area, main_menu_area, mask=mask)
    pil_main_menu_area = Image.fromarray(cv2.cvtColor(blue_regions, cv2.COLOR_BGR2RGB))
    cv2.imshow('Blue', blue_regions)
    
'''