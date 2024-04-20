def get_menu_boundaries(tcs_boundaries, frame):
    x1, y1, x2, y2 = tcs_boundaries
    w, h = x2 - x1, y2 - y1

    main_menu_area_boundaries = (int(0.395 * w), int(0.551 * h), int(0.210 * w + 0.395 * w), int(0.064 * h + 0.551 * h))
    return frame[main_menu_area_boundaries[1]:main_menu_area_boundaries[3], main_menu_area_boundaries[0]:main_menu_area_boundaries[2]], main_menu_area_boundaries