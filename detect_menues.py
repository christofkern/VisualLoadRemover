import easyocr

reader = easyocr.Reader(['en'])

def detect_main_menu(area):
    detection = reader.readtext(area)
    #print(detection)

    for box, text, confidence in detection:
        if "NEW GAME" in text.upper():
            return True
    return False


def detect_level_menu(area):
    detection = reader.readtext(area)
    #print(detection)

    select_detected = False
    back_detected = False
    exit_detected = False
    yes_detected = False
    no_detected = False

    for box, text, confidence in detection:
        if "SELECT" in text.upper():
            select_detected = True
        elif ("BACK" in text.upper() or "ACK" in text.upper() or "ACH" in text.upper()  #these are the known mistakes in english, try to improve this in the future
            or "RETOUR" in text.upper() or "RETOUT" in text.upper() #french  
            ):
            back_detected = True
        elif ("EXIT" in text.upper()
            or "QUITTER" in text.upper() or "QULTTER" in text.upper() #french
            ):
            exit_detected = True
        elif ("YES" in text.upper()
            or "OUI" in text.upper()
            ):
            yes_detected = True
        elif ("NO" in text.upper() #english
            or "NON" in text.upper() #french
            ):
            no_detected = True

    if back_detected and select_detected:
        return "Story"
    elif exit_detected and select_detected:
        return "FP Stage 1"
    elif yes_detected and no_detected:
        return "FP Stage 2"
    else:
        return ""




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