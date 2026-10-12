"""Reconcile offline evidence into the documentation catalogs and XLSX input.
Does not write pack files, quest files, or collector tags. Python 3.12 stdlib only.
"""
import collections, csv, hashlib, json, re, zipfile
from pathlib import Path
from order_docs_workbooks import apply_group_order

ROOT=Path(__file__).absolute().parents[1]; DOCS=ROOT/'docs'; DATA=DOCS/'data'
HIST=Path(r'E:\mcmp_test\i18n_work'); MOTHER=Path(r'E:\SvS_整合包_副本')
DATE='2026-10-12'; HIST_LABEL='历史导出；文件时间2026-09-23，实际采样时刻未记录'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,s):p.write_text(s.rstrip()+'\n',encoding='utf-8')
def clean(v):return str(v or '').replace('|','／').replace('\n',' ').strip()
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(clean(x) if x is not None else '—' for x in row)+' |' for row in rows])
def backup(name):
    p=DOCS/name; dest=DOCS/'archive/2026-10-12_资料更新前'/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    if p.exists() and not dest.exists():dest.write_bytes(p.read_bytes())
def sheet(name,title,note,headers,rows,widths=None,numeric=None,formulas=None):return dict(name=name,title=title,note=note,headers=headers,rows=rows,widths=widths or [],numeric=numeric or [],formulas=formulas or {})
def num(x):
    try:return float(x)
    except (TypeError,ValueError):return None

def main():
    d=read(DATA/'现版资料索引.json'); resources=d['resources']; models=set(d['model_item_ids'])
    mods={m['id']:j for j in d['mods'] for m in j['declarations']}; lang=d['translations']
    old=read(ROOT/'backups/docs_refresh_20261012/old_workbooks.json'); fallback={}
    for b in old.values():
        for s in b['sheets']:
            for row in s['rows']:
                vals={re.sub(r'\d','',k):v['value'] for k,v in row.items()}
                if isinstance(vals.get('B'),str) and ':' in vals['B'] and vals.get('C'):fallback[vals['B']]=vals['C']
    def name(id,kind):
        ns,p=id.split(':',1); keys=[kind+'.'+ns+'.'+p.replace('/','.'),'block.'+ns+'.'+p.replace('/','.')]
        for key in keys:
            if 'zh_cn' in lang.get(key,{}) and clean(lang[key]['zh_cn']['text']):return clean(lang[key]['zh_cn']['text']),lang[key]['zh_cn']['source']
        if id in fallback:return clean(fallback[id]),'旧XLSX中文名；现版语言键未匹配'
        for key in keys:
            if 'en_us' in lang.get(key,{}) and clean(lang[key]['en_us']['text']):return clean(lang[key]['en_us']['text']),lang[key]['en_us']['source']+'（未匹配中文）'
        return id,'未匹配名称，待核'
    def version(ns):return ' / '.join(m['version'] for m in mods.get(ns,{}).get('declarations',[]) if m['id']==ns) or ('1.20.1' if ns=='minecraft' else '未见同名顶层mod声明')
    def owner(ns):return ' / '.join(m['name'] for m in mods.get(ns,{}).get('declarations',[]) if m['id']==ns) or ns
    caps=collections.defaultdict(list); patches=collections.defaultdict(list); recipe_out=collections.defaultdict(list); loot_out=collections.defaultdict(list); adv_entity=collections.defaultdict(list)
    for r in resources:
        if r['kind']=='weapon_capability':caps[r['id']].append(r)
        if r['kind']=='mobpatch':patches[r['id']].append(r)
        if r['kind']=='recipe':
            result=r.get('result'); rid=result.get('item') if isinstance(result,dict) else result if isinstance(result,str) else None
            if rid:recipe_out[rid].append(r['id']+' @ '+r['source'])
        if r['kind']=='loot_table':
            for item in r.get('items',[]):loot_out[item].append(r['id']+' @ '+r['source'])
        if r['kind']=='advancement':
            for criterion in (r.get('data') or {}).get('criteria',{}).values():
                if criterion.get('trigger')!='minecraft:player_killed_entity':continue
                for ent in re.findall(r'"type"\s*:\s*"([a-z0-9_.-]+:[a-z0-9_./-]+)"',json.dumps(criterion.get('conditions',{}))):adv_entity[ent].append(r['id'])
    ef=set(read(HIST/'ef_items.json')); native=set(read(HIST/'ef_native_mods.json'))
    e4={'efn:'+x for x in ['exsiliumgladius_e','fire_exsiliumgladius_e','crimson_moon_e','meen_spear_e','nf_shortsword_2_e','nf_shortsword_e','air_tachi_e','crescent_moon_e','arc_tachi','flag_bearer','flag_bearer_e']}
    weapons=[]
    for id,damage,speed in read(HIST/'dump_weapons.json'):
        ns=id.split(':')[0]; nm,nms=name(id,'item'); static=[]
        if id in models:static.append('物品模型')
        if id in caps:static.append('EF武器JSON')
        sources=recipe_out[id]+loot_out[id]
        if sources:static.append('配方/掉落引用')
        weapons.append({'id':id,'namespace':ns,'name':nm,'version':version(ns),'damage_add':num(damage),'speed_add':num(speed),'historical_ef':id in ef,'static':'+'.join(static) or '未匹配资源；不等于不存在','status':'E4已排除，勿用于任务' if id in e4 else '历史注册；现版运行时待核','types':sorted(set(clean((r.get('data') or {}).get('type')) for r in caps[id] if r.get('data'))),'source':str(HIST/'dump_weapons.json'),'name_source':nms,'resource_sources':[r['source'] for r in caps[id]],'acquisition_refs':sources})
    weapons.sort(key=lambda x:(x['namespace'],x['id']))
    entities=[]
    hostile_cats={'MONSTER','infected','organoid','experiments'}
    for id,cat,hp,attack,armor in read(HIST/'dump_entities.json'):
        ns=id.split(':')[0];nm,nms=name(id,'entity')
        entities.append({'id':id,'namespace':ns,'name':nm,'category':cat,'hp':num(hp),'attack':num(attack),'armor':num(armor),'version':version(ns),'hostile_bucket':cat in hostile_cats,'historical_ef_namespace':ns in native,'patch_sources':[r['source'] for r in patches[id]],'kill_advancements':sorted(set(adv_entity[id])),'name_source':nms,'source':str(HIST/'dump_entities.json')})
    entities.sort(key=lambda x:(x['namespace'],x['id'])); entity_by={e['id']:e for e in entities}
    boss_ids=set(); boss_evidence=collections.defaultdict(list)
    checklistjar=MOTHER/'mods/boss_checklist-forge-5.2.0.jar'
    with zipfile.ZipFile(checklistjar) as z:
        for x in json.loads(z.read('data/boss_checklist/server_bosses_ids.json')):
            if x['id'] in entity_by:boss_ids.add(x['id']);boss_evidence[x['id']].append('Boss Checklist内置支持表∩历史实体；非主线授权')
    explicit={
      'cataclysm':['ender_guardian','netherite_monstrosity','ignis','the_harbinger','the_leviathan','ancient_remnant','maledictus','scylla'],
      'bloodandmadness':['father_gascoigne','gascoigne_beast','micolash'],
      'nightfall_invade':['arterius','scarlet_hunter'],
      'woc_remastered':['zertar','mechx_12'],
      'mowziesmobs':['ferrous_wroughtnaut','frostmaw','umvuthi','sculptor'],
      'eeeabsmobs':['nameless_guardian','corpse_warlock'],
      'jerotesvillage':['sediment_lord']}
    for ns,names in explicit.items():
        for local in names:
            id=ns+':'+local;boss_ids.add(id);boss_evidence[id].append('任务参考研究_五整合包FTB§四E-二轮；overlord玩家击杀进度' if ns=='jerotesvillage' else '主线深化研究§二E03～E09/四；资源/字节码研究')
    for e in entities:
        if e['namespace']=='slu' and e['id'].split(':')[1].startswith('boss_'):
            boss_ids.add(e['id']);boss_evidence[e['id']].append('SLU boss_命名候选；真实性/品质待核')
    bosses=[]
    for id in sorted(boss_ids):
        e=entity_by.get(id);ns=id.split(':')[0];nm,nms=name(id,'entity');local=id.split(':')[1]
        purpose='可选候选；未定必打'
        if id in ('cataclysm:maledictus','cataclysm:scylla'):purpose='终局比较候选；用户未定选'
        elif id=='slu:boss_soul_of_cinder':purpose='用户否决终局；可选/其余用途待定'
        elif ns=='slu':purpose='Ⅳ章池候选；人选/数量待批'
        elif id in ('bloodandmadness:father_gascoigne','bloodandmadness:gascoigne_beast'):purpose='Ⅲ完整变身战候选；仅判终段'
        elif ns in ('nightfall_invade','woc_remastered'):purpose='已获准提替换；名单看样后定'
        elif id=='jerotesvillage:sediment_lord':purpose='Ⅱ二轮代表战候选；原生入口/重试待核'
        warnings=[]
        if 'gascoigne' in id:warnings.append('人形移除不算完整胜利')
        if e and e['category']=='MISC':warnings.append('MISC不表示无战斗/非Boss')
        if e is None:warnings.append('历史属性无记录；不可填0')
        local_terms={local,local.replace('_','')}
        if local=='father_gascoigne':local_terms.add('gascoigne')
        if local=='gascoigne_beast':local_terms.add('beast_gascoigne')
        visuals=[v['source']+'!/'+v['path'] for v in d['visual_assets'] if '/'+ns+'/' in v['path'] and any(t in v['path'].lower() for t in local_terms)]
        patch=patches.get(id,[])
        bosses.append({'id':id,'name':nm,'namespace':ns,'purpose':purpose,'hp':e['hp'] if e else None,'attack':e['attack'] if e else None,'armor':e['armor'] if e else None,'evidence':boss_evidence[id],'model_action_review':'待用户看样；资源数量不评价品质','visual_refs':visuals,'patch_refs':[r['source'] for r in patch],'kill_advancements':sorted(set(adv_entity[id])),'warning':'；'.join(warnings),'name_source':nms})
    for key,nm in [('lothran','Lothran'),('sunflower_avatar','向日葵化身')]:
        bosses.append({'id':'函数场次：'+key,'name':nm,'namespace':'final_adversaries_lite','purpose':'可选函数Boss；非普通实体','hp':None,'attack':None,'armor':None,'evidence':['主线深化研究§二E08；data/final_adversaries/functions/adjust_bosses/spawn_'+key+'_at_nearest_spawnpoint.mcfunction'],'model_action_review':'待用户看样','visual_refs':[],'patch_refs':[],'kill_advancements':[],'warning':'没有普通Boss实体ID；不可直接套kill；胜利事件待核','name_source':'主线深化研究§二E08'})
    highhp=[e for e in entities if e['hp'] is not None and e['hp']>=100]
    old_weapons={m.group(1) for m in re.finditer(r'^\|\s*`?([a-z0-9_.-]+:[a-z0-9_./-]+)`?\s*\|',(DOCS/'全量武器表.md').read_text(encoding='utf-8'),re.M)}
    source_files=[]
    for f in ['dump_weapons.json','dump_entities.json','ef_items.json','ef_native_mods.json']:
        p=HIST/f;source_files.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'count':len(read(p)),'date_basis':'文件时间2026-09-23；采样时刻/实例未随数据保存'})
    catalog={'schema':1,'as_of':DATE,'method':'offline; no successful new runtime sample','sources':source_files,'jars':d['mods'],'weapons':weapons,'entities':entities,'boss_candidates':bosses,'high_hp_entity_ids':[e['id'] for e in highhp],'legacy_weapon_input':{'path':'docs/全量武器表.md','count':len(old_weapons),'current_history_only':sorted(set(w['id'] for w in weapons)-old_weapons),'legacy_only':sorted(old_weapons-set(w['id'] for w in weapons))},'counts':{'jars':len(d['mods']),'declarations':len(mods),'weapons_historical':len(weapons),'entities_historical':len(entities),'hostile_bucket':sum(e['hostile_bucket'] for e in entities),'other_category':sum(not e['hostile_bucket'] for e in entities),'boss_candidate_entries':len(bosses),'high_hp_entries':len(highhp),'weapon_json_files':sum(r['kind']=='weapon_capability' for r in resources),'weapon_json_keys':sum(bool(v) for v in caps.values()),'mobpatch_files':sum(r['kind']=='mobpatch' for r in resources),'mobpatch_keys':sum(bool(v) for v in patches.values())},'scan_issues':d['scan_issues']}
    write(DATA/'制作资料汇总.json',json.dumps(catalog,ensure_ascii=False,indent=2))
    # Workbook data are derived views, not a second source to hand-maintain.
    note=DATE+'离线核对；数值='+HIST_LABEL+'；现版注册/实战待核。来源见最右列及《数据与采样说明》'
    books=[]
    wh=['模组/命名空间','物品ID','现版名称','攻击加值（历史）','攻速修正（历史）','面板代理（非EF实伤）','EF历史标记','现版资源/类型','现版状态','名称来源','取得线索（静态）','数值来源']
    wr=[[w['namespace'],w['id'],w['name'],w['damage_add'],w['speed_add'],None,'历史导出命中' if w['historical_ef'] else '历史未命中；不是不适配结论',w['static']+'；'+','.join(w['types']),w['status'],w['name_source'],'；'.join(w['acquisition_refs'])[:1600] or '未匹配简单result/loot项；含Java/条件/特殊配方待核',w['source']+'；'+HIST_LABEL] for w in weapons]
    wf={f'F{i+5}':f'=IF(AND(ISNUMBER(D{i+5}),ISNUMBER(E{i+5})),D{i+5}*(4+E{i+5}),"")' for i in range(len(wr))}
    newcaps=sorted(id for id in caps if id not in {w['id'] for w in weapons} and id in models and id.split(':')[0] in mods)
    nr=[[id.split(':')[0],id,name(id,'item')[0],'仅静态候选；可能为工具/远程/旧兼容引用，不直接当新增武器','；'.join(r['source'] for r in caps[id])] for id in newcaps]
    books.append({'file':'SvS_武器表.xlsx','sheets':[sheet('武器目录','武器与战斗工具目录 · 历史数值 × 现版证据',note,wh,wr,[20,45,26,15,15,18,25,40,28,55,64,50],[3,4,5],wf),sheet('仅资源候选','有模型与EF JSON、未见于历史数值导出的条目',DATE+'静态候选；没有新运行时属性，不补0、不直接进入任务', ['命名空间','ID','名称','状态','资源来源'],nr,[22,46,28,55,80])]})
    eh=['模组/命名空间','实体ID','现版名称','注册类别（历史）','生命（历史）','攻击（历史）','护甲（历史）','现版声明版本','EF资源证据','判杀进度引用','名称来源','数值来源']
    def erows(es):return [[e['namespace'],e['id'],e['name'],e['category'],e['hp'],e['attack'],e['armor'],e['version'],'；'.join(e['patch_sources']) or '未匹配JSON；Java适配未排除','；'.join(e['kill_advancements']) or '未匹配玩家击杀进度',e['name_source'],e['source']+'；'+HIST_LABEL] for e in es]
    for file,title,bucket in [('SvS_敌对生物表.xlsx','敌对注册类别目录',True),('SvS_中立生物表.xlsx','其他注册类别目录（原“中立”表）',False)]:
        books.append({'file':file,'sheets':[sheet('实体目录',title,note+'；CREATURE/MISC等类别不保证被动，真菌自定义类别另列敌对。',eh,erows([e for e in entities if e['hostile_bucket']==bucket]),[20,44,28,23,15,15,15,24,60,40,60,52],[4,5,6])]})
    bh=['命名空间','候选ID/函数场次','名称','设计用途（非入选）','模型与动作评审','特效/技能评审','生命（历史）','攻击（历史）','护甲（历史）','可用判杀线索','风险与重试','识别依据','模型/动画/补丁资源','名称来源']
    br=[[b['namespace'],b['id'],b['name'],b['purpose'],b['model_action_review'],'待实测',b['hp'],b['attack'],b['armor'],'；'.join(b['kill_advancements']) or '最终胜利事件待核',b['warning'] or '原生入口/重试/多人/归因待测','；'.join(b['evidence']),'；'.join(b['visual_refs']+b['patch_refs'])[:2600] or '未按名称匹配；Java/函数/外部引用未排除',b['name_source']] for b in bosses]
    exclusions=[['spore:mound / spore:proto','母巢事件系统/目标','不是普通结构Boss；三波＋终段方向已批，场次成功/数值未实装','主线深化研究§二E02；待裁决清单Q06'],['bloodandmadness:cleric_beast','旧引用未注册','10-11任务引用审计剔除；不得按老攻略回填','FTB任务重置_v2.md；10-11引用审计记录'],['nightfall_invade:arterius_hard','WIP排除','名称带WIP；普通Arterius与此项分开','主线深化研究§二E06'],['combat_evolution:shelmarow','Test Mob排除','不能由战斗附属名称/动画量推断正式Boss','主线深化研究§二E09'],['jerotesvillage:second_rounder_golem / second_rounder_golem_sword','未完成对象','不选为唯一必打；不能被HP阈值误升为主线Boss','任务参考研究_五整合包FTB§四E-二轮']]
    books.append({'file':'SvS_Boss表.xlsx','sheets':[sheet('Boss候选与看样','Boss候选 · 先看模型动作，再定战位',note+'；候选识别不等于已证完整Boss/主线授权；不按血量选压轴。',bh,br,[22,47,28,36,38,22,15,15,15,42,44,58,80,58],[6,7,8]),sheet('高血量实体非Boss判定','历史生命≥100实体 · 仅为数值过滤',note+'；含部件、宠物、测试实体和精英；不作为Boss清单',eh,erows(highhp),[20,44,28,23,15,15,15,24,60,40,60,52],[4,5,6]),sheet('事件与排除说明','母巢事件、旧引用与测试对象',DATE+'用于避免任务设计误用；本页不是新增排期',['ID/对象','分类','使用边界','来源'],exclusions,[70,30,82,65])]})
    efrows=[]
    namespaces=sorted(set(w['namespace'] for w in weapons)|set(e['namespace'] for e in entities)|{r['id'].split(':')[0] for r in resources if r['kind'] in ('weapon_capability','mobpatch')})
    for ns in namespaces:
        ws=[w for w in weapons if w['namespace']==ns];es=[e for e in entities if e['namespace']==ns];cc=[r for r in resources if r['kind']=='weapon_capability' and r['id'].split(':')[0]==ns];pp=[r for r in resources if r['kind']=='mobpatch' and r['id'].split(':')[0]==ns]
        efrows.append([ns,owner(ns),version(ns),len(ws),sum(w['historical_ef'] for w in ws),len(cc),len({r['id'] for r in cc}),len(es),len(pp),len({r['id'] for r in pp}),'待核；零JSON不能判无适配','现版资料索引.json resources；ef_items.json历史标记'])
    books.append({'file':'SvS_EF适配统计表.xlsx','sheets':[sheet('EF证据分层','EF 20.14.17 · 历史标记与现版资源分层',DATE+'离线计数；含未装mod的兼容JSON，不等于安装/注册。文件数、唯一键与运行时覆盖率不同。',['命名空间','模组名称','现版声明版本','历史武器数','历史EF命中数','武器JSON文件数','武器JSON唯一键','历史实体数','MobPatch文件数','MobPatch唯一键','当前运行时/战斗','依据'],efrows,[24,35,36,16,17,18,18,16,18,18,38,65],[3,4,5,6,7,8,9])]})
    mr=[]
    def classification(j):
        ids={m['id'] for m in j['declarations']};role=j['role']
        if ids & {'spore','sporeinquisition','symbiote','civillis'}:return '主题生态与村庄'
        if any(t in role for t in ['库/API','依赖库','库；','API','附属依赖']):return '库与通用兼容'
        if any(t in role for t in ['性能/稳定','优化','内存','线程']):return '性能与稳定'
        if any(t in role for t in ['界面/音画','UI说明','界面','镜头','按键']):return '界面音画与操作'
        if any(t in role for t in ['配置/阶段','魔改支撑','任务底座','任务/脚本']):return '配置脚本与任务工具'
        if any(t in role for t in ['匠魂','制造','材料成长']):return '匠魂与制造成长'
        if any(t in role for t in ['饰品','补给','料理','食物','背包','仓储']):return '饰品补给与收纳'
        if any(t in role for t in ['狩龙','龙生态','驯龙']):return '龙生态'
        if any(t in role for t in ['路网','探索','建筑氛围','维度','地牢','结构']):return '世界探索与路线'
        if any(t in role for t in ['武器','护甲','技能书','名品']):return '武器护甲与技能'
        if any(t in role for t in ['战斗','Boss','讨伐','看样','主线','竞技','人形','动作','连段','AI']):return '战斗内容与动作'
        return '其他工具与待细分'
    for j in d['mods']:
        nslist=[m['id'] for m in j['declarations']];dep=[x for x in j['dependencies'] if x.get('mandatory')]
        mr.append([classification(j),j['file'],' / '.join(nslist),' / '.join(m['name'] for m in j['declarations']),' / '.join(m['version'] for m in j['declarations']),j['role']+'；作者简介：'+j['description'],sum(w['namespace'] in nslist for w in weapons),sum(e['namespace'] in nslist for e in entities),'；'.join(x['modId']+' '+str(x.get('versionRange','')) for x in dep),j['license'],'一致' if j['same_test'] else '差异',j['sha256'],j['file']+'!/META-INF/mods.toml + MANIFEST.MF；用途：主线深化研究§七'])
    ms=sheet('全模组清单','现版模组文件清单 · 215 jar / 221顶层声明',DATE+'母本/test逐jar SHA-256一致；无新增运行时采样。分类为制作索引，license不是分发许可结论。',['制作分类','jar文件名','顶层modId','显示名称','声明版本','任务角色与功能简介','历史武器数','历史实体数','mandatory依赖声明','license原声明','母本/test','SHA-256','依据'],mr,[30,65,40,36,27,70,16,16,72,40,18,70,65],[6,7])
    roles=sorted(set(r[0] for r in mr));summaryrows=[[role,None] for role in roles]
    summaryform={f'B{i+5}':f'=COUNTIF(全模组清单!$A$5:$A${len(mr)+4},A{i+5})' for i in range(len(roles))}
    books.append({'file':'Symbiote vs Spore 全模组清单.xlsx','sheets':[ms,sheet('用途统计','按制作用途统计 · 不做S–F强度或重要性榜',DATE+'统计以顶层jar为单位；分类来自主线深化研究§七的用途归纳。',['用途','jar数'],summaryrows,[80,20],[1],summaryform)]})
    # The user has saved/closed WPS, but Windows still reports an exclusive lock
    # on the old Boss workbook. Keep a complete current view under a new name.
    for b in books:
        if b['file']=='SvS_Boss表.xlsx':b['file']='SvS_Boss表_更新版.xlsx'
    apply_group_order(books, catalog)
    write(DATA/'工作簿数据.json',json.dumps(books,ensure_ascii=False,indent=2))
    # Reviewable markdown views from the same joined catalog.
    backup('数值表_Boss.md');backup('敌对生物表.md');backup('模组清单.md');backup('数据与采样说明.md')
    write(DOCS/'武器目录.md','# 武器与战斗工具目录（离线更新）\n\n> '+note+'。完整列与取得线索见 [武器表](SvS_武器表.xlsx)，统一源 [制作资料汇总](data/制作资料汇总.json)。\n\n## 一、用途与口径\n\n本表有攻击属性的历史条目 '+str(len(weapons))+' 件，包含剑、工具和部分远程物品；不是已确认现版武器注册总数。攻击列为主手属性加值，代理值仅是“攻击加值×(4+攻速修正)”的旧口径，不能替代史诗战斗连段、命中率、技能或真实输出。旧 `全量武器表.md` 是收藏家生成器冻结输入，与本表用途不同；本轮不重跑标签、不更换生成器输入、不改变1291件分档。依据：《数据与采样说明》§二；《E4_收藏家标签差集清单》§一/二。\n\n## 二、历史数值与现版证据\n\n'+table(['命名空间','ID','现版名称','攻击加值（历史）','攻速修正（历史）','EF历史标记','现版资源证据','状态'],[[w['namespace'],w['id'],w['name'],w['damage_add'],w['speed_add'],'历史命中' if w['historical_ef'] else '未命中',w['static'],w['status']] for w in weapons]))
    write(DOCS/'敌对生物表.md','# 敌对注册类别目录（离线更新）\n\n> '+note+'。完整来源、判杀进度及EF资源见 [敌对生物表](SvS_敌对生物表.xlsx)。\n\n## 一、分类口径\n\n沿用历史导出的 MONSTER、infected、organoid、experiments 四类，共 '+str(catalog['counts']['hostile_bucket'])+' 条；不从血量推断Boss，不从注册类别推断实战仇恨。CREATURE/MISC等归其他类别目录，仍可能含敌人。依据：dump_entities.json category字段、《数据与采样说明》§二。\n\n## 二、目录\n\n'+table(['命名空间','ID','名称','注册类别','生命（历史）','攻击（历史）','护甲（历史）'],[[e['namespace'],e['id'],e['name'],e['category'],e['hp'],e['attack'],e['armor']] for e in entities if e['hostile_bucket']]))
    write(DOCS/'中立及其他类别目录.md','# 其他注册类别目录（原“中立”表）\n\n> '+note+'。完整来源见 [原中立生物表](SvS_中立生物表.xlsx)，文件名保留兼容旧链接。\n\n## 一、分类口径\n\n共 '+str(catalog['counts']['other_category'])+' 条，排除敌对目录的四类；CREATURE、MISC、水生等是注册分类，不能承诺中立。例如 Nightfall Scarlet Hunter 为 MISC，Jerotes部分战斗生物为 CREATURE。依据：dump_entities.json；《主线深化研究》§二E06/四。\n\n## 二、目录\n\n'+table(['命名空间','ID','名称','注册类别','生命（历史）','攻击（历史）','护甲（历史）'],[[e['namespace'],e['id'],e['name'],e['category'],e['hp'],e['attack'],e['armor']] for e in entities if not e['hostile_bucket']]))
    write(DOCS/'数值表_Boss.md','# Boss候选与表现评审入口\n\n> '+DATE+'离线整理。原“血量≥100”表移为工作簿独立页，旧文留在 archive/2026-10-12_资料更新前。本页不把HP筛选当Boss判定。统一源：data/制作资料汇总.json；完整资源/进度证据：[Boss更新表](SvS_Boss表_更新版.xlsx)。旧Boss原表仍被WPS占用，本轮不覆盖。\n\n## 一、筛选与授权边界\n\n候选共 '+str(len(bosses))+' 项（包括2项函数场次），来自“Boss Checklist支持ID∩历史实体”、SLU boss_命名池、《任务参考研究》E-二轮及《主线深化研究》§二/四的明确研究对象；这不是全Boss注册统计，也不证明每项已完整可玩。模型与动作优先→特效技能→入口重试/终段胜利→数值。所有表现结论仍待用户看样。被诅咒者与斯库拉仅比较候选；薪王化身已被用户否决作为终局；Nightfall/WOC只获准提替换方案。血源人形消失不代表胜利；FA两场不是普通实体。依据：《主线深化研究》§四、《任务设计总稿》终局候选部分、用户本次历次反馈。\n\n## 二、候选登记\n\n'+table(['命名空间','ID/场次','名称','设计用途','表现评审','判杀线索','风险'],[[b['namespace'],b['id'],b['name'],b['purpose'],b['model_action_review'],'、'.join(b['kill_advancements']) or '最终成功待核',b['warning'] or '入口/重试/多人待核'] for b in bosses])+'\n\n## 三、数值使用\n\n工作簿保留历史属性但不按血量排序选主线；“高血量实体非Boss判定”页 '+str(len(highhp))+' 条含测试/部件/宠物。缺属性留空，不填0。本轮未生成战斗评分、Tier表或当前强度结论。（依据：《数据与采样说明》§二/三；《主线深化研究》§四。）')
    oldmod=(DOCS/'archive/2026-10-12_资料更新前/模组清单.md').read_text(encoding='utf-8')
    section=oldmod.split('## 二、重要内容怎样服务本包',1)[1].split('## 三、',1)[0]
    section=section.replace('任务SNBT只由用户编辑器生成','任务SNBT程序生成/校验已获用户授权；当前重写暂停').replace('M2检测替代方案待批','任务v2已加载，功能尚待验证')
    write(DOCS/'模组清单.md','# Symbiote vs Spore 现版模组清单\n\n> '+DATE+'离线盘点：母本与test各 **215个顶层jar / 221个顶层mod声明**，文件名集合相同、逐文件SHA-256全部一致；不包含完整运行时嵌套mod列表，也不代表配置逐项一致。来源：data/现版资料索引.json mods/jar_difference；每行jar元数据与manifest。\n\n## 一、口径与版本边界\n\nEF固定20.14.17；文件名版本和声明版本不同均保留。无暮色森林、Alex’s Caves、souls_like_bosses的顶层jar；支持包里的旧引用不等于安装。当前任务重写暂停，禁止启动游戏做采样；优化合入审查的建议不等于已安装。license列仅转录元数据，不等于分发授权。完整依赖声明、SHA与用途可筛选于 [全模组工作簿](Symbiote%20vs%20Spore%20全模组清单.xlsx)。依据：HANDOVER§〇/四、用户最新指示、逐jar元数据。\n\n## 二、重要内容怎样服务本包'+section+'## 三、全部jar及元数据\n\n'+table(['#','jar文件名','modId @ 声明版本','任务角色/用途','license原声明'],[[i+1,j['file'],'；'.join(m['id']+' @ '+m['version'] for m in j['declarations']),j['role'],j['license']] for i,j in enumerate(d['mods'])]))
    # Structure index keeps all providers, not a claimed final registry order.
    sr=[r for r in resources if r['kind'] in ('structure','structure_set')]
    with (DATA/'结构资源索引.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['kind','id','source','spacing','separation','structures'])
        for r in sr:
            data=r.get('data') or {};p=data.get('placement',{});p=p if isinstance(p,dict) else {};writer.writerow([r['kind'],r['id'],r['source'],p.get('spacing',''),p.get('separation',''),';'.join(x.get('structure','') for x in data.get('structures',[]) if isinstance(x,dict))])
    with (DATA/'EF资源索引.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['kind','id','source','type','armature','renderer','parse_status'])
        for r in resources:
            if r['kind'] not in ('weapon_capability','weapon_type','mobpatch'):continue
            content=r.get('data');v=content or {};writer.writerow([r['kind'],r['id'],r['source'],v.get('type',''),v.get('armature',''),v.get('renderer',''),'ok' if isinstance(content,dict) else '解析异常'])
    with (DATA/'资源解析异常.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['source','error']);writer.writerows([x['source'],x['error']] for x in d['scan_issues'])
    # Small summary for QA and follow-up.
    write(DATA/'汇总核对.json',json.dumps({'counts':catalog['counts'],'workbooks':[{ 'file':b['file'],'sheets':[(s['name'],len(s['rows'])) for s in b['sheets']]} for b in books],'legacy_weapon_delta':{k:len(v) for k,v in catalog['legacy_weapon_input'].items() if isinstance(v,list)},'structure_files':len([r for r in sr if r['kind']=='structure']),'structure_keys':len({r['id'] for r in sr if r['kind']=='structure'}),'structure_set_files':len([r for r in sr if r['kind']=='structure_set']),'structure_set_keys':len({r['id'] for r in sr if r['kind']=='structure_set'}),'only_resource_weapon_candidates':len(newcaps)},ensure_ascii=False,indent=2))
    print((DATA/'汇总核对.json').read_text(encoding='utf-8'))

if __name__=='__main__':main()
