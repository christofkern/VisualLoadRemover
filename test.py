import cv2
import pytesseract
from PIL import Image
import numpy as np

from draw_boundaries import draw_dashed_rectangle

# Load the video
cap = cv2.VideoCapture('H:\\Videos\\4K Video Downloader+\\[PB] LEGO Star Wars The Complete Saga Any% Speedrun in 22319.mp4')
#cap = cv2.VideoCapture('chimkin.mp4')
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Initialize background subtractor
bg_subtractor = cv2.createBackgroundSubtractorMOG2()



pause = True  # Pause flag
backwards = False
current_frame_index = 3420  # Keep track of the current frame
frame_processed = False


#setup stuff before the run
framerate = 30
tcs_boundaries = (0,0,1379,779)
grievous_boundaries = (0,0,574,432)
ar = "16:9" #check if menu etc is on the same spots on 16:10 and 4:3, possible need to change the area calculations, if game is just stretched in obs it shouldnt matter



while True:
    if not pause and not backwards: 
        ret, frame = cap.read()     
        current_frame_index += 1
        frame_processed = False
    else:
        if not pause and backwards:
            current_frame_index -= 1
            frame_processed = False

        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_index)
        ret, frame = cap.read()

        #possible introduce timeout, does all checks only every second and possibly backtrack, only if it gets too slow with all the ocr

    if not ret:
        print("no video found")
        break  # If no frame is returned, end the loop

    if not frame_processed:
    
        #detect main menu, possibly also pause menu (detect "Extras")
        main_menu_area = (545,430,835,485)
        x1,y1,x2,y2 = tcs_boundaries
        w = x2-x1
        h = y2-y1
        
        m1 = (int) (0.395 * w)
        m2 = (int) (0.551 * h)
        m3 = (int) (0.210 * w + m1)
        m4 = (int) (0.064 * h + m2)

        main_menu_area_boundaries = (m1,m2,m3,m4)        
        main_menu_area = frame[m2:m4,m1:m3]

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
            print("Main Menu detected")
        elif (1 if "E" in detection else 0) + \
            (1 if "X" in detection else 0) + \
            (1 if "T" in detection else 0) + \
            (1 if "R" in detection else 0) + \
            (1 if "A" in detection else 0) + \
            (1 if "S" in detection else 0) >= 4:
            print("Pause Menu detected")
            #print (detection)
   
            

        frame_processed = True
    '''
    roi_x, roi_y, roi_width, roi_height = 1050, 100, 220, 76
    # Crop the frame to the defined ROI
    cropped_frame = frame[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]

    # Display the cropped frame
    #cv2.imshow('Cropped Frame', cropped_frame)

    #convert to grayscale
    gray_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
    
    #threshold
    retval, thr_frame = cv2.threshold(gray_frame, 5, 255, cv2.THRESH_BINARY)


    # Find contours
    contours, _ = cv2.findContours(thr_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate through contours
    for contour in contours:
        # Calculate contour area
        area = cv2.contourArea(contour)

        

        # If contour area is above a certain threshold, draw rectangle around it
        if area > 300:  # Adjust threshold as needed
            #print(area)
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(cropped_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            

    '''





    #draw all indicators for reviewer
    draw_dashed_rectangle(frame, tcs_boundaries)

    draw_dashed_rectangle(frame, main_menu_area_boundaries, color=(120,120,120))



    cv2.imshow('Video Footage', frame)



    # Keyboard control
    key = cv2.waitKey(1) & 0xFF 
    if key == ord('q'):
        break
    elif key == ord('p'):
        pause = not pause
    elif key == ord('b'):
        backwards = not backwards    
    elif key == ord('s'):
        # Step forward logic
        current_frame_index +=1
        frame_processed = False
        pause = True
    elif key == ord('a'):
        # Step backward logic
        if current_frame_index > 0:
            current_frame_index -= 1 
            frame_processed = False
            pause = True
    
    elif key == ord('i'):
        print(current_frame_index)
    elif key == ord('f'):
        # Pause for frame number input
        frame_input = ''
        while True:
            key = cv2.waitKey(0) & 0xFF
            if key == 13:  # Enter key
                try:
                    frame_index = int(frame_input)
                    current_frame_index = frame_index
                    frame_processed = False
                except ValueError:
                    pass  # Ignore non-integer inputs
                break  
            elif key >= 48 and key <= 57:  # Numerical keys
                frame_input += chr(key)  
            elif key == 8:  # Backspace key
                frame_input = frame_input[:-1]  
            else:
                pass  
            

cap.release()
cv2.destroyAllWindows()