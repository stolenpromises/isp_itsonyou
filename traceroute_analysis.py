import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st

def plot_data(x_data, y_data, x_label, y_label, title, plot_type='line'):
    fig, ax = plt.subplots(figsize=(12, 6))
    if plot_type == 'line':
        ax.plot(x_data, y_data, label=title)
    elif plot_type == 'bar':
        ax.bar(x_data, y_data, label=title)
    
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    
    # Dynamic Y-axis scaling
    max_y = max(y_data)
    if max_y >= 60000:  # Scale to minutes
        ax.set_ylabel(y_label + ' (minutes)')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x / 60000:.1f}'))
    elif max_y >= 1000:  # Scale to seconds
        ax.set_ylabel(y_label + ' (seconds)')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x / 1000:.1f}'))
    else:
        ax.set_ylabel(y_label + ' (ms)')
    
    plt.xticks(rotation=45)
    st.pyplot(fig)

def suggest_high_latency_periods(df_total_latency, min_threshold, max_threshold, top_n=5):
    high_latency_periods = df_total_latency[(df_total_latency['total_avg_latency'] >= min_threshold) & 
                                            (df_total_latency['total_avg_latency'] <= max_threshold)]
    high_latency_periods = high_latency_periods.sort_values(by='total_avg_latency', ascending=False)
    return high_latency_periods.head(top_n)

def visualize_high_latency_periods(df_all, high_latency_intervals, print_full_content=False):
    for interval in high_latency_intervals:
        timestamp = interval
        df_high_latency = df_all[df_all['timestamp'] == timestamp]
        
        if print_full_content:
            print(f"\nHigh latency data for interval {timestamp}:")
            print(df_high_latency)
        
        hop_numbers = df_high_latency['hop_number'].unique()
        avg_latencies = [df_high_latency[df_high_latency['hop_number'] == hop]['avg'].mean() for hop in hop_numbers]
        
        incremental_latencies = [avg_latencies[0]]  # First hop latency is taken as it is
        for i in range(1, len(avg_latencies)):
            incremental_latency = avg_latencies[i] - avg_latencies[i - 1]
            incremental_latencies.append(incremental_latency)
        
        plot_data(
            x_data=hop_numbers,
            y_data=incremental_latencies,
            x_label='Hop Number',
            y_label='Incremental Latency (ms)',
            title=f'Incremental Latency for High Latency Interval: {timestamp}',
            plot_type='bar'
        )

def plot_total_avg_latency_over_time(df_total_latency):
    df_total_latency['timestamp'] = pd.to_datetime(df_total_latency['timestamp'])
    plot_data(
        x_data=df_total_latency['timestamp'],
        y_data=df_total_latency['total_avg_latency'],
        x_label='Timestamp',
        y_label='Total Average Latency',
        title='Total Average Latency Over Time'
    )
