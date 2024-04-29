#evans bounds: h: 1380, w: 780
#garys bounds: h: 1394, w: 784
#raphos bounds: (325,96,1884,979) h: 1559 w: 883


def get_brightness_check_boundaries(tcs_boundaries, frame):
    x1, y1, x2, y2 = tcs_boundaries
    
    w, h = x2 - x1, y2 - y1
    brightness_area_boundaries = (int(0.114 * w) + x1, int(0.684 * h) + y1, int(0.164 * w + 0.06 * w) + x1, int(0.255 * h + 0.684 * h) + y1)   
    return frame[brightness_area_boundaries[1]:brightness_area_boundaries[3], brightness_area_boundaries[0]:brightness_area_boundaries[2]], brightness_area_boundaries

def get_menu_boundaries(tcs_boundaries, frame, xbox):
    x1, y1, x2, y2 = tcs_boundaries
    w, h = x2 - x1, y2 - y1
    if xbox:
        main_menu_area_boundaries = (int(0.419 * w) + x1, int(0.630 * h) + y1, int(0.164 * w + 0.419 * w) + x1, int(0.068 * h + 0.630 * h) + y1)
    else:
        main_menu_area_boundaries = (int(0.395 * w) + x1, int(0.551 * h) + y1, int(0.210 * w + 0.395 * w) + x1, int(0.064 * h + 0.551 * h) + y1)
    return frame[main_menu_area_boundaries[1]:main_menu_area_boundaries[3], main_menu_area_boundaries[0]:main_menu_area_boundaries[2]], main_menu_area_boundaries

def get_level_menu_boundaries_p1(tcs_boundaries, frame):
    x1, y1, x2, y2 = tcs_boundaries
    w, h = x2 - x1, y2 - y1

    level_menu_area_boundaries = (int(0.153 * w) + x1, int(0.057 * h) + y1, int(0.121 * w + 0.153 * w) + x1, int(0.141 * h + 0.057 * h) + y1)
    return frame[level_menu_area_boundaries[1]:level_menu_area_boundaries[3], level_menu_area_boundaries[0]:level_menu_area_boundaries[2]], level_menu_area_boundaries

def get_level_menu_boundaries_p2(tcs_boundaries, frame):
    x1, y1, x2, y2 = tcs_boundaries
    w, h = x2 - x1, y2 - y1

    level_menu_area_boundaries = (int(0.725 * w) + x1, int(0.057 * h) + y1, int(0.121 * w + 0.725 * w) + x1, int(0.141 * h + 0.057 * h) + y1)
    return frame[level_menu_area_boundaries[1]:level_menu_area_boundaries[3], level_menu_area_boundaries[0]:level_menu_area_boundaries[2]], level_menu_area_boundaries

def get_fp_wipe_boundaries(tcs_boundaries, frame):
    x1, y1, x2, y2 = tcs_boundaries
    w, h = x2 - x1, y2 - y1

    level_menu_area_boundaries = (int(0.727 * w) + x1, int(0.184 * h) + y1, int(0.273 * w + 0.727 * w) + x1, int(0.442 * h + 0.184 * h) + y1)
    return frame[level_menu_area_boundaries[1]:level_menu_area_boundaries[3], level_menu_area_boundaries[0]:level_menu_area_boundaries[2]], level_menu_area_boundaries


def get_crawl_text_boundaries(tcs_boundaries, frame):
    x1, y1, x2, y2 = tcs_boundaries
    w, h = x2 - x1, y2 - y1

    level_menu_area_boundaries = (int(0.411 * w) + x1, int(0.086 * h) + y1, int(0.168 * w + 0.411 * w) + x1, int(0.075 * h + 0.086 * h) + y1)
    return frame[level_menu_area_boundaries[1]:level_menu_area_boundaries[3], level_menu_area_boundaries[0]:level_menu_area_boundaries[2]], level_menu_area_boundaries