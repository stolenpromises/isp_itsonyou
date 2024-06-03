# BEGIN CONTEXT: FILE 2/3
# File: traceroute_analysis.py

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st

def suggest_high_latency_periods(df_total_latency, min_threshold, max_threshold, top_n=5):
    """
    Suggest high latency periods based on the defined thresholds.

    Parameters
    ----------
    df_total_latency : pd.DataFrame
        DataFrame containing total average latency data.
    min_threshold : float
        Minimum latency threshold to identify high latency periods.
    max_threshold : float
        Maximum latency threshold to identify high latency periods.
    top_n : int, optional
        Number of top high latency periods to suggest (default is 5).

    Returns
    -------
    pd.DataFrame
        DataFrame containing the suggested high latency periods.
    """
    high_latency_periods = df_total_latency[(df_total_latency['total_avg_latency'] >= min_threshold) &
                                            (df_total_latency['total_avg_latency'] <= max_threshold)]
    high_latency_periods = high_latency_periods.sort_values(by='total_avg_latency', ascending=False)
    return high_latency_periods.head(top_n)

def visualize_high_latency_periods(df_all, high_latency_intervals):
    """
    Visualize individual hop latencies and incremental latencies for high latency periods.

    Parameters
    ----------
    df_all : pd.DataFrame
        DataFrame containing parsed traceroute data.
    high_latency_intervals : list of tuples
        List of tuples, each containing a start and end timestamp for the high latency intervals.

    Returns
    -------
    None
    """
    for interval in high_latency_intervals:
        start_time, end_time = interval
        df_high_latency = df_all[(df_all['timestamp'] >= start_time) & (df_all['timestamp'] <= end_time)]

        plt.figure(figsize=(12, 6))
        hop_numbers = df_high_latency['hop_number'].unique()
        avg_latencies = [df_high_latency[df_high_latency['hop_number'] == hop]['avg'].mean() for hop in hop_numbers]

        incremental_latencies = [avg_latencies[0]]  # First hop latency is taken as it is
        for i in range(1, len(avg_latencies)):
            incremental_latency = avg_latencies[i] - avg_latencies[i - 1]
            incremental_latencies.append(incremental_latency)

        plt.bar(hop_numbers, incremental_latencies, label=f'Interval: {start_time} to {end_time}')
        plt.xlabel('Hop Number')
        plt.ylabel('Incremental Latency (ms)')
        plt.title(f'Incremental Latency for High Latency Interval: {start_time} to {end_time}')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot()

def plot_total_avg_latency_over_time(df_total_latency):
    """
    Plot the total average latency over time with dynamic x-axis scaling.

    Parameters
    ----------
    df_total_latency : pd.DataFrame
        DataFrame containing total average latency data.

    Returns
    -------
    None
    """
    df_total_latency['timestamp'] = pd.to_datetime(df_total_latency['timestamp'])

    plt.figure(figsize=(12, 6))
    plt.plot(df_total_latency['timestamp'], df_total_latency['total_avg_latency'], label='Total Avg Latency')
    plt.axhline(y=df_total_latency['total_avg_latency'].mean(), color='r', linestyle='--', label='Average Latency')
    plt.xlabel('Timestamp')
    plt.ylabel('Total Average Latency (ms)')
    plt.title('Total Average Latency Over Time')
    plt.legend()
    plt.grid(True)

    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    plt.gca().xaxis.set_major_locator(locator)
    plt.gca().xaxis.set_major_formatter(formatter)

    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot()

# END CONTEXT: FILE 2/3
