# -*- coding: utf-8 -*-
"""export_mrpack.py · 仓库 → PCL 可导入的 .mrpack（Modrinth 整合包格式）

- files[]：Modrinth 渠道模组（pw.toml 里的 url+sha512+size）
- overrides/：CF 渠道 jar（本地实证）+ config/kubejs/scripts/defaultconfigs/resourcepacks/options.txt
- 产物：E:\\mcmp_test\\dist\\<name>-<version>.mrpack（zip 格式）

用法：python tools/export_mrpack.py [--out 目录] [--name 包名] [--version 版本]
"""
import argparse, hashlib, json, os, re, shutil, zipfile
from pathlib import Path

PACK = Path(r"E:\mcmp")
INSTANCE = Path(r"C:\PCL 正式版 2.8.13\.minecraft\versions\1.20.1-forge-47.4.23")
DIST = Path(r"E:\mcmp_test\dist")

# 随包分发的资源包（实例 resourcepacks 里启用的三件；IF 素材授权见 HANDOVER 待办）
RP_ZIPS = ["IMF-Trans.zip", "IMF-Trail.zip", "epicfightx_better_trail1.5.zip"]

# overrides/config 里排除的运行时噪音
CONFIG_EXCLUDE = {"fml.toml", "embeddium-fingerprint.json", "flywheel-client.toml"}


def parse_pw(p):
    t = p.read_text(encoding="utf-8")
    g = lambda k: (re.search(rf'^{k}\s*=\s*"([^"]*)"', t, re.MULTILINE) or [None, ""])[1]
    return {
        "name": g("name") or p.stem,
        "filename": g("filename"),
        "url": g("url"),
        "hash": g("hash"),
        "mr": "cdn.modrinth.com" in g("url"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DIST)
    ap.add_argument("--name", default="Symbiote vs Spore")
    ap.add_argument("--version", default="0.1.0")
    args = ap.parse_args()

    stage = args.out / "_stage"
    if stage.exists():
        shutil.rmtree(stage)
    ov = stage / "overrides"
    (ov / "mods").mkdir(parents=True)

    files = []
    bundled = []
    for p in sorted((PACK / "mods").glob("*.pw.toml")):
        e = parse_pw(p)
        if not e["filename"]:
            continue
        if e["mr"]:
            src = INSTANCE / "mods" / e["filename"]
            size = src.stat().st_size if src.exists() else 0
            files.append({
                "path": "mods/" + e["filename"],
                "hashes": {"sha512": e["hash"], "sha1": ""},
                "env": {"client": "required", "server": "required"},
                "downloads": [e["url"]],
                "fileSize": size,
            })
        else:
            src = INSTANCE / "mods" / e["filename"]
            if src.exists():
                shutil.copy2(src, ov / "mods" / e["filename"])
                bundled.append(e["filename"])
            else:
                print("[WARN] CF jar 缺失:", e["filename"])

    # config / kubejs / scripts / defaultconfigs → overrides
    for sub in ("config", "kubejs", "scripts", "defaultconfigs"):
        src = PACK / sub
        if not src.is_dir():
            continue
        for f in src.rglob("*"):
            if not f.is_file():
                continue
            rel = f.relative_to(PACK)
            if rel.parts[0] == "config" and f.name in CONFIG_EXCLUDE:
                continue
            if ".gitkeep" == f.name:
                continue
            # if_borrowed 平铺进 config 根（IF 调优生效层）
            if rel.parts[:2] == ("config", "if_borrowed"):
                rel = Path("config") / f.name
            dst = ov / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)

    # 资源包（实例目录取）
    (ov / "resourcepacks").mkdir(exist_ok=True)
    for z in RP_ZIPS:
        src = INSTANCE / "resourcepacks" / z
        if src.exists():
            shutil.copy2(src, ov / "resourcepacks" / z)
        else:
            print("[WARN] 资源包缺失:", z)

    # options.txt（实例现行：中文+资源包启用+键位）
    opt = INSTANCE / "options.txt"
    if opt.exists():
        shutil.copy2(opt, ov / "options.txt")

    # modrinth.index.json
    index = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": args.version,
        "name": args.name,
        "summary": "以共生对寄生——Epic Fight 动作战斗 × Symbiote 共生养成 × Fungal Infection: Spore 真菌天灾",
        "files": files,
        "dependencies": {"minecraft": "1.20.1", "forge-loader": "47.4.23"},
    }
    (stage / "modrinth.index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    # 打 zip（.mrpack）
    outzip = args.out / ("%s-%s.mrpack" % (args.name.replace(" ", ""), args.version))
    if outzip.exists():
        outzip.unlink()
    with zipfile.ZipFile(outzip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        zf.write(stage / "modrinth.index.json", "modrinth.index.json")
        for f in ov.rglob("*"):
            if f.is_file():
                zf.write(f, "overrides/" + str(f.relative_to(ov)).replace("\\", "/"))
    mb = outzip.stat().st_size / 1048576
    print("[OK] %s | Modrinth 渠道 %d 件 + CF 打进 %d 件 | %.1f MB" % (outzip.name, len(files), len(bundled), mb))
    shutil.rmtree(stage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
