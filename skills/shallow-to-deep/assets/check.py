#!/usr/bin/env python3
"""shallow-to-deep 片段檔的靜態檢核（SKILL.md 步驟 3）。

用法：python3 check.py <dir>/part-eli5.html <dir>/part-mentor.html
輸出每個片段的規模摘要，最後一行是 `靜態檢核：PASS` 或問題清單；有問題時退出碼 1。
只用標準函式庫，不開瀏覽器。
"""
import collections
import re
import sys

NAMED_COLORS = (
    'white|black|gray|grey|red|blue|green|yellow|orange|purple|pink|brown|silver|navy|teal|'
    'maroon|olive|lime|aqua|fuchsia|cyan|magenta|gold|ivory|beige|tan|coral|salmon|crimson|'
    'indigo|violet|khaki|lavender|turquoise'
)
DEFAULT_FONT_PX = 16     # shell body 16px；SVG 未指定時瀏覽器沿用
CJK_EM = 1.0             # 中日韓全形字約 1em 寬
ASCII_EM = 0.55          # 英數與標點平均約 0.55em
OVERFLOW_TOLERANCE = 4   # 估算誤差容忍（px，以 viewBox 單位計）


def style_map(style_css):
    """從片段 <style> 取 SVG 文字的預設字級、class → 字級、class → text-anchor。"""
    default = None
    sizes, anchors = {}, {}
    for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', style_css):
        m_size = re.search(r'font-size\s*:\s*([\d.]+)px', body)
        m_anchor = re.search(r'text-anchor\s*:\s*(\w+)', body)
        for one in sel.split(','):
            one = one.strip()
            if m_size and (re.search(r'\bsvg\s+text\s*$', one) or re.search(r'\bsvg\s*$', one)):
                default = float(m_size.group(1))
            for cls in re.findall(r'\.([\w-]+)', one):
                if m_size:
                    sizes[cls] = float(m_size.group(1))
                if m_anchor:
                    anchors[cls] = m_anchor.group(1)
    return default, sizes, anchors


def text_width(txt, px):
    w = 0.0
    for ch in txt:
        w += px * (CJK_EM if ord(ch) > 0x2E7F else ASCII_EM)
    return w


def transformed_scopes(svg):
    """回傳帶 transform 的 <g> 區段 (start, end)；區段內的座標不與外層比較。"""
    scopes = []
    for m in re.finditer(r'<g\b[^>]*\btransform=', svg):
        depth, i = 0, m.start()
        for tag in re.finditer(r'<(/?)g\b[^>]*?(/?)>', svg[m.start():]):
            if tag.group(1):
                depth -= 1
            elif not tag.group(2):
                depth += 1
            if depth == 0:
                scopes.append((m.start(), m.start() + tag.end()))
                break
    return scopes


def scope_of(pos, scopes):
    for k, (a, b) in enumerate(scopes):
        if a <= pos < b:
            return k
    return -1


def check_text_overflow(svg, idx, path, default_px, class_px, class_anchor):
    """估每個 <text> 的寬度，對照同一座標範圍內包住它的 <rect>，或 viewBox。"""
    problems = []
    head = re.match(r'<svg\b[^>]*>', svg).group(0)
    vb = re.search(r'viewBox="\s*([\d.-]+)\s+([\d.-]+)\s+([\d.]+)\s+([\d.]+)', head)
    vb_w = float(vb.group(3)) if vb else None
    scopes = transformed_scopes(svg)
    rects = []
    for r in re.finditer(r'<rect\b[^>]*>', svg):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', r.group(0)))
        if 'transform' in a:
            continue
        try:
            rects.append((scope_of(r.start(), scopes), float(a.get('x', 0)), float(a.get('y', 0)),
                          float(a['width']), float(a['height'])))
        except (KeyError, ValueError):
            continue
    for t in re.finditer(r'<text\b([^>]*)>(.*?)</text>', svg, flags=re.S):
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', t.group(1)))
        content = re.sub(r'<[^>]+>', '', t.group(2)).strip()
        if not content or 'transform' in attrs or ('<tspan' in t.group(2) and 'dy=' in t.group(2)):
            continue  # 旋轉或多行文字不估
        try:
            x, y = float(attrs.get('x', 0)), float(attrs.get('y', 0))
        except ValueError:
            continue
        classes = attrs.get('class', '').split()
        # 優先序同 CSS 階層：style= 內的 font-size > class 規則 > font-size="…" 呈現屬性
        m_style = re.search(r'style="[^"]*font-size\s*:\s*([\d.]+)', t.group(1))
        m_attr = re.search(r'\bfont-size="([\d.]+)', t.group(1))
        px = (float(m_style.group(1)) if m_style
              else next((class_px[c] for c in classes if c in class_px), None)
              or (float(m_attr.group(1)) if m_attr else None)
              or default_px or DEFAULT_FONT_PX)
        w = text_width(content, px)
        m = re.search(r'text-anchor\s*[:=]\s*"?(\w+)', t.group(1))
        anchor = m.group(1) if m else next((class_anchor[c] for c in classes if c in class_anchor), 'start')
        if anchor == 'middle':
            left, right = x - w / 2, x + w / 2
        elif anchor == 'end':
            left, right = x - w, x
        else:
            left, right = x, x + w
        scope = scope_of(t.start(), scopes)
        box = None
        for sc, rx, ry, rw, rh in rects:
            if sc == scope and rx <= x <= rx + rw and ry <= y <= ry + rh + 1 and y - px * 0.8 >= ry - 1:
                if box is None or rw < box[2]:
                    box = (rx, ry, rw, rh)
        label = f'{path}: 第 {idx} 張 SVG 文字「{content[:24]}」估寬 {w:.0f}px，'
        if box:
            over = max(box[0] - left, right - (box[0] + box[2]))
            if over > OVERFLOW_TOLERANCE:
                problems.append(label + f'超出所在色塊（x={box[0]:g} 寬 {box[2]:g}）約 {over:.0f}px')
        elif scope == -1 and vb_w is not None:
            over = max(-left, right - vb_w)
            if over > OVERFLOW_TOLERANCE:
                problems.append(label + f'超出 viewBox 寬 {vb_w:g} 約 {over:.0f}px')
    return problems


def check_fragment(path, all_ids):
    s = open(path, encoding='utf-8').read()
    prefix = 'e-' if 'eli5' in path else 'm-'
    part_id = 'part-eli5' if prefix == 'e-' else 'part-mentor'
    problems = []

    # 外層 section 與禁用標籤
    if not re.search(rf'<section class="part" id="{part_id}">', s):
        problems.append(f'{path}: 缺外層 <section class="part" id="{part_id}">')
    if re.search(r'<(html|head|body)\b', s):
        problems.append(f'{path}: 含 html／head／body 標籤')
    if re.search(r'<(script|link)\b', s) or re.search(r'\b(src|href)="https?://', s):
        problems.append(f'{path}: 載入外部資源或 script')

    # 章節 article + h2
    arts = re.findall(r'<article class="chapter" id="([^"]+)">', s)
    if not arts:
        problems.append(f'{path}: 找不到 article.chapter')
    n_h2 = len(re.findall(r'<h2[ >]', s))
    for title in re.findall(r'<h2[^>]*>(.*?)</h2>', s, flags=re.S):
        plain = re.sub(r'<[^>]+>', '', title).strip()
        if re.match(r'(\d+|[一二三四五六七八九十]+|[A-Za-z])\s*[.、．)．：:]', plain):
            problems.append(f'{path}: 章名自帶編號「{plain[:20]}」（目錄的 <ol> 會再編一次）')
    if n_h2 != len(arts):
        problems.append(f'{path}: article 數 {len(arts)} 與 h2 數 {n_h2} 不符')

    # id 前綴與唯一性
    ids = re.findall(r'\bid="([^"]+)"', s)
    for i in ids:
        if i == part_id:
            continue
        if not i.startswith(prefix):
            problems.append(f'{path}: id 缺前綴 {i}')
        all_ids[i] += 1

    # 寫死顏色與透明度
    for m in re.finditer(r'(fill|stroke|color|background(?:-color)?|stop-color)\s*[:=]\s*"?([^;"\s>]+)', s):
        v = m.group(2)
        if (re.match(r'#[0-9a-fA-F]{3,8}$', v) or v.startswith(('rgb(', 'rgba(', 'hsl(', 'hsla('))
                or re.fullmatch(NAMED_COLORS, v)):
            problems.append(f'{path}: 寫死顏色 {m.group(0)}')
    for m in re.finditer(r'(?:fill-|stroke-)?opacity\s*[:=]\s*"?([0-9.]+)', s):
        problems.append(f'{path}: 含透明度 {m.group(0)}')

    # style 選擇器前綴
    style_css = ''.join(re.findall(r'<style>(.*?)</style>', s, flags=re.S))
    for sel in re.findall(r'(?:^|})\s*([^{}]+?)\s*{', style_css, flags=re.S):
        for one in sel.split(','):
            one = one.strip()
            if one and not one.startswith('#' + part_id) and not one.startswith('@'):
                problems.append(f'{path}: 選擇器未以 #{part_id} 開頭：{one}')
    default_px, class_px, class_anchor = style_map(style_css)

    # 每張 SVG：viewBox、像素寬度、同圖引用、文字寬度
    svgs = re.findall(r'<svg\b[^>]*>.*?</svg>', s, flags=re.S)
    for k, svg in enumerate(svgs, 1):
        head = re.match(r'<svg\b[^>]*>', svg).group(0)
        if 'viewBox' not in head:
            problems.append(f'{path}: 第 {k} 張 SVG 無 viewBox')
        if re.search(r'\bwidth="\d+(px)?"', head):
            problems.append(f'{path}: 第 {k} 張 SVG 屬性寫死像素寬度')
        local = set(re.findall(r'\bid="([^"]+)"', svg))
        for ref in re.findall(r'(?:href="#|url\(#)([^")]+)', svg):
            if ref not in local:
                problems.append(f'{path}: 第 {k} 張 SVG 引用 #{ref} 不在同一張 SVG 內')
        problems += check_text_overflow(svg, k, path, default_px, class_px, class_anchor)

    print(f'{path}: {len(arts)} 章、{len(svgs)} 張 SVG、{len(ids)} 個 id、{s.count(chr(10)) + 1} 行')
    return problems


def main(paths):
    if not paths:
        print(__doc__)
        return 2
    all_ids = collections.Counter()
    problems = []
    for p in paths:
        problems += check_fragment(p, all_ids)
    for i, c in all_ids.items():
        if c > 1:
            problems.append(f'id 重複 {i} ×{c}')
    print('\n'.join(problems) if problems else '靜態檢核：PASS')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
