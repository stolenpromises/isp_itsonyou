import streamlit as st
import zipfile
import os
import pandas as pd
from datetime import datetime, timedelta
from traceroute_analysis import suggest_high_latency_periods, visualize_high_latency_periods, plot_total_avg_latency_over_time
from log_import import extract_logs  # Import the extract_logs function

# Set page title and layout
st.set_page_config(page_title="ISP Itsonyou Traceroute Analysis", layout="wide")

# Sidebar for user input
with st.sidebar:
    st.title("Traceroute Analysis Options")

    # File upload for zip file or folder selection
    file_upload = st.file_uploader("Upload Traceroute Logs (zip or folder)", type=["zip", "folder"])

    # Get list of available folders
    folder_options = [f for f in os.listdir() if os.path.isdir(f)]

    # Select folder if available
    selected_folder = st.selectbox("Select Folder", folder_options, index=0) if folder_options else None

    # Button to trigger analysis
    analyze_button = st.button("Analyze Logs")

# Main content area
if file_upload or selected_folder:
    # Define the extraction path
    extraction_path = 'parsed_logs/temp'
    
    # Extract logs if zip file is uploaded
    if file_upload and file_upload.name.endswith(".zip"):
        with zipfile.ZipFile(file_upload, 'r') as zip_ref:
            zip_ref.extractall(extraction_path)
        
        # Extract and parse logs
        df_all_hops = extract_logs(logs_directory=extraction_path)
        
        if df_all_hops.empty:
            st.error("No log files found in the uploaded zip file.")
            st.stop()
        
        # Save the parsed data to a CSV file
        csv_file_path = os.path.join(extraction_path, 'parsed_logs.csv')
        df_all_hops.to_csv(csv_file_path, index=False)
    else:
        # Read logs from folder if folder is selected
        csv_file_path = os.path.join(selected_folder, 'parsed_logs.csv')
        if os.path.exists(csv_file_path):
            df_all_hops = pd.read_csv(csv_file_path)
        else:
            st.error(f"No CSV file found in the selected folder: {csv_file_path}")
            st.stop()

    # Parse timestamps
    df_all_hops['timestamp'] = pd.to_datetime(df_all_hops['timestamp'])

    # Extract unique months, weeks, and days for dropdowns
    df_all_hops['month'] = df_all_hops['timestamp'].dt.to_period('M')
    df_all_hops['week'] = df_all_hops['timestamp'].dt.to_period('W')
    df_all_hops['day'] = df_all_hops['timestamp'].dt.to_period('D')

    unique_months = df_all_hops['month'].unique().tolist()
    unique_weeks = df_all_hops['week'].unique().tolist()
    unique_days = df_all_hops['day'].unique().tolist()

    # Dropdowns for month, week, and day selection
    selected_month = st.selectbox("Select Month", unique_months, format_func=lambda x: x.strftime('%Y-%m'))
    selected_week = st.selectbox("Select Week", unique_weeks, format_func=lambda x: x.strftime('%Y-%W'))
    selected_day = st.selectbox("Select Day", unique_days, format_func=lambda x: x.strftime('%Y-%m-%d'))

    # Filter data based on the selected time frame
    if selected_day:
        filtered_df = df_all_hops[df_all_hops['day'] == selected_day]
    elif selected_week:
        filtered_df = df_all_hops[df_all_hops['week'] == selected_week]
    elif selected_month:
        filtered_df = df_all_hops[df_all_hops['month'] == selected_month]
    else:
        filtered_df = df_all_hops

    # Plot the filtered data
    df_total_filtered_latency = filtered_df.groupby('timestamp')['avg'].sum().reset_index()
    df_total_filtered_latency.rename(columns={'avg': 'total_avg_latency'}, inplace=True)
    
    st.header("Filtered Latency Over Time")
    plot_total_avg_latency_over_time(df_total_filtered_latency)

    # Calculate total average latency for the entire dataset
    df_total_latency = df_all_hops.groupby('timestamp')['avg'].sum().reset_index()
    df_total_latency.rename(columns={'avg': 'total_avg_latency'}, inplace=True)

    # Define latency thresholds
    min_latency = st.number_input("Minimum Latency (ms)", min_value=0, value=150)
    max_latency = st.number_input("Maximum Latency (ms)", min_value=0, value=2500)

    # Display options for high latency analysis
    st.header("High Latency Analysis")

    # Option to specify number of high latency periods
    num_high_latency_periods = st.number_input("Number of High Latency Periods", min_value=1, max_value=100, value=40)

    # Option to suggest high latency periods
    if st.checkbox("Suggest High Latency Periods"):
        high_latency_periods = suggest_high_latency_periods(df_total_latency, min_latency, max_latency, top_n=num_high_latency_periods)
        st.write(high_latency_periods)

    # Option to visualize high latency periods
    if st.checkbox("Visualize High Latency Periods"):
        # Ensure high_latency_periods DataFrame is not empty
        if not high_latency_periods.empty:
            # Convert the selected periods to tuples of start and end times
            high_latency_intervals = [(row['timestamp'], row['timestamp']) for _, row in high_latency_periods.iterrows()]
            interval_options = [f"{start} to {end}" for start, end in high_latency_intervals]
            selected_interval = st.selectbox("Select High Latency Interval", interval_options)

            # Parse the selected interval string back to tuple
            start_time_str, end_time_str = selected_interval.split(" to ")
            selected_interval_tuple = (start_time_str, end_time_str)

            # Display the filtered data for the selected interval
            df_high_latency = df_all_hops[(df_all_hops['timestamp'] >= start_time_str) & (df_all_hops['timestamp'] <= end_time_str)]
            st.write(df_high_latency)

            # Button to select +/- interval around the high latency period
            interval_minutes = st.number_input("Select +/- Interval (minutes)", min_value=1, max_value=120, value=10)
            if st.button("Plot Total Average Latency Over Interval"):
                start_interval = (datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=interval_minutes)).strftime('%Y-%m-%d %H:%M:%S')
                end_interval = (datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=interval_minutes)).strftime('%Y-%m-%d %H:%M:%S')
                df_interval_latency = df_all_hops[(df_all_hops['timestamp'] >= start_interval) & (df_all_hops['timestamp'] <= end_interval)]
                
                # Plot total average latency over the interval
                df_total_interval_latency = df_interval_latency.groupby('timestamp')['avg'].sum().reset_index()
                df_total_interval_latency.rename(columns={'avg': 'total_avg_latency'}, inplace=True)

                plot_total_avg_latency_over_time(df_total_interval_latency)

            print("Passing selected high latency interval to visualize_high_latency_periods:", selected_interval_tuple)  # Debug print statement
            visualize_high_latency_periods(df_all_hops, [selected_interval_tuple])
        else:
            st.info("No high latency periods to visualize.")

    # Plot total average latency over time for the entire dataset
    st.header("Total Latency Over Entire Period")
    plot_total_avg_latency_over_time(df_total_latency)

else:
    st.info("Please upload your traceroute logs or select a folder to begin analysis.")
