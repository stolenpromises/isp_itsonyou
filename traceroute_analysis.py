# BEGIN CONTEXT: FILE 4/6 - traceroute_analysis.py

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

def visualize_high_latency_periods(df_all, high_latency_intervals, print_full_content=False):
    """
    Visualize individual hop latencies and incremental latencies for high latency periods.

    Parameters
    ----------
    df_all : pd.DataFrame
        DataFrame containing parsed traceroute data.
    high_latency_intervals : list of tuples
        List of tuples, each containing a start and end timestamp for the high latency intervals.
    print_full_content : bool, optional
        Flag to print full content of high latency data (default is False).

    Returns
    -------
    None
    """
    for interval in high_latency_intervals:
        start_time, end_time = interval
        df_high_latency = df_all[(df_all['timestamp'] >= start_time) & (df_all['timestamp'] <= end_time)]
        
        if print_full_content:
            print(f"\nHigh latency data for interval {start_time} to {end_time}:")
            print(df_high_latency)
        
        hop_numbers = df_high_latency['hop_number'].unique()
        avg_latencies = [df_high_latency[df_high_latency['hop_number'] == hop]['avg'].mean() for hop in hop_numbers]
        
        # Calculate incremental latency for each hop
        incremental_latencies = [avg_latencies[0]]  # First hop latency is taken as it is
        for i in range(1, len(avg_latencies)):
            incremental_latency = avg_latencies[i] - avg_latencies[i - 1]
            incremental_latencies.append(incremental_latency)
        
        # Plot the incremental latency
        plot_data(
            x_data=hop_numbers,
            y_data=incremental_latencies,
            x_label='Hop Number',
            y_label='Incremental Latency (ms)',
            title=f'Incremental Latency for High Latency Interval: {start_time} to {end_time}'
        )

def plot_data(x_data, y_data, x_label, y_label, title, plot_type='line'):
    """
    General function to plot data.

    Parameters
    ----------
    x_data : list or pd.Series
        Data for the x-axis.
    y_data : list or pd.Series
        Data for the y-axis.
    x_label : str
        Label for the x-axis.
    y_label : str
        Label for the y-axis.
    title : str
        Title of the plot.
    plot_type : str, optional
        Type of plot to generate ('line', 'bar', 'dot'), default is 'line'.

    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if plot_type == 'line':
        ax.plot(x_data, y_data, label=title)
    elif plot_type == 'bar':
        ax.bar(x_data, y_data, label=title)
    elif plot_type == 'dot':
        ax.plot(x_data, y_data, 'o', label=title)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# END CONTEXT: FILE 4/6 - traceroute_analysis.py