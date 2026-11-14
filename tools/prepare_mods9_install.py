"""Prepare the authorized six-mod intake. Never deploys or launches Minecraft."""
import argparse,hashlib,json,urllib.request,urllib.error,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BACKUP=ROOT/'backups/mods9_install_20261031'
INTAKE=Path('E:/mcmp_test/dl/新加入的模组9')
TARGETS={'test':Path('C:/PCL 正式版 2.8.13/.minecraft/versions/test'),'mother':Path('E:/SvS_整合包_副本')}
DEPS={
 'azurelib-neo-1.20.1-3.1.3.jar':{'url':'https://edge.forgecdn.net/files/7371/538/azurelib-neo-1.20.1-3.1.3.jar','project_id':817423,'file_id':7371538,'page':'https://www.curseforge.com/minecraft/mc-mods/azurelib/files/7371538'},
 'vzling-0.98.8-1.20.1-forge.jar':{'url':'https://edge.forgecdn.net/files/9100/905/vzling-0.98.8-1.20.1-forge.jar','project_id':1316184,'file_id':9100905,'page':'https://www.curseforge.com/minecraft/mc-mods/vzlinglib/files/9100905'},
}
CF_FIXED={
 'bookofdragons-1.31-1.20.1.jar':{'slug':'book-of-dragons','project_id':1413424,'file_id':7870334,'provenance':'Local Zone.Identifier HostUrl; official CDN bytes must match'},
 'celestisynth_fix-0.1.jar':{'slug':'celestisynth-fix','project_id':1568922,'file_id':8216806},
 'quest_enhance-1.20.1-forge-3.13.jar':{'slug':'quest-enhance','project_id':1610171,'file_id':9098926},
 'super-tier-magic-3.6.3.jar':{'slug':'super-tier-magic','project_id':1731849,'file_id':9277191},
}
def digest(p,algorithm='sha256'):return hashlib.new(algorithm,p.read_bytes()).hexdigest()
def write_json(p,value):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def files_snapshot(root,folders):
 return {p.relative_to(root).as_posix():digest(p) for name in folders if (root/name).exists() for p in (root/name).rglob('*') if p.is_file()}
def baseline():
 BACKUP.mkdir(parents=True,exist_ok=True);dest=BACKUP/'baseline.json'
 if dest.exists():print('Baseline already preserved');return
 old=json.loads((ROOT/'docs/data/模组9审查_2026-10-26.json').read_text(encoding='utf-8'))
 new=[]
 for row in old['intake']:
  p=INTAKE/row['file'];assert digest(p)==row['sha256'],('Intake changed',str(p))
  with zipfile.ZipFile(p) as z:assert z.testzip() is None
  new.append({'file':p.name,'path':str(p),'sha256':digest(p),'sha512':digest(p,'sha512'),'enabled':not p.name.startswith('spawn-')})
 state={'date':'2026-10-31','intake':new,'instances':{},'repo_protected':files_snapshot(ROOT,['config/ftbquests','kubejs/server_scripts','svs_tweak/src','docs/map-v2'])}
 for name in ['docs/questbook_v2.json','docs/FTB任务v2_ID映射.json','pack.toml','index.toml']:
  p=ROOT/name
  if p.exists():state['repo_protected'][name]=digest(p)
 for role,root in TARGETS.items():
  jars={p.name:digest(p) for p in (root/'mods').glob('*.jar')}
  config=files_snapshot(root,['config','defaultconfigs','configureddefaults','kubejs','scripts','resourcepacks'])
  saves={p.relative_to(root).as_posix():[p.stat().st_size,p.stat().st_mtime_ns] for p in (root/'saves').rglob('*') if p.is_file()}
  options={p.name:digest(p) for p in root.glob('options*') if p.is_file()}
  state['instances'][role]={'root':str(root),'jars':jars,'files':config,'saves_metadata':saves,'options_hashes':options}
  print(role,'baseline jars',len(jars),'config/resources',len(config),flush=True)
 write_json(dest,state)

def request_json(url):
 req=urllib.request.Request(url,headers={'User-Agent':'SvS-Modpack-Local-Integration/1.0'})
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def sources():
 baseline();dest=BACKUP/'download_sources.json'
 info=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {'intake':{},'dependencies':{}}
 for p in sorted(INTAKE.glob('*.jar')):
  if p.name.startswith('spawn-') or p.name in info['intake']:continue
  try:
   data=request_json('https://api.modrinth.com/v2/version_file/'+digest(p,'sha1')+'?algorithm=sha1')
   matching=[f for f in data['files'] if f['hashes']['sha1']==digest(p,'sha1')];assert len(matching)==1
   info['intake'][p.name]={'provider':'modrinth','project_id':data['project_id'],'version_id':data['id'],'url':matching[0]['url'],'sha512':matching[0]['hashes']['sha512']}
   assert info['intake'][p.name]['sha512']==digest(p,'sha512')
   print('Resolved',p.name,data['id'],flush=True)
  except urllib.error.HTTPError as e:
   if e.code!=404:raise
   info['intake'][p.name]={'provider':'unresolved','reason':'Exact local SHA1 absent from Modrinth'}
   print('Needs CurseForge source',p.name,flush=True)
  write_json(dest,info)
 for name,source in DEPS.items():
  p=BACKUP/'downloads'/name;p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():
   req=urllib.request.Request(source['url'],headers={'User-Agent':'SvS-Modpack-Local-Integration/1.0'})
   with urllib.request.urlopen(req,timeout=60) as r:raw=r.read()
   with zipfile.ZipFile(__import__('io').BytesIO(raw)) as z:assert z.testzip() is None
   p.write_bytes(raw)
  with zipfile.ZipFile(p) as z:assert z.testzip() is None
  info['dependencies'][name]={**source,'path':str(p),'sha256':digest(p),'sha512':digest(p,'sha512'),'size':p.stat().st_size}
  write_json(dest,info);print('Dependency ready',name,p.stat().st_size,flush=True)

def verify_cf():
 dest=BACKUP/'download_sources.json';info=json.loads(dest.read_text(encoding='utf-8'))
 for name,source in CF_FIXED.items():
  fileid=source['file_id'];q=BACKUP/'source_checks'/name;q.parent.mkdir(parents=True,exist_ok=True)
  url=f"https://edge.forgecdn.net/files/{fileid//1000}/{fileid%1000}/{name}"
  if not q.exists():
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'SvS-Modpack-Local-Integration/1.0'}),timeout=60) as r:q.write_bytes(r.read())
  assert digest(q)==digest(INTAKE/name),('Official bytes differ; preserve supplied version',name)
  with zipfile.ZipFile(q) as z:assert z.testzip() is None
  info['intake'][name]={'provider':'curseforge',**source,'page':f"https://www.curseforge.com/minecraft/mc-mods/{source['slug']}/files/{fileid}",'url':url,'sha512':digest(q,'sha512'),'official_download_matches':True}
  write_json(dest,info);print('Official hash match',name,flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['baseline','sources','verify-cf']);args=parser.parse_args()
 {'baseline':baseline,'sources':sources,'verify-cf':verify_cf}[args.stage]()
