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
    text(c, 'MESHTACTICO // 002', HUD_L+30, HUD_T+50, 26, GREEN, MONO, align='l')
    text(c, 'EU_868', HUD_R-30, HUD_T+50, 26, GREY, MONO, align='r')
    if int(t*2) % 2 == 0:
        c.arc(HUD_R-180, HUD_T+41, 9, 0, 2*math.pi); fill(c, RED)
    secs = 7*3600+15*60+2+int(t)
    z = '%02d:%02d:%02dZ' % (secs//3600, (secs//60) % 60, secs % 60)
    text(c, z, HUD_L+30, HUD_B-25, 26, GREY, MONO, align='l')
    text(c, f'{idx}/{n}', HUD_R-30, HUD_B-25, 26, GREY, MONO, align='r')

def step_chip(c, k, a=1.0):
    s = f'PASO {k}/5'
    font(c, MONO, 30); w = c.text_extents(s).x_advance + 40
    rrect(c, W/2-w/2, 345, w, 54, 27); stroke(c, GREEN, 3, a)
    text(c, s, W/2, 382, 30, GREEN, MONO, alpha=a)

def typed(s, p):
    n = int(round(len(s)*clamp(p)))
    return s[:n]

# ---------------- scenes ----------------
def sc_hook(c, t, D):
    t = t*1.75
    a1 = eout(seg(t, 0.0, 0.5))
    text(c, 'Monta tu', W/2, 560, 66, WHITE, alpha=a1)
    shown = typed('PRIMER NODO', seg(t, 0.4, 1.4))
    text(c, shown + ('_' if int(t*3) % 2 == 0 else ' '), W/2, 700, 112, GREEN)
    a2 = eout(seg(t, 1.5, 2.0))
    text(c, 'en 5 pasos.', W/2, 800, 60, WHITE, alpha=a2)
    ant = eout(seg(t, 2.0, 2.8)); na = eout(seg(t, 1.6, 2.2))
    node(c, W/2, 1250 + (1-na)*60, 1.25, ant=ant, t=t, wave=t > 2.8, alpha=na)

EPAPER = (0.80, 0.82, 0.78)

def epaper_lines(c, cx, cy, s, alpha=1.0):
    for k, w in enumerate((0.55, 0.35, 0.45)):
        line(c, cx-40*s, cy-h_(s)+40*s+k*16*s, cx-40*s+80*s*w, cy-h_(s)+40*s+k*16*s, (0.2, 0.22, 0.2), 4*s, alpha)

def h_(s): return 90*s

def sc_p1(c, t, D):
    step_chip(c, 1)
    text(c, 'Elige el nodo', W/2, 500, 74)
    a = eout(seg(t, 0.2, 0.8))
    node(c, W/2, 890 + (1-a)*40, 1.4, screen=EPAPER, alpha=a)
    epaper_lines(c, W/2, 890 + (1-a)*40 - 13, 1.4, alpha=a)
    a2 = eout(seg(t, 2.0, 2.5))
    text(c, 'Ejemplo: LilyGO T-Echo Plus', W/2, 1080, 46, GREEN, alpha=a2)
    feats = [('Pantalla e-paper', 0), ('GPS', 1), ('Batería 2400 mAh', 2), ('Vibración y zumbador', 3)]
    for label, k in feats:
        ak = eout(seg(t, 4.6+k*1.0, 5.0+k*1.0))
        col, row = k % 2, k // 2
        x = 290 + col*500; y = 1170 + row*100
        rrect(c, x-225, y-40, 450, 76, 38); stroke(c, GREEN, 3, ak)
        text(c, label, x, y+12, 34, WHITE, SANS, bold=False, alpha=ak)
    a3 = eout(seg(t, 9.4, 9.9))
    text(c, 'Todo en uno: sacar de la caja y usar.', W/2, 1430, 40, GREY, SANS, bold=False, alpha=a3)

def sc_p2(c, t, D):
    step_chip(c, 2)
    text(c, 'Antena primero', W/2, 500, 74)
    ant = eout(seg(t, 0.4, 1.6))
    cx, cy = W/2, 850
    node(c, cx, cy, 1.3, ant=ant, t=t, wave=False, screen=EPAPER)
    if ant < 1:
        top = cy-117-143*ant
        for k in range(3):
            yy = top+20+k*14
            line(c, cx-18, yy, cx+18, yy-6, GREEN, 3, 0.8)
    text(c, 'Antena de 868 MHz', W/2, 1080, 38, GREEN, MONO, alpha=eout(seg(t, 1.4, 1.9)))
    a = eout(seg(t, 2.0, 2.5))
    warn(c, 220, 1260, 0.9, alpha=a)
    text(c, 'Nunca lo enciendas', 320, 1245, 50, WHITE, align='l', alpha=a)
    text(c, 'sin antena.', 320, 1305, 50, WHITE, align='l', alpha=a)
    text(c, 'Puedes dañar la radio.', 320, 1365, 40, AMBER, SANS, bold=False, align='l', alpha=a)

def sc_p3(c, t, D):
    step_chip(c, 3)
    text(c, 'Última versión', W/2, 500, 74)
    x, y, w, h = laptop(c, 330, 720, 1.15)
    rrect(c, x, y, w, 34, 6); fill(c, (0.15, 0.2, 0.16))
    text(c, 'flasher.meshtastic.org', x+12, y+24, 19, GREEN, MONO, align='l')
    p = eout(seg(t, 1.0, 5.5))
    bx, by, bw = x+20, y+110, w-40
    rrect(c, bx, by, bw, 26, 13); stroke(c, GREY, 2)
    if p > 0:
        rrect(c, bx+3, by+3, max(20, (bw-6)*p), 20, 10); fill(c, GREEN)
    lab = 'ACTUALIZANDO %d%%' % int(p*100) if p < 1 else '✓ ÚLTIMA VERSIÓN'
    text(c, lab, x+w/2, by-20, 22, GREEN if p >= 1 else WHITE, MONO)
    line(c, 520, 750, 700, 750, GREY, 6)
    for k in range(5):
        q = (t*1.5 + k/5) % 1.0
        c.arc(520+180*q, 750, 6, 0, 2*math.pi); fill(c, GREEN, 0.9 if p < 1 else 0)
    text(c, 'USB-C', 610, 730, 24, GREY, MONO)
    node(c, 800, 750, 0.95, screen=EPAPER)
    steps = [('1', 'Conéctalo al ordenador por USB-C'),
             ('2', 'Abre flasher.meshtastic.org'),
             ('3', 'Elige tu modelo y la última'),
             ('',  'versión estable'),
             ('4', 'En el T-Echo: doble pulsación'),
             ('',  'en reset y arrastra el .uf2')]
    for k, (n, s_) in enumerate(steps):
        ak = eout(seg(t, [0.6,2.2,3.6,3.6,6.0,6.0][k], [1.0,2.6,4.0,4.0,6.4,6.4][k]))
        y0 = 1000 + k*62 + (20 if k >= 2 else 0) + (20 if k >= 4 else 0)
        if n:
            c.arc(150, y0-14, 24, 0, 2*math.pi); fill(c, GREEN, ak)
            text(c, n, 150, y0-3, 30, (0.05, 0.08, 0.05), MONO, alpha=ak)
        text(c, s_, 200, y0, 42, WHITE if n != '2' else GREEN, SANS, bold=(n == '2'), align='l', alpha=ak)

def sc_p4(c, t, D):
    step_chip(c, 4)
    text(c, 'Conecta el móvil', W/2, 500, 74)
    x, y, w, h = phone(c, 300, 870, 1.0)
    text(c, 'Meshtastic', x+w/2, y+40, 26, WHITE)
    rrect(c, x+10, y+70, w-20, 70, 10); fill(c, (0.12, 0.2, 0.13) if t > 1.0 else (0.09, 0.12, 0.1))
    text(c, 'Nodo_a1f3', x+24, y+114, 24, WHITE, MONO, align='l')
    if t > 0.6:
        c.arc(x+w-36, y+105, 8, 0, 2*math.pi); fill(c, GREEN if int(t*4) % 2 else GREEN_DIM)
    if t > 1.8:
        a = eout(seg(t, 1.8, 2.2))
        rrect(c, x+4, y+190, w-8, 200, 14); fill(c, (0.13, 0.16, 0.14), a)
        text(c, 'PIN', x+w/2, y+232, 26, GREY, MONO, alpha=a)
        digits = typed('123456', seg(t, 2.2, 3.2))
        for k in range(6):
            dx = x+22+k*28
            line(c, dx, y+300, dx+20, y+300, GREY, 3, a)
            if k < len(digits): text(c, digits[k], dx+10, y+290, 30, WHITE, MONO, alpha=a)
    if t > 3.3:
        check(c, x+w/2-22, y+322, 44, p=eout(seg(t, 3.3, 3.7)))
    c.set_dash([14, 10], -t*40); c.move_to(430, 820); c.line_to(700, 820); stroke(c, GREEN, 4); c.set_dash([])
    text(c, 'Bluetooth', 565, 800, 26, GREEN, MONO)
    au = eout(seg(t, 4.6, 5.1))
    line(c, 430, 960, 700, 960, WHITE, 7, au)
    text(c, 'Cable USB-C', 565, 1000, 26, WHITE, MONO, alpha=au)
    node(c, 820, 880, 1.0, t=t, wave=True, screen=EPAPER)
    a = eout(seg(t, 2.3, 2.8))
    text(c, 'Bluetooth: PIN en la pantalla del nodo', W/2, 1185, 40, WHITE, SANS, bold=False, alpha=a)
    text(c, '(sin pantalla: 123456)', W/2, 1235, 36, GREY, SANS, bold=False, alpha=a)
    a2 = eout(seg(t, 4.6, 5.1))
    text(c, 'O por cable USB-C (Android u ordenador)', W/2, 1305, 40, WHITE, SANS, bold=False, alpha=a2)
    a3 = eout(seg(t, 5.6, 6.1))
    rrect(c, 190, 1370, 700, 96, 48); fill(c, GREEN, a3)
    text(c, 'Bluetooth o cable: tú eliges', W/2, 1432, 42, (0.05, 0.08, 0.05), alpha=a3)

def sc_p5(c, t, D):
    step_chip(c, 5)
    text(c, 'Región y nombre', W/2, 500, 74)
    a = eout(seg(t, 0.2, 0.6))
    text(c, 'REGIÓN', 160, 620, 30, GREY, MONO, align='l', alpha=a)
    rrect(c, 160, 645, 760, 100, 14); stroke(c, WHITE, 3, a)
    changed = t > 5.2
    val = 'EU_868' if changed else 'UNSET'
    text(c, val, 200, 712, 50, GREEN if changed else RED, MONO, align='l', alpha=a)
    if changed: check(c, 840, 668, 54, p=eout(seg(t, 5.2, 5.6)))
    else:
        c.move_to(860, 685); c.line_to(890, 715); c.line_to(920, 685); stroke(c, WHITE, 4, a)
    if 4.3 < t < 5.2:
        aa = eout(seg(t, 4.3, 4.5))
        for k, o in enumerate(['UNSET', 'EU_433', 'EU_868']):
            rrect(c, 160, 755+k*70, 760, 66, 8); fill(c, (0.12, 0.16, 0.13) if o != 'EU_868' else (0.18, 0.32, 0.18), aa)
            text(c, o, 200, 800+k*70, 34, WHITE, MONO, align='l', alpha=aa)
    a2 = eout(seg(t, 2.5, 3.0)) * (0.0 if 4.25 < t < 5.25 else 1.0)
    text(c, 'Sin región, el nodo no transmite.', W/2, 830, 42, AMBER, SANS, bold=False, alpha=a2)
    a3 = eout(seg(t, 7.6, 8.0))
    text(c, 'NOMBRE', 160, 950, 30, GREY, MONO, align='l', alpha=a3)
    rrect(c, 160, 975, 760, 100, 14); stroke(c, WHITE, 3, a3)
    text(c, typed('ALFA-1', seg(t, 8.8, 9.3)), 200, 1042, 50, WHITE, MONO, align='l', alpha=a3)
    text(c, 'NOMBRE CORTO (máx. 4)', 160, 1150, 30, GREY, MONO, align='l', alpha=a3)
    rrect(c, 160, 1175, 360, 100, 14); stroke(c, WHITE, 3, a3)
    text(c, typed('A1', seg(t, 9.2, 9.5)), 200, 1242, 50, WHITE, MONO, align='l', alpha=a3)
    a4 = eout(seg(t, 9.2, 9.6)) if False else 0.0
    text(c, 'Así te verán en la red.', W/2, 1400, 46, GREEN, alpha=a4)

def sc_test(c, t, D):
    text(c, 'Tu primer mensaje', W/2, 470, 74)
    cx, cy = 300, 900
    others = [(640, 760), (860, 720), (900, 960), (690, 990)]
    for k, (ox, oy) in enumerate(others):
        ao = eout(seg(t, 1.6+k*0.15, 2.0+k*0.15))
        node(c, ox, oy, 0.55, screen=(0.25, 0.32, 0.25), alpha=0.75*ao)
    node(c, cx, cy, 1.0, t=t, wave=t < 2.0, screen=EPAPER)
    text(c, 'ALFA-1', cx, cy+150, 34, GREEN, MONO)
    text(c, 'CANAL POR DEFECTO', W/2, 560, 28, GREY, MONO)
    a = eout(seg(t, 0.4, 0.8))
    rrect(c, 120, 1130 - 20, 470, 76, 38); fill(c, (0.12, 0.2, 0.13), a)
    rrect(c, 120, 1130 - 20, 470, 76, 38); stroke(c, GREEN, 3, a)
    text(c, '¿Alguien a la escucha?', 355, 1160, 32, WHITE, SANS, alpha=a)
    if t > 3.0:
        ar = eout(seg(t, 3.0, 3.4))
        rrect(c, 500, 1220, 470, 76, 38); fill(c, (0.18, 0.18, 0.12), ar)
        rrect(c, 500, 1220, 470, 76, 38); stroke(c, AMBER, 3, ar)
        text(c, 'Te copio, 5 sobre 5', 735, 1270, 32, WHITE, SANS, alpha=ar)
        c.set_dash([10, 10], -t*30); c.move_to(860, 960); c.line_to(cx+80, cy-20); stroke(c, AMBER, 3, 0.6*ar); c.set_dash([])
    a2 = eout(seg(t, 3.4, 3.9))
    text(c, 'Si alguien está a la escucha, te contesta.', W/2, 1380, 40, WHITE, alpha=a2)
    a3 = eout(seg(t, 5.5, 6.0))
    text(c, 'Ojo: ese canal lo lee cualquiera.', W/2, 1450, 40, AMBER, alpha=a3)

def sc_end(c, t, D):
    node(c, W/2, 640, 0.9, t=t, wave=True)
    a = eout(seg(t, 0.2, 0.7))
    text(c, 'MESHTACTICO', W/2, 900, 120, GREEN, alpha=a)
    a2 = eout(seg(t, 0.7, 1.2))
    text(c, 'Próximo vídeo:', W/2, 1030, 52, WHITE, alpha=a2)
    text(c, 'tu canal privado', W/2, 1095, 52, WHITE, alpha=a2)
    text(c, 'que solo lea tu equipo', W/2, 1160, 44, GREY, SANS, bold=False, alpha=a2)
    a3 = eout(seg(t, 1.3, 1.8)); pulse = 1+0.03*math.sin(t*6)
    c.save(); c.translate(W/2, 1300); c.scale(pulse, pulse)
    rrect(c, -170, -48, 340, 96, 48); fill(c, GREEN, a3)
    text(c, 'SÍGUEME', 0, 18, 48, (0.05, 0.08, 0.05), alpha=a3); c.restore()
    a4 = eout(seg(t, 2.0, 2.5))
    text(c, 'Guárdalo para cuando te llegue el nodo', W/2, 1440, 36, GREY, SANS, bold=False, alpha=a4)

SCENES = [(sc_hook, 2.6), (sc_p1, 10.75), (sc_p2, 5.6), (sc_p3, 10.1), (sc_p4, 6.8), (sc_p5, 9.95), (sc_test, 7.6), (sc_end, 5.1)]
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
