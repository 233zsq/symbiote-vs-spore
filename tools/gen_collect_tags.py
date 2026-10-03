# -*- coding: utf-8 -*-
"""收藏家分档标签生成器（任务线规格书 v1 · 数据管线）

读 docs/全量武器表.md（游戏内注册表实测 dump），按 DPS 五分位生成
kubejs/data/svs/tags/item/collect_t1~t5.json（收藏家支线的"等级"维度）。

用法：python tools/gen_collect_tags.py
重跑时机：武器表刷新后 / mod 增删后（生成物入库，标签未知 id 由 MC 容忍但会刷日志，
故默认剔除已删除 mod 的前缀——见 EXCLUDE_PREFIX）。
"""
import json, io, re, glob, os, statistics

ROOT = r'E:/mcmp'
TABLE = os.path.join(ROOT, 'docs', '全量武器表.md')
OUT_DIR = r'E:/SvS_整合包_副本/kubejs/data/svs/tags/item'
DEAD_PREFIXES = {'souls_like_bosses'}   # 已删除的 mod（决议：9-25 删），表中残留条目不进标签
TIERS = 5

# ── 解析表 ─────────────────────────────────────────────────────────────
rows = []   # (id, 中文名, dps)
cur_mod = ''
for line in io.open(TABLE, encoding='utf-8'):
    m = re.match(r'^##\s+(.+?)（([a-z_0-9]+)）', line)
    if m:
        cur_mod = m.group(2)
        continue
    m = re.match(r'^\|\s*`([a-z0-9_]+:[a-z0-9_/]+)`\s*\|\s*(.+?)\s*\|', line)
    if m:
        cols = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cols) < 5:
            continue
        iid, cn, dps_s = cols[0].strip('`'), cols[1], cols[4]
        try:
            dps = float(dps_s)
        except ValueError:
            continue
        rows.append((iid, cn, dps))

# 剔除已删除 mod
rows = [r for r in rows if r[0].split(':')[0] not in DEAD_PREFIXES]

# ── 五分位分档 ─────────────────────────────────────────────────────────
dps_list = sorted(r[2] for r in rows)
cuts = [dps_list[int(len(dps_list) * i / TIERS)] for i in range(1, TIERS)]

def tier_of(dps):
    for t in range(TIERS - 1):
        if dps <= cuts[t]:
            return t
    return TIERS - 1

tiers = {i: [] for i in range(TIERS)}
for iid, cn, dps in rows:
    tiers[tier_of(dps)].append((iid, cn, dps))

# ── 输出 ───────────────────────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)
for i in range(TIERS):
    ids = sorted(t[0] for t in tiers[i])
    p = os.path.join(OUT_DIR, 'collect_t%d.json' % (i + 1))
    io.open(p, 'w', encoding='utf-8').write(
        json.dumps({'replace': False, 'values': ids}, ensure_ascii=False, indent=1))

# ── 报告 ───────────────────────────────────────────────────────────────
print('解析 %d 件武器（剔除前缀 %s）' % (len(rows), ','.join(DEAD_PREFIXES)))
for i in range(TIERS):
    dps_rng = (min(t[2] for t in tiers[i]), max(t[2] for t in tiers[i]))
    mods = sorted(set(t[0].split(':')[0] for t in tiers[i]))
    print('T%d: %d 件  DPS %.2f~%.2f  含 %d 个 mod' % (i + 1, len(tiers[i]), dps_rng[0], dps_rng[1], len(mods)))
print('分位切点:', ['%.2f' % c for c in cuts])
print('T5 抽样:', [t[0] for t in tiers[TIERS - 1][:5]])
print('T1 抽样:', [t[0] for t in tiers[0][:5]])
