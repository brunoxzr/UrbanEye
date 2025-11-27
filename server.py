from ultralytics import YOLO
import cv2
from flask import Flask, render_template, Response, jsonify
import threading
import time
import requests
import subprocess
import numpy as np

# =======================================================
# CONFIGURAÇÕES DO PROJETO
# =======================================================
VIDEO_URL = "http://100.130.10.166:4747/video"   # DroidCam iOS (H.264 encapsulado)
CITY_LAT = -23.304
CITY_LON = -51.169

LOCAL_ATUAL = "Entrada Principal — Evento FIIL"
LOCAL_ALTERNATIVO = "Estande 2 — Área Interna"

LOTACAO = {
    "TRANQUILO": 4,
    "MODERADO": 10
}

pessoas_atual = 0
status_atual = "DESCONHECIDO"
clima_atual = "indisponível"
recomendacao_atual = ""
frame_atual = None

# =======================================================
# FLASK + YOLO
# =======================================================
app = Flask(__name__)
model = YOLO("models/yolov8n.pt")


# =======================================================
# CLIMA (API: Open-Meteo)
# =======================================================
def atualizar_clima():
    global clima_atual
    try:
        r = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={CITY_LAT}&longitude={CITY_LON}&current_weather=true"
        ).json()

        codigo = r["current_weather"]["weathercode"]

        mapa = {
            0: "céu limpo",
            1: "parcialmente nublado",
            2: "nublado",
            3: "nublado denso",
            61: "chuva leve",
            63: "chuva moderada",
            65: "chuva forte",
            80: "pancadas de chuva",
            81: "pancadas moderadas",
            82: "pancadas fortes",
        }

        clima_atual = mapa.get(codigo, "desconhecido")
    except:
        clima_atual = "indisponível"


# =======================================================
# LÓGICA DE STATUS
# =======================================================
def calcular_status(qtd):
    if qtd <= LOTACAO["TRANQUILO"]:
        return "TRANQUILO"
    elif qtd <= LOTACAO["MODERADO"]:
        return "MODERADO"
    return "LOTADO"


def gerar_recomendacao(status, clima):
    # Regras inteligentes
    if status == "LOTADO":
        return (
            f"Muita movimentação na {LOCAL_ATUAL}. "
            f"Recomendamos deslocamento para {LOCAL_ALTERNATIVO}, onde o fluxo está menor."
        )

    if status == "MODERADO":
        return (
            f"Movimento moderado na {LOCAL_ATUAL}. "
            f"É seguro permanecer, mas o {LOCAL_ALTERNATIVO} está mais tranquilo."
        )

    if status == "TRANQUILO":
        if "chuva" in clima:
            return "Tranquilo, porém com chuva — prefira áreas cobertas (Estande 2)."
        return f"Ambiente tranquilo na {LOCAL_ATUAL}. Aproveite o momento!"

    return "Analisando fluxo em tempo real..."


# =======================================================
# ROTAS HTML
# =======================================================
@app.route("/")
def index():
    return render_template(
    "index.html",
    local_atual=LOCAL_ATUAL,
    local_alt=LOCAL_ALTERNATIVO,
    LOTACAO=LOTACAO
)


@app.route("/pontos")
def pontos():
    return render_template("pontos.html")

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/contato")
def contato():
    return render_template("contato.html")


# =======================================================
# API /status
# =======================================================
@app.route("/status")
def status():
    return jsonify({
        "pessoas": pessoas_atual,
        "status": status_atual,
        "clima": clima_atual,
        "recomendacao": recomendacao_atual,
        "local": LOCAL_ATUAL,
        "alternativa": LOCAL_ALTERNATIVO
    })


# =======================================================
# STREAM /video_feed
# =======================================================
@app.route("/video_feed")
def video_feed():
    def gerar():
        global frame_atual
        while True:
            if frame_atual is None:
                continue

            _, jpeg = cv2.imencode(".jpg", frame_atual)

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + jpeg.tobytes()
                + b"\r\n"
            )

    return Response(gerar(), mimetype="multipart/x-mixed-replace; boundary=frame")


# =======================================================
# PROCESSAMENTO DE VÍDEO — DroidCam iOS com FFmpeg
# =======================================================
def processar_video():
    global pessoas_atual, status_atual, recomendacao_atual, frame_atual

    ffmpeg_cmd = [
        "ffmpeg",
        "-i", VIDEO_URL,
        "-vf", "scale=640:480",
        "-f", "image2pipe",
        "-pix_fmt", "bgr24",
        "-vcodec", "rawvideo",
        "-"
    ]

    p = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    while True:
        raw_frame = p.stdout.read(640 * 480 * 3)
        if not raw_frame:
            continue

        frame = np.frombuffer(raw_frame, np.uint8).reshape((480, 640, 3))

        # YOLO — filtro somente pessoas (classe 0)
        qtd = 0
        results = model(frame, verbose=False)

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                if cls == 0 and conf >= 0.30:
                    qtd += 1

        pessoas_atual = qtd
        status_atual = calcular_status(qtd)
        recomendacao_atual = gerar_recomendacao(status_atual, clima_atual)

        # prepara frame limpo para desenhar
        frame_draw = frame.copy()

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                # desenhar SOMENTE pessoas (classe 0)
                if cls == 0 and conf >= 0.50:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # caixa azul estilo gov
                    cv2.rectangle(frame_draw, (x1, y1), (x2, y2), (15, 50, 200), 2)
                    cv2.putText(
                        frame_draw,
                        f"Pessoa {conf:.2f}",
                        (x1, y1 - 7),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (15, 50, 200),
                        2
                    )

        # atualizar frame final
        frame_atual = frame_draw



# =======================================================
# THREADS
# =======================================================
def clima_loop():
    while True:
        atualizar_clima()
        time.sleep(20)


# =======================================================
# MAIN
# =======================================================
if __name__ == "__main__":
    threading.Thread(target=processar_video, daemon=True).start()
    threading.Thread(target=clima_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
