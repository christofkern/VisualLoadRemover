def predict_rta(start_frame, current_frame_index, frame_rate):    
    if (start_frame is not None):
        elapsed_seconds = (current_frame_index - start_frame) / frame_rate    
        return elapsed_seconds, format_prediction(elapsed_seconds)
    return 0, "no start found yet"

def predict_loadless(rta_seconds, loads, frame_rate):
    for load in loads:
        load_seconds = (load[1] - load[0]) / frame_rate
        rta_seconds -= load_seconds
    return format_prediction(rta_seconds)

def format_prediction(time):
    hours = int(time // 3600)
    minutes = int((time % 3600) // 60)
    seconds = int(time % 60)
    milliseconds = int((time % 1) * 100)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:02d}"