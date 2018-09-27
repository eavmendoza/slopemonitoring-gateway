from Adafruit_IO import MQTTClient
import time
from volmem import client as volmem_client
import sys
import mqtt.mqttlib as mqttlib
from dbio import txn as dbtxn

def publish_pub_list(mqtt_client, mc_client):
    # print "Sending from memory ..."
    # mc = common.get_mc_server()
    # sc = mc.get('server_config')
    # smsoutbox = mc.get("smsoutbox")

    # print smsoutbox
    # phonebook = mc.get("phonebook")

    # resend_limit = sc['gsmio']['sendretry']
    df_pub_list = mc_client.get("df_pub_list")

    unpublished_list = df_pub_list[df_pub_list["stat"] == 0]
    # print(unpublished_list)

    # print("Server running")

    for index, row in unpublished_list.iterrows():
        msg_str = row['msg']
        print(msg_str)

        if mqtt_client:
            stat = mqtt_client.publish('gateway.gatewaytx', msg_str)
        
        print("Save to memory ", end="")
        dbtxn.sql_txn_log(msg_str)
        print("done")
        
        df_pub_list.loc[index, 'stat'] = 1

    # print(df_pub_list)

    # get smsoutbox for new messages inserted while sending
    df_pub_list_updated = mc_client.get("df_pub_list")

    # get all items later than the latest ts of smsoutbox
    ts_latest = df_pub_list.ts.max()
    df_pub_list_new_inserts = df_pub_list_updated[df_pub_list_updated.ts > ts_latest]

    # append new items in existing smsoutbox
    df_pub_list = df_pub_list.append(df_pub_list_new_inserts, 
        ignore_index = True, sort=True) 

    mc_client.set("df_pub_list", df_pub_list)

def server():
    print("Setting up memory ...", end='')
    mc_client = volmem_client.get()
    df_pub_list = mc_client.get("df_pub_list")

    try:
        if not df_pub_list:
            volmem_client.reset_memory("df_pub_list")
    except ValueError:
        print(" df_pub_list maybe present. continuing ... ", end=' ')

    print("done")

    print("Connecting to mqtt_lient ", end='')
    try:
        mqtt_client = mqttlib.get_client()
    except:
        print("Error connecting to server")
        mqtt_client = None
    print("done")


    while True:
        publish_pub_list(mqtt_client, mc_client)

        if not mqtt_client:
            print("Delay before reconnection")
            time.sleep(50)
            print("Restarting server")
            break
        time.sleep(1)

if __name__ == "__main__":

    while True:
        try:
            server()
        except mqttlib.DisconnectException:
            print("Reconnecting")
        except KeyboardInterrupt:
            print("Bye")
            sys.exit()