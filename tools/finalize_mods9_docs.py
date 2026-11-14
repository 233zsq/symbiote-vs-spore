"""Maintain only the reviewed docs and verify the preserved external snapshots.
Does not deploy anything, edit reference packs, or launch Minecraft.
"""
import collections,csv,hashlib,json,re
from pathlib import Path

R=Path(__file__).resolve().parents[1]; DOC=R/'docs'; B=R/'backups/mods9_review_20261026'
DATE='2026-10-26'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

rawp=DOC/'data/模组9审查_2026-10-26.json'
x=json.loads(rawp.read_text(encoding='utf-8'))
# Correct the original scan's broad substring categories without resampling or
# replacing the original instance/reference hashes.
original=B/'initial_intake_inventory.json'
if not original.exists():original.write_bytes(rawp.read_bytes())
kinds=['forge/biome_modifier','worldgen/biome','worldgen/configured_feature','worldgen/placed_feature','worldgen/structure','worldgen/structure_set','dimension_type','dimension','structures','recipes','loot_tables','advancements','epicfight_mobpatch','capabilities/weapons/types','capabilities/weapons','skills','origins','origin_layers','powers']
for row in x['intake']:
    if 'resource_count_scope' not in row:
        row['legacy_substring_resource_counts']=row['resource_counts']
    row['resource_counts']=dict(collections.Counter(next((k for k in kinds if re.match(r'^data/[^/]+/'+re.escape(k)+'/',n)),'tags' if re.match(r'^data/[^/]+/tags/',n) else 'assets' if n.startswith('assets/') else 'other_data') for n in row['resources']))
    row['resource_count_scope']='Exact data/<namespace>/<kind>/ prefix; tags and assets separated; JSON only.'
rawp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

recommendations={
 'quest_enhance':('优先隔离验证','FTB 2001.4.22已有；双方同版验证序列化与任务桥'),
 'hadean_breathe':('补依赖后候选','缺vzling >=0.98.8；结构矿物与限伤待验'),
 'bookofdragons':('补依赖后候选','缺azurelib >=3.1.3；龙巢与骑乘镜头待验'),
 'celestisynth':('适配阻断','1.3.4不兼容IF的CELEpic 1.0旧类引用'),
 'celestisynth_fix':('随目标版本验证','只修1.3.4客户端缓存；不是EF适配'),
 'flametalisman':('暂缓默认合入','独立扣血时停飞行破坏与成本规则需约束'),
 'spawn':('生态改版候选','直接修改群系生成；不解除worldgen冻结'),
}
with (DOC/'data/模组9候选清单_2026-10-26.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=['文件','modId','版本声明','SHA256','字节数','JavaClassMajor','依赖声明','简中键数','英文键数','建议','关键条件','本轮状态']
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for row in x['intake']:
        d=row['declarations'][0];key=d['modId'];rec,reason=recommendations[key]
        langs=row['languages'];langcount=lambda code:sum(len(v) for k,v in langs.items() if k.endswith('/'+code+'.json'))
        w.writerow(dict(zip(fields,[row['file'],key,d.get('version'),row['sha256'],row['size'],','.join(row['class_versions']),json.dumps(d.get('dependencies'),ensure_ascii=False),langcount('zh_cn'),langcount('en_us'),rec,reason,'未安装；静态审查，未加载/功能验收'])))

review='模组9审查与合入建议_2026-10-26.md'
ifile='沉浸战斗_Celestisynth适配与坐骑研究_2026-10-26.md'
dnd='Otherworld_DND职业等级借鉴方案_2026-10-26.md'
nav=f'[模组9审查]({review}) · [IF适配与坐骑]({ifile}) · [DND职业等级方案]({dnd})'
common=(f'> **2026-10-26当前范围：剧情与FTB施工暂停，转入模组审查和职业规则研究。** 用户指定七个JAR已完成静态审查，均未安装；本轮实盘母本226/test229。CELEpic 1.0针对CS1.3.1，与候选1.3.4类路径不兼容；Hadean缺VzlingLib，龙之书缺AzureLib。IF坐骑由Tamer、Find me和fight_more/FTB分层实现；Otherworld的13职业/44子职业作为设计参考，不整包搬入。{nav}。未启动或操作游戏，未改实例、存档、任务和战斗规则；游戏验收仍由用户负责，联机保留待验。下方较早“当前”记录按原日期阅读。\n\n')
updates={
 'README.md':common,
 'HANDOVER.md':common,
 '资料库总索引.md':common+f'本轮新增：以上三份专项报告、[维护记录](资料库更新记录_2026-10-26.md)、[候选CSV](data/模组9候选清单_2026-10-26.csv)、[原始证据](data/模组9审查_2026-10-26.json)、[专项证据](data/模组9专项研究_2026-10-26.json)。均为当前审查/待实施方案，六表仍保留原采样日期。\n\n',
 '开发计划_执行状态.md':common,
 '开发计划_v2.md':f'> **2026-10-26计划切换：** 用户暂放剧情，本轮完成候选模组、IF适配/坐骑及Otherworld职业等级研究；实施队列先等待模组与职业规则选择，不继续旧剧情/FTB待办。{nav}。七候选未安装；旧任务与Legendary Bosses安装状态保持各专项记录，不能因本报告自动执行。\n\n',
 '模组清单.md':f'> **2026-10-26候选批次9审查，非安装增量：** 本轮实盘母本226/test229。新增七候选均未安装，不计入下方10-16六表225 JAR快照；[审查结论]({review})、[候选清单](data/模组9候选清单_2026-10-26.csv)与[四实例/参考盘点](data/模组9审查_2026-10-26.json)单独保存。缺AzureLib与VzlingLib；CELEpic旧适配不支持候选CS1.3.4。\n\n',
 'EF适配现状与动画管线.md':f'> **2026-10-26专项核对：** IF用CELEpic 1.0接CS1.3.1与EF20.14.17；其26项CS类引用在候选1.3.4全部缺失，不能直接复制。Celestisynth Fix仅清理新包名CSAnimator缓存，不是EF适配；Hadean未随包提供EF能力资源。详见[版本证据与路线]({ifile})和[批次审查]({review})。均未安装/加载；EF保持20.14.17，旧覆盖统计不刷新为现版实测。\n\n',
 '候选与变更清单.md':f'> **2026-10-26新增候选，全部未安装：** 优先验证Quest Enhance；Hadean/Book of Dragons补前置后分批；CS1.3.4与旧CELEpic适配阻断；Super-Tier先约束规则、Spawn另列生态改版。DND职业和坐骑召回为待实施建议，不自动批准玩法变化。{nav}。\n\n',
 '数据与采样说明.md':f'> **2026-10-26独立审查数据：** [模组9审查](data/模组9审查_2026-10-26.json)新增候选与四目录文件哈希，[专项JSON](data/模组9专项研究_2026-10-26.json)保存适配类引用/职业资源。当前实盘226/229不回写为下方225 JAR六表快照；资源按实际目录计数、tags/assets另列，反编译默认值不冒充运行时属性。七候选未安装，无新增游戏采样。\n\n',
 '汉化维护.md':f'> **2026-10-26候选语言审查：** 龙之书仅英文293键；Spawn英文947/繁中372，无自带简中；CS英文224/简中114，需按键差复核。Quest Enhance英文/简中195、Hadean148、Super-Tier215。七候选未安装，本轮没有生成或安装汉化；未来仍用外置语言资源。版本与语言证据见[本批报告]({review})及原始JSON，键数不等于待翻译条目数。\n\n',
 '开源协议审查.md':f'> **2026-10-26候选许可补充：** 本批只读审查，不改ARR JAR。Super-Tier页面ARR与本地MIT标记不一致；CELEpic、Find me定制版、fight_more及Otherworld定制组件不按可自由修改/分发处理。参考包本地研究不等于复用授权；安装可行性与发布许可分别核验。见[批次报告]({review})、[IF研究]({ifile})、[DND路线]({dnd})。未进行公开分发或提交推送。\n\n',
 '验收与风险登记.md':f'> **2026-10-26本批未验项：** 七个候选均未安装，加载/功能/联机不能标通过。静态已确认CS1.3.4与旧CELEpic类引用不兼容；龙之书缺AzureLib、Hadean缺VzlingLib；Quest Enhance有双方序列化变更；Spawn干预群系；Super-Tier有强制扣血/破坏。验收批次见[模组9报告]({review})，DND与坐骑规则见对应专项。剧情/FTB施工暂停，用户负责游戏验收，联机保留待验。\n\n',
}
prompt=(f'> **2026-10-26工作包更新：** 当前用户明确先放剧情，审查“新加入的模组9”、研究IF的CS适配/坐骑与Otherworld的DND规则。{nav}。本轮已完成资料与方案；七候选未安装，剧情/FTB施工暂停。不要依据旧安装授权恢复施工，也不要把13职业方案写成已实现。EF固定20.14.17；候选CS1.3.4不能配旧CELEpic，Fix不是适配。Tamer/Find me/fight_more职责分别核对；DND战斗职业与原四条专精支线分层，远程Boss、法术、等级、休息等变化仍是建议。下一步按用户新指示确定实施范围，保留联机待验。\n\n')
for name in ['交接启动词_通用规则.md','GLM_交接启动词.md','交接启动词_规划AI.md']:updates[name]=prompt

changes=[]
for name,block in updates.items():
    p=DOC/name;body=p.read_text(encoding='utf-8-sig')
    before=B/'docs_before'/name;before.parent.mkdir(parents=True,exist_ok=True)
    if not before.exists():before.write_bytes(p.read_bytes())
    if block in body:
        changes.append({'file':str(p),'before_sha256':sha(before),'after_sha256':sha(p)})
        continue
    lines=body.splitlines(keepends=True)
    pos=next((i+1 for i,l in enumerate(lines) if l.startswith('# ')),0)
    lines.insert(pos,'\n'+block)
    p.write_text(''.join(lines),encoding='utf-8')
    changes.append({'file':str(p),'before_sha256':sha(before),'after_sha256':sha(p)})
(B/'docs_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated docs',len(changes),'candidate CSV rows',len(x['intake']),flush=True)

# Read all originally inventoried external JAR/config/resource paths once more.
checks={}
for name,snapshot in {**x['instances'],**x['references']}.items():
    root=Path(snapshot['root']);changed=[];missing=[]
    expected={row['file']:row for row in snapshot['jars']}
    current={p.name:p for p in (root/'mods').glob('*.jar')}
    for name2,row in expected.items():
        p=Path(row['path'])
        if not p.exists():missing.append(str(p))
        elif sha(p)!=row['sha256']:changed.append(str(p))
    for rel,digest in snapshot['config_resource_hashes'].items():
        p=root/rel
        if not p.exists():missing.append(str(p))
        elif sha(p)!=digest:changed.append(str(p))
    actual_files={p.relative_to(root).as_posix() for folder in ['config','defaultconfigs','configureddefaults','kubejs','scripts','resourcepacks'] if (root/folder).exists() for p in (root/folder).rglob('*') if p.is_file()}
    extra=sorted(set(current)-set(expected))
    extra_resources=sorted(actual_files-set(snapshot['config_resource_hashes']))
    checks[name]={'jar_count':len(current),'jar_hash_checks':len(expected),'config_resource_hash_checks':len(snapshot['config_resource_hashes']),'changed':changed,'missing':missing,'additional_jars':extra,'additional_config_resources':extra_resources,'unchanged':not(changed or missing or extra or extra_resources)}
    print('Verify',name,checks[name]['unchanged'],'jar',len(current),'resources',len(snapshot['config_resource_hashes']),flush=True)
checks['intake']={'files':len(x['intake']),'unchanged':all(Path(row['path']).exists() and sha(Path(row['path']))==row['sha256'] for row in x['intake'])}
(DOC/'data/模组9审查_文件保护核对_2026-10-26.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
