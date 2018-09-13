import configparser
from volmem import client as volmem_client
import os
import memcache

CFILE = "/boot/this_gateway.cnf"

class GatewayConfig:
    def __init__(self):

        cfg = configparser.ConfigParser()
        cfg.read(CFILE)

        self.config = dict()  

        for section in cfg.sections():
            options = dict()
            for opt in cfg.options(section):

                try:
                    options[opt] = cfg.getboolean(section, opt)
                    continue
                except ValueError:
                    # may not be booelan
                    pass

                try:
                    options[opt] = cfg.getint(section, opt)
                    continue
                except ValueError:
                    # may not be integer
                    pass

                # should be a string
                options[opt] = cfg.get(section, opt)

            # setattr(self, section.lower(), options)
            self.config[section.lower()] = options

def set_config():
    gate_cnf = GatewayConfig()

    print(gate_cnf.config)

    mc_client = volmem_client.get()
    mc_client.set("gateway_config", gate_cnf.config)

    print("Config file {} set to memory".format(CFILE))

if __name__ == "__main__":
    set_config()


