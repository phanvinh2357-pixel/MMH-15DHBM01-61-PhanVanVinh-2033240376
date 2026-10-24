import unittest
import os
import sys

# Đưa thư mục 03_SourceCode vào hệ thống tìm kiếm mô-đun của Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_engine import (
    generate_ecdh_keypair,
    compute_shared_secret,
    hkdf_extract,
    build_info_string,
    hkdf_expand,
    derive_session_keys
)
from session_manager import SecureSession


class TestHkdfSessionSecurity(unittest.TestCase):

    def test_tc01_ecdh_consistency(self):
        client_priv, client_pub = generate_ecdh_keypair()
        server_priv, server_pub = generate_ecdh_keypair()
        z_client = compute_shared_secret(client_priv, server_pub)
        z_server = compute_shared_secret(server_priv, client_pub)
        self.assertEqual(z_client, z_server, "Lỗi: Bí mật dùng chung ECDH hai phía không trùng khớp.")
        self.assertEqual(len(z_client), 32, "Lỗi: Độ dài bí mật chia sẻ ECDH P-256 phải đúng 32 bytes.")

    def test_tc02_extract_deterministic(self):
        salt = b"\x12" * 32
        ikm = b"\x34" * 32
        prk_lan_1 = hkdf_extract(salt, ikm)
        prk_lan_2 = hkdf_extract(salt, ikm)
        self.assertEqual(prk_lan_1, prk_lan_2, "Lỗi: Pha HKDF-Extract không đảm bảo tính tất định.")
        self.assertEqual(len(prk_lan_1), 32, "Lỗi: Đầu ra PRK của SHA-256 phải đúng 32 bytes.")

    def test_tc09_fallback_zero_salt(self):
        ikm = b"\x56" * 32
        prk_salt_chuan = hkdf_extract(b"\x00" * 32, ikm)
        prk_salt_none = hkdf_extract(None, ikm)
        prk_salt_rong = hkdf_extract(b"", ikm)
        self.assertEqual(prk_salt_none, prk_salt_chuan, "Lỗi: Fallback salt=None không khớp với 32 byte 0x00.")
        self.assertEqual(prk_salt_rong, prk_salt_chuan, "Lỗi: Fallback salt=b'' không khớp với 32 byte 0x00.")

    def test_tc10_invalid_ikm_handling(self):
        salt = b"\x78" * 32
        with self.assertRaises(ValueError):
            hkdf_extract(salt, None)
        with self.assertRaises(ValueError):
            hkdf_extract(salt, b"")

    def test_tc03_expand_deterministic(self):
        raise NotImplementedError("Lê Minh Khôi cần hiện thực ca kiểm thử TC03.")

    def test_tc04_rfc5869_test_vectors(self):
        raise NotImplementedError("Lê Minh Khôi cần hiện thực ca kiểm thử TC04.")

    def test_tc06_avalanche_effect_on_info(self):
        raise NotImplementedError("Lê Minh Khôi cần hiện thực ca kiểm thử TC06.")

    def test_tc08_prefix_consistency_by_length(self):
        raise NotImplementedError("Lê Minh Khôi cần hiện thực ca kiểm thử TC08.")

    def test_tc13_expand_max_length_bound(self):
        raise NotImplementedError("Lê Minh Khôi cần hiện thực ca kiểm thử TC13.")

    def test_tc14_export_key_independence(self):
        raise NotImplementedError("Lê Minh Khôi cần hiện thực ca kiểm thử TC14.")

    def test_tc05_domain_separation_orthogonality(self):
        raise NotImplementedError("Nguyễn Thanh Đăng Khoa cần hiện thực ca kiểm thử TC05.")

    def test_tc07_protocol_label_sensitivity(self):
        raise NotImplementedError("Nguyễn Thanh Đăng Khoa cần hiện thực ca kiểm thử TC07.")

    def test_tc11_ciphertext_tamper_fail_closed(self):
        raise NotImplementedError("Nguyễn Thanh Đăng Khoa cần hiện thực ca kiểm thử TC11.")

    def test_tc12_memory_zeroization(self):
        raise NotImplementedError("Đỗ Đặng Hiếu Trung cần hiện thực ca kiểm thử TC12.")

    def test_tc15_salt_freshness_cross_session(self):
        raise NotImplementedError("Đỗ Đặng Hiếu Trung cần hiện thực ca kiểm thử TC15.")


if __name__ == "__main__":
    unittest.main()