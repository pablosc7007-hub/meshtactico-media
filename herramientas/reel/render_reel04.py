import cairo, math, sys, os, subprocess, random

W, H, FPS = 1080, 1920, 30
BG = (0.043, 0.059, 0.047)
GREEN = (0.53, 0.89, 0.40)
GREEN_DIM = (0.30, 0.50, 0.24)
WHITE = (0.93, 0.95, 0.93)
GREY = (0.55, 0.60, 0.56)
RED = (0.93, 0.27, 0.22)
AMBER = (1.0, 0.78, 0.15)
SANS = 'Inter Display'
MONO = 'DejaVu Sans Mono'

# ---------------- helpers ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x*x*(3-2*x)
def eout(x): x = clamp(x); return 1-(1-x)**3
def seg(t, a, b): return clamp((t-a)/(b-a))

def font(c, face=SANS, size=60, bold=True):
    c.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)

def text(c, s, x, y, size=60, col=WHITE, face=SANS, bold=True, align='c', alpha=1.0):
    font(c, face, size, bold)
    e = c.text_extents(s)
    if align == 'c': x0 = x - (e.x_advance)/2
    elif align == 'r': x0 = x - e.x_advance
    else: x0 = x
    c.set_source_rgba(*col, alpha); c.move_to(x0, y); c.show_text(s)
    c.new_path()
    return e.x_advance

def rrect(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x+w-r, y+r, r, -math.pi/2, 0); c.arc(x+w-r, y+h-r, r, 0, math.pi/2)
    c.arc(x+r, y+h-r, r, math.pi/2, math.pi); c.arc(x+r, y+r, r, math.pi, 1.5*math.pi)
    c.close_path()

def stroke(c, col, w, alpha=1.0):
    c.set_source_rgba(*col, alpha); c.set_line_width(w); c.stroke()

def fill(c, col, alpha=1.0):
    c.set_source_rgba(*col, alpha); c.fill()

def line(c, x1, y1, x2, y2, col, w, alpha=1.0, dash=None):
    c.move_to(x1, y1); c.line_to(x2, y2)
    if dash: c.set_dash(dash)
    c.set_line_cap(cairo.LINE_CAP_ROUND); stroke(c, col, w, alpha); c.set_dash([])

# ---------------- icons ----------------
def waves(c, cx, cy, t, n=3, col=GREEN, r0=40, step=34, alpha=1.0):
    for k in range(n):
        ph = (t*0.9 - k*0.22) % 1.0
        a = alpha * (0.35 + 0.65*(1-abs(ph-0.5)*2))
        c.arc(cx, cy, r0+k*step, math.radians(-140), math.radians(-40))
        stroke(c, col, 7, a)

def node(c, cx, cy, s=1.0, ant=1.0, screen=GREEN, t=None, wave=False, alpha=1.0):
    w, h = 140*s, 180*s
    rrect(c, cx-w/2, cy-h/2, w, h, 18*s); fill(c, (0.06, 0.08, 0.065), alpha)
    rrect(c, cx-w/2, cy-h/2, w, h, 18*s); stroke(c, WHITE, 5*s, alpha)
    rrect(c, cx-w/2+20*s, cy-h/2+22*s, w-40*s, 62*s, 6*s); fill(c, screen, alpha)
    c.arc(cx, cy+40*s, 9*s, 0, 2*math.pi); fill(c, GREEN, alpha)
    if ant > 0:
        top = cy-h/2 - 110*s*ant
        line(c, cx, cy-h/2, cx, top, WHITE, 5*s, alpha)
        c.arc(cx, top, 9*s, 0, 2*math.pi); fill(c, WHITE, alpha)
        if wave and t is not None:
            waves(c, cx, top+10*s, t, alpha=alpha, r0=40*s, step=34*s)

def phone(c, cx, cy, s=1.0, alpha=1.0):
    w, h = 230*s, 460*s
    rrect(c, cx-w/2, cy-h/2, w, h, 32*s); fill(c, (0.05, 0.07, 0.06), alpha)
    rrect(c, cx-w/2, cy-h/2, w, h, 32*s); stroke(c, WHITE, 5*s, alpha)
    rrect(c, cx-35*s, cy-h/2+16*s, 70*s, 10*s, 5*s); fill(c, GREY, alpha)
    return (cx-w/2+16*s, cy-h/2+40*s, w-32*s, h-60*s)

def pcb(c, cx, cy, s=1.0, alpha=1.0):
    w, h = 170*s, 120*s
    rrect(c, cx-w/2, cy-h/2, w, h, 8*s); fill(c, (0.10, 0.25, 0.12), alpha)
    rrect(c, cx-w/2, cy-h/2, w, h, 8*s); stroke(c, GREEN, 4*s, alpha)
    c.rectangle(cx-50*s, cy-30*s, 50*s, 50*s); fill(c, (0.15, 0.15, 0.15), alpha)
    c.rectangle(cx-50*s, cy-30*s, 50*s, 50*s); stroke(c, GREY, 2*s, alpha)
    c.rectangle(cx+20*s, cy-35*s, 50*s, 32*s); fill(c, (0.3, 0.32, 0.3), alpha)
    for k in range(8):
        c.arc(cx-w/2+16*s+k*20*s, cy+h/2-14*s, 4*s, 0, 2*math.pi); fill(c, AMBER, alpha)
    line(c, cx+60*s, cy-h/2, cx+60*s, cy-h/2-40*s, WHITE, 4*s, alpha)

def warn(c, cx, cy, s=1.0, alpha=1.0):
    c.move_to(cx, cy-60*s); c.line_to(cx+70*s, cy+60*s); c.line_to(cx-70*s, cy+60*s); c.close_path()
    fill(c, AMBER, alpha)
    text(c, '!', cx, cy+45*s, 90*s, (0.08, 0.08, 0.08), alpha=alpha)

def check(c, x, y, s, col=GREEN, alpha=1.0, p=1.0):
    pts = [(x, y+s*0.55), (x+s*0.38, y+s*0.9), (x+s, y+s*0.1)]
    c.move_to(*pts[0])
    if p < 0.5: c.line_to(pts[0][0]+(pts[1][0]-pts[0][0])*p*2, pts[0][1]+(pts[1][1]-pts[0][1])*p*2)
    else:
        c.line_to(*pts[1]); q = (p-0.5)*2
        c.line_to(pts[1][0]+(pts[2][0]-pts[1][0])*q, pts[1][1]+(pts[2][1]-pts[1][1])*q)
    c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND); stroke(c, col, s*0.16, alpha)

def laptop(c, cx, cy, s=1.0, alpha=1.0):
    w, h = 300*s, 190*s
    rrect(c, cx-w/2, cy-h/2, w, h, 12*s); fill(c, (0.05, 0.07, 0.06), alpha)
    rrect(c, cx-w/2, cy-h/2, w, h, 12*s); stroke(c, WHITE, 5*s, alpha)
    c.move_to(cx-w/2-30*s, cy+h/2+6*s); c.line_to(cx+w/2+30*s, cy+h/2+6*s)
    c.line_to(cx+w/2+10*s, cy+h/2+26*s); c.line_to(cx-w/2-10*s, cy+h/2+26*s); c.close_path(); fill(c, WHITE, alpha)
    return (cx-w/2+14*s, cy-h/2+14*s, w-28*s, h-28*s)

# ---------------- background & HUD ----------------
def make_bg():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(surf)
    c.set_source_rgb(*BG); c.paint()
    for x in range(0, W, 60):
        line(c, x, 0, x, H, (0.2, 0.3, 0.22), 1, 0.25)
    for y in range(0, H, 60):
        line(c, 0, y, W, y, (0.2, 0.3, 0.22), 1, 0.25)
    # topo contours from a smooth field via marching squares-lite (iso polylines by sampling)
    import numpy as np
    gs = 12
    ys, xs = np.mgrid[0:H+gs:gs, 0:W+gs:gs].astype(float)
    f = (np.sin(xs/190+np.sin(ys/310)*1.5) + np.sin(ys/240+np.cos(xs/280)*1.4) +
         0.55*np.sin((xs+ys)/160) + 0.35*np.cos((xs-1.6*ys)/210))
    levels = np.arange(-2.6, 2.6, 0.22)
    c.set_line_width(1.4)
    for lv in levels:
        g = f - lv
        for i in range(g.shape[0]-1):
            for j in range(g.shape[1]-1):
                v = [g[i, j], g[i, j+1], g[i+1, j+1], g[i+1, j]]
                p = [(xs[i, j], ys[i, j]), (xs[i, j+1], ys[i, j+1]), (xs[i+1, j+1], ys[i+1, j+1]), (xs[i+1, j], ys[i+1, j])]
                pts = []
                for k in range(4):
                    a, b = v[k], v[(k+1) % 4]
                    if (a > 0) != (b > 0):
                        tt = a/(a-b); pa, pb = p[k], p[(k+1) % 4]
                        pts.append((pa[0]+(pb[0]-pa[0])*tt, pa[1]+(pb[1]-pa[1])*tt))
                if len(pts) >= 2:
                    c.move_to(*pts[0]); c.line_to(*pts[1])
                    if len(pts) == 4: c.move_to(*pts[2]); c.line_to(*pts[3])
        c.set_source_rgba(0.45, 0.55, 0.47, 0.16); c.stroke()
    # vignette
    g = cairo.RadialGradient(W/2, H/2, 300, W/2, H/2, 1250)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.6)
    c.set_source(g); c.paint()
    return surf

HUD_T, HUD_B, HUD_L, HUD_R = 250, 1560, 60, 1020

def hud(c, t, idx, n):
    L = 70
    for (x, y, dx, dy) in [(HUD_L, HUD_T, 1, 1), (HUD_R, HUD_T, -1, 1), (HUD_L, HUD_B, 1, -1), (HUD_R, HUD_B, -1, -1)]:
        c.move_to(x, y+dy*L); c.line_to(x, y); c.line_to(x+dx*L, y); stroke(c, GREEN, 3, 0.9)
    text(c, 'MESHTACTICO // 004', HUD_L+30, HUD_T+50, 26, GREEN, MONO, align='l')
    text(c, 'EU_868', HUD_R-30, HUD_T+50, 26, GREY, MONO, align='r')
    if int(t*2) % 2 == 0:
        c.arc(HUD_R-180, HUD_T+41, 9, 0, 2*math.pi); fill(c, RED)
    secs = 7*3600+15*60+2+int(t)
    z = '%02d:%02d:%02dZ' % (secs//3600, (secs//60) % 60, secs % 60)
    text(c, z, HUD_L+30, HUD_B-25, 26, GREY, MONO, align='l')
    text(c, f'{idx}/{n}', HUD_R-30, HUD_B-25, 26, GREY, MONO, align='r')

def step_chip(c, k, n=4, a=1.0):
    s = f'PASO {k}/{n}'
    font(c, MONO, 30); w = c.text_extents(s).x_advance + 40
    rrect(c, W/2-w/2, 345, w, 54, 27); stroke(c, GREEN, 3, a)
    text(c, s, W/2, 382, 30, GREEN, MONO, alpha=a)

def typed(s, p):
    n = int(round(len(s)*clamp(p))); return s[:n]

def F(t, D, a, b): return eout(seg(t, a*D, b*D))

def padlock(c, cx, cy, s=1.0, col=GREEN, alpha=1.0):
    c.arc(cx, cy-14*s, 16*s, math.pi, 2*math.pi); stroke(c, col, 6*s, alpha)
    line(c, cx-16*s, cy-14*s, cx-16*s, cy, col, 6*s, alpha); line(c, cx+16*s, cy-14*s, cx+16*s, cy, col, 6*s, alpha)
    rrect(c, cx-24*s, cy-4*s, 48*s, 38*s, 6*s); fill(c, col, alpha)

def eye(c, cx, cy, s=1.0, col=RED, alpha=1.0):
    c.save(); c.translate(cx, cy); c.scale(1, 0.55)
    c.arc(0, 0, 26*s, 0, 2*math.pi); c.restore(); stroke(c, col, 4*s, alpha)
    c.arc(cx, cy, 8*s, 0, 2*math.pi); fill(c, col, alpha)

import random as _r
def qr(c, x, y, size, seed=7, alpha=1.0, p=1.0):
    n = 25; m = size/n; rnd = _r.Random(seed)
    c.rectangle(x-8, y-8, size+16, size+16); fill(c, WHITE, alpha)
    cells = [(i, j) for i in range(n) for j in range(n)]
    for (i, j) in cells:
        fin = any(i0 <= i < i0+7 and j0 <= j < j0+7 for i0, j0 in ((0, 0), (0, n-7), (n-7, 0)))
        if fin:
            ii, jj = min(i % 7 if i < 7 else (i-(n-7)), 6), 0
            li = i if i < 7 else i-(n-7); lj = j if j < 7 else j-(n-7)
            on = li in (0, 6) or lj in (0, 6) or (2 <= li <= 4 and 2 <= lj <= 4)
        else:
            on = rnd.random() < 0.48 and rnd.random() < p*1.05
        if on:
            c.rectangle(x+j*m, y+i*m, m+0.5, m+0.5); fill(c, (0.05, 0.07, 0.05), alpha)

def terrain(c, pts, base=1250, col=(0.10, 0.20, 0.12), edge=GREEN_DIM, alpha=1.0):
    c.move_to(pts[0][0], base)
    for p in pts: c.line_to(*p)
    c.line_to(pts[-1][0], base); c.close_path()
    c.set_source_rgba(*col, alpha); c.fill_preserve(); c.set_source_rgba(*edge, alpha); c.set_line_width(4); c.stroke()

def sc_km(c, t, D):
    text(c, 'La distancia', W/2, 470, 74)
    text(c, 'la pone tu red', W/2, 550, 66, GREEN)
    xs = [170, 540, 910]; y = 860
    for k, x in enumerate(xs):
        ak = F(t, D, 0.08+k*0.12, 0.16+k*0.12)
        node(c, x, y, 0.6, alpha=ak)
        text(c, ['ALFA-1', 'ALFA-2', 'ALFA-3'][k], x, y+110, 30, GREEN, MONO, alpha=ak)
    for k in range(2):
        p = eout(seg(t, (0.25+k*0.15)*D, (0.38+k*0.15)*D))
        xa, xb = xs[k]+50, xs[k+1]-50
        if p > 0:
            line(c, xa, y-30, xa+(xb-xa)*p, y-30, GREEN, 6)
        text(c, '5 km', (xa+xb)/2, y-60, 40, WHITE, MONO, alpha=p)
    a = F(t, D, 0.58, 0.68)
    line(c, 170, 1060, 910, 1060, AMBER, 4, a)
    line(c, 170, 1040, 170, 1080, AMBER, 4, a); line(c, 910, 1040, 910, 1080, AMBER, 4, a)
    text(c, '10 km', W/2, 1135, 72, AMBER, MONO, alpha=a)
    text(c, '(ejemplo)', W/2, 1185, 28, GREY, SANS, bold=False, alpha=a)
    a2 = F(t, D, 0.75, 0.85)
    text(c, 'Cada nodo que añades', W/2, 1340, 48, WHITE, alpha=a2)
    text(c, 'estira la red.', W/2, 1410, 52, GREEN, alpha=a2)

def sc0(c, t, D):
    text(c, '¿Hasta dónde', W/2, 560, 80, WHITE, alpha=F(t, D, 0, 0.1))
    sh = typed('LLEGA TU NODO?', seg(t, 0.08*D, 0.35*D))
    text(c, sh + ('_' if int(t*3) % 2 == 0 else ' '), W/2, 690, 100, GREEN)
    node(c, 280, 1000, 0.9, t=t, wave=True)
    a = F(t, D, 0.2, 0.35)
    c.set_dash([16, 12], -t*40); c.move_to(380, 960); c.line_to(820, 960); stroke(c, GREY, 4, a); c.set_dash([])
    text(c, '? km', 600, 930, 48, AMBER, MONO, alpha=a)
    a2 = F(t, D, 0.5, 0.62)
    text(c, 'Más lejos de lo que crees.', W/2, 1300, 48, WHITE, alpha=a2)
    text(c, 'Casi todo depende de dónde lo pones.', W/2, 1370, 52, GREEN, alpha=a2)

def sc1(c, t, D):
    step_chip(c, 1)
    text(c, 'Línea de vista', W/2, 500, 74)
    terrain(c, [(60, 1150), (160, 900), (300, 1000), (540, 1150), (780, 1000), (920, 880), (1020, 1150)])
    node(c, 160, 820, 0.55); node(c, 920, 800, 0.55)
    hill = eout(seg(t, 0.12*D, 0.35*D))
    if t < 0.55*D:
        terrain(c, [(380, 1150), (540, 1150-330*hill), (700, 1150)], col=(0.14, 0.24, 0.14))
        a = F(t, D, 0.3, 0.38)
        line(c, 190, 760, 890, 740, GREEN, 4, 1)
        if hill > 0.9:
            cx_, cy_ = 540, 760
            line(c, cx_-30, cy_-30, cx_+30, cy_+30, RED, 9, a); line(c, cx_+30, cy_-30, cx_-30, cy_+30, RED, 9, a)
            text(c, 'Señal bloqueada', W/2, 1330, 46, RED, alpha=a)
    else:
        a = F(t, D, 0.55, 0.68)
        c.save(); c.translate(540, 750); c.scale(1, 0.18); c.arc(0, 0, 370, 0, 2*math.pi); c.restore()
        c.set_source_rgba(*GREEN, 0.15*a); c.fill_preserve(); c.set_source_rgba(*GREEN, a); c.set_line_width(3); c.stroke()
        line(c, 190, 760, 890, 740, GREEN, 4, 1)
        text(c, 'ZONA DE FRESNEL', 540, 680, 30, GREEN, MONO, alpha=a)
        text(c, 'No basta con verse:', W/2, 1330, 46, WHITE, alpha=a)
        text(c, 'despeja la zona alrededor de la línea.', W/2, 1395, 42, GREEN, alpha=a)

def sc2(c, t, D):
    step_chip(c, 1, 3)
    text(c, 'Altura', W/2, 500, 74)
    terrain(c, [(60, 1000), (250, 1150), (450, 1170), (700, 960), (820, 830), (1020, 1000)], base=1260)
    a1 = F(t, D, 0.05, 0.15)
    node(c, 380, 1100, 0.5, screen=(0.3, 0.32, 0.3), alpha=a1)
    text(c, 'Nodo caro en un valle', 300, 1240, 30, GREY, SANS, bold=False, alpha=a1)
    a2 = F(t, D, 0.4, 0.5)
    node(c, 820, 760, 0.5, t=t, wave=False, alpha=a2)
    text(c, 'Nodo normal en una cota', 800, 920, 30, GREEN, alpha=a2)
    a3 = F(t, D, 0.45, 0.55)
    for k in range(4):
        r = 60+k*55
        c.new_path(); c.arc(820, 700, r, math.radians(150), math.radians(250)); stroke(c, GREEN, 4, a3*(1-k*0.2))
    text(c, 'Subir el nodo unos metros puede', W/2, 1360, 46, WHITE, alpha=F(t, D, 0.18, 0.26))
    text(c, 'multiplicar el alcance.', W/2, 1425, 46, GREEN, alpha=F(t, D, 0.18, 0.26))

def sc3(c, t, D):
    step_chip(c, 2, 3)
    text(c, 'Antena', W/2, 500, 74)
    node(c, 300, 870, 1.1, t=t, wave=True)
    for k, lab in enumerate(['Vertical', '868 MHz', 'Despejada']):
        ak = F(t, D, 0.22+k*0.1, 0.3+k*0.1)
        check(c, 520, 700+k*100, 46, alpha=ak, p=ak)
        text(c, lab, 590, 740+k*100, 46, WHITE, align='l', alpha=ak)
    a = F(t, D, 0.58, 0.66)
    rrect(c, 640, 1060, 300, 260, 30); fill(c, (0.16, 0.14, 0.10), a)
    rrect(c, 640, 1060, 300, 260, 30); stroke(c, GREY, 4, a)
    text(c, 'MOCHILA', 790, 1110, 26, GREY, MONO, alpha=a)
    node(c, 790, 1220, 0.5, screen=(0.3, 0.32, 0.3), alpha=a)
    line(c, 650, 1070, 930, 1310, RED, 8, a); line(c, 930, 1070, 650, 1310, RED, 8, a)
    text(c, 'Fuera del fondo de la mochila', 120, 1400, 40, WHITE, SANS, align='l', alpha=F(t, D, 0.62, 0.72))
    text(c, 'y sin el cuerpo delante: ganas mucho.', 120, 1450, 40, GREEN, SANS, align='l', alpha=F(t, D, 0.62, 0.72))

def bars(c, x, y, n, col, a):
    for k in range(4):
        h = 30+k*22
        c.rectangle(x+k*26, y-h, 18, h); fill(c, col if k < n else (0.25, 0.27, 0.25), a)

def tree(c, x, y, a):
    c.move_to(x, y-120); c.line_to(x+60, y-20); c.line_to(x-60, y-20); c.close_path(); fill(c, GREEN_DIM, a)
    c.rectangle(x-10, y-20, 20, 30); fill(c, (0.4, 0.3, 0.2), a)

def sc4(c, t, D):
    step_chip(c, 3, 3)
    text(c, 'Los obstáculos', W/2, 480, 70)
    text(c, 'no lo cortan todo', W/2, 555, 62, GREEN)
    x1, x2, y = 160, 920, 900
    node(c, x1, y, 0.6, t=t, wave=True); node(c, x2, y, 0.6)
    tree(c, 400, y+80, 1.0); tree(c, 460, y+90, 1.0)
    for i in range(4):
        for j in range(3):
            c.rectangle(620+j*30+(15 if i % 2 else 0), y-60+i*34, 28, 30); fill(c, (0.55, 0.35, 0.25), 0.9)
    p = eout(seg(t, 0.15*D, 0.5*D))
    xe = x1+60+(x2-60-x1-60)*p
    c.set_dash([14, 10], -t*40); c.move_to(x1+60, y-40); c.line_to(xe, y-40); stroke(c, GREEN, 6, 0.9); c.set_dash([])
    if p >= 1: check(c, x2+40, y-120, 60)
    labels = ['Atraviesa arbolado', 'Rodea edificios', 'Aprovecha rebotes']
    for k, lab in enumerate(labels):
        ak = F(t, D, 0.3+k*0.1, 0.38+k*0.1)
        check(c, 180, 1080+k*70, 36, alpha=ak, p=ak)
        text(c, lab, 240, 1112+k*70, 40, WHITE, align='l', alpha=ak)
    a = F(t, D, 0.74, 0.82)
    text(c, 'Con algo en medio, muchas veces', W/2, 1360, 44, WHITE, alpha=a)
    text(c, 'el enlace sale igual.', W/2, 1425, 48, GREEN, alpha=a)

def sc5(c, t, D):
    text(c, 'Y si un monte se pone serio...', W/2, 470, 58)
    terrain(c, [(40, 1150), (200, 1180), (380, 1120), (540, 760), (700, 1120), (880, 1180), (1040, 1150)], base=1260)
    node(c, 190, 1100, 0.5); node(c, 890, 1100, 0.5)
    text(c, 'ALFA-1', 190, 1230, 28, GREEN, MONO); text(c, 'ALFA-2', 890, 1230, 28, GREEN, MONO)
    a = F(t, D, 0.15, 0.25)
    node(c, 540, 690, 0.5, alpha=a)
    text(c, 'COMPAÑERO EN ALTO', 540, 570, 28, YELLOW if False else AMBER, MONO, alpha=a)
    p1 = eout(seg(t, 0.3*D, 0.5*D)); p2 = eout(seg(t, 0.5*D, 0.7*D))
    if p1 > 0: line(c, 220, 1050, 220+(510-220)*p1, 1050+(720-1050)*p1, GREEN, 7)
    if p2 > 0: line(c, 570, 720, 570+(860-570)*p2, 720+(1050-720)*p2, GREEN, 7)
    if p2 >= 1: check(c, 930, 1000, 50)
    a2 = F(t, D, 0.72, 0.82)
    text(c, 'Usa la malla:', W/2, 1360, 46, WHITE, alpha=a2)
    text(c, 'cada compañero suma alcance.', W/2, 1425, 46, GREEN, alpha=a2)

def sc6(c, t, D):
    a0 = F(t, D, 0.0, 0.1)
    text(c, 'Prueba, mide', W/2, 470, 54, WHITE, alpha=a0)
    text(c, 'y mejora la posición.', W/2, 540, 50, GREEN, alpha=F(t, D, 0.12, 0.22))
    node(c, W/2, 830, 0.8, t=t, wave=True)
    a = F(t, D, 0.3, 0.4)
    text(c, 'MESHTACTICO', W/2, 1030, 120, GREEN, alpha=a)
    a2 = F(t, D, 0.45, 0.55)
    text(c, 'Próximo vídeo:', W/2, 1150, 52, WHITE, alpha=a2)
    text(c, 'roles del nodo', W/2, 1215, 52, WHITE, alpha=a2)
    a3 = F(t, D, 0.6, 0.7); pulse = 1+0.03*math.sin(t*6)
    c.save(); c.translate(W/2, 1360); c.scale(pulse, pulse)
    rrect(c, -170, -48, 340, 96, 48); fill(c, GREEN, a3)
    text(c, 'SÍGUEME', 0, 18, 48, (0.05, 0.08, 0.05), alpha=a3); c.restore()

SCENES = [(sc0, 6.3), (sc_km, 12.2), (sc2, 6.9), (sc3, 8.3), (sc4, 13.0), (sc5, 5.1), (sc6, 7.1)]


STARTS = [sum(d for _, d in SCENES[:i]) for i in range(len(SCENES))]
BGS = None

def frame(i, t):
    global BGS
    if BGS is None: BGS = make_bg()
    fn, D = SCENES[i]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(surf)
    c.set_source_surface(BGS); c.paint()
    hud(c, STARTS[i]+t, i+1, len(SCENES))
    a = min(1.0, t/0.3, (D-t)/0.3) if i > 0 else min(1.0, (D-t)/0.3)
    if i == len(SCENES)-1: a = min(1.0, t/0.3)
    c.push_group(); fn(c, t, D); c.pop_group_to_source(); c.paint_with_alpha(clamp(a))
    return surf

def render_scene(i):
    fn, D = SCENES[i]
    n = int(round(D*FPS)); tmp = f'scene{i}.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for k in range(n):
        s = frame(i, k/FPS); p.stdin.write(bytes(s.get_data()))
    p.stdin.close(); rc = p.wait()
    if rc == 0: os.replace(tmp, f'scene{i}.mp4')
    return rc

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        i, t = int(sys.argv[2]), float(sys.argv[3])
        frame(i, t).write_to_png(f'still_{i}_{t}.png')
    elif sys.argv[1] == 'scene':
        sys.exit(render_scene(int(sys.argv[2])))
