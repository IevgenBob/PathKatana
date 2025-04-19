
import socket
import time
from datetime import datetime

def wait_for_ack(feedback_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", feedback_port))
    s.listen(1)
    s.settimeout(5)
    try:
        conn, _ = s.accept()
        data = conn.recv(16).decode().strip()
        conn.close()
        return data == "ACK"
    except:
        return False
    finally:
        s.close()

def send_init_packet(target_ip, port, num_trains, num_packets, prefix):
    init_message = f"INIT:{num_trains}:{num_packets}:{prefix}\n".encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(init_message, (target_ip, port))
    sock.close()

def spacing_from_rate(rate_mbps, packet_size):
    bytes_per_sec = (rate_mbps * 1e6) / 8
    return packet_size / bytes_per_sec

def send_train(sock, spacing_sec, packet_size, num_packets, target_ip, port):
    pkt = b'\x00' * packet_size
    for _ in range(num_packets):
        sock.sendto(pkt, (target_ip, port))
        time.sleep(spacing_sec)

def run(target_ip, port, feedback_port, packet_size, num_packets, min_rate, max_rate, tolerance):
    print("[INIT] Sending INIT packet via UDP...")
    import math
    steps = math.ceil(math.log2((max_rate - min_rate) / tolerance))
    num_trains = steps
    prefix = datetime.now().strftime("test")
    send_init_packet(target_ip, port, num_trains, num_packets, prefix)

    print("[WAIT] Waiting for TCP ACK...")
    if not wait_for_ack(feedback_port):
        print("[ERROR] Receiver did not acknowledge INIT. Aborting.")
        return

    print("[START] Test begins...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    low, high = min_rate, max_rate
    best = low

    while high - low > tolerance:
        mid = (low + high) / 2
        spacing = spacing_from_rate(mid, packet_size)
        print(f"[TRY] {mid:.2f} Mbps | spacing: {spacing*1e6:.1f} μs")
        send_train(sock, spacing, packet_size, num_packets, target_ip, port)

        if wait_for_ack(feedback_port):
            best = mid
            low = mid
        else:
            high = mid

    print(f"[RESULT] Estimated Bandwidth: {best:.2f} Mbps")
