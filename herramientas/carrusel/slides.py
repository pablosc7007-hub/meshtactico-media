import sys
from render import *

# ---------- illustrations (box = x0,y0,x1,y1 in 1x) ----------
def ill_phone_nosignal(d, b):
    cx, cy = (b[0]+b[2])/2, (b[1]+b[3])/2
    sx0, sy0, sx1, sy1 = phone(d, cx, cy, 1.05)
    # signal bars crossed
    bx, by = cx-46, cy-40
    for k in range(4):
        d.rounded_rectangle([s(bx+k*24), s(by+60-k*18), s(bx+k*24+16), s(by+60)], radius=s(3), fill=(90, 100, 90))
    d.line(P((bx-12, by+70), (bx+100, by-30)), fill=RED, width=s(9))
    f = font(700, 30); t = 'Sin servicio'; tw = d.textlength(t, font=f)/S
    d.text((s(cx-tw/2), s(cy+50)), t, font=f, fill=WHITE)

def ill_tower(d, b):
    cx = (b[0]+b[2])/2; base = b[3]-10
    top = tower(d, cx, base, (b[3]-b[1])*0.7)
    waves(d, cx, top, 40, 3, RED, width=8, spread=40, step=30, start=-150)
    waves(d, cx, top, 40, 3, RED, width=8, spread=40, step=30, start=-30)

def ill_lora(d, b):
    x0, y0, x1, y1 = b; cy = y0+(y1-y0)*0.38
    # chirp: frequency sweep
    pts = []; n = 600
    for k in range(n):
        t = k/n; x = x0+10+(x1-x0-20)*t
        ph = 2*math.pi*(3*t + 9*(t*t))
        pts.append((x, cy + 46*math.sin(ph)))
    d.line(P(*pts), fill=GREEN, width=s(5), joint='curve')
    f = font(700, 26); d.text((s(x0+10), s(cy+64)), 'BARRIDO DE FRECUENCIA (CHIRP)', font=f, fill=GREEN)
    battery(d, x1-190, y1-96, 160, 80, 0.85)

def ill_868(d, b):
    x0, y0, x1, y1 = b; cx = (x0+x1)/2
    f = font(800, 74); t = '868 MHz'; tw = d.textlength(t, font=f)/S
    d.rounded_rectangle([s(cx-tw/2-26), s(y0), s(cx+tw/2+26), s(y0+104)], radius=s(14), fill=YELLOW)
    d.text((s(cx-tw/2), s(y0+8)), t, font=f, fill=(10, 10, 10))
    # spectrum
    base = y1-30; xs = x0+10; xe = x1-10
    d.line(P((xs, base), (xe, base)), fill=WHITE, width=s(4))
    import random; random.seed(4)
    n = 26
    for k in range(n):
        x = xs+(xe-xs)*(k+0.5)/n
        hot = 10 <= k <= 15
        h = (120+random.random()*40) if hot else (20+random.random()*30)
        d.rounded_rectangle([s(x-5), s(base-h), s(x+5), s(base)], radius=s(3), fill=GREEN if hot else (90, 100, 90))
    ft = font(700, 24); d.text((s(xs+(xe-xs)*0.36), s(base+6)), 'BANDA LIBRE', font=ft, fill=GREEN)

MESH = [(0.15, 0.25), (0.5, 0.12), (0.85, 0.3), (0.3, 0.62), (0.72, 0.68), (0.5, 0.92)]
EDGES = [(0, 1), (1, 2), (0, 3), (1, 3), (1, 4), (2, 4), (3, 4), (3, 5), (4, 5)]

def place(b, p):
    return (b[0]+(b[2]-b[0])*p[0], b[1]+50+(b[3]-b[1]-110)*p[1])

def ill_mesh(d, b, dead=None, route=None, sc=0.75):
    pts = [place(b, p) for p in MESH]
    for i, j in EDGES:
        col = (150, 160, 150)
        if dead in (i, j): col = (80, 85, 80)
        dashed(d, pts[i], pts[j], col, 4)
    if route:
        for i, j in zip(route, route[1:]):
            d.line(P(pts[i], pts[j]), fill=GREEN, width=s(9))
    for k, (x, y) in enumerate(pts):
        node(d, x, y+20*sc, sc, dim=(k == dead))
    if dead is not None:
        x, y = pts[dead]; cross(d, x-34, y-14, 68, RED, w=12)

def ill_mesh5(d, b):
    ill_mesh(d, b, sc=0.95)

def ill_phone_node(d, b):
    x0, y0, x1, y1 = b; cy = (y0+y1)/2
    sx0, sy0, sx1, sy1 = phone(d, x0+95, cy, 0.85)
    d.rounded_rectangle([s(sx0), s(sy0), s(sx1), s(sy1)], radius=s(8), fill=(30, 52, 32))
    for k in range(5):
        yy = sy0+22+k*40
        pts = [(sx0+4+(sx1-sx0-8)*t/40, yy+8*math.sin(t/40*6.28+k)) for t in range(41)]
        d.line(P(*pts), fill=(70, 110, 70), width=s(2))
    for (px, py) in ((0.3, 0.3), (0.7, 0.45), (0.45, 0.7)):
        X = sx0+(sx1-sx0)*px; Y = sy0+(sy1-sy0)*py
        d.ellipse([s(X-8), s(Y-8), s(X+8), s(Y+8)], fill=GREEN, outline=WHITE, width=s(2))
    node(d, x1-80, cy+20, 1.35)
    dashed(d, (x0+175, cy), (x1-135, cy), GREEN, 5, dash=12, gap=9)
    f = font(700, 26); t = 'Bluetooth'; tw = d.textlength(t, font=f)/S
    d.text((s((x0+175+x1-135)/2-tw/2), s(cy+12)), t, font=f, fill=GREEN)
    fl = font(700, 26)
    for t, x, yy in (('MÓVIL', x0+95, cy+132), ('NODO LoRa', x1-80, cy+96)):
        tw = d.textlength(t, font=fl)/S; d.text((s(x-tw/2), s(yy)), t, font=fl, fill=WHITE)

def ill_path(d, b):
    x0, y0, x1, y1 = b
    names = ['ALFA-1', 'ALFA-2', 'BRAVO-1', 'PC']
    n = 4; cy = y0+(y1-y0)*0.48
    xs = [x0+70+(x1-x0-140)*k/(n-1) for k in range(n)]
    ys = [cy+30, cy-30, cy+30, cy-30]
    for k in range(n-1):
        a = (xs[k]+40, ys[k]); bb = (xs[k+1]-48, ys[k+1])
        d.line(P(a, bb), fill=GREEN, width=s(8)); arrowhead(d, a, bb, GREEN, 26)
        mx, my = (a[0]+bb[0])/2, (a[1]+bb[1])/2
        d.ellipse([s(mx-22), s(my-62), s(mx+22), s(my-18)], fill=YELLOW)
        f = font(800, 30); t = str(k+1); tw = d.textlength(t, font=f)/S
        d.text((s(mx-tw/2), s(my-60)), t, font=f, fill=(10, 10, 10))
    for k in range(n):
        if k < n-1:
            node(d, xs[k], ys[k], 0.8)
        else:
            d.rounded_rectangle([s(xs[k]-42), s(ys[k]-42), s(xs[k]+42), s(ys[k]+42)], radius=s(8), outline=WHITE, width=s(6), fill=(20, 40, 20))
            check(d, xs[k]-22, ys[k]-20, 44)
        f = font(800, 30); tw = d.textlength(names[k], font=f)/S
        d.text((s(xs[k]-tw/2), s(ys[k]+62)), names[k], font=f, fill=YELLOW)
    fs = font(700, 26); t = 'SALTO 1 · SALTO 2 · SALTO 3'
    tw = d.textlength(t, font=fs)/S; d.text((s((x0+x1)/2-tw/2), s(y1-34)), t, font=fs, fill=GREEN)

def ill_reroute(d, b):
    ill_mesh(d, b, dead=1, route=[0, 3, 4, 2], sc=0.9)

def ill_icons9(d, b):
    x0, y0, x1, y1 = b; cx = (x0+x1)/2
    chat(d, cx-110, y0+10, 90)
    pin(d, cx+60, y0+4, 100)
    battery(d, cx-100, y0+150, 150, 70, 0.9)
    mic(d, cx-70, y0+310, 110); cross(d, cx-110, y0+262, 80, RED, w=10)
    cam(d, cx+70, y0+310, 110); cross(d, cx+30, y0+262, 80, RED, w=10)

# ---------- slides ----------
SLIDES = {
 1: dict(t=[('SIN COBERTURA.', WHITE), ('EQUIPO DISPERSO.', YELLOW)], lay='side', ill=ill_phone_nosignal,
         body=['Estás en el monte, el equipo está repartido y el móvil marca *«sin servicio».*',
               '¿Cómo sabes dónde está cada uno? ¿Cómo avisas de un cambio de plan?',
               'En estas 10 fotos te explico cómo funciona una red de comunicaciones que no depende de antenas, de internet ni de ningún operador.'],
         ban='Guárdalo: es la base de todo lo que vendrá después.'),
 2: dict(t=[('EL MÓVIL DEPENDE', WHITE), ('DE UNA ANTENA.', YELLOW)], lay='side', ill=ill_tower,
         body=['El móvil no habla con otro móvil: los dos hablan con *un repetidor.* Si no hay repetidor (en un valle, detrás de una cresta, en un interior o con la red saturada), no hay comunicación.',
               'El walkie sí habla directo, pero solo transmite voz: todos escuchan todo, no queda registro y nadie sabe dónde está cada uno.'],
         ban='Hace falta algo intermedio.'),
 3: dict(t=[('LoRa: LARGO ALCANCE,', WHITE), ('POCA ENERGÍA.', YELLOW)], lay='stack', ill=ill_lora, ih=250,
         body=['LoRa es una forma de modular la señal de radio pensada para enviar poca información *muy lejos.*',
               'Su truco es repartir la señal en «barridos» de frecuencia, lo que permite recibirla incluso cuando apenas se distingue del ruido.',
               'A cambio, es lenta: en Meshtastic va de *0,3 a 22 kbps* según el ajuste de radio, y de fábrica trabaja a unos *1 kbps.* No sirve para voz ni vídeo, pero sobra para texto y posiciones.'],
         ban='Gasta tan poco que una batería pequeña dura días.'),
 4: dict(t=[('868 MHz:', WHITE), ('BANDA LIBRE, SIN LICENCIA.', YELLOW)], lay='stack', ill=ill_868, ih=280,
         body=['En Europa, LoRa funciona en la banda de *868 MHz,* de uso *libre.* No necesitas licencia de radioaficionado, ni contrato, ni pedir permiso a nadie.',
               'Solo hay dos reglas: una potencia máxima legal y un límite de tiempo de emisión, para que nadie acapare la banda.'],
         ban='Por eso los mensajes son cortos y la red no se satura.'),
 5: dict(t=[('MESHTASTIC =', WHITE), ('LoRa + RED DE MALLA.', YELLOW)], lay='stack', ill=ill_mesh5, ih=380,
         body=['LoRa por sí solo une dos radios; Meshtastic lo convierte en una red. Es un proyecto libre y de código abierto que funciona sobre nodos LoRa baratos.',
               'No hay servidor ni centro de la red: *todos los nodos son iguales,* y cada uno puede enviar, recibir y retransmitir.'],
         ban='Si mañana desaparece internet, la red sigue funcionando igual.'),
 6: dict(t=[('CADA COMPONENTE:', WHITE), ('UN MÓVIL + UN NODO.', YELLOW)], lay='stack', ill=ill_phone_node, ih=380,
         body=['El nodo es la radio: un aparato pequeño que llevas en el chaleco o en la mochila, con antena.',
               'El móvil se conecta a él por *Bluetooth* y hace de pantalla: escribes, lees y ves el mapa. Si te desconectas, el nodo te guarda los mensajes.'],
         ban='Si apagas el móvil, el nodo sigue retransmitiendo para los demás.'),
 7: dict(t=[('SALTO', WHITE), ('A SALTO.', YELLOW)], lay='stack', ill=ill_path, ih=330,
         body=['Cuando envías un mensaje, todos los nodos que lo oyen lo retransmiten, y repiten lo mismo los que oyen a esos.',
               'Para avanzar lo máximo en cada salto, retransmite antes *el nodo más lejano,* y los demás se callan para no saturar la red.',
               'Por defecto, un mensaje da hasta *3 saltos.*'],
         ban='Cada salto suma alcance.'),
 8: dict(t=[('SI UN NODO CAE,', WHITE), ('LA RED SIGUE.', YELLOW)], lay='stack', ill=ill_reroute, ih=400,
         body=['No hay un camino fijo. Si un compañero se queda sin batería, baja a un barranco o se aleja, el mensaje busca otro camino entre los nodos que quedan.',
               'Cuantos más nodos, *más caminos, más alcance y más resistencia.*'],
         ban='No dependes de un único punto que, si falla, deja a todos sin comunicación.'),
 9: dict(t=[('QUÉ VIAJA', WHITE), ('Y QUÉ NO.', YELLOW)], lay='check', ill=ill_icons9,
         items=[(True, 'Mensajes de texto cortos (unos 200 caracteres), al grupo o a una persona, con confirmación de entrega.'),
                (True, 'Posiciones GPS de cada nodo, enviadas cada cierto tiempo.'),
                (True, 'Alertas y telemetría: batería, estado del nodo.'),
                (False, 'Ni voz ni vídeo.')],
         after='No es un teléfono: es un sistema ligero de *mando y control.*',
         ban='Lo justo para saber dónde está cada uno y qué hay que hacer.'),
 10: dict(t=[('POR QUÉ', WHITE), ('EN EL TERRENO.', YELLOW)], lay='end',
         items=[(True, '*Sin infraestructura:* funciona donde no llega nada.'),
                (True, '*Días de batería:* consumo mínimo.'),
                (True, '*Canales cifrados:* solo lee quien tiene la clave.'),
                (True, '*Todo el equipo* en el mapa de ATAK.')],
         ban='Comunicación táctica, sin depender de nadie.'),
}

def make(n):
    cfg = SLIDES[n]
    img = background(n).convert('RGBA')
    d = ImageDraw.Draw(img)
    frame(d, n)
    ty = title(d, cfg['t'])
    bottom = H-110
    btop = banner(d, cfg['ban'], bottom)
    top = ty+34; avail_bot = btop-36
    lay = cfg['lay']
    if lay == 'side':
        bw = 590; ibox = (M+bw+30, top, W-M, avail_bot)
        for size in range(44, 30, -1):
            if body_height(d, cfg['body'], size, bw) <= avail_bot-top: break
        hh = body_height(d, cfg['body'], size, bw)
        draw_body(d, cfg['body'], M, top+(avail_bot-top-hh)/2, size, bw)
        ih = min(ibox[3]-ibox[1], 420); iy = (ibox[1]+ibox[3])/2-ih/2
        cfg['ill'](d, (ibox[0], iy, ibox[2], iy+ih))
    elif lay == 'stack':
        ih = cfg['ih']; bw = W-2*M
        for size in range(44, 30, -1):
            if body_height(d, cfg['body'], size, bw) + ih + 40 <= avail_bot-top: break
        hh = body_height(d, cfg['body'], size, bw)
        free = avail_bot-top-ih-hh
        iy = top+free*0.35
        cfg['ill'](d, (M, iy, W-M, iy+ih))
        draw_body(d, cfg['body'], M, iy+ih+free*0.3, size, bw)
    elif lay == 'check':
        bw = 640; ibox = (M+bw+20, top, W-M, avail_bot)
        for size in range(42, 28, -1):
            h = checklist_height(d, cfg['items'], size, bw) + body_height(d, [cfg['after']], size, bw) + 10
            if h <= avail_bot-top: break
        y = top+(avail_bot-top-h)/2
        y = checklist(d, cfg['items'], M, y, size, bw)
        draw_body(d, [cfg['after']], M, y+10, size, bw)
        cfg['ill'](d, (ibox[0], (top+avail_bot)/2-210, ibox[2], (top+avail_bot)/2+210))
    elif lay == 'end':
        bw = W-2*M; size = 42
        y = checklist(d, cfg['items'], M, top+10, size, bw, gap=0.4)
        # end card
        cy = (y+avail_bot)/2
        logo(d, W/2-75, cy-120, 1.36, label=False)
        f = font(800, 84); t = 'MESHTACTICO'; tw = d.textlength(t, font=f)/S
        d.text((s(W/2-tw/2), s(cy-40)), t, font=f, fill=GREEN)
        f2 = font(700, 36); t2 = 'Próximo: monta tu primer nodo de campaña'
        tw2 = d.textlength(t2, font=f2)/S; d.text((s(W/2-tw2/2), s(cy+58)), t2, font=f2, fill=WHITE)
        f3 = font(700, 32); t3 = 'Guárdalo  ·  Compártelo con tu equipo  ·  Sígueme'
        tw3 = d.textlength(t3, font=f3)/S; d.text((s(W/2-tw3/2), s(cy+108)), t3, font=f3, fill=YELLOW)
    out = img.convert('RGB').resize((W, H), Image.LANCZOS)
    out.save(f'/home/claude/carrusel/out/MESHTACTICO_{n:02d}.png', optimize=True)

if __name__ == '__main__':
    import os; os.makedirs('/home/claude/carrusel/out', exist_ok=True)
    for n in (map(int, sys.argv[1:]) if len(sys.argv) > 1 else range(1, 11)):
        make(n); print('ok', n)
