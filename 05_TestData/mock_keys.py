MOCK_PRK: bytes = b"\x01" * 32

MOCK_KEYS: dict[str, bytes] = {
    "K_control": b"\x11" * 32,
    "K_send": b"\x22" * 32,
    "K_recv": b"\x33" * 32,
    "K_audit": b"\x44" * 32,
    "Nonce_base": b"\x55" * 12,
    "K_export": b"\x66" * 32,
}

MOCK_PAYLOAD: bytes = "DỮ LIỆU GIAO DỊCH TÀI CHÍNH: CHUYỂN KHOẢN 50.000 USD".encode("utf-8")