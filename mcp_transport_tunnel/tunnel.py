"""Binary framing and reassembly protocol for robust JSON-RPC communication."""
import struct
import zlib
import json
from typing import List, Tuple, Any

MAGIC = b"\xAA\x55"

class MessageFramer:
    def __init__(self):
        self._buffer = bytearray()

    def frame(self, payload: Any) -> bytes:
        data = json.dumps(payload, separators=(',', ':')).encode("utf-8")
        length = len(data)
        checksum = zlib.crc32(data) & 0xffffffff
        # Format: MAGIC (2B) + Length (4B, big-endian) + CRC32 (4B, big-endian) + Data
        header = struct.pack(">2sII", MAGIC, length, checksum)
        return header + data

    def feed(self, chunk: bytes) -> List[Any]:
        self._buffer.extend(chunk)
        messages = []

        while len(self._buffer) >= 10:
            if self._buffer[:2] != MAGIC:
                # Discard corrupted leading byte and seek next magic header
                del self._buffer[0]
                continue

            magic, length, checksum = struct.unpack(">2sII", self._buffer[:10])
            total_size = 10 + length

            if len(self._buffer) < total_size:
                # Await remaining bytes
                break

            data = bytes(self._buffer[10:total_size])
            actual_crc = zlib.crc32(data) & 0xffffffff

            if actual_crc != checksum:
                # Corrupted frame, discard magic and search forward
                del self._buffer[:2]
                continue

            del self._buffer[:total_size]
            try:
                msg = json.loads(data.decode("utf-8"))
                messages.append(msg)
            except Exception:
                pass

        return messages
