#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tarfile, time
from pathlib import Path

def human(n: int) -> str:
    for u in ["B","KB","MB","GB","TB"]:
        if n < 1024:
            return f"{n:.2f} {u}"
        n /= 1024
    return f"{n:.2f} PB"

def make_tar_xz(out_path: Path, files, lzma):
    # 依檔案大小由大到小（讓字典先被大檔「養」起來）
    files = [p for p in files if p.exists() and p.is_file()]
    files.sort(key=lambda p: p.stat().st_size, reverse=True)
    if not files:
        return None, 0.0
    t0 = time.time()
    with lzma.open(out_path, "wb",
                   format=lzma.FORMAT_XZ,
                   check=lzma.CHECK_CRC64,
                   preset=(9 | lzma.PRESET_EXTREME)) as xz:
        with tarfile.open(fileobj=xz, mode="w") as tar:
            for p in files:
                tar.add(str(p), arcname=p.name)
    return out_path.stat().st_size, (time.time() - t0)

def main():
    # 動態載入 lzma（避免直接 import）
    lzma = __import__('lzma')

    base = Path(__file__).resolve().parent
    out_dir = base / "compress_file"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 四個原始檔（與你既有專案一致）
    cn_files = [base/"西遊記.txt", base/"歌詞_黃金甲.txt"]
    en_files = [base/"PeterPan.txt", base/"Lyrics_GangNamStyle.txt"]

    # 計算原始大小（只計存在的檔）
    all_inputs = [p for p in (cn_files + en_files) if p.exists() and p.is_file()]
    if not all_inputs:
        print("No input files found next to this script.")
        print("Expected: Lyrics_GangNamStyle.txt, PeterPan.txt, 西遊記.txt, 歌詞_黃金甲.txt")
        return

    original_total = sum(p.stat().st_size for p in all_inputs)
    cn_original = sum(p.stat().st_size for p in cn_files if p.exists())
    en_original = sum(p.stat().st_size for p in en_files if p.exists())

    # 產出兩個檔：texts_cn.tar.xz、texts_en.tar.xz
    cn_out = out_dir / "texts_cn.tar.xz"
    en_out = out_dir / "texts_en.tar.xz"

    cn_size, cn_time = make_tar_xz(cn_out, cn_files, lzma)
    en_size, en_time = make_tar_xz(en_out, en_files, lzma)

    # 輸出結果
    print("=== Compression Summary (lossless, solid, preset=9|EXTREME) ===")
    print(f"Original total : {human(original_total)}")

    if cn_size is not None:
        cn_ratio_all = (cn_size / original_total * 100.0) if original_total else 100.0
        cn_ratio_grp = (cn_size / cn_original * 100.0) if cn_original else 100.0
        print(f"CN  -> {cn_out.name:16} {human(cn_size)}"
              f"  | vs ALL: {cn_ratio_all:.2f}%  vs CN-only: {cn_ratio_grp:.2f}%"
              f"  (time {cn_time:.2f}s)")
    else:
        print("CN  -> (no CN files present, skipped)")

    if en_size is not None:
        en_ratio_all = (en_size / original_total * 100.0) if original_total else 100.0
        en_ratio_grp = (en_size / en_original * 100.0) if en_original else 100.0
        print(f"EN  -> {en_out.name:16} {human(en_size)}"
              f"  | vs ALL: {en_ratio_all:.2f}%  vs EN-only: {en_ratio_grp:.2f}%"
              f"  (time {en_time:.2f}s)")
    else:
        print("EN  -> (no EN files present, skipped)")

    produced = [s for s in [cn_size, en_size] if s is not None]
    if produced:
        split_sum = sum(produced)
        split_ratio_all = split_sum / original_total * 100.0
        print(f"Split total    : {human(split_sum)}  | vs ALL: {split_ratio_all:.2f}%")
    else:
        print("No archives produced.")

if __name__ == "__main__":
    main()
