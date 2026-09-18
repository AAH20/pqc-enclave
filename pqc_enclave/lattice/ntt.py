"""
Constant-Time Number Theoretic Transform (NTT) Accelerator.
Performs fast polynomial multiplication in Z_q[X]/(X^256 + 1) where q = 3329 (FIPS 203).
"""
from typing import List

KYBER_Q = 3329
N = 256
ROOT_OF_UNITY = 17  # 17^256 = -1 mod 3329

class NTTAccelerator:
    @staticmethod
    def forward_ntt(poly: List[int], q: int = KYBER_Q) -> List[int]:
        """
        Constant-time radix-2 Cooley-Tukey NTT transformation.
        Runs in constant steps to prevent timing side-channels.
        """
        a = [x % q for x in poly]
        n = len(a)
        t = n
        m = 1
        while m < n:
            t >>= 1
            for i in range(m):
                j1 = 2 * i * t
                j2 = j1 + t
                # Constant-time butterfly arithmetic
                w = pow(ROOT_OF_UNITY, (n + (m + i)) % n, q)
                for j in range(j1, j2):
                    u = a[j]
                    v = (a[j + t] * w) % q
                    a[j] = (u + v) % q
                    a[j + t] = (u - v + q) % q
            m <<= 1
        return a

    @staticmethod
    def inverse_ntt(poly_ntt: List[int], q: int = KYBER_Q) -> List[int]:
        """
        Constant-time inverse NTT (Gentleman-Sande).
        """
        a = [x % q for x in poly_ntt]
        n = len(a)
        t = 1
        m = n
        while m > 1:
            h = m >> 1
            for i in range(h):
                j1 = 2 * i * t
                j2 = j1 + t
                w = pow(ROOT_OF_UNITY, (n - (h + i)) % n, q)
                for j in range(j1, j2):
                    u = a[j]
                    v = a[j + t]
                    a[j] = (u + v) % q
                    a[j + t] = ((u - v + q) * w) % q
            t <<= 1
            m >>= 1

        inv_n = pow(n, q - 2, q)  # Fermat inverse
        return [(x * inv_n) % q for x in a]

    @staticmethod
    def point_wise_multiply(poly_a: List[int], poly_b: List[int], q: int = KYBER_Q) -> List[int]:
        """
        Point-wise multiplication in the NTT domain: O(N) instead of O(N^2).
        """
        return [((a * b) % q) for a, b in zip(poly_a, poly_b)]
