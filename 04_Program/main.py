import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "03_SourceCode"))
if SOURCE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_DIR)

SOURCE_DIR = os.path.join(os.path.dirname(__file__), "..", "03_SourceCode")
sys.path.append(SOURCE_DIR)


def print_menu() -> None:
    print("=" * 60)
    print("  TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP.HCM (HUIT)")
    print("  BÀI TẬP 22: TÁCH KHÓA PHIÊN BẰNG HKDF (RFC 5869)")
    print("  Nhóm: 61 - Lớp: 15DHBM01 | Trưởng nhóm: Phan Văn Vinh")
    print("=" * 60)
    print("1. Chạy Mô phỏng giao tiếp Client - Server (Happy Path)")
    print("2. Chạy Mô phỏng 3 Kịch bản Tấn công & Tự vệ Fail-Closed")
    print("3. Kích hoạt toàn bộ 15 Ca kiểm thử tự động (Unit Test)")
    print("4. Chạy Đo lường hiệu năng 5 Kịch bản & Xuất file CSV (N>=30)")
    print("5. Vẽ và xuất biểu đồ phân tích thống kê (300 DPI)")
    print("0. Thoát chương trình")
    print("=" * 60)


def handle_normal_flow() -> None:
    print("\n[+] Đang gọi mô phỏng luồng bình thường từ simulation_runner.py...")
    try:
        import simulation_runner
        simulation_runner.run_normal_flow()
    except NotImplementedError as e:
        print(f"[!] Chức năng chưa hoàn thiện: {e}")
    except Exception as e:
        print(f"[!] Lỗi thực thi: {e}")


def handle_attack_scenarios() -> None:
    print("\n[+] Đang gọi mô phỏng 3 kịch bản tấn công từ simulation_runner.py...")
    try:
        import simulation_runner
        simulation_runner.run_attack_scenario_1()
        simulation_runner.run_attack_scenario_2()
        simulation_runner.run_attack_scenario_3()
    except NotImplementedError as e:
        print(f"[!] Chức năng chưa hoàn thiện: {e}")
    except Exception as e:
        print(f"[!] Lỗi thực thi: {e}")


def handle_run_tests() -> None:
    print("\n[+] Đang kích hoạt 15 ca kiểm thử từ test_suite.py...\n")
    try:
        import unittest
        import test_suite
        suite = unittest.TestLoader().loadTestsFromModule(test_suite)
        unittest.TextTestRunner(verbosity=2).run(suite)
    except Exception as e:
        print(f"[!] Lỗi kích hoạt kiểm thử: {e}")


def handle_run_benchmarks() -> None:
    print("\n[+] Đang gọi module đo kiểm từ benchmark_harness.py...")
    try:
        import benchmark_harness
        benchmark_harness.run_all_benchmarks()
    except NotImplementedError as e:
        print(f"[!] Chức năng chưa hoàn thiện: {e}")
    except Exception as e:
        print(f"[!] Lỗi thực thi: {e}")


def handle_generate_charts() -> None:
    print("\n[+] Đang gọi module vẽ biểu đồ từ plot_benchmarks.py...")
    try:
        import plot_benchmarks
        plot_benchmarks.generate_all_charts()
    except NotImplementedError as e:
        print(f"[!] Chức năng chưa hoàn thiện: {e}")
    except Exception as e:
        print(f"[!] Lỗi thực thi: {e}")


def main() -> None:
    while True:
        print_menu()
        choice = input("Vui lòng chọn chức năng (0-5): ").strip()
        if choice == "1":
            handle_normal_flow()
        elif choice == "2":
            handle_attack_scenarios()
        elif choice == "3":
            handle_run_tests()
        elif choice == "4":
            handle_run_benchmarks()
        elif choice == "5":
            handle_generate_charts()
        elif choice == "0":
            print("\nĐã thoát chương trình thành công.")
            break
        else:
            print("\n[!] Lựa chọn không hợp lệ, vui lòng nhập số từ 0 đến 5.")
        input("\nNhấn Enter để quay lại menu...")


if __name__ == "__main__":
    main()