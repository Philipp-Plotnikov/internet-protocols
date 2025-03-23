from dns_server import DNSServer


def main():
    host = input("Input host IP: ")
    remote_dns_server = input("Input remote DNS server IP: ")
    DNS_server = DNSServer(host, remote_dns_server)
    try:
        DNS_server.start()
    except OSError as e:
        print(e)


if __name__ == '__main__':
    main()
