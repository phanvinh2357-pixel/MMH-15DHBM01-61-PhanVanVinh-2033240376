import unittest
import os
import sys

# Đưa thư mục 03_SourceCode vào hệ thống tìm kiếm mô-đun của Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

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

    # ==========================================================================
    # PHẦN 1: KIỂM THỬ CỦA PHAN VĂN VINH (TV1)
    # ==========================================================================

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

    # ==========================================================================
    # PHẦN 2: KIỂM THỬ CỦA LÊ MINH KHÔI (TV2)
    # ==========================================================================

    def test_tc03_expand_deterministic(self):
        prk = b"\xaa" * 32
        info = build_info_string("DATA-PLANE", "client-write-enc", "data-tx-01", 32)
        okm_1 = hkdf_expand(prk, info, 32)
        okm_2 = hkdf_expand(prk, info, 32)
        self.assertEqual(okm_1, okm_2, "Lỗi: Hàm hkdf_expand không đảm bảo tính tất định.")
        self.assertEqual(len(okm_1), 32, "Lỗi: Độ dài khóa đầu ra không khớp tham số L.")

    def test_tc04_rfc5869_test_vectors(self):
        # Vector kiểm thử chuẩn Case 1 (SHA-256) theo RFC 5869 Appendix A.1
        ikm = bytes.fromhex("0b" * 22)
        salt = bytes.fromhex("000102030405060708090a0b0c")
        info = bytes.fromhex("f0f1f2f3f4f5f6f7f8f9")
        expected_prk = bytes.fromhex(
            "077709362c2e32df0ddc3f0dc47bba63"
            "90b6c73bb50f9c3122ec844ad7c2b3e5"
        )
        expected_okm = bytes.fromhex(
            "3cb25f25faacd57a90434f64d0362f2a"
            "2d2d0a90cf1a5a4c5db02d56ecc4c5bf"
            "34007208d5b887185865"
        )

        actual_prk = hkdf_extract(salt, ikm)
        actual_okm = hkdf_expand(actual_prk, info, 42)
        self.assertEqual(actual_prk, expected_prk, "Lỗi: PRK sai lệch so với vector chuẩn RFC 5869.")
        self.assertEqual(actual_okm, expected_okm, "Lỗi: OKM sai lệch so với vector chuẩn RFC 5869.")

    def test_tc06_avalanche_effect_on_info(self):
        prk = b"\xbb" * 32
        info_goc = bytearray(build_info_string("DATA-PLANE", "client-write-enc", "data-tx-01", 32))
        info_dao_bit = bytearray(info_goc)
        info_dao_bit[0] ^= 0x01  # Lật đúng 1 bit đầu tiên

        k1 = hkdf_expand(prk, bytes(info_goc), 32)
        k2 = hkdf_expand(prk, bytes(info_dao_bit), 32)

        hamming_dist = sum(bin(b1 ^ b2).count("1") for b1, b2 in zip(k1, k2))
        avalanche_ratio = hamming_dist / 256.0
        self.assertTrue(
            0.35 <= avalanche_ratio <= 0.65,
            f"Lỗi: Tỷ lệ hiệu ứng thác ({avalanche_ratio:.2%}) lệch khỏi ngưỡng chuẩn ~50%."
        )

    def test_tc08_prefix_consistency_by_length(self):
        prk = b"\xcc" * 32
        info = b"HUIT-SEC-V1||prefix-check"
        k_16 = hkdf_expand(prk, info, 16)
        k_32 = hkdf_expand(prk, info, 32)
        self.assertEqual(k_32[:16], k_16, "Lỗi: 16 byte đầu của khóa 32B không khớp với khóa 16B.")

    def test_tc13_expand_max_length_bound(self):
        prk = b"\xdd" * 32
        info = b"HUIT-SEC-V1||max-length"
        okm_max = hkdf_expand(prk, info, 8160)
        self.assertEqual(len(okm_max), 8160, "Lỗi: Không dẫn xuất đủ 8160 bytes ở ngưỡng trần.")

        with self.assertRaises(ValueError):
            hkdf_expand(prk, info, 8161)
        with self.assertRaises(ValueError):
            hkdf_expand(prk, info, 0)

    def test_tc14_export_key_independence(self):
        prk = b"\xee" * 32
        keys = derive_session_keys(prk)
        nonce = b"\x01" * 12
        aad = b"session-data-channel"
        plaintext = b"Du lieu mat tren kenh Data"

        ciphertext = AESGCM(keys["K_send"]).encrypt(nonce, plaintext, aad)
        with self.assertRaises(InvalidTag):
            AESGCM(keys["K_export"]).decrypt(nonce, ciphertext, aad)

    # ==========================================================================
    # PHẦN 3: KIỂM THỬ CỦA NGUYỄN THANH ĐĂNG KHOA (TV3)
    # ==========================================================================

    def test_tc05_domain_separation_orthogonality(self):
        prk = b"\x11" * 32
        keys = derive_session_keys(prk)
        self.assertEqual(len(keys), 5, "Lỗi: Phải dẫn xuất đủ 5 khóa phiên độc lập.")
        self.assertEqual(len(set(keys.values())), 5, "Lỗi: Phát hiện khóa phiên trùng lặp giữa các miền.")

    def test_tc07_protocol_label_sensitivity(self):
        prk = b"\x22" * 32
        info_tx = build_info_string("DATA-PLANE", "client-write-enc", "data-tx-01", 32)
        info_rx = build_info_string("DATA-PLANE", "server-write-enc", "data-rx-01", 32)
        self.assertNotEqual(info_tx, info_rx, "Lỗi: Chuỗi ngữ cảnh info không phân biệt được chiều gửi/nhận.")
        self.assertNotEqual(
            hkdf_expand(prk, info_tx, 32),
            hkdf_expand(prk, info_rx, 32),
            "Lỗi: Khóa dẫn xuất trùng nhau dù khác nhãn giao thức."
        )

    def test_tc11_ciphertext_tamper_fail_closed(self):
        priv_c, pub_c = generate_ecdh_keypair()
        priv_s, pub_s = generate_ecdh_keypair()
        z_c = compute_shared_secret(priv_c, pub_s)
        z_s = compute_shared_secret(priv_s, pub_c)
        salt = os.urandom(32)

        client = SecureSession("client", "SESS-01", derive_session_keys(hkdf_extract(salt, z_c)))
        server = SecureSession("server", "SESS-01", derive_session_keys(hkdf_extract(salt, z_s)))

        seq, ciphertext = client.encrypt_data(b"Lenh chuyen khoan: 50.000.000 VND")
        tampered_ct = bytearray(ciphertext)
        tampered_ct[0] ^= 0xFF  # Giả lập kẻ tấn công sửa đổi 1 byte bản mã

        with self.assertRaises(InvalidTag):
            server.decrypt_data(seq, bytes(tampered_ct))

    # ==========================================================================
    # PHẦN 4: KIỂM THỬ CỦA ĐỖ ĐẶNG HIẾU TRUNG (TV4)
    # ==========================================================================

    def test_tc12_memory_zeroization(self):
        prk = b"\x33" * 32
        session = SecureSession("client", "SESS-02", derive_session_keys(prk))

        tag = session.generate_audit_tag("AUDIT|action=LOGIN|status=OK")
        self.assertTrue(session.verify_audit_tag("AUDIT|action=LOGIN|status=OK", tag))

        session.terminate_session("Dong phien theo yeu cau nguoi dung")
        self.assertFalse(session.is_active)

        for key_buf in session._keys.values():
            self.assertEqual(bytes(key_buf), b"\x00" * 32, "Lỗi: Vật liệu khóa chưa được xóa sạch về 0x00 trên RAM.")

        with self.assertRaises(RuntimeError):
            session.encrypt_data(b"Du lieu gui sau khi da huy khoa")

    def test_tc15_salt_freshness_cross_session(self):
        priv_c, pub_c = generate_ecdh_keypair()
        priv_s, pub_s = generate_ecdh_keypair()
        z_shared = compute_shared_secret(priv_c, pub_s)

        salt_1 = os.urandom(32)
        salt_2 = os.urandom(32)
        self.assertNotEqual(salt_1, salt_2, "Lỗi: Salt ngẫu nhiên bị trùng lặp giữa hai phiên.")

        keys_1 = derive_session_keys(hkdf_extract(salt_1, z_shared))
        keys_2 = derive_session_keys(hkdf_extract(salt_2, z_shared))

        for k_name in keys_1:
            self.assertNotEqual(
                keys_1[k_name],
                keys_2[k_name],
                f"Lỗi: Khóa {k_name} bị tái sử dụng giữa hai phiên độc lập."
            )


if __name__ == "__main__":
    unittest.main()