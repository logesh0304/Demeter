import random
import time
import paho.mqtt
from paho.mqtt import client as mqtt_client

broker = 'broker.emqx.io'
port = 1883
topic_command ="demeter/command"
topic_status = "demeter/status"
topic_notification = "demeter/notification"
client_id = "demeter_rpi"
client=None
username = 'emqx'
password = 'public'

pwflag=0

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Successfully connected.")
        else:
            print("Failed to connect, return code %d\n", rc)
    
    global client

    if paho.mqtt.__version__[0]>'1':
      client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    else:
       client = mqtt_client.Client(client_id)
  
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    print("Connecting to  MQTT broker...")
    client.connect(broker, port)
    subscribe()
    client.loop_start()
    

#publish notification
def publish_notification(msg):
  result = client.publish(topic_notification, msg)
  # result: [0, 1]
  status = result[0]
  if status == 0:
     print(f"Send `{msg}` to topic `{topic_notification}`")
  else:
     print(f"Failed to send notification {msg}")


#publish status
def publish_status(msg):
  result = client.publish(topic_status, msg)
  # result: [0, 1]
  status = result[0]
  if status == 0:
     print(f"Send `{msg}` to topic `{topic_status}`")
  else:
     print(f"Failed to send status {msg}")
  
#subscribe
def subscribe():
    global client
    def on_message(client, userdata, msg):
        global pwflag
        print("Received command: "+msg.payload.decode())
        if(msg.payload.decode() == "On"):
          pwflag=1
          publish_status("running")
        elif(msg.payload.decode() == "Off"):
          pwflag=0
          publish_status("not_running")
    client.subscribe(topic_command)
    client.on_message = on_message