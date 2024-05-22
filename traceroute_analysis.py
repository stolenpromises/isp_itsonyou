import os
import pandas as pd
import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Function to parse a single log file
def parse_traceroute_log(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Extract timestamp from the filename
    filename = os.path.basename(file_path)
    timestamp_str = filename.split('_')[1].split('.')[0]
    timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
    
    # Extract hop data
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

# Function to visualize individual hop latencies for high latency periods
def visualize_high_latency_periods(df_all, df_total_latency, threshold):
    high_latency_periods = df_total_latency[df_total_latency['total_avg_latency'] > threshold]

    for timestamp in high_latency_periods['timestamp']:
        df_high_latency = df_all[df_all['timestamp'] == timestamp]
        plt.figure(figsize=(12, 6))
        for hop in df_high_latency['hop_number'].unique():
            df_hop = df_high_latency[df_high_latency['hop_number'] == hop]
            plt.plot(df_hop['hop_number'], df_hop['avg'], label=f'Hop {hop}')
        plt.xlabel('Hop Number')
        plt.ylabel('Average Latency (ms)')
        plt.title(f'Individual Hop Latencies for High Latency Period: {timestamp}')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

# Function to suggest key time intervals
def suggest_key_intervals(df, std_dev_multiplier=2, min_duration='2T', max_duration='5T'):
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
extraction_dir = os.path.join(extraction_path, 'isp_itsonyou', 'traceroute_logs')

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