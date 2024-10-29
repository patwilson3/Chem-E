import cv2
import numpy as np
from collections import deque
import time
from picamera2 import Picamera2, Preview
from libcamera import controls
import threading
import sendMessage

# Threading event
operation_active = threading.Event()
camera_lock = threading.Lock()  # Only allows one thread to access the camera

# Constants for frame center and offset
CENTER_X, CENTER_Y = 600 // 2, 500 // 2
OFFSET = 20  # Half of the side length of the 100x100 area

# Randomly selects 30 (x, y) pixels within the defined area
random_coords = [
    (np.random.randint(CENTER_X - OFFSET, CENTER_X + OFFSET),
     np.random.randint(CENTER_Y - OFFSET, CENTER_Y + OFFSET)) for _ in range(30)
]

def measure_color_change(frame, pixels):
    """
    Extract the RGB values of the specified pixels for a given frame
    and returns the average color values.
    """
    color_values = []
    for x, y in pixels:
        color_values.extend(frame[y, x])
    return np.mean(color_values)

def initialize_camera():
    #Initializes and configures the Picam with preview settings.
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration()
    picam2.configure(camera_config)
    return picam2

def capture_frame(picam2):
    #Captures a single frame from the camera
    frame = picam2.capture_array()
    frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(frame_bw, cv2.COLOR_GRAY2RGB)

def calculate_offset(temp_array):
    #Calculatea the baseline offset value from the mean of the temporary array
    base_val = np.mean(temp_array)
    return base_val - 60  # Adjust detection sensitivity as needed

def process_frame(picam2, pixels_to_measure, temp_array, stdev_array, offset, frame_size, start_time):
    """
    Process a single frame: captures, converts, and measures the color change.
    Updates the temp_array and checks for standard deviation threshold.
    """
    frame_rgb = capture_frame(picam2)
    mean_color_value = measure_color_change(frame_rgb, pixels_to_measure)
    temp_array.append(mean_color_value)

    if len(temp_array) == temp_array.maxlen:
        if frame_size == (temp_array.maxlen - 1):
            offset = calculate_offset(temp_array)

        adjusted_mean = np.mean(temp_array) - offset
        if adjusted_mean > 80:  # Threshold for mean value
            stdev = np.std(np.array(temp_array) - offset)
            stdev_array.append(stdev)

            if stdev < 1.5:  # Threshold for standard deviation indicating stabilization
                elapsed_time = time.time() - start_time
                print(f"Time measured through framesize: {frame_size / 30:.2f}")
                print(f"Time in seconds: {elapsed_time:.2f}")
                return False  # Stop processing as reaction is complete

    return True  # Continue processing

def running_alg():
    """Run the main algorithm to monitor color change and detect the reaction completion."""
    with camera_lock:
        # Initialize camera and data structures
        picam2 = initialize_camera()
        picam2.start_preview(Preview.QTGL)
        picam2.start()
        time.sleep(1)

        temp_array = deque(maxlen=500)
        stdev_array = []
        frame_size = 0
        offset = 0
        start_time = time.time()
        pixels_to_measure = random_coords

        try:
            while operation_active.is_set():
                if not process_frame(picam2, pixels_to_measure, temp_array, stdev_array, offset, frame_size, start_time):
                    break  # Stop processing if reaction is detected as complete
                frame_size += 1
        finally:
            picam2.stop_preview()
            picam2.close()
