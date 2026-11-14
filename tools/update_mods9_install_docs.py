"""Scoped docs maintenance after mods9 installation; no runtime/config writes."""
import hashlib,json,re,shutil
from pathlib import Path
from prepare_mods9_install import ROOT,BACKUP,digest,write_json

DOC=ROOT/'docs';ARCHIVE=DOC/'archive/2026-10-31_入口整理前'
REPORT='模组9_入包与回退记录_2026-10-31.md'
PLAN='剧情与FTB施工计划_2026-10-31.md'
ADOPT='DeepSeek建议_采纳对照_2026-10-31.md'
GUIDE=Path('C:/Users/ZGJ/WorkBuddy/Worktrees/mcmp/main-3e9168cc/docs/AI助手工作指南_决策与偏好.md')
CHANGES=[]
def update(name,transform):
 p=DOC/name;before=p.read_bytes() if p.exists() else None
 if before is not None:
  saved=BACKUP/'docs_before'/name;saved.parent.mkdir(parents=True,exist_ok=True)
  if not saved.exists():saved.write_bytes(before)
  archived=ARCHIVE/name;archived.parent.mkdir(parents=True,exist_ok=True)
  if not archived.exists():archived.write_bytes(before)
 body=before.decode('utf-8-sig').replace('\r\n','\n').replace('\r','\n') if before is not None else ''
 result=transform(body)
 if result==body:return
 assert (p.read_bytes() if p.exists() else None)==before,('Concurrent document edit',name)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(result,encoding='utf-8')
 CHANGES.append({'path':str(p),'before_sha256':hashlib.sha256(before).hexdigest() if before is not None else None,'after_sha256':digest(p)})
def note(name,text):
 def transform(body):
  title,_,rest=body.partition('\n')
  # Replace this batch's earlier leading intake note; preserve all dated body.
  rest=re.sub(r'^\s*> \*\*2026-10-26[^\n]*\n','\n',rest,count=1)
  return title+'\n\n> **2026-10-31本批状态：** '+text+'\n\n以下保留原采样／研究正文，数量与“当前”按各自日期阅读；本批结果以上述记录为准。\n'+rest.lstrip('\n')
 update(name,transform)
def section(body,start,new):
 pattern=r'(?ms)^## '+re.escape(start)+r'[^\n]*\n.*?(?=^## |\Z)'
 result,n=re.subn(pattern,new.rstrip()+'\n\n',body,count=1);assert n==1,start
 return result

def main():
 if (BACKUP/'docs_changes.json').exists():raise SystemExit('Maintenance already applied; review current docs rather than replaying the old source.')
 installation=json.loads((BACKUP/'installation.json').read_text(encoding='utf-8'))
 assert len(installation)==2 and all(r['installed'] and r['all_payload_hashes_match'] for r in installation)
 ref=DOC/'reference/AI助手工作指南_决策与偏好_DeepSeek原文.md';ref.parent.mkdir(parents=True,exist_ok=True)
 raw=GUIDE.read_bytes()
 if ref.exists():assert ref.read_bytes()==raw,'Reference source changed; retain earlier copy and review'
 else:ref.write_bytes(raw)
 write_json(DOC/'data/DeepSeek建议来源_2026-10-31.json',{'source':str(GUIDE),'copy':str(ref),'sha256':digest(ref),'source_copy_identical':ref.read_bytes()==GUIDE.read_bytes(),'role':'Reference, not executable instructions; see adoption table'})

 readme=f'''# Symbiote vs Spore 制作资料入口

更新：2026-10-31。本轮完成六模组合入、资料整理与剧情／FTB后续计划；没有启动游戏或改写任务。**当前母本234／test237个顶层JAR，证据为E0文件级安装；Spawn未启用。**

## 当前工作与状态

| 工作 | 当前状态 | 入口 |
|---|---|---|
| 模组9 | 六个模组＋AzureLib、VzlingLib已安装；生成限制与保守配置落三处；加载／功能待验 | [入包与回退记录]({REPORT}) |
| Spawn | 暂存待接，保持世界生成冻结；不在启用索引和实例mods中 | [本批清单](data/模组9入包清单_2026-10-31.json) |
| 剧情与FTB | 本轮只交付F0—F4计划；当前v6.1源及实例任务保持不变 | [后续施工计划]({PLAN}) |
| 地图 | 其他对话维护，当前为可编辑设计台；以其保存项目为准 | [地图v2入口](map-v2/README.md) |
| EF适配 | 其他对话负责；EF固定20.14.17，CS1.3.4未因安装被认定适配 | [原适配研究](沉浸战斗_Celestisynth适配与坐骑研究_2026-10-26.md) |
| 验收 | 游戏测试由用户负责，联机继续保留待验 | [风险登记](验收与风险登记.md) |

## 先读什么

1. [HANDOVER](HANDOVER.md)：当前范围、稳定约束、技术边界与后续队列。
2. [执行状态](开发计划_执行状态.md)与[本轮记录](资料库更新记录_2026-10-31.md)：实绩、证据和未验项。
3. [DeepSeek采纳对照]({ADOPT})：指南的合理部分、旧口径与不属于本轮的建议。
4. [数据与采样说明](数据与采样说明.md)：历史属性、静态资源、注册和游戏表现的区别。
5. [资料库总索引](资料库总索引.md)：按用途查找，历史报告不能自行变成施工授权。

## 文档按五类使用

| 类别 | 用途与主要入口 |
|---|---|
| 当前状态 | 本页、HANDOVER、执行状态；最新同事项用户指示和实际证据优先 |
| 实施记录 | [模组9入包]({REPORT})、各日期安装／验收／回退记录 |
| 设计方案 | [剧情／FTB施工计划]({PLAN})、[天外成王篇v4](剧情重写_v4_天外成王篇.md)、[四传说v5增补](剧情重写_v5_旧世四传说与造界者.md) |
| 参考材料 | [DeepSeek对照]({ADOPT})、[Otherworld研究](Otherworld_DND职业等级借鉴方案_2026-10-26.md)、各参考包研究 |
| 历史证据 | [整理前入口快照](archive/2026-10-31_入口整理前/README.md)、[历史目录](archive/README.md)；保留原日期与旧口径 |

## 制作资料与现版增量

| 查什么 | 入口 |
|---|---|
| 本轮八个新增JAR、依赖、来源与哈希 | [入包清单](data/模组9入包清单_2026-10-31.json)、[两实例安装核对](data/模组9安装核对_2026-10-31.json) |
| 模组、武器、实体、Boss、EF与结构静态资料 | [模组清单](模组清单.md)、[武器目录](武器目录.md)、[敌对目录](敌对生物表.md)、[其他类别目录](中立及其他类别目录.md)、[Boss资料](数值表_Boss.md)、[EF资料](EF适配现状与动画管线.md)、[结构表](整合包结构表.md) |
| 原六份工作簿与统一源 | 经[数据说明](数据与采样说明.md)使用；保留10-16等原采样日期，本轮增量不伪刷新为游戏实测 |
| 汉化、许可和配置 | [汉化维护](汉化维护.md)、[许可审查](开源协议审查.md)、[实例配置](实例配置说明.md) |

当前FTB源文件名仍是`questbook_v2.json`，内容修订为v6.1；不按文件名误用旧v2设计。T2／T1／T0和收藏家＋军械全鉴合并按用户后续要求保留。母本、test与仓库任务存在既有差异，本轮没有借新模组合入同步任务。

旧入口中的多条“当前”已归入有日期的历史快照；未完成机制、Legendary Bosses待安装和游戏验收状态分别按专项证据阅读。没有提交或推送仓库。
'''
 update('README.md',lambda _:readme)

 def handover(body):
  stable=body[body.index('## 〇、30 秒版'):]
  stable=section(stable,'〇、',f'''## 〇、30秒接手

用户于2026-10-31要求执行已确认计划。当前只完成本批六模组／前置入包、文档整理和后续计划；剧情与FTB施工未恢复。地图与EF由其他对话负责，不合并其源工作树或替它们施工。

- 本批状态和精确文件见[入包记录]({REPORT})、[安装核对](data/模组9安装核对_2026-10-31.json)。母本234／test237个顶层JAR，E0；未启动游戏。
- Spawn暂存，不在启用索引；worldgen继续冻结。CS1.3.4已安装，不能据此认定EF适配；旧CELEpic未装。
- 任务基线为v6.1（源文件名仍是questbook_v2.json）。原任务、ID和领奖记录不因本轮安装改变；后续从[计划F0]({PLAN})开始。
- [DeepSeek指南采纳对照]({ADOPT})区分参考、旧口径和已采用部分；围城重构／地图／EF建议不自动成为本轮任务。
- 整理前的全部状态段在[旧HANDOVER快照](archive/2026-10-31_入口整理前/HANDOVER.md)；以下技术和历史裁决保留原日期，不把旧数量当作当前数量。''')
  stable=section(stable,'三、',f'''## 三、当前状态（2026-10-31）

| 项目 | 现状与证据 |
|---|---|
| 本批安装 | 六个内容／修复模组＋两个前置，25文件三处对应；两实例原有JAR与清单外资源未变，E0 |
| 生成与特殊能力 | 独立外置数据包限制8结构、6feature注入；Super-Tier按批准保守值配置；实际行为待验 |
| 当前任务 | 仓库v6.1，test为先前安装v6；母本任务未随本轮同步；Legendary Bosses先前文件仍待独立安装 |
| 地图 | [设计台与地图v2](map-v2/README.md)由其他对话维护；不改seed、坐标、设计源或地图工具 |
| EF | 20.14.17固定；本轮不改模型、动画、mobpatch、适配规格或svs_tweak源码 |
| 游戏／联机 | 未启动或操作游戏；用户负责验收，双人仍待验 |
| 六表 | 仍是原采样快照；新增模组独立记录，不填造运行时属性 |

原10-07～10-30执行细节见对应专项和[整理前快照](archive/2026-10-31_入口整理前/HANDOVER.md)。''')
  stable=section(stable,'七、',f'''## 七、后续队列

1. 本批加载和功能由用户在独立测试世界验收；先确认模组／数据包启用，再测试界面、骑乘、战斗与特殊能力，不能用E0代替E1—E3。
2. 用户恢复剧情／FTB施工后，从[施工计划F0]({PLAN})整理总纲、主支线／奖励矩阵和三处差异；接着F1样章，确认后扩F2／F3，F4统一验收。
3. Spawn、结构／材料取得链、CS武器可用性是外部待接项；地图／EF交付由对应对话负责，本轮不发消息催办或代做。
4. DND后续只按等级成长／GameStages、加点和少量子职业能力研究；不实施完整13职业移植。具体数值和冲突须另列规格，不悄悄改现有远程、法术、围城等规则。
5. 旧M1～M6、围城失守／回拨、多人与优化队列保留专项记录，但本轮不处理；不能据历史待办顺带施工。
''')
  stable=stable.replace('## 九、关键事实速查','## 九、历史事实速查（按原记录日期使用）',1)
  marker='## 五、血泪教训'
  p=stable.index(marker)
  new_decision=f'''### 2026-10-31（本对话已确认的执行范围）

- 六模组＋两个必要前置入包，Spawn待接；正式包继续冻结新增生成，采用本批外置限制与Super-Tier保守配置。
- 只整理资料并制定剧情／FTB后续计划；不改剧情正文、任务源／SNBT／桥脚本，不扩地图、EF、围城或其他工程。
- 收藏家与军械全鉴合并、T0／T1／T2及奖励方向沿用用户10-17后续要求；指南旧“禁止Tier”不能覆盖它们。
- 参考指南的证据分级与轻量DND方向按[采纳对照]({ADOPT})使用；原文中其他“已定”不自动变成新机制裁决。

'''
  stable=stable[:p]+new_decision+stable[p:]
  return '# Symbiote vs Spore 交接文档\n\n更新：2026-10-31。当前工作以本页〇、三、七及用户最新指示为准；历史事实保留来源。\n\n'+stable
 update('HANDOVER.md',handover)

 def status(body):
  old=body[body.index('## 〇、批准记录'):]
  old=old.replace('## 五、当前待办（按计划依赖序）','## 五、历史待办（按原计划依赖序）',1)
  return f'''# 开发执行状态

更新：2026-10-31。当前实绩与历史验收分开登记。

## 当前批次

| 项目 | 状态 |
|---|---|
| 六模组＋前置入包 | 已完成E0，test237／母本234个JAR；25个新增文件校验一致 |
| 生成限制与Super-Tier配置 | 已落仓库／test／母本，功能未验 |
| Spawn | 未启用，候选待接 |
| 文档与DeepSeek对照 | 已整理；原文、历史入口、当前记录分别保留 |
| 剧情与FTB施工计划 | F0—F4已交付；未实际改写任务 |
| 地图／EF／围城等其他工程 | 不属于本批；保留其他对话工作 |
| 游戏加载／功能／联机 | 本轮未验，用户负责；双人待验保留 |

证据：[入包记录]({REPORT})、[安装保护核对](data/模组9安装核对_2026-10-31.json)、[后续计划]({PLAN})。本轮不继承旧序章或旧模组的运行时结论，不提交／推送。

## 历史执行证据

10-17序章、FTB v4／v5／v6、炮塔等切换记录见[整理前执行状态](archive/2026-10-31_入口整理前/开发计划_执行状态.md)。下面保留更早M1/M2的原文；其中“当前”“待办”均按原日期理解，不扩大本轮范围。

'''+old
 update('开发计划_执行状态.md',status)
 update('开发计划_v2.md',lambda _:f'''# 开发计划入口

更新：2026-10-31。计划按工作包管理，日期只用于事实与修订，不排施工日历。

## 当前已执行

六模组＋两个前置、外置生成限制、Super-Tier保守配置已完成E0安装；Spawn暂存。见[入包与回退记录]({REPORT})。未启动游戏，功能／联机待验。

## 下一轮剧情与FTB

唯一当前施工队列为[剧情与FTB施工计划]({PLAN})：F0总纲／依赖→F1序章与Ⅰ样章→F2阶段Ⅱ与支线→F3阶段Ⅲ—Ⅳ／终章→F4美术奖励与迁移验收。当前只交付计划，实际施工待用户恢复。

以v4／v5叙事和v6.1任务源为基线，保留ID与领奖记录、T0／T1／T2和收藏全鉴合并，逐步显示任务。地图与EF是外部交付，不代做；DND收敛为轻量成长，不移植完整职业栈。

## 其他工作与历史

地图由[地图v2入口](map-v2/README.md)指向对应对话成果。EF、围城、优化与其他模组工作本轮不处理。旧P0—P4/M1—M6计划保存在[本文件整理前快照](archive/2026-10-31_入口整理前/开发计划_v2.md)，不能当作新施工授权。

状态查[执行状态](开发计划_执行状态.md)，依据查[HANDOVER](HANDOVER.md)、[魔改决议](魔改设计决议.md)及[DeepSeek采纳对照]({ADOPT})；文档里的提案不能替代用户裁决。
''')

 common=f'六模组＋两个前置已完成E0安装，母本234／test237；Spawn未启用，世界生成继续冻结。见[入包记录]({REPORT})和[机器清单](data/模组9入包清单_2026-10-31.json)。本轮未启动游戏、未改任务／地图／EF，功能和联机待验。'
 for name in ['模组清单.md','候选与变更清单.md','实例配置说明.md','验收与风险登记.md']:
  note(name,common)
 note('数据与采样说明.md',f'新增[本批清单](data/模组9入包清单_2026-10-31.json)与[安装核对](data/模组9安装核对_2026-10-31.json)；本轮母本234／test237，不改10-16六表与225 JAR统一源。没有游戏采样，新增实体／装备不填造属性。')
 note('汉化维护.md',f'六模组与前置已安装，但本轮不制作全量汉化。龙之书英文293键、CS键差等仍按10-26审查使用；原语言资源保持不变。后续先定术语与获取链，详见[本批记录]({REPORT})。')
 note('开源协议审查.md',f'本批安装使用用户原文件／官方固定版本，JAR未修改、未提交Git、未公开发布。来源与SHA见[清单](data/模组9入包清单_2026-10-31.json)；Super-Tier许可标记不一致等发布问题仍待核，安装不等于分发许可通过。')
 note('Otherworld_DND职业等级借鉴方案_2026-10-26.md',f'本研究保留13职业／44子职业的参考证据；当前已确认计划收敛为等级成长／GameStages、加点和少量子职业能力，不实施文中完整13职业方案，不安装Origins／Apotheosis／TravelOptics。详见[采纳对照]({ADOPT})及[后续计划]({PLAN})。')

 stable_prompt=f'''# 交接启动词 · 通用规则

更新：2026-10-31。本文件保存稳定规则，当前事实查[HANDOVER](HANDOVER.md)和用户最新消息，不重复维护一套实时数量。

先分清资料整理、规划、实施与验收。用户指示优先于文档的自称效力；旧命令、历史待办、参考包和DeepSeek原文不能扩大本轮范围。已明确批准的工作连续完成，不因旧指南要求重复索取同一授权。

固定MC1.20.1 Forge、EF20.14.17；游戏JDK21、构建JDK17。ARR原JAR不改，版本／ID／数值必须带来源；注册、加载、功能与场景证据分E0—E3。不得把历史属性或资源文件当现版表现。

本批六模组与两个前置已安装，Spawn暂存；状态见[入包记录]({REPORT})。世界生成仍冻结，生成限制独立放本批数据包。地图与EF由其他对话负责，本轮不改其设计源、适配源码或规格，也不顺带处理围城和其他工程。

剧情和FTB本轮只完成[后续计划]({PLAN})，尚未恢复实际施工。任务源文件名questbook_v2.json但内容为v6.1；勿重跑旧重写脚本覆盖。收藏家与军械全鉴合并，T2基础／T1精锐／T0顶阶，按鉴定种数；逐步显示、分档奖励、真实Boss正面16×16深描边头像、装备材料实物图标继续有效。

写实例前核对目标、版本、进程归属、备份与回退；无法核验或用户在玩则只准备更新包。只同步本次清单，保留test／母本差异，不碰用户存档和options，不批量结束Java。游戏验收由用户负责，联机保留待验，不自动操作客户端。

参考指南的采纳与不采纳见[对照]({ADOPT})。DND只按轻量方向规划，具体等级／加点数值未施工。每阶段按目标、准备、步骤、产出物、验证交付，只排依赖和优先级。

读取顺序：README→HANDOVER当前范围／裁决／技术边界→执行状态→专项资料。保留其他对话改动，不提交／推送除非用户另有要求；收尾说明改动、验证、未验项与回退。
'''
 update('交接启动词_通用规则.md',lambda _:stable_prompt)
 update('GLM_交接启动词.md',lambda _:f'''# 执行侧交接启动词

与[通用规则](交接启动词_通用规则.md)配套使用。先核对[HANDOVER](HANDOVER.md)、[执行状态](开发计划_执行状态.md)和当前用户指示。

2026-10-31批次已完成六模组／前置E0安装、资料整理和后续计划；Spawn未启用，游戏加载／功能／联机未验。本轮具体范围及回退见[入包记录]({REPORT})。

用户恢复剧情／FTB施工后，按[计划]({PLAN})从F0开始，不自动执行F1以后的任务生成或旧安装包。源内容为v6.1，保留既有任务／奖励ID；先比较仓库、test、母本差异。地图和EF交付由其他对话负责，不代做、不向其他对话发送消息。

每批仅改必要路径，先备份、离线验证，再在可核验的退出窗口安装；测试由用户负责。游戏行为未回传不能写成功能通过。参考指南按[采纳对照]({ADOPT})使用，不恢复旧数量、禁Tier或整包同步口径。
''')
 update('交接启动词_规划AI.md',lambda _:f'''# 规划侧交接启动词

先读[通用规则](交接启动词_通用规则.md)、[HANDOVER](HANDOVER.md)、[当前计划]({PLAN})和[DeepSeek采纳对照]({ADOPT})。

当前叙事基线为天外成王v4＋四传说v5，任务源内容v6.1。六模组与前置已安装，Spawn暂存；注册／文件存在不代表取得链、战斗或EF适配通过。地图、EF、围城与其他工程不在本轮范围。

后续先做F0主支线／奖励矩阵及依赖，再做F1小样章供用户验收，最后扩展和统一收口。收藏家／全鉴合并、T0／T1／T2、逐步显示与分档奖励按最新用户要求；不要用任务数量、历史DPS或旧“禁止Tier”否定它们。

新能力必须对应实际接口和验证条件。DND收敛为等级成长／GameStages、加点和少量子职业能力，不移植完整13职业栈。未定机制单列影响与推荐，不据剧情文案补造物品、配方或事件。只排依赖与优先级，不排具体日期。

规划授权不自动成为施工授权；当前只交付计划，未恢复任务改写。所有结论分清事实、建议、已批未做和验收边界。
''')
 write_json(BACKUP/'docs_changes.json',CHANGES)
 print('Updated docs',len(CHANGES),'reference identical',True)

if __name__=='__main__':main()
