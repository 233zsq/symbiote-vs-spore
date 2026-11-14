"""Independent review of compatibility metadata, IDs, victory gating and rewards.
Reports static evidence only; the user owns Minecraft combat acceptance.
"""
import collections,hashlib,json,re,tomllib,zipfile
from pathlib import Path
from PIL import Image
import build_questbook_v2 as builder
R=Path(__file__).resolve().parents[1];B=R/'backups/legendary_bosses_20261018'
facts=json.loads((R/'docs/data/legendary_bosses_20261018.json').read_text(encoding='utf-8'))
dl=facts['download'];p=B/'legendarybosses-0.6.1-beta.jar';assert hashlib.sha256(p.read_bytes()).hexdigest()==dl['sha256']
z=zipfile.ZipFile(p);assert z.testzip() is None
meta=tomllib.loads(z.read('META-INF/mods.toml').decode());assert meta['mods'][0]['modId']=='legendarybosses' and meta['mods'][0]['version']=='0.6.1-beta'
dep={e['modId']:e for e in meta['dependencies']['legendarybosses']}
assert dep['geckolib']['versionRange']=='[4.4,)' and dep['minecraft']['versionRange']=='[1.20.1]'
assert {int.from_bytes(z.read(n)[6:8],'big') for n in z.namelist() if n.endswith('.class')}=={61}
assert not any(s in n for n in z.namelist() for s in ['/worldgen/','/biome_modifier/','/structures/'])
cfg=tomllib.loads((R/'config/Legendary Bosses/legendarybosses.toml').read_text(encoding='utf-8'))
assert cfg['difficulty']['mode']=='MODDED'
assert cfg['difficulty']['modded']==dict(healthMultiplier=1.0,damageMultiplier=1.0,armorOverride=-1.0,armorToughnessOverride=-1.0)
assert cfg['multiplayer']['healthPerExtraPlayer']==0
assert set(cfg['bosses'])=={'herobrine','entity303','null','notch'}
assert all(v==dict(enabled=True,healthMultiplier=1.0,damageMultiplier=1.0) for v in cfg['bosses'].values())
original=json.loads((B/'before/docs/questbook_v2.json').read_text(encoding='utf-8'));d=json.loads(builder.SOURCE.read_text(encoding='utf-8'))
old={q['key']:q for q in original['quests']};qs={q['key']:q for q in d['quests']}
assert d['content_revision']=='6.1-legendarybosses-20261018'
files,bindings,entries=builder.create(d);builder.validate_output(files);builder.validate_auxiliary(d,bindings,entries)
assert set(old)<=set(qs) and len(qs)-len(old)==21
for key,v in old.items():
    # Every old task and every old claim is retained, including once-only choice rewards.
    assert qs[key]['items']==v['items'],('old reward changed',key)
    assert qs[key].get('select_rewards')==v.get('select_rewards'),key
    for index,t in enumerate(v['tasks']):
        now=qs[key]['tasks'][index]
        assert {k:x for k,x in now.items() if k!='quest_keys'}=={k:x for k,x in t.items() if k!='quest_keys'},key
        if t.get('quest_keys'):assert set(t['quest_keys'])<=set(now['quest_keys']),key
    if key not in facts['changed_dependencies']:assert qs[key]['deps']==v['deps'],key

for boss in facts['bosses']:
    k=boss['key'];fight=qs[boss['fight_key']];prep=qs[boss['prep_key']];after=qs[boss['after_key']]
    assert fight['tasks']==[dict(kind='advancement',target='legendarybosses:'+k+'_slayer',count=1)]
    adv=json.loads(z.read('data/legendarybosses/advancements/'+k+'_slayer.json'))
    assert adv['criteria']['slay_'+k]['conditions']['entity'][0]['predicate']['type']=='legendarybosses:'+k
    source=(B/'decompiled/com/doorlegends/legendarybosses/entity/boss'/({'herobrine':'HerobrineEntity','entity_303':'Entity303Entity','null':'NullEntity','notch':'NotchEntity'}[k]+'.java')).read_text(encoding='utf-8')
    assert 'SLAYER_ADVANCEMENT' in source and 'this.finishingDeath = true;' in source
    assert 'slay_'+k in source and 'this.m_21153_(0.0f)' in source
    assert len(fight['sections'][0]['lines'])==3
    assert prep['tasks']==boss['offer'] and not any(t.get('consume') for t in prep['tasks'])
    assert qs[boss['next']]['deps']==[boss['after_key']]
    assert not fight['optional'] and not after['optional']
    assert after['items']==boss['payout'] and after['select_rewards']==boss['select']
    icon=R/'kubejs/assets/svs'/fight['icon_texture'].split(':')[1]
    with Image.open(icon) as im:assert im.size==(16,16) and im.mode=='RGBA' and im.getbbox()

covered={i for v in qs.values() for i in v.get('catalog_items',[])}
for s in facts['obtained_items']:assert 'legendarybosses:'+s in covered
assert not covered.intersection('legendarybosses:'+s for s in facts['excluded_props'])
for kind in ['weapon','armor']:
    milestones=[v for v in qs.values() if v['key'].startswith('E6_C_T0_'+kind+'_')]
    assert milestones
    for v in milestones:
        keys=v['tasks'][0]['quest_keys'];assert len(keys)>=v['tasks'][0]['count'] and len(keys)==len(set(keys))
        assert all(qs[k]['ledger_kind']==kind for k in keys)
new=[v for v in qs.values() if v.get('catalog_items') and any(i.startswith('legendarybosses:') for i in v['catalog_items'])]
assert len(new)==4 and all(v['tier']=='T0' and v['items']==[['kubejs:spore_coin',12]] for v in new)
en=json.loads(z.read('assets/legendarybosses/lang/en_us.json'));zh=json.loads((R/'kubejs/assets/legendarybosses/lang/zh_cn.json').read_text(encoding='utf-8'))
assert set(en)==set(zh) and len(zh)==190
for k in en:
    assert re.findall(r'%(?:\d+\$)?[sdf]',en[k])==re.findall(r'%(?:\d+\$)?[sdf]',zh[k]),k
    assert en[k].count('\n')==zh[k].count('\n'),k
    assert not any(c in zh[k] for c in ['於','後','麽','體','戰','鎧','鐮']),k
reg=(B/'decompiled/com/doorlegends/legendarybosses/registry/ModItems.java').read_text(encoding='utf-8')
for s in facts['obtained_items']:assert 'ITEMS.register("'+s+'"' in reg
caproot=R/'config/openloader/data/svs/data/legendarybosses/capabilities/weapons'
assert sorted(p.name for p in caproot.glob('*.json'))==['entity_303_scythe.json','herobrine_greatsword.json']
for p in caproot.glob('*.json'):assert set(json.loads(p.read_text(encoding='utf-8')))=={'type'},'do not add unsolicited damage attributes'
providers=json.loads((B/'existing_ef_weapon_type.json').read_text(encoding='utf-8'))
assert {p['role'] for p in providers}=={'repo','test','mother'}
for p in providers:assert hashlib.sha256(Path(p['resource']).read_bytes()).hexdigest()==p['sha256']
assert not (R/'config/openloader/data/svs/data/legendarybosses/epicfight_mobpatch').exists()
report=dict(result='PASS',jar_crc=True,jar_sha256=dl['sha256'],java_class_version=61,required_geckolib='>=4.4; installed 4.8.4',
            original_task_ids_preserved=len(old),new_bosses=4,new_objectives=21,new_gear=4,translation_keys=190,
            natural_worldgen_resources=0,default_effective_profile_preserved=True,
            runtime_status='NOT TESTED: client loading, EF interaction, cinematics, rituals, restoration and multiplayer acceptance belong to user',
            installation='DEFERRED: user is playing and requested files first')
(B/'static_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
