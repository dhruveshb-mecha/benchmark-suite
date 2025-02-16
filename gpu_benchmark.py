import time
import numpy as np
import pyopencl as cl
import platform
import psutil
import sys

LOG_FILE = "benchmark_gpu_log.txt"

def get_system_info():
    """Retrieve system information"""
    info = {
        "CPU": platform.processor(),
        "Architecture": platform.machine(),
        "Cores": psutil.cpu_count(logical=True),
        "Physical Cores": psutil.cpu_count(logical=False),
        "Total Memory (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Python Version": sys.version,
        "OpenCL Version": "Available" if pyopencl.get_platforms() else "Not Available",
    }
    return info

# ───────────────────────────────────────────────
# 🔹 GPU BENCHMARKS FOR ARM
# ───────────────────────────────────────────────
def benchmark_opencl_vector_addition():
    """Measure OpenCL computation on the Raspberry Pi GPU"""
    platform = cl.get_platforms()[0]  # Use the first platform (Raspberry Pi's OpenCL platform)
    device = platform.get_devices()[0]  # Use the first device (Raspberry Pi's GPU)

    context = cl.Context([device])
    queue = cl.CommandQueue(context, device)

    # OpenCL kernel for vector addition
    program_src = """
    __kernel void vec_add(__global const float* A, __global const float* B, __global float* C, const unsigned int n) {
        int i = get_global_id(0);
        if (i < n) {
            C[i] = A[i] + B[i];
        }
    }
    """
    program = cl.Program(context, program_src).build()

    # Prepare input data
    n = 1024 * 1024  # Length of the vectors (1M elements)
    A = np.random.rand(n).astype(np.float32)
    B = np.random.rand(n).astype(np.float32)
    C = np.empty_like(A)

    # Create OpenCL buffers
    buffer_A = cl.Buffer(context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=A)
    buffer_B = cl.Buffer(context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=B)
    buffer_C = cl.Buffer(context, cl.mem_flags.WRITE_ONLY, C.nbytes)

    # Run OpenCL kernel
    start_time = time.time()
    program.vec_add(queue, A.shape, None, buffer_A, buffer_B, buffer_C, np.uint32(n))
    cl.enqueue_copy(queue, C, buffer_C).wait()
    end_time = time.time()

    return end_time - start_time, f"OpenCL Vector Addition ({n} elements)"

def benchmark_matrix_multiplication():
    """Measure time for matrix multiplication using the CPU (can modify for OpenCL)"""
    A = np.random.rand(1024, 1024).astype(np.float32)
    B = np.random.rand(1024, 1024).astype(np.float32)

    start_time = time.time()
    result = np.dot(A, B)  # Using CPU for matrix multiplication
    end_time = time.time()

    return end_time - start_time, "Matrix Multiplication (CPU)"

def benchmark_cpu_computation():
    """Measure simple CPU computation time (for comparison)"""
    n = 10**7
    start_time = time.time()
    sum_result = sum(i for i in range(n))
    end_time = time.time()
    return end_time - start_time, f"CPU Computation (sum 0 to {n-1})"

# ───────────────────────────────────────────────
# 🔹 LOGGING & EXECUTION
# ───────────────────────────────────────────────
def log_results(system_info, results):
    """Log benchmark results to a file"""
    with open(LOG_FILE, "a") as log:
        log.write("="*50 + "\n")
        log.write(f"GPU Benchmark Run - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write("="*50 + "\n")
        for key, value in system_info.items():
            log.write(f"{key}: {value}\n")
        log.write("\nGPU Benchmark Results:\n")
        for test, (result, params) in results.items():
            log.write(f"{test} ({params}): {result:.2f} sec\n")
        log.write("\n\n")

def run_gpu_benchmarks():
    """Run all GPU benchmarks and log results"""
    system_info = get_system_info()
    
    print("Running GPU Benchmarks...\n")
    results = {
        "OpenCL Vector Addition": benchmark_opencl_vector_addition(),
        "Matrix Multiplication (CPU)": benchmark_matrix_multiplication(),
        "CPU Computation": benchmark_cpu_computation(),
    }

    # Print results
    for test, (result, params) in results.items():
        print(f"{test} ({params}): {result:.2f} sec")
    
    # Log results
    log_results(system_info, results)
    print("\nGPU benchmark results saved to:", LOG_FILE)

if __name__ == "__main__":
    run_gpu_benchmarks()