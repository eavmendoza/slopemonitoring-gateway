from Adafruit_IO import MQTTClient
import time
from volmem import client as volmem_client
import sys

mc_client = volmem_client.get()
mqtt_config = mc_client.get("gateway_config")["mqtt"]

ADAFRUIT_IO_KEY      = mqtt_config["key"]
ADAFRUIT_IO_USERNAME = mqtt_config["username"]

print(ADAFRUIT_IO_USERNAME)
print(ADAFRUIT_IO_KEY)

class DisconnectException(Exception):
    pass

def publish(feed=None, value=""):
    start = time.time()
    mqtt_client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
    mqtt_client.connect()
    print("Connection time: {0}".format(time.time() - start))

    print('Publishing {0}'.format(value))
    start = time.time()
    print(mqtt_client.publish(feed, value))
    print("Publish time: {0}".format(time.time() - start))

def disconnected(client):
   # Disconnected function will be called when the client disconnects.
   print('Disconnected from Adafruit IO!')
   raise DisconnectException

def get_client():
    mqtt_client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
    mqtt_client.on_disconnect = disconnected
    mqtt_client.connect()
    mqtt_client.loop_background()

    print("Connected to remote mqtt server")

    return mqtt_client