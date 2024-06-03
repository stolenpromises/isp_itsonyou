# BEGIN CONTEXT: FILE 1/3
# File: log_parser.py

import os
import re
from datetime import datetime
import pandas as pd

def parse_traceroute_log(file_path):
    """
    Parse a single traceroute log file.

    Parameters
    ----------
    file_path : str
        Path to the traceroute log file.

    Returns
    -------
    list of dict
        List of dictionaries containing parsed data for each hop.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return []
    except Exception as e:
        return []

    filename = os.path.basename(file_path)
    timestamp_str = filename.split('_')[1].split('.')[0]
    timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')

    hop_data = []
    hop_pattern = re.compile(r"^\s*(\d+)\.\|--\s*([^ ]+)\s+([\d\.]+)%\s+(\d+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")

    for line in lines:
        match = hop_pattern.match(line)
        if match:
            hop = {
                'timestamp': timestamp,
                'hop_number': int(match.group(1)),
                'host': match.group(2),
                'loss_percentage': float(match.group(3)),
                'sent': int(match.group(4)),
                'last': float(match.group(5)),
                'avg': float(match.group(6)),
                'best': float(match.group(7)),
                'worst': float(match.group(8)),
                'stdev': float(match.group(9))
            }
            hop_data.append(hop)

    return hop_data

def extract_logs(logs_directory):
    """
    Extract logs from a specified directory.

    Parameters
    ----------
    logs_directory : str
        Path to the directory containing the logs.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the parsed data from the logs.
    """
    log_files = [os.path.join(logs_directory, f) for f in os.listdir(logs_directory) if f.endswith('.txt')]
    all_hop_data = []
    for log_file in log_files:
        all_hop_data.extend(parse_traceroute_log(log_file))

    return pd.DataFrame(all_hop_data)

# END CONTEXT: FILE 1/3
