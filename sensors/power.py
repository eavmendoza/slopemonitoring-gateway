import logging
from ina219 import INA219
import time
import argparse
import sys
from mqtt import mqttlib
from datetime import datetime as dt
from volmem import client
from dbio import txn as dbtxn

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.5
ADDRESS = client.get().get("gateway_config")["ina219"]["address"]

def read(print_val=False):
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address=ADDRESS)
    ina.configure(ina.RANGE_16V, ina.GAIN_AUTO)

    if print_val:
        print("Bus Voltage    : %.3f V" % ina.voltage())
        print("Bus Current    : %.3f mA" % ina.current())
        print("Supply Voltage : %.3f V" % ina.supply_voltage())
        print("Shunt voltage  : %.3f mV" % ina.shunt_voltage())
        print("Power          : %.3f mW" % ina.power())

    return ina

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--publish", help="publish data",
        action="store_true")

    return parser.parse_args()

def read_publish():
    ina = read()

    btv = round(ina.supply_voltage(),2)
    cur = round(ina.current(),2)
    ts = dt.today().strftime("%y%m%d%H%M%S")

    message_value = "BCM-PDH-GTW1$BTV:{0};BTA:{1};DTM:{2}$".format(btv, 
        cur, ts)

    print(message_value)

    # client.push_pub_list(message_value)
    client.push_df_pub_list(message_value)
    dbtxn.sql_txn_log(message_value)



if __name__ == "__main__":

    args = get_arguments()

    if args.publish:
        read_publish()
        sys.exit()

    while True:
        read(print_val=True)
        time.sleep(5)