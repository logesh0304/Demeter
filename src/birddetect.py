import cv2
import time

CONFIDENCE_THRESHOlD=0.45
NMS_THRESHOLD=0.3
WEIGHTSFILE='./model/frozen_inference_graph.pb'
CONFIGFILE='./model/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
CLASSFILE='./model/coco.names'

classNames=[]
myClass=['bird','cat', 'dog', 'horse','sheep', 'cow', 'elephant','bear','zebra', 'giraffe', 'book']

net=None
def initialize():
    global net, classNames

    with open(CLASSFILE,"rt") as f:
        classNames = f.read().rstrip("\n").split("\n")

    print("Loading model..")
    net = cv2.dnn_DetectionModel(WEIGHTSFILE,CONFIGFILE)
    net.setInputSize(320,320)
    net.setInputScale(1.0/ 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)
    print("Model loaded")

focal_length=960
def calc_object_dist(true_height, pixel_height):
  dist = round((true_height*focal_length)/pixel_height);
  print("at distance:",dist)
  return dist

def detect(img, draw=False, detectclasses=myClass):

    start=time.time()
    classIds, confs, bbox = net.detect(img,confThreshold=CONFIDENCE_THRESHOlD,nmsThreshold=NMS_THRESHOLD)
    end=time.time()
    #print("Detected in {:.6f} seconds".format(end-start))

    findings=[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in detectclasses:
                findings.append([box, className, confidence])    

    if (draw):
        for box, className, confidence in findings:
            cv2.rectangle(img,box,color=(0,255,0),thickness=2)
            cv2.putText(img,className.upper(),(box[0]+10,box[1]+30),
            cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
            cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
            cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
        
        cv2.imshow("Output",img)
        cv2.waitKey(1)
        cv2.destroyAllWindows()

    foundedcls=[f[1] for f in findings]
    confs=[f[2] for f in findings]
    boxs=[f[0] for f in findings]
    creature=""
    finbox=[0,0,0,0]
    if len(foundedcls)>1:
        idx=confs.index(max(confs))
        creature=foundedcls[idx]
        finbox=boxs[idx]
    elif len(foundedcls)==1:
        creature=foundedcls[0]
        finbox=boxs[0]
    #print("Creatures found:",creature)
    return creature, int(finbox[3]-finbox[1])
  
