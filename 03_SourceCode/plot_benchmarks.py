import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "06_ExperimentalResults")
CSV_PATH = os.path.join(RESULTS_DIR, "benchmark_results.csv")
OUTPUT_CHART_DIR = os.path.join(RESULTS_DIR, "charts")


def _load() -> pd.DataFrame:
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError("Chưa có benchmark_results.csv, hãy chạy benchmark_harness.py trước.")
    return pd.read_csv(CSV_PATH)


def _save(name: str) -> None:
    os.makedirs(OUTPUT_CHART_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_CHART_DIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"[+] Đã lưu biểu đồ: {path}")


def plot_boxplot_hkdf_latency() -> None:
    df = _load()
    df = df[df["scenario"].str.match(r"^[AB]_")]
    plt.figure(figsize=(11, 5))
    sns.boxplot(data=df, x="scenario", y="time_ms")
    plt.xticks(rotation=45, ha="right")
    plt.title("Độ trễ HKDF-Expand (kịch bản A và B)")
    plt.xlabel("Cấu hình")
    plt.ylabel("Thời gian (ms)")
    _save("boxplot_hkdf_latency.png")


def plot_barchart_scenarios() -> None:
    df = pd.read_csv(os.path.join(RESULTS_DIR, "statistics_summary.csv"))
    plt.figure(figsize=(12, 5))
    plt.bar(df["scenario"], df["mean_ms"], yerr=df["std_ms"], capsize=3)
    plt.xticks(rotation=60, ha="right")
    plt.title("Độ trễ trung bình theo kịch bản (mean ± std)")
    plt.ylabel("Thời gian (ms)")
    _save("barchart_scenarios.png")


def plot_multisession_throughput() -> None:
    df = _load()
    e = df[df["scenario"] == "E_derive_6_keys"].copy()
    e["throughput"] = 1000.0 / e["time_ms"]  # phiên/giây
    mean_tp = e["throughput"].mean()
    plt.figure(figsize=(8, 4.5))
    plt.plot(e["run"], e["throughput"], marker="o", markersize=3)
    plt.axhline(mean_tp, linestyle="--", label=f"Trung bình: {mean_tp:.0f} phiên/s")
    plt.title("Thông lượng tạo bộ khóa phiên theo lần chạy")
    plt.xlabel("Lần chạy")
    plt.ylabel("Thông lượng (phiên/giây)")
    plt.legend()
    _save("multisession_throughput.png")


def generate_all_charts() -> None:
    plot_boxplot_hkdf_latency()
    plot_barchart_scenarios()
    plot_multisession_throughput()


if __name__ == "__main__":
    os.makedirs(OUTPUT_CHART_DIR, exist_ok=True)
    generate_all_charts()