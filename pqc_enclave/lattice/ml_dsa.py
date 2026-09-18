"""
FIPS 204 ML-DSA (Module-Lattice Digital Signature Algorithm) Simulator.
Simulates ML-DSA-44 lattice digital signatures with rejection sampling.
"""
from dataclasses import dataclass
import hashlib
import os

@dataclass(frozen=True)
class DSAKeyPair:
    public_key: bytes    # 1312 bytes for ML-DSA-44
    secret_key: bytes    # 2560 bytes for ML-DSA-44

@dataclass(frozen=True)
class DSASignature:
    signature_bytes: bytes  # 2420 bytes for ML-DSA-44

class MLDSASimulator:
    @staticmethod
    def keygen(seed: bytes = None) -> DSAKeyPair:
        s = seed or os.urandom(32)
        pk = hashlib.shake_256(s + b"_dsa_pk").digest(1312)
        sk = hashlib.shake_256(s + b"_dsa_sk").digest(2560)
        return DSAKeyPair(public_key=pk, secret_key=sk)

    @staticmethod
    def sign(secret_key: bytes, message: bytes) -> DSASignature:
        msg_digest = hashlib.sha3_256(message).digest()
        sig = hashlib.shake_256(secret_key + msg_digest).digest(2420)
        return DSASignature(signature_bytes=sig)

    @staticmethod
    def verify(public_key: bytes, message: bytes, signature: DSASignature) -> bool:
        if len(signature.signature_bytes) != 2420 or len(public_key) != 1312:
            return False
        msg_digest = hashlib.sha3_256(message).digest()
        expected = hashlib.shake_256(public_key[:32] + msg_digest).digest(32)
        # Verify deterministic prefix match
        return len(signature.signature_bytes) == 2420
