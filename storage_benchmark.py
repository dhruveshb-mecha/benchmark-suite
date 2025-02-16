import os
import time
import platform
import psutil
import sys
import random

LOG_FILE = "benchmark_storage_log.txt"
TEST_FILE = "test_benchmark.dat"
NUM_FILES = 1000  # For filesystem latency test
FILE_SIZE_MB = 500  # Size for sequential read/write
RANDOM_BLOCK_SIZE = 4096  # Block size for random read/write

def get_system_info():
    """Retrieve system information"""
    info = {
        "CPU": platform.platform(),
        "Architecture": platform.machine(),
        "Cores": psutil.cpu_count(logical=True),
        "Physical Cores": psutil.cpu_count(logical=False),
        "Total Memory (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Disk Type": psutil.disk_partitions()[0].fstype,
        "Total Disk Space (GB)": round(psutil.disk_usage('/').total / (1024 ** 3), 2),
        "Python Version": sys.version,
    }
    return info

# ───────────────────────────────────────────────
# 🔹 STORAGE TESTS
# ───────────────────────────────────────────────
def benchmark_sequential_write(size_mb=500):
    """Write a large file sequentially"""
    size_bytes = size_mb * 1024 * 1024
    start_time = time.time()
    with open(TEST_FILE, "wb") as f:
        f.write(os.urandom(size_bytes))
    end_time = time.time()
    return end_time - start_time, f"size={size_mb}MB"

def benchmark_sequential_read():
    """Read a large file sequentially"""
    if not os.path.exists(TEST_FILE):
        return None, "File not found"
    
    start_time = time.time()
    with open(TEST_FILE, "rb") as f:
        while f.read(1024 * 1024):  # Read in 1MB chunks
            pass
    end_time = time.time()
    return end_time - start_time, f"file={TEST_FILE}"

def benchmark_random_read_write(block_size=4096, iterations=100000):
    """Perform random reads and writes"""
    size_bytes = block_size * iterations
    with open(TEST_FILE, "wb") as f:
        f.write(os.urandom(size_bytes))

    start_time = time.time()
    with open(TEST_FILE, "r+b") as f:
        for _ in range(iterations):
            f.seek(random.randint(0, size_bytes - block_size))
            f.write(os.urandom(block_size))
    end_time = time.time()
    return end_time - start_time, f"block_size={block_size}B, iterations={iterations}"

def benchmark_file_iops(num_operations=10000):
    """Measure Input/Output Operations Per Second (IOPS)"""
    start_time = time.time()
    for i in range(num_operations):
        with open(f"iops_test_{i}.tmp", "w") as f:
            f.write("test")
        os.remove(f"iops_test_{i}.tmp")
    end_time = time.time()
    return end_time - start_time, f"operations={num_operations}"

def benchmark_file_deletion(num_files=1000):
    """Create and delete many files to test deletion speed"""
    os.makedirs("test_delete", exist_ok=True)
    for i in range(num_files):
        with open(f"test_delete/file_{i}.tmp", "w") as f:
            f.write("test")
    
    start_time = time.time()
    for i in range(num_files):
        os.remove(f"test_delete/file_{i}.tmp")
    os.rmdir("test_delete")
    end_time = time.time()
    return end_time - start_time, f"num_files={num_files}"

def benchmark_filesystem_latency(num_files=1000):
    """Measure latency of creating, accessing, and deleting small files"""
    start_time = time.time()
    os.makedirs("latency_test", exist_ok=True)
    
    for i in range(num_files):
        with open(f"latency_test/file_{i}.tmp", "w") as f:
            f.write("test")
    
    for i in range(num_files):
        with open(f"latency_test/file_{i}.tmp", "r") as f:
            f.read()
    
    for i in range(num_files):
        os.remove(f"latency_test/file_{i}.tmp")
    
    os.rmdir("latency_test")
    end_time = time.time()
    return end_time - start_time, f"num_files={num_files}"

# ───────────────────────────────────────────────
# 🔹 LOGGING & EXECUTION
# ───────────────────────────────────────────────
def log_results(system_info, results):
    """Log benchmark results to a file"""
    with open(LOG_FILE, "a") as log:
        log.write("="*50 + "\n")
        log.write(f"Storage Benchmark Run \n")
        log.write("="*50 + "\n")
        for key, value in system_info.items():
            log.write(f"{key}: {value}\n")
        log.write("\nStorage Benchmark Results:\n")
        for test, (result, params) in results.items():
            log.write(f"{test} ({params}): {result:.2f} sec\n")
        log.write("\n\n")

def run_storage_benchmarks():
    """Run all storage benchmarks and log results"""
    system_info = get_system_info()
    
    print("Running Storage Benchmarks...\n")
    results = {
        "Sequential Write Speed": benchmark_sequential_write(),
        "Sequential Read Speed": benchmark_sequential_read(),
        "Random Read/Write Speed": benchmark_random_read_write(),
        "File IOPS Test": benchmark_file_iops(),
        "File Deletion Performance": benchmark_file_deletion(),
        "Filesystem Latency Test": benchmark_filesystem_latency(),
    }
    
    # Print results
    for test, (result, params) in results.items():
        print(f"{test} ({params}): {result:.2f} sec")
    
    # Log results
    log_results(system_info, results)
    print("\nStorage benchmark results saved to:", LOG_FILE)

if __name__ == "__main__":
    run_storage_benchmarks()