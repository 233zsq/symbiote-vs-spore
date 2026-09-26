"""check_kubejs_rhino.py — KubeJS/Rhino 块内声明静态扫描

背景（2026-09-26 实证结论，见 docs/HANDOVER.md 四点八/四点九）：
  本包所用 KubeJS 2001.6.5 + rhino-forge-2001.2.3 里，凡嵌在控制流块
  （if / else / for / while / switch / do / try / catch）内部的 const / let，
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

实现说明（对抗性测试后的三处修正，见 docs/对抗式审查_2026-09-26.md）：
  1. 同时剥离 `//` 与 `/* */` 注释——块注释里的花括号曾让后续所有行漏报
  2. 控制流判定用「整个语句段」而不是「最后一行」——多行条件头 `if (a &&\n b) {` 曾漏报
  3. 声明匹配支持解构 `const {a} = x` / `const [a] = x`
"""
import os
import re
import sys

CTRL = re.compile(r'\b(if|for|while|switch|catch|try|do|else)\b')
DECL = re.compile(r'(?m)^[ \t]*(const|let)[ \t]*(\{|\[|[A-Za-z_$])')
BACKSLASH = chr(92)
QUOTES = ('"', "'", '`')


def strip_noise(src):
    """去掉行注释、块注释与字符串字面量，避免大括号计数被带偏"""
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
        if src.startswith('/*', i):
            j = src.find('*/', i + 2)
            # 块注释可能跨多行：保留换行以维持行号
            seg = src[i:(j + 2) if j >= 0 else n]
            out.append('\n' * seg.count('\n'))
            i = (j + 2) if j >= 0 else n
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

    语句段（seg）只在**括号深度为 0** 的 ; { } 处重置，
    这样 for (let i = 0; i < n; i++) 不会被头部分号切断；
    分类看**整段**而非最后一行，兼容多行条件头。
    另外：`}` 之后若紧跟 `while (...)`，**且该 `}` 关掉的是 `do` 块**，才把这段当作
    do-while 尾巴吃掉——否则会污染下一块的分段（假阳性），或反过来吃掉真正的 while 循环
    （假阴性）。判别依据是块种类：只有 `do {` 开的块才有尾巴。
    """
    top_at = [None] * (len(text) + 1)
    stack = []
    seg = []
    paren = 0
    idx = 0
    n = len(text)
    while idx < n:
        c = text[idx]
        top_at[idx] = stack[-1] if stack else None
        if c == '(':
            paren += 1
        elif c == ')':
            if paren > 0:
                paren -= 1
        if c == '{':
            body = ''.join(seg).strip()
            first = body.split()[0] if body.split() else ''
            if first == 'do':
                stack.append('do')
            elif CTRL.search(body):
                stack.append('ctrl')
            else:
                stack.append('fn')
            seg = []
        elif c == '}':
            popped = stack.pop() if stack else None
            seg = []
            if popped == 'do':
                # 吃掉 do-while 尾巴：while + 平衡括号
                j = idx + 1
                while j < n and text[j] in ' \t\r\n':
                    j += 1
                if text.startswith('while', j) and not (j + 5 < n and (text[j + 5].isalnum() or text[j + 5] == '_')):
                    k = j + 5
                    depth = 0
                    while k < n:
                        if text[k] == '(':
                            depth += 1
                        elif text[k] == ')':
                            depth -= 1
                            if depth == 0:
                                break
                        k += 1
                    for m in range(idx + 1, min(k + 1, n)):
                        top_at[m] = stack[-1] if stack else None
                    idx = k + 1
                    seg = []
                    continue
        elif c == ';' and paren == 0:
            seg = []
        else:
            seg.append(c)
        idx += 1
    return top_at


def scan_file(path):
    src = open(path, encoding='utf-8', errors='replace').read()
    text = strip_noise(src)
    top_at = block_kinds(text)
    raw_lines = src.splitlines()
    hits = []
    for m in re.finditer(DECL, text):
        if top_at[m.start()] in ('ctrl', 'do'):
            line = text.count('\n', 0, m.start()) + 1
            raw = raw_lines[line - 1].strip() if line <= len(raw_lines) else ''
            name = m.group(2) if m.group(2) not in ('{', '[') else m.group(2) + '…'
            hits.append((line, m.group(1), name, raw))
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