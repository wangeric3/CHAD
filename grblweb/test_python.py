from socketIO_client import SocketIO
import json, sys
#https://pypi.python.org/pypi/socketIO-client

def on_response(*args):
  print('on_response args are ', args)
  
def start_response(*args):
	socketIO.emit('usePort', 0);
	socketIO.emit('gcodeLine', { "line": "G0 X10 Y10" });
  
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

socketIO.on('ports', on_response)
socketIO.on('config', on_response)
socketIO.on('start', start_response)
	#socketIO.on('machineStatus', on_response)


	#socketIO.emit('howareyou', {"name": "Eric" })
socketIO.wait(seconds=10)
	# You can use  socketIO.wait() to listen forever