import streamlit as st
import zipfile
import os
import pandas as pd
from traceroute_analysis import suggest_high_latency_periods, visualize_high_latency_periods, plot_total_avg_latency_over_time

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
    # Extract logs if zip file is uploaded
    if file_upload and file_upload.name.endswith(".zip"):
        with zipfile.ZipFile(file_upload, 'r') as zip_ref:
            zip_ref.extractall('parsed_logs/temp')
        # Read logs from folder
        df_all_hops = pd.read_csv(os.path.join('parsed_logs/temp', 'parsed_logs.csv'))
        os.remove(os.path.join('parsed_logs/temp', 'parsed_logs.csv'))
    else:
        # Read logs from folder if folder is selected
        df_all_hops = pd.read_csv(os.path.join(selected_folder, 'parsed_logs.csv'))

    # Calculate total average latency
    df_total_latency = df_all_hops.groupby('timestamp')['avg'].sum().reset_index()
    df_total_latency.rename(columns={'avg': 'total_avg_latency'}, inplace=True)

    # Define latency threshold
    latency_threshold = df_total_latency['total_avg_latency'].mean() + 2 * df_total_latency['total_avg_latency'].std()

    # Display options for high latency analysis
    st.header("High Latency Analysis")

    # Option to suggest high latency periods
    if st.checkbox("Suggest High Latency Periods"):
        high_latency_periods = suggest_high_latency_periods(df_total_latency, latency_threshold)
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

            print("Passing selected high latency interval to visualize_high_latency_periods:", selected_interval_tuple)  # Debug print statement
            visualize_high_latency_periods(df_all_hops, [selected_interval_tuple])
        else:
            st.info("No high latency periods to visualize.")

    # Plot total average latency over time
    plot_total_avg_latency_over_time(df_total_latency)

else:
    st.info("Please upload your traceroute logs or select a folder to begin analysis.")
