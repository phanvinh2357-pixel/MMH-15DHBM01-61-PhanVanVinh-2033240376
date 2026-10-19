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
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm benchmark_scenario_d()")


def benchmark_scenario_e() -> Dict[str, List[float]]:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm benchmark_scenario_e()")


def export_results_to_csv(raw_data: Dict[str, List[float]], summary_data: List[Dict[str, float]]) -> None:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm export_results_to_csv()")


def run_all_benchmarks() -> None:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm run_all_benchmarks()")


if __name__ == "__main__":
    print(f"=== MÔI TRƯỜNG ĐO: {platform.system()} {platform.release()} | CPU: {platform.processor()} ===")
    run_all_benchmarks()