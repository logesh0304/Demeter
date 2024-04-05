import cv2
import numpy as np
import time

CONFIDENCE_THRESHOlD=0.3
NMS_THRESHOLD=0.4
MODEL_WEIGHTS='./model/model.weights'
MODEL_CONFIG='./model/model.cfg'

net=None
def initialize():
    global net
    print("Loading model..")
    net=cv2.dnn.readNet(MODEL_WEIGHTS,MODEL_CONFIG)
    print("Model loaded")

def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers


def detect(img, show_detections=False):
    image=cv2.imread(img)
    Width = image.shape[1]
    Height = image.shape[0]
    blob=cv2.dnn.blobFromImage(image, 1/255, (416,416), (0,0,0), swapRB=True, crop=False)
    net.setInput(blob)

    start=time.time()
    outs=net.forward(get_output_layers(net))
    end=time.time()
    print("Detected in {:.6f} seconds".format(end-start))

    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            confidence = np.max(scores)
            if confidence > CONFIDENCE_THRESHOlD:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])


    idxs = [idx[0] for idx in cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOlD,NMS_THRESHOLD)]
    print("Birds found:{}".format(len(idxs)))
    

    if show_detections:
        for i in idxs:
            # extract the bounding box coordinates
            (x, y) = (int(boxes[i][0]), int(boxes[i][1]))
            (w, h) = (int(boxes[i][2]), int(boxes[i][3]))
            color=[255,0,0]
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            text = "{:.4f}".format(confidences[i])
            cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.imshow("Image", image)
        cv2.waitKey(0)

    return [boxes[i] for i in idxs]
