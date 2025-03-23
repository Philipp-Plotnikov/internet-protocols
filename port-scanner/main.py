from port_scanner import scan

if __name__ == "__main__":
    host_ip = input("Input host IP: ")
    port_start, port_finish = input("Input port range through space. Finish port will be included: ").split(' ')
    protocol = input("Write TCP or UDP scan: ")
    scan(
        host_ip,
        int(port_start),
        int(port_finish),
        protocol
    )
