
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, struct, time
from pathlib import Path

MAGIC = b"ALZ2"   # special marker (different from prior ALZW)
VERSION = 2

BANNER = "[PURE-ALGO-LZW]"

def iter_file_bytes(paths):
    for p in paths:
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1<<20), b""):
                for b in chunk:
                    yield b

def lzw_compress_stream(byte_iter, write_code):
    dict_map = {bytes([i]): i for i in range(256)}
    next_code = 256
    max_code = 65535
    w = b""
    for b in byte_iter:
        k = bytes([b])
        wk = w + k
        if wk in dict_map:
            w = wk
        else:
            write_code(dict_map[w])
            if next_code <= max_code:
                dict_map[wk] = next_code
                next_code += 1
            w = k
    if w:
        write_code(dict_map[w])

def main():
    base = Path(__file__).resolve().parent
    # fixed inputs (same four names as LZMA task), skip if missing
    candidates = [
        base / "Lyrics_GangNamStyle.txt",
        base / "PeterPan.txt",
        base / "西遊記.txt",
        base / "歌詞_黃金甲.txt",
    ]
    files = [p for p in candidates if p.exists() and p.is_file()]
    if not files:
        print(BANNER, "No input files found next to this script."); return

    out_dir = base / "compress_file"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "texts_ALGO.alzw"  # distinct name

    t0 = time.time()
    with open(out_path, "wb") as out_f:
        # Header: MAGIC | ver | file_count
        out_f.write(MAGIC)
        out_f.write(bytes([VERSION]))
        out_f.write(struct.pack(">H", len(files)))
        # file table
        for p in files:
            name_b = p.name.encode("utf-8")
            out_f.write(struct.pack(">H", len(name_b)))
            out_f.write(name_b)
            out_f.write(struct.pack(">Q", p.stat().st_size))

        # codes are fixed 16-bit big-endian
        def write_code(code:int):
            out_f.write(struct.pack(">H", code))

        lzw_compress_stream(iter_file_bytes(files), write_code)

    elapsed = time.time() - t0
    original_bytes = sum(p.stat().st_size for p in files)
    archive_bytes = out_path.stat().st_size
    ratio = (archive_bytes / original_bytes * 100.0) if original_bytes else 100.0

    print(BANNER, "Compressed ->", out_path)
    print(BANNER, f"Original  : {original_bytes} bytes")
    print(BANNER, f"Archive   : {archive_bytes} bytes")
    print(BANNER, f"Ratio     : {ratio:.2f}%")
    print(BANNER, f"Time      : {elapsed:.2f}s")

if __name__ == "__main__":
    main()
