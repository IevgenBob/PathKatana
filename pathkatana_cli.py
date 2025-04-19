
import argparse
import sender
import receiver
import analyze

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PathKatana: Bandwidth Estimation Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # SEND
    send_parser = subparsers.add_parser("send", help="Send UDP packet trains with binary search")
    send_parser.add_argument("--target", default="127.0.0.1", help="Receiver IP")
    send_parser.add_argument("--port", type=int, default=9000)
    send_parser.add_argument("--feedback", type=int, default=9100)
    send_parser.add_argument("--size", type=int, default=1400)
    send_parser.add_argument("--packets", type=int, default=100)
    send_parser.add_argument("--min-rate", type=float, default=1.0)
    send_parser.add_argument("--max-rate", type=float, default=1000.0)
    send_parser.add_argument("--tolerance", type=float, default=1.0)

    # RECV
    recv_parser = subparsers.add_parser("recv", help="Receive UDP trains and calculate delta t")
    recv_parser.add_argument("--port", type=int, default=9000)
    recv_parser.add_argument("--feedback", type=int, default=9100)
    recv_parser.add_argument("--packets", type=int, default=100)
    recv_parser.add_argument("--stretch-threshold", type=int, default=200)
    recv_parser.add_argument("--csv-prefix", default="session", help="Prefix for output CSV filename")
    recv_parser.add_argument("--loop", action="store_true", help="Loop receive mode")

    # ANALYZE
    analyze_parser = subparsers.add_parser("analyze", help="Analyze CSV with optional Kalman filter")
    analyze_parser.add_argument("--input", default="packet_intervals.csv")
    analyze_parser.add_argument("--output", default="estimated_bandwidth.txt")
    analyze_parser.add_argument("--use-kalman", action="store_true")
    analyze_parser.add_argument("--q", type=float, default=0.1)
    analyze_parser.add_argument("--r", type=float, default=10.0)

    args = parser.parse_args()

    if args.command == "send":
        sender.run(
            args.target, args.port, args.feedback,
            args.size, args.packets,
            args.min_rate, args.max_rate, args.tolerance
        )
    elif args.command == "recv":
        receiver.run(
            args.port, args.feedback,
            args.packets, args.stretch_threshold,
            args.csv_prefix, args.loop
        )
    elif args.command == "analyze":
        analyze.analyze(
            args.input, args.use_kalman, args.q, args.r, args.output
        )
