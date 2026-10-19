import os
from crypto_engine import (
    generate_ecdh_keypair, 
    compute_shared_secret, 
    hkdf_extract, 
    derive_session_keys
)
from session_manager import SecureSession


def run_normal_flow():
    raise NotImplementedError("Nguyễn Thanh Đăng Khoa và Đỗ Đặng Hiếu Trung cần hiện thực hàm này.")


def run_attack_scenario_1():
    raise NotImplementedError("Nguyễn Thanh Đăng Khoa cần hiện thực hàm này.")


def run_attack_scenario_2():
    raise NotImplementedError("Nguyễn Thanh Đăng Khoa cần hiện thực hàm này.")


def run_attack_scenario_3():
    raise NotImplementedError("Đỗ Đặng Hiếu Trung cần hiện thực hàm này.")


if __name__ == "__main__":
    print("=== CHƯƠNG TRÌNH MÔ PHỎNG 3 KÊNH & 3 KỊCH BẢN TẤN CÔNG HKDF ===")