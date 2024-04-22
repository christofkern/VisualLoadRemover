import cv2
import numpy as np

from draw_boundaries import draw_dashed_rectangle
from detect_menues import detect_main_menu, detect_level_menu
from get_boundaries import get_menu_check_boundaries, get_menu_boundaries, get_level_menu_boundaries_p1, get_level_menu_boundaries_p2, get_crawl_text_boundaries
from check_duplicate_entry import duplicate_entry
from predict import predict_rta, predict_loadless
from file_storage import get_existing_file, write_to_file

# Load the video
path = 'H:\\Videos\\4K Video Downloader+\\[PB] LEGO Star Wars The Complete Saga Any% Speedrun in 22319.mp4'
#path = 'H:\\Videos\\4K Video Downloader+\\level_menu_test.mkv'
#path = 'H:\\Videos\\4K Video Downloader+\\10830 - Lego Star Wars  The Complete Saga  Free Play.mp4'
#path = 'H:\\Videos\\4K Video Downloader+\\ULTIMATE Final Gauntlet Clutch PB.mp4'
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
tcs_boundaries = (0,0,1379,779) #evan
#tcs_boundaries = (0,0,1394,784) #gary
grievous_boundaries = (0,0,574,432) #evan
#grievous_boundaries = (0,0,1394,784) #gary
ar = "16:9" #check if menu etc is on the same spots on 16:10 and 4:3, possible need to change the area calculations, if game is just stretched in obs it shouldnt matter
starting_offset = 0 #offset, if run has a large amount of video material before the actual run
current_frame_index = starting_offset
cut_out = [(1030,652,1366,769)] #areas that are in the game, but dont belong to the game, this will be replaced with black to make blacksceen detection possible

xbox = False 
#differences: offsets for loads, after level load no blackscreen, but shift, blackscreen is also not entirely black
blackscreen_max_value = 20 if xbox else 9

#global variables:
save_name = path.replace('\'','_') + ".txt"
start_frame, loads = get_existing_file(save_name)



    #save state from previous frame
start_menu_visible = False
level_menu_visible = False
fp_menu_visible = False
blackscreen = False
previous_centroids = None
current_centroids = None

    #detectors for decisionmaking of the program
detect_new_game_end = "" # "", initial, characters, end: these are the phases of new game
detect_load_game_end = "" #tbd
level_menu_check_frame = -1
level_menu_fp_check = False
detect_story_load_end = False




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
        
        #only do some of the ocr when screen brightness is below 40
        menu_check_frame, menu_check_frame_boundaries = get_menu_check_boundaries(tcs_boundaries, frame)
        gray_frame = cv2.cvtColor(menu_check_frame, cv2.COLOR_BGR2GRAY)    
        # Compute the mean pixel intensity
        average_brightness = gray_frame.mean()
        #print(average_brightness)
        if (average_brightness < 20):
            #detect main and pause menu:        
            main_menu_area, main_menu_area_boundaries = get_menu_boundaries(tcs_boundaries, frame, xbox)
            detected_main_menu = detect_main_menu(main_menu_area)

            #detect level door menu:
            level_menu_area_p1, level_menu_area_boundaries_p1 = get_level_menu_boundaries_p1(tcs_boundaries, frame)
            level_menu_area_p2, level_menu_area_boundaries_p2 = get_level_menu_boundaries_p2(tcs_boundaries, frame)
            detected_level_menu_p1 = detect_level_menu(level_menu_area_p1)
            detected_level_menu_p2 = detect_level_menu(level_menu_area_p2)
            detected_level_menu = detected_level_menu_p1 == "Story" or detected_level_menu_p2 == "Story"
            detected_fp_menu_stage1 = detected_level_menu_p1 == "FP Stage 1" or detected_level_menu_p2 == "FP Stage 1"
            detected_fp_menu_stage2 = detected_level_menu_p1 == "FP Stage 2" or detected_level_menu_p2 == "FP Stage 2"

       
        #detect cantina load from main menu:
        #check if previous frame was start menu and current isnt -> start frame or preparation of file
        if (start_menu_visible and not detected_main_menu):
            if (start_frame is None):
                start_frame = current_frame_index
                detect_new_game_end = "initial"
                write_to_file(save_name, start_frame, loads)
                print(f"Start of the run detected at frame {start_frame}") #this will bug, if the current frame has a start menu and you jump to a frame that isnt

        #write for next iteration
        start_menu_visible = detected_main_menu   
       

        #detect last pre-cantina blackscreen frame
        if (detect_new_game_end != "" or detect_load_game_end != ""):            
            #print(detect_new_game_end)
            game = frame[tcs_boundaries[1]:tcs_boundaries[3],tcs_boundaries[0]:tcs_boundaries[2]]
            game_array = np.array(game)
            is_black = np.all(game_array <= [blackscreen_max_value, blackscreen_max_value, blackscreen_max_value])   
            #first detect blackscreen, then character icons, then again blackscreen  
            if (blackscreen and not is_black and detect_new_game_end == "initial"):
                detect_new_game_end = "characters"

            if (detect_new_game_end == "characters"):            
                blue_character = game_array[:, :, 0] >= 200  # Blue value of 200 or higher
                green_character = game_array[:, :, 1] >= 140  # Green value of 140 or higher
                
                if(np.any(blue_character & green_character)):
                    detect_new_game_end = "end"                         

            if (blackscreen and not is_black and detect_new_game_end == "end"):
                frame_offset = 17
                if (framerate == 60):                    
                    frame_offset = 33
                if (start_frame + frame_offset < current_frame_index - 1): #prevent backwards detection
                    new_entry = [start_frame + frame_offset, current_frame_index - 1, "new game load"]
                if not duplicate_entry(loads, new_entry):
                    loads.append(new_entry)
                    write_to_file(save_name, start_frame, loads)
                    print(new_entry)
            blackscreen = is_black
            #print(detect_new_game_end)
            


        #detect story load from cantina:
        if (level_menu_visible and not detected_level_menu):
            level_menu_check_frame = current_frame_index
            level_menu_fp_check = False #this should always be false, but better save than sorry
            #check next 1.5 seconds:
                #if bright -> back to cantina
                #elif during that 1.5s the fp_menu was visible -> fp selection and decision tree (tbd)
               
        if (level_menu_check_frame >= 0):
            if (detected_fp_menu_stage1):
                level_menu_fp_check = True
                level_menu_check_frame = -1
                # -> complete FP decision tree

        
            if (current_frame_index == int(level_menu_check_frame + framerate * 1.5)):
                #check brightness of image
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    
                # Compute the mean pixel intensity
                average_brightness = gray_frame.mean()
                #print(average_brightness)
                if (xbox and average_brightness > 30): #in my tests on pc it was always around 0.5-0.6, cantina was around 30, on xbox, stars are 23.7   
                    level_menu_check_frame = -1
                elif (not xbox and average_brightness > 1):                
                    level_menu_check_frame = -1
        
        if(level_menu_check_frame >= 0): #this needs to start before detect_story_load_end is true, as on good harware it will be faster than the 1.5s
            #if we get the text, that is the first frame the timer starts again
            crawl_text_area, crawl_text_area_boundaries = get_crawl_text_boundaries(tcs_boundaries, frame)
            gray_frame = cv2.cvtColor(crawl_text_area, cv2.COLOR_BGR2GRAY)
            retval, thr_frame = cv2.threshold(gray_frame, blackscreen_max_value, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thr_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #cv2.imshow("threshold", thr_frame)
            
            if (xbox):
                total_movement = 0
                count = 0 
                previous_centroids = current_centroids
                current_centroids = []

            for index, contour in enumerate(contours):
                area = cv2.contourArea(contour)   
                # If contour area is above a certain threshold, draw rectangle around it
                if area > 150:  # This should be enough
                    #print(area)
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(crawl_text_area, (x, y), (x + w, y + h), (0, 255, 0), 2) #this somehow makes it show up in the big image, but thats cool i guess     
                    frame_offset = 18
                    if (framerate == 60):
                        frame_offset = 36               
                    new_entry = [level_menu_check_frame + frame_offset, current_frame_index - 1, "story load"]
                    level_menu_check_frame = -1
                    if not duplicate_entry(loads, new_entry):
                        loads.append(new_entry)
                        write_to_file(save_name, start_frame, loads)
                        print(new_entry)
                    break                
            
                if (xbox):  
                    M = cv2.moments(contour)
                    if M["m00"] != 0:  # Check if the denominator is not zero
                        current_centroid = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                        current_centroids.append(current_centroid)
                    else:
                        continue  # Skip this contour if the denominator is zero
                    if previous_centroids is not None and previous_centroids != []:
                        closest_previous_centroid = None
                        min_distance = float('inf')
                        #print(previous_centroids)
                        # Find the closest centroid from the previous frame
                        for prev_centroid in previous_centroids:
                            distance = np.linalg.norm(np.subtract(current_centroid, prev_centroid))
                            #print(current_centroid, prev_centroid, distance)
                            if distance < min_distance:                            
                                min_distance = distance
                                closest_previous_centroid = prev_centroid
                            
                        
                        # Calculate displacement vector between centroids
                        displacement = np.subtract(current_centroid, closest_previous_centroid)                        
                        # Calculate movement in pixels
                        movement = np.linalg.norm(displacement)
                        
                        if movement < 5:  # Filter out extreme movements
                            total_movement += movement
                            count += 1
            
                    if (index == len(contours)-1):
                        if (total_movement > 40): #normal star drift was < 20, star jump was around 70
                            #go back 1.033s, that is 62/31frames for load end
                            frame_offset = 18
                            end_offset = 31
                            if (framerate == 60):
                                frame_offset = 36
                                end_offset = 62
                            new_entry = [level_menu_check_frame + frame_offset, current_frame_index - end_offset, "story load"]
                            level_menu_check_frame = -1
                            if not duplicate_entry(loads, new_entry):
                                loads.append(new_entry)
                                write_to_file(save_name, start_frame, loads)
                                print(new_entry)

            if (not xbox):      
                game = frame[tcs_boundaries[1]:tcs_boundaries[3],tcs_boundaries[0]:tcs_boundaries[2]]
                game_array = np.array(game)
                is_black = np.all(game_array <= [blackscreen_max_value, blackscreen_max_value, blackscreen_max_value])             
                if (is_black):
                    #go back 1.033s, that is 62/31frames for load end
                    frame_offset = 18
                    end_offset = 31
                    if (framerate == 60):
                        frame_offset = 36
                        end_offset = 62
                    new_entry = [level_menu_check_frame + frame_offset, current_frame_index - end_offset, "story load"]
                    level_menu_check_frame = -1
                    if not duplicate_entry(loads, new_entry):
                        loads.append(new_entry)
                        write_to_file(save_name, start_frame, loads)
                        print(new_entry)
            


        level_menu_visible = detected_level_menu    


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
    indicate_color_2 = (250,50,50)
    indicate_color_3 = (50,250,50)
    draw_dashed_rectangle(frame, tcs_boundaries)
    if (average_brightness < 20):
        draw_dashed_rectangle(frame, menu_check_frame_boundaries, color=indicate_color)
    if start_menu_visible:
        draw_dashed_rectangle(frame, main_menu_area_boundaries, color=indicate_color)
    if detected_level_menu_p1 == "Story":
        draw_dashed_rectangle(frame, level_menu_area_boundaries_p1, color=indicate_color)
    if detected_level_menu_p2 == "Story":
        draw_dashed_rectangle(frame, level_menu_area_boundaries_p2, color=indicate_color)
    if detected_level_menu_p1 == "FP Stage 1":
        draw_dashed_rectangle(frame, level_menu_area_boundaries_p1, color=indicate_color_2)
    if detected_level_menu_p2 == "FP Stage 1":
        draw_dashed_rectangle(frame, level_menu_area_boundaries_p2, color=indicate_color_2)
    if detected_level_menu_p1 == "FP Stage 2":
        draw_dashed_rectangle(frame, level_menu_area_boundaries_p1, color=indicate_color_3)
    if detected_level_menu_p2 == "FP Stage 2":
        draw_dashed_rectangle(frame, level_menu_area_boundaries_p2, color=indicate_color_3)



    cv2.imshow('Video Footage', frame)
    
    #uncomment this if need to take a screenshot of the given startframe    
    #cv2.imwrite("garrison.png", frame)
    #exit()

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