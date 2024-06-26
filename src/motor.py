import RPi.GPIO as GPIO
import time

MOTOR_CHANNEL_DRIVE=(29,31,33,35)  # Ar, Ab, Br, Bb on driver

GPIO.setmode(GPIO.BOARD)
GPIO.setup(MOTOR_CHANNEL_DRIVE,GPIO.OUT)

left=(0,1,1,0)
straight=(1,0,1,0)
right=(1,0,0,1)
off=(0,0,0,0)

def run(dt,t):
    GPIO.output(MOTOR_CHANNEL_DRIVE, dt)
    time.sleep(t)
    GPIO.output((MOTOR_CHANNEL_DRIVE), off)

def main():
    i=int(input(":time:>"))
    d=input("dir>")
    print(d)
    if d=='l': 
        run(left,i)
    elif d=='s': 
        run(straight,i)
    elif d=='r': 
        run(right,i)

if __name__=="__main__":
    main()