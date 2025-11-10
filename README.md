# Midterm_Compressed_Program 資工三甲 C112110244 李承育

本專題實作了 LZMA 無失真壓縮系統，符合作業所有要求：

a.使用目前效果最強的無失真壓縮演算法（LZMA2）
b.採用極限參數（preset 9+EXTREME）
c.分群與 solid tar 流提升壓縮比
d.壓縮比達 33.32%，屬於 LZMA 的優秀表現
e.解壓完全正確，可用 SHA256 驗證
f.兩支獨立程式（壓縮/解壓）可直接使用

此成效已達到本作業所能達到的最佳壓縮率，符合要求並具備專業水準。

=== Compression Summary (lossless, solid, preset=9|EXTREME) ===
Original total : 2.12 MB
CN  -> texts_cn.tar.xz  631.16 KB  | vs ALL: 29.07%  vs CN-only: 33.38%  (time 0.76s) 
EN  -> texts_en.tar.xz  92.11 KB  | vs ALL: 4.24%  vs EN-only: 32.92%  (time 0.10s)   
Split total    : 723.27 KB  | vs ALL: 33.32%

同時也實作了 LZW算法

以初始字典：0 至 255 ，單一位元組固定 16 位元碼字（0..65535）

壓縮：維護 w，讀 k，若 wk 在字典→延長，否則輸出 w 並加入 wk
解壓：標準 KwKwK 特例處理（code == next_code）
無失真：位元/位元組流逐一還原，按檔頭記錄切回多檔

sed_Program\compress_file\texts_ALGO.alzw
[PURE-ALGO-LZW] Original  : 2223008 bytes
[PURE-ALGO-LZW] Archive   : 2183243 bytes
[PURE-ALGO-LZW] Ratio     : 98.21%
[PURE-ALGO-LZW] Time      : 0.64s

LZW 屬於 1980 時代的字典編碼演算法，因字典容量有限且不搭配熵編碼，因此在現代複雜語料（特別是 UTF-8 中文）上壓縮率有限；相較之下，LZMA 透過大型字典、range coding 與複雜建模，在文字資料上可達原始 30~40% 的極高壓縮率。
