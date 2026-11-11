import sys, os, inspect, random
from slides2 import *
import slides2 as S2

def eye(d, cx, cy, sz, col=RED):
    d.ellipse([s(cx-sz), s(cy-sz*0.55), s(cx+sz), s(cy+sz*0.55)], outline=col, width=s(4))
    d.ellipse([s(cx-sz*0.32), s(cy-sz*0.32), s(cx+sz*0.32), s(cy+sz*0.32)], fill=col)

def qrbox(d, x, y, size, seed=5):
    n = 25; m = size/n; rnd = random.Random(seed)
    d.rectangle([s(x-8), s(y-8), s(x+size+8), s(y+size+8)], fill=WHITE)
    for i in range(n):
        for j in range(n):
            fin = None
            for (i0, j0) in ((0, 0), (0, n-7), (n-7, 0)):
                if i0 <= i < i0+7 and j0 <= j < j0+7:
                    li, lj = i-i0, j-j0
                    fin = li in (0, 6) or lj in (0, 6) or (2 <= li <= 4 and 2 <= lj <= 4)
            on = fin if fin is not None else rnd.random() < 0.48
            if on:
                d.rectangle([s(x+j*m), s(y+i*m), s(x+(j+1)*m), s(y+(i+1)*m)], fill=(12, 18, 12))

def row(d, x, y, w, idx, name, role, priv):
    d.rounded_rectangle([s(x), s(y), s(x+w), s(y+96)], radius=s(14), fill=(26, 52, 28) if priv else (28, 32, 28), outline=GREEN if priv else (140, 150, 140), width=s(3))
    d.text((s(x+24), s(y+16)), idx, font=font(800, 54), fill=GREEN if priv else (150, 160, 150))
    d.text((s(x+80), s(y+10)), name, font=font(800, 44), fill=WHITE)
    d.text((s(x+80), s(y+58)), role, font=font(600, 24), fill=(160, 170, 160))
    if priv: padlock(d, x+w-50, y+44, 50, GREEN)

def ill_cover3(d, b):
    x0, y0, x1, y1 = b; cx = (x0+x1)/2
    padlock(d, cx, y0+150, 190, GREEN)
    row(d, x0+80, y1-220, x1-x0-160, '0', 'EQUIPO', 'PRIMARIO · PRIVADO', True)
    row(d, x0+80, y1-110, x1-x0-160, '1', 'LongFast', 'SECUNDARIO · PÚBLICO', False)

def ill_public(d, b):
    x0, y0, x1, y1 = b; cx, cy = (x0+x1)/2, (y0+y1)/2
    d.rounded_rectangle([s(cx-150), s(cy-60), s(cx+150), s(cy+60)], radius=s(14), outline=RED, width=s(4))
    d.text((s(cx-128), s(cy-52)), 'CLAVE', font=font(600, 24), fill=(170, 175, 170))
    d.text((s(cx-128), s(cy-26)), 'AQ==', font=font(800, 64), fill=RED)
    for k, (dx, dy) in enumerate([(-80, -140), (80, -150), (-90, 130), (85, 140), (0, 190)]):
        eye(d, cx+dx, cy+dy, 26)

def ill_equation(d, b):
    x0, y0, x1, y1 = b; cy = (y0+y1)/2
    items = [('NOMBRE', WHITE), ('+', YELLOW), ('CLAVE', WHITE), ('=', YELLOW), ('CANAL', GREEN)]
    xs = [x0+110, x0+260, x0+410, x0+575, x0+760]
    for (t, c), x in zip(items, xs):
        f = font(800, 44 if len(t) > 1 else 70); tw = d.textlength(t, font=f)/S
        if len(t) > 1:
            d.rounded_rectangle([s(x-tw/2-24), s(cy-50), s(x+tw/2+24), s(cy+50)], radius=s(14), outline=c, width=s(4), fill=(16, 30, 18))
            d.text((s(x-tw/2), s(cy-28)), t, font=f, fill=c)
        else:
            d.text((s(x-tw/2), s(cy-44)), t, font=f, fill=c)

def ill_add(d, b):
    x0, y0, x1, y1 = b; cy = (y0+y1)/2
    sx0, sy0, sx1, sy1 = phone(d, x0+150, cy, 1.15)
    d.text((s(sx0+6), s(sy0+4)), 'Ajustes › Canales', font=font(600, 20), fill=(170, 175, 170))
    d.rounded_rectangle([s(sx0), s(sy0+40), s(sx1), s(sy0+86)], radius=s(8), fill=(30, 40, 32))
    d.text((s(sx0+10), s(sy0+48)), '0  LongFast', font=font(700, 22), fill=WHITE)
    d.rounded_rectangle([s(sx0), s(sy0+100), s(sx1), s(sy0+146)], radius=s(23), fill=GREEN)
    d.text((s(sx0+12), s(sy0+108)), '+ Añadir canal', font=font(800, 24), fill=(10, 20, 10))
    d.line(P((x0+260, cy), (x1-200, cy)), fill=YELLOW, width=s(5)); arrowhead(d, (x0+260, cy), (x1-170, cy), YELLOW, 22)
    d.rounded_rectangle([s(x1-170), s(cy-50), s(x1), s(cy+50)], radius=s(12), outline=WHITE, width=s(3))
    d.text((s(x1-150), s(cy-30)), 'EQUIPO', font=font(800, 44), fill=WHITE)

def ill_key(d, b):
    x0, y0, x1, y1 = b; cx = (x0+x1)/2; cy = (y0+y1)/2
    rnd = random.Random(3); ch = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz0123456789+/'
    d.rounded_rectangle([s(x0), s(cy-110), s(x1), s(cy+30)], radius=s(14), outline=GREEN, width=s(4), fill=(16, 30, 18))
    for k in range(2):
        t = ''.join(rnd.choice(ch) for _ in range(14))
        d.text((s(x0+18), s(cy-96+k*58)), t, font=font(700, 40), fill=GREEN)
    padlock(d, cx, cy-180, 70, GREEN)
    f = font(800, 34); t = '256 bits · AES-256'; tw = d.textlength(t, font=f)/S
    d.text((s(cx-tw/2), s(cy+50)), t, font=f, fill=WHITE)
    d.text((s(cx-60), s(cy+110)), 'AQ==', font=font(800, 46), fill=RED)
    d.line(P((cx-74, cy+138), (cx+70, cy+138)), fill=RED, width=s(6))

def ill_qr(d, b):
    x0, y0, x1, y1 = b; cx = (x0+x1)/2; cy = (y0+y1)/2
    sx0, sy0, sx1, sy1 = phone(d, cx, cy, 1.0)
    qrbox(d, sx0+8, sy0+50, sx1-sx0-16)
    d.text((s(sx0+20), s(sy0+12)), 'EQUIPO', font=font(800, 26), fill=GREEN)

def ill_rows(d, b):
    x0, y0, x1, y1 = b; cy = (y0+y1)/2
    row(d, x0, cy-120, x1-x0, '0', 'EQUIPO', 'PRIMARIO', True)
    row(d, x0, cy, x1-x0, '1', 'LongFast', 'SECUNDARIO', False)
    pin(d, (x0+x1)/2, cy+130, 80, GREEN)

def ill_warn(d, b):
    x0, y0, x1, y1 = b; cx = (x0+x1)/2; cy = (y0+y1)/2
    d.polygon(P((cx, cy-150), (cx+150, cy+110), (cx-150, cy+110)), fill=YELLOW)
    f = font(800, 190); tw = d.textlength('!', font=f)/S
    d.text((s(cx-tw/2), s(cy-120)), '!', font=f, fill=(10, 10, 10))

def ill_rotate(d, b):
    x0, y0, x1, y1 = b; cx = (x0+x1)/2; cy = (y0+y1)/2-30
    r = 120
    d.arc([s(cx-r), s(cy-r), s(cx+r), s(cy+r)], 200, 520, fill=GREEN, width=s(14))
    import math
    ang = math.radians(160)
    ex, ey = cx+r*math.cos(ang), cy+r*math.sin(ang)
    arrowhead(d, (ex+30, ey-40), (ex, ey+6), GREEN, 40)
    padlock(d, cx, cy, 90, YELLOW)
    f = font(800, 34); t = 'CLAVE NUEVA'; tw = d.textlength(t, font=f)/S
    d.text((s(cx-tw/2), s(cy+r+30)), t, font=f, fill=YELLOW)

SL3 = {
 1: dict(t=[('TU CANAL', WHITE), ('PRIVADO.', YELLOW)], lay='stack', ill=ill_cover3, ih=540,
         body=['Lo que no cabía en el reel: cómo montarlo bien, cómo compartirlo sin filtrarlo y los errores que dejan tu canal abierto.'],
         ban='Guárdalo antes de configurar los nodos de tu equipo.'),
 2: dict(t=[('EL PROBLEMA:', WHITE), ('LONGFAST ES PÚBLICO.', YELLOW)], lay='side', ill=ill_public,
         body=['El canal por defecto se llama *LongFast* y usa la clave *AQ==,* la misma en todos los nodos del mundo.',
               'Está así a propósito: para que los nodos nuevos se encuentren.',
               'Pero cualquiera con un nodo de fábrica en tu zona *lee lo que escribes* ahí y puede ver tu posición.'],
         ban='Útil para descubrir la red. Inútil para tu equipo.'),
 3: dict(t=[('CÓMO FUNCIONA', WHITE), ('UN CANAL.', YELLOW)], lay='stack', ill=ill_equation, ih=160,
         body=['Un canal es un *nombre* más una *clave* (PSK). Solo los nodos con el mismo nombre y la misma clave descifran los mensajes.',
               'El resto recibe la señal igual, pero solo ve ruido.',
               'Cada nodo admite *hasta 8 canales:* 1 primario y 7 secundarios, todos en la misma radio.'],
         ban='Mismo nombre + misma clave = mismo canal.'),
 4: dict(t=[('PASO 1 · CREA', WHITE), ('EL CANAL.', YELLOW)], lay='steps', ill=ill_add, ih=350,
         items=['Abre la app Meshtastic y entra en *Ajustes › Canales.*',
                'Pulsa *Añadir canal.*',
                'Ponle un *nombre neutro:* que no revele quiénes sois ni dónde estáis.',
                'Guarda: la configuración se envía al nodo.'],
         ban='Un nombre que no diga nada de vosotros.'),
 5: dict(t=[('PASO 2 · CLAVE', WHITE), ('ALEATORIA.', YELLOW)], lay='side', ill=ill_key,
         body=['Deja que la app *genere la clave:* 256 bits, cifrado AES-256.',
               'No inventes una, no uses las claves "simples" y nunca la de fábrica, *AQ==.*',
               'Una clave corta o conocida es como no tener clave.'],
         ban='Clave generada por la app. Siempre.'),
 6: dict(t=[('PASO 3 · COMPARTE', WHITE), ('SIN FILTRARLA.', YELLOW)], lay='side', ill=ill_qr,
         body=['La app genera un *QR o un enlace* con los canales que elijas. Desactiva los que no quieras compartir.',
               '*El QR lleva la clave dentro:* quien lo escanee, entra en tu canal.',
               'Enséñalo en persona. Nunca en redes, en un grupo grande ni en una foto con la pantalla a la vista.'],
         ban='El QR es la contraseña.'),
 7: dict(t=[('PASO 4 · PRIMARIO', WHITE), ('PRIVADO.', YELLOW)], lay='side', ill=ill_rows,
         body=['Tu nodo envía su *posición y telemetría por el canal primario.*',
               'Si el primario es LongFast, tu posición es pública.',
               'Pon tu canal privado como *primario (canal 0)* y deja LongFast como *secundario* para seguir oyendo la red pública.'],
         ban='Posición por el privado. Charla pública por el secundario.'),
 8: dict(t=[('5 ERRORES', WHITE), ('TÍPICOS.', YELLOW)], lay='check', ill=ill_warn,
         items=[(False, 'Dejar *LongFast como primario* con el GPS activo.'),
                (False, '*Publicar el QR* o enseñarlo en una foto.'),
                (False, 'Copiar la clave a mano y *fallar un carácter.*'),
                (False, '*Nombre o clave distintos* en algún nodo: no se oyen.'),
                (False, 'No cambiar la clave al *perder un nodo.*')],
         after='Revisa los cinco antes de salir.',
         ban='Un solo fallo y el canal deja de ser privado.'),
 9: dict(t=[('¿PIERDES UN NODO?', WHITE), ('CAMBIA LA CLAVE.', YELLOW)], lay='side', ill=ill_rotate,
         body=['La clave *no caduca:* quien tenga un nodo o un QR antiguo puede leer todo lo que se envíe con ella, también lo que mandéis después.',
               'Si se pierde un nodo o alguien deja el equipo: *genera una clave nueva* y vuelve a compartir el QR solo con los que siguen.'],
         ban='Clave nueva = canal limpio.'),
 10: dict(t=[('RESUMEN', WHITE), ('CANAL PRIVADO.', YELLOW)], lay='end2',
         items=[(True, '*Nombre neutro* para el canal.'),
                (True, '*Clave aleatoria* de 256 bits.'),
                (True, '*QR* solo en persona.'),
                (True, '*Privado como primario,* LongFast secundario.'),
                (True, '*Clave nueva* si se pierde un nodo.')],
         ban='Guárdalo · Compártelo con tu equipo · Sígueme'),
}

src = inspect.getsource(S2.make2)
src = src.replace('def make2(n):', 'def make3(n):').replace("SL[n]", "SL3[n]").replace('out2', 'out3').replace('MESHTACTICO_02_', 'MESHTACTICO_03_')
src = src.replace("Próximo: tu canal privado", "Próximo: alcance real")
src = src.replace("    elif lay == 'end2':", """    elif lay == 'check':
        bw = 640
        for size in range(42, 28, -1):
            h = checklist_height(d, cfg['items'], size, bw) + body_height(d, [cfg['after']], size, bw) + 10
            if h <= bot-top: break
        y = top+(bot-top-h)/2
        y = checklist(d, cfg['items'], M, y, size, bw)
        draw_body(d, [cfg['after']], M, y+10, size, bw)
        cfg['ill'](d, (M+bw+20, (top+bot)/2-170, W-M, (top+bot)/2+170))
    elif lay == 'end2':""")
exec(src)

if __name__ == '__main__':
    for n in (map(int, sys.argv[1:]) if len(sys.argv) > 1 else range(1, 11)):
        make3(n); print('ok', n)
