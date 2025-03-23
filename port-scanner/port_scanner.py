from socket import *


PROTOCOL_PROBES = {
    "HTTP": b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n",
    "SMTP": b"EHLO test\r\n",
    "POP3": b"CAPA\r\n",
    "DNS": b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01",
    "SNTP": b"\x1b" + 47 * b"\0"
}


def scan_tcp(ip: str, port: int):
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.settimeout(1.0)
    try:
        result = tcp_socket.connect_ex((ip, port))
        if result == 0:
            print(f"\n{port}: TCP port is open")
            identify_protocol(tcp_socket, port)
        else:
            print(f"\n{port}: TCP port is closed")
    except Exception as e:
        print(f"\n{port}: Connection error - {e}")
    finally:
        tcp_socket.close()


def identify_protocol(sock: socket, port: int):
    for proto, probe in PROTOCOL_PROBES.items():
        try:
            sock.sendall(probe)
            response = sock.recv(1024).decode(errors="ignore")
            if response:
                print(f"  {port}: Likely protocol -> {proto} (Response: {response[:50]}...)")
                return
        except Exception:
            continue
    print(f"  {port}: Unknown protocol")


def scan_udp(ip: str, port: int):
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    udp_socket.settimeout(1.0)
    try:
        if port in [53, 123]:
            probe = PROTOCOL_PROBES["DNS"] if port == 53 else PROTOCOL_PROBES["SNTP"]
            udp_socket.sendto(probe, (ip, port))
            response, _ = udp_socket.recvfrom(1024)
            if response:
                print(f"\n{port}: UDP port is open (Likely { 'DNS' if port == 53 else 'SNTP' })")
                return
        else:
            identify_protocol(udp_socket, port)
        print(f"\n{port}: UDP port is open but protocol unknown")
    except Exception:
        print(f"\n{port}: UDP port is closed")
    finally:
        udp_socket.close()


def scan(ip: str, start: int, finish: int, protocol: str):
    for port in range(start, finish + 1):
        if protocol.upper() == "TCP":
            scan_tcp(ip, port)
        elif protocol.upper() == "UDP":
            scan_udp(ip, port)