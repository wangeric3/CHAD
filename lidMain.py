import time
from cv2 import *
import numpy as np
from socketIO_client import SocketIO
import sys
import RPi.GPIO as GPIO
import random
#mm location of lid
xlid = 50
ylid = 140
zlid = 20
#mm location of image
xcam = 100
ycam = 126
camd = 90
#pixel dimen of image
w = 472
h = 302
#mm to pixel ratio
k = 20/140
#mm location and amount of bins
ybin = 15
numbins = 3

cam = VideoCapture(0)

step = 0
type = -1
loop = 0
i = 4
status = 'na'

GPIO.setmode(GPIO.BOARD) 
motorE = 11
pumpA = 13
sol = 7
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
	# go to lid
	global step = -1
	socketIO.emit('chadMove', { "line": "G1 X"+str(xlid)+" Y"+str(ylid)+" Z"+str(zlid)+" F2500"})
	socketIO.on('machineStatus', on_machine_status)
	
def slide():
	global step = -2
	socketIO.emit('chadMove', { "line": "G1"+str(lidx+23)+" F2500"})
	socketIO.on('machineStatus', on_machine_status)

def usurpLid():
	global step = -3
	socketIO.emit('chadMove', { "line": "G1 Z0 F2500"})
	socketIO.on('machineStatus', on_machine_status)
	
def throwLid():
	global step = 1
	socketIO.emit('chadMove', { "line": "G1 X90 Y140 F2500"})
	socketIO.on('machineStatus', on_machine_status)
	
def phaseOne(*args):
	global step
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
	step = 3
	s, img = cam.read()
	imwrite("img.jpg",img)
    #JOSH'S SHIT GOES HERE
	#processImg() returns dict(xp,yp,type)
	i -= 1
	type = i #change
	socketIO.emit('bundle', {'loop': loop, 'event': 0, 'type': type})
	print ("Component Type: {}".format(type))
	if type != 0:
		xp = 320 #change
		yp = 240 #change
		X = xcam-(w*k)/2-xp*k
		Y = (ycam+camd-(h*k)/2+yp*k)
		gmove = "G1 X" + str(X) + " Y" + str(Y) + " F2500"
		print ("Component is at: ")
		print (gmove)
		socketIO.emit('bundle', {'loop': loop, 'event': 1, 'type': type})
		socketIO.emit('chadMove', { "line": gmove })
		socketIO.emit('chadMove', { "line": "G1 Z-10 F2500" })
		#time.sleep(1)
		socketIO.on('machineStatus', on_machine_status)
	else:
		print ("Nothing Left, Going Home!")
		socketIO.emit('chadMove', { "line": "G1 X0 Y0 F2500"});
		socketIO.emit('done');
		GPIO.output(motorE,GPIO.LOW)
		GPIO.output(pumpA,GPIO.LOW)
		GPIO.output(sol,GPIO.LOW)
		GPIO.cleanup()
		sys.exit()

def phaseThree():
	global step
	global type
	global loop
	step = 1
	GPIO.output(pumpA,GPIO.HIGH)
	time.sleep(.5)
	#if loop == 0:
		#time.sleep(1.5)
	socketIO.emit('bundle', {'loop': loop, 'event': 2, 'type': type})
	xbin = (type*160)/numbins - 160/(2*numbins)
	gbin = "G1 X" + str(xbin) + " Y" + str(ybin) + " F2500"
	print ("Bin is at: ")
	print (gbin)
	socketIO.emit('bundle', {'loop': loop, 'event': 3, 'type': type})
	socketIO.emit('chadMove', { "line": "G1 Z0 F2500" })
	socketIO.emit('chadMove', { "line": gbin});
	#time.sleep(1)
	socketIO.on('machineStatus', on_machine_status)
	
def on_machine_status(*args):
	global step
	global status
	print("current: "+args[0]['status'])
	print("previous: "+status)
	if(args[0]['status'] == 'Idle') and (status == 'Run'):
		socketIO.off('machineStatus')
		status = 'na'
		if (step==-1):
			GPIO.output(pumpA,GPIO.HIGH)
			slide()
		elif (step==-2):
			usurpLid()
		elif (step==-3):
			GPIO.output(sol,GPIO.HIGH)
			GPIO.output(pumpA,GPIO.LOW)
			time.sleep(1)
			GPIO.output(sol,GPIO.LOW)
			throwlid()
		elif (step==1):
			global loop
			GPIO.output(sol,GPIO.HIGH)
			GPIO.output(pumpA,GPIO.LOW)
			time.sleep(1)
			GPIO.output(sol,GPIO.LOW)
			socketIO.emit('bundle', {'loop': loop, 'event': 4, 'type': type})
			loop += 1
			phaseOne()
		elif (step==2):
			phaseTwo()
		elif (step==3):
			phaseThree()
	else:
		status = args[0]['status']
	
def on_end():
	print("Something's Wrong! STOP!")
	GPIO.output(motorE,GPIO.LOW)
	GPIO.output(pumpA,GPIO.LOW)
	GPIO.output(sol,GPIO.LOW)
	GPIO.cleanup()
	sys.exit()


socketIO.on('start', on_start)
socketIO.on('end', on_end)
#socketIO.on('manualPump', on_pump);
socketIO.wait()
