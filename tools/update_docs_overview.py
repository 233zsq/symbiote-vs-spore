"""Update documentation navigation, source boundaries and pause state, offline."""
import collections,csv,hashlib,json,re
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).absolute().parents[1];DOCS=ROOT/'docs';DATA=DOCS/'data';DATE='2026-10-12'
def read(p):return p.read_text(encoding='utf-8-sig')
def put(p,s):p.write_text(s.rstrip()+'\n',encoding='utf-8')
def modify(name,fn):
    p=DOCS/name;s=read(p);out=fn(s)
    if out!=s:put(p,out)
def after_title(s,note):
    if note in s:return s
    a,sep,b=s.partition('\n');return a+'\n\n'+note+'\n'+b.lstrip('\n')
def mdtable(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(str(v).replace('|','／').replace('\n',' ') for v in row)+' |' for row in rows])
def main():
    d=json.loads(read(DATA/'现版资料索引.json'));c=json.loads(read(DATA/'制作资料汇总.json'));q=json.loads(read(DATA/'汇总核对.json'))
    pause='> **当前指示（2026-10-12）：FTB重写暂停，先更新制作资料；不开Minecraft、不重载实例、不做游戏采样。** 任务v2保留施工中间态；用户恢复任务工作前不继续生成、替换或测试任务。当前数据入口见 [数据与采样说明](数据与采样说明.md)。'
    guide='''# 数据与采样说明（统一口径）

> 2026-10-12离线更新。用户要求暂不开游戏；本轮没有取得成功的新游戏采样。新工作簿是“历史默认属性＋现版文件证据”的整理，不是2026-10-12运行时快照。全部来源带路径/哈希，旧数值不改写为新验收。

## 一、一个数据源，多种阅读方式

`data/现版资料索引.json`保存215个jar元数据、逐文件SHA-256、资源路径与解析记录；`data/制作资料汇总.json`保存与历史导出按ID关联后的武器、实体、Boss候选及来源。六份Excel与武器/实体/Boss Markdown是该汇总的阅读视图，不能各自维护一套不同数字。`工作簿数据.json`是重建工作簿的中间数据，不高于上游证据。

| 输出 | 目录范围 | 口径 |
|---|---|---|
| SvS_武器表.xlsx / 武器目录.md | 1354条历史武器/战斗工具；另32项仅资源候选 | 历史属性全保留；E4排除项显式标注，不拿资源模型当注册确认 |
| SvS_敌对生物表.xlsx / 敌对生物表.md | 489条 | 历史MONSTER/infected/organoid/experiments分类 |
| SvS_中立生物表.xlsx / 中立及其他类别目录.md | 388条 | 原文件名保留；其他类别不保证中立/被动 |
| SvS_Boss表.xlsx / 数值表_Boss.md | 95项候选/函数场次；208条高血量实体独立页；5条事件/排除说明 | 不是全Boss注册数，不是95场必打；模型动作评审待看样 |
| SvS_EF适配统计表.xlsx | 81个历史/兼容资源命名空间 | 历史命中数、现版JSON文件数/唯一键分列；不输出当前覆盖率 |
| Symbiote vs Spore 全模组清单.xlsx / 模组清单.md | 215 jar / 221顶层声明 | 逐jar版本/依赖/哈希/用途；取消S–F重要性分档，非强度榜 |

工作簿共10个工作表，支持筛选，冻结表头与ID列；数值列为数字，版本列为文本。来源列保留具体文件/资源路径。依据：上述两个JSON及汇总核对.json；原六表已备份。

按用户对旧Boss表的说明统一阅读顺序：武器、实体、Boss明细先按模组分组，模组按**本工作表收录条目数降序**，同数按命名空间；模组名旁显示本页数量，整组交替底色。武器组内按“攻击加值×(4＋攻速修正)”的DPS代理值降序；实体/Boss组内依次按生命→攻击→护甲降序。同值按ID，缺值置后；仅资源候选无数值，组内按ID。Boss生命/攻击/护甲列移到名称旁，模型动作等评审列完整保留。全模组清单与EF统计按历史武器数＋历史实体数降序，静态JSON文件不计入内容总数；用途统计按jar数降序，事件/排除说明保留说明顺序。排序范围只对应各表样本，不扩称模组全部内容或战斗品质。长来源单元格保留全文，选中可查看完整路径。（依据：用户本轮对SvS_Boss表.xlsx的排序说明；历史dump；工作簿数据.json的sort_kind/groups。）

## 二、属性与名称来自哪里

| 原始证据 | 范围 | 能证明什么 |
|---|---|---|
| E:/mcmp_test/i18n_work/dump_weapons.json | 1354项，文件时间2026-09-23 | 历史主手攻击加值、攻速修正；未随导出保存实际采样时刻/实例/完整版本清单 |
| 同目录dump_entities.json | 877项，同上文件时间 | 历史注册类别与默认生命/攻击/护甲；不是难度、阶段、Boss技能实际伤害 |
| 同目录ef_items.json | 历史2395项EF标记清单 | 按ID是否命中旧导出；不代表现版1354项全部适配/不适配的结论 |
| 同目录ef_native_mods.json | 历史命名空间清单 | 原采样工具的标记，不把全mod生物一律涂为100%适配 |
| 母本mods与test/mods | 215个顶层jar逐文件SHA-256相同 | 当前文件范围与声明版本；嵌套依赖/实际运行mod数另算 |
| 母本jar、OpenLoader、KubeJS语言资源 | 候选zh_cn优先，旧XLSX名称再作后备 | 目录显示名与来源；资源包实际覆盖顺序/玩家可见翻译没有新验收 |

四份历史JSON的SHA-256在制作资料汇总.json的sources中。新表只修名称/口径与证据列，历史属性不偷偷乘倍率。缺值保持空白；不能把“未匹配”写成0。

武器代理公式沿用“攻击加值×(4＋攻速修正)”，只作旧口径比较，不是含玩家基础攻击的完整面板，更不是EF连段实伤；不据此做玩家Tier。匠魂动态材料/NBT、技能、出招倍率、抗性/限伤、触及、命中与多段都未被该值覆盖。（依据：历史导出、旧全量武器表；HANDOVER§四；任务线框架§〇。）

## 三、静态资源计数与已知异常

当前武器capability JSON为3184个文件/2746个资源键，另157个weapon type文件；MobPatch为102个文件/102键。包含预置给未安装模组的兼容JSON，重复键保留各provider；不凭本扫描的遍历顺序判定最终生效版本。零JSON不能排除Java侧适配。逐项见 [EF资源索引](data/EF资源索引.csv)。（依据：现版资料索引resources；EF适配现状与动画管线§〇。）

结构扫描覆盖215个顶层jar及OpenLoader数据目录/zip：204个structure文件/201键，144个structure_set文件/141键。包含模组内minecraft命名空间覆盖；**未纳入原版客户端完整结构资源，也未作运行时合并**，因此不能与旧“274＋33”直接按差值判断删除量。键存在、集合引用、自然可达、导航、Boss激活分别验证；本轮不改worldgen。（依据：结构资源索引.csv；整合包结构表§〇/六。）

扫描记录17处解析异常：cloudertinker 1个空配方；EFMCompat 15个空兼容JSON；1个magistuarmory/gold_chivalrylance.json有尾部额外内容。异常只登记于 [资源解析异常](data/资源解析异常.csv)，不擅改jar、不据此认定游戏崩溃；有效provider与运行行为待核。注释/尾逗号容错不等于完整Forge解析器验证。（依据：现版资料索引scan_issues。）

## 四、旧表与收藏家标签为什么不直接合并

`全量武器表.md`仍是tools/gen_collect_tags.py的冻结输入，1331个历史ID；本次1354项历史导出相对它独有52、旧表独有29（包含已移除模组）。两份样本不能硬并为现版注册总量。逐ID差集见制作资料汇总.json的legacy_weapon_input。旧表保留路径、列和数据行，只增加用途提示；新任务选材先查武器目录与状态列。

已批E4输出仍为1291件，t1～t5=257/289/226/283/236；不因文档更新重跑生成器、不换档、不改桥。t1现版游戏复核仍待用户有合适窗口后另行允许；“257与此前运行时一致”不等于本轮新测。E4排除的11个efn旧ID在武器历史视图中保留红线式状态文字，不恢复到任务/标签。（依据：E4_收藏家标签差集清单§一/二；验收与风险登记§二。）

## 五、Boss资料怎么辅助后续任务

候选来自Boss Checklist内置支持ID与历史实体交集、SLU boss_命名候选，以及五包研究E-二轮/主线深化研究E03～E09的明确对象；支持表/命名仅是线索，不代表品质通过。两项FA函数场次不伪造实体ID；母巢事件、测试/未完成对象另页登记。被诅咒者/斯库拉未定选；薪王化身不能回填终局。Boss模型与动作→特效技能→取得/重试/判胜→最后数值的顺序继续有效。（依据：主线深化研究§四；任务参考研究§四E-二轮；用户已答复。）

暂停期间只可离线补进度、模型/动作引用与取得线索；不得把找到kill进度或loot表写成“已验通入口/整场成功”。任务恢复须用户明确指示，不能因本资料整理完成自动启动游戏或继续写任务。

## 六、维护与回退

离线更新链：tools/refresh_docs_catalog.py --static-only → tools/assemble_docs_reference.py（含order_docs_workbooks分组排序）→ Artifact Tool工作簿构建 → tools/verify_docs_reference.py核对。仅调整排序时可运行tools/order_docs_workbooks.py，无需重新扫描jar。后续获准重新游戏采样时，先保留日期/实例/整套版本/导出方法/哈希，增加新的数据层再替换历史标签；不能仅改表头日期。

更新前完整文档备份：E:/mcmp/backups/docs_refresh_20261012/before_docs.zip；SHA-256=93b1f78c904391a65a8dfaa808016f00c976a5a9acd0d7e9035f6b1686e006ea。旧数值/模组/采样说明四文另保留在archive/2026-10-12_资料更新前；历史档案不直接用于施工。全部文件去向见资料库总索引.md，核对结果见资料库更新记录_2026-10-12.md。
'''
    guide=guide.replace('SvS_Boss表.xlsx /','SvS_Boss表_更新版.xlsx /')
    guide+='\n首次更新时原SvS_Boss表.xlsx被WPS占用，因此当前更新视图另存SvS_Boss表_更新版.xlsx，入口继续指向更新版；旧原表保留作历史与排序参照。本轮用户保存关闭更新版后已核对文件与排序前备份一致，再写回更新版。\n'
    put(DOCS/'数据与采样说明.md',guide)
    modify('全量武器表.md',lambda s:after_title(s,'> **用途更新（2026-10-12）：本文件仅为收藏家标签生成器的冻结历史输入，保留1331个ID及原五列。** 当前制作选材查 [武器目录](武器目录.md) / SvS_武器表.xlsx；两份不同样本不硬并。本轮不重跑标签，E4仍为1291件。数值时效见 [数据与采样说明](数据与采样说明.md)§二/四。'))
    # Keep old pipeline research, but current counts have one explicit leading owner.
    ef0='''## 〇、2026-10-12现版离线核对（当前计数入口）

母本/test各215顶层jar逐SHA-256相同；EF仍20.14.17。扫描jar＋OpenLoader数据资源得武器JSON3184文件/2746键，weapon type另157文件；MobPatch102文件/102键（SLU74、EFMCompat21、w.o.w6、Epic Fight Villages Guard兼容件1）。compat可能包含未安装mod的预置引用，不能当现版武器/实体数；重复provider保留，不冒称最终覆盖顺序。

来源：[EF资源索引](data/EF资源索引.csv)、现版资料索引.json resources；统计：[更新后的EF表](SvS_EF适配统计表.xlsx)。旧EF红色/百分比仅代表历史导出。17处资源解析异常见数据与采样说明§三，其中空兼容JSON/尾部额外内容均未改jar，不能推断游戏效果。

下面保留10-07/10-09的机制调查、特定包统计及动画管线；不是本轮新采样或新推荐。模型动作质量待用户看样，EF怪物适配继续搁置；本轮不写任何适配JSON、不启动游戏。

'''
    modify('EF适配现状与动画管线.md',lambda s:s if '## 〇、2026-10-12' in s else s.replace('## 一、',ef0+'## 一、',1))
    sr=[r for r in d['resources'] if r['kind']=='structure'];sets=[r for r in d['resources'] if r['kind']=='structure_set'];byid=collections.defaultdict(list);refer=collections.defaultdict(list)
    for r in sr:byid[r['id']].append(r['source'])
    for r in sets:
        for entry in (r.get('data') or {}).get('structures',[]):
            if isinstance(entry,dict):refer[entry.get('structure','')].append(r['id'])
    java=read(ROOT/'svs_tweak/src/main/java/com/svs/tweak/structure/StructureDensityRules.java')
    groups={}
    for key in ['BLACKLIST','WHITELIST','IGNORE','IGNORE_PREFIX']:
        m=re.search(r'\b'+key+r'\s*=\s*Set\.of\((.*?)\);',java,re.S);groups[key]=set(re.findall(r'"([^"]+)"',m[1])) if m else set()
    def cls(id):
        if id in groups['BLACKLIST']:return '黑名单'
        if id in groups['WHITELIST']:return '白名单'
        if id in groups['IGNORE'] or any(id.startswith(p) for p in groups['IGNORE_PREFIX']):return '忽略密度检查'
        return '默认淡化'
    struct0='''## 〇、2026-10-12现版离线资源范围

215个顶层jar＋OpenLoader数据目录/zip扫描：**204个structure文件/201键；144个structure_set文件/141键**。模组内minecraft命名空间覆盖计入，但原版客户端完整资源未计；不是运行时注册总数，不与9-30“274＋33”直接作增删比较。当前全部provider、集合spacing/separation及引用见 [结构资源索引](data/结构资源索引.csv)，当前键清单见§六。

§一/二保留已批密度规则；§三是9-30历史样本，§四是已被后续任务稿替代的路线示意，不能当现行必打长链。密度白名单21个**不等于21个必去任务**，也不证明各结构必刷或能定位。全部已批worldgen规则维持，本轮不改包/生成；源码分类来源：svs_tweak/.../StructureDensityRules.java。数据边界见数据与采样说明§三。

'''
    def struct_update(s):
        if '## 〇、2026-10-12' not in s:s=s.replace('## 一、',struct0+'## 一、',1)
        s=s.replace('## 三、全量结构表（按命名空间）','## 三、9-30历史结构表（按命名空间）')
        s=re.sub(r'## 四、[^\n]+', '## 四、历史线性路线示意（已被后续任务稿替代）',s,count=1)
        s=s.replace('无集合引用的结构不自然生成（地图定位/工具 jig，已略）','未发现集合引用的结构不据此保证标准自然生成；Java/函数路径仍需另核（原表略去的项目见当前索引）')
        if '## 六、2026-10-12' not in s:s+='\n\n## 六、2026-10-12当前结构键清单\n\n扫描键不等于自然可达；分类按仓库现源码读取，不改变裁决。多provider并列，未判最终加载优先级。\n\n'+mdtable(['结构键','源码密度分类','发现的结构集引用','资源来源'],[[id,cls(id),'；'.join(sorted(set(refer[id]))) or '未匹配标准结构集引用','；'.join(sources)] for id,sources in sorted(byid.items())])
        return s
    modify('整合包结构表.md',struct_update)
    # Refresh static translation count without pretending to have tested display order.
    langs=[]
    MOTHER=Path(r'E:\SvS_整合包_副本')
    for p in sorted((MOTHER/'config/openloader/resources').rglob('zh_cn.json')):
        try:entries=json.loads(read(p));langs.append([p.relative_to(MOTHER).as_posix(),len(entries),hashlib.sha256(p.read_bytes()).hexdigest()])
        except ValueError:langs.append([str(p),'解析失败',''])
    with (DATA/'汉化文件索引.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['mother_relative_path','entry_count','sha256']);w.writerows(langs)
    langcount=sum(x[1] for x in langs if isinstance(x[1],int))
    modify('汉化维护.md',lambda s:after_title(s,f'> **2026-10-12离线复核：母本OpenLoader资源目录有{len(langs)}份zh_cn.json，文件内键条目合计{langcount}（不跨文件去重）。** 逐文件路径/哈希见 [汉化文件索引](data/汉化文件索引.csv)。目录名称按本地候选资源更新；未验证最终加载顺序、占位符显示或40个SLU boss soul术语评审，不能当100%汉化结论。下文原清单为仓库10-09口径；当前来源以新索引为准。'))
    modify('实例配置说明.md',lambda s:after_title(s,pause).replace('旧实例，保留至用户明确批准删除','已由用户删除；无归档留痕，不再安排删除').replace('**只由用户游戏编辑器生成/修改SNBT**；AI只读真实ID、写设计稿和桥','2026-10-11已授权程序生成/校验SNBT；当前重写暂停，不继续施工').replace('阶段ID方案仍待批','v2阶段ID已生成；当前任务施工暂停').replace('四阶段重编、淬魔钢坯目标和存量迁移都按任务线实装核对二待批，不按旧五阶段示例直接替换','v2已回填四阶段ID；具体中间态见FTB任务重置_v2，功能未验，当前暂停').replace('weapon_balance.js仍是未部署骨架，等裁决','weapon_balance.js已移docs/archive/，不补入包'))
    modify('验收与风险登记.md',lambda s:after_title(s,pause).replace('副本/test/遗留test4','副本/test；test4已由用户删除，不再是同步目标').replace('启动→test已验；test4仍待批准删除','启动→test已验；test4已由用户删除，无归档留痕').replace('未经用户明确批准继续保留test4；批准后按计划核对范围再处理','不重复安排删除或补造归档完成证据；需找回时由用户查回收站').replace('静态核对已有，具体提案待批','v2已加载16章210节点，25项pending；功能未验；当前暂停').replace('先批注再编辑器SNBT，再桥激活；实例内验证完成/发奖/重登/多人，不能只验文件存在','恢复后按用户已授权的程序生成/校验流程；实例内完成/发奖/重登/多人仍需另验，当前不开游戏'))
    modify('候选与变更清单.md',lambda s:after_title(s,pause).replace('具体id映射待批','v2已生成四阶段ID，功能验收未完成').replace('E2 weapon_balance骨架、E3 Inquisition三档、E4标签过滤、EF怪物适配五问、test4删除、M2八点均转','E2已归档、E4已执行、test4已由用户删除；余E3 Inquisition三档、EF怪物适配五问与任务功能缺口均查').replace('E1已收口。未决项','E1已收口；合入初版方案见待裁决清单10-11批复，svs_lab实验不能算母本已合入。未决项'))
    modify('待裁决清单.md',lambda s:after_title(s,pause).replace('## 一、M2 八批注点（批完即可解锁编辑器实装）','## 一、M2 八批注点（10-11已批历史记录）').replace('## 五、一句话裁决（各一句话回复即可）','## 五、一句话裁决（已批记录，执行状态另查）').replace('## 六、非裁决·行动项（需要你做，不用批）','## 六、原行动项（当前暂停，不据此开游戏）').replace('- **E2/E3**：weapon_balance.js 见"决-2"；三档调参等 spark 数据。','- **E2**已移archive，不补入包；**E3**三档调参等spark数据与裁决。本轮不采样。'))
    modify('开发计划_执行状态.md',lambda s:s.replace('- 本轮只推进资料核对、重新采样、工作簿与文档更新、重复及历史口径收口。采样工具只读注册表/默认属性/EF能力，写日志后移除，不改玩法与任务。','- 用户随后明确“别开我的世界，现在尽量避免开游戏”；本轮转为纯离线更新。临时采样脚本已移除，未取得成功的新运行时数据；不再启动/重载实例。六份工作簿、模组/武器/实体/Boss/EF/结构资料及总索引已更新，证据与剩余缺口见《资料库更新记录_2026-10-12.md》。'))
    modify('HANDOVER.md',lambda s:after_title(s,pause).replace('更新：**2026-10-09（文档整理；游戏验收记录截至10-07）**','更新：**2026-10-12（离线资料更新；当前任务暂停，游戏证据按各记录日期）**').replace('| `docs/整合包结构表.md` | 9-30采样274模组结构+33原版结构；10-03裁决已回填，仍冻结worldgen |','| `docs/整合包结构表.md` | 10-12当前资源键索引＋9-30历史样本；密度裁决保留，worldgen冻结 |').replace('| `docs/数据与采样说明.md` | 6份xlsx＋数值md的口径登记；EFS-ISS无item，不因其入包机械重采 |','| `docs/数据与采样说明.md` | 10-12离线更新的六表/目录/统一JSON源；历史属性与现版静态证据分列；完整入口：资料库总索引.md |'))
    put(DOCS/'GLM_交接启动词.md','''# 给执行AI的交接启动词（当前暂停状态）

> 2026-10-12更新。下列文字说明接手边界，不自动授权新的改包、任务施工或开游戏。

```text
你接手Minecraft 1.20.1 Forge整合包Symbiote vs Spore。先读docs/HANDOVER（四裁决、五技术边界、七队列）、任务文档.txt、魔改设计决议（变更记录优先）、开发计划与执行状态，再查docs/README、资料库总索引、数据与采样说明。

当前用户要求：FTB任务重写暂停，先更新整合资料。用户明确“别开我的世界，现在尽量避免开游戏”，因此不得启动/重载test、svs_lab或其他实例做采样、功能验收、Boss看样。先做离线工作，等用户明确恢复相应工作后再继续。

母本E:/SvS_整合包_副本；开发实例C:/PCL 正式版 2.8.13/.minecraft/versions/test；仓库E:/mcmp；工具E:/mcmp_test。test4已由用户删除，核查无归档留痕，不再安排删除。svs_lab为独立游戏目录实验，不能回灌母本。同步规则母本→test→仓库；本次资料更新不修改玩法，不触发同步。

现版静态证据：母本/test各215个顶层jar，221顶层声明，逐文件SHA-256全同。六份xlsx与武器/实体/Boss目录已按统一源更新；历史1354武器/工具、877实体默认属性来自文件时间9-23的导出，不能当10-12新采样。资源JSON、历史EF标记和运行时动作必须分层。Boss表有95候选/函数场次，不是95必打或全量注册Boss数。当前目录/版本见模组清单，数据源见docs/data/制作资料汇总.json。

FTBv2保留施工中间态：16章210节点、25 pending；此前加载/引用审计通过（missing=[]），起步、计数、奖励、多人、全线未验。程序生成和校验SNBT已获用户后续直接授权，覆盖旧编辑器唯一限制；但当前暂停，不运行构建器、不替换任务、不继续功能测试。旧M2节点数和待批语句只作历史，不覆盖v2。不要提交此前FTB未提交改动充作资料更新。

已处置：E1空配置合法{}；E2weapon_balance骨架移archive不补包；E4标签1291件（257/289/226/283/236），本轮未重跑，现版复核仍待窗口。待测：围城失守/回拨/两人同村；TEMP清理等收敛。E3等spark证据和裁决；EF怪物适配搁置；F1～F4只登记，实测触发再处理。合入初版批准条件见待裁决清单，母本与svs_lab的实际部署要分开记。

不得升级/降级EF20.14.17；原版配方/数值/门禁政策待定；worldgen冻结（已裁决项除外）；不恢复Gateways/Placebo、武器锁或脚本限伤；排行氛围化。主线Boss每阶段少数，表现优先模型动作，其次特效技能，最后数值。终局比较被诅咒者/斯库拉未定选；薪王化身不得回填为终局；夜临/WOC只允许提出替换，名单看样后定。

接手先看git状态和最近提交，保留其他会话文件；只提交本次明确范围，数据目录可复现视图不能混作游戏实测。按文件/资源→加载→功能→用户验收分层写证据；archive是历史，不从旧启动词自动执行。本次具体工作由用户另行指定。
```

依据：HANDOVER§〇/二/四/五/七；开发计划_执行状态当前切换；待裁决清单卷首；数据与采样说明§一～六；用户最新直接指示。
''')
    put(DOCS/'交接启动词_规划AI.md','''# 给规划AI的交接启动词

> 2026-10-12更新；用于后续规划，不自动恢复FTB任务施工。

```text
你负责Symbiote vs Spore规划。当前FTB重写暂停，资料已做离线整合；用户明确暂不开Minecraft。只读母本、test、代码与参考包，不启动游戏，不把资源扫描写成运行时/战斗手感验收。交付范围由用户指定。

先读docs/README和资料库总索引，再依序HANDOVER四/五/七、任务文档、魔改设计决议变更记录、任务线框架、开发计划与执行状态。查数据先读数据与采样说明：当前215jar/221声明是文件事实；1354武器/877实体是历史属性；Boss95项为筛选候选及函数场次而非全注册总数。不要继续从旧全量武器表选已移除mod；它仅为标签生成器冻结输入。

机制继续有效：四阶段、四职业、四段式、检测模式三选一，通常称呼冒险者。新的叙事材料是参考文案，机制冲突先上报，不据文案新增物品/任务/官方同源设定。Boss以模型动作优先，再特效技能/可玩流程/数值；终局被诅咒者与斯库拉未定选，SLU薪王化身不作终局，夜临/WOC名单仍待看样。每阶段少数必打，其余可选。

程序生成/校验SNBT已获后续明确授权；当前暂停施工与测试，不能从旧编辑器限制或旧M2数量倒改现有v2。保留16章210节点25 pending中间态，仅加载/引用审计已过，功能未验。test4已由用户删除，无归档留痕；E2已归档、E4已收紧1291，不能重复列待裁决。

EF20.14.17固定，原版政策待定、worldgen冻结；不恢复旧五阶段/暮色主线、Gateways/Placebo、武器锁、脚本限伤或数值Tier表。每个新增提案写出处、优先级、依赖、验收草案、待用户裁决/实测；不排具体日期。不确定标待核，设计改变需用户重新裁决；用户恢复前不进入FTB重写。
```

依据：HANDOVER、开发计划_执行状态当前切换、数据与采样说明、主线深化研究§四、任务线框架及用户最新指示。
''')
    put(DOCS/'README.md','''# Symbiote vs Spore 制作资料入口

> 更新2026-10-12。**FTB重写暂停；当前先整合资料。用户要求尽量不开游戏，本轮改用离线证据。** EF固定20.14.17；母本/test各215顶层jar、221顶层声明，逐文件SHA-256全部相同。没有成功的新游戏采样，不把旧数值标成现版实测。（来源：现版资料索引.json；开发计划_执行状态当前切换；用户直接指示。）

## 先读什么

| 顺序 | 文档 | 用途 |
|---|---|---|
| 1 | [HANDOVER](HANDOVER.md) | §四裁决、§五技术边界、§七队列；§〇当前暂停优先 |
| 2 | [任务文档](任务文档.txt) / [魔改设计决议](魔改设计决议.md) | 理念与机制；变更记录高于旧正文 |
| 3 | [框架](任务线框架规格书_v1.md) / [计划](开发计划_v1.md) / [执行状态](开发计划_执行状态.md) | 已批边界、依赖与实际完成层级 |
| 4 | [数据与采样说明](数据与采样说明.md) | 六表、历史属性、现版资源、冻结标签输入怎样使用 |
| 5 | [全文件索引](资料库总索引.md) / [本轮记录](资料库更新记录_2026-10-12.md) | 每个文件现行/资料/暂停/历史用途、备份与验证 |

## 制作资料（先查这些）

| 查什么 | Markdown | 可筛选数据 |
|---|---|---|
| 当前模组、版本、用途、依赖声明 | [模组清单](模组清单.md) | [全模组Excel](Symbiote%20vs%20Spore%20全模组清单.xlsx) |
| 武器/工具、名称、历史属性、取得线索 | [武器目录](武器目录.md) | [武器Excel](SvS_武器表.xlsx) |
| 敌对类别/其他类别实体 | [敌对目录](敌对生物表.md) / [其他类别目录](中立及其他类别目录.md) | [敌对Excel](SvS_敌对生物表.xlsx) / [原中立Excel](SvS_中立生物表.xlsx) |
| Boss候选、终段判胜、看样及排除项 | [Boss入口](数值表_Boss.md) / [表现研究](主线深化研究_全模组与战斗筛选.md)§四 | [Boss Excel](SvS_Boss表.xlsx) |
| EF资源与历史标记 | [EF管线](EF适配现状与动画管线.md) | [EF Excel](SvS_EF适配统计表.xlsx) / [逐资源索引](data/EF资源索引.csv) |
| 结构键、集合、密度裁决 | [结构表](整合包结构表.md)§〇/六 | [结构资源索引](data/结构资源索引.csv) |
| 语言文件与待审术语 | [汉化维护](汉化维护.md) | [文件/键数/哈希](data/汉化文件索引.csv) |

数据统一源：[制作资料汇总](data/制作资料汇总.json)，底层证据：[现版资料索引](data/现版资料索引.json)。工作簿与MD均为阅读视图。旧 [全量武器表](全量武器表.md) 仅保留为收藏家标签生成器冻结输入，本轮不换输入、不重跑1291件标签。Boss候选不是强度排名或必打清单；注册类别不等于行为；资源存在不等于现版注册/动作正确。出处与限制详见数据与采样说明§二～五。

## 任务恢复后才使用

当前 [FTB重建中间态](FTB任务重置_v2.md)：16章210节点/25 pending；已加载并做引用审计，功能和全线尚未通过。保留 [源](questbook_v2.json)、[ID映射](FTB任务v2_ID映射.json)、[节点验收目录](FTB任务v2_节点与验收目录.md)，不继续生成/替换/测试。程序生成SNBT已获后续用户明确授权；暂停并未撤销机制裁决，也不表示允许现在施工。

设计资料：[总稿](任务设计总稿_v1.md)、[序章稿](任务设计稿_序章_觉醒_v1.md)、[阶段Ⅰ稿](任务设计稿_阶段Ⅰ_启程_v1.md)、[M2历史核对](任务线实装核对.md)、[M2.4施工记录](M2.4_施工记录_2026-10-11.md)。参考：[五包FTB](任务参考研究_五整合包FTB.md)、[武器匠魂](武器线与匠魂节奏_参考综合.md)、[全模组战斗筛选](主线深化研究_全模组与战斗筛选.md)。叙事：[世界观资料](世界观设定_SvS.md)、[章节文案](剧情文案_章节引言与里程碑_v1.md)，与机制冲突须用户裁决，不因文案存在自动回填任务。

## 其他工作与接手

| 工作 | 入口 |
|---|---|
| 验收/风险/已批条件 | [验收与风险](验收与风险登记.md)、[批复记录](待裁决清单.md)、[执行状态](开发计划_执行状态.md) |
| 配置/战斗/共生体 | [实例配置](实例配置说明.md)、[战斗手感](战斗手感基准.md)、[共生体配置](Symbiote配置调频设计.md)、[铁魔法禁用](铁魔法禁用清单.md) |
| 优化及新模组 | [综合审查](刀光与新增模组6_优化合入综合审查.md)、[Rapid](Rapid_Optimization_合入评估与执行交接.md)、[B0](合入_B0基线记录.md)、[隔离实验](合入_隔离实验实例_svs_lab.md)、[候选变更](候选与变更清单.md) |
| 发布证据 | [许可覆盖状态](开源协议审查.md)，元数据license不等于全包分发已通过 |
| AI接手 | [执行启动词](GLM_交接启动词.md)、[规划启动词](交接启动词_规划AI.md)，均已补暂停/不开游戏要求 |
| 历史 | [归档说明](archive/README.md)、[原整理记录](文档整理记录.md)、[本轮记录](资料库更新记录_2026-10-12.md) |

test4已由用户删除且无归档留痕；E1已收口、E2已归档、E4已收紧；E3等spark数据/裁决；围城失守/回拨/多人待测；EF怪物适配搁置；F类只登记。原版政策待定、worldgen冻结、EF锁版本、排行氛围化继续有效。（来源：HANDOVER§二/四/七；验收与风险登记。）
''')
    p=ROOT/'README.md';s=read(p).replace('**项目仍在制作中。任务正在整体重建，当前源码不代表已完成全流程游戏验收的发行版。**','**项目仍在制作中。FTB任务重写暂停，先更新制作资料；当前源码不代表已完成全流程游戏验收的发行版。**').replace('（2026-10-11 核查）','（2026-10-12离线核查，逐jar SHA-256一致）').replace('| 任务系统 | 旧五阶段架构整体替换为 v2；文件构建、机制接桥和游戏验收分别登记 |','| 任务系统 | v2为施工中间态，当前重写暂停；加载/引用审计通过，功能与全线未验 |')
    if '资料库离线更新' not in s:s+='\n\n资料库离线更新（2026-10-12）：五份数值表＋全模组表已统一来源，并更新模组/武器/实体/Boss/EF/结构目录。查看 [资料入口](docs/README.md) 与 [数据边界](docs/数据与采样说明.md)。用户要求暂不开游戏，未知注册/行为/手感保持待实测；资料整理完成不自动恢复FTB重写。\n'
    put(p,s)
    modify('README.md',lambda s:s.replace('(SvS_Boss表.xlsx)','(SvS_Boss表_更新版.xlsx)'))
    print(json.dumps({'translation_files':len(langs),'translation_entries':langcount,'structure_keys':len(byid)},ensure_ascii=False))

if __name__=='__main__':main()
