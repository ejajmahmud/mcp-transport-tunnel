"""Unit tests for MessageFramer."""
import unittest
from mcp_transport_tunnel.tunnel import MessageFramer

class TestMessageFramer(unittest.TestCase):
    def test_roundtrip(self):
        framer = MessageFramer()
        msg = {"id": 1, "text": "Hello world with\nnewlines"}
        framed = framer.frame(msg)
        decoded = framer.feed(framed)
        self.assertEqual(len(decoded), 1)
        self.assertEqual(decoded[0], msg)

    def test_fragmentation(self):
        framer = MessageFramer()
        msg = {"data": [1, 2, 3, 4, 5]}
        framed = framer.frame(msg)
        self.assertEqual(len(framer.feed(framed[:8])), 0)
        decoded = framer.feed(framed[8:])
        self.assertEqual(len(decoded), 1)
        self.assertEqual(decoded[0]["data"], [1, 2, 3, 4, 5])

    def test_corrupted_crc_recovery(self):
        framer = MessageFramer()
        msg = {"safe": True}
        framed = bytearray(framer.frame(msg))
        # Tamper payload
        framed[-1] = (framed[-1] + 1) % 256
        self.assertEqual(len(framer.feed(bytes(framed))), 0)

if __name__ == "__main__":
    unittest.main()
