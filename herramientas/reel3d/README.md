# Motor de reels 3D (Three.js)

Valle low-poly nocturno con curvas de nivel en verde, cámara continua, etiquetas pegadas a objetos y subtítulos palabra a palabra.

- `scene.html`: escena y línea de tiempo (`SEGS` = frases de la locución con sus tiempos; `KEYS` = cámara).
- `render.js`: renderiza fotogramas 1080x1920 con Chrome headless (SwiftShader).
  `npm i three@0.170.0` y luego `NODE_PATH=<ruta a playwright> node render.js frames 0 45.2 30 1`
- Montaje: `ffmpeg -framerate 30 -i frames/f_%05d.jpg -i voz.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -shortest out.mp4`
- Voz: ElevenLabs "David Martin" (Nh2zY9kknu6z4pZy6FhD), eleven_v4, atempo 1.07; tiempos con silencedetect.
