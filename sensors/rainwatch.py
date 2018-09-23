import RPi.GPIO as GPIO
import time
import argparse
from volmem import client
from dbio import txn as dbtxn
from datetime import datetime as dt
import sys

class RainProps:
    def __init__(self):
        mc = client.get()
        cnf = mc.get("gateway_config")
        self.rain_pin = int(cnf["rain"]["pin"])
        self.name = "{}-{}".format(cnf["gateway"]["name"], cnf["rain"]["name"])
        self.mem = mc    

def get_coded_dt():
    dt_today = dt.today().strftime("%Y-%m-%d %H:%M:%S")
    dt_today_coded = dt.today().strftime("%y%m%d%H%M%S")
    return dt_today_coded

def setup(rg):
    rain_pin = rg.rain_pin

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(rain_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    cb = lambda channel, arg1=rg: rain_event(channel, arg1)
    GPIO.add_event_detect(rain_pin, GPIO.FALLING, callback=cb, bouncetime=1000)  

def rain_event(channel, rg):
    dt_today_coded = get_coded_dt()
    print(dt_today, rg.name)
    message_value = "{};INS:1;DTM:{}".format(rg.name,dt_today_coded)
    client.push_df_pub_list(message_value)
    increment_rain_count(rg)

def reset_rain_count(rg):
    rg.mem.set("rain_count", 0)

def count_rain_tips(rg):
    try:
        tips = int(rg.mem.get("rain_count"))
    except (ValueError, TypeError):
        print("Error in rain count")
        return 0

    return tips

def increment_rain_count(rg):
    tips = count_rain_tips(rg)
    rg.mem.set("rain_count", tips+1)

def report_rain_tips(rg, period=30):
    tips = count_rain_tips(rg)
    dt_today_coded = get_coded_dt()
    message_value = "{};PER:{};VAL:{};DTM:{}".format(rg.name, period, tips,
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

    print("Setup rain ... ", end='')
    this_rain_gauge = RainProps()
    setup(this_rain_gauge)
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
            time.sleep(10000)
    except KeyboardInterrupt:
        print("Bye")
        
    GPIO.cleanup()
    
if __name__ == "__main__":
    main()




