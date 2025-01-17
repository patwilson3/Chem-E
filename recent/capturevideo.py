from picamera2 import Picamera2, Preview
import time

def record(path, duration):
	picam2 = Picamera2()
	camera_config = picam2.create_preview_configuration()
	picam2.configure(camera_config)
	picam2.start_preview(Preview.QTGL)
	picam2.start()
	time.sleep(2)
	picam2.start_and_record_video(f"/home/tests/{path}.mp4", duration=duration)

record("test1", 10)
