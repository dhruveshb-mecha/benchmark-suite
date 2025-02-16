import time
import numpy as np
import platform
import psutil
import sys
import os

LOG_FILE = "benchmark_memory_log.txt"

def get_system_info():
    """Retrieve system information"""
    mem = psutil.virtual_memory()

    info = {
        "CPU": platform.platform(),
        "Architecture": platform.machine(),
        "Cores": psutil.cpu_count(logical=True),
        "Physical Cores": psutil.cpu_count(logical=False),
        "Total Memory (GB)": round(mem.total / (1024 ** 3), 2),
        "Available Memory (GB)": round(mem.available / (1024 ** 3), 2),
        "Used Memory (GB)": round(mem.used / (1024 ** 3), 2),
        "Memory Usage (%)": mem.percent,
        "Swap Total (GB)": round(psutil.swap_memory().total / (1024 ** 3), 2),
        "Swap Used (GB)": round(psutil.swap_memory().used / (1024 ** 3), 2),
        "Python Version": sys.version,
    }
    return info

# ───────────────────────────────────────────────
# 🔹 MEMORY TESTS
# ───────────────────────────────────────────────
def benchmark_memory_read_write(size_mb=500):
    """Write and read back a block of memory"""
    size_bytes = size_mb * 1024 * 1024
    data = bytearray(size_bytes)  # Allocate memory
    start_time = time.time()
    
    for i in range(size_bytes):
        data[i] = i % 256  # Write operation
    
    read_data = sum(data)  # Read operation
    end_time = time.time()
    return end_time - start_time, f"size={size_mb}MB"

def benchmark_memory_bandwidth(size_mb=500):
    """Measure memory bandwidth by copying large arrays"""
    size_elements = (size_mb * 1024 * 1024) // 8  # Convert MB to 64-bit floats
    A = np.ones(size_elements, dtype=np.float64)
    start_time = time.time()
    B = np.copy(A)  # Copy operation
    end_time = time.time()
    return end_time - start_time, f"size={size_mb}MB"

def benchmark_memory_allocation(size_mb=1000):
    """Allocate and free large memory blocks"""
    size_bytes = size_mb * 1024 * 1024
    start_time = time.time()
    block = bytearray(size_bytes)  # Allocate
    del block  # Deallocate
    end_time = time.time()
    return end_time - start_time, f"size={size_mb}MB"

def benchmark_page_faults(iterations=1000000):
    """Simulate page faults by accessing scattered memory locations"""
    arr = np.zeros(iterations, dtype=np.int32)
    start_time = time.time()
    
    for _ in range(iterations):
        index = np.random.randint(0, iterations)
        arr[index] += 1
    
    end_time = time.time()
    return end_time - start_time, f"iterations={iterations}"

def benchmark_random_access_latency(iterations=100000):
    """Measure memory latency for random access"""
    size = iterations
    arr = np.zeros(size, dtype=np.int32)
    indices = np.random.randint(0, size, size)
    
    start_time = time.time()
    for i in indices:
        arr[i] += 1
    end_time = time.time()
    
    return end_time - start_time, f"iterations={iterations}"

# ───────────────────────────────────────────────
# 🔹 LOGGING & EXECUTION
# ───────────────────────────────────────────────
def log_results(system_info, results):
    """Log benchmark results to a file"""
    with open(LOG_FILE, "a") as log:
        log.write("="*50 + "\n")
        log.write(f"Memory Benchmark Run \n")
        log.write("="*50 + "\n")
        for key, value in system_info.items():
            log.write(f"{key}: {value}\n")
        log.write("\nMemory Benchmark Results:\n")
        for test, (result, params) in results.items():
            log.write(f"{test} ({params}): {result:.2f} sec\n")
        log.write("\n\n")

def run_memory_benchmarks():
    """Run all memory benchmarks and log results"""
    system_info = get_system_info()
    
    print("Running Memory Benchmarks...\n")
    results = {
        "Memory Read/Write Speed": benchmark_memory_read_write(),
        "Memory Bandwidth Test": benchmark_memory_bandwidth(),
        "Memory Allocation Stress Test": benchmark_memory_allocation(),
        "Page Faults Test": benchmark_page_faults(),
        "Random Access Latency": benchmark_random_access_latency(),
    }
    
    # Print results
    for test, (result, params) in results.items():
        print(f"{test} ({params}): {result:.2f} sec")
    
    # Log results
    log_results(system_info, results)
    print("\nMemory benchmark results saved to:", LOG_FILE)

if __name__ == "__main__":
    run_memory_benchmarks()