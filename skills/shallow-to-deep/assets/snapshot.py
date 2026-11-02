#!/usr/bin/env python3
"""shallow-to-deep 的實看截圖（SKILL.md 步驟 5）。

用法：python3 snapshot.py <dir>/index.html <vdir> [--page-height 3000] [--min-width 720] [--chrome <path>]
做三件事，不起伺服器、不改 index.html：
1. 在 <vdir> 建驗證副本：補 doctype 與 charset，注入一段 script 讀網址參數
   theme=light|dark、only=<part id>、skip=<px>（分頁）、w=<px>（限制內容寬度）。
2. 以 headless Chrome --dump-dom 量各部高度，並以最小寬度（預設 720px）檢查 .wrap 有無水平溢出。
3. 深色主題逐部分頁截圖（每頁 1280×page-height），淺色各部第一頁，另截頁首（目錄）。
印出量測結果與每張 PNG 的路徑；看完後 `rm -rf <vdir>`。找不到 Chrome 時退出碼 2。
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

INJECT = '''<!doctype html>
<meta charset="utf-8">
<script>
(function () {
  var q = new URLSearchParams(location.search), css = '';
  var t = q.get('theme'); if (t) document.documentElement.setAttribute('data-theme', t);
  var only = q.get('only'); if (only) css += '.part:not(#' + only + '),.part-banner,header.hero,nav.toc,footer{display:none!important}';
  var w = q.get('w'); if (w) css += 'html,body{width:' + w + 'px!important;max-width:' + w + 'px!important}';
  var skip = q.get('skip'); if (skip) css += '.wrap{margin-top:-' + skip + 'px!important}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
  addEventListener('load', function () {
    var d = document.documentElement, wr = document.querySelector('.wrap') || d;
    document.title = 'H=' + d.scrollHeight + ' WRAP=' + wr.scrollWidth + '/' + wr.clientWidth;
  });
})();
</script>
'''
CHROME_CANDIDATES = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    'google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser',
]


def find_chrome(explicit):
    for c in ([explicit] if explicit else []) + CHROME_CANDIDATES:
        if c and (os.path.isfile(c) or shutil.which(c)):
            return c
    return None


def run_chrome(chrome, profile, args):
    cmd = [chrome, '--headless=new', '--hide-scrollbars', f'--user-data-dir={profile}'] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120).stdout


def metric(chrome, profile, url, query, width=1280):
    dom = run_chrome(chrome, profile, [f'--window-size={width},1000', '--dump-dom', f'{url}?{query}'])
    m = re.search(r'<title>H=(\d+) WRAP=(\d+)/(\d+)', dom)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (None, None, None)


def shot(chrome, profile, url, query, out, size):
    run_chrome(chrome, profile, [f'--window-size={size}', f'--screenshot={out}', f'{url}?{query}'])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('index')
    ap.add_argument('vdir')
    ap.add_argument('--page-height', type=int, default=3000)
    ap.add_argument('--min-width', type=int, default=720)
    ap.add_argument('--chrome')
    a = ap.parse_args()

    chrome = find_chrome(a.chrome)
    if not chrome:
        print('找不到 headless Chrome；回報「未實看」。', file=sys.stderr)
        return 2
    os.makedirs(a.vdir, exist_ok=True)
    html = re.sub(r'^\s*<!doctype html>\s*', '', open(a.index, encoding='utf-8').read(), flags=re.I)
    copy = os.path.join(a.vdir, 'index.html')
    open(copy, 'w', encoding='utf-8').write(INJECT + html)
    url = 'file://' + os.path.abspath(copy)
    profile = os.path.join(a.vdir, 'profile')
    parts = re.findall(r'<section class="part" id="([^"]+)"', html)

    print('## 量測')
    h_full, wrap_sw, wrap_cw = metric(chrome, profile, url, f'w={a.min_width}')
    flag = 'OK' if wrap_sw == wrap_cw else f'溢出 {wrap_sw - wrap_cw}px'
    print(f'最小寬度 {a.min_width}px：.wrap scrollWidth/clientWidth = {wrap_sw}/{wrap_cw} → {flag}')
    heights = {}
    for p in parts:
        heights[p], _, _ = metric(chrome, profile, url, f'only={p}')
        print(f'{p} 高度（1280 寬）：{heights[p]}px')

    print('## 截圖（依序 Read 每一張）')
    pngs = [shot(chrome, profile, url, 'theme=light', os.path.join(a.vdir, 'header-light.png'), '1280,1400')]
    for p in parts:
        short = p.replace('part-', '')
        n = max(1, -(-heights[p] // a.page_height))
        for i in range(n):
            pngs.append(shot(chrome, profile, url, f'theme=dark&only={p}&skip={i * a.page_height}',
                             os.path.join(a.vdir, f'{short}-dark-p{i + 1}.png'), f'1280,{a.page_height}'))
        pngs.append(shot(chrome, profile, url, f'theme=light&only={p}',
                         os.path.join(a.vdir, f'{short}-light-p1.png'), f'1280,{a.page_height}'))
    for png in pngs:
        print(png)
    print(f'看完後：rm -rf {a.vdir}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
