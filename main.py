import cv2

from draw_boundaries import draw_dashed_rectangle
from detect_menues import detect_main_menu, detect_level_menu
from get_boundaries import get_brightness_check_boundaries, get_menu_boundaries, get_level_menu_boundaries_p1, get_level_menu_boundaries_p2
from predict import predict_rta, predict_loadless
from file_storage import get_existing_file
from detect_loads import detect_main_menu_load, detect_level_menu_load

# Load the video
#path = 'H:\\Videos\\4K Video Downloader+\\[PB] LEGO Star Wars The Complete Saga Any% Speedrun in 22319.mp4'
#path = 'H:\\Videos\\4K Video Downloader+\\level_menu_test.mkv'
path = 'H:\\Videos\\4K Video Downloader+\\10830 - Lego Star Wars  The Complete Saga  Free Play.mp4'
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
framerate = 60
#tcs_boundaries = (0,0,1379,779) #evan
#tcs_boundaries = (0,0,1394,784) #gary
tcs_boundaries = (325,96,1884,979) #rapho
grievous_boundaries = (0,0,574,432) #evan
#grievous_boundaries = (0,0,1394,784) #gary
grievous_boundaries = (325,96,1884,979) #rapho
ar = "16:9" #check if menu etc is on the same spots on 16:10 and 4:3, possible need to change the area calculations, if game is just stretched in obs it shouldnt matter
starting_offset = 2021 #offset, if run has a large amount of video material before the actual run
current_frame_index = starting_offset
cut_out = []#[(1030,652,1366,769)] #areas that are in the game, but dont belong to the game, this will be replaced with black to make blacksceen detection possible

xbox = False 
#differences: offsets for loads, after level load no blackscreen, but star shift, different colors possibly
blackscreen_max_value = 20
crawl_text_detect_max_value = 5 if not xbox else 10 #experiment here!

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
level_menu_fp_frame_history = []
fp_load_indicator_frame = -1



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
        menu_check_frame, menu_check_frame_boundaries = get_brightness_check_boundaries(tcs_boundaries, frame)
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
            start_menu_visible, blackscreen, loads, start_frame, detect_new_game_end = detect_main_menu_load(start_menu_visible, detected_main_menu, start_frame, current_frame_index, 
                                                                                    save_name, loads, detect_new_game_end, detect_load_game_end, frame, tcs_boundaries, 
                                                                                    blackscreen_max_value, blackscreen, framerate)

            
            #detect story/fp/challenge load from cantina (only story rn):
            level_menu_check_frame, fp_load_indicator_frame, level_menu_fp_check, previous_centroids, current_centroids, loads = detect_level_menu_load(level_menu_visible, detected_level_menu, 
                                            level_menu_check_frame, fp_load_indicator_frame, level_menu_fp_check, current_frame_index, detected_fp_menu_stage1, framerate, frame, 
                                            level_menu_fp_frame_history, tcs_boundaries, xbox, crawl_text_detect_max_value, previous_centroids, current_centroids, loads, save_name, 
                                            start_frame, blackscreen_max_value)
            


                


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
    #cv2.imwrite("rapho.png", frame)
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