"""Record every documentation file's role and validate the offline refresh boundary."""
import collections,hashlib,json,re,zipfile
from pathlib import Path
from urllib.parse import quote,unquote
ROOT=Path(__file__).absolute().parents[1];DOCS=ROOT/'docs';DATA=DOCS/'data'
def text(p):return p.read_text(encoding='utf-8-sig')
def write(p,s):p.write_text(s.rstrip()+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def role(p):
    name=p.name;parts=p.relative_to(DOCS).parts
    if parts[0]=='data':return '统一资料/派生数据','离线证据；读取数据与采样说明后用，不当运行时验收'
    if parts[0]=='archive':return ('历史目录入口','历史用途，当前执行看docs/README') if name=='README.md' else ('归档原证据','保留原文；不因旧价格/队列/示例自动施工')
    if name=='SvS_Boss表.xlsx':return '历史工作簿与排序参照','首次更新遇WPS占用而保留；当前入口是SvS_Boss表_更新版.xlsx'
    if p.suffix=='.xlsx':return '当前工作簿视图','已离线更新；历史属性/当前资源/待实测分列'
    if name in {'HANDOVER.md','任务文档.txt','魔改设计决议.md','任务线框架规格书_v1.md'}:return '现行裁决/原则','机制约束继续有效；后续直接授权和当前暂停优先'
    if name in {'开发计划_执行状态.md','验收与风险登记.md','待裁决清单.md','开发计划_v1.md'}:return '计划/裁决/执行登记','计划与实绩分开；FTB暂停/不开游戏；具体结果看执行状态'
    if name in {'模组清单.md','武器目录.md','敌对生物表.md','中立及其他类别目录.md','数值表_Boss.md','数据与采样说明.md','整合包结构表.md','EF适配现状与动画管线.md','汉化维护.md'}:return '当前制作资料','使用新数据口径；原研究段/旧样本已显式标历史'
    if name=='全量武器表.md':return '冻结的标签生成器输入','1331原始ID及五列保留；不是当前任务选材表；1291输出不重跑'
    if name in {'README.md','资料库总索引.md','资料库更新记录_2026-10-12.md','文档整理记录.md'}:return '导航/整理记录','记录入口与去向，不代替机制规格和实测'
    if name in {'FTB任务重置_v2.md','FTB任务v2_节点与验收目录.md','FTB任务v2_ID映射.json','questbook_v2.json','M2.4_施工记录_2026-10-11.md'}:return 'FTB施工中间态/证据（暂停）','16章210节点25 pending；此前仅加载/引用审计通过，当前不重建/测试'
    if name in {'任务线实装核对.md','M2.4_编辑器施工顺序单.md','任务设计稿_序章_觉醒_v1.md','任务设计稿_阶段Ⅰ_启程_v1.md','任务设计总稿_v1.md'}:return '任务设计/历史施工资料','已批机制可用；旧节点/编辑器限制不覆盖v2和后续SNBT授权；当前暂停'
    if name in {'世界观设定_SvS.md','剧情文案_章节引言与里程碑_v1.md'}:return '并行新增叙事资料（原文保留）','已纳入导航；本轮不修改或回填，文中批复以用户/裁决文档为准'
    if name in {'任务参考研究_五整合包FTB.md','武器线与匠魂节奏_参考综合.md','主线深化研究_全模组与战斗筛选.md','战斗手感基准.md'}:return '参考研究/评审方法','借结构/方法，不抄跨版本ID；候选/历史统计不当已实现状态'
    if name.startswith('规格书_'):
        return ('搁置规格','EF怪物适配五问未闭环；不写适配JSON') if 'EF怪物适配' in name else ('机制规格/已执行留档','参数合同与后续裁决合读；实际通过项查执行状态')
    if name in {'GLM_交接启动词.md','交接启动词_规划AI.md','实例配置说明.md','候选与变更清单.md'}:return '当前接手/维护入口','已补暂停/不开游戏/test4删除/E2/E4状态；不自动授权施工'
    if name in {'刀光与新增模组6_优化合入综合审查.md','Rapid_Optimization_合入评估与执行交接.md','合入_B0基线记录.md','合入_隔离实验实例_svs_lab.md'}:return '合入研究/实验状态','按10-11已批条件；svs_lab与母本分开；当前不开游戏'
    if name=='E4_收藏家标签差集清单.md':return 'E4已执行证据','1291件标签；旧步骤为过程记录，当前不重复生成；现版复核待窗口'
    if name=='对抗式审查_2026-09-26.md':return '原始审查（保留引用路径）','历史假设，后续裁决/实证优先；源码引用保留路径'
    if name=='开源协议审查.md':return '许可覆盖登记','151件历史审查≠当前215全部通过；license只录证据'
    if name in {'Symbiote配置调频设计.md','铁魔法禁用清单.md'}:return '机制专项资料','保留机制与历史实测层级；当前不调参/新增禁用'
    return '资料文件','保留用途与来源；不自动构成新授权'

def maintain_pause_entries():
    # Propagate latest direct steering to likely stale construction entry points.
    note='> **2026-10-12当前状态：FTB重写暂停，用户要求尽量不开游戏。** 本文保留作设计/历史施工资料；不据旧步骤自动启动游戏或生成/替换任务。现版资料见 [数据与采样说明](数据与采样说明.md)，当前进度见 [执行状态](开发计划_执行状态.md)。'
    for name in ['开发计划_v1.md','任务线框架规格书_v1.md','任务线实装核对.md','M2.4_编辑器施工顺序单.md','任务设计稿_序章_觉醒_v1.md','任务设计稿_阶段Ⅰ_启程_v1.md','任务设计总稿_v1.md','FTB任务重置_v2.md']:
        p=DOCS/name;s=text(p)
        if note not in s:a,_,b=s.partition('\n');write(p,a+'\n\n'+note+'\n'+b.lstrip('\n'))
    p=DOCS/'任务设计总稿_v1.md';s=text(p)
    s=s.replace('当前状态：test19仍为最近全绿基线，test20已导入test；M1部分通过，任务桥仍有占位，M2与后期设计尚未由用户编辑器落成。游戏进度只认HANDOVER与执行状态，本稿变厚不表示制作进度前移。','当前状态：本稿的推荐已于10-11按初版原则采纳，5处修正及看样/参数条件见《待裁决清单》卷首；后续用户已授权程序生成/校验SNBT。v2已加载16章210节点、25 pending，功能与全线未验，现暂停重写；本稿是设计输入，旧节点数量不再约束v2。test19仍为最近全绿基线，具体进度看执行状态。')
    write(p,s)
    p=DOCS/'archive/README.md';s=text(p)
    if '2026-10-12_资料更新前' not in s:s+='\n\n`2026-10-12_资料更新前/`保存本次更新前的模组清单、敌对生物表、HP阈值Boss表、数据与采样说明四文，逐字节保留。六份旧Excel和全量文档完整备份在E:/mcmp/backups/docs_refresh_20261012/before_docs.zip，当前工作簿和用途见上级数据与采样说明。\n'
    s=s.replace('旧提示不能用来让AI手写SNBT或升级EF','旧提示不能代替用户后续授权或允许升级EF；当前程序生成SNBT的授权及暂停状态见上级HANDOVER§〇')
    write(p,s)
def main():
    if '--index-only' not in __import__('sys').argv:maintain_pause_entries()
    # Check frozen old input rows and archive preservation against the pre-refresh zip.
    backup=ROOT/'backups/docs_refresh_20261012/before_docs.zip';manifest=json.loads(text(ROOT/'backups/docs_refresh_20261012/before_manifest.json'))
    with zipfile.ZipFile(backup) as z:
        names=z.namelist();key=next(n for n in names if n.endswith('全量武器表.md'))
        before=z.read(key).decode('utf-8-sig');after=text(DOCS/'全量武器表.md')
        data_rows=lambda s:[line for line in s.splitlines() if re.match(r'^\|\s*`?[a-z0-9_.-]+:',line)]
        frozen_identical=data_rows(before)==data_rows(after)
    preserved=[];changed_archives=[];new_archive_errors=[]
    for row in manifest:
        p=ROOT/row['path']
        if '/archive/' in row['path'] and p.name!='README.md':
            (preserved if p.exists() and sha(p)==row['sha256'] else changed_archives).append(row['path'])
    for name in ['模组清单.md','敌对生物表.md','数值表_Boss.md','数据与采样说明.md']:
        before_sha=next(row['sha256'] for row in manifest if row['path']=='docs/'+name)
        if sha(DOCS/'archive/2026-10-12_资料更新前'/name)!=before_sha:new_archive_errors.append(name)
    rows=[];inventory=[]
    for p in sorted(DOCS.rglob('*')):
        if not p.is_file() or p.name.startswith('~$'):continue
        rel=p.relative_to(DOCS).as_posix();r,b=role(p)
        # Reading complete text here also records headings and avoids only indexing filenames.
        heads=re.findall(r'^#{1,4} .+$',text(p),re.M) if p.suffix in ('.md','.txt') else []
        derived_index=p.name in {'资料库总索引.md','资料库更新记录_2026-10-12.md','文档文件登记.json','本轮核对结果.json'}
        inventory.append({'path':rel,'role':r,'boundary':b,'sha256':None if derived_index else sha(p),'bytes':None if derived_index else p.stat().st_size,'headings':heads,'digest_note':'滚动索引/记录自身不作自引用哈希' if derived_index else '本次整理时快照'})
        rows.append((rel,r,b))
    active=[x for x in rows if not x[0].startswith(('archive/','data/'))];history=[x for x in rows if x[0].startswith('archive/')];data=[x for x in rows if x[0].startswith('data/')]
    intro='''# 制作资料库全文件索引

> 2026-10-12离线整合。每个文件按现行裁决/当前资料/设计参考/暂停中间态/归档证据区分；不是把所有文件重新标为“已完成”。用户要求暂不开游戏，FTB重写保持暂停。数据解释入口：数据与采样说明.md；最新进度入口：开发计划_执行状态.md。

## 一、维护归属与合并原则

当前范围与版本→模组清单；武器/实体/Boss/EF数据→统一JSON及六个工作簿；机制→魔改设计决议/对应规格；进度→执行状态；风险→验收与风险登记；批复→待裁决清单/HANDOVER裁决。其他文档通过链接引用，不复制一套当前事实。旧不同样本不硬并；已执行规格保留合同/证据，参考研究保留独有结论；被替代数值正文已归档，冻结生成器输入保留原路径。

本次不删除具有独有证据的原文；旧HP阈值表合入Boss工作簿的独立页、敌对MD/模组MD替换为统一资料视图。首次更新遇WPS占用的旧Boss原表保留作排序参照，仅更新版作为当前入口。六表已按用户旧Boss表的模组数量/组内属性顺序整理，具体口径见数据与采样说明§一。叙事两文由并行工作新增，已索引但本轮未改正文或回填任务。文中自述批复不自动增加机制授权。

## 二、活动文件逐项用途

'''
    def lines(rs):return '\n'.join(['| 文件 | 类别 | 现在怎样用 |','|---|---|---|']+['| ['+rel+']('+quote(rel,safe='/')+') | '+r+' | '+b+' |' for rel,r,b in rs])
    write(DOCS/'资料库总索引.md',intro+lines(active)+'\n\n## 三、统一数据与派生文件\n\n'+lines(data)+'\n\n## 四、历史文件（原文不施工）\n\n'+lines(history)+'\n\n## 五、来源与效力\n\n逐文件路径/大小/哈希/标题见data/文档文件登记.json；所有文字文件按完整正文读入以核标题/引用/旧口径。归属划分是本轮维护安排，不新增游戏机制、安装或删除授权。事实依据：HANDOVER§四/五/七、任务文档工作原则、魔改设计决议变更记录、开发计划_执行状态当前切换、数据与采样说明。旧报告的文件日期只代表原报告时间。')
    write(DATA/'文档文件登记.json',json.dumps(inventory,ensure_ascii=False,indent=2))
    wb=json.loads(text(ROOT/'backups/docs_sheet_work/installed_verification.json'));q=json.loads(text(DATA/'汇总核对.json'))
    # Fresh full snapshot hash list plus a clear report. No claims of successful gameplay tests.
    record='''# 资料库更新记录（2026-10-12）

## 一、这轮交付及暂停边界

用户先暂停FTB重写，要求更新整合全部docs与五份数值Excel/全模组表，随后明确“别开我的世界，现在尽量避免开游戏”。本轮改为离线读jar、配置、语言资源、既有日志和历史导出；没有取得成功的新运行时采样。用户该指示后未再启动游戏或重载世界；不继续FTB构建、桥接、领奖测试和Boss看样。任务v2仍16章210节点/25 pending，加载/引用审计通过≠功能或全线通过。

早先的临时采样尝试在test最新日志00:03:39被KubeJS类过滤拦截（net.minecraftforge.fml.ModList），没有成功END采样标记，未纳入数据。test/kubejs/server_scripts/_svs_docs_snapshot.js已移除，避免下次开档自动运行；不把该失败算新数据。证据：test/logs/latest.log对应报错行；本轮交付采用历史JSON与静态源。

## 二、事实更新和资料整合

| 工作 | 结果与边界 | 来源 |
|---|---|---|
| 现版清单 | 母本/test各215顶层jar、221顶层声明；逐文件SHA-256全部相同 | 现版资料索引mods/jar_difference；jar TOML/manifest |
| 武器/实体 | 1354历史武器/工具、877历史实体（敌对类别489/其他388）完整保留；新资源/名称/取得线索分列 | 历史dump JSON；制作资料汇总 |
| Boss | 95候选/函数场次＋208高血量实体独立页＋5事件/排除说明；先模型动作，不按HP选终局 | Boss Checklist支持表交集；主线深化研究§四；五包研究E-二轮 |
| EF | 3184武器JSON文件/2746键；157类型文件；102 MobPatch文件/键；历史标记与资源分列 | EF资源索引.csv；现版资料索引 |
| 结构 | 204 structure文件/201键，144 structure_set文件/141键；当前键和已批源码密度分类一并入表 | 结构资源索引.csv；StructureDensityRules.java |
| 汉化 | 母本OpenLoader95个zh_cn文件、10069文件内键条目；名称候选有来源，不冒称显示/术语评审通过 | 汉化文件索引.csv；汉化维护卷首 |
| 历史去重 | 模组/敌对/Boss/采样说明旧正文4份移为原文快照；旧HP表并入工作簿独立页；其他独有机制/证据保留 | archive/2026-10-12_资料更新前；资料库总索引 |
| 接手状态 | 交接启动词、README、实例配置、风险登记纠正旧test4/E2/E4/SNBT限制和待批口径；补FTB暂停/不开游戏 | 用户后续授权；HANDOVER§〇/二；执行状态 |

旧全量武器表的1331ID数据行逐字保持，仅增用途提示；收藏家1291件输出不重跑、不换档、不改桥。旧武器样本独有29/历史导出独有52按差集保留，不擅断为新增或删除注册项。17个解析异常只登记，不动jar。许可原声明不是全包分发审核通过。

## 三、工作簿写回与验证

五份更新表已写回原路径；首次更新时旧SvS_Boss表.xlsx被WPS占用，所以完整新表另存SvS_Boss表_更新版.xlsx，导航继续指向新表，旧表保留作历史与排序参照。后续用户要求学习旧Boss表排序，并保存关闭更新版；核对磁盘内容与备份一致后写回。六个当前工作簿共10页，逐单元格核对来源值/ID/版本文本，错误0；1366个公式（1354代理值＋12用途计数）存在且没有错误缓存。已渲染并检查各页主要区域及模组分界，设置了表头冻结、筛选、数值格式和来源列。具体SHA与行数见下表。

六表排序已统一：明细按本页模组条目数降序分组，模组名旁标数量、整组交替底色；组内武器按DPS代理值降序，实体/Boss按生命→攻击→护甲降序，缺值后置。Boss三项属性移至名称旁；模型动作/用途/风险/来源全部保留。全模组与EF汇总按历史武器数＋实体数降序；事件排除页保持说明顺序。排序及原始行内容不变校验错误0，1366公式已按新行号重新核对。口径与来源见《数据与采样说明》§一/二，未启动游戏、未恢复FTB工作。

'''
    record+='| 当前文件 | 页数 | 数据行（含支持页） | 公式 | SHA-256 |\n|---|---|---|---|---|\n'
    for b in wb['workbooks']:record+='| '+b['file']+' | '+str(b['sheets'])+' | '+str(b['data_rows'])+' | '+str(b['formula_count'])+' | '+b['sha256']+' |\n'
    record+='''
## 四、备份和原文完整性

更新前docs完整备份：E:/mcmp/backups/docs_refresh_20261012/before_docs.zip（91文件，WPS临时锁除外）。SHA-256=93b1f78c904391a65a8dfaa808016f00c976a5a9acd0d7e9035f6b1686e006ea；原清单before_manifest.json同目录。原六表XML单元格读取结果为old_workbooks.json，旧Excel另在backups/docs_refresh_20261011。

'''
    record+=f'已有归档原证据核对：{len(preserved)}份逐字节不变，异常{len(changed_archives)}；archive/README为导航维护不计原证据。冻结武器输入的数据行完全一致：{frozen_identical}。旧Boss原文件哈希仍与备份一致。\n'
    sort_backup=ROOT/'backups/docs_sheet_work/sort_backup_path.txt'
    if sort_backup.exists():record+='\n六表排序前的当前版本另行备份于'+text(sort_backup).strip()+'，含六表、工作簿数据、采样说明及更新记录；各文件SHA-256见同目录manifest.json。\n'
    record+='''
## 五、尚未完成的确认（当前不启动游戏）

现版完整注册/属性/动态NBT/EF战斗接管、最终资源覆盖、翻译显示与SLU术语、原生导航/起战/失败重试/最终归因、Boss模型动作观感、choice到账、队伍与围城等仍保留待实测。E3等spark数据与裁决，EF怪物适配搁置，F类只登记。用户恢复相应工作之前不采样、不看样、不恢复FTB重写；资料完成不是自动恢复的授权。

文件已写入本地仓库工作区；本轮没有提交或推送，也没有把此前FTB/其他会话未提交文件一并收走。两份并行新增叙事文档仅纳入导航，原文未改。所有文件用途与路径见资料库总索引；数据维护见数据与采样说明§六。
'''
    write(DOCS/'资料库更新记录_2026-10-12.md',record)
    # Validate new/current navigation links and preserve all earlier archive evidence.
    missing=[]
    for name in ['README.md','资料库总索引.md','资料库更新记录_2026-10-12.md','数据与采样说明.md','武器目录.md','敌对生物表.md','数值表_Boss.md','中立及其他类别目录.md']:
        p=DOCS/name
        for target in re.findall(r'\]\(([^)]+)\)',text(p)):
            target=unquote(target).split('#')[0]
            if not target or re.match(r'^[a-zA-Z]+:',target):continue
            if not (p.parent/target).exists():missing.append([name,target])
    boss_before=next(row['sha256'] for row in manifest if row['path']=='docs/SvS_Boss表.xlsx')
    report={'current_workbook_errors':wb['error_count'],'frozen_weapon_rows_identical':frozen_identical,'preserved_archive_count':len(preserved),'changed_archives':changed_archives,'new_archive_errors':new_archive_errors,'missing_current_links':missing,'temp_sampler_absent':not Path(r'C:\PCL 正式版 2.8.13\.minecraft\versions\test\kubejs\server_scripts\_svs_docs_snapshot.js').exists(),'locked_boss_original_unchanged':sha(DOCS/'SvS_Boss表.xlsx')==boss_before,'backup_sha256':sha(backup),'files_indexed':len(inventory),'active_files':len(active),'archive_files':len(history),'data_files':len(data)}
    write(DATA/'本轮核对结果.json',json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
    assert not changed_archives and not new_archive_errors and frozen_identical and not missing and report['temp_sampler_absent'] and report['locked_boss_original_unchanged']

if __name__=='__main__':main()
