import cv2
import numpy as np
from collections import deque
import time
from picamera2 import Picamera2, Preview
from libcamera import controls
import sys
import threading



#threading event 
operation_active = threading.Event()
#only allows one thread to effect the running_alg
camera_lock = threading.Lock()


center_x = 600 // 2  # Calculate center x-coordinate
center_y = 500 // 2  # Calculate center y-coordinate
offset = 20  # Half of the side length of the 100x100 area

random_coords = [(np.random.randint(center_x - offset, center_x + offset),
                  np.random.randint(center_y - offset, center_y + offset)) for _ in range(30)]

def measure_color_change(frame, pixels):
    color_values = []
    for pixel in pixels:
        x, y = pixel
        color = frame[y, x]
        color_values.extend(color)
    return [np.mean(color_values),np.mean(color_values),np.mean(color_values)]



def running_alg():
    #encapsulates camera so only one thread can access it
    with camera_lock:
        temp_array_length = 500
        temp_array = deque(maxlen=temp_array_length)
        t0= time.time()
        picam2 = Picamera2()
        camera_config = camera_config = picam2.create_preview_configuration()
        picam2.configure(camera_config)
        picam2.start_preview(Preview.QTGL)
        picam2.start()
        time.sleep(1)
        #print(temp_array)

        stdev_array=[]
        frame_size = 0
        color_values_over_time = {'R': [], 'G': [], 'B': []}

        while operation_active.is_set():
            
            frame = picam2.capture_array()
            
                
            frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_rgb = cv2.cvtColor(frame_bw, cv2.COLOR_GRAY2RGB)

            pixels_to_measure = random_coords

            color_values = measure_color_change(frame_rgb, pixels_to_measure)
            temp_array.append(color_values[0::3])
            

            if len(temp_array)==temp_array_length:
                if(frame_size ==(temp_array_length-1)):
                    base_val = np.mean(temp_array)
                    offset = base_val-60
                    color_values_over_time['R'].append(np.mean(temp_array)-offset)
                if(np.mean(temp_array)-offset>80): #80
                    stdev_array.append(np.std(np.array(temp_array)-offset))
                    if(np.std(np.array(temp_array))<1.5):#1.5
                        t1=time.time()
                        print("Time measured through framesize: ", (frame_size/30))
                        print("time in seconds: ", t1-t0)
                        break
            frame_size += 1
        picam2.stop_preview()
        picam2.close()
        
