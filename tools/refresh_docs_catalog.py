"""Read local pack/docs evidence and build a single catalog for the documentation tables.
No changes to the pack, registries, quest source or gameplay scripts.
Run with bundled Python 3.12 (tomllib). Workbook authoring is a separate Artifact Tool step.
"""
import argparse, collections, datetime, hashlib, json, os, re, tomllib, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(os.path.abspath(__file__)).parents[1]
DOCS=ROOT/'docs'
MOTHER=Path(r'E:\SvS_整合包_副本')
TEST=Path(r'C:\PCL 正式版 2.8.13\.minecraft\versions\test')
OUT=DOCS/'data'
DATE='2026-10-12'
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(s): return str(s or '').replace('\n',' ').replace('|','／').strip()
def read_json(raw):
    try:return json.loads(raw.decode('utf-8-sig'))
    except (ValueError,UnicodeDecodeError):
        text=raw.decode('utf-8-sig',errors='replace')
        text=re.sub(r'("(?:[^"\\]|\\.)*")|(/\*[\s\S]*?\*/|//[^\n]*)',lambda m:m.group(1) or '',text)
        text=re.sub(r',\s*([}\]])',r'\1',text)
        return json.loads(text)

def old_workbooks():
    result={}
    for p in DOCS.glob('*.xlsx'):
        if p.name.startswith('~$'):continue
        sheets=[]
        with zipfile.ZipFile(p) as z:
            strings=[]
            if 'xl/sharedStrings.xml' in z.namelist():
                strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
            for i,sheet in enumerate(ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS),1):
                rows=[]
                xml=ET.fromstring(z.read('xl/worksheets/sheet%d.xml'%i))
                for row in xml.findall('s:sheetData/s:row',NS):
                    cells={}
                    for c in row:
                        v=c.find('s:v',NS); f=c.find('s:f',NS); inline=c.find('s:is',NS)
                        value=v.text if v is not None else ''.join(inline.itertext()) if inline is not None else ''
                        if c.get('t')=='s':value=strings[int(value)]
                        elif c.get('t') not in ('inlineStr','str') and value:
                            try:value=float(value)
                            except ValueError:pass
                        cells[c.get('r')]= {'value':value,'formula':f.text if f is not None else None}
                    rows.append(cells)
                sheets.append({'name':sheet.get('name'),'rows':rows})
        result[p.name]={'sha256':sha(p),'sheets':sheets}
    return result

def scan_static():
    mods=[]; resources=[]; lang={}; issues=[]; model_ids=set(); roles={}; descriptions={}; visuals=[]
    for line in (DOCS/'主线深化研究_全模组与战斗筛选.md').read_text(encoding='utf-8').splitlines():
        m=re.match(r'\|\s*\d+\s*\|\s*`([^`]+\.jar)`\s*\|.*?\|\s*(.*?)\s*\|$',line)
        if m:roles[m[1]]=m[2]
    description_source=DOCS/'archive/2026-10-12_资料更新前/模组清单.md'
    if not description_source.exists():description_source=DOCS/'模组清单.md'
    for line in description_source.read_text(encoding='utf-8').splitlines():
        cells=[x.strip() for x in line.strip('|').split('|')]
        if len(cells)>=5 and cells[1].endswith('.jar`'):descriptions[cells[1].strip('`')]=cells[3]
    for p in sorted((MOTHER/'mods').glob('*.jar'),key=lambda p:p.name.lower()):
        row={'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'declarations':[], 'dependencies':[], 'license':'', 'resource_counts':{},'role':roles.get(p.name,''),'description':descriptions.get(p.name,'')}
        peer=TEST/'mods'/p.name
        row['test_sha256']=sha(peer) if peer.is_file() else None
        row['same_test']=row['sha256']==row['test_sha256']
        with zipfile.ZipFile(p) as z:
            names=z.namelist(); manifest={}
            if 'META-INF/MANIFEST.MF' in names:
                for ln in z.read('META-INF/MANIFEST.MF').decode(errors='replace').splitlines():
                    if ': ' in ln:
                        k,v=ln.split(': ',1);manifest[k]=v
            if 'META-INF/mods.toml' in names:
                try:
                    meta=tomllib.loads(z.read('META-INF/mods.toml').decode('utf-8-sig'))
                    row['license']=meta.get('license','')
                    for m in meta.get('mods',[]):
                        version=str(m.get('version',''))
                        if version=='${file.jarVersion}':version=manifest.get('Implementation-Version','${file.jarVersion}')
                        row['declarations'].append({'id':m.get('modId',''),'name':m.get('displayName',''),'version':version,'description':clean(m.get('description',''))})
                    for owner,deps in meta.get('dependencies',{}).items():
                        for d in deps:row['dependencies'].append(dict(owner=owner,**d))
                except Exception as e:issues.append({'source':p.name,'error':str(e)})
            elif 'fabric.mod.json' in names:
                m=read_json(z.read('fabric.mod.json'));row['declarations']=[{'id':m.get('id',''),'name':m.get('name',''),'version':m.get('version',''),'description':m.get('description','')}];row['license']=str(m.get('license',''))
            for n in names:
                if re.match(r'assets/[^/]+/(geo|animations|animmodels)/',n) and n.endswith('.json'):
                    visuals.append({'path':n,'source':p.name})
                m=re.match(r'assets/([^/]+)/lang/(zh_cn|en_us)\.json$',n)
                if m:
                    try:
                        for k,v in read_json(z.read(n)).items():
                            lang.setdefault(k,{})[m[2]]={'text':v,'source':p.name+'!/'+n}
                    except Exception as e:issues.append({'source':p.name+'!/'+n,'error':str(e)})
                m=re.match(r'assets/([^/]+)/models/item/(.+)\.json$',n)
                if m:model_ids.add(m[1]+':'+m[2])
                kind=None; rid=None
                for prefix,label in [('capabilities/weapons','weapon_capability'),('epicfight_mobpatch','mobpatch'),('worldgen/structure','structure'),('worldgen/structure_set','structure_set'),('advancements','advancement'),('recipes','recipe'),('loot_tables','loot_table')]:
                    m=re.match(r'data/([^/]+)/'+prefix+r'/(.+)\.json$',n)
                    if m:kind=('weapon_type' if label=='weapon_capability' and m[2].startswith('types/') else label);rid=m[1]+':'+m[2];break
                if kind:
                    try:content=read_json(z.read(n))
                    except Exception as e:issues.append({'source':p.name+'!/'+n,'error':str(e)});content=None
                    # Keep complete evidence for small registries, references only for recipes/loot.
                    record={'kind':kind,'id':rid,'source':p.name+'!/'+n}
                    if kind=='recipe' and isinstance(content,dict):record['result']=content.get('result');record['type']=content.get('type')
                    elif kind=='loot_table':record['items']=sorted(set(re.findall(r'"name"\s*:\s*"([a-z0-9_.-]+:[a-z0-9_./-]+)"',json.dumps(content))))
                    else:record['data']=content
                    resources.append(record)
                    row['resource_counts'][kind]=row['resource_counts'].get(kind,0)+1
        mods.append(row)
    # Data/resource overrides are applied after jar evidence, without claiming active resourcepack order.
    for pack in sorted((MOTHER/'config/openloader/data').rglob('*.zip')):
        with zipfile.ZipFile(pack) as z:
            for n in z.namelist():
                for prefix,label in [('capabilities/weapons','weapon_capability'),('epicfight_mobpatch','mobpatch'),('worldgen/structure','structure'),('worldgen/structure_set','structure_set'),('advancements','advancement'),('recipes','recipe'),('loot_tables','loot_table')]:
                    m=re.match(r'data/([^/]+)/'+prefix+r'/(.+)\.json$',n)
                    if not m:continue
                    try:content=read_json(z.read(n))
                    except Exception as e:issues.append({'source':str(pack)+'!/'+n,'error':str(e)});content=None
                    rec={'kind':('weapon_type' if label=='weapon_capability' and m[2].startswith('types/') else label),'id':m[1]+':'+m[2],'source':'config/openloader/data/'+pack.name+'!/'+n}
                    if label=='recipe' and isinstance(content,dict):rec['result']=content.get('result');rec['type']=content.get('type')
                    elif label=='loot_table':rec['items']=sorted(set(re.findall(r'"name"\s*:\s*"([a-z0-9_.-]+:[a-z0-9_./-]+)"',json.dumps(content))))
                    else:rec['data']=content
                    resources.append(rec)
    for p in sorted((MOTHER/'config/openloader/data').rglob('*.json')):
        rel=p.relative_to(MOTHER).as_posix(); match=re.search(r'/data/([^/]+)/(capabilities/weapons|epicfight_mobpatch|worldgen/structure|worldgen/structure_set|advancements|recipes|loot_tables)/(.+)\.json$',rel)
        if not match:continue
        ns,section,entry=match.groups(); kind={'capabilities/weapons':'weapon_capability','epicfight_mobpatch':'mobpatch','worldgen/structure':'structure','worldgen/structure_set':'structure_set','advancements':'advancement','recipes':'recipe','loot_tables':'loot_table'}[section]
        if kind=='weapon_capability' and entry.startswith('types/'):kind='weapon_type'
        try:content=read_json(p.read_bytes())
        except Exception as e:issues.append({'source':rel,'error':str(e)});content=None
        rec={'kind':kind,'id':ns+':'+entry,'source':rel}
        if kind=='recipe' and isinstance(content,dict):rec['result']=content.get('result');rec['type']=content.get('type')
        elif kind=='loot_table':rec['items']=sorted(set(re.findall(r'"name"\s*:\s*"([a-z0-9_.-]+:[a-z0-9_./-]+)"',json.dumps(content))))
        else:rec['data']=content
        resources.append(rec)
    for p in sorted((MOTHER/'config/openloader/resources').rglob('*.json')):
        m=re.search(r'/assets/([^/]+)/lang/(zh_cn|en_us)\.json$',p.as_posix())
        if not m:continue
        try:
            for k,v in read_json(p.read_bytes()).items():lang.setdefault(k,{})[m[2]]={'text':v,'source':p.relative_to(MOTHER).as_posix()}
        except Exception as e:issues.append({'source':p.relative_to(MOTHER).as_posix(),'error':str(e)})
    for p in sorted((MOTHER/'kubejs/assets').rglob('*.json')):
        m=re.match(r'([^/]+)/lang/(zh_cn|en_us)\.json$',p.relative_to(MOTHER/'kubejs/assets').as_posix())
        if m:
            for k,v in read_json(p.read_bytes()).items():lang.setdefault(k,{})[m[2]]={'text':v,'source':'kubejs/assets/'+p.relative_to(MOTHER/'kubejs/assets').as_posix()}
    return {'mods':mods,'resources':resources,'translations':lang,'model_item_ids':sorted(model_ids),'visual_assets':visuals,'scan_issues':issues,
            'jar_difference':{'mother_only':sorted(set(p.name for p in (MOTHER/'mods').glob('*.jar'))-set(p.name for p in (TEST/'mods').glob('*.jar'))),'test_only':sorted(set(p.name for p in (TEST/'mods').glob('*.jar'))-set(p.name for p in (MOTHER/'mods').glob('*.jar')))}}

def parse_runtime(path):
    result={'weapons':[],'entities':[],'mods':[],'tags':[],'item_ids':[],'entity_ids':[],'end':None,'source':str(path),'sha256':sha(path)}
    keys={'WEAPON':'weapons','ENTITY':'entities','MOD':'mods','TAG':'tags','ITEM_IDS':'item_ids','ENTITY_IDS':'entity_ids','END':'end'}
    for line in path.read_text(encoding='utf-8-sig',errors='replace').splitlines():
        m=re.search(r'\[SVS-DOCS-([A-Z_]+)\] (.*)',line)
        if not m:continue
        k=m[1]
        if k=='BEGIN':
            for key in ('weapons','entities','mods','tags','item_ids','entity_ids'):result[key]=[]
            result['end']=None
        elif k in keys:
            data=json.loads(m[2]);target=keys[k]
            if k in ('WEAPON','ENTITY','MOD','TAG'):result[target].append(data)
            else:result[target]=data
    if not result['end']:raise ValueError('Runtime snapshot has no successful END marker')
    assert len(result['weapons'])==result['end']['weapons']
    assert len(result['entities'])==result['end']['living']
    return result

def document_inventory():
    rows=[]
    for p in sorted(DOCS.rglob('*')):
        if not p.is_file() or p.name.startswith('~$') or 'data' in p.relative_to(DOCS).parts:continue
        row={'path':p.relative_to(DOCS).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'archived':'archive' in p.relative_to(DOCS).parts}
        if p.suffix in ('.md','.txt'):
            text=p.read_text(encoding='utf-8-sig');row['headings']=re.findall(r'^#{1,4} .+$',text,re.M)
            row['references']=sorted(set(re.findall(r'\]\(([^)]+)\)',text)))
            row['old_mentions']={s:len(re.findall(re.escape(s),text)) for s in ['test4','1330','214','SNBT只能','不手写任务','待用户批注'] if s in text}
        rows.append(row)
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime-log',type=Path);ap.add_argument('--static-only',action='store_true');args=ap.parse_args()
    OUT.mkdir(exist_ok=True)
    data={'schema':1,'as_of':DATE,'instance':'test','mother':str(MOTHER),'scan_time':datetime.datetime.now().isoformat(timespec='seconds'),**scan_static(),'documents':document_inventory()}
    if args.runtime_log:data['runtime']=parse_runtime(args.runtime_log)
    elif not args.static_only:raise ValueError('Specify --runtime-log or --static-only explicitly')
    (OUT/'现版资料索引.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    old=ROOT/'backups/docs_refresh_20261012/old_workbooks.json'
    if not old.exists():old.write_text(json.dumps(old_workbooks(),ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'jars':len(data['mods']),'hash_mismatches':sum(not m['same_test'] for m in data['mods']),'resources':len(data['resources']),'scan_issues':len(data['scan_issues']),'runtime':data.get('runtime',{}).get('end'),'documents_read':len(data['documents'])},ensure_ascii=False))

if __name__=='__main__':main()
