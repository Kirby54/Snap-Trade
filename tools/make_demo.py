#!/usr/bin/env python3
"""Build the readable README illustration. Dev dependency: Pillow, no market data."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BG = '#f3f6fa'
INK = '#17283f'
MUTED = '#54647a'
BORDER = '#dce4ed'
GREEN = '#087965'
AMBER = '#8a4b08'
RED = '#bc4257'


def font(size, bold=False):
    name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default(size=size)


def render(step=None):
    im = Image.new('RGB', (1200, 760), BG)
    d = ImageDraw.Draw(im)

    def text(x, y, value, size=26, color=INK, bold=False):
        d.text((x, y), value, font=font(size, bold), fill=color, anchor='lt')

    def box(xy, fill='white', outline=BORDER, radius=20, width=2):
        d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

    text(44, 32, 'SNAP & TRADE', 24, GREEN, True)
    box((880, 25, 1156, 67), '#fff0d5', '#fff0d5', radius=12)
    text(900, 35, 'ILLUSTRATIVE EXAMPLE', 19, AMBER, True)
    headings = {1: '1. Read both timeframes.', 2: '2. Check the numbers.', 3: '3. Wait for confirmation.'}
    text(44, 89, headings.get(step, 'A clear plan. At a glance.'), 44, bold=True)
    text(44, 146, 'Execution + context. Checked levels. One concise decision.', 26, MUTED)

    # The chart and decision are separate panels. No overlay or scrolling text.
    box((44, 205, 595, 640), outline=GREEN if step == 1 else BORDER, width=3)
    text(68, 231, 'CAC40-DEMO', 28, bold=True)
    box((487, 224, 570, 268), '#e9f1f8', '#e9f1f8', radius=10)
    text(505, 234, '5m', 25, MUTED, True)

    def yy(price):
        return round(300 + (8390 - price) * 10)

    for value in (8390, 8380, 8370):
        y = yy(value)
        d.line((68, y, 472, y), fill=BORDER, width=2)
        text(494, y-12, str(value), 25, MUTED)
    prices = [8386, 8387, 8385, 8384, 8383, 8381, 8380, 8379, 8377, 8376, 8374, 8372]
    for i, close in enumerate(prices):
        x = 82 + i*33
        d.line((x, yy(close+2), x, yy(close-2)), fill=RED, width=3)
        d.rectangle((x-7, yy(close+1), x+7, yy(close)), fill=RED)
    y = yy(8372)
    for x in range(68, 475, 12):
        d.line((x, y, min(x+6, 476), y), fill=GREEN, width=2)
    box((480, y-21, 577, y+22), GREEN, GREEN, radius=8)
    text(491, y-11, '8372', 28, 'white', True)
    text(68, 551, 'Latest price: 8372', 27, GREEN, True)
    text(68, 592, '1h context: downtrend', 25, MUTED)

    box((621, 205, 1156, 640), outline=GREEN if step in (2, 3) else BORDER, width=3)
    box((646, 228, 1131, 300), '#fff0d5', '#fff0d5', radius=14)
    text(669, 247, 'NO TRADE YET', 34, AMBER, True)
    text(649, 325, 'Conditional SHORT scenario', 27, bold=True)
    text(649, 366, '2/3 available · trigger pending', 25, MUTED)
    d.line((649, 412, 1128, 412), fill=BORDER, width=2)
    for x, label, value, color in ((649, 'ENTRY', '8372', INK), (816, 'STOP', '8390', RED), (986, 'TP1', '8340', GREEN)):
        text(x, 439, label, 23, MUTED, True)
        text(x, 477, value, 38, color, True)
    d.line((649, 537, 1128, 537), fill=BORDER, width=2)
    text(649, 565, 'Wait for a closed rejection.', 25, INK, True)
    text(649, 602, 'Refresh both charts before entry.', 23, MUTED)

    text(46, 680, 'Synthetic data · no orders · no performance claim', 25, MUTED)
    text(46, 722, 'Ask “explain” for the detailed review.', 23, MUTED)
    return im


def main():
    out = ROOT / 'assets'
    out.mkdir(exist_ok=True)
    render().save(out / 'demo.png', optimize=True)
    frames = [render(step) for step in (1, 2, 3)]
    frames[0].save(out / 'demo.gif', save_all=True, append_images=frames[1:],
                   duration=[3500, 3500, 5000], loop=0, optimize=True)
    print('Generated static README illustration and three-step GIF')


if __name__ == '__main__':
    main()
