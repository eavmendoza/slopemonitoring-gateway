import memcache

def get():
    return memcache.Client([('127.0.0.1', 11211)])