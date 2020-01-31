#!/usr/bin/python3 -u
#!/home/openhabian/Python3/Python-3.7.4/python -u
#-u to unbuffer output. Otherwise when calling with nohup or redirecting output things are printed very lately or would even mixup

from bluepy import btle
import os
import re
#from dataclasses import dataclass
import time
import paho.mqtt.client as mqtt
import json

adress = 'A4:C1:38:CB:01:60'
location = 'master'

class MyDelegate(btle.DefaultDelegate):
	def __init__(self, params):
		btle.DefaultDelegate.__init__(self)
		# ... initialise here

	
	def handleNotification(self, cHandle, data):
		try:
			# temp
			temp=int.from_bytes(data[0:2],byteorder='little',signed=True)/100
			publish_message(location, "temperature", temp)

			# humidity
			humidity=int.from_bytes(data[2:3],byteorder='little')
			publish_message(location, "humidity", humidity)

			# battery
			batt=p.readCharacteristic(0x001b)
			batt=int.from_bytes(batt,byteorder="little")
			publish_message(location, "temp_sensor_battery", batt)

		except Exception as e:
			print("Fehler")
			print(e)
	
def publish_message(location, measurement, reading):

	topic = "home/inside/sensor/"+str(location)

	server_address="192.168.0.10" 

	client_label = "docker_"+str(location)+"_conditions"
	client = mqtt.Client(client_label)
	client.connect(server_address, keepalive=60)

	#ts = time.time()

	dict_msg = {measurement:reading}
	str_msg = str(measurement) + ",value=" + str(reading)
	msg = json.dumps(dict_msg)

	client.publish(topic,str_msg)
	

def connect():
	p = btle.Peripheral(adress)	
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
			print("Trying to connect to " + adress)
			p=connect()
			connected=True
			unconnectedTime=None			
		if p.waitForNotifications(2000):
			continue
		p.disconnect()
		break
	except Exception as e:
		print("Connection lost")
		if connected is True: #First connection abort after connected
			unconnectedTime=int(time.time())
			connected=False
		time.sleep(1)
		


