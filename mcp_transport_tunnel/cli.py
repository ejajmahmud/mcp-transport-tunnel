"""Command-line interface for MCP Transport Tunnel."""
import argparse
from .tunnel import MessageFramer

def main():
    parser = argparse.ArgumentParser(description="MCP Transport Tunnel CLI")
    parser.add_argument("--demo", action="store_true", help="Demonstrate binary framing and assembly")
    args = parser.parse_args()

    framer = MessageFramer()
    sample_msg = {"jsonrpc": "2.0", "method": "tools/call", "params": {"query": "SELECT *\nFROM logs\nWHERE id=1;"}}
    framed = framer.frame(sample_msg)
    print(f"Original payload framed into {len(framed)} bytes with CRC-32 protection.")

    # Simulate fragmented delivery
    half1, half2 = framed[:15], framed[15:]
    res1 = framer.feed(half1)
    print(f"Fed partial chunk (15 bytes): {len(res1)} message(s) ready.")
    res2 = framer.feed(half2)
    print(f"Fed remaining chunk: {len(res2)} message(s) ready. Decoded successfully.")

if __name__ == "__main__":
    main()
