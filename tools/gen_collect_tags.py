# -*- coding: utf-8 -*-
"""收藏家分档标签生成器（任务线规格书 v1 · 数据管线）

读 docs/全量武器表.md（游戏内注册表实测 dump），按 DPS 五分位生成
kubejs/server_scripts/svs_collect_tags.js（ServerEvents.tags 事件注册）。

2026-10-03 转轨说明：原方案输出 kubejs/data 数据包 JSON，但本环境三条独立测试
（Item.hasTag / KubeJS tags 事件读取 / 原版 clear #tag 命令）均不可见该标签，
改用 KubeJS 官方事件系统注册（实测可靠——KubeJS 事件系统整体已大量实证在跑）。

用法：python tools/gen_collect_tags.py
重跑时机：武器表刷新后 / mod 增删后（生成物入库）。
"""
import json, io, re, os

ROOT = r'E:/mcmp'
TABLE = os.path.join(ROOT, 'docs', '全量武器表.md')
SCRIPT = os.path.join(ROOT, 'kubejs', 'server_scripts', 'svs_collect_tags.js')
DEAD_PREFIXES = {'souls_like_bosses'}   # 已删除的 mod（决议：9-25 删），表中残留条目不进标签
TIERS = 5

# ── 解析表 ─────────────────────────────────────────────────────────────
rows = []   # (id, 中文名, dps)
for line in io.open(TABLE, encoding='utf-8'):
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

# ── 输出（ServerEvents.tags）────────────────────────────────────────────
parts = []
parts.append('// svs_collect_tags.js —— 收藏家分档标签（生成物！由 tools/gen_collect_tags.py 生成，勿手改）\n')
parts.append('// 数据源：docs/全量武器表.md，DPS 五分位；重跑生成器即可再生。\n')
parts.append("ServerEvents.tags('item', event => {\n")
for i in range(TIERS):
    ids = sorted(t[0] for t in tiers[i])
    arr = ', '.join("'%s'" % x for x in ids)
    parts.append("  event.add('svs:collect_t%d', [%s])\n" % (i + 1, arr))
parts.append('})\n')
os.makedirs(os.path.dirname(SCRIPT), exist_ok=True)
io.open(SCRIPT, 'w', encoding='utf-8').write(''.join(parts))

# ── 报告 ───────────────────────────────────────────────────────────────
print('解析 %d 件武器（剔除前缀 %s）' % (len(rows), ','.join(DEAD_PREFIXES)))
for i in range(TIERS):
    dps_rng = (min(t[2] for t in tiers[i]), max(t[2] for t in tiers[i]))
    mods = sorted(set(t[0].split(':')[0] for t in tiers[i]))
    print('T%d: %d 件  DPS %.2f~%.2f  含 %d 个 mod' % (i + 1, len(tiers[i]), dps_rng[0], dps_rng[1], len(mods)))
print('分位切点:', ['%.2f' % c for c in cuts])
print('输出:', SCRIPT)
