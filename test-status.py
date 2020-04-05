import paho.mqtt.client as mqtt
import json

location = 'lounge'

status_topic = "home/inside/sensor/"+str(location)+"/status"

server_address="192.168.0.10" 

client = mqtt.Client(location)
client.connect(server_address, keepalive=60)

online_msg = json.dumps({"location":location, "status":"online"})
offline_msg = json.dumps({"location":location, "status":"offline"})

	 	 
def on_connect(client, userdata, flags, rc):
	client.publish(status_topic,payload=online_msg, qos=0, retain=True)

client = mqtt.Client()
client.on_connect = on_connect
client.will_set(status_topic, payload=offline_msg, qos=0, retain=True)
client.connect(server_address, 1883, 60)
client.loop_forever()
