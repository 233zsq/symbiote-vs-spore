"""Package the saved, audited v1 world as a template, without any game/mod jars."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".map-work"
OUT = ROOT / "artifacts/maps"


def main():
    audit = json.loads((OUT / "world-audit.json").read_text(encoding="utf-8"))
    result = json.loads((WORK / "build-result.json").read_text(encoding="utf-8"))
    layout = json.loads((WORK / "layout.json").read_text(encoding="utf-8"))
    if audit["inside_chunks"] != audit["expected_chunks"] or audit["statuses"] != {"minecraft:full": audit["expected_chunks"]}:
        raise ValueError("Incomplete generated world")
    if audit["road_missing"] or audit["bed_parts_missing"] or audit["bed_parts_checked"] != 12 or audit["map_residents"] != 3:
        raise ValueError("Map block/entity checks are incomplete")
    if result["server_exit_code"] or len(result["completed_jobs"]) != result["expected_jobs"]:
        raise ValueError("Map build was not completed and stopped cleanly")
    if (WORK / "repair-jobs.json").exists():
        repairs = json.loads((WORK / "repair-result.json").read_text(encoding="utf-8"))
        if repairs["server_exit_code"] or len(repairs["completed_jobs"]) != repairs["expected_jobs"]:
            raise ValueError("Repairs are incomplete")
    world = WORK / "server" / layout["id"]
    target = OUT / "svs-first-light-v1-world.zip"
    excluded = {"session.lock", "level.dat_old"}
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=5) as archive:
        for path in sorted(world.rglob("*")):
            if not path.is_file() or path.name in excluded:
                continue
            rel = path.relative_to(world)
            if rel.parts[0] in {"playerdata", "stats", "advancements"}:
                continue
            # Build commands stay in the source kit, not the playable template.
            if rel.parts[:5] == ("datapacks", "svs_map_v1", "data", "svs_map", "functions"):
                continue
            archive.write(path, str(Path(layout["id"]) / rel))
    with target.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    locks = json.loads((WORK / "source-audit.json").read_text(encoding="utf-8"))["locks"]
    files = []
    for mod in locks:
        path = WORK / "cache" / mod["filename"]
        with path.open("rb") as handle:
            sha1 = hashlib.file_digest(handle, "sha1").hexdigest()
        files.append({"path": "mods/"+mod["filename"], "hashes": {"sha1": sha1, "sha512": mod["sha512"]},
                      "env": {"client": "required", "server": "required"},
                      "downloads": [mod["source"]], "fileSize": path.stat().st_size})
    pack_index = {"formatVersion": 1, "game": "minecraft", "versionId": "first-light-v1",
                  "name": "SvS 初行地图 v1（独立试玩）", "summary": "借火村、坠星坡、失联医院与砂谷遗迹地图小样",
                  "files": files, "dependencies": {"minecraft": "1.20.1", "forge": "47.4.23"}}
    pack = OUT / "svs-first-light-v1.mrpack"
    with zipfile.ZipFile(pack, "w", zipfile.ZIP_DEFLATED, compresslevel=5) as archive:
        archive.writestr("modrinth.index.json", json.dumps(pack_index, ensure_ascii=False, indent=2)+"\n")
        with zipfile.ZipFile(target) as world_zip:
            for entry in world_zip.infolist():
                archive.writestr("overrides/saves/"+entry.filename, world_zip.read(entry.filename))
        archive.writestr("overrides/地图试玩说明.txt", "借火者之路 · 初行地图 v1\n\n在世界列表选择 svs_first_light_v1 进入。\n营地可休息整备；沿路标寻找坠星坡、失联医院和砂谷遗迹。\n本版是独立地图小样，主线任务与完整整包平衡尚未接入。\n")
    with pack.open("rb") as handle:
        pack_hash = hashlib.file_digest(handle, "sha256").hexdigest()
    report = {"world_zip": target.name, "bytes": target.stat().st_size, "sha256": digest,
              "mrpack": {"file": pack.name, "bytes": pack.stat().st_size, "sha256": pack_hash},
              "layout": layout, "source_lock": locks,
              "verified": {"full_chunks": audit["inside_chunks"], "road_samples": audit["road_checks"], "bed_parts": audit["bed_parts_checked"], "residents": audit["map_residents"]},
              "not_verified": ["玩家客户端视觉与战斗手感", "共生体融合交互", "灾变Boss召唤/掉落", "完整整合包兼容与FTB任务", "指南针/locate导航", "感染长期扩散与围城"]}
    (OUT / "release-manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    shutil.copy2(WORK / "layout.json", ROOT / "maps/first-light-v1/layout.generated.json")
    print(json.dumps({k: report[k] for k in ["world_zip", "bytes", "sha256", "verified"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
