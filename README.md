
# ISP Itsonyou Project

## Overview

This project analyzes network performance issues using traceroute logs. The primary goals are to identify periods of high latency, determine the source of slowdowns, and visualize the data.

## Folder Structure

```
isp_itsonyou/
│
├── traceroute_analysis.py        # Main script for analyzing traceroute logs
├── log_import.py                 # Script for importing and parsing logs
├── streamlit_interface.py        # Streamlit-based user interface for the project
├── README.md                     # Project documentation
│
└── traceroute_logs/              # Directory containing traceroute log files
    ├── first_12_hours_logs.zip   # Sample logs for testing
    └── [other log files]         # Additional log files
```

## Goals and Objectives

1. **Identify Periods of High Latency**:
   - Analyze the logs to identify periods when the total latency exceeds normal levels.
   - Specifically, we are interested in identifying times when the total latency exceeds 2000ms, which indicates a significant slowdown.

2. **Identify the Source of Slowdown**:
   - Determine which network hops are contributing most to the latency during these periods.
   - We expect that the slowdown is often caused by one or more of the first 1-5 hops, which are typically within the ISP's network infrastructure.

3. **Visualize the Data**:
   - Create plots to visually represent the average total latency over time.
   - Generate individual hop latency plots to pinpoint where the slowdowns occur within the network path.

**Background:**

- The network connection in question is a 300/10 Mbps connection.
- Intermittent issues have been observed, characterized by periods of very high latency (up to 2000ms) and reduced throughput (below 30 Mbps).

**Logs Description:**

The logs are traceroute outputs saved in text files with timestamps in their filenames. Each log file follows this format:

```
/home/nathanm/traceroute_logs/mtr_20240521195616.txt

Start: 2024-05-21T19:56:16-0500
HOST: nathandebiansecure                      Loss%   Snt   Last   Avg  Best  Wrst StDev
  1.|-- SAX2V1R.lan                              0.0%    60    0.4   0.7   0.3   1.4   0.2
  2.|-- syn-159-111-244-013.inf.spectrum.com     0.0%    60    6.4   6.6   2.4  34.0   6.0
  3.|-- lag-56.wxhctxbn01h.netops.charter.com    0.0%    60    6.2   6.7   4.0  15.8   2.0
  4.|-- lag-38.rcr01ftwptxzp.netops.charter.com  0.0%    60    7.8   8.8   6.3  12.3   1.5
  5.|-- lag-806.bbr01dllstx.netops.charter.com   0.0%    60   10.7  12.3   9.4  14.3   1.5
  6.|-- lag-801.prr01dllstx.netops.charter.com   0.0%    60   10.6  15.1  10.6 132.0  15.4
  7.|-- 72.14.197.124                            0.0%    60   14.9  13.5  10.9  16.1   1.4
  8.|-- 108.170.225.147                          0.0%    60   13.5  13.2  10.7  16.0   1.4
  9.|-- 142.251.60.47                            0.0%    60   11.5  12.3  10.2  14.7   1.3
 10.|-- dns.google                               0.0%    60   10.2  13.2  10.1  52.6   5.3
```
## Dependencies

- Python 3.x
- Pandas
- Matplotlib
- Streamlit

## NumPy-Style Docstrings

The `traceroute_analysis.py` and `log_import.py` scripts have been updated to include NumPy-style docstrings for better documentation and clarity.

### traceroute_analysis.py
- **Functions:**
  - `suggest_high_latency_periods`
  - `visualize_high_latency_periods`
  - `plot_total_avg_latency_over_time`
  - `main`

### log_import.py
- **Functions:**
  - `parse_traceroute_log`
  - `extract_logs`

## Metrics to Implement:

1. **Hop Latency Histograms**:
   - Visualize the distribution of latencies for individual hops.

2. **Packet Loss Analysis**:
   - Analyze and visualize packet loss percentages for each hop.

3. **Latency Percentiles**:
   - Calculate and visualize latency percentiles (e.g., 95th, 99th).

## LLM Opening Prompt

(To be used in event a new conversation needs to be started, i.e., all context is lost)

Assist with software development. This project analyzes network performance issues using traceroute logs. The primary goals are to identify periods of high latency, determine the source of slowdowns, and visualize the data. You should write code to execute in your environment with my logs as test inputs. Later I will execute locally on my Debian KDE system. As it sits now, I am executing via Windows 11 and VS Code. We don't want to do too many steps in a single turn. Let's keep it simple.

Begin by extracting the contents of the zip file and reading in the entirety of README.md file to understand the project.
Development is now being conducted alongside your environment in VS Studio Code on a Windows 11 system.

Do not suggest executing code locally, due to errors in your environment.
Rather, troubleshoot why the errors in your environment are happening via breaking the process into smaller steps, using print statements, etc.
We will probably go for a complete reset of the coding environment and/or a new conversation before resorting to local execution on my end.

With this opening prompt a zip of the current project status has been attached.

1. Extract the project without adding anything to the name, i.e., no _unzipped or anything. Just use the folder isp_itsonyou (via extraction) as the root folder for the project.
2. Get the README.md file and read it to understand the project.
   - When reading in files, such as README.md, it is not necessary to redisplay them for me in a human readable format. Single line read ins which work for you are all that is needed, in most cases. I don't want to use up too much context window re-displaying text which has already been read in.
   - When listing the content of log folders after extraction, only list the first 5 or so files. This is to save context window space.
3. Sample logs can be found under isp_itsonyou\
4. Run a test on a portion of the logs to see if the code is working as expected up to it's last documented functional state.
