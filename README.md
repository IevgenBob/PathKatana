# PathKatana: Accurate Available Bandwidth Estimation

## Overview
PathKatana is a CLI tool for measuring available bandwidth between client and server using UDP packet trains and analysis of delta delays. The method is based on the PathKatana algorithm (SIGCOMM'22).

## Components
- `sender.py`: sends UDP packet trains using binary search over transmission rate
- `receiver.py`: logs packet arrival times and calculates delta delays
- `analyze.py`: analyzes a single CSV result (supports Kalman filter)
- `analyze_ext.py`: batch analysis of multiple CSVs with PDF output and curve fitting

## Usage

### 1. Start receiver
```bash
python3 pathkatana_cli.py recv --csv-prefix test --loop
```

### 2. Start sender
```bash
python3 pathkatana_cli.py send
```

### 3. Analyze single result
```bash
python3 analyze.py --input results/test-YYYYMMDD_HHMMSS.csv --pdf
```

### 4. Batch analysis
```bash
python3 analyze_ext.py --input results/*.csv
```

## Features
- Binary search for stable bandwidth
- Kalman filter (optional)
- Delta delay graphs
- Theoretical sigmoid curve fitting in PDF reports


