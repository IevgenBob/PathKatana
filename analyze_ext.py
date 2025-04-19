
import argparse
import glob
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

def parse_csv(file_path):
    packets = []
    bandwidths = []
    deltas = []
    with open(file_path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            try:
                pkt = int(row[0])
                dt = float(row[2])
                bw = float(row[3])
                packets.append(pkt)
                deltas.append(dt)
                bandwidths.append(bw)
            except:
                continue
    return packets, deltas, bandwidths

def analyze_file(file_path):
    packets, deltas, bandwidths = parse_csv(file_path)
    if not bandwidths:
        return None

    avg_bw = sum(bandwidths) / len(bandwidths)
    min_bw = min(bandwidths)
    max_bw = max(bandwidths)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = f"{os.path.splitext(file_path)[0]}_{ts}.pdf"
    with PdfPages(pdf_path) as pdf:
        plt.figure(figsize=(10, 4))
        plt.plot(packets, bandwidths, label='Bandwidth (Mbps)')
        try:
            xdata = np.array(packets)
            ydata = np.array(bandwidths)
            popt, _ = curve_fit(sigmoid, xdata, ydata, maxfev=10000)
            plt.plot(xdata, sigmoid(xdata, *popt), '--', label="Theoretical Fit")
        except Exception as e:
            print(f"[WARN] Could not fit curve: {e}")
        plt.axhline(avg_bw, linestyle='--', color='gray', label=f"Avg: {avg_bw:.2f} Mbps")
        plt.title(f"{os.path.basename(file_path)} - Bandwidth")
        plt.xlabel("Packet #")
        plt.ylabel("Bandwidth (Mbps)")
        plt.grid(True)
        plt.legend()
        pdf.savefig()
        plt.close()

        plt.figure(figsize=(10, 4))
        plt.plot(packets, deltas, color="orange", label="Δt (μs)")
        plt.xlabel("Packet #")
        plt.ylabel("Δt (μs)")
        plt.title(f"{os.path.basename(file_path)} - Δt Between Packets")
        plt.grid(True)
        plt.legend()
        pdf.savefig()
        plt.close()

    print(f"[PDF] Saved individual: {pdf_path}")
    return os.path.basename(file_path), avg_bw

def analyze_group(files):
    summary = []
    for file_path in files:
        result = analyze_file(file_path)
        if result:
            summary.append(result)

    if not summary:
        print("No valid files to analyze.")
        return

    
def sigmoid(x, a, b, c):
    return a / (1 + np.exp(b * (x - c)))

# Generate summary graph
    labels = [name for name, _ in summary]
    averages = [bw for _, bw in summary]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, averages)
    plt.xticks(rotation=90)
    plt.ylabel("Average Bandwidth (Mbps)")
    plt.title("Average Bandwidth per Session")
    plt.tight_layout()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = f"summary_bandwidth_{ts}.pdf"
    plt.savefig(out)
    print(f"[PDF] Saved summary: {out}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze one or more CSV files and generate PDF(s)")
    parser.add_argument("--input", nargs="+", default=["results/*.csv"], help="Input CSV(s) or glob pattern")
    args = parser.parse_args()

    files = []
    for pattern in args.input:
        files.extend(glob.glob(pattern))

    analyze_group(files)
