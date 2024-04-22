#evans bounds: h: 1380, w: 780
#garys bounds: h: 1394, w: 784


def get_menu_check_boundaries(tcs_boundaries, frame):
    x1, y1, x2, y2 = tcs_boundaries
    w, h = x2 - x1, y2 - y1

    level_menu_area_boundaries = (int(0.114 * w), int(0.684 * h), int(0.164 * w + 0.114 * w), int(0.255 * h + 0.684 * h))
    return frame[level_menu_area_boundaries[1]:level_menu_area_boundaries[3], level_menu_area_boundaries[0]:level_menu_area_boundaries[2]], level_menu_area_boundaries

def get_menu_boundaries(tcs_boundaries, frame, xbox):
    x1, y1, x2, y2 = tcs_boundaries
    w, h = x2 - x1, y2 - y1
    if xbox:
        main_menu_area_boundaries = (int(0.419 * w), int(0.630 * h), int(0.164 * w + 0.419 * w), int(0.068 * h + 0.630 * h))
    else:
        main_menu_area_boundaries = (int(0.395 * w), int(0.551 * h), int(0.210 * w + 0.395 * w), int(0.064 * h + 0.551 * h))
    return frame[main_menu_area_boundaries[1]:main_menu_area_boundaries[3], main_menu_area_boundaries[0]:main_menu_area_boundaries[2]], main_menu_area_boundaries

def get_level_menu_boundaries_p1(tcs_boundaries, frame):
    x1, y1, x2, y2 = tcs_boundaries
    w, h = x2 - x1, y2 - y1

    level_menu_area_boundaries = (int(0.153 * w), int(0.057 * h), int(0.121 * w + 0.153 * w), int(0.141 * h + 0.057 * h))
    return frame[level_menu_area_boundaries[1]:level_menu_area_boundaries[3], level_menu_area_boundaries[0]:level_menu_area_boundaries[2]], level_menu_area_boundaries

def get_level_menu_boundaries_p2(tcs_boundaries, frame):
    x1, y1, x2, y2 = tcs_boundaries
    w, h = x2 - x1, y2 - y1

    level_menu_area_boundaries = (int(0.725 * w), int(0.057 * h), int(0.121 * w + 0.725 * w), int(0.141 * h + 0.057 * h))
    return frame[level_menu_area_boundaries[1]:level_menu_area_boundaries[3], level_menu_area_boundaries[0]:level_menu_area_boundaries[2]], level_menu_area_boundaries

def get_crawl_text_boundaries(tcs_boundaries, frame):
    x1, y1, x2, y2 = tcs_boundaries
    w, h = x2 - x1, y2 - y1

    level_menu_area_boundaries = (int(0.411 * w), int(0.086 * h), int(0.168 * w + 0.411 * w), int(0.075 * h + 0.086 * h))
    return frame[level_menu_area_boundaries[1]:level_menu_area_boundaries[3], level_menu_area_boundaries[0]:level_menu_area_boundaries[2]], level_menu_area_boundaries