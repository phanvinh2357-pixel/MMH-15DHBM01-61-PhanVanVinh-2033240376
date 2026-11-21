import os
import struct
from typing import Dict, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hmac, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand


class SecureSession:
    def __init__(self, role: str, session_id: str, keys: Dict[str, bytes]):
        if role.lower() not in ("client", "server"):
            raise ValueError("Vai trò phiên (role) chỉ chấp nhận 'client' hoặc 'server'.")
        self.role = role.lower()
        self.session_id = session_id
        # Lưu khóa dưới dạng mutable bytearray để hỗ trợ xóa an toàn trên RAM (Zeroization)
        self._keys: Dict[str, bytearray] = {
            k: bytearray(v) for k, v in keys.items()
        }
        self.tx_seq: int = 0
        self.rx_seq: int = 0
        self.is_active: bool = True
        self.termination_reason: str = ""

    def _ensure_active(self) -> None:
        if not self.is_active:
            raise RuntimeError("Lỗi an toàn: Phiên làm việc đã kết thúc và vật liệu khóa đã bị hủy.")

    # ========================================================================
    # PHẦN 1: PHỤ TRÁCH BỞI NGUYỄN THANH ĐĂNG KHOA (TV3)
    # ========================================================================

    def _derive_nonce(self, seq: int) -> bytes:
        if seq < 0:
            raise ValueError("Số thứ tự gói tin (seq) không được âm.")
        # Kết hợp 4 byte prefix + 8 byte số thứ tự big-endian = 12 bytes (96-bit Nonce chuẩn AES-GCM)
        return b"\x00\x00\x00\x00" + struct.pack("!Q", seq)

    def encrypt_control_message(self, command: str) -> Tuple[bytes, bytes]:
        self._ensure_active()
        nonce = os.urandom(12)
        aad = f"HUIT-SEC-V1|CONTROL|{self.session_id}".encode("utf-8")
        aesgcm = AESGCM(bytes(self._keys["K_control"]))
        ciphertext = aesgcm.encrypt(nonce, command.encode("utf-8"), aad)
        return nonce, ciphertext

    def decrypt_control_message(self, nonce: bytes, ciphertext: bytes) -> str:
        self._ensure_active()
        aad = f"HUIT-SEC-V1|CONTROL|{self.session_id}".encode("utf-8")
        aesgcm = AESGCM(bytes(self._keys["K_control"]))
        plaintext = aesgcm.decrypt(nonce, ciphertext, aad)
        return plaintext.decode("utf-8")

    def encrypt_data(self, data: bytes) -> Tuple[int, bytes]:
        self._ensure_active()
        seq = self.tx_seq
        self.tx_seq += 1

        nonce = self._derive_nonce(seq)
        tx_key_name = "K_send" if self.role == "client" else "K_recv"
        aad = f"HUIT-SEC-V1|DATA|{self.session_id}|{seq}".encode("utf-8")

        aesgcm = AESGCM(bytes(self._keys[tx_key_name]))
        ciphertext = aesgcm.encrypt(nonce, data, aad)
        return seq, ciphertext

    def decrypt_data(self, seq: int, ciphertext: bytes) -> bytes:
        self._ensure_active()
        if seq < self.rx_seq:
            raise ValueError("Lỗi an toàn: Phát hiện gói tin phát lại hoặc sai thứ tự (Replay Attack).")

        nonce = self._derive_nonce(seq)
        rx_key_name = "K_recv" if self.role == "client" else "K_send"
        aad = f"HUIT-SEC-V1|DATA|{self.session_id}|{seq}".encode("utf-8")

        aesgcm = AESGCM(bytes(self._keys[rx_key_name]))
        plaintext = aesgcm.decrypt(nonce, ciphertext, aad)
        self.rx_seq = seq + 1
        return plaintext

    # ========================================================================
    # PHẦN 2: PHỤ TRÁCH BỞI ĐỖ ĐẶNG HIẾU TRUNG (TV4)
    # ========================================================================

    def generate_audit_tag(self, log_record: str) -> bytes:
        self._ensure_active()
        h = hmac.HMAC(bytes(self._keys["K_audit"]), hashes.SHA256())
        h.update(log_record.encode("utf-8"))
        return h.finalize()

    def verify_audit_tag(self, log_record: str, tag: bytes) -> bool:
        self._ensure_active()
        h = hmac.HMAC(bytes(self._keys["K_audit"]), hashes.SHA256())
        h.update(log_record.encode("utf-8"))
        try:
            h.verify(tag)
            return True
        except Exception:
            return False

    def zeroize_memory(self) -> None:
        for key_buf in self._keys.values():
            for i in range(len(key_buf)):
                key_buf[i] = 0x00
        self.is_active = False

    def terminate_session(self, reason: str) -> None:
        self.termination_reason = reason
        self.zeroize_memory()


def derive_keys_single_shot(prk: bytes) -> Dict[str, bytes]:
    """Dẫn xuất gộp toàn bộ 160 bytes vật liệu khóa trong một lần gọi HKDF-Expand (dùng để đối chứng hiệu năng)."""
    if prk is None or len(prk) < 32:
        raise ValueError("Lỗi an toàn: Khóa giả ngẫu nhiên PRK phải có độ dài tối thiểu 32 bytes.")

    hkdf = HKDFExpand(
        algorithm=hashes.SHA256(),
        length=160,
        info=b"HUIT-SEC-V1||SINGLE-SHOT-ALL-KEYS",
    )
    okm = hkdf.derive(prk)
    return {
        "K_control": okm[0:32],
        "K_send": okm[32:64],
        "K_recv": okm[64:96],
        "K_audit": okm[96:128],
        "K_export": okm[128:160],
    }