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


from crypto_engine import CryptoEngineExpand as CE

PRK = b"\x99" * 32


def _measure(fn, n=ITERATIONS):
    out = []
    for _ in range(n):
        t0 = time.perf_counter_ns()
        fn()
        out.append((time.perf_counter_ns() - t0) / 1e6)  # ms
    return out


def _stats(v):
    return {"mean_ms": statistics.mean(v), "std_ms": statistics.stdev(v)}


def benchmark_scenario_a() -> Dict[str, List[float]]:
    """A: độ trễ HKDF-Expand theo độ dài đầu ra L."""
    info = CE.build_context_info("DATA-PLANE", "client-write-enc", 2, 32)
    return {f"L={L}B": _measure(lambda L=L: CE.hkdf_expand(PRK, info, L))
            for L in (16, 32, 64, 128, 256)}


def benchmark_scenario_b() -> Dict[str, List[float]]:
    """B: độ trễ HKDF-Expand theo kích thước info."""
    return {f"info={n}B": _measure(lambda n=n: CE.hkdf_expand(PRK, b"a" * n, 32))
            for n in (16, 64, 256, 1024)}


def benchmark_scenario_c() -> Dict[str, Dict[str, float]]:
    """C: chi phí từng khóa trong derive_session_keys (mean, std)."""
    specs = {
        "K_control": ("CONTROL-PLANE", "ctrl-aes-gcm-key", 1, 32),
        "K_send": ("DATA-PLANE", "client-write-enc", 2, 32),
        "K_recv": ("DATA-PLANE", "server-write-enc", 3, 32),
        "K_audit": ("AUDIT-PLANE", "session-audit-mac", 4, 32),
        "Nonce_base": ("DATA-PLANE", "aead-base-iv", 5, 12),
        "K_export": ("EXPORT-PLANE", "session-export-key", 6, 32),
    }
    out = {}
    for name, (p, lb, k, n) in specs.items():
        def one(p=p, lb=lb, k=k, n=n):
            CE.hkdf_expand(PRK, CE.build_context_info(p, lb, k, n), n)
        out[name] = _stats(_measure(one))
    return out


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
    """E: tổng độ trễ derive_session_keys (6 khóa một lần)."""
    return {"derive_6_keys": _measure(lambda: CE.derive_session_keys(PRK))}


def export_results_to_csv(raw_data: Dict[str, List[float]], summary_data: List[Dict[str, float]]) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(RAW_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "run", "time_ms"])
        for name, vals in raw_data.items():
            for i, t in enumerate(vals, 1):
                w.writerow([name, i, f"{t:.6f}"])
    with open(SUMMARY_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["scenario", "n", "mean_ms", "std_ms"])
        w.writeheader()
        w.writerows(summary_data)
    print(f"[+] Đã ghi: {RAW_CSV_PATH}")
    print(f"[+] Đã ghi: {SUMMARY_CSV_PATH}")


def run_all_benchmarks() -> None:
    raw: Dict[str, List[float]] = {}
    summary: List[Dict[str, float]] = []

    def add(prefix, data):
        for name, vals in data.items():
            key = f"{prefix}_{name}"
            raw[key] = vals
            summary.append({"scenario": key, "n": len(vals), **_stats(vals)})

    add("A", benchmark_scenario_a())
    add("B", benchmark_scenario_b())
    for name, s in benchmark_scenario_c().items():
        summary.append({"scenario": f"C_{name}", "n": ITERATIONS, **s})
    try:
        d = benchmark_scenario_d()
        add("D", {k: [x / 1000 for x in v] for k, v in d.items()})  # µs -> ms
    except ImportError as e:
        print(f"[!] Bỏ qua kịch bản D (chưa có hkdf_extract): {e}")
    add("E", benchmark_scenario_e())
    export_results_to_csv(raw, summary)


if __name__ == "__main__":
    print(f"=== MÔI TRƯỜNG ĐO: {platform.system()} {platform.release()} | CPU: {platform.processor()} ===")
    run_all_benchmarks()