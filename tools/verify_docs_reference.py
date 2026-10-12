"""Check documentation workbook identities, source values, formulas and local links offline."""
import collections, itertools, json, math, re, hashlib, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).absolute().parents[1];N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def read_book(path):
    sheets=[]
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():strings=[''.join(n.itertext()) for n in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',N)]
        for i in range(1,len(ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',N))+1):
            cells={}
            for c in ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')).findall('.//s:sheetData/s:row/s:c',N):
                v=c.find('s:v',N);value=v.text if v is not None else ''.join(c.find('s:is',N).itertext()) if c.find('s:is',N) is not None else None
                if c.get('t')=='s':value=strings[int(value)]
                elif c.get('t') not in ('inlineStr','str','e') and value is not None:
                    try:value=float(value)
                    except ValueError:pass
                f=c.find('s:f',N);cells[c.get('r')]=(value,f.text if f is not None else None,c.get('t'))
            sheets.append(cells)
    return sheets
def col(n):
    s=''
    while n:n,k=divmod(n-1,26);s=chr(65+k)+s
    return s

def check_order(spec, cells, label, errors):
    rows=[[cells.get(col(j)+str(i),(None,None,None))[0] for j in range(1,len(spec['headers'])+1)]
          for i in range(5,len(spec['rows'])+5)]
    kind=spec.get('sort_kind')
    def rank(value):
        return (0,-value) if isinstance(value,(int,float)) and math.isfinite(value) else (1,0)
    if kind and kind.startswith('group_count_then_'):
        blocks=[(key,list(group)) for key,group in itertools.groupby(rows,key=lambda r:r[0])]
        if len({k for k,g in blocks})!=len(blocks):errors.append(label+': non-contiguous mod groups')
        sizes=[len(g) for k,g in blocks]
        if sizes!=sorted(sizes,reverse=True):errors.append(label+': mod group counts are not descending')
        if sum(sizes)!=len(rows):errors.append(label+': group size mismatch')
        for key,group in blocks:
            if not key.endswith(f' · {len(group)}项'):errors.append(label+': incorrect visible group count')
            for row in group:
                if ':' in row[1] and row[1].split(':',1)[0]!=key.split('\n')[-1].split(' · ')[0]:errors.append(label+': namespace/ID mismatch')
            if kind=='group_count_then_proxy':keys=[(rank(r[5]),r[1]) for r in group]
            elif kind=='group_count_then_attributes':
                numeric=[spec['headers'].index(h) for h in ('生命（历史）','攻击（历史）','护甲（历史）')]
                keys=[tuple(rank(r[j]) for j in numeric)+(r[1],) for r in group]
            else:keys=[r[1] for r in group]
            if keys!=sorted(keys):errors.append(label+': within-mod order is wrong: '+key)
        for meta,(key,group) in zip(spec.get('groups',[]),blocks):
            if meta['label']!=key or meta['count']!=len(group):errors.append(label+': formatting group metadata mismatch')
    elif kind=='content_total':
        w=spec['headers'].index('历史武器数');e=spec['headers'].index('历史实体数')
        totals=[r[w]+r[e] for r in rows]
        if totals!=sorted(totals,reverse=True):errors.append(label+': total content is not descending')
    elif kind=='category_count':
        if [r[1] for r in rows]!=sorted([r[1] for r in rows],reverse=True):errors.append(label+': category counts are not descending')

def check_reorder_only(src, errors):
    base=Path((ROOT/'backups/docs_sheet_work/sort_backup_path.txt').read_text(encoding='utf-8'))
    old=json.loads((base/'data/工作簿数据.json').read_text(encoding='utf-8'))
    before={(b['file'],s['name']):s for b in old for s in b['sheets']}
    for book in src:
        for spec in book['sheets']:
            previous=before[(book['file'],spec['name'])]
            def contents(s):
                omit_first=bool(spec.get('groups'))
                return collections.Counter(json.dumps({h:r[j] for j,h in enumerate(s['headers']) if not(omit_first and j==0)},ensure_ascii=False,sort_keys=True)
                                           for r in s['rows'])
            if contents(previous)!=contents(spec):errors.append(book['file']+' '+spec['name']+': underlying row content changed')
def main():
    src=json.loads((ROOT/'docs/data/工作簿数据.json').read_text(encoding='utf-8'))
    dest=ROOT/'docs' if '--installed' in __import__('sys').argv else ROOT/'backups/docs_sheet_work/outputs'
    errors=[]; report=[]
    if '--sort-audit' in __import__('sys').argv:check_reorder_only(src,errors)
    for book in src:
        p=dest/book['file'];sheets=read_book(p);count=0
        for spec,cells in zip(book['sheets'],sheets):
            check_order(spec,cells,book['file']+' '+spec['name'],errors)
            for j,header in enumerate(spec['headers'],1):
                if cells.get(col(j)+'4',(None,None,None))[0]!=header:errors.append(book['file']+': header mismatch')
            for i,row in enumerate(spec['rows'],5):
                for j,expected in enumerate(row,1):
                    addr=col(j)+str(i);got=cells.get(addr,(None,None,None))
                    if addr in spec.get('formulas',{}):
                        count+=1
                        if not got[1]:errors.append(f'{book["file"]} {addr}: lost formula')
                        elif got[1]!=spec['formulas'][addr].lstrip('='):errors.append(f'{book["file"]} {addr}: wrong row formula reference')
                        if got[2]=='e':errors.append(f'{book["file"]} {addr}: formula error {got[0]}')
                        if spec['name']=='武器目录':
                            predicted=row[3]*(4+row[4]) if isinstance(row[3],(int,float)) and isinstance(row[4],(int,float)) else ''
                            if isinstance(predicted,(float,int)) and (not isinstance(got[0],(float,int)) or not math.isclose(predicted,got[0],rel_tol=1e-10,abs_tol=1e-10)):errors.append(f'{book["file"]} {addr}: proxy formula result mismatch')
                        if spec['name']=='用途统计':
                            predicted=sum(r[0]==row[0] for r in book['sheets'][0]['rows'])
                            if got[0]!=predicted:errors.append(f'{book["file"]} {addr}: role count formula result mismatch')
                    elif expected is None or expected=='':
                        if got[0] not in (None,''):errors.append(f'{book["file"]} {addr}: expected blank got {got[0]}')
                    elif isinstance(expected,(float,int)):
                        if not isinstance(got[0],(float,int)) or not math.isclose(expected,got[0],rel_tol=1e-10,abs_tol=1e-10):errors.append(f'{book["file"]} {addr}: number mismatch {expected} vs {got[0]}')
                    elif str(expected)!=str(got[0]):errors.append(f'{book["file"]} {addr}: text mismatch {str(expected)[:100]} vs {str(got[0])[:100]}')
        report.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sheets':len(sheets),'data_rows':sum(len(s['rows']) for s in book['sheets']),'formula_count':count})
    summary={'scope':str(dest),'workbooks':report,'errors':errors[:80],'error_count':len(errors)}
    out=ROOT/'backups/docs_sheet_work'/('installed_verification.json' if '--installed' in __import__('sys').argv else 'data_verification.json')
    out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
