import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def suggest_high_latency_periods(df_total_latency, threshold, top_n=10):
    """
    Suggest high latency periods based on the defined threshold.

    Parameters
    ----------
    df_total_latency : pd.DataFrame
        DataFrame containing total average latency data.
    threshold : float
        Latency threshold to identify high latency periods.
    top_n : int, optional
        Number of top high latency periods to suggest (default is 10).

    Returns
    -------
    pd.DataFrame
        DataFrame containing the suggested high latency periods.
    """
    high_latency_periods = df_total_latency[df_total_latency['total_avg_latency'] > threshold]
    print("Suggested high latency periods:")
    print(high_latency_periods.head(top_n))
    return high_latency_periods.head(top_n)

def visualize_high_latency_periods(df_all, high_latency_intervals, print_full_content=False):
    """
    Visualize individual hop latencies for high latency periods.

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
        
        plt.figure(figsize=(12, 6))
        hop_numbers = df_high_latency['hop_number'].unique()
        avg_latencies = [df_high_latency[df_high_latency['hop_number'] == hop]['avg'].mean() for hop in hop_numbers]
        
        for hop in hop_numbers:
            df_hop = df_high_latency[df_high_latency['hop_number'] == hop]
            if print_full_content:
                print(f"Plotting data for Hop {hop}:")
                print(df_hop[['hop_number', 'avg']])
        
        plt.scatter(hop_numbers, avg_latencies, label=f'Interval: {start_time} to {end_time}')
        plt.xlabel('Hop Number')
        plt.ylabel('Average Latency (ms)')
        plt.title(f'Individual Hop Latencies for High Latency Interval: {start_time} to {end_time}')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

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
    # Convert timestamps to datetime objects
    df_total_latency['timestamp'] = pd.to_datetime(df_total_latency['timestamp'])
    
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
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    plt.gca().xaxis.set_major_locator(locator)
    plt.gca().xaxis.set_major_formatter(formatter)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main(high_latency_intervals=None, print_full_content=False):
    """
    Main function to run the traceroute analysis.

    Parameters
    ----------
    high_latency_intervals : list of tuples, optional
        List of tuples, each containing a start and end timestamp for the high latency intervals (default is None).
    print_full_content : bool, optional
        Flag to print full content of high latency data (default is False).

    Returns
    -------
    None
    """
    # Load the DataFrame
    df_all_hops = pd.read_csv('/mnt/data/parsed_logs.csv')

    # Calculate total average latency
    df_total_latency = df_all_hops.groupby('timestamp')['avg'].sum().reset_index()
    df_total_latency.rename(columns={'avg': 'total_avg_latency'}, inplace=True)

    # Define latency threshold
    latency_threshold = df_total_latency['total_avg_latency'].mean() + 2 * df_total_latency['total_avg_latency'].std()

    if high_latency_intervals is None:
        # Suggest high latency periods and plot total average latency over time
        high_latency_periods = suggest_high_latency_periods(df_total_latency, latency_threshold)
        plot_total_avg_latency_over_time(df_total_latency)
    else:
        # Visualize high latency periods for specified intervals
        visualize_high_latency_periods(df_all_hops, high_latency_intervals, print_full_content)
        plot_total_avg_latency_over_time(df_total_latency)

# Example usage
# First run (no parameter, suggest high latency intervals)
# main()

# Second run (with specified high latency intervals)
# Example interval format: [('2024-05-21 23:10', '2024-05-21 23:15')]
# main(high_latency_intervals=[('2024-05-21 20:16:14', '2024-05-21 20:26:17'), ('2024-05-22 01:57:55', '2024-05-22 02:00:00')], print_full_content=False)