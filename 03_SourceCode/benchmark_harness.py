import time
import os
import csv
import statistics
import platform
from typing import Dict, List, Tuple

ITERATIONS: int = 50

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "06_ExperimentalResults")
RAW_CSV_PATH = os.path.join(RESULTS_DIR, "benchmark_results.csv")
SUMMARY_CSV_PATH = os.path.join(RESULTS_DIR, "statistics_summary.csv")


def benchmark_scenario_a() -> Dict[str, List[float]]:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm benchmark_scenario_a()")


def benchmark_scenario_b() -> Dict[str, List[float]]:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm benchmark_scenario_b()")


def benchmark_scenario_c() -> Dict[str, Dict[str, float]]:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm benchmark_scenario_c()")


def benchmark_scenario_d() -> Dict[str, List[float]]:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "03_SourceCode"))
    from crypto_engine import hkdf_extract

    print("[*] Đang thực thi Kịch bản D: Đo độ trễ HKDF-Extract theo kích thước Salt...")
    salt_configs = {
        "Salt_0B_Rong": b"",
        "Salt_32B_Chuan": os.urandom(32),
        "Salt_64B_KhoiHash": os.urandom(64),
        "Salt_256B_MoRong": os.urandom(256)
    }
    ikm = os.urandom(32)
    results: Dict[str, List[float]] = {}

    for name, salt_val in salt_configs.items():
        latencies = []
        for _ in range(10):
            _ = hkdf_extract(salt_val, ikm)
        
        for _ in range(ITERATIONS):
            start = time.perf_counter_ns()
            _ = hkdf_extract(salt_val, ikm)
            end = time.perf_counter_ns()
            latencies.append((end - start) / 1000.0)
        results[name] = latencies

    raw_path = os.path.join(RESULTS_DIR, "scenario_d_raw.csv")
    with open(raw_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Lan_Lap"] + list(salt_configs.keys()))
        for i in range(ITERATIONS):
            row = [i + 1] + [results[k][i] for k in salt_configs.keys()]
            writer.writerow(row)
    print(f"[+] Đã xuất dữ liệu thô Kịch bản D vào: {raw_path}")
    return results


def benchmark_scenario_e() -> Dict[str, List[float]]:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm benchmark_scenario_e()")


def export_results_to_csv(raw_data: Dict[str, List[float]], summary_data: List[Dict[str, float]]) -> None:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm export_results_to_csv()")


def run_all_benchmarks() -> None:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm run_all_benchmarks()")


if __name__ == "__main__":
    print(f"=== MÔI TRƯỜNG ĐO: {platform.system()} {platform.release()} | CPU: {platform.processor()} ===")
    run_all_benchmarks()