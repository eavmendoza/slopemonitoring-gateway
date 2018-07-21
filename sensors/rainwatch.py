import RPi.GPIO as GPIO
import time

def setup(rain_pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(rain_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(rain_pin, GPIO.FALLING, callback=rain_event, bouncetime=300)  

def rain_event(channel):
    print("hey")

def main():
    time.sleep(10000)

if __name__ == "__main__":
    rain_pin = 18
    try:
        setup(rain_pin)
        while True:
            main()
    except KeyboardInterrupt:
        print("Bye")
        
    GPIO.cleanup()




