#!/usr/bin/env python3
"""task 粒度全域並行規劃與波次排程（implement-loop.md 步驟 0P、並行模式與完成報告使用）。

子命令：
  build  讀 tasks.md 與 analyzer 產出的逐 task 集合，兩兩判定衝突、分批、模擬波次並決定
         執行模式，寫出 parallel-plan.json，並把摘要合併進狀態檔 steps.implement.parallel_plan。
  check  確認 parallel-plan.json 涵蓋 tasks.md 全部未勾選 task（續跑時判斷要不要重做）。
  next   並行模式：依目前勾選狀態排出下一個波次（每個 phase 一條 lane），寫入狀態檔
         steps.implement.current_wave；已有進行中的波次則原樣印出（續跑）。
  close  並行模式：波次 commit 前呼叫，waves_done 加 1 並移除 current_wave。
  mode   改用另一個執行模式（使用者指定、降級回依序）：同時改寫 parallel-plan.json 與狀態檔，
         兩處的 mode 永遠一致。
  verify 完成報告用：以實際 commit 檔案核對集合涵蓋率，列出可能漏判。

名詞（本 skill 自訂，詳見 README「名詞：批次與波次」）：
  批次（batch） 規劃產物：依衝突關係分層，同批 task 兩兩不衝突。只用來衡量並行潛力，不照它執行。
  波次（wave）  執行單位：每個 phase 一條 lane，lane 內的 task 由同一個 implementer 依序做、
                可以互相依賴；不同 lane 兩兩不衝突，同時實作、一起過閘門、一個波次一個 commit。
                由同一份衝突規劃排出，一個波次通常涵蓋多個批次的 task。

集合檔格式（每個 task 一行，欄位以 " | " 分隔、清單以 "," 分隔，無則留空）：
  T014 | P=yes | W=a.ts,b/* | R=c.ts | Res=登錄點:x.ts | C=Sym@path | Dep=T013,US1 | Conf=高 | Kind=test
  Kind 可省略；test＝測試先行的測試 task（對應實作完成前預期失敗）；gate＝收尾 task（執行全部
  測試／lint 並修到通過，寫入集合事先無法預知）——不參與集合衝突判定，排在同 phase 最後。
"""
import argparse, fnmatch, glob, itertools, json, os, re, subprocess, sys
from collections import Counter, defaultdict

TASK_LINE = re.compile(r'^[-*] \[([ xX])\] (T\d+[a-z]?)\b(.*)$')
PHASE_HEAD = re.compile(r'^## (Phase \d+[^\n]*)$')
EXCLUDE_ACTUAL = re.compile(r'(^|/)(tasks\.md|\.sdd-workflow\.json|parallel-plan\.json)$')
# 波次的上限：同時執行的 lane（implementer）數、單一 lane 累計的寫入檔數
MAX_LANES, MAX_LANE_FILES = 3, 12
# 自動採用並行模式的門檻：波次模擬的估計加速、分析基礎；另要求波次數不多於 phase 數
# （每個波次都要跑一輪整合測試、審查與驗收，波次比 phase 多時總成本高於依序模式）
MIN_SPEEDUP = 1.5
# 測試檔判別（預期紅燈只列測試檔，不列測試輔助檔）
TEST_FILE = re.compile(r'(\.(test|spec)\.[^/]+$|_test\.[^/]+$|(^|/)test_[^/]+\.py$|\.bats$)')
# E2E 的 port 分配基準（環境變數 SDD_PORT_BASE 可改）：unit j 用 基準+j，閘門用 基準+10 起
PORT_BASE = int(os.environ.get('SDD_PORT_BASE', '4100'))


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
            t = {'W': [], 'R': [], 'Res': [], 'C': [], 'Dep': [], 'Conf': '中', 'Kind': ''}
            for field in line.split('|')[1:]:
                k, _, v = field.strip().partition('=')
                if k in ('W', 'R', 'Res', 'C', 'Dep'):
                    t[k] = split_list(v)
                elif k == 'Conf':
                    t['Conf'] = v.strip() or '中'
                elif k == 'Kind':
                    t['Kind'] = v.strip().lower()
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
    if 'gate' in (A.get('Kind'), B.get('Kind')):
        # 收尾 task 的寫入集合無法預知，不做集合判定：只與同 phase（排在其後）與明文相依衝突
        if A['phase'] == B['phase']:
            return '宣告', '收尾 task 排在同 phase 最後'
        if a in B['Dep'] or b in A['Dep'] or A['phase'] in B['Dep'] or B['phase'] in A['Dep']:
            return '宣告', '收尾 task 的明文相依'
        return None
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


def directed_preds(order, conflicts):
    """衝突依執行順序定方向（前→後），回傳每個 task 必須先完成的 task 集合。"""
    rank = {t: n for n, t in enumerate(order)}
    preds = defaultdict(set)
    for a, b in conflicts:
        u, v = (a, b) if rank[a] < rank[b] else (b, a)
        preds[v].add(u)
    return preds


def plan_wave(order, preds, phase, W, done):
    """排出下一個波次：回傳 {phase: [task...]}。

    每個 phase 一條 lane，lane 內的 task 由同一個 implementer 依序做，可以彼此相依；
    task 進波次的條件是所有前驅已完成，或前驅在同一條 lane。不同 lane 的 task 因此
    兩兩不衝突。lane 數上限 MAX_LANES，lane 累計寫入檔超過 MAX_LANE_FILES 就收口。
    """
    lanes, files, closed = {}, {}, set()
    for t in order:
        ph = phase[t]
        if t in done or ph in closed or (ph not in lanes and len(lanes) >= MAX_LANES):
            continue
        if not all(p in done or p in lanes.get(ph, ()) for p in preds[t]):
            continue
        grown = files.get(ph, set()) | set(W[t])
        if ph in lanes and len(grown) > MAX_LANE_FILES:
            closed.add(ph)
            continue
        lanes.setdefault(ph, []).append(t)
        files[ph] = grown
    return lanes


def simulate_waves(order, preds, phase, W):
    """從零開始排完全部 task，回傳 (波次數, 估計成本＝各波次最長 lane 的 task 數總和)。"""
    done, waves, cost = set(), 0, 0
    while len(done) < len(order):
        lanes = plan_wave(order, preds, phase, W, done)
        if not lanes:
            sys.exit('error=no_progress：排不出下一個波次（前驅關係有誤）')
        waves += 1
        cost += max(len(v) for v in lanes.values())
        done.update(t for v in lanes.values() for t in v)
    return waves, cost


def write_plan(path, plan):
    """每個 task、每筆衝突、每個批次各一行，讓入版控的規劃檔可讀、diff 有意義。"""
    dump = lambda v: json.dumps(v, ensure_ascii=False)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('{\n"summary": ' + dump(plan['summary']) + ',\n')
        f.write('"order": ' + dump(plan['order']) + ',\n')
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
    for g in ids:  # 收尾 task 排在同 phase 其他 task 之後
        if T[g]['Kind'] == 'gate':
            deps[g] |= {t for t in ids if T[t]['phase'] == T[g]['phase'] and T[t]['Kind'] != 'gate'}
    order_conflicts = [f'{t} 依賴排在後面的 {d}' for t in ids for d in sorted(deps[t] & set(T[t]['Dep']), key=pos.get)
                       if pos[d] > pos[t]]
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
    phase_of = {t: T[t]['phase'] for t in ids}
    waves, cost = simulate_waves(exec_order, directed_preds(exec_order, conf), phase_of,
                                 {t: T[t]['W'] for t in ids})
    est = len(ids) / cost
    n_phases = len(set(phase_of.values()))
    # 熱點檔：被半數以上 user story 寫入的檔案——它把 story 串成一條鏈，建議拆檔或移到 Foundational
    stories = {p for p in phase_of.values() if p.startswith('US')}
    writers = defaultdict(set)
    for t in ids:
        for f in T[t]['W']:
            if '*' not in f and T[t]['phase'] in stories:
                writers[f].add(T[t]['phase'])
    hot_files = sorted((f for f, ps in writers.items() if len(ps) >= max(2, (len(stories) + 1) // 2)),
                       key=lambda f: -len(writers[f]))
    if basis != 'codegraph':
        mode, reason = 'sequential', f'分析基礎為 {basis}，集合不足以作為並行實作的邊界'
    elif est < MIN_SPEEDUP:
        mode, reason = 'sequential', f'波次估計加速 {est:.1f}x 未達 {MIN_SPEEDUP}x'
    elif waves > n_phases:
        mode, reason = 'sequential', f'波次數 {waves} 多於 phase 數 {n_phases}，閘門輪數比依序模式多'
    else:
        mode, reason = 'parallel', f'波次估計加速 {est:.1f}x，分析基礎 codegraph'
    summary = {
        'mode': mode,
        'mode_reason': reason,
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
        'phases': n_phases,
        'waves': waves,
        'est_speedup': round(est, 2),
        'critical_path': path,
        'low_conf': [t for t in ids if '低' in T[t]['Conf']],
        'P_marked_conflicts': [sum(p in conf for p in p_pairs), len(p_pairs)],
        'order_conflicts': order_conflicts,
        'cyclic': cyclic,
        'hot_files': [f'{f}({len(writers[f])}/{len(stories)})' for f in hot_files],
        'plan_file': os.path.relpath(args.out, args.root) if args.root else args.out,
    }
    plan = {
        'summary': summary,
        'order': exec_order,
        'batches': [batches[k] for k in sorted(batches)],
        'tasks': {t: {k: T[t][k] for k in ('phase', 'P', 'W', 'R', 'Res', 'C', 'Dep', 'Conf', 'Kind')} for t in ids},
        'conflicts': [{'a': a, 'b': b, 'type': t, 'evidence': e} for (a, b), (t, e) in conf.items()],
        'hotspots': hot.most_common(10),
    }
    write_plan(args.out, plan)
    if args.state:
        st = json.load(open(args.state, encoding='utf-8'))
        impl = st.setdefault('steps', {}).setdefault('implement', {})
        impl['parallel_plan'] = {k: summary[k] for k in (
            'mode', 'mode_reason', 'granularity', 'basis', 'tasks', 'conflict_pairs', 'pairs',
            'by_type', 'batches', 'max_width', 'phases', 'waves', 'est_speedup', 'low_conf', 'plan_file')}
        impl.pop('current_wave', None)
        save_state(args.state, st)
    s = summary
    print(f"mode={s['mode']}（{s['mode_reason']}）")
    print(f"waves={s['waves']} phases={s['phases']} est_speedup={s['est_speedup']}x")
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
    if hot_files:
        print(f"hot_files={','.join(s['hot_files'])}")


def save_state(path, st):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
        f.write('\n')


def check(args):
    if not os.path.exists(args.plan):
        print('plan=missing')
        sys.exit(1)
    plan = json.load(open(args.plan, encoding='utf-8'))
    if 'order' not in plan:  # 導入並行實作前產出的規劃檔，缺執行順序，無法排波次
        print('plan=stale 規劃檔版本過舊')
        sys.exit(1)
    planned = set(plan['tasks'])
    pending = [i for i, _, done, _ in parse_tasks(args.tasks) if not done]
    lack = [i for i in pending if i not in planned]
    print('plan=ok' if not lack else 'plan=stale ' + ','.join(lack))
    sys.exit(0 if not lack else 1)


def next_wave(args):
    st = json.load(open(args.state, encoding='utf-8'))
    impl = st.setdefault('steps', {}).setdefault('implement', {})
    cur = impl.get('current_wave')
    if cur:  # 續跑：波次已排定（可能已派遣或已合併），不重排
        print(f"wave={cur['k']} resume=yes completes={','.join(cur['completes']) or '無'}")
        print_wave(cur)
        return
    plan = json.load(open(args.plan, encoding='utf-8'))
    T = plan['tasks']
    status = parse_tasks(args.tasks)
    done = {i for i, _, d, _ in status if d}
    lack = [i for i, _, d, _ in status if not d and i not in T]
    if lack:
        print('error=stale_plan ' + ','.join(lack))
        sys.exit(3)
    pending = [t for t in plan['order'] if t not in done]
    if not pending:
        print('wave=none')
        return
    preds = directed_preds(plan['order'], [(c['a'], c['b']) for c in plan['conflicts']])
    lanes = plan_wave(plan['order'], preds, {t: v['phase'] for t, v in T.items()},
                      {t: v['W'] for t, v in T.items()}, done)
    if not lanes:
        print('error=no_progress：排不出下一個波次（前驅關係有誤）')
        sys.exit(3)
    reason = ''
    if args.setup_first and 'Setup' in lanes:
        # 專案根還沒有可用的測試工具鏈：先只做 Setup，其他 lane 在沒有工具鏈的 worktree 裡無法驗證
        lanes, reason = {'Setup': lanes['Setup']}, 'toolchain'
    picked = {t for v in lanes.values() for t in v}
    completes = [ph for ph in lanes if all(t in picked for t in pending if T[t]['phase'] == ph)]
    units = {}
    for n, (ph, ts) in enumerate(lanes.items(), 1):
        W = list(dict.fromkeys(x for t in ts for x in T[t]['W']))
        # 修正邊界的延伸：同 phase 先前波次已完成 task 的寫入集合（修正常要動前面 task 建的檔）
        fix = [x for x in dict.fromkeys(x for t in plan['order'] if t in done and T[t]['phase'] == ph
                                        for x in T[t]['W']) if x not in W]
        units[f'u{n}'] = {'phase': ph, 'tasks': ts, 'W': W, 'fix': fix, 'port': PORT_BASE + n}
    # lane 內可用的修正邊界：fix+ 扣掉同波次其他 lane 的 W 與 R（含收尾 task 的 lane 在 worktree 裡修正時用；
    # 完整的 fix+ 只用於專案根的 W6／W8 修正）
    for u, v in units.items():
        others = [x for o, w in units.items() if o != u for t in w['tasks'] for x in T[t]['W'] + T[t]['R']]
        v['lane_fix'] = [f for f in v['fix'] if not any(match(f, x) for x in others)]
    # 預期紅燈：已寫好（已完成或本波次會做）的測試先行 task，其對應實作在本波次結束後仍未完成。
    # 對應實作＝同 phase、非 test／gate、寫入集合與該測試讀取集合相交的 task；找不到（E2E 常只讀
    # fixture）時退回「所屬 phase 仍有未完成 task」。只列測試檔。
    after = done | picked
    open_ph = {T[t]['phase'] for t in pending if t not in picked}

    def still_red(t):
        impls = [i for i, v in T.items() if v['phase'] == T[t]['phase'] and v.get('Kind') not in ('test', 'gate')
                 and first_hit(v['W'], T[t]['R'])]
        return any(i not in after for i in impls) if impls else T[t]['phase'] in open_ph
    red_tasks = [t for t in plan['order'] if t in after and T[t].get('Kind') == 'test' and still_red(t)]
    red = list(dict.fromkeys(x for t in red_tasks for x in T[t]['W'] if TEST_FILE.search(x)))
    # 已 commit 的部分（worktree 裡看得到的），附給 implementer
    red_base = list(dict.fromkeys(x for t in red_tasks if t in done for x in T[t]['W'] if TEST_FILE.search(x)))
    k = impl.get('waves_done', 0) + 1
    gates = len(units) + sum(1 for ph in completes if ph.startswith('US'))  # reviewer 每 unit、validator 每 story
    impl['current_wave'] = {'k': k, 'units': units, 'completes': completes, 'expected_red': red,
                            'expected_red_base': red_base,
                            'gate_ports': [PORT_BASE + 10 + i for i in range(gates)]}
    save_state(args.state, st)
    print(f"wave={k} units={len(units)} completes={','.join(completes) or '無'}"
          + (f' reason={reason}' if reason else ''))
    print_wave(impl['current_wave'])


def print_wave(cur):
    for u, v in cur['units'].items():
        print(f"{u} | {v['phase']} | {','.join(v['tasks'])} | W={','.join(v['W'])}")
        if v.get('fix'):
            print(f"{u} fix+={','.join(v['fix'])}")
        if v.get('lane_fix'):
            print(f"{u} lane-fix+={','.join(v['lane_fix'])}")
    print(f"expected_red={','.join(cur.get('expected_red', [])) or '無'}")
    print(f"expected_red_base={','.join(cur.get('expected_red_base', [])) or '無'}")
    ports = ' '.join(f"{u}={v['port']}" for u, v in cur['units'].items() if 'port' in v)
    if ports:
        print(f"ports={ports} gates={','.join(map(str, cur.get('gate_ports', [])))}")


def close_wave(args):
    st = json.load(open(args.state, encoding='utf-8'))
    impl = st['steps']['implement']
    if not impl.pop('current_wave', None):
        print('error=no_current_wave')
        sys.exit(1)
    impl['waves_done'] = impl.get('waves_done', 0) + 1
    save_state(args.state, st)
    print(f"waves_done={impl['waves_done']}")


def set_mode(args):
    plan = json.load(open(args.plan, encoding='utf-8'))
    reason = args.reason
    plan['summary'].update(mode=args.set, mode_reason=reason)
    write_plan(args.plan, plan)
    st = json.load(open(args.state, encoding='utf-8'))
    pp = st.setdefault('steps', {}).setdefault('implement', {}).setdefault('parallel_plan', {})
    pp.update(mode=args.set, mode_reason=reason)
    save_state(args.state, st)
    print(f"mode={args.set}（{reason}）")


def git(root, *a):
    return subprocess.run(['git', '-c', 'core.quotepath=off', '-C', root, *a],
                          capture_output=True, text=True, check=True).stdout


def feature_files(args):
    """feature 目錄（tasks.md、狀態檔、spec／plan 等設計文件）不是實作產物，不列入涵蓋率。"""
    fdir = os.path.relpath(os.path.dirname(os.path.abspath(args.plan)), os.path.abspath(args.root)) + '/'
    return lambda f: f.startswith(fdir) or EXCLUDE_ACTUAL.search(f)


def verify_waves(args, plan, rng):
    """並行模式：每個波次 commit 的 body 有 tasks: 行，可逐波次核對集合涵蓋率。"""
    T, nnn, skip = plan['tasks'], args.feature, feature_files(args)
    log = git(args.root, 'log', rng, '--reverse', '--format=%x01%H%x00%B', f'--grep=（{nnn}）', '--fixed-strings')
    waves = []
    for rec in log.split('\x01')[1:]:
        sha, _, body = rec.partition('\x00')
        if '實作波次' not in body.split('\n', 1)[0]:
            continue
        m = re.search(r'^tasks:\s*(.+)$', body, re.M)
        tasks = [t for t in split_list(m.group(1)) if t in T] if m else []
        files = git(args.root, 'show', '--name-only', '--format=', sha.strip())
        waves.append((body.split('\n', 1)[0], tasks, {f for f in files.split() if f and not skip(f)}))
    s = plan['summary']
    print(f"tasks={len(T)} waves={len(waves)}（預估 {s.get('waves')}）est_speedup={s.get('est_speedup')}x "
          f"conflict_pairs={s['conflict_pairs']}/{s['pairs']}")
    total = unc_total = risky_total = 0
    for n, (subject, tasks, actual) in enumerate(waves):
        W = [x for t in tasks for x in T[t]['W']]
        others = [x for t in T if t not in tasks for x in T[t]['W'] + T[t]['R']]
        other_act = set().union(*[w[2] for i, w in enumerate(waves) if i != n])
        unc = sorted(f for f in actual if not any(match(x, f) for x in W))
        risky = [f for f in unc if f in other_act or any(match(x, f) for x in others)]
        total, unc_total, risky_total = total + len(actual), unc_total + len(unc), risky_total + len(risky)
        if not tasks:
            print(f"{subject}: body 缺 tasks: 行，無法核對")
        elif risky:
            print(f"{subject}: 實際 {len(actual)} 檔，集合未涵蓋 {len(unc)}，可能漏判 {len(risky)}：{', '.join(risky[:6])}")
    print(f'coverage: 實際變更 {total} 檔，集合未涵蓋 {unc_total}，可能漏判（他波次也碰）{risky_total}')


def verify(args):
    plan = json.load(open(args.plan, encoding='utf-8'))
    T = plan['tasks']
    nnn = args.feature
    base = git(args.root, 'log', '--format=%H', '-1', f'--grep=完成並行規劃（{nnn}）').strip()
    rng = f'{base}..HEAD' if base else 'HEAD'
    # mode 以狀態檔為準（使用者指定或降級時兩處都會改；舊流程只改了狀態檔）
    mode = plan['summary'].get('mode')
    if args.state and os.path.exists(args.state):
        mode = json.load(open(args.state, encoding='utf-8')).get('steps', {}).get(
            'implement', {}).get('parallel_plan', {}).get('mode', mode)
    print(f'mode={mode}')
    if mode == 'parallel':
        return verify_waves(args, plan, rng)
    skip = feature_files(args)
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
        actual[ph] = {f for f in files.split() if f and not skip(f)}
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
    n = sub.add_parser('next')
    n.add_argument('--tasks', required=True)
    n.add_argument('--plan', required=True)
    n.add_argument('--state', required=True)
    n.add_argument('--setup-first', action='store_true',
                   help='專案根還沒有可用的測試工具鏈時：Setup 有未完成 task 就只排 Setup 一條 lane')
    cl = sub.add_parser('close')
    cl.add_argument('--state', required=True)
    m = sub.add_parser('mode')
    m.add_argument('--plan', required=True)
    m.add_argument('--state', required=True)
    m.add_argument('--set', required=True, choices=('parallel', 'sequential'))
    m.add_argument('--reason', required=True, help='寫入 mode_reason，如「使用者指定：驗證並行流程」')
    v = sub.add_parser('verify')
    v.add_argument('--plan', required=True)
    v.add_argument('--state', help='.sdd-workflow.json；提供時以其 parallel_plan.mode 為準')
    v.add_argument('--root', required=True)
    v.add_argument('--feature', required=True, help='feature 編號 NNN')
    a = ap.parse_args()
    {'build': build, 'check': check, 'next': next_wave, 'close': close_wave, 'mode': set_mode,
     'verify': verify}[a.cmd](a)


if __name__ == '__main__':
    main()
