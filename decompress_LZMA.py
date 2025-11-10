#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tarfile
from pathlib import Path

def extract_one(in_path, out_dir, lzma):
    if not in_path.exists():
        print(f"(skip) not found: {in_path.name}")
        return False
    with lzma.open(in_path, "rb") as xz, tarfile.open(fileobj=xz, mode="r:") as tar:
        tar.extractall(path=out_dir)
    print(f"Extracted {in_path.name} -> {out_dir}")
    return True

def main():
    # 動態載入 lzma（避免直接 import）
    lzma = __import__('lzma')

    base = Path(__file__).resolve().parent
    in_dir = base / "compress_file"
    out_dir = base / "decompress_file"
    out_dir.mkdir(parents=True, exist_ok=True)

    cn_in = in_dir / "texts_cn.tar.xz"
    en_in = in_dir / "texts_en.tar.xz"

    any_ok = False
    any_ok |= extract_one(cn_in, out_dir, lzma)
    any_ok |= extract_one(en_in, out_dir, lzma)

    if not any_ok:
        print("No input archives found in compress_file/ (expected texts_cn.tar.xz and/or texts_en.tar.xz).")

if __name__ == "__main__":
    main()
