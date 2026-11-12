#!/usr/bin/env python3
"""Rebuild clearly synthetic chart fixtures and illustrative GIF. Dev dependency: Pillow."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evaluation/images'
OUT.mkdir(parents=True, exist_ok=True)

def font(size):
    try: return ImageFont.truetype('DejaVuSans.ttf', size)
    except OSError: return ImageFont.load_default(size=size)


def chart(title, session='OPEN', axis=True, tf='5m', stop=8390):
    im = Image.new('RGB', (960, 560), '#101825')
    d = ImageDraw.Draw(im)
    d.text((24,18), title + ' | CAC40-DEMO | ' + tf, fill='white', font=font(22))
    d.text((24,55), 'Header cursor OHLC: O 8392 H 8399 L 8389 C 8394', fill='#ffce73', font=font(17))
    d.text((24,82), 'Quote panel: 8361 (timestamp/instrument unconfirmed)', fill='#ffce73', font=font(17))
    for y in range(135,446,50):
        d.line((30,y,830,y), fill='#28364a')
        d.text((842,y-9), str(round(8405-(y-135)/7)), fill='#b8c5db',font=font(15))
    prices=[8386,8387,8385,8384,8383,8381,8380,8379,8377,8376,8374,8372]
    def yy(v): return int(135+(8405-v)*7)
    for i,c in enumerate(prices):
        x=65+i*61
        d.line((x,yy(c+5),x,yy(c-5)),fill='#e87980',width=2)
        d.rectangle((x-10,yy(c+1),x+10,yy(c)),fill='#e87980')
    for value,name,color in ((8372,'LATEST 8372','#55d9b4'),(stop,f'SL {stop}','#ef8289')):
        d.line((30,yy(value),827,yy(value)),fill=color,width=2)
        if name.startswith('LATEST') and not axis:
            label=Image.new('RGB',(126,28),'#101825');ld=ImageDraw.Draw(label)
            ld.text((3,2),'LATEST ????',font=font(16),fill=color)
            im.paste(label.filter(ImageFilter.GaussianBlur(5)),(828,yy(value)-14))
        else:
            d.rectangle((827,yy(value)-14,959,yy(value)+14),fill='#101825')
            d.text((828,yy(value)-12),name,fill=color,font=font(16))
    d.text((25,462),f'Session: {session} | 2026-11-12 15:00 +01:00 | 12 CLOSED candles',fill='white',font=font(17))
    d.text((25,490),'Mean high-low = 10 points | volume: unavailable | indicator: none',fill='#bcc8da',font=font(16))
    d.text((25,528),'SYNTHETIC FIXTURE — NOT MARKET DATA OR PERFORMANCE EVIDENCE',fill='#ffce73',font=font(16))
    return im


cases=[]
for ident,session,axis,context,stop,signal in (
    ('index_price_conflict','OPEN',True,True,8390,'NO TRADE'),
    ('missing_context','OPEN',True,False,8390,'NO TRADE'),
    ('closed_session','CLOSED',True,True,8390,'NO TRADE'),
    ('tight_stop','OPEN',True,True,8379,'NO TRADE'),
    ('unreadable_price','OPEN',False,True,8390,'NO TRADE')):
    path=OUT/(ident+'.png')
    chart(ident.replace('_',' '),session,axis,stop=stop).save(path)
    files=[path]
    if context:
        higher=OUT/(ident+'-1h.png');chart('Higher structure: DOWN',session,axis=True,tf='1h',stop=stop).save(higher);files.append(higher)
    cases.append({'id':ident,'synthetic':True,
                  'images':[{'path':str(p.relative_to(ROOT)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
                  'expected':{'latest_price':8372 if axis else None,'signal':signal,'available':3}})
(ROOT/'evaluation/cases.json').write_text(json.dumps({'version':1,'scope':'synthetic development fixtures; not a held-out market benchmark','cases':cases},indent=2)+'\n')
frames=[]
for heading,lines in [
 ('1 / Read the chart', ['Axis latest: 8372','Cursor OHLC: 8394 — historical candle','Panel: 8361 — do not substitute']),
 ('2 / Require context', ['5m only: NO TRADE','Request the same instrument on 1h','No guessed background trend']),
 ('3 / Check the plan', ['1h structure: down; closed trigger confirmed','3/3 available — volume and momentum unavailable','Stop distance 18 >= 1.5 x 10; TP1 gross R:R 1.78']),
 ('4 / Return a short card', ['SHORT candidate on synthetic data','Entry 8372 | SL 8390 | TP1 8340','No orders; unknown costs; no performance claim'])]:
    im=chart('Illustrative workflow')
    d=ImageDraw.Draw(im);d.rectangle((40,125,818,430),fill='#1d2c40',outline='#55d9b4',width=2)
    d.text((64,148),heading,fill='#55d9b4',font=font(28))
    for i,line in enumerate(lines):d.text((64,215+i*57),line,fill='white',font=font(18))
    frames.append(im)
(ROOT/'assets').mkdir(exist_ok=True)
frames[0].save(ROOT/'assets/demo.gif',save_all=True,append_images=frames[1:],duration=2400,loop=0)
print('Generated synthetic fixtures and illustrative demo.gif')
