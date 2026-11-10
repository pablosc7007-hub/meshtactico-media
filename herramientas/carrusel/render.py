import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

S = 2                       # supersampling
W, H = 1080, 1350
M = 72                      # margin
GREEN = (124, 255, 79)
YELLOW = (255, 212, 0)
WHITE = (255, 255, 255)
RED = (255, 70, 60)
DARK = (14, 26, 16)
F = '/home/claude/carrusel/fonts/BC%d.ttf'
SRC = Image.open('/mnt/user-data/uploads/6b364b79-image.png').convert('RGB')
BOXES = [(1,2,416,429),(422,2,836,429),(841,2,1252,429),(2,433,418,820),(423,433,839,820),
         (844,433,1252,820),(1,825,273,1253),(278,825,624,1253),(629,825,975,1253),(980,825,1252,1253)]

def font(w, size): return ImageFont.truetype(F % w, int(size * S))
def s(v): return int(round(v * S))
def P(*pts): return [(s(x), s(y)) for x, y in pts]

# ---------- background ----------
def topo():
    y, x = np.mgrid[0:H, 0:W] / 1.0
    f = (np.sin(x/170+np.sin(y/260)*1.6) + np.sin(y/210+np.cos(x/300)*1.3) +
         0.6*np.sin((x+y)/140) + 0.4*np.cos((x-1.7*y)/190))
    v = (f*3.2) % 1.0
    d = np.minimum(v, 1-v)
    a = np.clip(1 - d/0.035, 0, 1) * 0.16
    return a

TOPO = topo()

def background(i):
    b = BOXES[i-1]
    p = SRC.crop((b[0]+3, b[1]+3, b[2]-3, b[3]-3))
    sc = max(W/p.width, H/p.height)
    bg = p.resize((round(p.width*sc), round(p.height*sc)), Image.LANCZOS)
    bg = bg.crop(((bg.width-W)//2, (bg.height-H)//2, (bg.width-W)//2+W, (bg.height-H)//2+H))
    bg = bg.filter(ImageFilter.GaussianBlur(22))
    bg = ImageEnhance.Color(bg).enhance(0.8)
    arr = np.asarray(bg).astype(float) * 0.30 + np.array(DARK) * 0.45
    # vignette + darker top/bottom for text
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.45*(((xx-W/2)/(W/1.2))**2 + ((yy-H/2)/(H/1.2))**2)
    arr *= np.clip(vig, 0.4, 1)[..., None]
    arr = arr*(1-TOPO[..., None]) + np.array(GREEN)*TOPO[..., None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'))
    return img.resize((W*S, H*S), Image.LANCZOS)

# ---------- primitives ----------
def dashed(d, a, b, fill, width, dash=14, gap=10):
    (x1, y1), (x2, y2) = a, b
    L = math.hypot(x2-x1, y2-y1); n = int(L // (dash+gap)) + 1
    for k in range(n):
        t0 = k*(dash+gap)/L; t1 = min((k*(dash+gap)+dash)/L, 1)
        if t0 >= 1: break
        d.line(P((x1+(x2-x1)*t0, y1+(y2-y1)*t0), (x1+(x2-x1)*t1, y1+(y2-y1)*t1)), fill=fill, width=s(width))

def arrowhead(d, a, b, fill, size=16):
    (x1, y1), (x2, y2) = a, b
    ang = math.atan2(y2-y1, x2-x1)
    pts = [(x2, y2), (x2-size*math.cos(ang-0.45), y2-size*math.sin(ang-0.45)),
           (x2-size*math.cos(ang+0.45), y2-size*math.sin(ang+0.45))]
    d.polygon(P(*pts), fill=fill)

def check(d, x, y, sz, color=GREEN):
    d.line(P((x, y+sz*0.55), (x+sz*0.38, y+sz*0.9), (x+sz, y+sz*0.1)), fill=color, width=s(sz*0.2), joint='curve')

def cross(d, x, y, sz, color=RED, w=None):
    w = w or sz*0.2
    d.line(P((x, y), (x+sz, y+sz)), fill=color, width=s(w)); d.line(P((x+sz, y), (x, y+sz)), fill=color, width=s(w))

def waves(d, cx, cy, r0, n, color, width=6, spread=50, step=22, start=-90):
    for k in range(n):
        r = r0 + k*step
        d.arc([s(cx-r), s(cy-r), s(cx+r), s(cy+r)], start-spread, start+spread, fill=color, width=s(width))

def node(d, cx, cy, sc=1.0, color=GREEN, dim=False):
    w, h = 64*sc, 96*sc
    body = (24, 52, 24) if not dim else (40, 44, 40)
    out = color if not dim else (110, 120, 110)
    d.line(P((cx+w*0.22, cy-h/2), (cx+w*0.22, cy-h/2-44*sc)), fill=out, width=s(6*sc))
    d.ellipse([s(cx+w*0.22-6*sc), s(cy-h/2-50*sc), s(cx+w*0.22+6*sc), s(cy-h/2-38*sc)], fill=out)
    d.rounded_rectangle([s(cx-w/2), s(cy-h/2), s(cx+w/2), s(cy+h/2)], radius=s(12*sc), fill=body, outline=out, width=s(4*sc))
    scr = (60, 110, 50) if not dim else (60, 64, 60)
    d.rounded_rectangle([s(cx-w/2+10*sc), s(cy-h/2+12*sc), s(cx+w/2-10*sc), s(cy+2*sc)], radius=s(5*sc), fill=scr)
    for k in range(2):
        d.ellipse([s(cx-14*sc+k*20*sc), s(cy+18*sc), s(cx-4*sc+k*20*sc), s(cy+28*sc)], fill=out)

def phone(d, cx, cy, sc=1.0, screen=None):
    w, h = 150*sc, 290*sc
    d.rounded_rectangle([s(cx-w/2), s(cy-h/2), s(cx+w/2), s(cy+h/2)], radius=s(22*sc), fill=(12, 18, 14), outline=WHITE, width=s(5*sc))
    d.rounded_rectangle([s(cx-22*sc), s(cy-h/2+12*sc), s(cx+22*sc), s(cy-h/2+20*sc)], radius=s(4*sc), fill=WHITE)
    return (cx-w/2+12*sc, cy-h/2+32*sc, cx+w/2-12*sc, cy+h/2-16*sc)

def tower(d, cx, base, h, color=WHITE):
    top = base-h
    d.line(P((cx-h*0.22, base), (cx, top), (cx+h*0.22, base)), fill=color, width=s(7), joint='curve')
    for k in range(1, 5):
        y = top + h*k/5; half = h*0.22*k/5
        d.line(P((cx-half, y), (cx+half, y)), fill=color, width=s(5))
        if k < 4:
            y2 = top + h*(k+1)/5; h2 = h*0.22*(k+1)/5
            d.line(P((cx-half, y), (cx+h2, y2)), fill=color, width=s(3))
            d.line(P((cx+half, y), (cx-h2, y2)), fill=color, width=s(3))
    d.ellipse([s(cx-10), s(top-10), s(cx+10), s(top+10)], fill=color)
    return top

def battery(d, x, y, w, h, level=0.85, color=GREEN):
    d.rounded_rectangle([s(x), s(y), s(x+w), s(y+h)], radius=s(10), outline=WHITE, width=s(6))
    d.rounded_rectangle([s(x+w), s(y+h*0.3), s(x+w+12), s(y+h*0.7)], radius=s(3), fill=WHITE)
    d.rounded_rectangle([s(x+10), s(y+10), s(x+10+(w-20)*level), s(y+h-10)], radius=s(5), fill=color)

def chat(d, x, y, sz, color=WHITE):
    d.rounded_rectangle([s(x), s(y), s(x+sz), s(y+sz*0.72)], radius=s(sz*0.14), fill=color)
    d.polygon(P((x+sz*0.18, y+sz*0.7), (x+sz*0.16, y+sz*0.95), (x+sz*0.42, y+sz*0.7)), fill=color)
    for k in range(3):
        d.rounded_rectangle([s(x+sz*0.16), s(y+sz*(0.14+k*0.17)), s(x+sz*(0.84 if k < 2 else 0.6)), s(y+sz*(0.22+k*0.17))], radius=s(3), fill=(14, 26, 16))

def pin(d, cx, y, sz, color=RED):
    r = sz*0.36
    d.ellipse([s(cx-r), s(y), s(cx+r), s(y+2*r)], fill=color)
    d.polygon(P((cx-r*0.86, y+r*1.5), (cx+r*0.86, y+r*1.5), (cx, y+sz)), fill=color)
    d.ellipse([s(cx-r*0.4), s(y+r*0.6), s(cx+r*0.4), s(y+r*1.4)], fill=(14, 26, 16))

def padlock(d, cx, cy, sz, color=WHITE):
    d.arc([s(cx-sz*0.28), s(cy-sz*0.55), s(cx+sz*0.28), s(cy+sz*0.05)], 180, 360, fill=color, width=s(sz*0.1))
    d.line(P((cx-sz*0.28, cy-sz*0.25), (cx-sz*0.28, cy)), fill=color, width=s(sz*0.1))
    d.line(P((cx+sz*0.28, cy-sz*0.25), (cx+sz*0.28, cy)), fill=color, width=s(sz*0.1))
    d.rounded_rectangle([s(cx-sz*0.42), s(cy-sz*0.05), s(cx+sz*0.42), s(cy+sz*0.5)], radius=s(sz*0.08), fill=color)

def mic(d, cx, cy, sz, color=(170, 175, 170)):
    d.rounded_rectangle([s(cx-sz*0.16), s(cy-sz*0.45), s(cx+sz*0.16), s(cy+sz*0.1)], radius=s(sz*0.16), fill=color)
    d.arc([s(cx-sz*0.3), s(cy-sz*0.25), s(cx+sz*0.3), s(cy+sz*0.25)], 0, 180, fill=color, width=s(sz*0.07))
    d.line(P((cx, cy+sz*0.25), (cx, cy+sz*0.42)), fill=color, width=s(sz*0.07))

def cam(d, cx, cy, sz, color=(170, 175, 170)):
    d.rounded_rectangle([s(cx-sz*0.45), s(cy-sz*0.28), s(cx+sz*0.18), s(cy+sz*0.28)], radius=s(sz*0.08), fill=color)
    d.polygon(P((cx+sz*0.2, cy), (cx+sz*0.48, cy-sz*0.22), (cx+sz*0.48, cy+sz*0.22)), fill=color)

def logo(d, x, y, sz=1.0, color=GREEN, label=True, fsize=30):
    w = 110*sz; h = 52*sz
    d.line(P((x, y+h), (x+w*0.27, y), (x+w*0.5, y+h*0.62), (x+w*0.73, y), (x+w, y+h)), fill=color, width=s(15*sz), joint='curve')
    if label:
        f = font(800, fsize); tw = d.textlength('MESHTACTICO', font=f)/S
        d.text((s(x+w/2-tw/2), s(y+h+8*sz)), 'MESHTACTICO', font=f, fill=WHITE)

# ---------- text ----------
def tokens(text):
    """*yellow* markup -> [(word, color)]"""
    out = []; yel = False
    for part in text.split(' '):
        w = part
        st = w.startswith('*'); en = w.endswith('*') and len(w) > 1
        if st: yel = True; w = w[1:]
        if en: w = w[:-1]
        out.append((w, YELLOW if (yel or (st and en)) else WHITE))
        if en: yel = False
    return out

def layout_par(d, text, f, maxw):
    lines = []; cur = []; curw = 0
    sp = d.textlength(' ', font=f)/S
    for w, c in tokens(text):
        ww = d.textlength(w, font=f)/S
        if cur and curw + sp + ww > maxw:
            lines.append(cur); cur = []; curw = 0
        cur.append((w, c, ww)); curw += (sp if len(cur) > 1 else 0) + ww
    if cur: lines.append(cur)
    return lines

def body_height(d, paras, size, maxw, lh=1.24, pgap=0.55):
    f = font(600, size); h = 0
    for i, p in enumerate(paras):
        h += len(layout_par(d, p, f, maxw))*size*lh + (size*pgap if i < len(paras)-1 else 0)
    return h

def draw_body(d, paras, x, y, size, maxw, lh=1.24, pgap=0.55):
    f = font(600, size); sp = d.textlength(' ', font=f)/S
    for p in paras:
        for line in layout_par(d, p, f, maxw):
            cx = x
            for w, c, ww in line:
                d.text((s(cx), s(y)), w, font=f, fill=c); cx += ww + sp
            y += size*lh
        y += size*pgap
    return y

def checklist(d, items, x, y, size, maxw, gap=0.55):
    f = font(600, size)
    for ok, text in items:
        (check if ok else cross)(d, x, y+size*0.18, size*0.72)
        lines = layout_par(d, text, f, maxw-size*1.15)
        for line in lines:
            cx = x+size*1.15
            for w, c, ww in line:
                d.text((s(cx), s(y)), w, font=f, fill=c); cx += ww + d.textlength(' ', font=f)/S
            y += size*1.2
        y += size*gap
    return y

def checklist_height(d, items, size, maxw, gap=0.55):
    f = font(600, size); h = 0
    for ok, text in items:
        h += len(layout_par(d, text, f, maxw-size*1.15))*size*1.2 + size*gap
    return h

def banner(d, text, ybottom, size=40):
    maxw = W-2*M-60
    for sz in range(size, 33, -1):
        f = font(800, sz)
        if d.textlength(text, font=f)/S <= maxw:
            lines = [text]; break
    else:
        sz = size; f = font(800, sz); words = text.split(' ')
        best = None
        for k in range(1, len(words)):
            a, b = ' '.join(words[:k]), ' '.join(words[k:])
            m = max(d.textlength(a, font=f), d.textlength(b, font=f))/S
            if m <= maxw and (best is None or m < best[0]): best = (m, [a, b])
        lines = best[1]
    h = len(lines)*sz*1.12 + 34
    y0 = ybottom-h
    d.rounded_rectangle([s(M), s(y0), s(W-M), s(ybottom)], radius=s(10), fill=YELLOW)
    y = y0+14
    for t in lines:
        tw = d.textlength(t, font=f)/S
        d.text((s(W/2-tw/2), s(y)), t, font=f, fill=(10, 10, 10)); y += sz*1.12
    return y0

def frame(d, n):
    c = 38; L = 46
    for (x, y, dx, dy) in [(c, c, 1, 1), (W-c, c, -1, 1), (c, H-c, 1, -1), (W-c, H-c, -1, -1)]:
        d.line(P((x, y+dy*L), (x, y), (x+dx*L, y)), fill=GREEN, width=s(4))
    logo(d, M, 72, 0.62, fsize=26)
    f = font(700, 30); t = f'{n:02d} / 10'; tw = d.textlength(t, font=f)/S
    d.text((s(W-M-tw), s(78)), t, font=f, fill=GREEN)
    if n < 10:
        f2 = font(700, 26); t2 = 'DESLIZA'; tw2 = d.textlength(t2, font=f2)/S
        d.text((s(W-M-tw2-58), s(H-80)), t2, font=f2, fill=GREEN)
        for k in range(3):
            x0 = W-M-46+k*16
            d.line(P((x0, H-74), (x0+10, H-64), (x0, H-54)), fill=GREEN, width=s(4))

def title(d, lines, y=170, size=104):
    f = font(800, size)
    for t, c in lines:
        # shrink if too wide
        sz = size
        while d.textlength(t, font=font(800, sz))/S > W-2*M and sz > 60: sz -= 4
        d.text((s(M), s(y)), t, font=font(800, sz), fill=c); y += sz*1.0
    return y
