import os
import time
import platform
import psutil
import sys
import subprocess
import socket
import speedtest
import shutil
import argparse

LOG_FILE = "network_benchmark_log.txt"
PING_TARGET = "8.8.8.8"  # Google's DNS Server
IPERF_SERVER = "ping.online.net"  # iPerf3 public server (France)
IPERF_PORT = "5200"  # Port for iPerf3

def get_default_interface():
    """Get the default network interface (eth0 if available, otherwise wlan0)"""
    net_ifaces = psutil.net_if_addrs()
    if "eth0" in net_ifaces:
        return "eth0"
    elif "wlan0" in net_ifaces:
        return "wlan0"
    return None  # No valid interface found

def get_system_info():
    """Retrieve system information"""
    info = {
        "CPU": platform.platform(),
        "Architecture": platform.machine(),
        "Cores": psutil.cpu_count(logical=True),
        "Physical Cores": psutil.cpu_count(logical=False),
        "Total Memory (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Python Version": sys.version,
    }
    return info

# ───────────────────────────────────────────────
# 🔹 INTERNET SPEED TESTS (WITH INTERFACE SUPPORT)
# ───────────────────────────────────────────────
def benchmark_download_speed(interface):
    """Measure internet download speed using a specific interface"""
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        st.download()
        speed = st.results.download / (1024 * 1024)  # Convert to Mbps
        return speed, f"{speed:.2f} Mbps ({interface})"
    except Exception as e:
        return None, f"Error: {str(e)}"

def benchmark_upload_speed(interface):
    """Measure internet upload speed using a specific interface"""
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        st.upload()
        speed = st.results.upload / (1024 * 1024)  # Convert to Mbps
        return speed, f"{speed:.2f} Mbps ({interface})"
    except Exception as e:
        return None, f"Error: {str(e)}"

# ───────────────────────────────────────────────
# 🔹 LATENCY & PACKET LOSS TESTS (WITH INTERFACE SUPPORT)
# ───────────────────────────────────────────────
def benchmark_latency(interface):
    """Measure ping latency using a specific interface"""
    try:
        result = subprocess.run(["ping", "-I", interface, "-c", "5", PING_TARGET], capture_output=True, text=True)
        output = result.stdout
        if "rtt min/avg/max/mdev" in output:
            avg_latency = output.split("rtt min/avg/max/mdev = ")[1].split("/")[1]
            return float(avg_latency), f"{avg_latency} ms ({interface})"
        else:
            return None, f"Ping failed on {interface}"
    except Exception as e:
        return None, f"Error: {str(e)}"

def benchmark_packet_loss(interface):
    """Measure packet loss using a specific interface"""
    try:
        result = subprocess.run(["ping", "-I", interface, "-c", "10", PING_TARGET], capture_output=True, text=True)
        output = result.stdout
        if "packet loss" in output:
            loss_percentage = output.split(", ")[2].split("%")[0]
            return float(loss_percentage), f"{loss_percentage} % ({interface})"
        else:
            return None, f"Packet loss data not found ({interface})"
    except Exception as e:
        return None, f"Error: {str(e)}"

# ───────────────────────────────────────────────
# 🔹 NETWORK THROUGHPUT TESTS (iPerf3 - WITH INTERFACE SUPPORT)
# ───────────────────────────────────────────────
def benchmark_bandwidth(interface):
    """Measure network bandwidth using iPerf3 with a specific interface"""
    if not shutil.which("iperf3"):
        return None, "iperf3 not found, please install it"

    try:
        result = subprocess.run(["iperf3", "-c", IPERF_SERVER, "-p", IPERF_PORT, "-B", interface], capture_output=True, text=True)
        output = result.stdout
        if "receiver" in output:
            speed = output.split("receiver")[-1].split()[-2]
            return float(speed), f"iperf3 Bandwidth to {IPERF_SERVER}: {speed} Mbps ({interface})"
        else:
            return None, f"iperf3 test failed on {interface}"
    except Exception as e:
        return None, f"Error: {str(e)}"

# ───────────────────────────────────────────────
# 🔹 DNS RESOLUTION SPEED TEST
# ───────────────────────────────────────────────
def benchmark_dns_resolution():
    """Measure DNS resolution speed"""
    start_time = time.time()
    try:
        socket.gethostbyname("www.google.com")
    except Exception:
        return None, "Failed to resolve"
    end_time = time.time()
    return end_time - start_time, "DNS Resolution Time"

# ───────────────────────────────────────────────
# 🔹 LOGGING & EXECUTION
# ───────────────────────────────────────────────
def log_results(system_info, results):
    """Log benchmark results to a file"""
    with open(LOG_FILE, "a") as log:
        log.write("="*50 + "\n")
        log.write(f"Network Benchmark Run \n")
        log.write("="*50 + "\n")
        for key, value in system_info.items():
            log.write(f"{key}: {value}\n")
        log.write("\nNetwork Benchmark Results:\n")
        for test, (result, params) in results.items():
            log.write(f"{test} ({params}): {result:.2f} sec\n" if isinstance(result, (int, float)) else f"{test} ({params}): {result}\n")
        log.write("\n\n")

def run_network_benchmarks(interface):
    """Run all network benchmarks for the specified interface"""
    system_info = get_system_info()
    
    print(f"Running Network Benchmarks on {interface}...\n")
    results = {
        "Download Speed Test": benchmark_download_speed(interface),
        "Upload Speed Test": benchmark_upload_speed(interface),
        "Network Latency Test": benchmark_latency(interface),
        "Packet Loss Test": benchmark_packet_loss(interface),
        "Bandwidth Test (iperf3)": benchmark_bandwidth(interface),
        "DNS Resolution Speed": benchmark_dns_resolution(),
    }

    # Print results
    for test, (result, params) in results.items():
        print(f"{test} ({params}): {result:.2f} sec" if isinstance(result, (int, float)) else f"{test} ({params}): {result}")
    
    # Log results
    log_results(system_info, results)
    print("\nNetwork benchmark results saved to:", LOG_FILE)

# ───────────────────────────────────────────────
# 🔹 ARGUMENT PARSING FOR NETWORK INTERFACE SELECTION
# ───────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run network benchmarks with a specified network interface.")
    parser.add_argument("--interface", default=get_default_interface(), help="Specify the network interface (e.g., eth0, wlan0). Default is auto-detected.")

    args = parser.parse_args()
    if args.interface is None:
        print("No valid network interface found. Please specify manually.")
    else:
        run_network_benchmarks(args.interface)