import serial
import time


#setting up the connection between the raspberry pi and the arduino
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)

def send_message_to_ard(message):

  try:
    #converts the message in byte format to send to the arduino
    ser.write((message + '\n').encode("utf-8"))
    print("message sent")
  except Exception as e:
    print("Error sending message")
