import os

def get_existing_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            starting_frame = file.readline().strip()
            loads = []
            if (starting_frame.isnumeric and starting_frame != ''):
                print(starting_frame)
                starting_frame = int(starting_frame)
            else:
                starting_frame = None
            # Read all other lines into loads array
            for line in file:
                parts = line.split(',')                
                loads.append((int(parts[0][1:]),int(parts[1]), parts[2][2:-3]))
            return starting_frame, loads
    return None, []

def write_to_file(save_name, starting_frame, loads):
    with open(save_name, 'w', encoding='utf-8') as file:
        if starting_frame is not None:
            file.write(str(starting_frame) + '\n')
        else:
            file.write('\n')
        for load in loads:
            file.write(str(load) + '\n')