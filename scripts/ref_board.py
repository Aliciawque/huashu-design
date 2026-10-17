#!/usr/bin/env python3
"""把参考作品截成一张参考板，让 agent 在动手前真的「看过」它。

写「参考 Stripe Press」几个字，模型做出来的是它对 Stripe Press 的平均印象；
截一张图放在眼前，它才会去量网格、比字号、取颜色。

用法：
  python3 scripts/ref_board.py <网址或图片> [<网址或图片> …] --out refs/board.jpg [--full]

  网址：用无头浏览器打开，截首屏（--full 截整页，最多 4000px 高）
  图片：本地路径或图片网址（.jpg/.png/.webp/.gif），直接放进板子
  每个来源单独存一张（refs/ref-1.jpg …），再拼一张总板。打不开的会列出来，不会中断。

拿到图后用你的看图能力打开总板，把「借的是什么」写成具体规则（网格几栏、标题和正文字号比、
主色占比、图文关系），而不是「参考了它的风格」。
"""

import argparse
import html
import sys
from pathlib import Path

IMG_EXT = ('.jpg', '.jpeg', '.png', '.webp', '.gif')


def shoot(page, src, out, full):
    if Path(src).exists():
        src = Path(src).resolve().as_uri()
    if src.lower().split('?')[0].endswith(IMG_EXT):
        page.set_viewport_size({'width': 1440, 'height': 900})
        r = page.goto(src, wait_until='load', timeout=30000)   # 浏览器直接打开图片，自己包一层 <img>
        if (r and not r.ok) or not page.evaluate('document.images[0] && document.images[0].naturalWidth'):
            raise RuntimeError(f'图片加载失败（HTTP {r.status if r else "?"}）')
        page.locator('img').first.screenshot(path=str(out), type='jpeg', quality=82)
        return
    page.set_viewport_size({'width': 1440, 'height': 900})
    page.goto(src, wait_until='domcontentloaded', timeout=30000)
    try:
        page.wait_for_load_state('networkidle', timeout=8000)
    except Exception:
        pass  # 有长连接的站点等不到 networkidle，首屏通常已经够了
    page.wait_for_timeout(800)
    if full:
        h = min(page.evaluate('document.documentElement.scrollHeight'), 4000)
        page.set_viewport_size({'width': 1440, 'height': h})
        page.wait_for_timeout(400)
    page.screenshot(path=str(out), type='jpeg', quality=82)


def mostly_blank(path):
    """截图几乎是一种颜色：WebGL 站点在无头浏览器里常常是黑的，懒加载的页面是白的。"""
    try:
        from PIL import Image
    except ImportError:
        return False
    im = Image.open(path).convert('L').resize((96, 60))
    px = im.tobytes()
    mean = sum(px) / len(px)
    return sum(abs(v - mean) for v in px) / len(px) < 6


def board(page, shots, out):
    cells = ''.join(
        f'<figure><img src="{p.resolve().as_uri()}"><figcaption>{html.escape(s)}</figcaption></figure>'
        for p, s in shots)
    page.set_viewport_size({'width': 1500, 'height': 600})
    tmp = out.parent / '.board.html'
    tmp.write_text(f'''<!doctype html><meta charset="utf-8"><style>
body{{margin:0;padding:20px;background:#ddd;font:13px/1.3 -apple-system,"PingFang SC","Noto Sans SC",sans-serif}}
.g{{display:grid;grid-template-columns:repeat(2,720px);gap:16px;align-items:start}}
figure{{margin:0}} img{{width:720px;display:block;max-height:1100px;object-fit:cover;object-position:top}}
figcaption{{margin-top:4px;word-break:break-all;color:#333}}</style><div class="g">{cells}</div>''', encoding='utf-8')
    page.goto(tmp.resolve().as_uri(), wait_until='load', timeout=30000)   # 本地图只能从 file:// 页面里引用
    page.screenshot(path=str(out), full_page=True, type='jpeg', quality=80)
    tmp.unlink()


def main(argv):
    ap = argparse.ArgumentParser(description='把参考作品截成参考板')
    ap.add_argument('sources', nargs='+')
    ap.add_argument('--out', default='refs/board.jpg')
    ap.add_argument('--full', action='store_true', help='网页截整页（最多 4000px）')
    a = ap.parse_args(argv)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('需要 Playwright：pip install playwright && python3 -m playwright install chromium')
        print('没有的话：用 WebSearch 的图片结果或请用户发截图，存进 refs/ 后直接用看图能力打开。')
        return 2
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    shots, failed = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for i, src in enumerate(a.sources, 1):
            one = out.parent / f'ref-{i}.jpg'
            try:
                shoot(page, src, one, a.full)
                if mostly_blank(one):
                    failed.append(src)
                    print('✗', src, '：截图几乎是一片纯色（WebGL/3D 站点或懒加载），等于没看到')
                    continue
                shots.append((one, src))
                print('✓', one, '←', src)
            except Exception as e:
                failed.append(src)
                print('✗', src, '：', str(e).splitlines()[0])
        if shots:
            board(page, shots, out)
            print('参考板 →', out)
        browser.close()
    if failed:
        print('\n打不开的来源（常见原因：反爬、要登录、地区限制）。换一个同作品的报道页或图片地址，'
              '或请用户发截图。不要凭印象假装看过。')
    return 0 if shots else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
