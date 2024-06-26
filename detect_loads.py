import numpy as np
import cv2

from file_storage import write_to_file
from check_duplicate_entry import duplicate_entry
from get_boundaries import get_crawl_text_boundaries, get_fp_wipe_boundaries


def detect_main_menu_load(start_menu_visible, detected_main_menu, start_frame, current_frame_index, save_name, loads, detect_new_game_end, detect_load_game_end, 
                            frame, tcs_boundaries, blackscreen_max_value, blackscreen, framerate):
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
        game = frame[tcs_boundaries[1]:tcs_boundaries[3],tcs_boundaries[0]:tcs_boundaries[2]]
        game_array = np.array(game)
        is_black = np.all(game_array <= [blackscreen_max_value, blackscreen_max_value, blackscreen_max_value])  
        #print(is_black) 
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
                detect_new_game_end = ""
                print(new_entry)
        blackscreen = is_black
        #print(detect_new_game_end)
    
    return start_menu_visible, blackscreen, loads, start_frame, detect_new_game_end

def detect_level_menu_load_end(tcs_boundaries, frame, crawl_text_detect_max_value, xbox, current_centroids, framerate, blackscreen_max_value):
    #if we get the text, that is the first frame the timer starts again
    crawl_text_area, crawl_text_area_boundaries = get_crawl_text_boundaries(tcs_boundaries, frame)
    gray_frame = cv2.cvtColor(crawl_text_area, cv2.COLOR_BGR2GRAY)
    retval, thr_frame = cv2.threshold(gray_frame, crawl_text_detect_max_value, 255, cv2.THRESH_BINARY)
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
            return 1           
            
    
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
                    end_offset = 31
                    if (framerate == 60):
                        end_offset = 62
                    return end_offset
           

    if (not xbox):      
        game = frame[tcs_boundaries[1]:tcs_boundaries[3],tcs_boundaries[0]:tcs_boundaries[2]]  
        gray_frame = cv2.cvtColor(game, cv2.COLOR_BGR2GRAY)    
        # Compute the mean pixel intensity
        average_brightness = gray_frame.mean()
        #print(average_brightness)
        if (average_brightness < 0.1): #need to this instead of full blackscreen as sometimes that frame gets skipped and the screen wipe has already been started, maybe this needs to be higher than 0.1 even
            #go back 1.033s, that is 62/31frames for load end
            end_offset = 31
            if (framerate == 60):
                end_offset = 62
            return end_offset  
    return -1                     



def detect_level_menu_load(level_menu_visible, detected_level_menu, level_menu_check_frame, fp_load_indicator_frame, level_menu_fp_check, current_frame_index, detected_fp_menu_stage1, 
                            framerate, frame, level_menu_fp_frame_history,  tcs_boundaries, xbox, crawl_text_detect_max_value, previous_centroids, current_centroids, 
                            loads, save_name, start_frame, blackscreen_max_value):    
    if (level_menu_visible and not detected_level_menu):
        level_menu_check_frame = current_frame_index
        level_menu_fp_check = False #this should always be false, but better save than sorry
        #check next 1.5 seconds:
            #if bright -> back to cantina
            #elif during that 1.5s the fp_menu was visible -> fp selection and decision tree
            
    if (level_menu_check_frame >= 0):
        if (detected_fp_menu_stage1):
            level_menu_fp_check = True
            level_menu_check_frame = -1
            # going back into story is not possible, so no need to handle that
            # FP handling will be at the bottom
            print("FP Selected")

    
        if (current_frame_index == int(level_menu_check_frame + framerate * 1.5)):
            #check brightness of image
            game = frame[tcs_boundaries[1]:tcs_boundaries[3],tcs_boundaries[0]:tcs_boundaries[2]]
            gray_frame = cv2.cvtColor(game, cv2.COLOR_BGR2GRAY)    
            # Compute the mean pixel intensity
            average_brightness = gray_frame.mean()
            #print(average_brightness)
            if (xbox and average_brightness > 30): #in my tests on pc it was always around 1.5-1.6, cantina was around 30, on xbox, stars are 23.7   
                level_menu_check_frame = -1
            elif (not xbox and average_brightness > 3):                
                level_menu_check_frame = -1   

        end_offset = detect_level_menu_load_end(tcs_boundaries, frame, crawl_text_detect_max_value, xbox, current_centroids, framerate, blackscreen_max_value)
        
        if (end_offset >= 0):
            frame_offset = 18
            if (framerate == 60):
                frame_offset = 36  
            new_entry = [level_menu_check_frame + frame_offset, current_frame_index - end_offset, "story load"]
            
            level_menu_check_frame = -1
            if not duplicate_entry(loads, new_entry):
                loads.append(new_entry)
                write_to_file(save_name, start_frame, loads)
                print(new_entry)
           


    if (level_menu_fp_check):
        #print("FP Handling")
        fp_wipe_area, fp_wipe_area_boundaries = get_fp_wipe_boundaries(tcs_boundaries, frame)
        gray_frame = cv2.cvtColor(fp_wipe_area, cv2.COLOR_BGR2GRAY)
        # Find contours in the mask
        circles = cv2.HoughCircles(gray_frame, cv2.HOUGH_GRADIENT, dp=1, minDist=100,
                           param1=50, param2=30, minRadius=85, maxRadius=100)
        # ensure at least some circles were found
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
            # loop over the (x, y) coordinates and radius of the circles
            for (center_x, center_y, radius) in circles:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(fp_wipe_area, (center_x, center_y), radius, (0, 255, 0), 2)
                cv2.circle(fp_wipe_area, (center_x, center_y), 2, (0, 0, 255), 2)
        
                target_border_color = (255, 81, 9) #we are in BGR
                color_range = 20  # You can adjust this value based on the tolerance you need

                # Check if circle is moving to the right and if border is within acceptable color range
                if level_menu_fp_frame_history:  # Check if frame_history is not empty
                    movement_direction = 1 if center_x > level_menu_fp_frame_history[-1][2] else 0  # Compare with previous center x-coordinate
                else:
                    movement_direction = 0  # If frame_history is empty, set movement direction to 0
                if center_x + radius - 5 >= 0 and center_x + radius - 5 < fp_wipe_area.shape[1]:
                    border_color = fp_wipe_area[center_y, center_x + radius - 5]
                else:
                    border_color = (0, 0, 0)  # Default color if index is out of bounds
                color_difference = np.linalg.norm(np.array(border_color) - np.array(target_border_color))
                within_color_range = color_difference < color_range
                if(within_color_range) :
                    level_menu_fp_frame_history.append((movement_direction, within_color_range, center_x))  # Store movement direction and current center x-coordinate
                    #print(level_menu_fp_frame_history)

        # Check if conditions are met to print "Freeplay circle found"
        min_consecutive_frames = int(framerate / 6)
        if len(level_menu_fp_frame_history) >= min_consecutive_frames:
            consecutive_frames = level_menu_fp_frame_history[-min_consecutive_frames:]
            if all(movement == 1 and color_match for movement, color_match, _ in consecutive_frames):
                #print("Freeplay circle found")
                similarity_threshold = 20                 
                all_similar_colors = True
                for y in range(fp_wipe_area.shape[0]):
                    for x in range(fp_wipe_area.shape[1]):
                        pixel_color = fp_wipe_area[y, x]
                        # Check if the pixel color is roughly similar to the average color
                        if (abs(pixel_color[0].astype(int) - pixel_color[1].astype(int)) > similarity_threshold and
                            abs(pixel_color[0].astype(int) - pixel_color[2].astype(int)) > similarity_threshold and
                            abs(pixel_color[0].astype(int) - pixel_color[2].astype(int)) > similarity_threshold):
                            all_similar_colors = False
                            break
                    if not all_similar_colors:
                        break

                if all_similar_colors:
                    fp_load_indicator_frame = current_frame_index
                    level_menu_fp_check = False
        #cv2.imshow("Detected Circle", fp_wipe_area) 

    if (fp_load_indicator_frame > 0):

        end_offset = detect_level_menu_load_end(tcs_boundaries, frame, crawl_text_detect_max_value, xbox, current_centroids, framerate, blackscreen_max_value)
        if end_offset > -1:
            #go back 1.033s, that is 62/31frames for load end
            frame_offset = 8
            if (framerate == 60):
                frame_offset = 15  
            new_entry = [fp_load_indicator_frame + frame_offset, current_frame_index - end_offset, "fp/chall load"]

            fp_load_indicator_frame = -1
            if not duplicate_entry(loads, new_entry):
                loads.append(new_entry)
                write_to_file(save_name, start_frame, loads)
                print(new_entry)

    return level_menu_check_frame, fp_load_indicator_frame, level_menu_fp_check, previous_centroids, current_centroids, loads

