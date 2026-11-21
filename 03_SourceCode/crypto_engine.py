from typing import Tuple, Dict
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand

PROTOCOL_PREFIX = b"HUIT-SEC-V1"


# ==============================================================================
# PHẦN 1: PHỤ TRÁCH BỞI PHAN VĂN VINH (TV1)
# ==============================================================================

def generate_ecdh_keypair() -> Tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key


def compute_shared_secret(private_key: ec.EllipticCurvePrivateKey,
                          peer_public_key: ec.EllipticCurvePublicKey) -> bytes:
    shared_secret = private_key.exchange(ec.ECDH(), peer_public_key)
    return shared_secret


def hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    if ikm is None or len(ikm) == 0:
        raise ValueError("Lỗi an toàn: Nguồn entropy IKM không được rỗng hoặc None.")

    if salt is None or len(salt) == 0:
        salt = b"\x00" * 32

    h = hmac.HMAC(salt, hashes.SHA256())
    h.update(ikm)
    prk = h.finalize()
    return prk


# ==============================================================================
# PHẦN 2: PHỤ TRÁCH BỞI LÊ MINH KHÔI (TV2)
# ==============================================================================

def build_info_string(plane: str, label: str, key_id: str, length: int) -> bytes:
    if not plane or not label or not key_id:
        raise ValueError("Lỗi an toàn: Các tham số ngữ cảnh (plane, label, key_id) không được rỗng.")
    if length <= 0:
        raise ValueError("Lỗi an toàn: Độ dài khóa yêu cầu phải lớn hơn 0.")

    plane_bytes = plane.encode("utf-8")
    label_bytes = label.encode("utf-8")
    key_id_bytes = str(key_id).encode("utf-8")
    length_bytes = f"{length:02d}".encode("utf-8")

    return (
        PROTOCOL_PREFIX
        + b"||" + plane_bytes
        + b"||" + label_bytes
        + b"||" + key_id_bytes
        + b"||" + length_bytes
    )


def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    if prk is None or len(prk) < 32:
        raise ValueError("Lỗi an toàn: Khóa giả ngẫu nhiên PRK phải có độ dài tối thiểu 32 bytes.")
    if length <= 0 or length > 255 * 32:
        raise ValueError(f"Lỗi an toàn: Độ dài đầu ra L ({length} bytes) phải nằm trong khoảng [1, 8160] bytes.")

    if info is None:
        info = b""

    hkdf = HKDFExpand(
        algorithm=hashes.SHA256(),
        length=length,
        info=info,
    )
    return hkdf.derive(prk)


def derive_session_keys(prk: bytes) -> Dict[str, bytes]:
    return {
        "K_control": hkdf_expand(prk, build_info_string("CONTROL-PLANE", "ctrl-aes-gcm-key", "ctrl-01", 32), 32),
        "K_send": hkdf_expand(prk, build_info_string("DATA-PLANE", "client-write-enc", "data-tx-01", 32), 32),
        "K_recv": hkdf_expand(prk, build_info_string("DATA-PLANE", "server-write-enc", "data-rx-01", 32), 32),
        "K_audit": hkdf_expand(prk, build_info_string("AUDIT-PLANE", "session-audit-mac", "audit-01", 32), 32),
        "K_export": hkdf_expand(prk, build_info_string("EXPORT-PLANE", "session-export-key", "export-01", 32), 32),
    }