import serial
from time import sleep
import navigate as nav
import math

ser=None

STEPDIST=30 #cm
SPEED = 23.5 #cm/sec
TURN_DELAY=1 #sec for 90 deg turn

pos=[0,0]
heading=0

def init():
  global ser
  ser=serial.Serial("/dev/ttyS0", 19200)
  print("Serial port initialized.")
  nav.init_field()
  
def close():
  ser.close()
  
def rundelay(dist): # dist in cm, delay in s
  return (dist/SPEED)
  
def updatepos(dist):
  if heading==0: pos[0]+=dist
  elif heading==2 or heading==-2 : pos[0]-=dist
  elif heading==-1 : pos[1]-=dist
  else : pos[1]+=dist
  
def runstep():
  exec_cmd("FWD")
  sleep(rundelay(STEPDIST))
  exec_cmd("STP")
  updatepos(STEPDIST)

def run_to_target(target_dist, langle):
  global pos, heading
  gangle=to_gangle(langle)
  target= round(target_dist*math.cos(gangle) + pos[0]) , round(target_dist*math.sin(gangle) + pos[1])
  seq, dest, fheading=nav.get_move_seq(pos,target,heading)
  print("Motion sequence:", seq)
  for cmd in seq:
    if len(cmd)==1:
      exec_cmd(cmd[0])
      if cmd[0]=="UTRN":
        sleep(2*TURN_DELAY)
      else:
        sleep(TURN_DELAY)
      exec_cmd("STP")

    else:
      exec_cmd(cmd[0])
      sleep(rundelay(int(cmd[1])))
      exec_cmd("STP")
    heading=fheading
    pos=list(dest)

def to_gangle(langle):
  if heading==0: ulangle=langle
  elif heading==2 or heading==-2 : ulangle = langle+180
  elif heading==-1 : ulangle=langle+90
  else : ulangle = langle+270
  return ulangle%360
  
def exec_cmd(cmd):
  print("Sent command: "+cmd+";")
  ser.write((cmd+";").encode())
  wait_till_done()

def wait_till_done():
  ack=ser.read_until(b";").decode()
  if ack=="DONE":
    return True
  elif ack=="ERR":
    raise Exception("Error from arduino: "+ser.read_until(b";").decode())
 # else:
#  raise Exception("Acknoledgement not received from arduino !")