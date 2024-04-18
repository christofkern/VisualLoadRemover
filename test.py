import cv2
import numpy as np

# Load the video
cap = cv2.VideoCapture('G:\\Downloads\\wetransfer_escape-letter-crawl-mp4_2024-04-16_1431\\new game cantina load.mp4')
cap = cv2.VideoCapture('chimkin.mp4')
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Initialize background subtractor
bg_subtractor = cv2.createBackgroundSubtractorMOG2()

roi_x, roi_y, roi_width, roi_height = 1050, 100, 220, 76

pause = True  # Pause flag
backwards = False
current_frame_index = 70  # Keep track of the current frame



while True:
    if not pause and not backwards: 
        ret, frame = cap.read()     
        current_frame_index += 1

        #video analyzer:

        '''possible loads:
        - cantina load
        - level loads:
            - Story:
                - Skip crawl text
                - No skip crawl text
            - FreePlay:
                - Skip crawl text
                - No skip crawl text
            - Challenges:
                - Skip crawl text
                - No skip crawl text
            - Continue Story
                - Skip crawl text
                - No skip crawl text
        - Reset
            - PC
            - XBox

        '''

       

        # Update previous frame for the next iteration





    #everything below is only for visual control
    else:
        if not pause and backwards:
            current_frame_index -= 1

        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_index)
        ret, frame = cap.read()

    if not ret:
        print("no video found")
        break  # If no frame is returned, end the loop

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
            print(area)
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(cropped_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            

    # Display the frame with detected contours
    cv2.imshow('Detected Contours', cropped_frame)

    # Handle key press events
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
        pause = True
    elif key == ord('a'):
        # Step backward logic
        if current_frame_index > 0:
            current_frame_index -= 1 
            pause = True

cap.release()
cv2.destroyAllWindows()