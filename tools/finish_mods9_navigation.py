"""One-time docs navigation and queue registration for the mods9 handoff."""
import collections,hashlib,json,re,shutil
from pathlib import Path
from prepare_mods9_install import ROOT,BACKUP,digest,write_json

D=ROOT/'docs';A=D/'archive/2026-10-31_入口整理前'
CURRENT={'README.md','HANDOVER.md','资料库总索引.md','开发计划_v2.md','开发计划_执行状态.md','交接启动词_通用规则.md','交接启动词_规划AI.md','GLM_交接启动词.md'}
IMPORTANT=['模组9_入包与回退记录_2026-10-31.md','剧情与FTB施工计划_2026-10-31.md','DeepSeek建议_采纳对照_2026-10-31.md','资料库更新记录_2026-10-31.md']
def category(p):
 n=p.name
 if n in CURRENT:return '当前状态'
 if n==IMPORTANT[1]:return '设计方案'
 if n.startswith(('FTB任务v4_','FTB任务v5_','FTB任务v6_')):return '实施记录'
 if n in ['开发计划_v1.md','剧情重写_v2_借火者之路.md','全量武器表.md','FTB任务重置_v2.md']:return '历史证据'
 if n in IMPORTANT[:1] or n==IMPORTANT[3] or re.search(r'记录|验收|核对|审查|入包|落装|施工|复查|维护',n):return '实施记录'
 if n in IMPORTANT[1:2] or re.search(r'^剧情|^任务设计|^规格书|^世界观|^天外成王|^Symbiote配置|^战斗手感|魔改设计|任务线框架',n):return '设计方案'
 return '参考材料'
def main():
 index=D/'资料库总索引.md';before=index.read_bytes();A.mkdir(parents=True,exist_ok=True)
 if not (A/index.name).exists():(A/index.name).write_bytes(before)
 saved=BACKUP/'docs_before'/index.name;saved.parent.mkdir(parents=True,exist_ok=True)
 if not saved.exists():saved.write_bytes(before)
 rows=[]
 for p in sorted(D.glob('*.md'),key=lambda p:p.name):
  title=next((l[2:].strip() for l in p.read_text(encoding='utf-8-sig').splitlines() if l.startswith('# ')),p.stem)
  role=category(p)
  status='本轮当前入口' if p.name in CURRENT or p.name in IMPORTANT else '按原文日期与证据使用，不自动扩展本轮施工'
  if p.name=='Otherworld_DND职业等级借鉴方案_2026-10-26.md':status='完整职业研究保留参考；现计划仅轻量DND'
  if p.name=='questbook_v2.json':status='文件名保留，内容为v6.1'
  rows.append({'path':p.relative_to(D).as_posix(),'title':title,'category':role,'status':status})
 lines=['# 资料库总索引','','更新：2026-10-31。按用途找资料；来源与证据等级决定能证明什么，文件自称“当前”或“已定”不能覆盖用户最新指示。','','## 当前入口','','[README](README.md) · [HANDOVER](HANDOVER.md) · [本轮改动](资料库更新记录_2026-10-31.md) · [安装与回退](模组9_入包与回退记录_2026-10-31.md) · [剧情／FTB计划](剧情与FTB施工计划_2026-10-31.md) · [DeepSeek采纳](DeepSeek建议_采纳对照_2026-10-31.md)','','本轮六模组＋两个前置E0安装，母本234／test237；Spawn未启用。任务、地图和EF实现未改，游戏／多人未验。旧六表保留原采样日期。']
 for group in ['当前状态','实施记录','设计方案','参考材料','历史证据']:
  lines+=['','## '+group,'','| 文件 | 用途／读取边界 |','|---|---|']
  for row in rows:
   if row['category']!=group:continue
   lines.append(f'| [{row["path"]}]({row["path"]}) | {row["status"]} |')
 lines+=['','## 子目录、数据与工作簿','','| 入口 | 用途 |','|---|---|','| [地图v2](map-v2/README.md) | 其他对话维护的地图工程，按其设计源继续，不在本轮改动 |','| [DeepSeek原文](reference/AI助手工作指南_决策与偏好_DeepSeek原文.md) | 原样参考副本，采纳范围看对照表 |','| [任务源](questbook_v2.json) | 当前v6.1工程源，保留文件名，未在本轮改写 |','| [模组9入包清单](data/模组9入包清单_2026-10-31.json) | 八个新增JAR、来源／哈希、生成覆盖与Spawn暂存 |','| [安装核对](data/模组9安装核对_2026-10-31.json) | test／母本文件级证据，E0 |','| [施工队列](data/剧情FTB施工队列_2026-10-31.json) | F0—F4、外部待接与原有pending目标 |','| [收尾校验](data/模组9收尾校验_2026-10-31.json) | 保护对象、配置、来源、索引和新链接检查 |','| [原六表数据说明](数据与采样说明.md) | 六份Excel、统一源与历史属性口径；本轮不伪刷新为运行时值 |','| [导航登记](data/资料库导航_2026-10-31.json) | 本索引的逐文件用途分类 |','| [历史目录](archive/README.md) | 各轮历史证据与旧稿 |','| [整理前入口说明](archive/2026-10-31_入口整理前/_归档说明.md) | 本轮重整前快照；相对链接按原docs根解释 |','','本表为用途导航，不逐份重审无关技术结论。地图／EF文件仍由对应对话维护；未因整理归入参考而撤销用户已批规则。']
 assert index.read_bytes()==before,'Concurrent index edit'
 index.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 for row in rows:
  if row['path']=='资料库总索引.md':row['title']='资料库总索引'
 archive_note=A/'_归档说明.md'
 archive_note.write_text('# 2026-10-31入口整理前快照\n\n本目录保存本轮实际改写前的Markdown原字节，不是执行入口。快照中的相对链接按它们原先所在的docs根目录解释；请通过[当前资料入口](../../README.md)和[总索引](../../资料库总索引.md)打开现行文件。\n\n旧“当前状态”、模组数量、任务版本、工作队列与暂停要求按原日期阅读。没有修改地图或EF子工程来适配本目录，也没有把旧提示词当作新授权。\n',encoding='utf-8')
 archive=D/'archive/README.md';before=archive.read_bytes();saved=BACKUP/'docs_before/archive/README.md';saved.parent.mkdir(parents=True,exist_ok=True)
 if not saved.exists():saved.write_bytes(before)
 body=before.decode('utf-8-sig').replace('\r\n','\n');entry='- [2026-10-31入口整理前](2026-10-31_入口整理前/_归档说明.md)：本轮重整前的入口、状态、规划与相关文本原样留痕；不是现行施工队列。\n'
 if entry not in body:
  first,_,rest=body.partition('\n');archive.write_text(first+'\n\n'+entry+'\n'+rest.lstrip(),encoding='utf-8')
 q=json.loads((D/'questbook_v2.json').read_text(encoding='utf-8'))
 pending=[{'key':x['key'],'title':x['title'],'chapter':x['chapter'],'state':'pending; unchanged','condition':x['text'][1]} for x in q['quests'] if x['availability']=='pending']
 phases=[{'phase':'F0','priority':'P0','state':'next; actual construction not started','depends_on':[],'output':'主支线／奖励／依赖矩阵与三处差异'}, {'phase':'F1','priority':'P1','state':'planned','depends_on':['F0'],'output':'序章与阶段Ⅰ样章、用户连续路线验收'}, {'phase':'F2','priority':'P2','state':'planned','depends_on':['F1 user acceptance','specific map/EF availability'],'output':'阶段Ⅱ与专精／军工／龙养成支线'}, {'phase':'F3','priority':'P3','state':'planned','depends_on':['F1 user acceptance','boss/event deliverables'],'output':'阶段Ⅲ—Ⅳ／终章与真实事件'}, {'phase':'F4','priority':'P4','state':'planned; progressive work per sample','depends_on':['approved samples','F2/F3 content readiness'],'output':'美术、奖励、迁移和全书验收'}]
 write_json(D/'data/剧情FTB施工队列_2026-10-31.json',{'source_revision':q['content_revision'],'scope':'Planning only; no quest mutations','phases':phases,'pending_unchanged':pending,'external_dependencies':['Spawn完整生成限制','新结构／材料／龙种的可达路径','CS1.3.4 EF可用性','Legendary Bosses独立安装与验收','原pending事件机制'],'excluded_implementation':['map','Epic Fight adaptation','siege rework','full DND stack']})
 write_json(D/'data/资料库导航_2026-10-31.json',{'date':'2026-10-31','scope':'Navigation, not runtime registry refresh','root_markdown':rows,'categories':dict(collections.Counter(r['category'] for r in rows)),'task_source_revision':q['content_revision']})
 print('Navigation entries',len(rows),'pending preserved',len(pending))

if __name__=='__main__':main()
