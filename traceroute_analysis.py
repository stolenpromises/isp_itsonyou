import os
import pandas as pd
import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
        Parsed data containing hop information.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Extract timestamp from the filename
    filename = os.path.basename(file_path)
    timestamp_str = filename.split('_')[1].split('.')[0]
    timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
    
    # Extract hop data using regex pattern matching
    hop_data = []
    hop_pattern = re.compile(r"^\s*(\d+)\.\|\--\s*([^ ]+)\s+([\d\.]+)%\s+(\d+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")
    
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

def visualize_high_latency_periods(df_all, df_total_latency, threshold):
    """
    Visualize individual hop latencies for high latency periods.

    Parameters
    ----------
    df_all : DataFrame
        DataFrame containing parsed traceroute data.
    df_total_latency : DataFrame
        DataFrame containing total average latency data.
    threshold : float
        Latency threshold to identify high latency periods.
    """
    high_latency_periods = df_total_latency[df_total_latency['total_avg_latency'] > threshold]
    print("High latency periods:")
    print(high_latency_periods)

    for timestamp in high_latency_periods['timestamp']:
        df_high_latency = df_all[df_all['timestamp'] == timestamp]
        print(f"\nHigh latency data for {timestamp}:")
        print(df_high_latency)

        plt.figure(figsize=(12, 6))
        hop_numbers = []
        avg_latencies = []
        for hop in df_high_latency['hop_number'].unique():
            df_hop = df_high_latency[df_high_latency['hop_number'] == hop]
            hop_numbers.append(hop)
            avg_latencies.append(df_hop['avg'].values[0])
            print(f"Plotting data for Hop {hop}:")
            print(df_hop[['hop_number', 'avg']])

        plt.scatter(hop_numbers, avg_latencies, label=f'Timestamp: {timestamp}')
        plt.xlabel('Hop Number')
        plt.ylabel('Average Latency (ms)')
        plt.title(f'Individual Hop Latencies for High Latency Period: {timestamp}')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def suggest_key_intervals(df, std_dev_multiplier=2, min_duration='2T', max_duration='5T'):
    """
    Suggest time intervals where latency exceeds a specified threshold for a sustained period.

    Parameters
    ----------
    df : DataFrame
        DataFrame containing total average latency data.
    std_dev_multiplier : float
        Multiplier for standard deviation to set the threshold.
    min_duration : str
        Minimum duration for the sustained period (e.g., '2T' for 2 minutes).
    max_duration : str
        Maximum duration for the sustained period (e.g., '5T' for 5 minutes).

    Returns
    -------
    list of tuple
        List of suggested time intervals.
    """
    mean_latency = df['total_avg_latency'].mean()
    std_dev_latency = df['total_avg_latency'].std()
    threshold = mean_latency + std_dev_multiplier * std_dev_latency
    
    df['exceeds_threshold'] = df['total_avg_latency'] > threshold
    df['group'] = (df['exceeds_threshold'] != df['exceeds_threshold'].shift()).cumsum()
    
    intervals = []
    for _, group in df[df['exceeds_threshold']].groupby('group'):
        if len(group) >= pd.to_timedelta(min_duration) / (df['timestamp'].iloc[1] - df['timestamp'].iloc[0]):
            start_time = group['timestamp'].min()
            end_time = group['timestamp'].max()
            duration = end_time - start_time
            if pd.to_timedelta(min_duration) <= duration <= pd.to_timedelta(max_duration):
                intervals.append((start_time, end_time))
    
    return intervals[:10]

# Directory containing the log files
extraction_dir = os.path.join('traceroute_logs')

# List all log files
log_files = [os.path.join(extraction_dir, file) for file in os.listdir(extraction_dir) if file.endswith('.txt')]

# Parse each log file and aggregate the data from all available logs
all_data = []
for log_file in log_files:
    all_data.extend(parse_traceroute_log(log_file))

# Create a DataFrame from the aggregated data
df_all = pd.DataFrame(all_data)

# Calculate total average latency per timestamp
df_total_latency = df_all.groupby('timestamp')['avg'].sum().reset_index()
df_total_latency.columns = ['timestamp', 'total_avg_latency']

# Determine the appropriate x-axis locator based on the time range
time_range = df_total_latency['timestamp'].max() - df_total_latency['timestamp'].min()

if time_range < pd.Timedelta('1 days'):
    locator = mdates.HourLocator(interval=1)
    formatter = mdates.DateFormatter('%I %p')
elif time_range < pd.Timedelta('7 days'):
    locator = mdates.DayLocator(interval=1)
    formatter = mdates.DateFormatter('%b %d')
else:
    locator = mdates.WeekdayLocator(interval=1)
    formatter = mdates.DateFormatter('%b %d')

# Plot with dynamic x-axis scaling
plt.figure(figsize=(12, 6))
plt.plot(df_total_latency['timestamp'], df_total_latency['total_avg_latency'], label='Total Avg Latency')
plt.axhline(y=df_total_latency['total_avg_latency'].mean(), color='r', linestyle='--', label='Average Latency')
plt.xlabel('Timestamp')
plt.ylabel('Total Average Latency (ms)')
plt.title('Total Average Latency Over Time')
plt.legend()
plt.grid(True)

# Set dynamic x-axis locator and formatter
plt.gca().xaxis.set_major_locator(locator)
plt.gca().xaxis.set_major_formatter(formatter)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Example usage of the new functions
threshold = 250  # example threshold value for testing
visualize_high_latency_periods(df_all, df_total_latency, threshold)

# Suggest key time intervals where latency exceeds threshold for a sustained period
suggested_intervals = suggest_key_intervals(df_total_latency, std_dev_multiplier=2)
print("Suggested high latency intervals:")
for start, end in suggested_intervals:
    print(f"From {start} to {end}")