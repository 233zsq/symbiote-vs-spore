#!/usr/bin/env python3
"""check_json.py · B 级批量产物入库前 JSON 语法校验

默认递归校验 config/openloader/data/ 与 kubejs/data/ 下全部 .json 文件；
也可追加任意文件或目录参数。发现语法错误时输出 文件:行:列 与错误详情，
并以非零状态码退出。全绿（含零文件）退出码为 0。

用法：
    python tools/check_json.py                      # 校验默认目录
    python tools/check_json.py path/to/a.json dir/  # 追加校验目标

仅限标准库，兼容 Python 3.8+（开发机基线 3.13）。
"""

import json
import sys
from pathlib import Path

DEFAULT_DIRS = [Path("config/openloader/data"), Path("kubejs/data")]


def collect_json_files(paths):
    files = []
    for p in paths:
        if not p.exists():
            continue
        if p.is_dir():
            files.extend(sorted(p.rglob("*.json")))
        elif p.suffix.lower() == ".json":
            files.append(p)
    return files


def main():
    extra = [Path(a) for a in sys.argv[1:]]
    targets = collect_json_files(DEFAULT_DIRS + extra)

    checked = 0
    failures = 0
    for f in targets:
        checked += 1
        try:
            with open(f, "r", encoding="utf-8-sig") as fh:
                json.load(fh)
        except json.JSONDecodeError as e:
            failures += 1
            print(f"[FAIL] {f}:{e.lineno}:{e.colno} {e.msg}")
        except (OSError, UnicodeDecodeError) as e:
            failures += 1
            print(f"[FAIL] {f} 读取失败: {e}")

    if checked == 0:
        print("check_json: 未发现 JSON 文件（目录为空属正常，骨架阶段）")
    else:
        print(f"check_json: 校验 {checked} 个文件，失败 {failures} 个")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
