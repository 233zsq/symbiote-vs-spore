"""Run explicit map build jobs against the isolated, already prepared Forge server.

Does not accept EULA or install Forge. Leaves all output in .map-work/.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import queue
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".map-work"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java", type=Path, required=True)
    parser.add_argument("--resume", action="store_true", help="Skip previously completed jobs after inspecting a failed attempt")
    parser.add_argument("--phase", choices=["build", "repair"], default="build")
    args = parser.parse_args()
    server = WORK / "server"
    if "eula=true" not in (server / "eula.txt").read_text(encoding="utf-8"):
        raise SystemExit("User EULA acceptance is required")
    phase = args.phase
    result_path, log_path = WORK / (phase+"-result.json"), WORK / (phase+"-console.log")
    jobs = json.loads((WORK / (phase+"-jobs.json")).read_text(encoding="utf-8"))
    previous = {}
    if result_path.exists():
        previous = json.loads(result_path.read_text(encoding="utf-8"))
        if not args.resume or len(previous["completed_jobs"]) == len(jobs):
            raise SystemExit("Build was already attempted. Inspect results before explicitly preparing another run.")
        count = len(list(WORK.glob(phase+"-console-attempt*.log")))+1
        log_path.rename(WORK / f"{phase}-console-attempt{count}.log")
        result_path.rename(WORK / f"{phase}-result-attempt{count}.json")
    process = subprocess.Popen([str(args.java), "@user_jvm_args.txt", "@libraries/net/minecraftforge/forge/1.20.1-47.4.23/win_args.txt", "nogui"], cwd=server,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, encoding="utf-8", errors="replace", bufsize=1)
    messages = queue.Queue()
    log = log_path.open("w", encoding="utf-8")
    def read_output():
        for line in process.stdout:
            log.write(line); log.flush(); messages.put(line)
    thread = threading.Thread(target=read_output, daemon=True)
    thread.start()
    def send(command):
        process.stdin.write(command+"\n"); process.stdin.flush()
    def wait_for(needle, timeout=180, check_commands=False):
        deadline = time.monotonic()+timeout
        received = []
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("Server exited; see .map-work/build-console.log")
            try:
                line = messages.get(timeout=1)
            except queue.Empty:
                continue
            received.append(line)
            if check_commands and any(t in line for t in ["<--[HERE]", "Unknown function", "That position is not loaded", "Failed to place structure", "Failed to execute function"]):
                raise RuntimeError("Build command failed: " + line.strip())
            if needle in line:
                return received
        raise TimeoutError(needle)
    completed = list(previous.get("completed_jobs", []))
    try:
        wait_for('For help, type "help"')
        print("Server ready; one-shot functions loaded at startup", flush=True)
        if "Failed to load function svs_map:" in log_path.read_text(encoding="utf-8"):
            raise RuntimeError("Map function parse failure; inspect build-console.log")
        send("forceload remove all")
        for index, job in enumerate(jobs):
            if job["id"] in completed:
                continue
            x1, z1, x2, z2 = job["bounds"]
            count = (x2//16-x1//16+1)*(z2//16-z1//16+1)
            if count > 256:
                raise ValueError(f"Too many force-loaded chunks for {job['id']}: {count}")
            send(f"forceload add {x1} {z1} {x2} {z2}")
            time.sleep(1)
            send("function "+job["function"])
            structure_job = job["function"].startswith("svs_map:build/") and job["id"] != "build_home"
            if structure_job:
                send("data get storage svs_map:build "+job["id"].removeprefix("build_"))
            marker = "SVSMAP_DONE_"+job["id"]
            send("say "+marker)
            response = wait_for(marker, check_commands=True)
            if structure_job:
                if not any("has the following contents: 1b" in text for text in response):
                    raise RuntimeError("No structure generation confirmation: " + job["id"])
            send(f"forceload remove {x1} {z1} {x2} {z2}")
            completed.append(job["id"])
            if index % 10 == 0 or job["function"].startswith("svs_map:build/"):
                print(f"BUILD {index+1}/{len(jobs)} {job['id']}", flush=True)
        for cmd in ["gamerule doMobSpawning true", "gamerule mobGriefing true", "gamerule doDaylightCycle true", "gamerule doWeatherCycle true", "gamerule randomTickSpeed 3", "time set day", "save-all flush"]:
            send(cmd)
        wait_for("Saved the game", 180)
    finally:
        if process.poll() is None:
            send("stop")
            process.wait(timeout=120)
        thread.join(timeout=5)
        log.close()
        result_path.write_text(json.dumps({"completed_jobs": completed, "expected_jobs": len(jobs), "server_exit_code": process.returncode}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    if len(completed) != len(jobs) or process.returncode:
        raise SystemExit(1)
    print("Build jobs completed; inspect blocks/entities before packaging", flush=True)


if __name__ == "__main__":
    main()
