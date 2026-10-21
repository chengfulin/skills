#!/usr/bin/env python3
"""task 粒度全域並行規劃（implement-loop.md 步驟 0P 與完成報告使用）。

子命令：
  build  讀 tasks.md 與 analyzer 產出的逐 task 集合，兩兩判定衝突、分批，
         寫出 parallel-plan.json，並把摘要合併進狀態檔 steps.implement.parallel_plan。
  check  確認 parallel-plan.json 涵蓋 tasks.md 全部未勾選 task（續跑時判斷要不要重做）。
  verify 完成報告用：以各 phase 的實際 commit 檔案核對集合涵蓋率，列出可能漏判。

集合檔格式（每個 task 一行，欄位以 " | " 分隔、清單以 "," 分隔，無則留空）：
  T014 | P=yes | W=a.ts,b/* | R=c.ts | Res=登錄點:x.ts | C=Sym@path | Dep=T013,US1 | Conf=高
"""
import argparse, fnmatch, glob, itertools, json, os, re, subprocess, sys
from collections import Counter, defaultdict

TASK_LINE = re.compile(r'^[-*] \[([ xX])\] (T\d+[a-z]?)\b(.*)$')
PHASE_HEAD = re.compile(r'^## (Phase \d+[^\n]*)$')
EXCLUDE_ACTUAL = re.compile(r'(^|/)(tasks\.md|\.sdd-workflow\.json|parallel-plan\.json)$')


def phase_label(heading):
    m = re.search(r'User Story (\d+)', heading)
    if m:
        return f'US{m.group(1)}'
    for name in ('Setup', 'Foundational', 'Polish'):
        if name.lower() in heading.lower():
            return name
    return heading.split(':')[0].strip()


def parse_tasks(path):
    """回傳依 tasks.md 出現順序的 [(id, phase, checked, has_P)]。"""
    out, phase = [], None
    for line in open(path, encoding='utf-8'):
        h = PHASE_HEAD.match(line.rstrip('\n'))
        if h:
            phase = phase_label(h.group(1))
            continue
        m = TASK_LINE.match(line)
        if m and phase:
            out.append((m.group(2), phase, m.group(1) != ' ', m.group(3).lstrip().startswith('[P]')))
    return out


def split_list(v):
    return [x.strip() for x in v.split(',') if x.strip()]


def parse_sets(dirpath):
    sets = {}
    for path in sorted(glob.glob(os.path.join(dirpath, '*.txt'))):
        for raw in open(path, encoding='utf-8'):
            line = raw.strip().strip('`')
            m = re.match(r'(T\d+[a-z]?)\s*\|', line)
            if not m:
                continue
            t = {'W': [], 'R': [], 'Res': [], 'C': [], 'Dep': [], 'Conf': '中'}
            for field in line.split('|')[1:]:
                k, _, v = field.strip().partition('=')
                if k in ('W', 'R', 'Res', 'C', 'Dep'):
                    t[k] = split_list(v)
                elif k == 'Conf':
                    t['Conf'] = v.strip() or '中'
            sets[m.group(1)] = t
    return sets


def match(a, b):
    """路徑比對；含 * 的是「檔名未定的新檔」，與同目錄任何路徑都視為相同（保守）。"""
    return a == b or ('*' in a and fnmatch.fnmatch(b, a)) or ('*' in b and fnmatch.fnmatch(a, b))


def first_hit(xs, ys):
    for x in xs:
        for y in ys:
            if match(x, y):
                return x if '*' not in x else y
    return None


def res_id(r):
    k, _, v = r.partition(':')
    return 'migration' if 'migration' in r.lower() else (v or k).strip().lower()


def conflict(a, b, A, B):
    """a 在 b 之前（tasks.md 順序）。回傳 (類型, 證據) 或 None。"""
    hit = first_hit(A['W'], B['W'])
    if hit:
        return '寫入', hit
    hit = first_hit(A['W'], B['R']) or first_hit(B['W'], A['R'])
    if hit:
        return '相依', hit
    shared = {res_id(r) for r in A['Res']} & {res_id(r) for r in B['Res']}
    if shared:
        return '資源', sorted(shared)[0]
    for X, Y in ((A, B), (B, A)):
        for sym in X['C']:
            path = sym.partition('@')[2].strip()
            if path and first_hit([path], Y['W'] + Y['R']):
                return '契約', sym
    if a in B['Dep'] or b in A['Dep']:
        return '宣告', 'task 相依'
    if A['phase'] in B['Dep'] or B['phase'] in A['Dep']:
        return '宣告', 'phase 相依（analyzer 只能指出 phase）'
    if '低' in (A['Conf'], B['Conf']):
        return '未定', '信心低：落點要等其他 task 實作後才能判定'
    return None


def write_plan(path, plan):
    """每個 task、每筆衝突、每個批次各一行，讓入版控的規劃檔可讀、diff 有意義。"""
    dump = lambda v: json.dumps(v, ensure_ascii=False)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('{\n"summary": ' + dump(plan['summary']) + ',\n')
        f.write('"batches": [\n' + ',\n'.join(dump(b) for b in plan['batches']) + '\n],\n')
        f.write('"tasks": {\n' + ',\n'.join(f'{dump(k)}: {dump(v)}' for k, v in plan['tasks'].items()) + '\n},\n')
        f.write('"conflicts": [\n' + ',\n'.join(dump(c) for c in plan['conflicts']) + '\n],\n')
        f.write('"hotspots": ' + dump(plan['hotspots']) + '\n}\n')


def build(args):
    order = parse_tasks(args.tasks)
    if not order:
        sys.exit('error=no_tasks：tasks.md 找不到任何 task 行或 Phase 標題')
    pending = [(i, ph, p) for i, ph, done, p in order if not done]
    sets = parse_sets(args.sets)
    missing = [i for i, _, _ in pending if i not in sets]
    if missing:
        print('error=missing_sets ' + ','.join(missing))
        sys.exit(3)
    ids = [i for i, _, _ in pending]
    pos = {t: n for n, t in enumerate(ids)}
    T = {}
    for i, ph, p in pending:
        T[i] = dict(sets[i], phase=ph, P=p)
    # 執行順序：先只依明文相依（Dep 列出的 task ID）做拓撲排序，同層依 tasks.md 順序；
    # 其餘衝突一律依這個順序定方向（前→後）。明文相依成環＝順序無法事前判定，
    # 環上的 task 比照低信心處理（與其他所有 task 衝突），並依 tasks.md 順序打斷後回報。
    deps = {t: {d for d in T[t]['Dep'] if d in pos} for t in ids}
    order_conflicts = [f'{t} 依賴排在後面的 {d}' for t in ids for d in sorted(deps[t], key=pos.get) if pos[d] > pos[t]]
    exec_order, done, cyclic = [], set(), []
    remaining = list(ids)
    while remaining:
        ready = [t for t in remaining if deps[t] <= done]
        if not ready:  # 明文相依成環：取 tasks.md 最前者強制放入
            ready = [remaining[0]]
            cyclic.append(remaining[0])
        t = min(ready, key=pos.get)
        exec_order.append(t)
        done.add(t)
        remaining.remove(t)
    for t in cyclic:
        T[t]['Conf'] = '低'
    conf = {}
    for a, b in itertools.combinations(ids, 2):
        c = conflict(a, b, T[a], T[b])
        if c:
            conf[(a, b)] = c
    rank = {t: n for n, t in enumerate(exec_order)}
    level, preds = {}, defaultdict(set)
    for (a, b) in conf:
        u, v = (a, b) if rank[a] < rank[b] else (b, a)
        preds[v].add(u)
    for t in exec_order:
        level[t] = 1 + max((level[u] for u in preds[t]), default=0)
    batches = defaultdict(list)
    for t in exec_order:
        batches[level[t]].append(t)
    # 關鍵路徑：從最晚的 task 沿「決定其批次的前驅」回溯
    cur = max(ids, key=lambda t: (level[t], rank[t]))
    path = [cur]
    while level[cur] > 1:
        cand = [u for u in preds[cur] if level[u] == level[cur] - 1]
        if not cand:
            break
        cur = max(cand, key=rank.get)
        path.append(cur)
    path.reverse()
    same_phase = lambda a, b: T[a]['phase'] == T[b]['phase']
    pairs = list(itertools.combinations(ids, 2))
    within = [p for p in pairs if same_phase(*p)]
    p_pairs = [p for p in within if T[p[0]]['P'] and T[p[1]]['P']]
    hot = Counter(e for (t, e) in conf.values() if t in ('寫入', '相依'))
    basis = args.basis
    summary = {
        'advisory': True,
        'granularity': 'task',
        'basis': basis,
        'tasks': len(ids),
        'pairs': len(pairs),
        'conflict_pairs': len(conf),
        'within_phase': [sum(p in conf for p in within), len(within)],
        'cross_phase': [len(conf) - sum(p in conf for p in within), len(pairs) - len(within)],
        'by_type': dict(Counter(t for t, _ in conf.values())),
        'batches': len(batches),
        'max_width': max(len(v) for v in batches.values()),
        'critical_path': path,
        'low_conf': [t for t in ids if '低' in T[t]['Conf']],
        'P_marked_conflicts': [sum(p in conf for p in p_pairs), len(p_pairs)],
        'order_conflicts': order_conflicts,
        'cyclic': cyclic,
        'plan_file': os.path.relpath(args.out, args.root) if args.root else args.out,
    }
    plan = {
        'summary': summary,
        'batches': [batches[k] for k in sorted(batches)],
        'tasks': {t: {k: T[t][k] for k in ('phase', 'P', 'W', 'R', 'Res', 'C', 'Dep', 'Conf')} for t in ids},
        'conflicts': [{'a': a, 'b': b, 'type': t, 'evidence': e} for (a, b), (t, e) in conf.items()],
        'hotspots': hot.most_common(10),
    }
    write_plan(args.out, plan)
    if args.state:
        st = json.load(open(args.state, encoding='utf-8'))
        impl = st.setdefault('steps', {}).setdefault('implement', {})
        impl['parallel_plan'] = {k: summary[k] for k in (
            'advisory', 'granularity', 'basis', 'tasks', 'conflict_pairs', 'pairs', 'by_type',
            'batches', 'max_width', 'low_conf', 'plan_file')}
        with open(args.state, 'w', encoding='utf-8') as f:
            json.dump(st, f, ensure_ascii=False, indent=2)
            f.write('\n')
    s = summary
    print(f"tasks={s['tasks']} batches={s['batches']} speedup={s['tasks'] / s['batches']:.1f}x max_width={s['max_width']}")
    print(f"conflict_pairs={s['conflict_pairs']}/{s['pairs']} within_phase={s['within_phase'][0]}/{s['within_phase'][1]} "
          f"cross_phase={s['cross_phase'][0]}/{s['cross_phase'][1]} by_type={json.dumps(s['by_type'], ensure_ascii=False)}")
    print(f"critical_path={'→'.join(path)}")
    print('hotspots=' + '; '.join(f'{e}×{n}' for e, n in plan['hotspots'][:5]))
    print(f"low_conf={','.join(s['low_conf']) or '無'}")
    print(f"P_marked_conflicts={s['P_marked_conflicts'][0]}/{s['P_marked_conflicts'][1]}")
    print(f"order_conflicts={'; '.join(order_conflicts) or '無'}")
    if cyclic:
        print(f"cyclic={','.join(cyclic)}")


def check(args):
    if not os.path.exists(args.plan):
        print('plan=missing')
        sys.exit(1)
    planned = set(json.load(open(args.plan, encoding='utf-8'))['tasks'])
    pending = [i for i, _, done, _ in parse_tasks(args.tasks) if not done]
    lack = [i for i in pending if i not in planned]
    print('plan=ok' if not lack else 'plan=stale ' + ','.join(lack))
    sys.exit(0 if not lack else 1)


def git(root, *a):
    return subprocess.run(['git', '-c', 'core.quotepath=off', '-C', root, *a],
                          capture_output=True, text=True, check=True).stdout


def verify(args):
    plan = json.load(open(args.plan, encoding='utf-8'))
    T = plan['tasks']
    nnn = args.feature
    base = git(args.root, 'log', '--format=%H', '-1', f'--grep=完成並行規劃（{nnn}）').strip()
    rng = f'{base}..HEAD' if base else 'HEAD'
    grep = {'Setup': f'完成 Setup（{nnn}）', 'Foundational': f'完成 Foundational（{nnn}）',
            'Polish': '完成功能實作（implement）'}
    phases = sorted({t['phase'] for t in T.values()}, key=lambda p: min(k for k, v in T.items() if v['phase'] == p))
    if not base:  # Polish 的 after_implement 訊息不含 NNN，沒有起點就會撈到其他 feature
        print(f'warning=no_plan_commit：找不到「完成並行規劃（{nnn}）」，略過 Polish 核對')
        phases = [p for p in phases if p != 'Polish']
    actual = {}
    for ph in phases:
        pat = grep.get(ph, f'（{nnn}, {ph}）')
        files = git(args.root, 'log', rng, '--name-only', '--format=', f'--grep={pat}', '--fixed-strings')
        actual[ph] = {f for f in files.split() if f and not EXCLUDE_ACTUAL.search(f)}
    print(f"tasks={len(T)} batches={len(plan['batches'])} speedup={len(T) / len(plan['batches']):.1f}x "
          f"conflict_pairs={plan['summary']['conflict_pairs']}/{plan['summary']['pairs']}")
    total = unc_total = risky_total = 0
    for ph in phases:
        W = [x for t in T.values() if t['phase'] == ph for x in t['W']]
        others = [x for t in T.values() if t['phase'] != ph for x in t['W'] + t['R']]
        other_act = set().union(*[actual[p] for p in phases if p != ph])
        unc = sorted(f for f in actual[ph] if not any(match(x, f) for x in W))
        risky = [f for f in unc if f in other_act or any(match(x, f) for x in others)]
        total += len(actual[ph])
        unc_total += len(unc)
        risky_total += len(risky)
        if not actual[ph]:
            print(f"{ph}: 找不到 commit（訊息 grep：{grep.get(ph, f'（{nnn}, {ph}）')}）")
        elif risky:
            print(f"{ph}: 實際 {len(actual[ph])} 檔，集合未涵蓋 {len(unc)}，可能漏判 {len(risky)}：{', '.join(risky[:6])}")
    print(f'coverage: 實際變更 {total} 檔，集合未涵蓋 {unc_total}，可能漏判（他 phase 也碰）{risky_total}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build')
    b.add_argument('--tasks', required=True)
    b.add_argument('--sets', required=True, help='analyzer 逐 task 集合檔所在目錄（*.txt）')
    b.add_argument('--out', required=True, help='parallel-plan.json 輸出路徑')
    b.add_argument('--state', help='.sdd-workflow.json；提供時寫入 steps.implement.parallel_plan')
    b.add_argument('--root', help='專案根，用來把 plan_file 記成相對路徑')
    b.add_argument('--basis', default='codegraph', choices=('codegraph', 'grep', 'greenfield'))
    c = sub.add_parser('check')
    c.add_argument('--tasks', required=True)
    c.add_argument('--plan', required=True)
    v = sub.add_parser('verify')
    v.add_argument('--plan', required=True)
    v.add_argument('--root', required=True)
    v.add_argument('--feature', required=True, help='feature 編號 NNN')
    a = ap.parse_args()
    {'build': build, 'check': check, 'verify': verify}[a.cmd](a)


if __name__ == '__main__':
    main()
