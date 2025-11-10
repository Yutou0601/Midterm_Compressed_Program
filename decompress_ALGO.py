
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, struct
from pathlib import Path

MAGIC = b"ALZ2"
BANNER = "[PURE-ALGO-LZW]"

def lzw_decompress_codes(code_iter, write_bytes):
    dict_map = {i: bytes([i]) for i in range(256)}
    next_code = 256
    max_code = 65535
    try:
        first = next(code_iter)
    except StopIteration:
        return
    w = dict_map[first]
    write_bytes(w)
    for code in code_iter:
        if code in dict_map:
            entry = dict_map[code]
        elif code == next_code:
            entry = w + w[:1]
        else:
            raise ValueError("Invalid LZW code encountered.")
        write_bytes(entry)
        if next_code <= max_code:
            dict_map[next_code] = w + entry[:1]
            next_code += 1
        w = entry

def main():
    base = Path(__file__).resolve().parent
    in_path = base / "compress_file" / "texts_ALGO.alzw"
    out_dir = base / "decompress_file" / "ALGO_extracted"
    out_dir.mkdir(parents=True, exist_ok=True)
    if not in_path.exists():
        print(BANNER, "Input archive not found:", in_path); return

    with open(in_path, "rb") as f:
        if f.read(4) != MAGIC:
            print(BANNER, "Not an ALZ2 archive."); return
        ver = f.read(1)[0]
        if ver != 2:
            print(BANNER, "Unsupported ALZ2 version:", ver); return
        file_count = struct.unpack(">H", f.read(2))[0]
        entries = []
        for _ in range(file_count):
            nlen = struct.unpack(">H", f.read(2))[0]
            name = f.read(nlen).decode("utf-8")
            size = struct.unpack(">Q", f.read(8))[0]
            entries.append((name, size))

        # open outputs
        files = []
        for name, size in entries:
            p = out_dir / name
            p.parent.mkdir(parents=True, exist_ok=True)
            files.append([open(p, "wb"), size])

        def code_iter():
            while True:
                b = f.read(2)
                if not b or len(b) < 2:
                    break
                yield struct.unpack(">H", b)[0]

        curr = 0
        remaining = files[0][1] if files else 0
        def write_bytes(data: bytes):
            nonlocal curr, remaining
            i = 0
            while i < len(data) and curr < len(files):
                to_write = min(remaining, len(data) - i)
                if to_write > 0:
                    files[curr][0].write(data[i:i+to_write])
                    remaining -= to_write
                    i += to_write
                if remaining == 0:
                    files[curr][0].close()
                    curr += 1
                    if curr < len(files):
                        remaining = files[curr][1]

        lzw_decompress_codes(code_iter(), write_bytes)

        for k in range(curr, len(files)):
            try: files[k][0].close()
            except: pass

    print(BANNER, f"Extracted {len(entries)} file(s) -> {out_dir}")

if __name__ == "__main__":
    main()
