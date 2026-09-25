"""check_kubejs_rhino.py — KubeJS/Rhino 块内声明静态扫描

背景（2026-09-25 实测结论，见 docs/HANDOVER.md 四点七）：
  本包所用 KubeJS 2001.6.5 + rhino-forge-2001.2.3 里，凡嵌在控制流块
  （if / else / for / while / switch / try / catch / do）内部的 const / let，
  第一次执行会把名字写进持久作用域，**第二次执行同一行即抛
  `TypeError: redeclaration of var X`**。
  回调函数最外层的 const/let 安全（每次调用新建激活对象）。

  危害分两档：
    · KubeJS 自有事件（EntityEvents/ServerEvents/ItemEvents/PlayerEvents…）
      → 异常被 KubeJS 捕获，只刷日志，功能静默失效；
    · ForgeEvents.onEvent（原生 Forge 总线，只在 startup 脚本可用）
      → Forge 总线记录后重新抛出 → 直接崩游戏（Ticking entity）。

用法：
    python tools/check_kubejs_rhino.py            # 扫 kubejs/ 下全部脚本
    python tools/check_kubejs_rhino.py <路径>...  # 扫指定文件/目录
退出码 0 = 干净，1 = 有风险点（可用于提交前钩子）。
"""
import os
import re
import sys

CTRL = re.compile(r'\b(if|for|while|switch|catch|try|do|else)\b')
BACKSLASH = chr(92)
QUOTES = ('"', "'", '`')


def strip_noise(src):
    """去掉 // 注释与字符串字面量，避免大括号计数被带偏"""
    out = []
    i, n = 0, len(src)
    in_s = None
    while i < n:
        c = src[i]
        if in_s:
            if c == BACKSLASH:
                out.append(' ')
                i += 2
                continue
            if c == in_s:
                in_s = None
            out.append('\n' if c == '\n' else ' ')
            i += 1
            continue
        if src.startswith('//', i):
            j = src.find('\n', i)
            i = j if j >= 0 else n
            continue
        if c in QUOTES:
            in_s = c
            out.append(' ')
            i += 1
            continue
        out.append(c)
        i += 1
    return ''.join(out)


def block_kinds(text):
    """返回 top_at[]：每个字符位置上，所处块的最内层类型（'fn' / 'ctrl' / None）

    关键点：语句段（seg）只在**括号深度为 0** 的 ; { } 处重置，
    否则 for (let i = 0; i < n; i++) 会被头部的分号切断而误判成函数块。
    """
    top_at = [None] * (len(text) + 1)
    stack = []
    seg = []
    paren = 0
    for idx, c in enumerate(text):
        top_at[idx] = stack[-1] if stack else None
        if c == '(':
            paren += 1
        elif c == ')':
            if paren > 0:
                paren -= 1
        if c == '{':
            last = ''.join(seg).strip().splitlines()
            head = last[-1] if last else ''
            stack.append('ctrl' if CTRL.search(head) else 'fn')
            seg = []
        elif c == '}':
            if stack:
                stack.pop()
            seg = []
        elif c == ';' and paren == 0:
            seg = []
        else:
            seg.append(c)
    return top_at


def scan_file(path):
    src = open(path, encoding='utf-8', errors='replace').read()
    text = strip_noise(src)
    top_at = block_kinds(text)
    raw_lines = src.splitlines()
    hits = []
    for m in re.finditer(r'(?m)^[ \t]*(const|let)[ \t]+([A-Za-z_$][\w$]*)', text):
        if top_at[m.start()] == 'ctrl':
            line = text.count('\n', 0, m.start()) + 1
            raw = raw_lines[line - 1].strip() if line <= len(raw_lines) else ''
            hits.append((line, m.group(1), m.group(2), raw))
    return hits


def collect(targets):
    files = []
    for t in targets:
        if os.path.isdir(t):
            for root, _dirs, names in os.walk(t):
                for nm in names:
                    if nm.endswith('.js') and nm != 'example.js':
                        files.append(os.path.join(root, nm))
        elif os.path.isfile(t):
            files.append(t)
    return sorted(files)


def main(argv):
    roots = argv[1:] or ['kubejs']
    if len(roots) == 1 and not os.path.exists(roots[0]):
        roots = ['kubejs'] if os.path.isdir('kubejs') else roots
    files = collect(roots)
    if not files:
        print('未找到脚本（在整合包根目录运行：python tools/check_kubejs_rhino.py）')
        return 0
    total = 0
    for f in files:
        hits = scan_file(f)
        if not hits:
            continue
        total += len(hits)
        print('### %s — %d 处风险' % (f.replace(BACKSLASH, '/'), len(hits)))
        for line, kw, name, raw in hits:
            print('    L%-5d %-5s %-16s %s' % (line, kw, name, raw[:76]))
    print()
    if total:
        print('共 %d 处「控制流块内 const/let」：第二次执行会抛 redeclaration。' % total)
        print('修法：声明提到所属函数/回调的最外层（块内只做赋值）。')
        return 1
    print('干净：未发现控制流块内的 const/let。')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))