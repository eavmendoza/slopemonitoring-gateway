import logging
from ina219 import INA219
import time
import argparse
import sys
from mqtt import mqttlib

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.5
ADDRESS = 0x40

def read():
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address=ADDRESS)
    ina.configure(ina.RANGE_16V, ina.GAIN_AUTO)

    print("Bus Voltage    : %.3f V" % ina.voltage())
    print("Bus Current    : %.3f mA" % ina.current())
    print("Supply Voltage : %.3f V" % ina.supply_voltage())
    print("Shunt voltage  : %.3f mV" % ina.shunt_voltage())
    print("Power          : %.3f mW" % ina.power())

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--publish", help="publish data",
        action="store_true")

    return parser.parse_args()

def read_publish():
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address=ADDRESS)
    ina.configure(ina.RANGE_16V, ina.GAIN_AUTO)

    btv = round(ina.supply_voltage(),2)
    cur = round(ina.current(),2)

    message_value = "LGR:BCM-PDH-GTW1;BTV:{0};CUR:{1}".format(btv, cur)

    print(message_value)

    mqttlib.publish("gateway.gatewaytx", message_value)


if __name__ == "__main__":

    args = get_arguments()

    if args.publish:
        read_publish()
        sys.exit()

    while True:
        read()
        time.sleep(5)