from configparser import ConfigParser
from volmem import client

def set():
    mem = client.get()
    config = ConfigParser()
    config.read('this_gateway.cnf')
    mem.set("cnf",config)

if __name__ == "__main__":
    set()
