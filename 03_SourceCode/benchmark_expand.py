"""
Module: benchmark_expand.py (Đo kiểm Kịch bản A & B)
Thực hiện bởi: Lê Minh Khôi - 2033240160
"""

import time
from crypto_engine import CryptoEngineExpand

def run_benchmark():
    prk = b"\x99" * 32
    iterations = 1000  # Lặp 1000 lần để tính trung bình chính xác

    print("=== KHẢO SÁT KỊCH BẢN A: ĐỘ TRỄ THEO ĐỘ DÀI L ===")
    lengths = [16, 32, 64]
    for l in lengths:
        info = CryptoEngineExpand.build_context_info("DATA-PLANE", "test-label", 1, l)
        start_time = time.perf_counter_ns()
        for _ in range(iterations):
            CryptoEngineExpand.hkdf_expand(prk, info, l)
        end_time = time.perf_counter_ns()
        
        avg_ns = (end_time - start_time) / iterations
        print(f"  - Độ dài L = {l:2d} bytes | Trung bình: {avg_ns:.2f} ns/lần")

    print("\n=== KHẢO SÁT KỊCH BẢN B: ĐỘ TRỄ THEO KÍCH THƯỚC INFO ===")
    info_sizes = {
        16: "abc",
        64: "a" * 50,
        256: "a" * 240
    }
    
    for target_size, label_str in info_sizes.items():
        info = CryptoEngineExpand.build_context_info("DATA-PLANE", label_str, 1, 32)
        start_time = time.perf_counter_ns()
        for _ in range(iterations):
            CryptoEngineExpand.hkdf_expand(prk, info, 32)
        end_time = time.perf_counter_ns()
        
        avg_ns = (end_time - start_time) / iterations
        print(f"  - Kích thước info thực tế ~ {len(info):3d} bytes | Trung bình: {avg_ns:.2f} ns/lần")

if __name__ == "__main__":
    run_benchmark()