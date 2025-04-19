
import socket
import time
import csv
import threading
import os
from datetime import datetime

def wait_for_init(sock, feedback_port):
    while True:
        data, addr = sock.recvfrom(1024)
        if data.startswith(b"INIT:"):
            print("[RECV] INIT packet received.")
            parts = data.decode().strip().split(":")
            total_trains = int(parts[1])
            packets_per_train = int(parts[2])
            prefix = parts[3] if len(parts) > 3 else "session"
            total_packets = total_trains * packets_per_train
            for i in range(3):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(("127.0.0.1", feedback_port))
                    s.sendall(b"ACK\n")
                    print(f"[ACK] OK (after {i+1} tries)")
                    s.close()
                    break
                except Exception as e:
                    print(f"[RETRY] Failed to send ACK: {e}")
                    time.sleep(1)
            return total_packets, prefix

def run(port, feedback_port, num_packets, stretch_threshold, csv_prefix, loop=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", port))
    
    while True:
        total_packets, prefix = wait_for_init(sock, feedback_port)
        received = 0
        prev_time = None
        deltas = []
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("results", exist_ok=True)
        csv_filename = f"results/{csv_prefix}-{ts}.csv"

        prev_time = None
        deltas = []
        received = 0

        with open(csv_filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["packet_number", "arrival_time", "delta_us", "estimated_bw_mbps"])

            while received < total_packets:
                if received == 0:
                    print(f"[SESSION] Starting new session expecting {total_packets} packets")
                try:
                    data, _ = sock.recvfrom(1600)
                except socket.timeout:
                    print("[WARN] Timeout waiting for final packets.")
                    break

                now = time.time()
                delta_us = ""
                bw = ""
                if prev_time:
                    dt = now - prev_time
                    delta_us = int(dt * 1e6)
                    deltas.append(delta_us)
                    bw = round((len(data) / dt) * 8 / 1e6, 2)
                    print(f"[{received + 1}] Δt: {delta_us} μs | BW: {bw} Mbps")
                else:
                    print(f"[{received + 1}] First packet")

                prev_time = now
                received += 1
                writer.writerow([received, datetime.fromtimestamp(now).strftime("%H:%M:%S.%f"), delta_us, bw])

        def send_feedback(ok: bool):
            for i in range(3):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(("127.0.0.1", feedback_port))
                    s.sendall(b"OK\n" if ok else b"FAIL\n")
                    s.close()
                    return
                except Exception as e:
                    print(f"[WARN] Could not send final feedback: {e}")
                    time.sleep(1)

        ok = all(abs(deltas[i] - deltas[i - 1]) <= stretch_threshold for i in range(1, len(deltas)))
        send_feedback(ok)
        print(f"[FILE] Saved {csv_filename} (received: {received}/{total_packets})")

        # Flush leftover UDP packets before next INIT
        try:
            while True:
                sock.settimeout(0.01)
                sock.recvfrom(1600)
        except socket.timeout:
            pass
        sock.settimeout(None)

        if not loop:
            break
