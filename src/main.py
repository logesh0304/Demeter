import RPi.GPIO as GPIO
import time
import pygame
import cv2
import random

import birddetect as bd
import cloudpush as cp
import rover 
import mqtt_control as mqtt_c

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
COVER_ANGLE=360

SOUND_PLAY_TIME=5 # sec
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


pygame.mixer.init()

bird_sound_files=['catbeep.wav', 'hawk.wav', 'shotgun.wav', 'machinegun.wav']
animal_sound_files={'person':'machinegun.wav',
                    'dog':'dogbeep.wav',
                    'cat':'catbeep.wav',
                    'cow':'dogsbark.wav',
                    'elephant':'beebuzz.wav',
                    'bear':'beep.wav',
                    'horse':'thunder.wav',
                    'sheep':'dogsbark.wav',
                    'giraffe':'shotgun.wav',
                    'book':'beep.wav',
                    'zebra':'thunder.wav'}

# Tunable
cheights = {'person':100,  # it draws bunding box for half the person also
                    'bird':15,
                    'dog':50,
                    'cat':20,
                    'cow':120,
                    'elephant':250,
                    'bear':160,
                    'horse':140,
                    'sheep':100,
                    'giraffe':450,
                    'book':20,
                    'zebra':110}

pulse_seq_idx=0

cam=None
def init_camera():
    global cam
    cam = cv2.VideoCapture(0)
    cam.set(3,CAM_RESOLUTION[0])
    cam.set(4,CAM_RESOLUTION[1])
    print("Camera initialized.")

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
        
def capture_image():
    global cam
    success, img = cam.read()
    if success:
        return img
    print("Image capture failed\nretrying\n")
    # Reinitiating camera & retrying
    cam.release()
    init_camera()
    return capture_image()
    

def play_sound(soundfile, playtime=SOUND_PLAY_TIME):
    sound = pygame.mixer.Sound(soundfile)
    sound.set_volume(SOUND_VOLUME)
    playing = sound.play(loops=-1)
    time.sleep(playtime)
    playing.stop()
 
def repel(creature, attempt):
    rover.exec_cmd('LSR')
    if creature=='bird':
        soundfile=random.choice(bird_sound_files)
    else :
        soundfile=animal_sound_files[creature]
    play_sound(SOUNDS_DIRECTORY+soundfile)

# Executed when can't able to repel 
def final_act():
    mqtt_c.publish_notification("Can't repel.")

error=None
def main():
    print("Peckaway started.")
    bd.initialize()
    init_camera()
    rover.init()
    mqtt_c.connect_mqtt()
    attempt=1
    rdir=-1 # left
    langle=0

    try:
        while True:
            if mqtt_c.pwflag==0:
              continue
            for i in range (int(COVER_ANGLE/ROTATE_ANGLE)): 
              
                # wait shoot wait to prevent shake
                time.sleep(ROTATE_DELAY/2)
                # Executes until the creature is repelled, if repelled or nothing found attempt resets
                # else try again and if more than max attempts reached else part of while loop
                while (attempt<=MAX_REPEL_ATTEMPTS):
                    img=capture_image()
                    for i in range(3): # try three time to check ifcreatur detected
                        creature, pixheight=bd.detect(img)
                        if creature:
                            break
                    print("Creatures found:",creature)
                    if creature : 
                        dist=bd.calc_object_dist(cheights[creature],pixheight)
                        if dist>0:
                          rover.run_to_target(dist,langle)
                        repel(creature, attempt)
                        cv2.imwrite(IMG_FILE, img)
                        cp.push(IMG_FILE, creature)
                        attempt+=1
                    else: 
                        break
                else: # This executes only if attempt > MAX_REPEL_ATTEMPT
                    final_act()
                attempt=1

                rotate_stepper_motor(rdir*ROTATE_ANGLE)
                langle+=rdir*ROTATE_ANGLE
                time.sleep(ROTATE_DELAY/2)
                if mqtt_c.pwflag==0:
                  break
            if mqtt_c.pwflag==0:
              continue
            rdir*=-1 # rotation is reversed each time to prevent spinning of wires

            #rover motion
            rover.runstep()

    except KeyboardInterrupt as ke:
        global error
        error=ke
    except Exception as e:
        error=e
    finally:
        mqtt_c.publish_notification("Rover unexpectedly Stopped working !!")
        mqtt_c.publish_status("not_running")
        GPIO.cleanup()
        cam.release()
        rover.close()
        raise error
    

if __name__ == '__main__':
    main()
