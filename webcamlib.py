#from imgproc import *

# open the webcam
#my_camera = Camera(320, 240)
# grab an image from the camera
#my_image = my_camera.grabImage()
#my_image.save("imgweb.jpg")

from cv2 import *
# initialize the camera
cam = VideoCapture(0)   # 0 -> index of camera
s, img = cam.read()
if s:    # frame captured without any errors
    imwrite("filename.jpg",img) #save image