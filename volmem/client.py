import memcache

def get():
    return memcache.Client([('127.0.0.1', 11211)])

def push_pub_list(message_value):
    mc = get()
    pub_list = mc.get("pub_list")
    pub_list.append(message_value)
    mc.set("pub_list", pub_list)