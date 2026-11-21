import time
import os
import sys
import csv
import statistics
import platform
from typing import Dict, List, Any

# Đảm bảo Python luôn tìm thấy các mô-đun trong thư mục 03_SourceCode
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_engine import (
    generate_ecdh_keypair,
    compute_shared_secret,
    hkdf_extract,
    hkdf_expand,
    derive_session_keys,
)
from session_manager import SecureSession, derive_keys_single_shot

ITERATIONS: int = 50
WARMUP_ITERATIONS: int = 10

RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "06_ExperimentalResults"))
RAW_CSV_PATH = os.path.join(RESULTS_DIR, "benchmark_results.csv")
SUMMARY_CSV_PATH = os.path.join(RESULTS_DIR, "statistics_summary.csv")
TXT_REPORT_PATH = os.path.join(RESULTS_DIR, "ket_qua_benchmark.txt")


def _compute_stats(scenario: str, metric: str, samples: List[float]) -> Dict[str, Any]:
    """Tính toán các chỉ số thống kê mô tả cho một tập mẫu độ trễ (đơn vị: microsecond)."""
    sorted_samples = sorted(samples)
    p95_idx = min(len(sorted_samples) - 1, int(0.95 * len(sorted_samples)))
    return {
        "Kich_Ban": scenario,
        "Chi_Tieu": metric,
        "So_Lan_Lap": len(samples),
        "Trung_Binh_us": round(statistics.mean(samples), 3),
        "Do_Lech_Chuan_us": round(statistics.stdev(samples) if len(samples) > 1 else 0.0, 3),
        "Trung_Vi_us": round(statistics.median(samples), 3),
        "Min_us": round(min(samples), 3),
        "Max_us": round(max(samples), 3),
        "P95_us": round(sorted_samples[p95_idx], 3),
    }


def benchmark_scenario_a() -> Dict[str, List[float]]:
    print("[*] Đang thực thi Kịch bản A: Phân rã độ trễ bắt tay ECDH P-256 & HKDF...")
    metrics = [
        "A_ECDH_KeyGen_us",
        "A_ECDH_SharedSecret_us",
        "A_HKDF_Extract_us",
        "A_HKDF_Expand_5Keys_us",
        "A_Full_Handshake_us",
    ]
    results: Dict[str, List[float]] = {m: [] for m in metrics}

    salt = os.urandom(32)
    _, peer_pub = generate_ecdh_keypair()

    # Warm-up
    for _ in range(WARMUP_ITERATIONS):
        priv, _ = generate_ecdh_keypair()
        z = compute_shared_secret(priv, peer_pub)
        prk = hkdf_extract(salt, z)
        _ = derive_session_keys(prk)

    # Đo chính thức N = 50 lần
    for _ in range(ITERATIONS):
        t0 = time.perf_counter_ns()
        priv, _ = generate_ecdh_keypair()
        t1 = time.perf_counter_ns()
        z = compute_shared_secret(priv, peer_pub)
        t2 = time.perf_counter_ns()
        prk = hkdf_extract(salt, z)
        t3 = time.perf_counter_ns()
        _ = derive_session_keys(prk)
        t4 = time.perf_counter_ns()

        results["A_ECDH_KeyGen_us"].append((t1 - t0) / 1000.0)
        results["A_ECDH_SharedSecret_us"].append((t2 - t1) / 1000.0)
        results["A_HKDF_Extract_us"].append((t3 - t2) / 1000.0)
        results["A_HKDF_Expand_5Keys_us"].append((t4 - t3) / 1000.0)
        results["A_Full_Handshake_us"].append((t4 - t0) / 1000.0)

    return results


def benchmark_scenario_b() -> Dict[str, List[float]]:
    print("[*] Đang thực thi Kịch bản B: Độ trễ HKDF-Expand theo kích thước khóa đầu ra L...")
    lengths = [16, 32, 64, 256, 1024, 4096, 8160]
    prk = os.urandom(32)
    info = b"HUIT-SEC-V1||BENCHMARK||EXPAND-SCALING"
    results: Dict[str, List[float]] = {}

    for length in lengths:
        col_name = f"B_Expand_{length}B_us"
        latencies: List[float] = []

        for _ in range(WARMUP_ITERATIONS):
            _ = hkdf_expand(prk, info, length)

        for _ in range(ITERATIONS):
            start = time.perf_counter_ns()
            _ = hkdf_expand(prk, info, length)
            end = time.perf_counter_ns()
            latencies.append((end - start) / 1000.0)

        results[col_name] = latencies

    return results


def benchmark_scenario_c() -> Dict[str, Dict[str, float]]:
    print("[*] Đang thực thi Kịch bản C: Thông lượng & độ trễ AEAD AES-256-GCM trên kênh dữ liệu...")
    payload_sizes = {
        "C_Payload_64B": 64,
        "C_Payload_1KB": 1024,
        "C_Payload_16KB": 16 * 1024,
        "C_Payload_64KB": 64 * 1024,
    }
    keys = derive_session_keys(os.urandom(32))
    results: Dict[str, Dict[str, float]] = {}

    for label, size_bytes in payload_sizes.items():
        payload = os.urandom(size_bytes)
        client = SecureSession("client", "BENCH-SESS", keys)
        server = SecureSession("server", "BENCH-SESS", keys)

        # Warm-up
        for _ in range(WARMUP_ITERATIONS):
            seq, ct = client.encrypt_data(payload)
            _ = server.decrypt_data(seq, ct)

        latencies_us: List[float] = []
        for _ in range(ITERATIONS):
            start = time.perf_counter_ns()
            seq, ct = client.encrypt_data(payload)
            _ = server.decrypt_data(seq, ct)
            end = time.perf_counter_ns()
            latencies_us.append((end - start) / 1000.0)

        mean_us = statistics.mean(latencies_us)
        stdev_us = statistics.stdev(latencies_us) if len(latencies_us) > 1 else 0.0
        # Thông lượng hai chiều (mã hóa + giải mã) tính bằng MB/s
        throughput_mbps = ((size_bytes * 2) / (1024 * 1024)) / (mean_us / 1_000_000.0)

        results[label] = {
            "size_bytes": float(size_bytes),
            "mean_us": round(mean_us, 3),
            "stdev_us": round(stdev_us, 3),
            "throughput_mbps": round(throughput_mbps, 2),
            "raw_latencies": latencies_us,
        }

    return results


def benchmark_scenario_d() -> Dict[str, List[float]]:
    print("[*] Đang thực thi Kịch bản D: Đo độ trễ HKDF-Extract theo kích thước Salt...")
    salt_configs = {
        "Salt_0B_Rong": b"",
        "Salt_32B_Chuan": os.urandom(32),
        "Salt_64B_KhoiHash": os.urandom(64),
        "Salt_256B_MoRong": os.urandom(256),
    }
    ikm = os.urandom(32)
    results: Dict[str, List[float]] = {}

    for name, salt_val in salt_configs.items():
        latencies = []
        for _ in range(WARMUP_ITERATIONS):
            _ = hkdf_extract(salt_val, ikm)

        for _ in range(ITERATIONS):
            start = time.perf_counter_ns()
            _ = hkdf_extract(salt_val, ikm)
            end = time.perf_counter_ns()
            latencies.append((end - start) / 1000.0)
        results[name] = latencies

    os.makedirs(RESULTS_DIR, exist_ok=True)
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
    print("[*] Đang thực thi Kịch bản E: Đối chứng Multi-Expand phân tách miền vs Single-Shot & Zeroization...")
    prk = os.urandom(32)
    results: Dict[str, List[float]] = {
        "E_MultiExpand_DomainSep_us": [],
        "E_SingleShot_160B_us": [],
        "E_Zeroize_Memory_us": [],
    }

    for _ in range(WARMUP_ITERATIONS):
        keys = derive_session_keys(prk)
        _ = derive_keys_single_shot(prk)
        sess = SecureSession("client", "WARMUP", keys)
        sess.zeroize_memory()

    for _ in range(ITERATIONS):
        t0 = time.perf_counter_ns()
        keys = derive_session_keys(prk)
        t1 = time.perf_counter_ns()
        _ = derive_keys_single_shot(prk)
        t2 = time.perf_counter_ns()

        sess = SecureSession("client", "BENCH-ZERO", keys)
        t3 = time.perf_counter_ns()
        sess.zeroize_memory()
        t4 = time.perf_counter_ns()

        results["E_MultiExpand_DomainSep_us"].append((t1 - t0) / 1000.0)
        results["E_SingleShot_160B_us"].append((t2 - t1) / 1000.0)
        results["E_Zeroize_Memory_us"].append((t4 - t3) / 1000.0)

    return results


def export_results_to_csv(raw_data: Dict[str, List[float]], summary_data: List[Dict[str, Any]]) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # 1. Xuất toàn bộ dữ liệu thô (50 lần lặp x tất cả chỉ tiêu)
    columns = list(raw_data.keys())
    with open(RAW_CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Lan_Lap"] + columns)
        for i in range(ITERATIONS):
            row = [i + 1] + [round(raw_data[col][i], 3) for col in columns]
            writer.writerow(row)

    # 2. Xuất bảng tổng hợp thống kê (Mean, StdDev, Median, Min, Max, P95)
    fieldnames = [
        "Kich_Ban",
        "Chi_Tieu",
        "So_Lan_Lap",
        "Trung_Binh_us",
        "Do_Lech_Chuan_us",
        "Trung_Vi_us",
        "Min_us",
        "Max_us",
        "P95_us",
    ]
    with open(SUMMARY_CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_data)

    # 3. Xuất báo cáo dạng văn bản dễ đọc để chèn trực tiếp vào Báo cáo Word
    with open(TXT_REPORT_PATH, mode="w", encoding="utf-8") as f:
        f.write("=== KẾT QUẢ THỰC NGHIỆM HIỆU NĂNG HKDF & AEAD SESSION ===\n")
        f.write(f"Hệ điều hành : {platform.system()} {platform.release()}\n")
        f.write(f"Vi xử lý     : {platform.processor()}\n")
        f.write(f"Số lần lặp   : N = {ITERATIONS} (sau {WARMUP_ITERATIONS} lần chạy làm nóng)\n")
        f.write("=" * 88 + "\n")
        f.write(f"{'Kịch bản':<12} | {'Chỉ tiêu đo':<28} | {'Mean (us)':>10} | {'StdDev':>9} | {'Median':>9} | {'P95 (us)':>9}\n")
        f.write("-" * 88 + "\n")
        for item in summary_data:
            f.write(
                f"{item['Kich_Ban']:<12} | {item['Chi_Tieu']:<28} | "
                f"{item['Trung_Binh_us']:>10.3f} | {item['Do_Lech_Chuan_us']:>9.3f} | "
                f"{item['Trung_Vi_us']:>9.3f} | {item['P95_us']:>9.3f}\n"
            )

    print(f"[+] Đã xuất dữ liệu thô tổng hợp vào : {RAW_CSV_PATH}")
    print(f"[+] Đã xuất thống kê mô tả vào      : {SUMMARY_CSV_PATH}")
    print(f"[+] Đã xuất bảng tóm tắt văn bản vào: {TXT_REPORT_PATH}")


def run_all_benchmarks() -> None:
    res_a = benchmark_scenario_a()
    res_b = benchmark_scenario_b()
    res_c = benchmark_scenario_c()
    res_d = benchmark_scenario_d()
    res_e = benchmark_scenario_e()

    raw_data: Dict[str, List[float]] = {}
    summary_data: List[Dict[str, Any]] = []

    for metric, samples in res_a.items():
        raw_data[metric] = samples
        summary_data.append(_compute_stats("Kich_Ban_A", metric, samples))

    for metric, samples in res_b.items():
        raw_data[metric] = samples
        summary_data.append(_compute_stats("Kich_Ban_B", metric, samples))

    for label, info in res_c.items():
        metric_name = f"{label}_us"
        samples = info["raw_latencies"]
        raw_data[metric_name] = samples
        stat_row = _compute_stats("Kich_Ban_C", metric_name, samples)
        summary_data.append(stat_row)
        print(f"    -> {label}: Mean = {info['mean_us']} us | Throughput = {info['throughput_mbps']} MB/s")

    for salt_name, samples in res_d.items():
        metric_name = f"D_{salt_name}_us"
        raw_data[metric_name] = samples
        summary_data.append(_compute_stats("Kich_Ban_D", metric_name, samples))

    for metric, samples in res_e.items():
        raw_data[metric] = samples
        summary_data.append(_compute_stats("Kich_Ban_E", metric, samples))

    export_results_to_csv(raw_data, summary_data)
    print("=== HOÀN TẤT TOÀN BỘ 5 KỊCH BẢN ĐO HIỆU NĂNG ===")


if __name__ == "__main__":
    print(f"=== MÔI TRƯỜNG ĐO: {platform.system()} {platform.release()} | CPU: {platform.processor()} ===")
    run_all_benchmarks()