import os
import struct
from typing import Dict, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hmac, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand


class SecureSession:
    def __init__(self, role: str, session_id: str, keys: Dict[str, bytes]):
        self.role = role
        self.session_id = session_id
        self._keys = keys.copy()
        self.tx_seq: int = 0
        self.rx_seq: int = 0
        self.is_active: bool = True

    # ========================================================================
    # PHẦN 1: PHỤ TRÁCH BỞI NGUYỄN THANH ĐĂNG KHOA (TV3)
    # ========================================================================

    def _derive_nonce(self, seq: int) -> bytes:
        raise NotImplementedError("Nguyễn Thanh Đăng Khoa cần hiện thực hàm _derive_nonce()")

    def encrypt_control_message(self, command: str) -> Tuple[bytes, bytes]:
        raise NotImplementedError("Nguyễn Thanh Đăng Khoa cần hiện thực hàm encrypt_control_message()")

    def decrypt_control_message(self, nonce: bytes, ciphertext: bytes) -> str:
        raise NotImplementedError("Nguyễn Thanh Đăng Khoa cần hiện thực hàm decrypt_control_message()")

    def encrypt_data(self, data: bytes) -> Tuple[int, bytes]:
        raise NotImplementedError("Nguyễn Thanh Đăng Khoa cần hiện thực hàm encrypt_data()")

    def decrypt_data(self, seq: int, ciphertext: bytes) -> bytes:
        raise NotImplementedError("Nguyễn Thanh Đăng Khoa cần hiện thực hàm decrypt_data()")

    # ========================================================================
    # PHẦN 2: PHỤ TRÁCH BỞI ĐỖ ĐẶNG HIẾU TRUNG (TV4)
    # ========================================================================

    def generate_audit_tag(self, log_record: str) -> bytes:
        raise NotImplementedError("Đỗ Đặng Hiếu Trung cần hiện thực hàm generate_audit_tag()")

    def verify_audit_tag(self, log_record: str, tag: bytes) -> bool:
        raise NotImplementedError("Đỗ Đặng Hiếu Trung cần hiện thực hàm verify_audit_tag()")

    def zeroize_memory(self) -> None:
        raise NotImplementedError("Đỗ Đặng Hiếu Trung cần hiện thực hàm zeroize_memory()")

    def terminate_session(self, reason: str) -> None:
        raise NotImplementedError("Đỗ Đặng Hiếu Trung cần hiện thực hàm terminate_session()")


def derive_keys_single_shot(prk: bytes) -> Dict[str, bytes]:
    raise NotImplementedError("Đỗ Đặng Hiếu Trung cần hiện thực hàm derive_keys_single_shot()")