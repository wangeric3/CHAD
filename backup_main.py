import time
from cv2 import *
import cv2
import numpy as np
from socketIO_client import SocketIO
import sys
import RPi.GPIO as GPIO
import random
import yaml
#z -34 other, -37 motor,  
#mm location of lid
xlid = 50
ylid = 140
#mm location of image
xcam = 100
ycam = 126
camd = 104
#pixel dimen of image
wpic = 472
hpic = 302
#mm to pixel ratio
k = 43/94
#mm location and amount of bins
ybin = 115

cam = VideoCapture(0)

step = 1
type = -1
loop = 0
status = 'na'
partList = [1,2,3,4]
coords = (0,0)

GPIO.setmode(GPIO.BOARD) 
motorE = 18
pumpA = 16
sol = 12
GPIO.setup(motorE,GPIO.OUT)
GPIO.setup(pumpA,GPIO.OUT)
GPIO.setup(sol,GPIO.OUT)
GPIO.output(motorE,GPIO.LOW)
GPIO.output(pumpA,GPIO.LOW)
GPIO.output(sol,GPIO.LOW)

#Activate Enables
GPIO.output(motorE,GPIO.HIGH)



def callback(*args):
	print(args);
	# if not Worker, throw exception
	if(args[0] != 'Worker'):
		print('[ERROR] Handshake Unsuccessful. Killing process')
		raise ValueError('Server did not accept handshake')
	print('[INFO] Handshake Successful. Starting as Worker Node')


socketIO = SocketIO('localhost', 8000)
# Start handshake
try:
	print('[INFO] Sending Handshake Packet')
	socketIO.emit('handShake', {"clientType": 1}, callback)
	socketIO.wait_for_callbacks(seconds=1) # wait for response packet
except Exception as e:
	sys.exit(e);

def on_start(*args):
	global step
	global loop
	if (loop==0):
		random.shuffle(partList)
	step = 2
	#Move to take pic
	imgloc = "G1 X"+str(xcam)+" Y"+str(ycam)+" F2500"
	socketIO.emit('chadMove', { "line": imgloc})
	#time.sleep(1)
	socketIO.on('machineStatus', on_machine_status)
	
def phaseTwo():
	global step
	global type
	global loop
	global i
	global xbin
	step = 3
	s, frame = cam.read()
	undistort(frame)
	img2 = cv2.imread('images/mainPic.jpg',0)
	method = cv2.TM_CCOEFF_NORMED;
	if (loop>3):
		print ("Nothing Left, Going Home!")
		socketIO.emit('chadMove', { "line": "G1 X0 Y0 F2500"});
		socketIO.emit('done');
		GPIO.output(motorE,GPIO.LOW)
		GPIO.output(pumpA,GPIO.LOW)
		GPIO.output(sol,GPIO.LOW)
		GPIO.cleanup()
		sys.exit()
	elif (partList[loop] == 1):
		type = 1
		xbin = 155
		coords = findBattery(img2, method)
	elif (partList[loop] == 2):
		type = 2
		xbin = 95
		coords = findCircuitboard(img2, method)
	elif (partList[loop] == 3):
		type = 3
		xbin = 50
		coords = findSounddriver(img2, method)
	elif (partList[loop] == 4):
		type = 4
		xbin = 5
		coords = findMotor(img2, method)
	socketIO.emit('bundle', {'loop': loop, 'event': 0, 'type': type})
	print ("Component Type: {}".format(type))
	print (*partList)
	print ("Loop "+str(loop))
	xp = coords[0] #change
	yp = coords[1] #change
	print("pixel: "+str(xp)+", "+str(yp))
	if (type==1):
		X = 106
		Y = 27
		Z = -35.5
		#xoff = 13
		#yoff = 20
	elif (type==2):
		X = 115
		Y = 57
		Z = -35
		#xoff = 12
		#yoff = 11
	elif (type==3):
		X = 73
		Y = 54
		Z = -35
		#xoff = 17
		#yoff = 13
	elif (type==4):
		X = 64
		Y = 31
		Z = -37
		#xoff = 17
		#yoff = 18
	#X = (xcam-(wpic*k)/2+xp*k)-xoff
	#Y = (ycam-camd+(hpic*k)/2-yp*k)-yoff
	#Y = ycam-camd-(hpic*k)/2+(hpic-yp)*k
	#Y = ycam-camd-(hpic*k)/2+yp*k
	gmove = "G1 X" + str(X) + " Y" + str(Y) + " F2500"
	print ("Component is at: ")
	print (gmove)
	socketIO.emit('bundle', {'loop': loop, 'event': 1, 'type': type})
	socketIO.emit('chadMove', { "line": gmove })
	socketIO.emit('chadMove', { "line": "G1 Z"+str(Z)+" F1500" })
	time.sleep(1)
	socketIO.on('machineStatus', on_machine_status)
		

def on_machine_status(*args):
	global step
	global status
	print("current: "+args[0]['status'])
	print("previous: "+status)
	if(args[0]['status'] == 'Idle') and (status == 'Run'):
		socketIO.off('machineStatus')
		status = 'na'
		if (step==1):
			global loop
			GPIO.output(sol,GPIO.HIGH)
			GPIO.output(pumpA,GPIO.LOW)
			time.sleep(1)
			GPIO.output(sol,GPIO.LOW)
			socketIO.emit('bundle', {'loop': loop, 'event': 4, 'type': type})
			loop += 1
			on_start()
		elif (step==2):
			phaseTwo()
		elif (step==3):
			phaseThree()
	else:
		status = args[0]['status']
			

def phaseThree():
	global step
	global type
	global loop
	global xbin
	step = 1
	GPIO.output(pumpA,GPIO.HIGH)
	time.sleep(.5)
	#if loop == 0:
		#time.sleep(1.5)
	socketIO.emit('bundle', {'loop': loop, 'event': 2, 'type': type})
	#xbin = (type*160)/numbins - 160/(2*numbins)
	gbin = "G1 X" + str(xbin) + " Y" + str(ybin) + " F2500"
	print ("Bin is at: ")
	print (gbin)
	socketIO.emit('bundle', {'loop': loop, 'event': 3, 'type': type})
	socketIO.emit('chadMove', { "line": "G1 Z0 F1500" })
	socketIO.emit('chadMove', { "line": gbin});
	time.sleep(1)
	socketIO.on('machineStatus', on_machine_status)
	
def on_end():
	print("Something's Wrong! STOP!")
	GPIO.output(motorE,GPIO.LOW)
	GPIO.output(pumpA,GPIO.LOW)
	GPIO.output(sol,GPIO.LOW)
	GPIO.cleanup()
	sys.exit()

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
	cv2.imwrite('images/mainPic.jpg', result)

def findBattery(img2, method):
        #---Apply template Matching
    template = cv2.imread('images/battery.jpg',0)
    w, h = template.shape[::-1]
    img = img2.copy()
    res = cv2.matchTemplate(img,template,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #print(tname)
    print(min_val, max_val)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(img,top_left, bottom_right, (0,255,0), 5)
    cv2.imwrite('grblweb/images/BatteryRect.jpg',img)
    location = (top_left[0]+w/2, top_left[1]+h/2)
    return location

def findCircuitboard(img2, method):
        #---Apply template Matching
    template = cv2.imread('images/circuitboard.jpg',0)
    w, h = template.shape[::-1]
    img = img2.copy()
    res = cv2.matchTemplate(img,template,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #print(tname)
    print(min_val, max_val)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(img,top_left, bottom_right, (0,255,0), 5)
    cv2.imwrite('grblweb/images/CircuitboardRect.jpg',img)
    location = (top_left[0]+w/2, top_left[1]+h/2)
    return location
    
def findSounddriver(img2, method):
        #---Apply template Matching
    template = cv2.imread('images/sounddriver.jpg',0)
    w, h = template.shape[::-1]
    img = img2.copy()
    res = cv2.matchTemplate(img,template,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #print(tname)
    print(min_val, max_val)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(img,top_left, bottom_right, (0,255,0), 5)
    cv2.imwrite('grblweb/images/SounddriverRect.jpg',img)
    location = (top_left[0]+w/2, top_left[1]+h/2)
    return location
    
def findMotor(img2, method):
        #---Apply template Matching
    template = cv2.imread('images/motor.jpg',0)
    w, h = template.shape[::-1]
    img = img2.copy()
    res = cv2.matchTemplate(img,template,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #print(tname)
    print(min_val, max_val)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(img,top_left, bottom_right, (0,255,0), 5)
    cv2.imwrite('grblweb/images/MotorRect.jpg',img)
    location = (top_left[0]+w/2, top_left[1]+h/2)
    return location

socketIO.on('start', on_start)
socketIO.on('end', on_end)
#socketIO.on('manualPump', on_pump);
socketIO.wait()
