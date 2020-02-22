#!/usr/bin/python3 -u
#!/home/openhabian/Python3/Python-3.7.4/python -u
#-u to unbuffer output. Otherwise when calling with nohup or redirecting output things are printed very lately or would even mixup

from bluepy import btle
import os
import re
import time
#import mysql.connector as mariadb
from mqtt_helper import mqtt_helper

address = 'A4:C1:38:6B:B1:CB'
location = 'lounge'

mqtt_helper = mqtt_helper(location)

# device_label='RPi_1'

# db_host = '192.168.0.10'
# db_host_port = '3306'
# db_user = 'rpi'
# db_pass = 'warm_me'
# db = 'temp_logger'

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

			# insert_stmt = """
    		# INSERT INTO temperature
    		# (device, temp)
    		# VALUES
    		# ('{}',{})""".format(device_label,temp)
						
			# con = mariadb.connect(host = db_host, port = db_host_port, user = db_user, password = db_pass, database = db)
			# cur = con.cursor()
			
			# try:
			# 	cur.execute(insert_stmt)
			# 	con.commit()
			# except:
			# 	con.rollback()
			# 	con.close()

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
		


