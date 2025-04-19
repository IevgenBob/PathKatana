
import csv
import argparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

class KalmanFilter:
    def __init__(self, q=0.1, r=10.0):
        self.x = 0.0
        self.p = 1.0
        self.q = q
        self.r = r

    def update(self, measurement):
        self.p += self.q
        k = self.p / (self.p + self.r)
        self.x += k * (measurement - self.x)
        self.p *= (1 - k)
        return self.x

def analyze(csv_file, use_kalman=True, q=0.1, r=10.0, output_file="estimated_bandwidth.txt", make_pdf=False):
    if not csv_file.endswith(".csv"):
        csv_file += ".csv"

    print(f"[DEBUG] Opening CSV: {csv_file}")
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        packets, deltas, values = [], [], []
        skipped = 0

        for row in reader:
            try:
                pkt = int(row[0])
                dt = row[2].strip()
                bw = row[3].strip()
                if bw:
                    bw_val = float(bw)
                    values.append(bw_val)
                    packets.append(pkt)
                    deltas.append(float(dt) if dt else 0)
                else:
                    skipped += 1
            except Exception as e:
                print(f"[WARN] Skipping row {row}: {e}")
                skipped += 1

    if not values:
        print(f"[ERROR] No valid bandwidth data found in {csv_file}")
        return

    print(f"[INFO] Parsed {len(values)} valid rows, skipped {skipped}")

    if use_kalman:
        print("[INFO] Applying Kalman filter...")
        kf = KalmanFilter(q, r)
        values = [kf.update(v) for v in values]

    avg_bw = sum(values) / len(values)
    print(f"[RESULT] Avg: {avg_bw:.2f} Mbps  Min: {min(values):.2f}  Max: {max(values):.2f}")

    with open(output_file, "w") as f:
        f.write(f"{avg_bw:.2f} Mbps\n")

    if make_pdf:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_name = f"bandwidth_report_{ts}.pdf"
        with PdfPages(pdf_name) as pdf:
            plt.figure(figsize=(10, 4))
            plt.plot(packets, values, label="Bandwidth (Mbps)")
            plt.axhline(avg_bw, color="gray", linestyle="--", label=f"Mean: {avg_bw:.2f}")
            plt.xlabel("Packet #")
            plt.ylabel("Bandwidth (Mbps)")
            plt.title("Bandwidth over Time")
            plt.grid(True)
            plt.legend()
            pdf.savefig()
            plt.close()

            plt.figure(figsize=(10, 4))
            plt.plot(packets, deltas, color="orange", label="Δt (μs)")
            plt.xlabel("Packet #")
            plt.ylabel("Delta t (μs)")
            plt.title("Δt Between Packets")
            plt.grid(True)
            pdf.savefig()
            plt.close()

        print(f"[PDF] Saved report to {pdf_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="?", help="Input CSV file (positional)")
    parser.add_argument("--input", help="Input CSV file")
    parser.add_argument("--output", default="estimated_bandwidth.txt")
    parser.add_argument("--use-kalman", action="store_true")
    parser.add_argument("--q", type=float, default=0.1)
    parser.add_argument("--r", type=float, default=10.0)
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args()

    csv_file = args.input or args.filename or "packet_intervals.csv"
    analyze(csv_file, args.use_kalman, args.q, args.r, args.output, args.pdf)
