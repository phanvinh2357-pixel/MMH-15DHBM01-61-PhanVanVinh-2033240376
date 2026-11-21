import os
import sys

# Đảm bảo Python luôn tìm thấy các mô-đun trong cùng thư mục 03_SourceCode
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

from crypto_engine import (
    generate_ecdh_keypair,
    compute_shared_secret,
    hkdf_extract,
    derive_session_keys,
)
from session_manager import SecureSession


def _init_demo_sessions(session_id: str = "HUIT-SESS-2026"):
    """Hàm hỗ trợ khởi tạo cặp phiên Client - Server qua bắt tay ECDH P-256 và HKDF."""
    client_priv, client_pub = generate_ecdh_keypair()
    server_priv, server_pub = generate_ecdh_keypair()

    z_client = compute_shared_secret(client_priv, server_pub)
    z_server = compute_shared_secret(server_priv, client_pub)
    assert z_client == z_server, "Lỗi bắt tay ECDH!"

    salt = os.urandom(32)
    client_keys = derive_session_keys(hkdf_extract(salt, z_client))
    server_keys = derive_session_keys(hkdf_extract(salt, z_server))

    client_session = SecureSession("client", session_id, client_keys)
    server_session = SecureSession("server", session_id, server_keys)
    return salt, client_keys, client_session, server_session


def run_normal_flow():
    print("\n" + "=" * 72)
    print("[MÔ PHỎNG 1] LUỒNG HOẠT ĐỘNG CHUẨN TRÊN 3 KÊNH & HỦY KHÓA AN TOÀN")
    print("=" * 72)

    salt, keys, client, server = _init_demo_sessions("SESS-NORMAL-01")
    print(f"[+] Bắt tay ECDH P-256 & HKDF-Extract thành công (Salt: {salt[:8].hex()}...)")
    print("[+] Bộ 5 khóa phiên độc lập được dẫn xuất (256-bit mỗi khóa):")
    for k_name, k_val in keys.items():
        print(f"    - {k_name:<10}: {k_val[:12].hex()}... (32 bytes)")

    # 1. Kênh Điều khiển (CONTROL-PLANE)
    cmd_goc = "CMD:SET_KEY_ROTATION|INTERVAL=3600s"
    nonce_ctrl, ct_ctrl = client.encrypt_control_message(cmd_goc)
    cmd_nhan = server.decrypt_control_message(nonce_ctrl, ct_ctrl)
    print(f"\n[1. CONTROL-PLANE] Client gửi lệnh  : {cmd_goc}")
    print(f"                    Server giải mã   : {cmd_nhan} -> [HỢP LỆ]")

    # 2. Kênh Dữ liệu hai chiều (DATA-PLANE)
    msg_tx = b"Giao dich #01: Chuyen 25.000.000 VND toi tai khoan 2033240376"
    seq_tx, ct_data = client.encrypt_data(msg_tx)
    msg_rx = server.decrypt_data(seq_tx, ct_data)
    print(f"\n[2. DATA-PLANE]    Client gửi (seq={seq_tx}): {msg_tx.decode('utf-8')}")
    print(f"                    Server nhận      : {msg_rx.decode('utf-8')} -> [HỢP LỆ]")

    ack_tx = b"ACK #01: Giao dich da duoc xac thuc va ghi so"
    seq_ack, ct_ack = server.encrypt_data(ack_tx)
    ack_rx = client.decrypt_data(seq_ack, ct_ack)
    print(f"                    Server phản hồi  : {ack_rx.decode('utf-8')} -> [HỢP LỆ]")

    # 3. Kênh Kiểm toán Nhật ký (AUDIT-PLANE)
    audit_log = "AUDIT|SESS=SESS-NORMAL-01|CLIENT_TX=1|SERVER_TX=1|RESULT=COMMITTED"
    audit_tag = server.generate_audit_tag(audit_log)
    is_valid_log = client.verify_audit_tag(audit_log, audit_tag)
    print(f"\n[3. AUDIT-PLANE]   Bản ghi nhật ký : {audit_log}")
    print(f"                    Thẻ HMAC-SHA256  : {audit_tag[:16].hex()}...")
    print(f"                    Xác thực toàn vẹn: {is_valid_log} -> [KHỚP CHỮ KÝ]")

    # 4. Đóng phiên & Xóa sạch khóa trên RAM (Zeroization)
    client.terminate_session("Hoan tat phien giao dich")
    server.terminate_session("Hoan tat phien giao dich")
    print(f"\n[4. ZEROIZATION]   Trạng thái phiên : is_active={client.is_active}")
    print(f"                    Vùng đệm K_send  : {bytes(client._keys['K_send']).hex()} (Đã xóa sạch về 0x00)")


def run_attack_scenario_1():
    print("\n" + "=" * 72)
    print("[KỊCH BẢN TẤN CÔNG 1] NHẦM LẪN KHÓA GIỮA CÁC MIỀN (CROSS-DOMAIN ATTACK)")
    print("=" * 72)

    _, keys, client, server = _init_demo_sessions("SESS-ATTACK-01")
    nonce_ctrl, ct_ctrl = client.encrypt_control_message("CMD:SHUTDOWN_FIREWALL")
    print("[*] Gói tin được mã hóa bằng K_control trên CONTROL-PLANE.")

    # Thử dùng khóa xuất khẩu (K_export) hoặc khóa dữ liệu (K_send) để giải mã gói tin điều khiển
    print("[*] Kẻ tấn công / Mô-đun lỗi thử dùng K_export để giải mã gói tin CONTROL-PLANE...")
    try:
        aad_ctrl = b"HUIT-SEC-V1|CONTROL|SESS-ATTACK-01"
        AESGCM(keys["K_export"]).decrypt(nonce_ctrl, ct_ctrl, aad_ctrl)
        print("[THẤT BẠI] Lỗ hổng: K_export giải mã được gói tin của kênh khác!")
    except InvalidTag:
        print("[CHẶN THÀNH CÔNG] Hệ thống ném ngoại lệ InvalidTag! Khóa các miền hoàn toàn độc lập.")

    # Thử đưa bản mã kênh CONTROL sang hàm giải mã kênh DATA
    print("[*] Thử chuyển hướng bản mã CONTROL-PLANE sang bộ giải mã DATA-PLANE...")
    try:
        server.decrypt_data(0, ct_ctrl)
        print("[THẤT BẠI] Lỗ hổng: Kênh DATA chấp nhận bản mã của kênh CONTROL!")
    except InvalidTag:
        print("[CHẶN THÀNH CÔNG] Từ chối giải mã (Fail-Closed) do sai khóa và sai ngữ cảnh AAD.")


def run_attack_scenario_2():
    print("\n" + "=" * 72)
    print("[KỊCH BẢN TẤN CÔNG 2] SỬA ĐỔI BẢN MÃ & PHÁT LẠI GÓI TIN (TAMPER & REPLAY)")
    print("=" * 72)

    _, _, client, server = _init_demo_sessions("SESS-ATTACK-02")
    seq, ciphertext = client.encrypt_data(b"Chuyen khoan: 10.000 VND")

    # Phần A: Tấn công sửa đổi 1 bit trên đường truyền (Bit-flipping Tamper)
    tampered_ct = bytearray(ciphertext)
    tampered_ct[0] ^= 0x01
    print("[*] Phần A: Kẻ tấn công chặn đường truyền và đảo 1 bit trong bản mã...")
    try:
        server.decrypt_data(seq, bytes(tampered_ct))
        print("[THẤT BẠI] Bản mã bị sửa đổi vẫn được giải mã!")
    except InvalidTag:
        print("[CHẶN THÀNH CÔNG] AES-256-GCM phát hiện sai lệch thẻ xác thực (InvalidTag) -> Hủy gói tin.")

    # Phần B: Tấn công phát lại gói tin hợp lệ cũ (Replay Attack)
    print("\n[*] Phần B: Server nhận gói tin hợp lệ seq=0, sau đó kẻ tấn công phát lại gói tin này...")
    valid_msg = server.decrypt_data(seq, ciphertext)
    print(f"    -> Lần 1 (seq={seq}): Server giải mã thành công -> '{valid_msg.decode('utf-8')}'")
    try:
        server.decrypt_data(seq, ciphertext)
        print("[THẤT BẠI] Server chấp nhận gói tin phát lại!")
    except ValueError as e:
        print(f"[CHẶN THÀNH CÔNG] Phát hiện tấn công phát lại: {e}")


def run_attack_scenario_3():
    print("\n" + "=" * 72)
    print("[KỊCH BẢN TẤN CÔNG 3] GIẢ MẠO NHẬT KÝ & TRÍCH XUẤT RAM SAU ĐÓNG PHIÊN")
    print("=" * 72)

    _, _, client, server = _init_demo_sessions("SESS-ATTACK-03")

    # Phần A: Sửa đổi nội dung nhật ký kiểm toán đã ký
    log_goc = "AUDIT|USER=admin|ACTION=WITHDRAW|AMOUNT=1000"
    tag_goc = server.generate_audit_tag(log_goc)
    log_gia_mao = "AUDIT|USER=admin|ACTION=WITHDRAW|AMOUNT=9999"

    print("[*] Phần A: Kẻ nội gián sửa số tiền trong nhật ký từ 1000 thành 9999...")
    ket_qua = client.verify_audit_tag(log_gia_mao, tag_goc)
    print(f"[CHẶN THÀNH CÔNG] Kết quả kiểm tra chữ ký HMAC-SHA256: {ket_qua} (Phát hiện giả mạo nhật ký).")

    # Phần B: Đóng phiên, xóa RAM và thử truy xuất lại khóa/mã hóa trái phép
    print("\n[*] Phần B: Kết thúc phiên (terminate_session) và thử trích xuất bộ nhớ / mã hóa tiếp...")
    client.terminate_session("Phat hien hanh vi bat thuong")
    ram_dump = bytes(client._keys["K_control"]).hex()
    print(f"    -> Kết quả đọc vùng nhớ K_control sau zeroize: {ram_dump}")
    try:
        client.encrypt_data(b"Du lieu gui trai phep sau khi dong phien")
        print("[THẤT BẠI] Phiên đã đóng vẫn cho phép mã hóa!")
    except RuntimeError as e:
        print(f"[CHẶN THÀNH CÔNG] Hệ thống khóa chặt truy cập sau hủy khóa: {e}")


if __name__ == "__main__":
    print("=== CHƯƠNG TRÌNH MÔ PHỎNG 3 KÊNH & 3 KỊCH BẢN TẤN CÔNG HKDF ===")
    run_normal_flow()
    run_attack_scenario_1()
    run_attack_scenario_2()
    run_attack_scenario_3()
    print("\n=== HOÀN TẤT TOÀN BỘ KỊCH BẢN MÔ PHỎNG AN TOÀN ===")