from socket import *


def scan_tcp(ip: str, port: int):
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.settimeout(0.1)
    try:
        result = tcp_socket.connect_ex((ip, port))
        if result == 0:
            print(f"\n{port}: TCP port is opened")
        else:
            print(f"\n{port}: TCP port is closed")
    except:
        print(f"\n{port}: Connection error")
    finally:
        tcp_socket.close()


def scan_udp(ip: str, port: int):
    udp_socket = socket(AF_INET, SOCK_STREAM)
    udp_socket.settimeout(0.1)
    try:
        udp_socket.connect_ex((ip, port))
        try:
            udp_socket.sendto(b'\x11', (ip, port))
        except:
            print(f"\n{port}: UDP port is closed")
        else:
            print(f"\n{port}: UDP port is opened")
    finally:
        udp_socket.close()


def scan(ip: str, start: int, finish: int, protocol: str):
    for port in range(start, finish + 1):
        if protocol == "TCP":
            scan_tcp(ip, port)
        elif protocol == "UDP":
            scan_udp(ip, port)
