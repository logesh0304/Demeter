import RPi.GPIO as GPIO
import picamera
import time
import birddetect as bd

#TODO 
# [ ] motor in idle state to reduce power
# [ ] cloud pushing

#                   v1          v2          v3
# resolution        5 MP        8 MP        11.9 MP
# cam resolution    2592x1944   3280x2464   4608x2592
# FOV               53.5,41.41  62.2,48.8   66,41

CAM_FOV=(62.2, 48.8) # (xdeg, ydeg)
CAM_FULL_RESOLUTION=(3280,2464)
CAM_RESOLUTION=(640,480) #480p
IMG_FILE='img.jpeg'

ROTATE_STEP=30 #deg 
AIM_THRESHOLD=4.2 # minimum degree 
MAX_REPEL_ATTEMPTS=10
STEP_ANGLE=1.8 #deg #fullstep
COVERAGE=180 #deg

MOTOR_CHANNEL=(29,31,33,35) 
PULSE_TIME=0.01 # 10ms for 180 deg per second
PULSE_SEQUENCE=[(0,1,1,1),      # Wave drive
                (1,0,1,1),
                (1,1,0,1),
                (1,1,1,0)]
BUZZER_PIN=13
BEEP_TIME=3 #sec

GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUZZER_PIN,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(MOTOR_CHANNEL,GPIO.OUT)

cam=picamera.PiCamera()
cam.resolution=CAM_RESOLUTION
#cam.brightness=60

pulse_seq_idx=0
def rotate_stepper_motor(deg): # deg - for left + for right
    global pulse_seq_idx
    steps=abs(int(deg/STEP_ANGLE))
    for i in range(steps):
        if deg>0: # clockwise
            GPIO.output(MOTOR_CHANNEL, PULSE_SEQUENCE[pulse_seq_idx])
            pulse_seq_idx = 0 if pulse_seq_idx==3 else pulse_seq_idx+1
        else:   # anti-clockwise
            GPIO.output(MOTOR_CHANNEL, PULSE_SEQUENCE[pulse_seq_idx])
            pulse_seq_idx = 3 if pulse_seq_idx==0 else pulse_seq_idx-1
        time.sleep(PULSE_TIME)      

def capture_image(img_file):
    cam.capture(img_file)

# need to consider aspect ratio changes
def calc_aim_angle(boxes):
    bcenter=0
    for box in boxes:
        bcenter+=box[0]+(box[2]/2)  # x+(w/2)
    bcenter=bcenter/len(boxes) # Averaging centers of multiple boxes
    angle = (CAM_FOV[0]/CAM_FULL_RESOLUTION[0]) * (bcenter - CAM_RESOLUTION[0]/2) * (CAM_FULL_RESOLUTION[0]/CAM_RESOLUTION[0])
    return angle

def repel():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(BEEP_TIME)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

totrot=0
dirflag=1
def main():
    global totrot
    global dirflag
    print("Peckaway started.")
    bd.initialize()
    try:
        while True:
            capture_image(IMG_FILE)
            boxes=bd.detect(IMG_FILE)
            if len(boxes)>0 :
                # aiming
                aim_angle=calc_aim_angle(boxes)
                if aim_angle>AIM_THRESHOLD :
                    rotate_stepper_motor(aim_angle)
                repel()
                continue # Try to repel untill it goes
            rotate_stepper_motor(dirflag*ROTATE_STEP)
            totrot+=ROTATE_STEP
            if totrot>COVERAGE :
                dirflag*=-1
                totrot=0
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
    

if __name__ == '__main__':
    main()
