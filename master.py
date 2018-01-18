import cv2
import yaml
import numpy as np
from scipy import ndimage
from matplotlib import pyplot as plt

'''dont change'''
def undistort(frame):
    with open('data.yaml', 'r') as a:
        doc = yaml.load(a)
    newmtx = doc["camera_matrix"]
    newdist = doc["dist_coeff"]
    img = frame
    h,  w = img.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(newmtx,newdist,(w,h),1,(w,h))
    #---undistort
    mapx,mapy = cv2.initUndistortRectifyMap(newmtx,newdist,None,newcameramtx,(w,h),5)
    dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)
    # crop the image
    x,y,w,h = roi
    result = dst[y:y+h, x:x+w]
    result = cv2.flip(result,0)
    result = cv2.flip(result,1)
    cv2.imwrite('D:\Coding\Eclipse\ImageRecognition\TestSample\main.jpg', result)

'''fancy display'''
def displayImg(img1, img2):
    plt.switch_backend('TkAgg')
    figsize = (3,9);
    plt.rcParams["figure.figsize"] = figsize
    plt.subplot(121),plt.imshow(img1,cmap = 'gray')
    plt.title('Detected Component'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(img2,cmap = 'gray')
    plt.title('Identified Location'), plt.xticks([]), plt.yticks([])
    plt.suptitle('Display')
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    plt.show(block=False)
    plt.waitforbuttonpress(0)

def convPixel(myTuple, pixLoc):
    k1 = (myTuple[4][0] - myTuple[3][0]) / (myTuple[1][0] - myTuple[0][0])
    k2 = (myTuple[5][1] - myTuple[3][1]) / (myTuple[2][1] - myTuple[0][1])
    realX = (int)((pixLoc[0] - myTuple[0][0])*k1 + myTuple[3][0])
    realY = (int)(myTuple[3][1] - (pixLoc[1] - myTuple[0][1])*k2)
    location = (realX, realY);
    return location;
    
'''add this'''
def findLocation(template, img):
    '''rotates through all 4 orientation of template
    returns a tuple of : (location coordinate,
    camera picture with rectangle and dot,
    image of the template at the correct orientation)
    '''
    max = -1.0
    for i in range (0,4):
        #cv2.imshow('template', template)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img,template,method)
        min_value, max_value, min_location, max_location = cv2.minMaxLoc(res)
        if max < max_value:
            max = max_value
            save = template
            rectValue = (min_value, max_value, max_location, w, h);
        template = ndimage.rotate(template,90)
        i+=1
    min_val, max_val, max_loc, w, h = rectValue
    print(min_val, max_val)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    cv2.imwrite('lazybum.jpg',img)
    location = ((int)(top_left[0]+w/2), (int) (top_left[1]+h/2))
    cv2.rectangle(img,top_left, bottom_right, (0,0,255), 5)
    cv2.circle(img, location, 3, (0,255,0), 2)
    #cv2.imshow('window1',img)
    displayImg(save,img)
    result = (location, save, img);
    return result

'''
update these
save camera pic with rect and dot as NameRect.jpg
save correct template with as NameTemp.jpg
'''
def findBattery(img2, method, myTuple):
    template = cv2.imread('battery.jpg',0)
    img = img2.copy()
    location, save, img = findLocation(template,img)
    cv2.imwrite('batteryRect.jpg', img)
    cv2.imwrite('batteryTemp.jpg', save)
    realLoc = convPixel(myTuple, location)
    return realLoc

def findCircuitboard(img2, method, myTuple):
    template = cv2.imread('circuitboard.jpg',0)
    img = img2.copy()
    location, save, img = findLocation(template,img)
    cv2.imwrite('CircuitboardRect.jpg', img)
    cv2.imwrite('CircuitboardTemp.jpg', save)
    realLoc = convPixel(myTuple, location)
    return realLoc
    
def findSounddriver(img2, method, myTuple):
    template = cv2.imread('sounddriver.jpg',0)
    img = img2.copy()
    location, save, img = findLocation(template,img)
    cv2.imwrite('SounddriverRect.jpg', img)
    cv2.imwrite('SounddriverTemp.jpg', save)
    realLoc = convPixel(myTuple, location)
    return realLoc
    
def findMotor(img2, method, myTuple):
    template = cv2.imread('motor.jpg',0)
    img = img2.copy()
    location, save, img = findLocation(template,img)
    cv2.imwrite('MotorRect.jpg', img)
    cv2.imwrite('MotorTemp.jpg', save)
    realLoc = convPixel(myTuple, location)
    return realLoc

#-----Actual Code-----#  
#---Take Picture
#cap = cv2.VideoCapture(0)
#ret, frame = cap.read()
#ret, frame = cap.read()
#undistort(frame)

#cap.release()

img = cv2.imread('D:\Coding\Eclipse\ImageRecognition\Showcase\pic19.jpg',0)
img2 = img.copy()
method = cv2.TM_CCOEFF_NORMED;

LU = (12,11)
RU = (30, 11)
LD = (12, 54)
ALU = (45, 67)
ARU = (73, 67)
ALD = (45, 85)

myTuple = (LU, RU, LD, ALU, ARU, ALD)

print (findBattery(img2, method))
cv2.waitKey(0)
print (findCircuitboard(img2, method))
cv2.waitKey(0)
print (findMotor(img2, method))
cv2.waitKey(0)
print (findSounddriver(img2, method))
cv2.waitKey(0)
