import RPi.GPIO as GPIO
import time
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

GPIO.output(motorE,GPIO.HIGH)
GPIO.output(pumpA,GPIO.HIGH)
GPIO.output(sol,GPIO.HIGH)

time.sleep(1)


GPIO.output(motorE,GPIO.LOW)
GPIO.output(pumpA,GPIO.LOW)
GPIO.output(sol,GPIO.LOW)
GPIO.cleanup()