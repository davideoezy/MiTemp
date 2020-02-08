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
import mysql.connector as mariadb

adress = 'A4:C1:38:6B:B1:CB'
location = 'lounge'

topic = "home/inside/sensor/"+str(location)
status_topic = "status/heater

server_address="192.168.0.10" 

client_label = str(location)+"_conditions"
client = mqtt.Client(client_label)

offline_msg = json.dumps({"location":location, "status":"offline"})
client.will_set(status_topic, payload=offline_msg, qos=0, retain=True)

client.connect(server_address, keepalive=60)

device_label='RPi_1'

db_host = '192.168.0.10'
db_host_port = '3306'
db_user = 'rpi'
db_pass = 'warm_me'
db = 'temp_logger'

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
			
			publish_message(location, temp, humidity, batt)
			publish_status(location)

			insert_stmt = """
    		INSERT INTO temperature
    		(device, temp)
    		VALUES
    		('{}',{})""".format(device_label,temp)
						
			con = mariadb.connect(host = db_host, port = db_host_port, user = db_user, password = db_pass, database = db)
			cur = con.cursor()
			
			try:
				cur.execute(insert_stmt)
				con.commit()
			except:
				con.rollback()
				con.close()

		except Exception as e:
			print("Fehler")
			print(e)
	
def publish_message(location, temp, hum, batt):

	dict_msg = {"location":location, "temperature":temp, "humidity":hum, "battery":batt}
	#str_msg = str(measurement) + ", value=" + str(reading)
	msg = json.dumps(dict_msg)

	client.publish(topic,msg)	

def publish_status(location):
	status_topic = "status/heater"
	online_msg = json.dumps({"location":location, "status":"online"})
	client.publish(status_topic,payload=online_msg, qos=0, retain=True)

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
	except Exception as e:
		print("Connection lost")
		if connected is True: #First connection abort after connected
			unconnectedTime=int(time.time())
			connected=False
		time.sleep(1)
		


