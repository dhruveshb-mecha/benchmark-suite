import time
import platform
import psutil
import sys
import subprocess
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

LOG_FILE = "tensorflow_benchmark_log.txt"

def get_system_info():
    """Retrieve system information"""
    info = {
        "CPU": platform.platform(),
        "Architecture": platform.machine(),
        "Cores": psutil.cpu_count(logical=True),
        "Physical Cores": psutil.cpu_count(logical=False),
        "Total Memory (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Python Version": sys.version,
        "TensorFlow Version": tf.__version__,
        "GPU Available": "Yes" if tf.config.list_physical_devices('GPU') else "No"
    }
    return info

# ───────────────────────────────────────────────
# 🔹 TENSORFLOW INFERENCE BENCHMARK
# ───────────────────────────────────────────────
def benchmark_inference():
    """Measure TensorFlow inference time"""
    # Simple model for inference
    model = models.Sequential([
        layers.Dense(128, activation='relu', input_shape=(1024,)),
        layers.Dense(10, activation='softmax')
    ])
    
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Random data to simulate a real-world scenario
    data = np.random.random((1000, 1024))
    labels = np.random.randint(0, 10, size=(1000,))

    start_time = time.time()
    model.fit(data, labels, epochs=1, batch_size=32, verbose=0)
    end_time = time.time()

    return end_time - start_time, "TensorFlow Inference (1 Epoch)"

# ───────────────────────────────────────────────
# 🔹 TENSORFLOW TRAINING BENCHMARK
# ───────────────────────────────────────────────
def benchmark_training():
    """Measure TensorFlow training time"""
    # Simple model for training
    model = models.Sequential([
        layers.Dense(128, activation='relu', input_shape=(1024,)),
        layers.Dense(10, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Random data to simulate training
    data = np.random.random((1000, 1024))
    labels = np.random.randint(0, 10, size=(1000,))

    start_time = time.time()
    model.fit(data, labels, epochs=5, batch_size=32, verbose=0)  # 5 epochs for training benchmark
    end_time = time.time()

    return end_time - start_time, "TensorFlow Training (5 Epochs)"

# ───────────────────────────────────────────────
# 🔹 LOGGING & EXECUTION
# ───────────────────────────────────────────────
def log_results(system_info, results):
    """Log benchmark results to a file"""
    with open(LOG_FILE, "a") as log:
        log.write("="*50 + "\n")
        log.write(f"TensorFlow Benchmark Run - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write("="*50 + "\n")
        for key, value in system_info.items():
            log.write(f"{key}: {value}\n")
        log.write("\nTensorFlow Benchmark Results:\n")
        for test, (result, params) in results.items():
            log.write(f"{test} ({params}): {result:.2f} sec\n")
        log.write("\n\n")

def run_tensorflow_benchmarks():
    """Run TensorFlow benchmarks and log results"""
    system_info = get_system_info()
    
    print("Running TensorFlow Benchmarks...\n")
    results = {
        "TensorFlow Inference Benchmark": benchmark_inference(),
        "TensorFlow Training Benchmark": benchmark_training(),
    }

    # Print results
    for test, (result, params) in results.items():
        print(f"{test} ({params}): {result:.2f} sec")
    
    # Log results
    log_results(system_info, results)
    print("\nTensorFlow benchmark results saved to:", LOG_FILE)

if __name__ == "__main__":
    run_tensorflow_benchmarks()