import os
import cv2
import numpy as np

# https://stackoverflow.com/questions/25724923/opencv-how-do-i-implement-keystone-correction
#This code performs a keystone correction, you click to give the coordinates of the trapezoid the image should be fitting to, and it fits the image to that trapezoid

pSrc = [(  98,67),( 331 ,  75),( 415 , 469),(  27 , 466)]
pDst = [(  27,67),( 415 ,  75),( 415 , 469),(  27 , 466)]
def srcMouse(event, x, y, flags,params):
    global pSrc
    if event == cv2.EVENT_LBUTTONDOWN:

        if len(pSrc) >=4:
            pSrc=[]
        pSrc.append((x,y))
        print(np.array(pSrc,dtype=np.float32))

def dstMouse(event, x, y, flags,params):
    global pDst
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(pDst) >=4:
            pDst=[]
        pDst.append((x,y))

cv2.namedWindow('src')
cv2.setMouseCallback('src', srcMouse, 0)
cv2.namedWindow('dst')
cv2.setMouseCallback('dst', dstMouse, 0)

im = cv2.imread(os.path.join("misc_images", 'image.png'))
dst = np.zeros(im.shape,dtype=np.uint8)
while(1):
    imD = im.copy()
    dstD = dst.copy()
    for p in pSrc:
        cv2.circle(imD,p,2,(255,0,0),-1)
    for p in pDst:
        cv2.circle(dstD,p,2,(255,0,0),-1)

    if len(pSrc)==4 and len(pDst)==4:
        H = cv2.findHomography(np.array(pSrc,dtype=np.float32),np.array(pDst,dtype=np.float32),cv2.LMEDS)
        dstD=cv2.warpPerspective(imD,H[0],(dstD.shape[1],dstD.shape[0]))
    cv2.imshow('src',imD)
    cv2.imshow('dst',dstD)
    if cv2.waitKey(1) ==27:
        exit(0)   

