#!/usr/bin/env python3
"""sync_mods.py · 仓库 → 游戏实例的模组同步

按 mods/*.pw.toml 元数据把模组 jar 同步进实例 mods/ 目录：
逐个读取 download.url / hash，已存在且 sha512 一致的跳过，
缺失或不一致的一律经 `curl --http1.1 --retry` 下载（Java/okhttp 的
HTTP/2 会被本机代理掐断，见 docs/HANDOVER.md 环境拓扑），校验哈希后落位。

同时反向检查实例 mods/ 里是否存在没有 .pw.toml 对应的"野 jar"
（绕开 packwiz 手工放入的模组会让实例与仓库脱节，只警告不删除）。

用法：
    python tools/sync_mods.py                      # 同步到默认开发实例
    python tools/sync_mods.py --instance <实例目录>  # 指定其他实例
    python tools/sync_mods.py --dry-run            # 只报告差异，不下载

默认实例：D:\\mcmp_test\\versions\\1.20.1-Forge_47.4.23（可用 --instance 覆盖）
仅限标准库，兼容 Python 3.8+（开发机基线 3.13）。
"""

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_INSTANCE = Path(r"D:\mcmp_test\versions\1.20.1-Forge_47.4.23")

try:
    import tomllib  # Python 3.11+

    def parse_pw_toml(path):
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
        dl = data.get("download", {})
        return {
            "name": data.get("name", path.stem),
            "filename": data.get("filename", ""),
            "url": dl.get("url", ""),
            "hash": dl.get("hash", ""),
            "hash_format": dl.get("hash-format", "sha512"),
        }

except ImportError:  # 无 tomllib 的老版本 Python：按行提取（packwiz 生成格式稳定）

    def parse_pw_toml(path):
        text = path.read_text(encoding="utf-8")
        def grab(key):
            m = re.search(rf'^{key}\s*=\s*"([^"]*)"', text, re.MULTILINE)
            return m.group(1) if m else ""
        return {
            "name": grab("name") or path.stem,
            "filename": grab("filename"),
            "url": grab("url"),
            "hash": grab("hash"),
            "hash_format": grab("hash-format") or "sha512",
        }


def file_hash(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest):
    # 本机代理会掐 HTTP/2 大文件下载，必须 --http1.1（见 HANDOVER 踩坑记录）
    cmd = [
        "curl", "--http1.1", "-fSL",
        "--retry", "3", "--retry-delay", "2", "--retry-all-errors",
        "-o", str(dest), url,
    ]
    return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


def main():
    ap = argparse.ArgumentParser(description="按 mods/*.pw.toml 同步模组 jar 到实例")
    ap.add_argument("--pack", type=Path, default=Path("."), help="packwiz 仓库根（默认当前目录）")
    ap.add_argument("--instance", type=Path, default=DEFAULT_INSTANCE, help="实例目录")
    ap.add_argument("--dry-run", action="store_true", help="只报告差异，不下载")
    args = ap.parse_args()

    pw_dir = args.pack / "mods"
    inst_mods = args.instance / "mods"
    if not pw_dir.is_dir():
        print(f"[FAIL] 未找到 {pw_dir}（请在仓库根执行，或用 --pack 指定）")
        return 1
    if not args.dry_run:
        inst_mods.mkdir(parents=True, exist_ok=True)

    entries = [parse_pw_toml(p) for p in sorted(pw_dir.glob("*.pw.toml"))]
    entries = [e for e in entries if e["url"] and e["filename"]]

    ok = skipped = failed = 0
    expected = set()
    for e in entries:
        dest = inst_mods / e["filename"]
        expected.add(e["filename"].lower())
        algo = e["hash_format"] or "sha512"
        if dest.exists() and file_hash(dest, algo) == e["hash"]:
            skipped += 1
            continue
        if args.dry_run:
            print(f"[DIFF] {e['name']} ({e['filename']}) 缺失或哈希不一致")
            failed += 1
            continue
        part = dest.with_name(dest.name + ".part")
        if not download(e["url"], part):
            print(f"[FAIL] {e['name']} 下载失败: {e['url']}")
            part.unlink(missing_ok=True)
            failed += 1
            continue
        actual = file_hash(part, algo)
        if actual != e["hash"]:
            print(f"[FAIL] {e['name']} 哈希不一致（期望 {e['hash'][:16]}… 实得 {actual[:16]}…）")
            part.unlink(missing_ok=True)
            failed += 1
            continue
        part.replace(dest)
        ok += 1
        print(f"[ OK ] {e['name']} -> {e['filename']}")

    strays = []
    if inst_mods.is_dir():
        for jar in sorted(inst_mods.glob("*.jar")):
            if jar.name.lower() not in expected:
                strays.append(jar.name)
                print(f"[WARN] 实例存在无元数据对应的野 jar（请走 packwiz 入包）: {jar.name}")

    if args.dry_run:
        print(f"sync_mods(dry-run): 元数据 {len(entries)} 条，待同步 {failed} 个，已就位 {skipped} 个")
        return 1 if failed else 0
    print(f"sync_mods: 新同步 {ok} 个，已就位跳过 {skipped} 个，失败 {failed} 个，野 jar 警告 {len(strays)} 个")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
