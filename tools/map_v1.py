"""Reproducible, isolated map-work downloads and source verification (Python 3.11+).

Only writes .map-work/ and artifacts/maps/ under this repository. Game jars are
not committed. Does not install anything in the user's launcher instance.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".map-work"
PLAN_PATH = ROOT / "maps/first-light-v1/plan.json"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(path, algorithm="sha512"):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, algorithm).hexdigest()


def metadata():
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    result = []
    for slug in plan["mod_metadata"]:
        path = ROOT / "mods" / (slug + ".pw.toml")
        mod = tomllib.loads(path.read_text(encoding="utf-8-sig"))
        name = mod["filename"]
        if Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError("Unsafe mod filename: " + name)
        if not mod["download"].get("url", "").startswith("https://"):
            raise ValueError("Missing HTTPS source: " + slug)
        mod["metadata_file"] = str(path.relative_to(ROOT)).replace("\\", "/")
        result.append(mod)
    return result


def download_one(mod, reuse):
    cache = WORK / "cache" / mod["filename"]
    spec = mod["download"]
    algorithm = spec["hash-format"]
    expected = spec["hash"]
    if cache.exists() and digest(cache, algorithm) == expected:
        return cache
    candidate = reuse / mod["filename"] if reuse else None
    if candidate and candidate.is_file() and digest(candidate, algorithm) == expected:
        shutil.copy2(candidate, cache)
        return cache
    part = cache.with_suffix(cache.suffix + ".part")
    subprocess.run([
        "curl.exe", "--http1.1", "--fail", "--location", "--silent",
        "--show-error", "--retry", "2", "--connect-timeout", "15",
        "--max-time", "180", "--output", str(part), spec["url"],
    ], check=True)
    actual = digest(part, algorithm)
    if actual != expected:
        raise ValueError(f"Hash mismatch for {mod['filename']}: {actual}")
    part.replace(cache)
    return cache


def download(args):
    (WORK / "cache").mkdir(parents=True, exist_ok=True)
    mods = metadata()
    errors = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(download_one, mod, args.reuse): mod for mod in mods}
        for future in as_completed(futures):
            mod = futures[future]
            try:
                path = future.result()
                print("VERIFIED", path.name, path.stat().st_size, flush=True)
            except Exception as exc:
                errors.append({"filename": mod["filename"], "error": str(exc)})
                print("FAILED", mod["filename"], str(exc), flush=True)
    write_json(WORK / "download-report.json", {"errors": errors, "requested": len(mods)})
    if errors:
        raise SystemExit(1)


def inspect(_args):
    declarations = {}
    dependencies = []
    structures = {}
    locks = []
    for mod in metadata():
        path = WORK / "cache" / mod["filename"]
        if digest(path, mod["download"]["hash-format"]) != mod["download"]["hash"]:
            raise ValueError("Unverified jar " + path.name)
        with zipfile.ZipFile(path) as jar:
            if "META-INF/mods.toml" in jar.namelist():
                data = tomllib.loads(jar.read("META-INF/mods.toml").decode("utf-8-sig"))
                for entry in data.get("mods", []):
                    declarations[entry["modId"]] = path.name
                for owner, deps in data.get("dependencies", {}).items():
                    for dep in deps:
                        if dep.get("mandatory") and dep.get("side", "BOTH") != "CLIENT":
                            dependencies.append({"owner": owner, **dep})
            for name in jar.namelist():
                parts = name.split("/")
                if len(parts) >= 5 and parts[0] == "data" and parts[2:4] == ["worldgen", "structure"] and name.endswith(".json"):
                    key = parts[1] + ":" + "/".join(parts[4:])[:-5]
                    structures[key] = {"jar": path.name, "path": name}
        locks.append({"filename": path.name, "sha512": digest(path), "source": mod["download"]["url"]})
    missing = [d for d in dependencies if d["modId"] not in declarations and d["modId"] not in {"forge", "minecraft", "java"}]
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    missing_structures = [s["structure"] for s in plan["sites"] if s.get("structure") and s["structure"] not in structures]
    report = {"declarations": declarations, "dependencies": dependencies,
              "missing_dependencies": missing, "missing_structures": missing_structures,
              "structures": {s["structure"]: structures.get(s["structure"]) for s in plan["sites"] if s.get("structure")},
              "locks": locks}
    write_json(WORK / "source-audit.json", report)
    print(json.dumps({k: report[k] for k in ["declarations", "missing_dependencies", "missing_structures", "structures"]}, ensure_ascii=False, indent=2))
    if missing or missing_structures:
        raise SystemExit(1)


def stage(args):
    server = WORK / "server"
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    if (server / plan["id"] / "level.dat").exists():
        raise ValueError("Refusing to re-stage an existing generated world")
    mods_dir = server / "mods"
    mods_dir.mkdir(parents=True, exist_ok=True)
    for mod in metadata():
        cache = WORK / "cache" / mod["filename"]
        if digest(cache, mod["download"]["hash-format"]) != mod["download"]["hash"]:
            raise ValueError("Unverified jar " + cache.name)
        shutil.copy2(cache, mods_dir / cache.name)
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    world = server / plan["id"]
    datapack = world / "datapacks/svs_map_v1"
    datapack.mkdir(parents=True, exist_ok=True)
    write_json(datapack / "pack.mcmeta", {"pack": {"pack_format": 15, "description": "SvS 初行地图 v1 制作工具"}})
    # Targets are placed deliberately. This is a new, isolated world-only pack.
    audit = json.loads((WORK / "source-audit.json").read_text(encoding="utf-8"))
    for key, record in audit["structures"].items():
        with zipfile.ZipFile(WORK / "cache" / record["jar"]) as jar:
            structure = json.loads(jar.read(record["path"]))
        structure["biomes"] = []
        write_json(datapack / record["path"], structure)
    (server / "server.properties").write_text(
        f"level-name={plan['id']}\nlevel-seed={plan['seed']}\n"
        "level-type=minecraft:normal\ngenerate-structures=true\n"
        "server-ip=127.0.0.1\nserver-port=25575\nonline-mode=false\n"
        "enable-rcon=false\nenable-query=false\nview-distance=4\nsimulation-distance=3\n"
        "max-players=2\nmax-tick-time=-1\ngamemode=survival\ndifficulty=normal\n"
        "allow-flight=true\nspawn-protection=0\nmotd=SvS isolated map workshop\n",
        encoding="utf-8")
    (server / "user_jvm_args.txt").write_text("-Xms2G\n-Xmx6G\n-Djava.awt.headless=true\n", encoding="utf-8")
    # RoadWeaver embeds lwjgl-opencl, whose module descriptor needs lwjgl core.
    # The official dedicated-server libraries do not contain the client core.
    core = args.lwjgl_core
    if not core or digest(core, "sha1") != "ae58664f88e18a9bb2c77b063833ca7aaec484cb":
        raise ValueError("Provide verified official lwjgl-3.3.1.jar via --lwjgl-core")
    core_rel = "libraries/org/lwjgl/lwjgl/3.3.1/lwjgl-3.3.1.jar"
    (server / core_rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(core, server / core_rel)
    args_file = server / "libraries/net/minecraftforge/forge/1.20.1-47.4.23/win_args.txt"
    lines = args_file.read_text(encoding="utf-8").splitlines()
    if core_rel not in lines[0]:
        lines[0] += ";" + core_rel
        args_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Staged isolated server:", server)
    print("EULA acceptance is separate and is never set by this tool.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    cmd = commands.add_parser("download")
    cmd.add_argument("--reuse", type=Path)
    cmd.set_defaults(func=download)
    commands.add_parser("inspect").set_defaults(func=inspect)
    cmd = commands.add_parser("stage")
    cmd.add_argument("--lwjgl-core", type=Path, required=True)
    cmd.set_defaults(func=stage)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
