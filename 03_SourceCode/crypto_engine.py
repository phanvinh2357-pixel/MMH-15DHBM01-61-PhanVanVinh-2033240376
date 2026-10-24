from typing import Tuple, Dict
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand

PROTOCOL_PREFIX = b"HUIT-SEC-V1"


# ============================================================================
# PHẦN 1: PHỤ TRÁCH BỞI PHAN VĂN VINH (TV1)
# ============================================================================

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


# ============================================================================
# PHẦN 2: PHỤ TRÁCH BỞI LÊ MINH KHÔI (TV2)
# ============================================================================

def build_info_string(plane: str, label: str, key_id: str, length: int) -> bytes:
    raise NotImplementedError("Lê Minh Khôi cần hiện thực hàm tạo chuỗi ngữ cảnh info.")


def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    raise NotImplementedError("Lê Minh Khôi cần hiện thực hàm mở rộng HKDF-Expand.")


def derive_session_keys(prk: bytes) -> Dict[str, bytes]:
    raise NotImplementedError("Lê Minh Khôi cần hiện thực hàm dẫn xuất tập khóa phiên.")