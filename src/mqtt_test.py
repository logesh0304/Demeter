import mqtt_control as mq

mq.connect_mqtt()
while(True):
    mq.publish_status(input(">"))
    print(mq.pwflag)