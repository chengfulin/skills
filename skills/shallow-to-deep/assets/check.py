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


SVG_SHAPES = r'\b(svg|text|tspan|rect|path|circle|ellipse|line|polyline|polygon|g|marker)\b'
FILL_TOKENS = ('--accent-fill', '--accent-2-fill', '--warn-fill')   # 放文字的色塊：上面的字只用 --fg
COLOR_TOKENS = ('--accent', '--accent-2', '--warn')                  # 彩色 token：線、描邊、圖示、彩色文字；放了文字就要改用 *-fill
INVERT_TOKENS = ('--fg', '--muted')                                  # 反白色塊：上面的字用 --bg／--surface
LIGHT_FILL_TOKENS = ('--bg', '--surface', '--line', 'none')          # 底色：上面的字不能用 --bg／--surface


def style_map(style_css):
    """從片段 <style> 取 SVG 文字的預設字級／預設 fill、class → 字級／text-anchor／fill。"""
    default = None
    default_fill = None
    sizes, anchors, fills = {}, {}, {}
    for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', style_css):
        m_size = re.search(r'font-size\s*:\s*([\d.]+)px', body)
        m_anchor = re.search(r'text-anchor\s*:\s*(\w+)', body)
        m_fill = re.search(r'(?<![\w-])fill\s*:\s*([^;]+)', body)
        for one in sel.split(','):
            one = one.strip()
            is_text_default = re.search(r'\bsvg\s+text(:not\(\[fill\]\))?\s*$', one) or re.search(r'\bsvg\s*$', one)
            if m_size and is_text_default:
                default = float(m_size.group(1))
            if m_fill and is_text_default:
                default_fill = m_fill.group(1).strip()
            for cls in re.findall(r'\.([\w-]+)', one):
                if m_size:
                    sizes[cls] = float(m_size.group(1))
                if m_anchor:
                    anchors[cls] = m_anchor.group(1)
                if m_fill:
                    fills[cls] = m_fill.group(1).strip()
    return default, sizes, anchors, default_fill, fills


def check_style_overrides(style_css, path):
    """片段 <style> 以元素選擇器對 SVG 元素設 fill／stroke，會蓋掉元素上的 fill="…"／stroke="…"（CSS 優先於呈現屬性）。
    只允許加 :not([fill])／:not([stroke]) 當預設值；class 選擇器不在此限（作者是刻意套用）。"""
    problems = []
    for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', style_css):
        for prop in ('fill', 'stroke'):
            if not re.search(rf'(?<![\w-]){prop}\s*:', body):
                continue
            for one in sel.split(','):
                one = one.strip()
                if not one or '.' in one.split()[-1]:
                    continue  # 最末段是 class 選擇器：刻意套用，不算覆寫
                if re.search(SVG_SHAPES, one) and f':not([{prop}])' not in one:
                    problems.append(f'{path}: <style> 以「{one}」設 {prop}，會蓋掉元素上的 {prop}="…"；改成 {one}:not([{prop}]) 只當預設值')
    return problems


def token_of(value):
    """把 fill 值正規化成 token 名（'--accent'）或 'none'／None。"""
    if value is None:
        return None
    value = value.strip()
    if value == 'none':
        return 'none'
    m = re.match(r'var\((--[\w-]+)\)', value)
    return m.group(1) if m else value


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


def check_text_overflow(svg, idx, path, default_px, class_px, class_anchor, default_fill=None, class_fill=None):
    """估每個 <text> 的寬度，對照同一座標範圍內包住它的 <rect>，或 viewBox；並檢查文字與所在色塊的 token 配對。"""
    class_fill = class_fill or {}
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
            m_sf = re.search(r'fill\s*:\s*([^;"]+)', a.get('style', ''))
            rects.append((scope_of(r.start(), scopes), float(a.get('x', 0)), float(a.get('y', 0)),
                          float(a['width']), float(a['height']), token_of(m_sf.group(1) if m_sf else a.get('fill'))))
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
        for sc, rx, ry, rw, rh, rfill in rects:
            if sc == scope and rx <= x <= rx + rw and ry <= y <= ry + rh + 1 and y - px * 0.8 >= ry - 1:
                if box is None or rw * rh < box[2] * box[3]:
                    box = (rx, ry, rw, rh, rfill)
        label = f'{path}: 第 {idx} 張 SVG 文字「{content[:24]}」估寬 {w:.0f}px，'
        if box:
            over = max(box[0] - left, right - (box[0] + box[2]))
            if over > OVERFLOW_TOLERANCE:
                problems.append(label + f'超出所在色塊（x={box[0]:g} 寬 {box[2]:g}）約 {over:.0f}px')
        elif scope == -1 and vb_w is not None:
            over = max(-left, right - vb_w)
            if over > OVERFLOW_TOLERANCE:
                problems.append(label + f'超出 viewBox 寬 {vb_w:g} 約 {over:.0f}px')
        # 文字與所在色塊的 token 配對（有效 fill 的優先序同 CSS：style= > class 規則 > fill="…" > style 的 svg text 預設）
        m_sfill = re.search(r'style="[^"]*(?<![\w-])fill\s*:\s*([^;"]+)', t.group(1))
        fill = token_of(m_sfill.group(1) if m_sfill
                        else next((class_fill[c] for c in classes if c in class_fill), None)
                        or attrs.get('fill') or default_fill)
        where = f'{path}: 第 {idx} 張 SVG 文字「{content[:24]}」'
        if fill is None:
            problems.append(where + '未指定 fill（瀏覽器預設黑色，深色主題看不見）；加 fill="var(--fg)" 或在 <style> 設 svg text:not([fill]) 的預設')
        elif box and box[4] in FILL_TOKENS and fill != '--fg':
            problems.append(where + f'fill={fill} 放在 {box[4]} 色塊上；色塊上的字只用 var(--fg)')
        elif box and box[4] in COLOR_TOKENS:
            problems.append(where + f'放在 {box[4]} 色塊上；有文字的色塊改用 var({box[4]}-fill)，字用 var(--fg)')
        elif box and box[4] in INVERT_TOKENS and fill not in ('--bg', '--surface'):
            problems.append(where + f'fill={fill} 放在 {box[4]} 反白色塊上，對比不足；字用 var(--bg) 或 var(--surface)')
        elif box and box[4] in LIGHT_FILL_TOKENS and fill in ('--bg', '--surface'):
            problems.append(where + f'fill={fill} 放在 {box[4]} 底上，看不見；改用 var(--fg)／var(--muted) 或彩色 token')
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
    default_px, class_px, class_anchor, default_fill, class_fill = style_map(style_css)
    problems += check_style_overrides(style_css, path)

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
        problems += check_text_overflow(svg, k, path, default_px, class_px, class_anchor, default_fill, class_fill)

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
