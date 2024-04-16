import RPi.GPIO as GPIO
import time
import birddetect as bd
import cloudpush as cp
import pygame
import cv2
import random

#TODO 
# [ ] motor in idle state to reduce power
# [ ] cloud pushing

#					v1			v2			v3
# resolution 		5 MP		8 MP		11.9 MP
# cam resolution 	2592x1944	3280x2464	4608x2592
# FOV 				53.5,41.41	62.2,48.8 	66,41

# CAM_FOV=(62.2, 48.8) # (xdeg, ydeg) 
# CAM_FULL_RESOLUTION=(3280,2464) 	
CAM_RESOLUTION=(640,480) #480p
IMG_FILE='cap.jpeg'

ROTATE_ANGLE=30 #deg 
ROTATE_DELAY=1 #sec

# AIM_THRESHOLD=4.2 # minimum degree 
MAX_REPEL_ATTEMPTS=3
STEP_ANGLE=1.8 #deg #fullstep
COVER_ANGLE=180

SOUND_PLAY_TIME=3 # sec
SOUNDS_DIRECTORY='./sounds/'
SOUND_VOLUME=0.1

MOTOR_CHANNEL=(29,31,33,35) 
PULSE_TIME=0.01 # 10ms for 180 deg per second
PULSE_SEQUENCE=[(1,0,0,0),		# Wave drive
                (0,1,0,0),
                (0,0,1,0),
                (0,0,0,1)]

GPIO.setmode(GPIO.BOARD)
GPIO.setup(MOTOR_CHANNEL,GPIO.OUT)

cam = cv2.VideoCapture(0)
cam.set(3,CAM_RESOLUTION[0])
cam.set(4,CAM_RESOLUTION[1])

pygame.mixer.init()

bird_sound_files=['hawk.wav', 'shotgun.wav', 'machinegun.wav']
animal_sound_files={'person':'beebuzz.wav',
                    'dog':'dogbeep.wav',
                    'cat':'catbeep.wav',
                    'cow':'dogsbark.wav',
                    'elephant':'beebuzz.wav',
                    'bear':'beep.wav',
                    'horse':'thunder.wav',
                    'sheep':'dogsbark.wav',
                    'giraffe':'shotgun.wav',
                    'zebra':'thunder.wav'}

pulse_seq_idx=0
def rotate_stepper_motor(deg): # deg - for left + for right
    global pulse_seq_idx
    steps=abs(int(deg/STEP_ANGLE))
    for i in range(steps):
        if deg>0: # clockwise
            GPIO.output(MOTOR_CHANNEL, PULSE_SEQUENCE[pulse_seq_idx])
            pulse_seq_idx = 0 if pulse_seq_idx==3 else pulse_seq_idx+1
        else:	# anti-clockwise
            GPIO.output(MOTOR_CHANNEL, PULSE_SEQUENCE[pulse_seq_idx])
            pulse_seq_idx = 3 if pulse_seq_idx==0 else pulse_seq_idx-1
        time.sleep(PULSE_TIME)
        

def capture_image(write=False):
    global cam
    success, img = cam.read()
    if success:
        if write:
            cv2.imwrite(IMG_FILE, img)
        return img
    print("Image capture failed\nretrying\n")
    cam = cv2.VideoCapture(0)
    cam.set(3,CAM_RESOLUTION[0])
    cam.set(4,CAM_RESOLUTION[1])
    return capture_image(write)
    

def play_sound(soundfile, playtime=SOUND_PLAY_TIME):
    sound = pygame.mixer.Sound(soundfile)
    sound.set_volume(SOUND_VOLUME)
    playing = sound.play(loops=-1)
    time.sleep(playtime)
    playing.stop()
 
def repel(creature, attempt):
    
    if attempt>MAX_REPEL_ATTEMPTS:
        print("Can't repel Birds")
    else:
        if creature=='bird':
            soundfile=random.choice(bird_sound_files)
        else :
            soundfile=animal_sound_files[creature]
        play_sound(SOUNDS_DIRECTORY+soundfile)

def main():
    print("Peckaway started.")
    bd.initialize()
    attempt=1
    curent_angle=COVER_ANGLE/2
    rdir=1
    try:
        while True:
            if curent_angle>COVER_ANGLE or curent_angle<0:
                rdir*=-1

            creature=bd.detect(capture_image(True))
            if creature :
                if attempt<=MAX_REPEL_ATTEMPTS+1 : 
                    repel(creature, attempt)
                    cp.push(IMG_FILE, creature)
                    attempt+=1
                    continue # Try to repel untill it goes

            rotate_stepper_motor(rdir*ROTATE_ANGLE)
            curent_angle+=rdir*ROTATE_ANGLE
            attempt=1
            time.sleep(ROTATE_DELAY)
            # cloud push
    except KeyboardInterrupt as ke:
        print(ke)
    finally:
        GPIO.cleanup()
        cam.release()
    

if __name__ == '__main__':
    main()
