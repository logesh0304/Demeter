import cloudinary
import cloudinary.uploader
import thingspeak
from datetime import datetime


import cloudinary
          
cloudinary.config( 
  cloud_name = "dqcqguq0c", 
  api_key = "925586279826923", 
  api_secret = "vNL8AgIflYuTLcL6suhF5lrjw8M" 
)


channel_id=2510276
write_key='ZO9G6U7P5EWBJTA0'

channel=thingspeak.Channel(id=channel_id, api_key=write_key)

def image_push(imgfile, creature, name):
    response=cloudinary.uploader.upload(imgfile, public_id="peckaway_caps", tags=[creature], folder='pecaway_caps')
    return response['url']

def push(imgfile, creature):
    timestamp=datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    name=creature+"_"+timestamp
    try:
        url=image_push(imgfile, creature, name)
        response=channel.update({'field1':timestamp, 'field2': creature, 'field3':url})
    except Exception as e:
        print("cannot upload data!\n\n",e)

