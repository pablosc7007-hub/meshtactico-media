import sys, os
import numpy as np
from render import *
import render as R

# ---------- procedural background (no source photo) ----------
def background2(i):
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    base = np.zeros((H, W, 3))
    base[:] = np.array([12, 20, 14], float)
    # soft green glow, position varies per slide
    gx = W*(0.25 + 0.5*((i*37) % 10)/10); gy = H*(0.3 + 0.4*((i*53) % 10)/10)
    glow = np.exp(-(((xx-gx)/650)**2 + ((yy-gy)/750)**2))
    base += glow[..., None]*np.array([18, 42, 20])
    vig = 1 - 0.5*(((xx-W/2)/(W/1.1))**2 + ((yy-H/2)/(H/1.1))**2)
    base *= np.clip(vig, 0.45, 1)[..., None]
    # grid
    grid = ((xx % 60) < 1.2) | ((yy % 60) < 1.2)
    base[grid] = base[grid]*0.85 + np.array([40, 70, 45])*0.15
    t = R.TOPO
    base = base*(1-t[..., None]) + np.array(GREEN)*t[..., None]
    img = Image.fromarray(np.clip(base, 0, 255).astype('uint8'))
    return img.resize((W*S, H*S), Image.LANCZOS)

EPAPER = (205, 210, 198)

def epaper_node(d, cx, cy, sc=1.0):
    w, h = 64*sc, 96*sc
    node(d, cx, cy, sc)
    d.rounded_rectangle([s(cx-w/2+10*sc), s(cy-h/2+12*sc), s(cx+w/2-10*sc), s(cy+2*sc)], radius=s(5*sc), fill=EPAPER)
    for k, f in enumerate((0.6, 0.4, 0.5)):
        y = cy-h/2+22*sc+k*9*sc
        d.line(P((cx-w/2+16*sc, y), (cx-w/2+16*sc+(w-32*sc)*f, y)), fill=(40, 44, 40), width=s(3*sc))

def laptop(d, cx, cy, sc=1.0):
    w, h = 300*sc, 190*sc
    d.rounded_rectangle([s(cx-w/2), s(cy-h/2), s(cx+w/2), s(cy+h/2)], radius=s(12), fill=(12, 18, 14), outline=WHITE, width=s(5))
    d.polygon(P((cx-w/2-30, cy+h/2+6), (cx+w/2+30, cy+h/2+6), (cx+w/2+10, cy+h/2+26), (cx-w/2-10, cy+h/2+26)), fill=WHITE)
    return (cx-w/2+14, cy-h/2+14, w-28, h-28)

# ---------- illustrations ----------
def ill_cover(d, b):
    x0, y0, x1, y1 = b; cx, cy = (x0+x1)/2, (y0+y1)/2+30
    epaper_node(d, cx, cy, 2.2)
    waves(d, cx+0.22*64*2.2, cy-96*2.2/2-44*2.2-6, 50, 3, GREEN, width=8, spread=45, step=34)
    f = font(700, 30)
    for k, n in enumerate(['1', '2', '3', '4', '5']):
        x = x0+70+k*(x1-x0-140)/4; y = y1-10
        d.ellipse([s(x-26), s(y-26), s(x+26), s(y+26)], outline=GREEN, width=s(4), fill=(16, 34, 18))
        tw = d.textlength(n, font=f)/S; d.text((s(x-tw/2), s(y-18)), n, font=f, fill=GREEN)
        if k < 4:
            d.line(P((x+30, y), (x0+70+(k+1)*(x1-x0-140)/4-30, y)), fill=(90, 110, 90), width=s(3))

def ill_buy(d, b):
    x0, y0, x1, y1 = b; cx, cy = (x0+x1)/2, (y0+y1)/2
    f = font(800, 64); t = '868 MHz'; tw = d.textlength(t, font=f)/S
    d.rounded_rectangle([s(cx-tw/2-24), s(cy-120), s(cx+tw/2+24), s(cy-30)], radius=s(12), fill=YELLOW)
    d.text((s(cx-tw/2), s(cy-114)), t, font=f, fill=(10, 10, 10))
    f2 = font(700, 30)
    for k, (t2, ok) in enumerate((('868 MHz: Europa', True), ('915 MHz: América', False))):
        y = cy+10+k*56
        (check if ok else cross)(d, cx-170, y+4, 28, GREEN if ok else RED)
        d.text((s(cx-125), s(y)), t2, font=f2, fill=WHITE if ok else (170, 175, 170))

def ill_techo(d, b):
    x0, y0, x1, y1 = b; cx, cy = (x0+x1)/2, (y0+y1)/2-10
    epaper_node(d, cx, cy, 2.2)
    f = font(800, 50); t = '50-60 €'; t = t.replace('-', '–'); tw = d.textlength(t, font=f)/S
    by = cy+125
    d.rounded_rectangle([s(cx-tw/2-22), s(by), s(cx+tw/2+22), s(by+76)], radius=s(12), fill=YELLOW)
    d.text((s(cx-tw/2), s(by+6)), t, font=f, fill=(10, 10, 10))
    f2 = font(600, 22); t2 = 'AliExpress, tienda oficial LilyGO'; tw2 = d.textlength(t2, font=f2)/S
    d.text((s(cx-tw2/2), s(by+86)), t2, font=f2, fill=(170, 180, 170))

def ill_antenna(d, b):
    x0, y0, x1, y1 = b; cx, cy = (x0+x1)/2, (y0+y1)/2+60
    sc = 2.0; w, h = 64*sc, 96*sc
    # body without antenna
    d.rounded_rectangle([s(cx-w/2), s(cy-h/2), s(cx+w/2), s(cy+h/2)], radius=s(12*sc), fill=(24, 52, 24), outline=GREEN, width=s(4*sc))
    d.rounded_rectangle([s(cx-w/2+10*sc), s(cy-h/2+12*sc), s(cx+w/2-10*sc), s(cy+2*sc)], radius=s(5*sc), fill=EPAPER)
    # SMA connector + antenna floating above
    ax = cx+w*0.22
    d.rectangle([s(ax-9), s(cy-h/2-18), s(ax+9), s(cy-h/2)], fill=(200, 170, 60))
    d.rounded_rectangle([s(ax-8), s(cy-h/2-170), s(ax+8), s(cy-h/2-40)], radius=s(8), fill=(30, 30, 30), outline=WHITE, width=s(3))
    for k in range(3):
        y = cy-h/2-34+k*8
        d.line(P((ax-14, y), (ax+14, y-4)), fill=GREEN, width=s(3))
    # arrow down
    d.line(P((ax+40, cy-h/2-150), (ax+40, cy-h/2-40)), fill=YELLOW, width=s(5))
    arrowhead(d, (ax+40, cy-h/2-150), (ax+40, cy-h/2-30), YELLOW, 20)

def ill_why_update(d, b):
    x0, y0, x1, y1 = b; cx, cy = (x0+x1)/2, (y0+y1)/2
    f = font(800, 48)
    items = [('v. antigua', (150, 155, 150)), ('última estable', GREEN)]
    for k, (t, c) in enumerate(items):
        x = cx-200+k*400
        d.rounded_rectangle([s(x-150), s(cy-60), s(x+150), s(cy+60)], radius=s(16), outline=c, width=s(4), fill=(16, 30, 18))
        tw = d.textlength(t, font=font(700, 36))/S
        d.text((s(x-tw/2), s(cy-22)), t, font=font(700, 36), fill=c)
    d.line(P((cx-40, cy), (cx+30, cy)), fill=YELLOW, width=s(6)); arrowhead(d, (cx-40, cy), (cx+44, cy), YELLOW, 22)

def ill_flash(d, b):
    x0, y0, x1, y1 = b; cy = (y0+y1)/2
    sx, sy, sw, sh = laptop(d, x0+190, cy, 1.0)
    d.rounded_rectangle([s(sx), s(sy), s(sx+sw), s(sy+32)], radius=s(6), fill=(30, 50, 32))
    d.text((s(sx+10), s(sy+4)), 'flasher.meshtastic.org', font=font(600, 22), fill=GREEN)
    # drive icon
    d.rounded_rectangle([s(sx+40), s(sy+60), s(sx+130), s(sy+130)], radius=s(8), outline=WHITE, width=s(3))
    d.text((s(sx+52), s(sy+80)), 'USB', font=font(700, 24), fill=WHITE)
    d.text((s(sx+150), s(sy+70)), '.uf2', font=font(800, 40), fill=YELLOW)
    d.line(P((x0+370, cy), (x1-150, cy)), fill=(170, 175, 170), width=s(6))
    d.text((s((x0+370+x1-150)/2-40), s(cy-40)), 'USB-C', font=font(700, 26), fill=(170, 175, 170))
    epaper_node(d, x1-90, cy+10, 1.25)
    f = font(800, 28)
    d.text((s(x1-150), s(cy+95)), '2× RESET', font=f, fill=YELLOW)

def ill_connect(d, b):
    x0, y0, x1, y1 = b; cy = (y0+y1)/2
    sx0, sy0, sx1, sy1 = phone(d, x0+110, cy, 0.95)
    d.rounded_rectangle([s(sx0), s(sy0+60), s(sx1), s(sy0+120)], radius=s(8), fill=(30, 52, 32))
    d.text((s(sx0+10), s(sy0+74)), 'PIN 123456', font=font(700, 22), fill=WHITE)
    dashed(d, (x0+200, cy-40), (x1-140, cy-40), GREEN, 5, dash=12, gap=9)
    d.text((s((x0+x1)/2-50), s(cy-84)), 'Bluetooth', font=font(700, 28), fill=GREEN)
    d.line(P((x0+200, cy+50), (x1-140, cy+50)), fill=WHITE, width=s(7))
    d.text((s((x0+x1)/2-40), s(cy+62)), 'USB-C', font=font(700, 28), fill=WHITE)
    epaper_node(d, x1-80, cy+20, 1.35)

def ill_region(d, b):
    x0, y0, x1, y1 = b
    f = font(700, 26); fv = font(800, 44)
    rows = [('REGIÓN', 'EU_868', GREEN), ('NOMBRE LARGO', 'ALFA-1', WHITE), ('NOMBRE CORTO', 'A1', WHITE)]
    for k, (lab, val, c) in enumerate(rows):
        y = y0+10+k*112
        d.text((s(x0), s(y)), lab, font=f, fill=(150, 160, 150))
        wbox = (x1-x0) if k < 2 else 280
        d.rounded_rectangle([s(x0), s(y+34), s(x0+wbox), s(y+100)], radius=s(10), outline=WHITE, width=s(3))
        d.text((s(x0+20), s(y+42)), val, font=fv, fill=c)
        if k == 0: check(d, x1-62, y+46, 42)

def ill_firstmsg(d, b):
    x0, y0, x1, y1 = b; cy = (y0+y1)/2
    epaper_node(d, x0+90, cy+20, 1.3)
    others = [(x1-260, cy-90), (x1-90, cy-40), (x1-200, cy+80), (x1-60, cy+120)]
    for (ox, oy) in others:
        node(d, ox, oy, 0.55, dim=True)
    d.rounded_rectangle([s(x0+190), s(cy-120), s(x0+520), s(cy-60)], radius=s(30), fill=(24, 50, 26), outline=GREEN, width=s(3))
    d.text((s(x0+212), s(cy-110)), '¿Alguien a la escucha?', font=font(700, 28), fill=WHITE)
    d.rounded_rectangle([s(x0+300), s(cy+40), s(x0+600), s(cy+100)], radius=s(30), fill=(50, 46, 16), outline=YELLOW, width=s(3))
    d.text((s(x0+322), s(cy+50)), 'Te copio, 5 sobre 5', font=font(700, 28), fill=WHITE)

# ---------- slides ----------
SL = {
 1: dict(t=[('MONTA TU', WHITE), ('PRIMER NODO.', YELLOW)], lay='stack', ill=ill_cover, ih=520,
         body=['5 pasos para pasar de la caja a la red. Lo que en el vídeo cabía en un minuto, aquí con detalle y con los fallos típicos de cada paso.'],
         ban='Guárdalo para cuando te llegue el nodo.'),
 2: dict(t=[('PASO 1 · QUÉ MIRAR', WHITE), ('ANTES DE COMPRAR.', YELLOW)], lay='side', ill=ill_buy,
         body=['*La banda correcta:* en Europa, *868 MHz.* Muchos modelos se venden también en 915 MHz, que es para América. Revisa la versión antes de pagar.',
               '*Todo en uno:* carcasa, batería, pantalla y GPS. Para empezar, mejor que montar piezas sueltas.',
               '*Chip de radio moderno* (SX1262 o similar).'],
         ban='Error típico: comprar la versión de 915 MHz.'),
 3: dict(t=[('EJEMPLO:', WHITE), ('LilyGO T-ECHO.', YELLOW)], lay='side', ill=ill_techo,
         body=['*Pantalla de tinta electrónica:* se lee a pleno sol y casi no gasta.',
               '*GPS integrado:* comparte tu posición sin depender del móvil.',
               '*Batería de 850 mAh* y microcontrolador de bajo consumo (nRF52840).',
               '*Compacto:* viene con carcasa, antena de 868 MHz y cable USB-C.'],
         ban='Unos 50–60 € en la tienda oficial de LilyGO.'),
 4: dict(t=[('PASO 2 · ANTENA', WHITE), ('ANTES DE ENCENDER.', YELLOW)], lay='side', ill=ill_antenna,
         body=['Si el nodo transmite sin antena, la energía no tiene por dónde salir y vuelve al chip de radio. *Puede dañarlo.*',
               'Usa una antena *de 868 MHz:* una de otra banda funciona, pero pierdes alcance.',
               'Enróscala a mano, firme pero sin forzar la rosca.'],
         ban='Primero la antena. Siempre.'),
 5: dict(t=[('PASO 3 · ACTUALIZA', WHITE), ('A LA ÚLTIMA VERSIÓN.', YELLOW)], lay='stack', ill=ill_why_update, ih=170,
         body=['Aunque el nodo venga con Meshtastic de fábrica, puede traer una versión antigua.',
               'Actualizar te da *correcciones de fallos, mejoras de batería y compatibilidad con la app,* que deja de funcionar con firmwares demasiado viejos.',
               'Elige siempre la *última versión estable,* no las alfa: son de pruebas.'],
         ban='Primer encendido = primera actualización.'),
 6: dict(t=[('CÓMO SE ACTUALIZA', WHITE), ('UN T-ECHO.', YELLOW)], lay='steps', ill=ill_flash, ih=250,
         items=['Abre *flasher.meshtastic.org* en Chrome o Edge.',
                'Elige tu modelo y la última versión estable. Descarga el archivo *.uf2.*',
                'Conecta el nodo al ordenador por USB-C, con *cable de datos.*',
                'Pulsa *dos veces seguidas el botón de reset:* aparece como una unidad USB.',
                'Arrastra el *.uf2* a esa unidad. Se reinicia solo.'],
         ban='¿No aparece la unidad? Prueba otro cable.'),
 7: dict(t=[('PASO 4 · CONECTA', WHITE), ('EL MÓVIL.', YELLOW)], lay='stack', ill=ill_connect, ih=330,
         body=['Instala la app *Meshtastic* (Android o iPhone).',
               '*Por Bluetooth:* búscalo desde la app, no desde los ajustes del móvil. El PIN aparece en la pantalla del nodo; si no tiene pantalla, prueba 123456.',
               '*Por cable USB-C:* en Android y en el ordenador. En iPhone, solo Bluetooth.'],
         ban='Más fiable para la primera configuración: el cable.'),
 8: dict(t=[('PASO 5 · REGIÓN', WHITE), ('Y NOMBRE.', YELLOW)], lay='side', ill=ill_region,
         body=['Un nodo nuevo viene con la región *UNSET* y *no transmite* hasta que la eliges. En España: *EU_868.*',
               '*Nombre largo:* hasta 39 caracteres. *Corto:* máximo 4, es el que se ve en el mapa y en los chats.',
               'Usa indicativos de equipo, no tu nombre real.'],
         ban='Sin región no hay radio.'),
 9: dict(t=[('TU PRIMER', WHITE), ('MENSAJE.', YELLOW)], lay='stack', ill=ill_firstmsg, ih=300,
         body=['Escribe en el *canal por defecto* (LongFast). Si hay alguien a la escucha en tu zona, te contestará, y en la lista de nodos irán apareciendo los que te oyen.',
               '*Ojo:* ese canal lo puede leer cualquiera que tenga Meshtastic con la configuración de fábrica. No mandes nada que no publicarías.'],
         ban='Próximo vídeo: tu canal privado.'),
 10: dict(t=[('RESUMEN', WHITE), ('EN 5 PASOS.', YELLOW)], lay='end2',
         items=[(True, '*Compra* la versión de 868 MHz.'),
                (True, '*Antena* antes de encender.'),
                (True, '*Actualiza* a la última versión estable.'),
                (True, '*Conecta* el móvil: Bluetooth o USB-C.'),
                (True, '*Región EU_868* y nombre de equipo.')],
         ban='Guárdalo · Compártelo con tu equipo · Sígueme'),
}

def make2(n):
    cfg = SL[n]
    img = background2(n).convert('RGBA')
    d = ImageDraw.Draw(img)
    frame(d, n)
    ty = title(d, cfg['t'], size=96)
    btop = banner(d, cfg['ban'], H-110)
    top = ty+30; bot = btop-34
    lay = cfg['lay']
    if lay == 'side':
        bw = 600; ibox = (M+bw+20, top, W-M, bot)
        for size in range(42, 28, -1):
            if body_height(d, cfg['body'], size, bw) <= bot-top: break
        hh = body_height(d, cfg['body'], size, bw)
        draw_body(d, cfg['body'], M, top+(bot-top-hh)/2, size, bw)
        ih = min(bot-top, 420); iy = (top+bot)/2-ih/2
        cfg['ill'](d, (ibox[0], iy, ibox[2], iy+ih))
    elif lay == 'stack':
        ih = cfg['ih']; bw = W-2*M
        for size in range(42, 28, -1):
            if body_height(d, cfg['body'], size, bw) + ih + 40 <= bot-top: break
        hh = body_height(d, cfg['body'], size, bw)
        free = bot-top-ih-hh
        iy = top+free*0.35
        cfg['ill'](d, (M, iy, W-M, iy+ih))
        draw_body(d, cfg['body'], M, iy+ih+free*0.3, size, bw)
    elif lay == 'steps':
        ih = cfg['ih']; bw = W-2*M-70
        f = None
        for size in range(40, 28, -1):
            h = sum(len(layout_par(d, it, font(600, size), bw))*size*1.2 + size*0.5 for it in cfg['items'])
            if h + ih + 30 <= bot-top: break
        free = bot-top-ih-h
        iy = top+free*0.3
        cfg['ill'](d, (M, iy, W-M, iy+ih))
        y = iy+ih+free*0.4
        fnum = font(800, size*0.8)
        for k, it in enumerate(cfg['items']):
            d.ellipse([s(M), s(y+2), s(M+size*1.1), s(y+2+size*1.1)], fill=GREEN)
            t = str(k+1); tw = d.textlength(t, font=fnum)/S
            d.text((s(M+size*0.55-tw/2), s(y+size*0.12)), t, font=fnum, fill=(10, 20, 10))
            y = draw_body(d, [it], M+70, y, size, bw, pgap=0.0) + size*0.5
    elif lay == 'end2':
        size = 44; bw = W-2*M
        y = checklist(d, cfg['items'], M, top+10, size, bw, gap=0.45)
        cy = (y+bot)/2
        logo(d, W/2-75, cy-115, 1.36, label=False)
        f = font(800, 84); t = 'MESHTACTICO'; tw = d.textlength(t, font=f)/S
        d.text((s(W/2-tw/2), s(cy-38)), t, font=f, fill=GREEN)
        f2 = font(700, 36); t2 = 'Próximo: tu canal privado'
        tw2 = d.textlength(t2, font=f2)/S; d.text((s(W/2-tw2/2), s(cy+58)), t2, font=f2, fill=WHITE)
    out = img.convert('RGB').resize((W, H), Image.LANCZOS)
    os.makedirs('/home/claude/carrusel/out2', exist_ok=True)
    out.save(f'/home/claude/carrusel/out2/MESHTACTICO_02_{n:02d}.png', optimize=True)

if __name__ == '__main__':
    for n in (map(int, sys.argv[1:]) if len(sys.argv) > 1 else range(1, 11)):
        make2(n); print('ok', n)
