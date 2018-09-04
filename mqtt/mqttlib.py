from Adafruit_IO import MQTTClient
import time
from volmem import client

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

def server():
    mqtt_client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
    mqtt_client.connect()

    print("Connected to remote mqtt server")
    mc = client.get()
    pub_list = mc.get("pub_list")
    if not pub_list:
        mc.set("pub_list", [])

    while True:

        pub_list = client.get().get("pub_list")

        while len(pub_list) > 0:
            print(pub_list)
            value = pub_list.pop(0)
            print(value)
            print(mqtt_client.publish("gateway.gatewaytx", value))
            time.sleep(0.5)

        mc.set("pub_list", [])

        time.sleep(2)

if __name__ == "__main__":

    try:
        server()
    except KeyboardInterrupt:
        print("Bye")