# ISP Itsonyou

## Overview

This project analyzes traceroute logs to identify and visualize network latency patterns.

## Features

- Load traceroute logs from a folder and convert them to CSV.
- Upload CSV files for analysis.
- Visualize total average latency over time.
- Identify and visualize high latency periods.
- Plot incremental latency for specified hops.

## Folder Structure
```
isp_itsonyou/
│
├── traceroute_analysis.py        # Main script for analyzing traceroute logs
├── log_parser.py                 # Script for importing and parsing logs
├── main.py                       # Streamlit-based user interface for the project
├── README.md                     # Project documentation
│
└── traceroute_logs/              # Directory containing traceroute log files
    ├── sample   # Sample logs for testing
```
## Installation

1. Clone the repository:

```sh
git clone <repository-url>
cd isp_itsonyou
```

2. Create a virtual environment and activate it:

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required dependencies:

```sh
pip install -r requirements.txt
```

## Usage

1. Ensure you have traceroute logs in the expected format.
2. Run the Streamlit application:

```sh
streamlit run main.py
```

3. Load your logs or CSV file using the sidebar.
4. Configure your analysis options and visualize the results.

## Generating Traceroute Logs

To generate traceroute logs, you can use the following example script to automate the process. This script will run `traceroute` every minute and save the output to a log file with a timestamp.

### Script to Generate Traceroute Logs

Save the following script as `generate_traceroute_logs.sh` and make it executable:

```sh
#!/bin/bash

# Create the directory for traceroute logs if it doesn't exist
mkdir -p traceroute_logs

while true; do
    # Get the current date and time
    timestamp=$(date +%Y%m%d%H%M%S)
    
    # Run traceroute and save the output to a log file
    traceroute google.com > traceroute_logs/traceroute_log_$timestamp.txt
    
    # Wait for 1 minute before running the next traceroute
    sleep 60
done
```

Make the script executable:

```sh
chmod +x generate_traceroute_logs.sh
```

Run the script to start generating logs:

```sh
./generate_traceroute_logs.sh
```

### Important Notes

- Ensure that the log files are saved in the `traceroute_logs` directory as shown in the script.
- Each log file should be named with the timestamp format `traceroute_log_YYYYMMDDHHMMSS.txt`.

## Sample Data

Sample logs and a sample CSV are available in the `parsed_logs` and `traceroute_logs` folders respectively.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Dependencies
- Python 3.x
- Pandas
- Matplotlib
- Streamlit


## Metrics to Implement:

### Packet Loss Analysis:

- Analyze and visualize packet loss percentages for each hop.

### Latency Percentiles:

- Calculate and visualize latency percentiles (e.g., 95th, 99th).

---
