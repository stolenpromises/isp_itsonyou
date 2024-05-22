import os
import zipfile
import pandas as pd
import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st

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

# Streamlit UI setup
st.title('Traceroute Analysis')

# File upload
uploaded_files = st.file_uploader("Upload Traceroute Log Files", accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for uploaded_file in uploaded_files:
        with open(f"/tmp/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        all_data.extend(parse_traceroute_log(f"/tmp/{uploaded_file.name}"))

    df_all = pd.DataFrame(all_data)

    # User input for date range
    start_date = st.date_input("Start Date", df_all['timestamp'].min().date())
    end_date = st.date_input("End Date", df_all['timestamp'].max().date())

    # Filter data based on user input
    df_filtered = df_all[(df_all['timestamp'] >= pd.Timestamp(start_date)) & (df_all['timestamp'] <= pd.Timestamp(end_date))]

    # Calculate total average latency per timestamp
    df_total_latency = df_filtered.groupby('timestamp')['avg'].sum().reset_index()
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
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_total_latency['timestamp'], df_total_latency['total_avg_latency'], label='Total Avg Latency')
    ax.axhline(y=df_total_latency['total_avg_latency'].mean(), color='r', linestyle='--', label='Average Latency')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Total Average Latency (ms)')
    ax.set_title('Total Average Latency Over Time')
    ax.legend()
    ax.grid(True)

    # Set dynamic x-axis locator and formatter
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    # Visualize individual hop latencies for high latency periods
    high_latency_periods = df_total_latency[df_total_latency['total_avg_latency'] > df_total_latency['total_avg_latency'].mean()]

    for timestamp in high_latency_periods['timestamp']:
        df_high_latency = df_filtered[df_filtered['timestamp'] == timestamp]
        fig, ax = plt.subplots(figsize=(12, 6))
        for hop in df_high_latency['hop_number'].unique():
            df_hop = df_high_latency[df_high_latency['hop_number'] == hop]
            ax.plot(df_hop['hop_number'], df_hop['avg'], label=f'Hop {hop}')
        ax.set_xlabel('Hop Number')
        ax.set_ylabel('Average Latency (ms)')
        ax.set_title(f'Individual Hop Latencies for High Latency Period: {timestamp}')
        ax.legend()
        ax.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
