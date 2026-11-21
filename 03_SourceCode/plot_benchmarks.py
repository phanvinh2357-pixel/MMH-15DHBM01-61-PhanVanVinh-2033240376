import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "06_ExperimentalResults"))
CSV_PATH = os.path.join(RESULTS_DIR, "benchmark_results.csv")
OUTPUT_CHART_DIR = os.path.join(RESULTS_DIR, "charts")

# Cấu hình giao diện biểu đồ chuẩn báo cáo khoa học
sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False


def _load_benchmark_df() -> pd.DataFrame:
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"Không tìm thấy tệp dữ liệu: {CSV_PATH}. "
            "Vui lòng chạy 'python 03_SourceCode/benchmark_harness.py' trước."
        )
    return pd.read_csv(CSV_PATH)


def plot_boxplot_hkdf_latency() -> None:
    df = _load_benchmark_df()
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # --- Biểu đồ trái: Kịch bản D (Độ trễ HKDF-Extract theo kích thước Salt) ---
    salt_cols = {
        "D_Salt_0B_Rong_us": "0B (Rỗng)",
        "D_Salt_32B_Chuan_us": "32B (Chuẩn)",
        "D_Salt_64B_KhoiHash_us": "64B (Khối Hash)",
        "D_Salt_256B_MoRong_us": "256B (Mở rộng)",
    }
    df_salt = df[list(salt_cols.keys())].rename(columns=salt_cols).melt(
        var_name="Kich_Thuoc_Salt", value_name="Do_Tre_us"
    )
    sns.boxplot(
        data=df_salt,
        x="Kich_Thuoc_Salt",
        y="Do_Tre_us",
        hue="Kich_Thuoc_Salt",
        palette="Blues",
        legend=False,
        ax=axes[0],
        width=0.5,
    )
    axes[0].set_title("Kịch bản D: Phân bố độ trễ HKDF-Extract theo kích thước Salt", fontweight="bold")
    axes[0].set_xlabel("Cấu hình Salt đầu vào")
    axes[0].set_ylabel("Độ trễ thực thi (µs)")

    # --- Biểu đồ phải: Kịch bản B (Độ trễ HKDF-Expand theo độ dài L) ---
    expand_cols = {
        "B_Expand_16B_us": "16B",
        "B_Expand_32B_us": "32B",
        "B_Expand_64B_us": "64B",
        "B_Expand_256B_us": "256B",
        "B_Expand_1024B_us": "1KB",
        "B_Expand_4096B_us": "4KB",
        "B_Expand_8160B_us": "8160B\n(Max)",
    }
    df_expand = df[list(expand_cols.keys())].rename(columns=expand_cols).melt(
        var_name="Do_Dai_L", value_name="Do_Tre_us"
    )
    sns.boxplot(
        data=df_expand,
        x="Do_Dai_L",
        y="Do_Tre_us",
        hue="Do_Dai_L",
        palette="Greens",
        legend=False,
        ax=axes[1],
        width=0.55,
    )
    axes[1].set_title("Kịch bản B: Độ trễ HKDF-Expand theo độ dài khóa đầu ra L", fontweight="bold")
    axes[1].set_xlabel("Độ dài vật liệu khóa đầu ra (Bytes)")
    axes[1].set_ylabel("Độ trễ thực thi (µs)")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_CHART_DIR, "fig1_hkdf_latency_boxplot.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Đã xuất biểu đồ 1: {out_path}")


def plot_barchart_scenarios() -> None:
    df = _load_benchmark_df()
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # --- Biểu đồ trái: Kịch bản A (Phân rã chi phí bắt tay ECDH + HKDF) ---
    handshake_cols = {
        "A_ECDH_KeyGen_us": "ECDH\nKeyGen",
        "A_ECDH_SharedSecret_us": "ECDH\nExchange",
        "A_HKDF_Extract_us": "HKDF\nExtract",
        "A_HKDF_Expand_5Keys_us": "HKDF Expand\n(5 Khóa)",
        "A_Full_Handshake_us": "Tổng Bắt Tay\nToàn Trình",
    }
    means_a = [df[c].mean() for c in handshake_cols.keys()]
    stds_a = [df[c].std() for c in handshake_cols.keys()]
    labels_a = list(handshake_cols.values())

    bars_a = axes[0].bar(
        labels_a,
        means_a,
        yerr=stds_a,
        capsize=5,
        color=["#4C72B0", "#55A868", "#C44E52", "#8172B3", "#CCB974"],
        edgecolor="black",
        alpha=0.9,
    )
    axes[0].set_title("Kịch bản A: Phân rã thời gian thiết lập phiên (Mean ± SD)", fontweight="bold")
    axes[0].set_ylabel("Thời gian trung bình (µs)")
    for bar, mean_val in zip(bars_a, means_a):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + max(stds_a) * 0.15,
            f"{mean_val:.1f} µs",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    # --- Biểu đồ phải: Kịch bản E (Đối chứng Phân tách miền vs Single-Shot & Zeroize) ---
    domain_cols = {
        "E_MultiExpand_DomainSep_us": "Multi-Expand\n(5 Miền Độc Lập)",
        "E_SingleShot_160B_us": "Single-Shot\n(160B Gộp)",
        "E_Zeroize_Memory_us": "Zeroize RAM\n(Xóa 5 Khóa)",
    }
    means_e = [df[c].mean() for c in domain_cols.keys()]
    stds_e = [df[c].std() for c in domain_cols.keys()]
    labels_e = list(domain_cols.values())

    bars_e = axes[1].bar(
        labels_e,
        means_e,
        yerr=stds_e,
        capsize=5,
        color=["#2B5C8F", "#D95F02", "#7570B3"],
        edgecolor="black",
        alpha=0.9,
        width=0.5,
    )
    axes[1].set_title("Kịch bản E: Chi phí Phân tách miền & Hủy khóa RAM", fontweight="bold")
    axes[1].set_ylabel("Thời gian trung bình (µs)")
    for bar, mean_val in zip(bars_e, means_e):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + max(stds_e) * 0.15,
            f"{mean_val:.2f} µs",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_CHART_DIR, "fig2_handshake_and_domain_sep_barchart.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Đã xuất biểu đồ 2: {out_path}")


def plot_multisession_throughput() -> None:
    df = _load_benchmark_df()
    payload_specs = [
        ("C_Payload_64B_us", "64 B", 64),
        ("C_Payload_1KB_us", "1 KB", 1024),
        ("C_Payload_16KB_us", "16 KB", 16 * 1024),
        ("C_Payload_64KB_us", "64 KB", 64 * 1024),
    ]

    labels = []
    mean_latencies = []
    std_latencies = []
    mean_throughputs = []
    std_throughputs = []

    for col, label, size_bytes in payload_specs:
        lat_series = df[col]
        # Thông lượng hai chiều (Mã hóa + Giải mã) đơn vị MB/s
        tp_series = ((size_bytes * 2) / (1024 * 1024)) / (lat_series / 1_000_000.0)

        labels.append(label)
        mean_latencies.append(lat_series.mean())
        std_latencies.append(lat_series.std())
        mean_throughputs.append(tp_series.mean())
        std_throughputs.append(tp_series.std())

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # --- Biểu đồ trái: Thông lượng AES-256-GCM (MB/s) ---
    bars_tp = axes[0].bar(
        labels,
        mean_throughputs,
        yerr=std_throughputs,
        capsize=5,
        color="#1B9E77",
        edgecolor="black",
        alpha=0.9,
        width=0.5,
    )
    axes[0].set_title("Kịch bản C: Thông lượng kênh dữ liệu AES-256-GCM (MB/s)", fontweight="bold")
    axes[0].set_xlabel("Kích thước gói tin (Payload)")
    axes[0].set_ylabel("Thông lượng trung bình (MB/s)")
    for bar, tp_val in zip(bars_tp, mean_throughputs):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + max(std_throughputs) * 0.12,
            f"{tp_val:.1f} MB/s",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    # --- Biểu đồ phải: Độ trễ xử lý khứ hồi (µs) ---
    axes[1].errorbar(
        labels,
        mean_latencies,
        yerr=std_latencies,
        fmt="-o",
        color="#D95F02",
        linewidth=2.2,
        markersize=8,
        capsize=5,
    )
    axes[1].set_title("Kịch bản C: Độ trễ khứ hồi Mã hóa + Giải mã (µs)", fontweight="bold")
    axes[1].set_xlabel("Kích thước gói tin (Payload)")
    axes[1].set_ylabel("Độ trễ trung bình (µs)")
    for x_idx, lat_val in enumerate(mean_latencies):
        axes[1].annotate(
            f"{lat_val:.1f} µs",
            (labels[x_idx], lat_val),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_CHART_DIR, "fig3_aead_session_throughput.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Đã xuất biểu đồ 3: {out_path}")


def generate_all_charts() -> None:
    os.makedirs(OUTPUT_CHART_DIR, exist_ok=True)
    print("[*] Đang khởi tạo các biểu đồ thống kê từ dữ liệu thực nghiệm...")
    plot_boxplot_hkdf_latency()
    plot_barchart_scenarios()
    plot_multisession_throughput()
    print("=== HOÀN TẤT XUẤT TOÀN BỘ BIỂU ĐỒ VÀO THƯ MỤC 06_ExperimentalResults/charts ===")


if __name__ == "__main__":
    os.makedirs(OUTPUT_CHART_DIR, exist_ok=True)
    generate_all_charts()