import RPi.GPIO as GPIO
import time
from volmem import client

def setup():
    mem = client.get()
    rain_pin = int(mem.get("cnf")["rain"]["pin"])

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(rain_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(rain_pin, GPIO.FALLING, callback=rain_event, bouncetime=300)  

def rain_event(channel):
    print("hey")

def main():
    setup()
    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        print("Bye")
        
    GPIO.cleanup()
    
if __name__ == "__main__":
    main()




