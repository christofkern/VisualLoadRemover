import numpy as np

from file_storage import write_to_file
from check_duplicate_entry import duplicate_entry

def detect_main_menu_load(start_menu_visible, detected_main_menu, start_frame, current_frame_index, save_name, loads, detect_new_game_end, detect_load_game_end, frame, tcs_boundaries, blackscreen_max_value, blackscreen, framerate):
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
                detect_new_game_end = ""
                print(new_entry)
        blackscreen = is_black
        #print(detect_new_game_end)
    
    return start_menu_visible, blackscreen, loads, start_frame, detect_new_game_end