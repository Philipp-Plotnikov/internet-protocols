import time
import pickle
import dnslib
from cache_dns_record import CacheDNSRecord
from dnslib import DNSRecord
from io import open


class Cache:
    __CACHE_FILENAME = "cache"

    def __init__(self):
        self.__a: dict[str, CacheDNSRecord] = dict()
        self.__aaaa: dict[str, CacheDNSRecord] = dict()
        self.__ns: dict[str, CacheDNSRecord] = dict()
        self.__ptr: dict[str, CacheDNSRecord] = dict()


    def update(self, dns_answer: DNSRecord):
        for new_record in dns_answer.rr + dns_answer.ar + dns_answer.auth:
            labelTupple = new_record.rname.label
            full_domain_name = self.get_full_domain_name(labelTupple)
            record_type = new_record.rtype
            if record_type == dnslib.QTYPE.NS:
                self.update_ns(new_record, full_domain_name)
            elif record_type == dnslib.QTYPE.A:
                self.update_a(new_record, full_domain_name)
            elif record_type == dnslib.QTYPE.AAAA:
                self.update_aaaa(new_record, full_domain_name)
            elif record_type == dnslib.QTYPE.PTR:
                self.update_ptr(new_record, full_domain_name)


    def update_ns(self, new_record, full_domain_name: str):
        cache_dns_record = CacheDNSRecord(new_record.ttl)
        cache_dns_record.objects.append(new_record.rdata.label.label)
        self.__ns[full_domain_name] = cache_dns_record


    def update_a(self, new_record, full_domain_name: str):
        cache_dns_record = CacheDNSRecord(new_record.ttl)
        cache_dns_record.objects.append(new_record.rdata.data)
        self.__a[full_domain_name] = cache_dns_record


    def update_aaaa(self, new_record, full_domain_name: str):
        cache_dns_record = CacheDNSRecord(new_record.ttl)
        cache_dns_record.objects.append(new_record.rdata.data)
        self.__aaaa[full_domain_name] = cache_dns_record


    def update_ptr(self, new_record, full_domain_name: str):
        cache_dns_record = CacheDNSRecord(
            new_record.ttl,
            new_record.rdata.label.label
        )
        self.__ptr[full_domain_name] = cache_dns_record
         

    def get_record(self, dns_query: DNSRecord):
        full_domain_name = self.get_full_domain_name(dns_query.q.qname.label)
        q_type = dns_query.q.qtype
        if q_type == dnslib.QTYPE.A:
            return self.__a.get(full_domain_name)
        elif q_type == dnslib.QTYPE.AAAA:
            return self.__aaaa.get(full_domain_name)
        elif q_type == dnslib.QTYPE.NS:
            return self.__ns.get(full_domain_name)
        elif q_type == dnslib.QTYPE.PTR:
            return self.__ptr.get(full_domain_name)
    
    def get_full_domain_name(self, labelTupple):
        full_domain_name = ""
        for label in labelTupple:
            full_domain_name = f"{full_domain_name}{label.decode('utf-8')}."
        return full_domain_name

    def delete_expired_records(self):
        list_copy = self.__a.copy()
        for key, value in list_copy.items():
            if self.remain_ttl(value) == 0:
                self.__a.pop(key, None)
        list_copy = self.__aaaa.copy()
        for key, value in list_copy.items():
            if self.remain_ttl(value) == 0:
                self.__aaaa.pop(key, None)
        list_copy = self.__ns.copy()
        for key, value in list_copy.items():
            if self.remain_ttl(value) == 0:
                self.__ns.pop(key, None)
        list_copy = self.__ptr.copy()
        for key, value in list_copy.items():
            if self.remain_ttl(value) == 0:
                self.__ptr.pop(key, None)


    def remain_ttl(self, obj: CacheDNSRecord):
        passed_time = int(time.time() - obj.init_time)
        return max(0, obj.ttl - passed_time)


    def save_cache(self):
        try:
            with open(Cache.__CACHE_FILENAME, 'wb') as file:
                file.write(pickle.dumps(self))
                print("Cache was saved")
        except Exception as e:
            print(e)


    @staticmethod
    def unload_cache():
        cache = Cache()
        try:
            with open(Cache.__CACHE_FILENAME, 'rb') as file:
                cache: Cache = pickle.loads(file.read())
                print("Cache was loaded")
        except Exception as e:
            print("Cache is empty")
        return cache
