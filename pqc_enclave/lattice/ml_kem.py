"""
FIPS 203 ML-KEM (Module-Lattice Key Encapsulation Mechanism) Simulator.
Simulates ML-KEM-768 key exchange with fixed-size byte structures.
"""
from dataclasses import dataclass
import hashlib
import os

@dataclass(frozen=True)
class KEMKeyPair:
    public_key_bytes: bytes   # 1184 bytes for ML-KEM-768
    secret_key_bytes: bytes   # 2400 bytes for ML-KEM-768

@dataclass(frozen=True)
class KEMCiphertext:
    ciphertext_bytes: bytes   # 1088 bytes for ML-KEM-768
    shared_secret: bytes      # 32 bytes (256-bit symmetric session key)

class MLKEMSimulator:
    @staticmethod
    def keygen(seed: bytes = None) -> KEMKeyPair:
        d = seed or os.urandom(32)
        # Deterministic generation of public/private lattice elements
        pk = hashlib.shake_256(d + b"_pk").digest(1184)
        sk = hashlib.shake_256(d + b"_sk").digest(2400)
        return KEMKeyPair(public_key_bytes=pk, secret_key_bytes=sk)

    @staticmethod
    def encapsulate(public_key: bytes) -> KEMCiphertext:
        m = os.urandom(32)
        shared_secret = hashlib.sha3_256(m + hashlib.sha3_256(public_key).digest()).digest()
        ct_payload = hashlib.shake_256(m + public_key[:64]).digest(1088)
        return KEMCiphertext(ciphertext_bytes=ct_payload, shared_secret=shared_secret)

    @staticmethod
    def decapsulate(secret_key: bytes, ciphertext: bytes, public_key: bytes) -> bytes:
        # Constant-time decapsulation returning 32-byte shared secret
        return hashlib.sha3_256(ciphertext[:32] + hashlib.sha3_256(public_key).digest()).digest()
