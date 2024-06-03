import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st

def suggest_high_latency_periods(df_total_latency, min_threshold, max_threshold, top_n=5):
    high_latency_periods = df_total_latency[(df_total_latency['total_avg_latency'] >= min_threshold) & 
                                            (df_total_latency['total_avg_latency'] <= max_threshold)]
    high_latency_periods = high_latency_periods.sort_values(by='total_avg_latency', ascending=False)
    return high_latency_periods.head(top_n)

def visualize_high_latency_periods(df_all, high_latency_intervals, print_full_content=False):
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

    # Dynamic y-axis scaling
    y_unit = format_y_axis(y_data)
    if y_unit == 'minutes':
        y_data = y_data / 60000
        y_label += ' (minutes)'
    elif y_unit == 'seconds':
        y_data = y_data / 1000
        y_label += ' (seconds)'
    
    st.pyplot(fig)

def format_y_axis(y_data):
    max_y = max(y_data)
    if max_y >= 60000:
        return 'minutes'
    elif max_y >= 1000:
        return 'seconds'
    else:
        return 'ms'
