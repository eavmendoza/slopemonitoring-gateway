from Adafruit_IO import MQTTClient
import time

ADAFRUIT_IO_KEY      = '437c1e57fd9941fcb444c504eea003d1'
ADAFRUIT_IO_USERNAME = 'eavmendoza' 

def publish(feed=None, value=""):
    start = time.time()
    client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
    client.connect()
    print("Connection time: {0}".format(time.time() - start))

    print('Publishing {0}'.format(value))
    start = time.time()
    print(client.publish(feed, value))
    print("Publish time: {0}".format(time.time() - start))

