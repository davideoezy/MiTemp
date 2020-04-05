#!/usr/bin/python3 -u
#!/home/openhabian/Python3/Python-3.7.4/python -u
#-u to unbuffer output. Otherwise when calling with nohup or redirecting output things are printed very lately or would even mixup

from bluepy import btle
import os
import re
import time
from mqtt_helper import mqtt_helper

address = 'A4:C1:38:CB:01:60'
location = 'master'

mqtt_helper = mqtt_helper(location)

class MyDelegate(btle.DefaultDelegate):
	def __init__(self, params):
		btle.DefaultDelegate.__init__(self)
		# ... initialise here

	
	def handleNotification(self, cHandle, data):
		try:
			# temp
			temp=int.from_bytes(data[0:2],byteorder='little',signed=True)/100

			# humidity
			humidity=int.from_bytes(data[2:3],byteorder='little')

			# battery
			batt=p.readCharacteristic(0x001b)
			batt=int.from_bytes(batt,byteorder="little")
			
			mqtt_helper.publish_message(temp, humidity, batt)
			mqtt_helper.publish_status()

		except Exception as e:
			print("Fehler")
			print(e)
	
def connect():
	p = btle.Peripheral(address)	
	val=b'\x01\x00'
	p.writeCharacteristic(0x0038,val,True)
	p.withDelegate(MyDelegate("abc"))
	return p
	
connected=False

pid=os.getpid()	
bluepypid=None
unconnectedTime=None

while True:
	try:
		if not connected:
			print("Trying to connect to " + address)
			p=connect()
			connected=True
			unconnectedTime=None			
		if p.waitForNotifications(2000):
			continue
	except Exception as e:
		print("Connection lost")
		if connected is True: #First connection abort after connected
			unconnectedTime=int(time.time())
			connected=False
		time.sleep(1)
		


