import time
import hashlib
import numpy as np
from Crypto.Cipher import Blowfish, AES
import zlib
import os
import platform
import psutil
import sys
import threading

LOG_FILE = "benchmark_log.txt"

def get_system_info():
    """Retrieve system information"""
    info = {
        "CPU": platform.platform(),
        "Architecture": platform.machine(),
        "Cores": psutil.cpu_count(logical=True),
        "Physical Cores": psutil.cpu_count(logical=False),
        "Python Version": sys.version,
    }
    return info

# ───────────────────────────────────────────────
# 🔹 PRIME NUMBER TESTS
# ───────────────────────────────────────────────
def benchmark_prime_numbers(n=50000):
    """Find prime numbers up to n using brute-force method"""
    start_time = time.time()
    primes = []
    for num in range(2, n):
        is_prime = all(num % i != 0 for i in range(2, int(num**0.5) + 1))
        if is_prime:
            primes.append(num)
    end_time = time.time()
    return end_time - start_time, f"n={n}"

def benchmark_sieve_of_eratosthenes(n=50000):
    """Find prime numbers up to n using Sieve of Eratosthenes"""
    start_time = time.time()
    primes = [True] * (n + 1)
    p = 2
    while (p * p <= n):
        if primes[p]:
            for i in range(p * p, n + 1, p):
                primes[i] = False
        p += 1
    prime_numbers = [p for p in range(2, n) if primes[p]]
    end_time = time.time()
    return end_time - start_time, f"n={n}"

# ───────────────────────────────────────────────
# 🔹 CPU-INTENSIVE ALGORITHMS
# ───────────────────────────────────────────────
def benchmark_sha256(iterations=100000):
    """Compute SHA256 hash multiple times"""
    start_time = time.time()
    for _ in range(iterations):
        hashlib.sha256(b"benchmark").hexdigest()
    end_time = time.time()
    return end_time - start_time, f"iterations={iterations}"

def benchmark_aes_encryption(iterations=100000):
    """Encrypt data using AES multiple times"""
    start_time = time.time()
    key = os.urandom(16)
    cipher = AES.new(key, AES.MODE_ECB)
    data = os.urandom(16)
    for _ in range(iterations):
        cipher.encrypt(data)
    end_time = time.time()
    return end_time - start_time, f"iterations={iterations}"

def benchmark_gzip_compression(size=5000000):
    """Compress a block of data using GZIP"""
    start_time = time.time()
    data = os.urandom(size)
    zlib.compress(data)
    end_time = time.time()
    return end_time - start_time, f"size={size} bytes"

# ───────────────────────────────────────────────
# 🔹 NUMERIC & MULTI-THREADED TESTS
# ───────────────────────────────────────────────
def benchmark_numpy_operations(size=500):
    """Perform NumPy matrix multiplication"""
    start_time = time.time()
    A = np.random.rand(size, size)
    B = np.random.rand(size, size)
    np.dot(A, B)
    end_time = time.time()
    return end_time - start_time, f"matrix_size={size}x{size}"

def benchmark_sorting(n=1000000):
    """Sort a large list of random numbers"""
    data = np.random.rand(n)
    start_time = time.time()
    sorted_data = np.sort(data)
    end_time = time.time()
    return end_time - start_time, f"n={n}"

def benchmark_multi_threaded_prime(n=10000, threads=4):
    """Multi-threaded prime calculation"""

    def find_primes(start, end, primes_list):
        for num in range(start, end):
            if all(num % i != 0 for i in range(2, int(num**0.5) + 1)):
                primes_list.append(num)

    start_time = time.time()
    threads_list = []
    primes_list = []
    step = n // threads

    for i in range(threads):
        t = threading.Thread(target=find_primes, args=(i * step, (i + 1) * step, primes_list))
        threads_list.append(t)
        t.start()

    for t in threads_list:
        t.join()

    end_time = time.time()
    return end_time - start_time, f"n={n}, threads={threads}"

# ───────────────────────────────────────────────
# 🔹 LOGGING & EXECUTION
# ───────────────────────────────────────────────
def log_results(system_info, results):
    """Log benchmark results to a file"""
    with open(LOG_FILE, "a") as log:
        log.write("="*50 + "\n")
        log.write(f"CPU Benchmark Run \n")
        log.write("="*50 + "\n")
        for key, value in system_info.items():
            log.write(f"{key}: {value}\n")
        log.write("\nBenchmark Results:\n")
        for test, (result, params) in results.items():
            log.write(f"{test} ({params}): {result:.2f} sec\n")
        log.write("\n\n")

def run_benchmarks():
    """Run all benchmarks and log results"""
    system_info = get_system_info()
    
    print("Running CPU Benchmarks...\n")
    results = {
        "Prime Number Calculation (Brute-Force)": benchmark_prime_numbers(),
        "Prime Number Calculation (Sieve of Eratosthenes)": benchmark_sieve_of_eratosthenes(),
        "SHA256 Hashing": benchmark_sha256(),
        "AES Encryption": benchmark_aes_encryption(),
        "GZIP Compression": benchmark_gzip_compression(),
        "NumPy Matrix Multiplication": benchmark_numpy_operations(),
        "Sorting Algorithm": benchmark_sorting(),
        "Multi-threaded Prime Calculation": benchmark_multi_threaded_prime(),
    }
    
    # Print results
    for test, (result, params) in results.items():
        print(f"{test} ({params}): {result:.2f} sec")
    
    # Log results
    log_results(system_info, results)
    print("\nBenchmark results saved to:", LOG_FILE)

if __name__ == "__main__":
    run_benchmarks()