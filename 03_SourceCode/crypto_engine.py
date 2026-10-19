from typing import Tuple, Dict
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand

PROTOCOL_PREFIX = b"HUIT-SEC-V1"


# ============================================================================
# PHẦN 1: PHỤ TRÁCH BỞI PHAN VĂN VINH (TV1)
# ============================================================================

def generate_ecdh_keypair() -> Tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
    raise NotImplementedError("Phan Văn Vinh cần hiện thực hàm sinh cặp khóa ECDH P-256.")


def compute_shared_secret(private_key: ec.EllipticCurvePrivateKey, 
                          peer_public_key: ec.EllipticCurvePublicKey) -> bytes:
    raise NotImplementedError("Phan Văn Vinh cần hiện thực hàm tính bí mật chia sẻ Z.")


def hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    raise NotImplementedError("Phan Văn Vinh cần hiện thực hàm trích xuất HKDF-Extract.")


# ============================================================================
# PHẦN 2: PHỤ TRÁCH BỞI LÊ MINH KHÔI (TV2)
# ============================================================================

def build_info_string(plane: str, label: str, key_id: str, length: int) -> bytes:
    raise NotImplementedError("Lê Minh Khôi cần hiện thực hàm tạo chuỗi ngữ cảnh info.")


def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    raise NotImplementedError("Lê Minh Khôi cần hiện thực hàm mở rộng HKDF-Expand.")


def derive_session_keys(prk: bytes) -> Dict[str, bytes]:
    raise NotImplementedError("Lê Minh Khôi cần hiện thực hàm dẫn xuất tập khóa phiên.")