import time

class CacheDNSRecord:
    def __init__(self, ttl, name=None):
        self.name = name
        self.init_time = time.time()
        self.ttl = ttl
        self.objects = []