import cv2

# F = (Ph*D)/H
# Ph=480p

# Trial1    D=62cm     H=31cm       F=960
# Trial2    D=38.5cm   H=19cm       F=972.63
# Trial3    D=82cm     H=41.5cm     F=948.43
#                                 Avg=960

cap=cv2.VideoCapture(2)
cap.set(3,640)
cap.set(4,480)

while True:
    success, img = cap.read()
    #print(objectInfo)
    cv2.imshow("Output",img)
    cv2.waitKey(1)
