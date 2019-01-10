from Adafruit_IO import MQTTClient
import time
from volmem import client as volmem_client
import sys

mc_client = volmem_client.get()
mqtt_config = mc_client.get("gateway_config")["mqtt"]

ADAFRUIT_IO_KEY      = mqtt_config["key"]
ADAFRUIT_IO_USERNAME = mqtt_config["username"]
THROTTLE_FEED_ID = mqtt_config["feed"]

class DisconnectException(Exception):
    pass

class ThrottleException(Exception):
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

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    raise ThrottleException(payload)

    # print('Feed {0} received new value: {1}'.format(feed_id, payload))

def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print("Connected to Adafruit IO!  Listening for {0} "
    "changes...".format(THROTTLE_FEED_ID))
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe(THROTTLE_FEED_ID)

def get_client():
    mqtt_client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
    mqtt_client.on_disconnect = disconnected
    mqtt_client.on_message = message
    mqtt_client.on_connect = connected
    

    mqtt_client.connect()
    mqtt_client.loop_background()

    print("Connected to remote mqtt server")

    return mqtt_client