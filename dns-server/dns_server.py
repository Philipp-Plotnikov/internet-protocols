import socket
import dnslib
from dnslib import DNSRecord
from cache import Cache
from cache_dns_record import CacheDNSRecord

class DNSServer:
    __PORT = 53

    def __init__(self, host: str, remote_dns_server: str):
        self.__cache = Cache.unload_cache()
        self.__HOST = host
        self.__host_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__remote_dns_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.__REMOTE_DNS_SERVER = remote_dns_server


    def handle_request(self, dns_query: bytes, customer_addr: tuple[str, int]):
        cache = self.__cache
        host_socket = self.__host_socket
        remote_dns_server_socket = self.__remote_dns_server_socket
        try:
            parsed_dns_query = dnslib.DNSRecord.parse(dns_query)
            cache.delete_expired_records()
            cache_record = cache.get_record(parsed_dns_query)
            if cache_record is not None:
                print('Data was fetched from cache')
                self.add_answer_to_query(cache_record, parsed_dns_query)
                host_socket.sendto(parsed_dns_query.pack(), customer_addr)
                return
            print('Requesting the upstream DNS server')
            remote_dns_server_socket.send(dns_query)
            respond_data, _ = remote_dns_server_socket.recvfrom(10000)
            host_socket.sendto(respond_data, customer_addr)
            parsed_respond = dnslib.DNSRecord.parse(respond_data)
            cache.update(parsed_respond)
        except Exception as e:
            print(e)


    def add_answer_to_query(self, cache_record: CacheDNSRecord, dns_query: DNSRecord):
        q_type = dns_query.q.qtype
        q = dns_query.q
        cache = self.__cache
        if q_type == dnslib.QTYPE.A:
            for addr in cache_record.objects:
                dns_query.add_answer(
                    dnslib.RR(
                    q.qname,
                    q.qtype,
                    q.qclass,
                    cache.remain_ttl(cache_record),
                    dnslib.A(addr.rdata.data)
                ))
            return
        if q_type == dnslib.QTYPE.AAAA:
            for addr in cache_record.objects:
                dns_query.add_answer(
                    dnslib.RR(
                    q.qname,
                    q.qtype,
                    q.qclass,
                    cache.remain_ttl(cache_record),
                    dnslib.AAAA(addr)
                ))
            return
        if q_type == dnslib.QTYPE.NS:
            for addr in cache_record.objects:
                dns_query.add_answer(dnslib.RR(
                    q.qname,
                    q.qtype,
                    q.qclass,
                    cache.remain_ttl(cache_record),
                    dnslib.NS(addr)
                ))
            return
        if q_type == dnslib.QTYPE.PTR:
            dns_query.add_answer(dnslib.RR(
                q.qname,
                q.qtype,
                q.qclass,
                cache.remain_ttl(cache_record),
                dnslib.PTR(cache_record.name)
            ))


    def start(self):
        with self.__host_socket as host_socket:
            with self.__remote_dns_server_socket as remote_dns_server_socket:
                host_socket.bind((self.__HOST, self.__PORT))
                remote_dns_server_socket.connect((self.__REMOTE_DNS_SERVER, self.__PORT))
                while True:
                    try:
                        query_data, customer_addr = host_socket.recvfrom(10000)
                        self.handle_request(query_data, customer_addr)
                    except Exception as e:
                        print(e)


    def __del__(self):
        if self.__cache is not None:
            self.__cache.save_cache()