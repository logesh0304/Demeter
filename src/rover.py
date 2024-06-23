import RPi.GPIO as GPIO
import time

MOTOR_CHANNEL_DRIVE=(8,10,11,13)  # Ar, Ab, Br, Bb on driver
MOVE_DELAY=4

GPIO.setmode(GPIO.BOARD)
GPIO.setup(MOTOR_CHANNEL_DRIVE,GPIO.OUT)

off=(0,0,0,0)
forward=(1,0,1,0)
back=(0,1,0,1)
left=(0,1,1,0)
right=(1,0,0,1)

def run(drive_seq,t):
    GPIO.output(MOTOR_CHANNEL_DRIVE, drive_seq)
    time.sleep(t)
    GPIO.output((MOTOR_CHANNEL_DRIVE), off)
