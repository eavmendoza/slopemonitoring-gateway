import RPi.GPIO as GPIO
import time
import argparse
from volmem import client
from dbio import txn as dbtxn
from datetime import datetime as dt
import sys
from signal import pause

LAST_TIP_DT = dt.today()

class RainProps:
    def __init__(self):
        mc = client.get()
        cnf = mc.get("gateway_config")
        self.rain_pin = int(cnf["rain"]["pin"])
        self.name = "{}-{}".format(cnf["gateway"]["name"], cnf["rain"]["name"])
        self.mem = mc    

def get_coded_dt():
    return dt.today().strftime("%y%m%d%H%M%S")

def gpio_setup(rg):
    rain_pin = rg.rain_pin

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(rain_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    cb = lambda channel, arg1=rg: rain_event(channel, arg1)
    # cb = rain_event
    GPIO.add_event_detect(rain_pin, GPIO.FALLING, callback=cb, bouncetime=500)  

def rain_event(channel, rg):

    global LAST_TIP_DT
    dt_event = dt.today()
    time_from_last_tip = dt_event - LAST_TIP_DT
    if time_from_last_tip.seconds < 3:
        print("Debounce")
        return
    else:
        print(time_from_last_tip.seconds, end=" ")
        LAST_TIP_DT = dt_event

    # else record rain pulse
    rg.mem.incr("rain_count")
    dt_today_coded = get_coded_dt()
    print(dt_today_coded, rg.name)
    message_value = "{}$TIP:1;DTM:{}$".format(rg.name,dt_today_coded)
    client.push_df_pub_list(message_value)

def reset_rain_count(rg):
    rg.mem.set("rain_count", 0)

def count_rain_tips(rg):
    try:
        tips = int(rg.mem.get("rain_count"))
    except (ValueError, TypeError):
        print("Error in rain count")
        return 0

    return tips

def report_rain_tips(rg, period=30):
    tips = count_rain_tips(rg)
    dt_today_coded = get_coded_dt()
    message_value = "{}$PER:{};TIP:{};DTM:{}$".format(rg.name, period, tips,
        dt_today_coded)
    print(message_value)
    client.push_df_pub_list(message_value)
    reset_rain_count(rg)

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--count", help="count tips", action="store_true")
    parser.add_argument("-r","--reset", help="reset tips", action="store_true")
    parser.add_argument("-p","--report", help="report period", type=int)

    args = parser.parse_args()

    if not args.report:
        args.report = 0

    return args

def main():
    args = get_arguments()

    print("Getting rain props ... ", end='')
    this_rain_gauge = RainProps()
    print("done")
    print("Gpio setup ... ", end='')
    gpio_setup(this_rain_gauge)
    print("done")
    print("Setting count ... ", end='')
    count = this_rain_gauge.mem.get("rain_count")
    if not count:
        reset_rain_count(this_rain_gauge)
    print("done")

    if args.reset:
        print("Resetting rain count ... ", end='')
        reset_rain_count(this_rain_gauge)
        print("done")
        return

    if args.count:
        tips = count_rain_tips(this_rain_gauge)
        print("Rain tips: {}".format(tips))
        return

    if args.report > 0:
        report_rain_tips(this_rain_gauge, args.report)
        return
    
    try:
        while True:
            time.sleep(60)
            GPIO.remove_event_detect(this_rain_gauge.rain_pin)
            GPIO.cleanup()
            gpio_setup(this_rain_gauge)
            print(".", end="")
    except KeyboardInterrupt:
        print("Bye")
        
    GPIO.cleanup()
    
if __name__ == "__main__":
    main()




