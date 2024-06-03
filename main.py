# BEGIN CONTEXT: FILE 3/6 - main.py

import os
import pandas as pd
import streamlit as st
from log_parser import extract_logs
from traceroute_analysis import suggest_high_latency_periods, visualize_high_latency_periods, plot_total_avg_latency_over_time
import matplotlib.pyplot as plt

# Set page title and layout
st.set_page_config(page_title="ISP Traceroute Analysis", layout="wide")

# Title
st.title("Traceroute Analysis")

# Sidebar for user input
with st.sidebar:
    st.header("Traceroute Analysis Options")

    # Folder selection for logs
    log_folder = st.text_input("Enter the path to the folder with logs")

    # Button to trigger log extraction and CSV conversion
    if st.button("Load Logs and Convert to CSV", key='load_convert'):
        if log_folder and os.path.isdir(log_folder):
            df_all_hops = extract_logs(log_folder)
            csv_file_path = os.path.join(log_folder, 'parsed_logs.csv')
            df_all_hops.to_csv(csv_file_path, index=False)
            st.success(f"Logs converted to CSV and saved at {csv_file_path}")
        else:
            st.error("Please enter a valid folder path")

    # CSV file upload
    csv_file = st.file_uploader("Upload CSV File", type=["csv"])

# Main content area
if csv_file:
    df_all_hops = pd.read_csv(csv_file)
    df_all_hops['timestamp'] = pd.to_datetime(df_all_hops['timestamp'])

    # Columns for Time Scope and Options
    col1, col2 = st.columns(2)

    with col1:
        # Time Scope Selection
        st.header("Time Scope")
        unique_months = df_all_hops['timestamp'].dt.to_period('M').unique().tolist()
        unique_weeks = df_all_hops['timestamp'].dt.to_period('W').unique().tolist()
        unique_days = df_all_hops['timestamp'].dt.to_period('D').unique().tolist()

        selected_month = st.selectbox("Select Month", ["All"] + unique_months, format_func=lambda x: 'All' if x == "All" else str(x))
        selected_week = st.selectbox("Select Week", ["All"] + unique_weeks, format_func=lambda x: 'All' if x == "All" else str(x))
        selected_days = st.multiselect("Select Days", unique_days, format_func=lambda x: 'All' if x == "All" else x.strftime('%Y-%m-%d'))

    with col2:
        # Options
        st.header("Options")
        suggest_high_latency = st.checkbox("Suggest High Latency Periods", value=True)
        visualize_high_latency = st.checkbox("Visualize High Latency Periods", value=True)

        # Min/Max Latency Inputs
        min_latency = st.number_input("Minimum Latency (ms)", min_value=0, value=150)
        max_latency = st.number_input("Maximum Latency (ms)", min_value=0, value=2500)
        num_high_latency_periods = st.number_input("Number of High Latency Periods", min_value=1, max_value=100, value=5)

        # Hop Plot Section
        plot_hop = st.checkbox("Plot Hop Incremental Latency", value=True)
        hop_numbers = df_all_hops['hop_number'].unique().tolist()
        selected_hops = st.multiselect("Specify Hop Number", hop_numbers, default=hop_numbers[:1])

    # Main Plot Button
    if st.button("Plot", key='main_plot'):
        filtered_df = df_all_hops.copy()
        if selected_month != "All":
            filtered_df = filtered_df[filtered_df['timestamp'].dt.to_period('M') == selected_month]
        if selected_week != "All":
            filtered_df = filtered_df[filtered_df['timestamp'].dt.to_period('W') == selected_week]
        if selected_days:
            filtered_df = filtered_df[filtered_df['timestamp'].dt.to_period('D').isin(selected_days)]

        # Plot Average Total Latency Over Scope
        df_total_filtered_latency = filtered_df.groupby('timestamp')['avg'].sum().reset_index()
        df_total_filtered_latency.rename(columns={'avg': 'total_avg_latency'}, inplace=True)
        st.header("Filtered Latency Over Time")
        fig, ax = plt.subplots()
        ax.plot(df_total_filtered_latency['timestamp'], df_total_filtered_latency['total_avg_latency'], label='Total Avg Latency')
        ax.axhline(y=df_total_filtered_latency['total_avg_latency'].mean(), color='r', linestyle='--', label='Average Latency')
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Total Average Latency (ms)')
        ax.set_title('Total Average Latency Over Time')
        ax.legend()
        ax.grid(True)
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # High Latency Analysis
        if suggest_high_latency:
            high_latency_periods = suggest_high_latency_periods(df_total_filtered_latency, min_latency, max_latency, top_n=num_high_latency_periods)
            st.write(high_latency_periods)
        if visualize_high_latency and 'high_latency_periods' in locals() and not high_latency_periods.empty:
            high_latency_intervals = [(row['timestamp'], row['timestamp']) for _, row in high_latency_periods.iterrows()]
            interval_options = [f"{start} to {end}" for start, end in high_latency_intervals]
            selected_interval = st.selectbox("Select High Latency Interval", interval_options, key='select_interval')

            start_time_str, end_time_str = selected_interval.split(" to ")
            selected_interval_tuple = (start_time_str, end_time_str)

            df_high_latency = filtered_df[(filtered_df['timestamp'] >= start_time_str) & (filtered_df['timestamp'] <= end_time_str)]
            st.write(df_high_latency)

            interval_minutes = st.number_input("Select +/- Interval (minutes)", min_value=1, max_value=120, value=10, key='interval_minutes')
            start_interval = (pd.to_datetime(start_time_str) - pd.Timedelta(minutes=interval_minutes)).strftime('%Y-%m-%d %H:%M:%S')
            end_interval = (pd.to_datetime(end_time_str) + pd.Timedelta(minutes=interval_minutes)).strftime('%Y-%m-%d %H:%M:%S')
            df_interval_latency = filtered_df[(filtered_df['timestamp'] >= start_interval) & (filtered_df['timestamp'] <= end_interval)]

            df_total_interval_latency = df_interval_latency.groupby('timestamp')['avg'].sum().reset_index()
            df_total_interval_latency.rename(columns={'avg': 'total_avg_latency'}, inplace=True)

            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(df_total_interval_latency['timestamp'], df_total_interval_latency['total_avg_latency'], label='Total Avg Latency')
            ax.axhline(y=df_total_interval_latency['total_avg_latency'].mean(), color='r', linestyle='--', label='Average Latency')
            ax.set_xlabel('Timestamp')
            ax.set_ylabel('Total Average Latency (ms)')
            ax.set_title('Total Average Latency Over Time')
            ax.legend()
            ax.grid(True)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            visualize_high_latency_periods(filtered_df, [selected_interval_tuple])

        # Plot Hop Incremental Latency
        if plot_hop:
            for hop_number in selected_hops:
                df_hop_latency = filtered_df[filtered_df['hop_number'] == hop_number]
                df_hop_latency = df_hop_latency.groupby('timestamp')['avg'].mean().reset_index()
                df_hop_latency.rename(columns={'avg': 'incremental_latency'}, inplace=True)

                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(df_hop_latency['timestamp'], df_hop_latency['incremental_latency'], label=f'Incremental Latency for Hop {hop_number}')
                ax.set_xlabel('Timestamp')
                ax.set_ylabel('Incremental Latency (ms)')
                ax.set_title(f'Incremental Latency for Hop {hop_number} Over Time')
                ax.legend()
                ax.grid(True)
                plt.xticks(rotation=45)
                st.pyplot(fig)

else:
    st.info("Please upload your traceroute logs or select a folder to begin analysis.")

# END CONTEXT: FILE 6/6 - main.py
