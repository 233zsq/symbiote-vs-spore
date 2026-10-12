"""Apply the user's old Boss workbook grouping convention to offline views only."""
import collections
import json
import math
from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]
DATA = ROOT / 'docs/data'


def descending(value):
    known = isinstance(value, (float, int)) and math.isfinite(value)
    return (0, -value) if known else (1, 0)


def apply_group_order(books, catalog):
    owners = {m['id']: ' '.join(m['name'].split())
              for jar in catalog['jars'] for m in jar['declarations']}
    owners['minecraft'] = 'Minecraft'
    owners.setdefault('final_adversaries_lite', 'Final Adversaries Lite')
    for book in books:
        for spec in book['sheets']:
            name = spec['name']
            headers = spec['headers']
            rows = spec['rows']
            if name == 'Boss候选与看样':
                # Keep the numeric comparison beside the name, as in the old table.
                desired = ['模组/命名空间', '候选ID/函数场次', '名称',
                           '生命（历史）', '攻击（历史）', '护甲（历史）',
                           '模型与动作评审', '特效/技能评审', '设计用途（非入选）',
                           '可用判杀线索', '风险与重试', '识别依据',
                           '模型/动画/补丁资源', '名称来源']
                headers[0] = '模组/命名空间'
                order = [headers.index(h) for h in desired]
                spec['rows'] = rows = [[row[i] for i in order] for row in rows]
                spec['widths'] = [spec['widths'][i] for i in order]
                spec['headers'] = headers = desired
                spec['numeric'] = [3, 4, 5]
            if name in ('武器目录', '仅资源候选', '实体目录',
                        'Boss候选与看样', '高血量实体非Boss判定'):
                def namespace(row):
                    identifier = row[1]
                    if ':' in identifier:
                        return identifier.split(':', 1)[0]
                    return row[0].split('\n')[-1].split(' · ', 1)[0]

                counts = collections.Counter(namespace(r) for r in rows)
                if name == '武器目录':
                    def strength(row):
                        a, s = row[3:5]
                        value = a * (4 + s) if isinstance(a, (int, float)) and isinstance(s, (int, float)) else None
                        return descending(value)
                    spec['sort_kind'] = 'group_count_then_proxy'
                    within = '组内：DPS代理值↓；同值按ID；缺值置后'
                elif name == '仅资源候选':
                    def strength(row):
                        return ()
                    spec['sort_kind'] = 'group_count_then_id'
                    within = '无属性样本，组内按ID'
                else:
                    columns = [headers.index(h) for h in ('生命（历史）', '攻击（历史）', '护甲（历史）')]
                    def strength(row):
                        return tuple(v for i in columns for v in descending(row[i]))
                    spec['sort_kind'] = 'group_count_then_attributes'
                    within = '组内：生命↓→攻击↓→护甲↓；同值按ID；缺值置后'
                rows.sort(key=lambda r: (-counts[namespace(r)], namespace(r), strength(r), r[1]))
                groups = []
                offset = 5
                for ns, group in __import__('itertools').groupby(rows, namespace):
                    entries = list(group)
                    label = f'{owners.get(ns, ns)}\n{ns} · {len(entries)}项'
                    for row in entries:
                        row[0] = label
                    groups.append({'namespace': ns, 'start_row': offset,
                                   'count': len(entries), 'label': label})
                    offset += len(entries)
                spec['groups'] = groups
                headers[0] = '模组 / 命名空间 · 本页数量'
                spec['widths'][0] = 38
                spec['sort_note'] = '模组：本页收录条目数↓；同数按命名空间。' + within
                if name == '武器目录':
                    spec['formulas'] = {f'F{i}': f'=IF(AND(ISNUMBER(D{i}),ISNUMBER(E{i})),D{i}*(4+E{i}),"")'
                                        for i in range(5, len(rows) + 5)}
            elif name in ('EF证据分层', '全模组清单'):
                wi = headers.index('历史武器数')
                ei = headers.index('历史实体数')
                identity = 0 if name == 'EF证据分层' else 1
                rows.sort(key=lambda r: (-(r[wi] + r[ei]), r[identity]))
                spec['sort_kind'] = 'content_total'
                spec['sort_note'] = '模组：历史武器数＋历史实体数↓；同数按' + ('命名空间' if identity == 0 else 'jar文件名') + '。静态资源文件数不计入内容总数。'
            elif name == '用途统计':
                counts = collections.Counter(r[0] for r in book['sheets'][0]['rows'])
                rows.sort(key=lambda r: (-counts[r[0]], r[0]))
                spec['formulas'] = {f'B{i}': f'=COUNTIF(全模组清单!$A$5:$A${len(book["sheets"][0]["rows"]) + 4},A{i})'
                                    for i in range(5, len(rows) + 5)}
                spec['sort_kind'] = 'category_count'
                spec['sort_note'] = '用途分类：jar数↓；同数按分类名称。'
            else:
                spec['sort_note'] = '事件、旧引用与排除对象按说明顺序登记；无统一数值比较口径。'
    return books


def main():
    source = DATA / '工作簿数据.json'
    books = json.loads(source.read_text(encoding='utf-8'))
    catalog = json.loads((DATA / '制作资料汇总.json').read_text(encoding='utf-8'))
    books = apply_group_order(books, catalog)
    source.write_text(json.dumps(books, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps([{'file': b['file'], 'sheets': [
        {'name': s['name'], 'rows': len(s['rows']), 'leading_groups':
         [(g['namespace'], g['count']) for g in s.get('groups', [])[:4]]}
        for s in b['sheets']]} for b in books], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
