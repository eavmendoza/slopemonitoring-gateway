import timeit
import time
from dbio import txn
import argparse
import volmem.client 
from datetime import datetime as dt
import RPi.GPIO as GPIO
import subprocess as sub

LAST_TIP_DT = dt.today()

class RainProps:
    def __init__(self):
        print("Getting rain props ... ", end='')
        mc = volmem.client.get()
        cnf = mc.get("gateway_config")
        self.rain_pin = int(cnf["rain"]["pin"])
        self.name = "{}-{}".format(cnf["gateway"]["name"], cnf["rain"]["name"])
        self.mem = mc    
        print("done")


def get_coded_dt():
    return dt.today().strftime("%y%m%d%H%M%S")

def gpio_setup(rg):
    print("Gpio setup ... ", end='')
    rain_pin = rg.rain_pin

    import RPi.GPIO as GPIO

    # GPIO.setmode(GPIO.BCM)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(rain_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print(rain_pin)
    # GPIO.setup(rain_pin, GPIO.OUT)
    # GPIO.output(rain_pin, GPIO.HIGH)
    # print("Infinite loop")
    # while(True):
    #     pass

    cb = lambda channel, arg1=rg: rain_event(channel, arg1)
    # cb = rain_event
    GPIO.add_event_detect(rain_pin, GPIO.FALLING, callback=cb, bouncetime=500)  
    # GPIO.add_event_detect(rain_pin, GPIO.FALLING, callback=cb)
    print("done")

def rain_event(channel, rg):

    global LAST_TIP_DT
    dt_event = dt.today()
    print("TIP")
    time_from_last_tip = dt_event - LAST_TIP_DT
    if time_from_last_tip.seconds < 3:
        print("Debounce")
        return
    else:
        sub.Popen(['python3', '/home/pi/gateway2/sensors/led.py', '-d500'], stdout=sub.PIPE, stderr=sub.STDOUT)
        print(time_from_last_tip.seconds, end=" ")
        LAST_TIP_DT = dt_event

    # else record rain pulse
    rg.mem.incr("rain_count")
    dt_today_coded = get_coded_dt()
    print(dt_today_coded, rg.name)
    message_value = "{}$TIP:1;DTM:{}$".format(rg.name,dt_today_coded)
    volmem.client.push_pub_list(message_value)

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

    # previous way of counting tips, save to memory
    # volmem.client.push_pub_list(message_value)

    # save directly to sql
    start_time = timeit.default_timer()
    txn.sql_txn_log(message_value)
    print("exec_time:", timeit.default_timer() - start_time)

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

def set_rain_count(this_rain_gauge):
    print("Setting count ... ", end='')
    count = this_rain_gauge.mem.get("rain_count")
    if not count:
        reset_rain_count(this_rain_gauge)
    print("done")

def main():
    start_time = timeit.default_timer()
    args = get_arguments()

    this_rain_gauge = RainProps()

    GPIO.cleanup()

    if args.report > 0:
        print("Reporting rain")
        report_rain_tips(this_rain_gauge, args.report)
        return

    gpio_setup(this_rain_gauge)
    set_rain_count(this_rain_gauge)

    if args.reset:
        print("Resetting rain count ... ", end='')
        reset_rain_count(this_rain_gauge)
        print("done")
        return

    if args.count:
        tips = count_rain_tips(this_rain_gauge)
        print("Rain tips: {}".format(tips))
        return

    try:
        while True:
            time.sleep(300)
            GPIO.remove_event_detect(this_rain_gauge.rain_pin)
            GPIO.cleanup()
            gpio_setup(this_rain_gauge)
            print(".", end="")
    except KeyboardInterrupt:
        print("Bye")
        
    GPIO.cleanup()
    
if __name__ == "__main__":
    main()




