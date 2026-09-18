import unittest
from pqc_enclave.lattice.ntt import NTTAccelerator
from pqc_enclave.lattice.ml_kem import MLKEMSimulator
from pqc_enclave.lattice.ml_dsa import MLDSASimulator
from pqc_enclave.tunnel.quantum_tunnel import QuantumSafeTelemetryTunnel

class TestPQCEnclave(unittest.TestCase):
    def test_ntt_invertibility(self):
        poly = [i % 3329 for i in range(256)]
        ntt_fwd = NTTAccelerator.forward_ntt(poly)
        poly_rec = NTTAccelerator.inverse_ntt(ntt_fwd)
        self.assertEqual(len(poly_rec), 256)
        # Check reconstruction
        for orig, rec in zip(poly, poly_rec):
            self.assertEqual(orig, rec)

    def test_ml_kem_sizes_and_decapsulation(self):
        kp = MLKEMSimulator.keygen()
        self.assertEqual(len(kp.public_key_bytes), 1184)
        self.assertEqual(len(kp.secret_key_bytes), 2400)

        ct = MLKEMSimulator.encapsulate(kp.public_key_bytes)
        self.assertEqual(len(ct.ciphertext_bytes), 1088)
        self.assertEqual(len(ct.shared_secret), 32)

        ss_dec = MLKEMSimulator.decapsulate(kp.secret_key_bytes, ct.ciphertext_bytes, kp.public_key_bytes)
        self.assertEqual(len(ss_dec), 32)

    def test_ml_dsa_signature_verification(self):
        kp = MLDSASimulator.keygen()
        msg = b"AUTONOMOUS_SWARM_MISSION_WAYPOINT_7"
        sig = MLDSASimulator.sign(kp.secret_key, msg)
        self.assertEqual(len(sig.signature_bytes), 2420)
        self.assertTrue(MLDSASimulator.verify(kp.public_key, msg, sig))

    def test_quantum_safe_tunnel(self):
        tunnel = QuantumSafeTelemetryTunnel()
        peer_kp = MLKEMSimulator.keygen()
        ct, handshake_ms = tunnel.establish_session(peer_kp.public_key_bytes)
        self.assertTrue(handshake_ms >= 0)

        packet = tunnel.encrypt_telemetry({"alt_m": 120.5, "speed_mps": 25.0})
        self.assertEqual(packet["seq"], 1)
        self.assertIn("auth_tag", packet)
        self.assertTrue(packet["latency_ms"] < 5.0)

if __name__ == "__main__":
    unittest.main()
