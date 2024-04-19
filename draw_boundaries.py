import cv2

def draw_dashed_rectangle(frame, tcs_boundaries, color=(0, 255, 0), thickness=1, dash_length=15, gap_length=40):
    # Define the coordinates of the rectangle
    x1, y1, x2, y2 = tcs_boundaries
        
    # Draw the dashed rectangle
    for i in range(x1, x2, dash_length + gap_length):
        cv2.line(frame, (i, y1), (min(i + dash_length, x2), y1), color, thickness)
        cv2.line(frame, (i, y2), (min(i + dash_length, x2), y2), color, thickness)
    
    for i in range(y1, y2, dash_length + gap_length):
        cv2.line(frame, (x1, i), (x1, min(i + dash_length, y2)), color, thickness)
        cv2.line(frame, (x2, i), (x2, min(i + dash_length, y2)), color, thickness)

