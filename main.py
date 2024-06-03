import os
import pandas as pd
import streamlit as st
from log_parser import extract_logs
from traceroute_analysis import suggest_high_latency_periods, visualize_high_latency_periods, plot_total_avg_latency_over_time, plot_data

st.set_page_config(page_title="ISP Traceroute Analysis", layout="wide")
st.title("Traceroute Analysis")

with st.sidebar:
    st.header("Traceroute Analysis Options")
    log_folder = st.text_input("Enter the path to the folder with logs")
    if st.button("Load Logs and Convert to CSV", key='load_convert'):
        if log_folder and os.path.isdir(log_folder):
            df_all_hops = extract_logs(log_folder)
            csv_file_path = os.path.join(log_folder, 'parsed_logs.csv')
            df_all_hops.to_csv(csv_file_path, index=False)
            st.success(f"Logs converted to CSV and saved at {csv_file_path}")
        else:
            st.error("Please enter a valid folder path")
    csv_file = st.file_uploader("Upload CSV File", type=["csv"])

def set_ready_to_plot():
    st.session_state['ready_to_plot'] = True

if csv_file:
    df_all_hops = pd.read_csv(csv_file)
    df_all_hops['timestamp'] = pd.to_datetime(df_all_hops['timestamp'])

    col1, col2 = st.columns(2)

    with col1:
        st.header("Time Scope")
        unique_months = df_all_hops['timestamp'].dt.to_period('M').unique().tolist()
        unique_weeks = df_all_hops['timestamp'].dt.to_period('W').unique().tolist()
        unique_days = df_all_hops['timestamp'].dt.to_period('D').unique().tolist()

        selected_month = st.selectbox("Select Month", ["All"] + unique_months, format_func=lambda x: 'All' if x == "All" else str(x))
        selected_week = st.selectbox("Select Week", ["All"] + unique_weeks, format_func=lambda x: 'All' if x == "All" else str(x))
        selected_days = st.multiselect("Select Days", unique_days, format_func=lambda x: 'All' if x == "All" else x.strftime('%Y-%m-%d'))

        st.button("Ready to Plot", on_click=set_ready_to_plot, key='ready_to_plot_button')

    if st.session_state.get('ready_to_plot', False):
        with col2:
            st.header("Options")
            suggest_high_latency = st.checkbox("Suggest High Latency Periods", value=True)
            visualize_high_latency = st.checkbox("Visualize High Latency Periods", value=True)
            min_latency = st.number_input("Minimum Latency (ms)", min_value=0, value=150)
            max_latency = st.number_input("Maximum Latency (ms)", min_value=0, value=2500)
            num_high_latency_periods = st.number_input("Number of High Latency Periods", min_value=1, max_value=100, value=5)
            plot_hop = st.checkbox("Plot Hop Incremental Latency", value=True)
            hop_numbers = df_all_hops['hop_number'].unique().tolist()
            selected_hops = st.multiselect("Specify Hop Number", hop_numbers, default=hop_numbers[:1])

        if st.button("Plot", key='main_plot'):
            filtered_df = df_all_hops.copy()
            if selected_month != "All":
                filtered_df = filtered_df[filtered_df['timestamp'].dt.to_period('M') == selected_month]
            if selected_week != "All":
                filtered_df = filtered_df[filtered_df['timestamp'].dt.to_period('W') == selected_week]
            if selected_days:
                filtered_df = filtered_df[filtered_df['timestamp'].dt.to_period('D').isin(selected_days)]

            df_total_filtered_latency = filtered_df.groupby('timestamp')['avg'].sum().reset_index()
            df_total_filtered_latency.rename(columns={'avg': 'total_avg_latency'}, inplace=True)
            with col1:
                st.header("Filtered Latency Over Time")
                plot_total_avg_latency_over_time(df_total_filtered_latency)

            if suggest_high_latency:
                with col2:
                    high_latency_periods = suggest_high_latency_periods(df_total_filtered_latency, min_latency, max_latency, top_n=num_high_latency_periods)
                    high_latency_periods = high_latency_periods.sort_values(by='timestamp')
                    st.write(high_latency_periods)
                    if visualize_high_latency and not high_latency_periods.empty:
                        st.subheader("High Latency Analysis Options")
                        interval_options = high_latency_periods['timestamp'].tolist()
                        selected_interval = st.selectbox("Select High Latency Interval", interval_options, key='select_interval')
                        interval_minutes = st.number_input("Select +/- Interval (minutes)", min_value=1, max_value=120, value=10, key='interval_minutes')

                        start_time_str = selected_interval.strftime('%Y-%m-%d %H:%M:%S')
                        selected_interval_tuple = start_time_str

                        df_high_latency = filtered_df[(filtered_df['timestamp'] == selected_interval)]
                        st.write(df_high_latency)

                        start_interval = (pd.to_datetime(start_time_str) - pd.Timedelta(minutes=interval_minutes)).strftime('%Y-%m-%d %H:%M:%S')
                        end_interval = (pd.to_datetime(start_time_str) + pd.Timedelta(minutes=interval_minutes)).strftime('%Y-%m-%d %H:%M:%S')
                        df_interval_latency = filtered_df[(filtered_df['timestamp'] >= start_interval) & (filtered_df['timestamp'] <= end_interval)]

                        df_total_interval_latency = df_interval_latency.groupby('timestamp')['avg'].sum().reset_index()
                        df_total_interval_latency.rename(columns={'avg': 'total_avg_latency'}, inplace=True)

                        with col1:
                            plot_data(
                                x_data=df_total_interval_latency['timestamp'],
                                y_data=df_total_interval_latency['total_avg_latency'],
                                x_label='Timestamp',
                                y_label='Total Average Latency',
                                title='Total Average Latency Over Time'
                            )

                        visualize_high_latency_periods(filtered_df, [selected_interval_tuple])

            if plot_hop:
                with col1:
                    for hop_number in selected_hops:
                        df_hop_latency = filtered_df[filtered_df['hop_number'] == hop_number]
                        df_hop_latency = df_hop_latency.groupby('timestamp')['avg'].mean().reset_index()
                        df_hop_latency.rename(columns={'avg': 'incremental_latency'}, inplace=True)
                        plot_data(
                            x_data=df_hop_latency['timestamp'],
                            y_data=df_hop_latency['incremental_latency'],
                            x_label='Timestamp',
                            y_label='Incremental Latency (ms)',
                            title=f'Incremental Latency for Hop {hop_number} Over Time'
                        )

else:
    st.info("Please upload your traceroute logs or select a folder to begin analysis.")
