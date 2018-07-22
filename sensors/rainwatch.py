import RPi.GPIO as GPIO
import time
from volmem import client
from dbio import txn as dbtxn
from datetime import datetime as dt

class RainProps:
    def __init__(self):
        cnf = client.get().get("cnf")
        self.rain_pin = int(cnf["rain"]["pin"])
        self.name = cnf["gateway"]["name"] + cnf["rain"]["name"]    


def setup(rg):
    rain_pin = rg.rain_pin

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(rain_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    cb = lambda channel, arg1=rg: rain_event(channel, arg1)
    GPIO.add_event_detect(rain_pin, GPIO.FALLING, callback=cb, bouncetime=1000)  

def rain_event(channel, rg):
    dt_today = dt.today().strftime("%Y-%m-%d %H:%M:%S")
    dt_today_coded = dt.today().strftime("%y%m%d%H%M%S")
    print(dt_today, rg.name)
    query = ("insert into transactions (dt, message) "
        "values ('%s','rgid:%s;dt:%s')" % (dt_today, rg.name, dt_today_coded))

    dbtxn.write(query)

def main():
    this_rain_gauge = RainProps()
    setup(this_rain_gauge)
    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        print("Bye")
        
    GPIO.cleanup()
    
if __name__ == "__main__":
    main()




