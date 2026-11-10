# Herramientas de producción MESHTACTICO

Copia de seguridad de los motores con los que se generan los reels y carruseles,
para que el estilo se pueda reproducir aunque cambie la sesión.

## Reel (1080x1920, 30 fps)
- `reel/render_reel.py` (pycairo + ffmpeg). Fuentes: Inter Display + DejaVu Sans Mono.
- Estilo: fondo #0B0F0C, verde fósforo, mapa topográfico, visor HUD "MESHTACTICO // 0XX", hora Zulu.
- Voz: ElevenLabs, voz "David Martin" (voice_id Nh2zY9kknu6z4pZy6FhD), modelo eleven_v4.
- Las escenas se ajustan a las pausas de la locución (silencedetect).

## Carrusel (10 x 1080x1350)
- `carrusel/render.py` (primitivas) + `slides2.py` (plantilla del carrusel 02).
- Fuente: Barlow Condensed (OFL), en `carrusel/fonts/`.
- Estilo: título blanco + línea amarilla, banda amarilla inferior, numeración 0X/10, "DESLIZA".

## Publicación
- Los archivos se suben a `reels/` y `carruseles/` de este repo y se publican en Metricool
  (marca 7977600) usando la URL raw.githubusercontent.com. Imágenes en JPG.
