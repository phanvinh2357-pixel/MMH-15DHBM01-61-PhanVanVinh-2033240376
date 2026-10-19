import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "06_ExperimentalResults")
CSV_PATH = os.path.join(RESULTS_DIR, "benchmark_results.csv")
OUTPUT_CHART_DIR = os.path.join(RESULTS_DIR, "charts")


def plot_boxplot_hkdf_latency() -> None:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm plot_boxplot_hkdf_latency()")


def plot_barchart_scenarios() -> None:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm plot_barchart_scenarios()")


def plot_multisession_throughput() -> None:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm plot_multisession_throughput()")


def generate_all_charts() -> None:
    raise NotImplementedError("Lương Gia Huy cần hiện thực hàm generate_all_charts()")


if __name__ == "__main__":
    os.makedirs(OUTPUT_CHART_DIR, exist_ok=True)
    generate_all_charts()