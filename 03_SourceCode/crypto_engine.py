"""
Module: crypto_engine.py (Phần hiện thực: HKDF-Expand & Domain Separation)
Tác giả: Lê Minh Khôi - Mã sinh viên: 2033240160
"""

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

class CryptoEngineExpand:
    @staticmethod
    def build_context_info(protocol: str, label: str, key_id: int, length: int) -> bytes:
        """
        Chuẩn hóa chuỗi Context info theo đúng đặc tả phân tách miền:
        info = Header || Protocol || Label || Key_ID || Length
        """
        header = b"HUIT-SEC-V1"
        plane_bytes = protocol.encode('utf-8')
        label_bytes = label.encode('utf-8')
        key_id_bytes = f"{key_id:04d}".encode('utf-8')
        length_bytes = f"{length:02d}".encode('utf-8')
        
        info = header + b"||" + plane_bytes + b"||" + label_bytes + b"||" + key_id_bytes + b"||" + length_bytes
        return info

    @staticmethod
    def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
        """
        Hàm HKDF-Expand với bộ kiểm tra biên nghiêm ngặt L <= 8160 bytes (L_max).
        Ném ngoại lệ ValueError nếu vi phạm giới hạn để tránh lặp bộ đếm.
        """
        if length <= 0 or length > 255 * 32:  # 8160 bytes
            raise ValueError(f"ValueError: Invalid requested key length ({length} bytes). L must be between 1 and 8160.")
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=None,
            info=info,
        )
        return hkdf.derive(prk)

    @classmethod
    def derive_session_keys(cls, prk: bytes) -> dict:
        """
        Đường ống trích xuất toàn bộ các khóa phiên mục tiêu dựa trên phân tách miền.
        """
        keys = {}
        
        # 1. Khóa Điều khiển (K_control)
        info_ctrl = cls.build_context_info("CONTROL-PLANE", "ctrl-aes-gcm-key", 1, 32)
        keys['K_control'] = cls.hkdf_expand(prk, info_ctrl, 32)

        # 2. Khóa Gửi Dữ liệu (K_send)
        info_send = cls.build_context_info("DATA-PLANE", "client-write-enc", 2, 32)
        keys['K_send'] = cls.hkdf_expand(prk, info_send, 32)

        # 3. Khóa Nhận Dữ liệu (K_recv)
        info_recv = cls.build_context_info("DATA-PLANE", "server-write-enc", 3, 32)
        keys['K_recv'] = cls.hkdf_expand(prk, info_recv, 32)

        # 4. Khóa Kiểm toán Nhật ký (K_audit)
        info_audit = cls.build_context_info("AUDIT-PLANE", "session-audit-mac", 4, 32)
        keys['K_audit'] = cls.hkdf_expand(prk, info_audit, 32)

        # 5. Nonce Gốc (Nonce_base) - Độ dài 12 bytes
        info_nonce = cls.build_context_info("DATA-PLANE", "aead-base-iv", 5, 12)
        keys['Nonce_base'] = cls.hkdf_expand(prk, info_nonce, 12)

        # 6. Khóa Xuất khẩu phiên (K_export) - Độ dài 32 bytes
        info_export = cls.build_context_info("EXPORT-PLANE", "session-export-key", 6, 32)
        keys['K_export'] = cls.hkdf_expand(prk, info_export, 32)

        return keys

# --- Khối kiểm thử đơn vị (Unit Test) ---
if __name__ == "__main__":
    print("=== KIỂM THỬ MODULE HKDF-EXPAND (Lê Minh Khôi - 2033240160) ===")
    sample_prk = b"\x11" * 32  # Giả lập PRK 32 bytes
    
    session_keys = CryptoEngineExpand.derive_session_keys(sample_prk)
    for k_name, k_val in session_keys.items():
        print(f"[+] {k_name} ({len(k_val)} bytes): {k_val.hex()}")

    try:
        print("\n[*] Đang kiểm tra ngoại lệ biên L = 9000...")
        CryptoEngineExpand.hkdf_expand(sample_prk, b"test-info", 9000)
    except ValueError as e:
        print(f"[PASS] Bắt thành công ngoại lệ biên: {e}")