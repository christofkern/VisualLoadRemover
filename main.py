import cv2
import numpy as np

from draw_boundaries import draw_dashed_rectangle
from detect_menues import detect_menues
from get_boundaries import get_menu_boundaries
from check_duplicate_entry import duplicate_entry
from predict import predict_rta, predict_loadless
from file_storage import get_existing_file, write_to_file

# Load the video
path = 'H:\\Videos\\4K Video Downloader+\\[PB] LEGO Star Wars The Complete Saga Any% Speedrun in 22319.mp4'
cap = cv2.VideoCapture(path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Initialize background subtractor
bg_subtractor = cv2.createBackgroundSubtractorMOG2()


pause = True  # Pause flag
backwards = False
current_frame_index = 0  # Keep track of the current frame
frame_processed = False


#setup stuff before the run
framerate = 30
tcs_boundaries = (0,0,1379,779)
grievous_boundaries = (0,0,574,432)
ar = "16:9" #check if menu etc is on the same spots on 16:10 and 4:3, possible need to change the area calculations, if game is just stretched in obs it shouldnt matter
starting_offset = 0 #offset, if run has a large amount of video material before the actual run
current_frame_index = starting_offset
cut_out = [(1030,652,1366,769)] #areas that are in the game, but dont belong to the game, this will be replaced with black to make blacksceen detection possible
blackscreen_max_value = 9

#global variables:
start_frame = None
loads = [] #holds tuples of start + end frames of a load



    #save state from previous frame
start_menu_visible = False
pause_menu_visible = False
blackscreen = False

    #detectors for decisionmaking of the program
detect_new_game_end = "" #empty, initial, characters, end
detect_load_game_end = "" 




#try to read existing file, if none is present, make a new one and open it
save_name = path.replace('\'','_') + ".txt"
start_frame, loads = get_existing_file(save_name)
print (loads)

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

    #blackout areas that are not native to TCS
    for area in cut_out:
        x1, y1, x2, y2 = area
        frame[y1:y2, x1:x2] = [0, 0, 0]

    if not ret:
        print("no video found")
        break  # If no frame is returned, end the loop

    if not frame_processed:
    
        #detect main and pause menu:        
        main_menu_area, main_menu_area_boundaries = get_menu_boundaries(tcs_boundaries, frame)
        detected_menu = detect_menues(tcs_boundaries, main_menu_area)
        #check if previous frame was start menu and current isnt -> start frame or preparation of file
        if (start_menu_visible and not detected_menu == "Main Menu"):
            if (start_frame is None):
                start_frame = current_frame_index
                detect_new_game_end = "initial"
                write_to_file(save_name, start_frame, loads)
                print(f"Start of the run detected at frame {start_frame}") #this will bug, if the current frame has a start menu and you jump to a frame that isnt

        #write for next iteration
        start_menu_visible = False
        pause_menu_visible = False
        if (detected_menu == "Main Menu"):
            start_menu_visible = True
        elif(detected_menu == "Pause Menu"):
            pause_menu_visible = True
       

        #detect last pre-cantina blackscreen frame
        if (detect_new_game_end != "" or detect_load_game_end != ""): 
            #first detect blackscreen, then character icons, then again blackscreen
            game = frame[tcs_boundaries[1]:tcs_boundaries[3],tcs_boundaries[0]:tcs_boundaries[2]]
            game_array = np.array(game)
            is_black = np.all(game_array <= [blackscreen_max_value, blackscreen_max_value, blackscreen_max_value])   
            
            if (blackscreen and not is_black and detect_new_game_end == "initial"):
                detect_new_game_end = "characters"

            if (detect_new_game_end == "characters"):            
                blue_character = game_array[:, :, 0] >= 200  # Blue value of 200 or higher
                green_character = game_array[:, :, 1] >= 140  # Green value of 140 or higher
                
                if(np.any(blue_character & green_character)):
                    detect_new_game_end = "end"                         

            if (blackscreen and not is_black and detect_new_game_end == "end"):
                frame_offset = 0
                if (framerate == 30):
                    frame_offset = 17
                else:
                    frame_offset = 33
                if (start_frame + frame_offset < current_frame_index - 1): #prevent backwards detection
                    new_entry = [start_frame + frame_offset, current_frame_index - 1, "new game load"]
                if not duplicate_entry(loads, new_entry):
                    loads.append(new_entry)
                    write_to_file(save_name, start_frame, loads)
                    print(new_entry)

            #print(detect_new_game_end)
            blackscreen = is_black


        #detect level load

   
            



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
    indicate_color = (50,50,250)
    draw_dashed_rectangle(frame, tcs_boundaries)

    if start_menu_visible or pause_menu_visible:
        draw_dashed_rectangle(frame, main_menu_area_boundaries, color=indicate_color)
    

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
    
    elif key == ord('c'):
        s, prediction =  predict_rta(start_frame, current_frame_index, framerate)        
        print(f"RTA: {prediction}, Loadless: {predict_loadless(s, loads, framerate)}, if a load is currently happening, this will be wrong")
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