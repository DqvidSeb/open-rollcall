#!/usr/bin/env python3
"""
RollCall - Cliente de Cámara
============================
Modo enrollar  : python camera_client.py enroll <employee_id>
Modo asistencia: python camera_client.py attend [--camera INDEX]

Dependencias:
    pip install opencv-python requests python-dotenv mediapipe numpy

Notas sobre detección facial (best practices)
─────────────────────────────────────────────
1. Detector principal: **MediaPipe Face Detection** (BlazeFace).
   - Estado del arte para video en CPU, >100 FPS típicamente.
   - Devuelve 6 keypoints (ojos, nariz, boca, orejas).
   - Genera prácticamente cero falsos positivos a confianza ≥ 0.7
     (a diferencia del Haar Cascade clásico, que satura el frame con
     "cuadritos" sobre cuellos, cejas, sombras y patrones de fondo).
2. Fallback: Haar Cascade con parámetros ESTRICTOS, solo si MediaPipe
   no está disponible. Calidad notablemente inferior.
3. Tracker temporal: suaviza el bounding box (EMA) y mantiene el rostro
   "vivo" durante pequeños huecos de detección (0.4 s). Esto elimina el
   parpadeo de "medio segundo y desaparece".
4. Selección automática de rostro principal: si hay más de uno se elige
   el más grande y centrado (el sujeto activo). Los demás se ignoran.
5. Alineación por ojos antes del recorte → embeddings ArcFace más
   estables y mayor confianza.
"""
from __future__ import annotations

import argparse
import base64
import math
import os
import queue
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Optional
from zoneinfo import ZoneInfo

import cv2
import numpy as np
import requests
from dotenv import load_dotenv

# ── Detector moderno (opcional pero recomendado) ──────────────────────────────
# MediaPipe: en versiones recientes (>= 0.10.21) el submódulo `solutions` ya
# no se importa automáticamente y hay que forzarlo. Intentamos varias rutas.
mp_face_detection = None  # se inicializa abajo si esta disponible
try:
    import mediapipe as mp  # type: ignore  # noqa: F401
    try:
        # Ruta canonica (versiones <= 0.10.20)
        from mediapipe import solutions as _mp_solutions  # type: ignore
        mp_face_detection = _mp_solutions.face_detection
    except (ImportError, AttributeError):
        try:
            # Ruta interna (versiones nuevas donde solutions no se reexporta)
            from mediapipe.python.solutions import (  # type: ignore
                face_detection as _mp_face_detection,
            )
            mp_face_detection = _mp_face_detection
        except (ImportError, AttributeError):
            mp_face_detection = None
except ImportError:
    pass

MEDIAPIPE_AVAILABLE = mp_face_detection is not None

# YuNet (detector ONNX bundled con OpenCV >= 4.5.4). No requiere otra libreria
# de Python; solo descarga un archivo .onnx la primera vez (~340 KB).
YUNET_AVAILABLE = hasattr(cv2, "FaceDetectorYN")
YUNET_MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/"
    "models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
YUNET_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "face_detection_yunet_2023mar.onnx"
)

# ── Config ─────────────────────────────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

BASE_URL     = os.getenv("BASE_URL", "http://localhost:8000/api/v1")
API_USER     = os.getenv("API_USER", "")
API_PASSWORD = os.getenv("API_PASSWORD", "")

# ── Horario activo (se carga desde la API al inicio) ──────────────────────────
# Valores por defecto: Colombia, jornada estándar.
# Se sobreescriben llamando a load_active_schedule() durante el arranque.
# NO modificar estos valores a mano: configurar el horario desde la API
# (POST /api/v1/schedules o PATCH /api/v1/schedules/{id}).
_SCHEDULE_TZ_STR   = "America/Bogota"
SCHEDULE_TZ        = ZoneInfo(_SCHEDULE_TZ_STR)
CHECKIN_START      = 8    # hora (int) de inicio ventana check-in
CHECKIN_END        = 12   # hora (int) de fin ventana check-in (exclusive)
CHECKOUT_START     = 14   # hora (int) de inicio ventana check-out
CHECKOUT_END       = 24   # 24 = hasta medianoche
SCHEDULE_NAME      = "[por defecto]"


def load_active_schedule() -> None:
    """
    Consulta GET /api/v1/schedules/active y sobreescribe las variables
    globales de zona horaria y ventanas horarias con los valores de BD.

    · El endpoint es público (sin token): el cliente puede llamarlo antes
      de hacer login, durante el arranque.
    · Si la llamada falla (red caída, servidor no disponible, etc.) se
      conservan los valores por defecto y se imprime una advertencia.
      El cliente arranca igual; es preferible funcionar con defaults
      que bloquear el acceso a la cámara.

    Se invoca una sola vez en main(), justo antes del bucle principal.
    """
    global SCHEDULE_TZ, _SCHEDULE_TZ_STR
    global CHECKIN_START, CHECKIN_END, CHECKOUT_START, CHECKOUT_END, SCHEDULE_NAME

    try:
        resp = requests.get(
            f"{BASE_URL}/schedules/active",
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()

        tz_str = data.get("timezone", "America/Bogota")
        # Validar que la TZ sea reconocida antes de asignarla
        try:
            tz = ZoneInfo(tz_str)
        except Exception:
            print(f"[schedule] Zona horaria desconocida '{tz_str}', usando America/Bogota")
            tz = ZoneInfo("America/Bogota")
            tz_str = "America/Bogota"

        def _hhmm_to_hour(t_str: str) -> int:
            """Extrae la hora entera de 'HH:MM:SS' o 'HH:MM'."""
            return int(t_str.split(":")[0])

        SCHEDULE_TZ        = tz
        _SCHEDULE_TZ_STR   = tz_str
        CHECKIN_START      = _hhmm_to_hour(data["check_in_start"])
        CHECKIN_END        = _hhmm_to_hour(data["check_in_end"])
        CHECKOUT_START     = _hhmm_to_hour(data["checkout_start"])
        CHECKOUT_END       = _hhmm_to_hour(data["checkout_end"])
        SCHEDULE_NAME      = data.get("name", "—")

        print(
            f"[schedule] Horario cargado: '{SCHEDULE_NAME}' | TZ: {_SCHEDULE_TZ_STR} | "
            f"Check-in: {CHECKIN_START:02d}:00–{CHECKIN_END:02d}:00 | "
            f"Check-out: {CHECKOUT_START:02d}:00–{CHECKOUT_END:02d}:00"
        )

    except Exception as exc:
        print(
            f"[schedule] ⚠️  No se pudo cargar el horario desde la API: {exc}\n"
            f"           Usando valores por defecto: TZ={_SCHEDULE_TZ_STR} | "
            f"Check-in: {CHECKIN_START:02d}:00–{CHECKIN_END:02d}:00 | "
            f"Check-out: {CHECKOUT_START:02d}:00–{CHECKOUT_END:02d}:00"
        )

# ── Detector / tracker ─────────────────────────────────────────────────────────
DETECT_MIN_CONFIDENCE = 0.70   # MediaPipe — alto = casi cero falsos positivos
DETECT_MODEL_RANGE    = 0      # 0 = corto alcance (≤2 m, recomendado para webcam)
TRACK_EMA_ALPHA       = 0.55   # suavizado bbox (0 = solo histórico, 1 = solo nuevo)
TRACK_LOST_TTL_S      = 0.45   # se mantiene "vivo" tras perder detección

# ── Enrollment ─────────────────────────────────────────────────────────────────
ENROLL_PHOTOS         = 5
ENROLL_INITIAL_DELAY  = 15.0   # segundos antes de la primera foto
ENROLL_BETWEEN_DELAY  = 10.0   # segundos entre fotos sucesivas
ENROLL_TIMEOUT_S      = 180    # timeout HTTP (DeepFace descarga modelo la 1ª vez)

# Calidad mínima para aceptar una foto de enrollment
ENROLL_BLUR_MIN       = 45.0   # varianza Laplacian — más estricto en enrollment
ENROLL_FACE_AREA_MIN  = 0.05   # rostro ocupa >= 5% del frame
ENROLL_BRIGHT_MIN     = 40     # brillo mínimo
ENROLL_BRIGHT_MAX     = 240    # brillo máximo
ENROLL_EYE_DIST_MIN   = 35     # distancia inter-ocular mínima en px (rostro suficientemente grande)
ENROLL_YAW_MAX        = 0.25   # asimetría máxima entre ojo izq/der respecto a nariz (frontalidad)

# ── Asistencia ─────────────────────────────────────────────────────────────────
COOLDOWN_S            = 30     # segundos entre registros del mismo empleado
RECOGNITION_EVERY_S   = 2.5    # intervalo mínimo entre llamadas al servidor
CONFIDENCE_MIN        = 0.55   # confianza mínima cliente (servidor ya filtra por distancia)
ATTEND_TIMEOUT_S      = 20     # timeout HTTP para check-in
ATTEND_BLUR_MIN       = 22.0   # nitidez mínima para enviar al servidor
ATTEND_FACE_AREA_MIN  = 0.03   # 3% del frame
ATTEND_EYE_DIST_MIN   = 28     # px
# Con 1, registramos en cuanto el primer match supera CONFIDENCE_MIN. Esto evita
# que el usuario se quede 3-5s frente a la camara esperando a que pase el voto.
# La proteccion contra falsos positivos sigue activa: threshold de distancia
# en servidor + COOLDOWN_S de 30s por empleado + CONFIDENCE_MIN en cliente.
VOTE_NEEDED           = 1
VOTE_WINDOW           = 3

# Colores BGR
C_GREEN   = (0, 220, 80)
C_YELLOW  = (0, 200, 255)
C_RED     = (30, 30, 220)
C_BLUE    = (240, 160, 0)
C_WHITE   = (255, 255, 255)
C_BLACK   = (0, 0, 0)
C_GRAY    = (160, 160, 160)
C_ORANGE  = (0, 140, 255)
C_CYAN    = (255, 200, 0)

FONT      = cv2.FONT_HERSHEY_SIMPLEX
FONT_BOLD = cv2.FONT_HERSHEY_DUPLEX


# ══════════════════════════════════════════════════════════════════════════════
# Calidad de imagen
# ══════════════════════════════════════════════════════════════════════════════

def blur_score(gray: np.ndarray) -> float:
    """Varianza del Laplaciano — mayor = más nítido."""
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def brightness(gray: np.ndarray) -> float:
    return float(gray.mean())


def face_area_ratio(fw: int, fh: int, frame_w: int, frame_h: int) -> float:
    return (fw * fh) / (frame_w * frame_h)


def _downscale_for_detection(frame: np.ndarray, target_long_side: int) -> np.ndarray:
    """
    Reduce el frame para que el lado mayor sea `target_long_side`.

    El detector facial (YuNet/MediaPipe) no necesita HD para una webcam:
    a 480px de ancho corre 3-4x mas rapido en CPU y la calidad de deteccion
    es practicamente la misma para rostros de tamano webcam (>=80px).

    Si el frame ya es mas pequeno se devuelve sin tocar.
    """
    h, w = frame.shape[:2]
    long_side = max(h, w)
    if long_side <= target_long_side:
        return frame
    scale = target_long_side / float(long_side)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)


# CLAHE es relativamente costoso de instanciar. Lo creamos una sola vez y lo
# reusamos en todos los frames (es thread-safe a nivel de uso secuencial dentro
# del hilo principal). Reduce alocaciones y micro-latencia por frame.
_CLAHE = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))


def apply_clahe(gray: np.ndarray) -> np.ndarray:
    """Ecualización adaptativa de contraste (CLAHE) — normaliza iluminación."""
    return _CLAHE.apply(gray)


def align_face_by_eyes(
    frame: np.ndarray,
    bbox: tuple[int, int, int, int],
    landmarks: list[tuple[int, int]],
    pad: float = 0.40,
    out_size: int = 256,
) -> np.ndarray:
    """
    Recorta + alinea el rostro rotándolo para que los ojos queden horizontales.
    Esto mejora notablemente la precisión de ArcFace, que fue entrenado con
    rostros alineados. Si no hay landmarks, hace un recorte simple.
    """
    x, y, w, h = bbox
    fh, fw = frame.shape[:2]
    px = int(w * pad)
    py = int(h * pad)
    x1 = max(0, x - px)
    y1 = max(0, y - py)
    x2 = min(fw, x + w + px)
    y2 = min(fh, y + h + py)

    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        # fallback degenerate
        return cv2.resize(frame, (out_size, out_size), interpolation=cv2.INTER_AREA)

    # Si tenemos al menos los dos ojos, alineamos.
    if len(landmarks) >= 2:
        # MediaPipe: 0 = ojo derecho del sujeto, 1 = ojo izquierdo del sujeto
        rx, ry = landmarks[0][0] - x1, landmarks[0][1] - y1
        lx, ly = landmarks[1][0] - x1, landmarks[1][1] - y1
        dx = lx - rx
        dy = ly - ry
        angle = math.degrees(math.atan2(dy, dx))
        ch, cw = crop.shape[:2]
        center = (cw / 2.0, ch / 2.0)
        M = cv2.getRotationMatrix2D(center, angle, scale=1.0)
        crop = cv2.warpAffine(
            crop, M, (cw, ch),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )

    return cv2.resize(crop, (out_size, out_size), interpolation=cv2.INTER_AREA)


def preprocess_for_recognition(face_crop: np.ndarray) -> np.ndarray:
    """
    CLAHE sobre el canal de luminancia del recorte para igualar iluminación.
    Mejora el reconocimiento en condiciones de luz variable sin alterar color.
    """
    ycrcb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2YCrCb)
    channels = list(cv2.split(ycrcb))
    channels[0] = apply_clahe(channels[0])
    ycrcb_eq = cv2.merge(channels)
    return cv2.cvtColor(ycrcb_eq, cv2.COLOR_YCrCb2BGR)


def encode_frame(frame: np.ndarray, quality: int = 90) -> str:
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buf.tobytes()).decode("utf-8")


# ══════════════════════════════════════════════════════════════════════════════
# Votación temporal (anti-falsos-positivos)
# ══════════════════════════════════════════════════════════════════════════════

class ConsecutiveVoter:
    """
    Acumula reconocimientos y dispara solo cuando el mismo employee_id
    aparece VOTE_NEEDED veces dentro de una ventana de VOTE_WINDOW intentos.
    """

    def __init__(self, needed: int = VOTE_NEEDED, window: int = VOTE_WINDOW) -> None:
        self._needed = needed
        self._window = window
        self._history: deque[str | None] = deque(maxlen=window)

    def vote(self, employee_id: str | None) -> bool:
        self._history.append(employee_id)
        if employee_id is None:
            return False
        return self._history.count(employee_id) >= self._needed

    def reset(self) -> None:
        self._history.clear()


# ══════════════════════════════════════════════════════════════════════════════
# Helpers visuales
# ══════════════════════════════════════════════════════════════════════════════

def put_text_bg(
    frame: np.ndarray,
    text: str,
    pos: tuple[int, int],
    font_scale: float = 0.55,
    fg: tuple = C_WHITE,
    bg: tuple = C_BLACK,
    thickness: int = 1,
) -> None:
    (w, h), baseline = cv2.getTextSize(text, FONT, font_scale, thickness)
    x, y = pos
    cv2.rectangle(frame, (x - 2, y - h - 4), (x + w + 2, y + baseline), bg, -1)
    cv2.putText(frame, text, (x, y), FONT, font_scale, fg, thickness, cv2.LINE_AA)


def draw_rounded_rect(
    frame: np.ndarray,
    pt1: tuple[int, int],
    pt2: tuple[int, int],
    color: tuple,
    thickness: int = 2,
    radius: int = 12,
) -> None:
    x1, y1 = pt1
    x2, y2 = pt2
    cv2.line(frame, (x1 + radius, y1), (x2 - radius, y1), color, thickness)
    cv2.line(frame, (x1 + radius, y2), (x2 - radius, y2), color, thickness)
    cv2.line(frame, (x1, y1 + radius), (x1, y2 - radius), color, thickness)
    cv2.line(frame, (x2, y1 + radius), (x2, y2 - radius), color, thickness)
    cv2.ellipse(frame, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)
    cv2.ellipse(frame, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)
    cv2.ellipse(frame, (x1 + radius, y2 - radius), (radius, radius),  90, 0, 90, color, thickness)
    cv2.ellipse(frame, (x2 - radius, y2 - radius), (radius, radius),   0, 0, 90, color, thickness)


def draw_landmarks(
    frame: np.ndarray,
    landmarks: list[tuple[int, int]],
    color: tuple = C_CYAN,
) -> None:
    """Dibuja los keypoints de MediaPipe: ojos (azul), nariz, boca."""
    if not landmarks:
        return
    # 0,1 ojos | 2 nariz | 3 boca | 4,5 orejas
    eye_color   = (255, 255, 0)
    nose_color  = (0, 255, 200)
    mouth_color = (200, 100, 255)
    palette = [eye_color, eye_color, nose_color, mouth_color, color, color]
    for i, (lx, ly) in enumerate(landmarks):
        col = palette[i] if i < len(palette) else color
        cv2.circle(frame, (lx, ly), 3, col, -1, cv2.LINE_AA)
        cv2.circle(frame, (lx, ly), 5, C_WHITE, 1, cv2.LINE_AA)


def draw_quality_bar(
    frame: np.ndarray,
    label: str,
    value: float,
    max_val: float,
    x: int, y: int,
    width: int = 120,
    ok: bool = True,
) -> None:
    ratio = min(value / max_val, 1.0) if max_val > 0 else 0.0
    bar_w = int(width * ratio)
    color = C_GREEN if ok else C_RED
    cv2.rectangle(frame, (x, y), (x + width, y + 10), C_GRAY, -1)
    cv2.rectangle(frame, (x, y), (x + bar_w, y + 10), color, -1)
    put_text_bg(frame, f"{label}: {value:.0f}", (x, y - 3), font_scale=0.38, fg=color, bg=C_BLACK)


# ══════════════════════════════════════════════════════════════════════════════
# Auth
# ══════════════════════════════════════════════════════════════════════════════

class AuthSession:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self._token: str = ""

    def login(self, username: str, password: str) -> None:
        resp = requests.post(
            f"{self.base_url}/auth/login",
            data={"username": username, "password": password},
            timeout=10,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Login fallido ({resp.status_code}): {resp.text}")
        self._token = resp.json()["access_token"]
        print("[AUTH] Sesion iniciada correctamente.")

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}

    def post(self, path: str, json: dict, timeout: int = 20) -> requests.Response:
        return requests.post(
            f"{self.base_url}{path}",
            json=json,
            headers=self.headers,
            timeout=timeout,
        )


# ══════════════════════════════════════════════════════════════════════════════
# Detector facial — MediaPipe (principal) + Haar (fallback)
# ══════════════════════════════════════════════════════════════════════════════

class Detection(dict):
    """{'bbox': (x,y,w,h), 'landmarks': [(x,y), ...], 'score': float}"""


class MediaPipeFaceDetector:
    """
    Detector basado en BlazeFace de MediaPipe.
    - Sin falsos positivos al usar min_detection_confidence ≥ 0.7.
    - Provee 6 landmarks: ojos, nariz, boca, orejas.
    - Rápido en CPU (>100 FPS en webcam HD).
    """

    NAME = "MediaPipe (BlazeFace)"

    def __init__(self) -> None:
        if mp_face_detection is None:
            raise RuntimeError(
                "MediaPipe Face Detection no esta disponible. "
                "Instala una version compatible o usa el fallback Haar."
            )

        self._mp = mp_face_detection.FaceDetection(
            model_selection=DETECT_MODEL_RANGE,
            min_detection_confidence=DETECT_MIN_CONFIDENCE,
        )

    def detect(self, frame_bgr: np.ndarray) -> list[Detection]:
        # MediaPipe usa coordenadas relativas, asi que el downscale es
        # transparente: las coords ya vienen normalizadas y se multiplican
        # por (w, h) del frame original al final.
        h, w = frame_bgr.shape[:2]
        small = _downscale_for_detection(frame_bgr, DETECT_TARGET_LONG_SIDE)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False

        result = self._mp.process(rgb)

        if not result.detections:
            return []

        out: list[Detection] = []

        for det in result.detections:
            box = det.location_data.relative_bounding_box

            x = max(0, int(box.xmin * w))
            y = max(0, int(box.ymin * h))
            bw = min(w - x, int(box.width * w))
            bh = min(h - y, int(box.height * h))

            if bw <= 0 or bh <= 0:
                continue

            lms = [
                (int(kp.x * w), int(kp.y * h))
                for kp in det.location_data.relative_keypoints
            ]

            score = float(det.score[0]) if det.score else 0.0

            out.append(
                Detection(
                    bbox=(x, y, bw, bh),
                    landmarks=lms,
                    score=score,
                )
            )

        return out

class YuNetFaceDetector:
    """
    Detector facial YuNet de OpenCV.
    - Más moderno que Haar.
    - No depende de MediaPipe.
    - Devuelve bbox + landmarks básicos: ojos, nariz y comisuras de boca.
    """

    NAME = "OpenCV YuNet"

    def __init__(self) -> None:
        if not YUNET_AVAILABLE:
            raise RuntimeError(
                "OpenCV no tiene FaceDetectorYN. Instala opencv-contrib-python."
            )

        if not os.path.exists(YUNET_MODEL_PATH):
            raise RuntimeError(
                "No se encontro el modelo YuNet. Descargalo con:\n"
                "python -c \"from urllib.request import urlretrieve; "
                "urlretrieve('https://github.com/opencv/opencv_zoo/raw/main/models/"
                "face_detection_yunet/face_detection_yunet_2023mar.onnx', "
                "'face_detection_yunet_2023mar.onnx')\""
            )

        self._detector = cv2.FaceDetectorYN.create(
            YUNET_MODEL_PATH,
            "",
            (320, 320),
            score_threshold=DETECT_MIN_CONFIDENCE,
            nms_threshold=0.3,
            top_k=5000,
        )
        self._input_size: tuple[int, int] | None = None

    def detect(self, frame_bgr: np.ndarray) -> list[Detection]:
        h, w = frame_bgr.shape[:2]

        # Detectamos en un frame reducido y reescalamos las coords al original.
        # YuNet devuelve coords absolutas, asi que aplicamos factor 1/scale.
        small = _downscale_for_detection(frame_bgr, DETECT_TARGET_LONG_SIDE)
        sh, sw = small.shape[:2]
        scale_x = w / float(sw)
        scale_y = h / float(sh)

        if self._input_size != (sw, sh):
            self._detector.setInputSize((sw, sh))
            self._input_size = (sw, sh)

        _ok, faces = self._detector.detect(small)

        if faces is None or len(faces) == 0:
            return []

        out: list[Detection] = []

        for face in faces:
            x, y, bw, bh = face[:4]
            score = float(face[14])

            x = max(0, int(x * scale_x))
            y = max(0, int(y * scale_y))
            bw = min(w - x, int(bw * scale_x))
            bh = min(h - y, int(bh * scale_y))

            if bw <= 0 or bh <= 0:
                continue

            # YuNet: right_eye, left_eye, nose, right_mouth, left_mouth.
            # Reescalamos cada landmark al sistema del frame original.
            def sx(v: float) -> int:
                return int(v * scale_x)

            def sy(v: float) -> int:
                return int(v * scale_y)

            landmarks = [
                (sx(face[4]),  sy(face[5])),
                (sx(face[6]),  sy(face[7])),
                (sx(face[8]),  sy(face[9])),
                (sx((face[10] + face[12]) / 2), sy((face[11] + face[13]) / 2)),
                (sx(face[10]), sy(face[11])),
                (sx(face[12]), sy(face[13])),
            ]

            out.append(
                Detection(
                    bbox=(x, y, bw, bh),
                    landmarks=landmarks,
                    score=score,
                )
            )

        return out

class HaarFaceDetector:
    """
    Fallback estricto cuando MediaPipe no esta instalado.
    Parametros muy restrictivos para minimizar falsos positivos.
    """

    NAME = "Haar Cascade (fallback)"

    def __init__(self) -> None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self._detector = cv2.CascadeClassifier(cascade_path)
        if self._detector.empty():
            raise RuntimeError("No se encontro el clasificador Haar Cascade.")

    def detect(self, frame_bgr: np.ndarray) -> list[Detection]:
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        raw = self._detector.detectMultiScale(
            gray,
            scaleFactor=1.15,     # mas estricto => menos falsos positivos
            minNeighbors=6,       # mas estricto
            minSize=(80, 80),     # rechaza detecciones pequenas (ruido)
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        if len(raw) == 0:
            return []
        return [
            Detection(bbox=(int(x), int(y), int(w), int(h)), landmarks=[], score=1.0)
            for (x, y, w, h) in raw
        ]


def make_detector():
    if YUNET_AVAILABLE and os.path.exists(YUNET_MODEL_PATH):
        print("[DET] Usando OpenCV YuNet.")
        return YuNetFaceDetector()

    if MEDIAPIPE_AVAILABLE:
        print("[DET] Usando MediaPipe (BlazeFace).")
        return MediaPipeFaceDetector()

    print(
        "[DET][WARN] YuNet/MediaPipe no disponibles — usando Haar Cascade "
        "(calidad inferior).\n"
        "            Para YuNet descarga el modelo:\n"
        "            python -c \"from urllib.request import urlretrieve; "
        "urlretrieve('https://github.com/opencv/opencv_zoo/raw/main/models/"
        "face_detection_yunet/face_detection_yunet_2023mar.onnx', "
        "'face_detection_yunet_2023mar.onnx')\""
    )
    return HaarFaceDetector()


# ══════════════════════════════════════════════════════════════════════════════
# Tracker: suavizado + seleccion de rostro principal
# ══════════════════════════════════════════════════════════════════════════════

class FaceTracker:
    """
    Selecciona el rostro principal (mas grande + cercano al centro) y suaviza
    su bounding box con EMA para eliminar el "parpadeo". Mantiene la deteccion
    viva durante pequenos huecos (lost_ttl) para evitar el efecto de
    "aparece-desaparece" cada medio segundo.
    """

    def __init__(
        self,
        alpha: float = TRACK_EMA_ALPHA,
        lost_ttl: float = TRACK_LOST_TTL_S,
    ) -> None:
        self._alpha = alpha
        self._lost_ttl = lost_ttl
        self._bbox: Optional[tuple[int, int, int, int]] = None
        self._lms: list[tuple[int, int]] = []
        self._last_seen: float = 0.0
        self._extra_count: int = 0   # cuantos rostros adicionales se ignoraron

    @property
    def extra_faces(self) -> int:
        return self._extra_count

    def _pick_best(
        self,
        detections: list[Detection],
        frame_shape: tuple[int, ...],
    ) -> Detection:
        h, w = frame_shape[:2]
        cx, cy = w / 2.0, h / 2.0
        diag2 = (w * w + h * h)

        def score(d: Detection) -> float:
            x, y, bw, bh = d["bbox"]
            face_cx = x + bw / 2.0
            face_cy = y + bh / 2.0
            area_ratio = (bw * bh) / (w * h)
            dist2 = ((face_cx - cx) ** 2 + (face_cy - cy) ** 2) / diag2
            # Prioriza tamano y centralidad; pondera mas el area.
            return area_ratio - 0.25 * dist2

        return max(detections, key=score)

    def update(
        self,
        detections: list[Detection],
        frame_shape: tuple[int, ...],
    ) -> Optional[Detection]:
        now = time.time()

        if not detections:
            self._extra_count = 0
            if self._bbox is not None and (now - self._last_seen) < self._lost_ttl:
                return Detection(bbox=self._bbox, landmarks=self._lms, score=0.0)
            self._bbox = None
            self._lms = []
            return None

        self._extra_count = max(0, len(detections) - 1)
        best = self._pick_best(detections, frame_shape)
        new_bbox = best["bbox"]

        if self._bbox is not None and (now - self._last_seen) < self._lost_ttl:
            a = self._alpha
            sx = int(a * new_bbox[0] + (1 - a) * self._bbox[0])
            sy = int(a * new_bbox[1] + (1 - a) * self._bbox[1])
            sw = int(a * new_bbox[2] + (1 - a) * self._bbox[2])
            sh = int(a * new_bbox[3] + (1 - a) * self._bbox[3])
            smoothed = (sx, sy, sw, sh)
        else:
            smoothed = new_bbox

        self._bbox = smoothed
        self._lms = best["landmarks"]
        self._last_seen = now
        return Detection(bbox=smoothed, landmarks=best["landmarks"], score=best["score"])

    def reset(self) -> None:
        self._bbox = None
        self._lms = []
        self._extra_count = 0


# ══════════════════════════════════════════════════════════════════════════════
# Camara
# ══════════════════════════════════════════════════════════════════════════════

# Resolucion de captura. 960x540 es el sweet spot: suficiente para deteccion y
# reconocimiento, pero ~2.7x menos pixeles que 1280x720 -> latencia mucho menor.
CAPTURE_WIDTH  = 960
CAPTURE_HEIGHT = 540
CAPTURE_FPS    = 30

# Lado mayor al que se reduce el frame solo para correr el detector. La deteccion
# no necesita 960px de ancho para una cara webcam; con 480 es suficiente y
# corre ~4x mas rapido en CPU. El bbox/landmarks se reescalan al frame original.
DETECT_TARGET_LONG_SIDE = 480


def open_camera(index: int = -1) -> cv2.VideoCapture:
    indices = [index] if index >= 0 else list(range(5))
    for i in indices:
        # En Windows DSHOW es el backend mas estable para webcams USB/integradas.
        backend = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
        cap = cv2.VideoCapture(i, backend)
        if cap.isOpened():
            # OJO con el orden: en muchos backends hay que fijar FOURCC ANTES
            # que la resolucion para evitar el modo YUY2 default que limita a
            # 10 FPS a 720p+ en webcams integradas (caso clasico Asus/HP/Lenovo).
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
            cap.set(cv2.CAP_PROP_FPS, CAPTURE_FPS)
            # Buffer pequeno => menor latencia.
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            # Autofocus solo si la camara lo soporta (algunas integradas no).
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = cap.get(cv2.CAP_PROP_FPS)
            print(
                f"[CAM] Abierta en indice {i} — "
                f"{actual_w}x{actual_h} @ {actual_fps:.0f} FPS (MJPG)."
            )
            return cap
        cap.release()
    raise RuntimeError(
        "No se encontro ninguna camara. "
        "Conecta una camara USB o usa --camera <indice> para especificar."
    )


# ══════════════════════════════════════════════════════════════════════════════
# Calidad — comprobaciones usando landmarks
# ══════════════════════════════════════════════════════════════════════════════

def _eye_distance(landmarks: list[tuple[int, int]]) -> float:
    if len(landmarks) < 2:
        return 0.0
    (x0, y0), (x1, y1) = landmarks[0], landmarks[1]
    return math.hypot(x1 - x0, y1 - y0)


def _frontality(landmarks: list[tuple[int, int]]) -> float:
    """
    Mide que tan frontal esta el rostro usando la asimetria horizontal
    entre nariz y eje de los ojos. 0 = perfectamente frontal, 1 = perfil.
    """
    if len(landmarks) < 3:
        return 0.0
    re, le, nose = landmarks[0], landmarks[1], landmarks[2]
    eye_cx = (re[0] + le[0]) / 2.0
    eye_dist = max(1.0, abs(le[0] - re[0]))
    return abs(nose[0] - eye_cx) / eye_dist


def _check_enroll_quality(
    frame: np.ndarray,
    detection: Optional[Detection],
) -> tuple[bool, str, dict]:
    fh, fw = frame.shape[:2]
    if detection is None:
        return False, "Ubica tu rostro frente a la camara", {}

    x, y, w, h = detection["bbox"]
    lms = detection["landmarks"]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_gray = gray[max(0, y):y + h, max(0, x):x + w]
    if face_gray.size == 0:
        return False, "Rostro fuera del encuadre", {}

    b_score = blur_score(face_gray)
    bright  = brightness(face_gray)
    area_r  = face_area_ratio(w, h, fw, fh)
    eye_d   = _eye_distance(lms)
    yaw     = _frontality(lms)

    metrics = {
        "blur": b_score,
        "bright": bright,
        "area_pct": area_r * 100,
        "eye_dist": eye_d,
        "yaw": yaw,
    }

    if b_score < ENROLL_BLUR_MIN:
        return False, "Imagen borrosa — quietate o mejora la iluminacion", metrics
    if bright < ENROLL_BRIGHT_MIN:
        return False, "Muy oscuro — mejora la iluminacion", metrics
    if bright > ENROLL_BRIGHT_MAX:
        return False, "Sobreexpuesto — reduce la luz directa", metrics
    if area_r < ENROLL_FACE_AREA_MIN:
        return False, "Acercate mas a la camara", metrics
    if lms and eye_d < ENROLL_EYE_DIST_MIN:
        return False, "Acercate mas — ojos muy juntos en la imagen", metrics
    if lms and yaw > ENROLL_YAW_MAX:
        return False, "Mira mas de frente a la camara", metrics

    return True, "Calidad OK", metrics


def _check_attend_quality(
    frame: np.ndarray,
    detection: Optional[Detection],
) -> tuple[bool, str]:
    if detection is None:
        return False, ""
    fh, fw = frame.shape[:2]
    x, y, w, h = detection["bbox"]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_gray = gray[max(0, y):y + h, max(0, x):x + w]
    if face_gray.size == 0:
        return False, "Rostro fuera del encuadre"

    b = blur_score(face_gray)
    area = face_area_ratio(w, h, fw, fh)
    bright = brightness(face_gray)
    eye_d = _eye_distance(detection["landmarks"])

    if b < ATTEND_BLUR_MIN:
        return False, "Imagen borrosa"
    if area < ATTEND_FACE_AREA_MIN:
        return False, "Acercate mas a la camara"
    if bright < ENROLL_BRIGHT_MIN or bright > ENROLL_BRIGHT_MAX:
        return False, "Ajusta la iluminacion"
    if detection["landmarks"] and eye_d < ATTEND_EYE_DIST_MIN:
        return False, "Acercate mas a la camara"
    return True, "OK"


# ══════════════════════════════════════════════════════════════════════════════
# Modo Enrollment
# ══════════════════════════════════════════════════════════════════════════════

ANGLE_GUIDES = [
    "Mira directo a la camara - Centro",
    "Gira ligeramente a la IZQUIERDA",
    "Gira ligeramente a la DERECHA",
    "Inclina la cabeza hacia ARRIBA",
    "Inclina la cabeza hacia ABAJO",
]


def run_enrollment(employee_id: str, auth: AuthSession, camera_index: int = -1) -> None:
    cap = open_camera(camera_index)
    detector = make_detector()
    tracker  = FaceTracker()

    images_b64: list[str] = []
    current_step = 0
    phase_start: Optional[float] = None
    phase_delay  = ENROLL_INITIAL_DELAY
    last_metrics: dict = {}

    print(f"\n[ENROLL] Empleado: {employee_id}")
    print(f"[ENROLL] {ENROLL_PHOTOS} fotos — {ENROLL_INITIAL_DELAY}s inicial, {ENROLL_BETWEEN_DELAY}s entre fotos")
    print("[ENROLL] Presiona ESC para cancelar.\n")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("[ERROR] No se pudo leer el frame.")
            break

        frame = cv2.flip(frame, 1)
        fh, fw = frame.shape[:2]
        overlay = frame.copy()

        detections = detector.detect(frame)
        primary    = tracker.update(detections, frame.shape)
        extras     = tracker.extra_faces

        # Si hay multiples rostros: ignorar y avisar (mas estricto en enrollment)
        if extras > 0:
            q_ok, q_msg, last_metrics = False, "Solo una persona en el encuadre", {}
        else:
            q_ok, q_msg, last_metrics = _check_enroll_quality(frame, primary)

        if q_ok and phase_start is None:
            phase_start = time.time()
        elif not q_ok:
            phase_start = None

        # ── Panel superior ─────────────────────────────────────────────────────
        cv2.rectangle(overlay, (0, 0), (fw, 72), (18, 18, 18), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        cv2.putText(
            frame,
            f"ENROLLMENT  Foto {current_step + 1}/{ENROLL_PHOTOS}",
            (12, 28), FONT_BOLD, 0.68, C_YELLOW, 1, cv2.LINE_AA,
        )
        guide = ANGLE_GUIDES[current_step] if current_step < ENROLL_PHOTOS else "Listo"
        cv2.putText(frame, guide, (12, 56), FONT, 0.54, C_WHITE, 1, cv2.LINE_AA)

        # ── Rostro principal ───────────────────────────────────────────────────
        if primary is not None:
            x, y, w, h = primary["bbox"]
            color = C_GREEN if q_ok else C_ORANGE
            draw_rounded_rect(frame, (x, y), (x + w, y + h), color, 2)
            draw_landmarks(frame, primary["landmarks"], color=color)

        # ── Indicadores de calidad ─────────────────────────────────────────────
        if last_metrics:
            qx = fw - 160
            draw_quality_bar(frame, "Nitidez", last_metrics.get("blur", 0),
                             200, qx, fh - 95, ok=last_metrics.get("blur", 0) >= ENROLL_BLUR_MIN)
            draw_quality_bar(frame, "Brillo", last_metrics.get("bright", 0),
                             255, qx, fh - 72, ok=ENROLL_BRIGHT_MIN <= last_metrics.get("bright", 0) <= ENROLL_BRIGHT_MAX)
            draw_quality_bar(frame, "Tamano", last_metrics.get("area_pct", 0),
                             30, qx, fh - 49, ok=last_metrics.get("area_pct", 0) >= ENROLL_FACE_AREA_MIN * 100)

        # ── Barra de progreso / mensaje ────────────────────────────────────────
        if q_ok and phase_start is not None and primary is not None:
            elapsed   = time.time() - phase_start
            remaining = max(0.0, phase_delay - elapsed)
            ratio     = min(elapsed / phase_delay, 1.0)
            bar_w     = int(ratio * (fw - 40))

            cv2.rectangle(frame, (20, fh - 28), (fw - 20, fh - 12), C_GRAY, 1)
            cv2.rectangle(frame, (20, fh - 28), (20 + bar_w, fh - 12), C_GREEN, -1)
            put_text_bg(frame, f"Capturando en {remaining:.1f}s", (20, fh - 34), fg=C_WHITE)

            if elapsed >= phase_delay:
                face_crop = align_face_by_eyes(
                    frame, primary["bbox"], primary["landmarks"],
                    pad=0.40, out_size=256,
                )
                images_b64.append(encode_frame(face_crop, quality=92))
                current_step += 1
                print(
                    f"[ENROLL] Foto {current_step}/{ENROLL_PHOTOS} capturada "
                    f"(nitidez={last_metrics.get('blur', 0):.0f}, "
                    f"eye_dist={last_metrics.get('eye_dist', 0):.0f}px)"
                )

                # ── Pantalla de confirmacion ──────────────────────────────────
                confirm_until = time.time() + 2.0
                thumb = cv2.resize(face_crop, (140, 140))
                while time.time() < confirm_until:
                    ret2, cf = cap.read()
                    if not ret2:
                        break
                    cf = cv2.flip(cf, 1)
                    cfh, cfw = cf.shape[:2]

                    ov2 = cf.copy()
                    cv2.rectangle(ov2, (0, 0), (cfw, cfh), (0, 180, 60), -1)
                    cv2.addWeighted(ov2, 0.15, cf, 0.85, 0, cf)

                    th, tw = thumb.shape[:2]
                    cf[12:12 + th, cfw - tw - 12:cfw - 12] = thumb
                    cv2.rectangle(cf, (cfw - tw - 14, 10), (cfw - 10, 12 + th + 2), C_GREEN, 2)

                    msg = f"FOTO {current_step}/{ENROLL_PHOTOS} CAPTURADA"
                    (mw, _mh), _ = cv2.getTextSize(msg, FONT_BOLD, 0.9, 1)
                    cv2.putText(cf, msg, ((cfw - mw) // 2, cfh // 2), FONT_BOLD, 0.9, C_GREEN, 2, cv2.LINE_AA)

                    if current_step < ENROLL_PHOTOS:
                        next_guide = f"Siguiente: {ANGLE_GUIDES[current_step]}"
                        (nw, _), _ = cv2.getTextSize(next_guide, FONT, 0.52, 1)
                        cv2.putText(cf, next_guide, ((cfw - nw) // 2, cfh // 2 + 38), FONT, 0.52, C_WHITE, 1, cv2.LINE_AA)

                    cv2.imshow("RollCall - Enrollment", cf)
                    if cv2.waitKey(1) & 0xFF == 27:
                        cap.release()
                        cv2.destroyAllWindows()
                        return

                phase_start = None
                phase_delay = ENROLL_BETWEEN_DELAY
                tracker.reset()

                if current_step >= ENROLL_PHOTOS:
                    break
        else:
            color = C_ORANGE if primary is not None else C_GRAY
            put_text_bg(frame, q_msg, (20, fh - 18), fg=color)

        cv2.imshow("RollCall - Enrollment", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            print("[ENROLL] Cancelado.")
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()
    cv2.destroyAllWindows()

    if len(images_b64) < ENROLL_PHOTOS:
        print(f"[ENROLL] Solo {len(images_b64)}/{ENROLL_PHOTOS} fotos. Abortando.")
        return

    print(f"\n[ENROLL] Enviando al servidor (puede tardar hasta {ENROLL_TIMEOUT_S}s la primera vez)...")
    try:
        resp = auth.post(
            f"/face/enroll/{employee_id}",
            {"images_base64": images_b64},
            timeout=ENROLL_TIMEOUT_S,
        )
        if resp.status_code in (200, 201):
            data = resp.json()
            print(f"[ENROLL] Enrollment exitoso: {data['samples_captured']} muestras guardadas.")
        elif resp.status_code == 503:
            print("[ENROLL] El servidor no tiene DeepFace instalado.")
            print("         pip install deepface opencv-python-headless Pillow")
        else:
            print(f"[ENROLL] Error del servidor ({resp.status_code}): {resp.text}")
    except requests.exceptions.ReadTimeout:
        print(f"[ENROLL] Timeout — el servidor tardo mas de {ENROLL_TIMEOUT_S}s.")
        print("         Es normal la primera vez (DeepFace descarga el modelo). Intenta de nuevo.")
    except requests.exceptions.ConnectionError:
        print(f"[ENROLL] Sin conexion a {BASE_URL}")


# ══════════════════════════════════════════════════════════════════════════════
# RecognitionWorker — desacopla la I/O del servidor del loop de render.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class RecognitionResult:
    """Resultado producido por el worker para que el loop principal lo dibuje."""
    status_code: int
    payload: dict[str, Any] | None
    error: str | None
    submitted_at: float
    received_at: float


class RecognitionWorker:
    """
    Hilo en segundo plano que envia el frame al servidor de reconocimiento.

    Diseno: la cola de entrada tiene capacidad 1 y politica "latest-wins".
    Cuando el loop principal quiere enviar un nuevo frame y ya hay uno en vuelo,
    NO espera: descarta el viejo (si aun no se procesa) y mete el nuevo. Esto
    hace que el render no se bloquee NUNCA por la red ni por la inferencia
    en el servidor — que es la razon principal por la que la camara iba a
    "0-2 FPS" en el codigo anterior.

    La cola de salida sirve para que el hilo principal recoja el resultado
    cuando pueda, sin perder integridad.
    """

    def __init__(
        self,
        send_fn: Callable[[str], requests.Response],
        timeout_s: float,
    ) -> None:
        self._send_fn = send_fn
        self._timeout = timeout_s
        # max=1: solo un frame pendiente. Si llega otro lo reemplazamos.
        self._in_q: "queue.Queue[tuple[str, float] | None]" = queue.Queue(maxsize=1)
        self._out_q: "queue.Queue[RecognitionResult]" = queue.Queue()
        self._inflight = threading.Event()
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._run, name="RecognitionWorker", daemon=True
        )

    # ── API publica ──────────────────────────────────────────────────────────
    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        try:
            self._in_q.put_nowait(None)  # despierta el thread
        except queue.Full:
            pass
        self._thread.join(timeout=2.0)

    @property
    def busy(self) -> bool:
        """True si hay una peticion en vuelo (util para gating del loop)."""
        return self._inflight.is_set()

    def submit(self, image_b64: str) -> bool:
        """
        Intenta enviar un frame al worker. Si ya habia uno en cola sin procesar,
        lo descarta (latest-wins). Devuelve True si se acepto, False si el
        worker esta ocupado con una llamada en vuelo (el llamador debe esperar
        al siguiente ciclo).
        """
        if self._inflight.is_set():
            return False
        # Limpia lo que haya pendiente (no procesado todavia) y mete el nuevo.
        try:
            self._in_q.get_nowait()
        except queue.Empty:
            pass
        try:
            self._in_q.put_nowait((image_b64, time.time()))
            return True
        except queue.Full:
            return False

    def poll(self) -> RecognitionResult | None:
        """Devuelve el siguiente resultado si esta listo, o None."""
        try:
            return self._out_q.get_nowait()
        except queue.Empty:
            return None

    # ── Loop interno ─────────────────────────────────────────────────────────
    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                item = self._in_q.get(timeout=0.2)
            except queue.Empty:
                continue
            if item is None:
                break
            image_b64, submitted_at = item
            self._inflight.set()
            try:
                resp = self._send_fn(image_b64)
                payload: dict[str, Any] | None = None
                # Intentamos json primero — caso normal con FastAPI.
                try:
                    payload = resp.json() if resp.content else None
                except ValueError:
                    payload = None
                # Si no hay JSON y hay cuerpo (caso tipico de un 500 con HTML
                # "Internal Server Error"), sintetizamos un payload con
                # {"detail": "<primeras 200 chars del body>"} para que el
                # diagnostico en cliente muestre algo util en vez de "HTTP 500".
                if payload is None and resp.content:
                    body_text = ""
                    try:
                        body_text = resp.text
                    except Exception:  # noqa: BLE001
                        body_text = ""
                    if body_text:
                        snippet = body_text.strip().replace("\n", " ")
                        if len(snippet) > 200:
                            snippet = snippet[:200] + "..."
                        payload = {"detail": snippet}
                self._out_q.put(
                    RecognitionResult(
                        status_code=resp.status_code,
                        payload=payload,
                        error=None,
                        submitted_at=submitted_at,
                        received_at=time.time(),
                    )
                )
            except requests.exceptions.ReadTimeout:
                self._out_q.put(
                    RecognitionResult(
                        status_code=0,
                        payload=None,
                        error="timeout",
                        submitted_at=submitted_at,
                        received_at=time.time(),
                    )
                )
            except requests.exceptions.ConnectionError:
                self._out_q.put(
                    RecognitionResult(
                        status_code=0,
                        payload=None,
                        error="connection",
                        submitted_at=submitted_at,
                        received_at=time.time(),
                    )
                )
            except Exception as exc:  # pragma: no cover — red defensiva
                self._out_q.put(
                    RecognitionResult(
                        status_code=0,
                        payload=None,
                        error=f"unexpected: {exc}",
                        submitted_at=submitted_at,
                        received_at=time.time(),
                    )
                )
            finally:
                self._inflight.clear()


# ══════════════════════════════════════════════════════════════════════════════
# Modo Asistencia
# ══════════════════════════════════════════════════════════════════════════════

def now_local() -> datetime:
    """Hora actual en la zona horaria del schedule activo."""
    return datetime.now(SCHEDULE_TZ)


# Alias de compatibilidad (usado en partes del código que aún referencia now_bogota)
now_bogota = now_local


def time_window() -> str:
    """
    Clasifica la hora actual según el schedule cargado desde la API.
    Retorna 'checkin', 'checkout' o 'outside'.
    """
    h = now_local().hour
    if CHECKIN_START <= h < CHECKIN_END:
        return "checkin"
    if CHECKOUT_START <= h < CHECKOUT_END:
        return "checkout"
    return "outside"


def _draw_diag_panel(
    frame: np.ndarray,
    diag: dict,
    h: int,
    w: int,
) -> None:
    """
    Panel inferior tipo verify: SIEMPRE muestra que esta haciendo el servidor.
    No es una animacion — es informacion. Asi el operador nunca se queda sin
    saber por que el sistema reconoce o por que no.
    """
    kind = diag.get("kind", "error")
    latency = diag.get("latency_ms", 0.0)

    if kind == "match":
        bg_color   = (16, 38, 16)   # verde oscuro
        title_color = C_GREEN
        title = "RECONOCIDO"
        line1 = f"{diag.get('full_name', '—')}  ({diag.get('code', '—')})"
        line2 = (
            f"Distancia: {diag.get('distance', 0.0):.4f}    "
            f"Confianza: {diag.get('confidence', 0.0):.2%}    "
            f"Latencia: {latency:.0f}ms"
        )
    elif kind == "no_match":
        bg_color   = (38, 30, 16)   # ambar oscuro
        title_color = C_ORANGE
        title = "NO MATCH"
        nearest = diag.get("nearest_name") or "—"
        dist = diag.get("distance", 0.0)
        if dist > 0:
            line1 = f"Mas cercano: {nearest}    Distancia: {dist:.4f}"
        else:
            line1 = diag.get("msg", "Sin coincidencia") or "Sin coincidencia"
        line2 = f"Latencia: {latency:.0f}ms"
    elif kind == "conflict":
        bg_color   = (38, 16, 30)
        title_color = C_YELLOW
        title = "YA REGISTRADO HOY"
        line1 = diag.get("msg", "") or ""
        line2 = f"Latencia: {latency:.0f}ms"
    else:
        bg_color   = (38, 16, 16)
        title_color = C_RED
        title = "ERROR"
        line1 = diag.get("msg", "") or ""
        line2 = f"Latencia: {latency:.0f}ms"

    panel_h = 78
    ov = frame.copy()
    cv2.rectangle(ov, (0, h - panel_h), (w, h), bg_color, -1)
    cv2.addWeighted(ov, 0.82, frame, 0.18, 0, frame)
    cv2.line(frame, (0, h - panel_h), (w, h - panel_h), title_color, 2)

    cv2.putText(frame, title, (16, h - panel_h + 26),
                FONT_BOLD, 0.65, title_color, 1, cv2.LINE_AA)
    if line1:
        cv2.putText(frame, line1[:96], (16, h - panel_h + 50),
                    FONT, 0.52, C_WHITE, 1, cv2.LINE_AA)
    if line2:
        cv2.putText(frame, line2[:96], (16, h - panel_h + 70),
                    FONT, 0.46, C_GRAY, 1, cv2.LINE_AA)


def _draw_big_check(
    frame: np.ndarray,
    center: tuple[int, int],
    radius: int,
    color: tuple,
    thickness: int = 4,
) -> None:
    """Dibuja un circulo + un check (tipo material design) centrado en `center`."""
    cv2.circle(frame, center, radius, color, thickness, cv2.LINE_AA)
    cx, cy = center
    # Trazos del check: dos lineas con un quiebre.
    p1 = (cx - int(radius * 0.45), cy + int(radius * 0.05))
    p2 = (cx - int(radius * 0.10), cy + int(radius * 0.40))
    p3 = (cx + int(radius * 0.50), cy - int(radius * 0.35))
    cv2.line(frame, p1, p2, color, thickness + 1, cv2.LINE_AA)
    cv2.line(frame, p2, p3, color, thickness + 1, cv2.LINE_AA)


def _draw_result_overlay(
    frame: np.ndarray,
    result: dict,
    h: int,
    w: int,
    elapsed: float,
    total: float,
) -> None:
    """
    Overlay de resultado.

    - `elapsed`/`total` permiten animar: flash inicial breve y luego fade-out.
    - Para reconocimientos exitosos pintamos un check grande centrado +
      panel inferior con nombre, codigo, confianza y hora.
    - Para fallos un panel inferior compacto.
    """
    if result.get("recognized"):
        event = result.get("event_type", "check_in")
        is_checkin = event == "check_in"
        color = C_GREEN if is_checkin else C_YELLOW
        icon  = "ENTRADA REGISTRADA" if is_checkin else "SALIDA REGISTRADA"
        name  = result.get("full_name", "")
        code  = result.get("employee_code", "")
        conf  = result.get("confidence", 0.0)
        hhmm  = result.get("event_time_str", "")

        # ── Flash inicial (0.0 - 0.35s) sobre TODO el frame ─────────────────
        # Pico de intensidad en t=0.10s, decae a 0 en t=0.35s.
        flash_dur = 0.35
        if elapsed < flash_dur:
            t = elapsed / flash_dur
            intensity = (1.0 - t) * 0.5  # 0.5 al inicio, 0 al final
            flash = frame.copy()
            flash[:] = color
            cv2.addWeighted(flash, intensity, frame, 1.0 - intensity, 0, frame)

        # ── Check grande centrado, con pulso decreciente ────────────────────
        # Crece de 0.85 -> 1.10 del radio base en los primeros 0.4s.
        base_r = min(h, w) // 5
        if elapsed < 0.4:
            scale = 0.85 + (elapsed / 0.4) * 0.25
        else:
            scale = 1.10
        radius = max(40, int(base_r * scale))
        center = (w // 2, h // 2 - 20)

        # Sombra blanca para contraste sobre fondos claros u oscuros.
        _draw_big_check(frame, center, radius + 3, C_WHITE, thickness=6)
        _draw_big_check(frame, center, radius, color, thickness=5)

        # Texto grande encima del check.
        title_size, _ = cv2.getTextSize(icon, FONT_BOLD, 1.0, 2)
        title_x = (w - title_size[0]) // 2
        title_y = center[1] - radius - 24
        # Sombra negra del texto para legibilidad.
        cv2.putText(frame, icon, (title_x + 2, title_y + 2),
                    FONT_BOLD, 1.0, C_BLACK, 3, cv2.LINE_AA)
        cv2.putText(frame, icon, (title_x, title_y),
                    FONT_BOLD, 1.0, color, 2, cv2.LINE_AA)

        # Mensaje "PUEDES IRTE" debajo del check.
        sub = "PUEDES IRTE" if not is_checkin else "BIENVENIDO"
        sub_size, _ = cv2.getTextSize(sub, FONT_BOLD, 0.85, 2)
        sub_x = (w - sub_size[0]) // 2
        sub_y = center[1] + radius + 38
        cv2.putText(frame, sub, (sub_x + 2, sub_y + 2),
                    FONT_BOLD, 0.85, C_BLACK, 3, cv2.LINE_AA)
        cv2.putText(frame, sub, (sub_x, sub_y),
                    FONT_BOLD, 0.85, C_WHITE, 2, cv2.LINE_AA)

        # ── Panel inferior con metadata ─────────────────────────────────────
        panel_h = 92
        ov = frame.copy()
        cv2.rectangle(ov, (0, h - panel_h), (w, h), (18, 18, 18), -1)
        cv2.addWeighted(ov, 0.82, frame, 0.18, 0, frame)
        cv2.line(frame, (0, h - panel_h), (w, h - panel_h), color, 3)

        cv2.putText(frame, name, (20, h - panel_h + 34),
                    FONT_BOLD, 0.75, C_WHITE, 1, cv2.LINE_AA)
        cv2.putText(frame, f"Codigo: {code}", (20, h - panel_h + 62),
                    FONT, 0.55, C_GRAY, 1, cv2.LINE_AA)
        cv2.putText(frame, f"Confianza: {conf:.1%}", (20, h - panel_h + 82),
                    FONT, 0.50, color, 1, cv2.LINE_AA)
        if hhmm:
            cv2.putText(frame, hhmm, (w - 180, h - panel_h + 38),
                        FONT_BOLD, 0.85, color, 1, cv2.LINE_AA)

        # ── Cuenta regresiva del overlay ────────────────────────────────────
        remaining = max(0.0, total - elapsed)
        bar_w = int((remaining / total) * (w - 40)) if total > 0 else 0
        cv2.rectangle(frame, (20, h - 8), (20 + bar_w, h - 4), color, -1)
    else:
        # Panel "no reconocido" — compacto y rojo, sin flash.
        panel_h = 56
        ov = frame.copy()
        cv2.rectangle(ov, (0, h - panel_h), (w, h), (24, 20, 38), -1)
        cv2.addWeighted(ov, 0.82, frame, 0.18, 0, frame)
        cv2.line(frame, (0, h - panel_h), (w, h - panel_h), C_RED, 2)
        cv2.putText(frame, "Rostro no reconocido",
                    (16, h - 22), FONT_BOLD, 0.7, C_RED, 1, cv2.LINE_AA)


class FpsMeter:
    """Promedio movil simple del tiempo entre frames -> FPS estable y barato."""

    def __init__(self, window: int = 30) -> None:
        self._times: deque[float] = deque(maxlen=window)
        self._last: float | None = None

    def tick(self) -> float:
        now = time.time()
        if self._last is not None:
            self._times.append(now - self._last)
        self._last = now
        if not self._times:
            return 0.0
        avg = sum(self._times) / len(self._times)
        return 1.0 / avg if avg > 0 else 0.0


def _print_full_person(data: dict, latency_ms: float, hora: datetime) -> None:
    """Imprime en consola TODOS los datos disponibles del registro."""
    event = data.get("event_type", "check_in")
    is_in = event == "check_in"
    arrow = "→ ENTRADA REGISTRADA" if is_in else "← SALIDA REGISTRADA"

    border = "=" * 72
    print(f"\n{border}")
    print(f"  {arrow}    [{hora.strftime('%Y-%m-%d %H:%M:%S')} America/Bogota]")
    print(border)
    # Identidad
    print(f"  Nombre completo : {data.get('full_name') or '—'}")
    print(f"  Codigo empleado : {data.get('employee_code') or '—'}")
    print(f"  ID empleado     : {data.get('employee_id') or '—'}")
    # Datos extra cuando el backend los incluye (ver schema enriquecido).
    for label, key in (
        ("Email           ", "email"),
        ("Telefono        ", "phone"),
        ("Departamento    ", "department"),
        ("Cargo           ", "position"),
        ("Estado          ", "status"),
        ("Fecha ingreso   ", "hire_date"),
    ):
        if data.get(key) is not None:
            print(f"  {label}: {data[key]}")
    # Datos del evento.
    print(f"  Tipo evento     : {event}")
    if data.get("event_time"):
        print(f"  Timestamp evento: {data['event_time']}")
    if data.get("method"):
        print(f"  Metodo          : {data['method']}")
    print(f"  Confianza       : {(data.get('confidence') or 0.0):.2%}")
    print(f"  Log id          : {data.get('id') or '—'}")
    print(f"  Latencia red    : {latency_ms:.0f} ms")
    print(f"{border}\n")


@dataclass
class AttendHandleResult:
    """
    Resultado del handler de una respuesta del servidor en modo attend.

    - `overlay`: dict para `_draw_result_overlay` cuando hay registro confirmado.
    - `overlay_total_s`, `overlay_until_ts`: duracion y deadline del overlay.
    - `diag`: snapshot SIEMPRE poblado para el panel inferior tipo verify
      (incluye distancia, confianza, nombre del mas cercano o del match,
      mensaje crudo del servidor y status_code). Permite que el operador
      vea en pantalla por que reconoce o por que no.
    - `warn`: mensaje breve para overlay temporal (timeout/sin conexion).
    """
    overlay: dict | None
    overlay_total_s: float
    overlay_until_ts: float
    diag: dict
    warn: str | None


def _conf_to_dist(conf: float | None) -> float:
    """Convierte confianza (1 - dist/2) -> distancia coseno."""
    if conf is None or conf <= 0:
        return 0.0
    return max(0.0, 2.0 * (1.0 - conf))


def _handle_recognition_result(
    res: RecognitionResult,
    voter: ConsecutiveVoter,
    last_per_emp: dict[str, float],
    hora: datetime,
) -> AttendHandleResult:
    """Procesa un RecognitionResult del worker y prepara overlay + diagnostico."""
    now_ts = time.time()
    latency_ms = (res.received_at - res.submitted_at) * 1000.0

    # ── Errores de red ───────────────────────────────────────────────────────
    if res.error == "timeout":
        return AttendHandleResult(
            None, 0.0, 0.0,
            {"kind": "error", "msg": "Servidor lento — timeout", "latency_ms": latency_ms},
            "Servidor lento — timeout",
        )
    if res.error == "connection":
        return AttendHandleResult(
            None, 0.0, 0.0,
            {"kind": "error", "msg": f"Sin conexion a {BASE_URL}",
             "latency_ms": latency_ms},
            f"Sin conexion a {BASE_URL}",
        )
    if res.error:
        return AttendHandleResult(
            None, 0.0, 0.0,
            {"kind": "error", "msg": f"Error: {res.error}", "latency_ms": latency_ms},
            f"Error: {res.error}",
        )

    sc = res.status_code
    data = res.payload or {}
    detail = data.get("detail") if isinstance(data, dict) else None

    # ── Registro exitoso ─────────────────────────────────────────────────────
    if sc in (200, 201):
        emp_id     = str(data.get("employee_id", ""))
        confidence = float(data.get("confidence") or 0.0)
        full_name  = data.get("full_name") or "—"
        code       = data.get("employee_code") or "—"
        event      = data.get("event_type", "check_in")

        diag = {
            "kind": "match",
            "full_name": full_name,
            "code": code,
            "confidence": confidence,
            "distance": _conf_to_dist(confidence),
            "event_type": event,
            "latency_ms": latency_ms,
            "msg": f"{event.upper()} -> {full_name} ({code})",
        }
        print(
            f"[SRV {sc}] match {full_name} code={code} event={event} "
            f"conf={confidence:.4f} dist~{_conf_to_dist(confidence):.4f} "
            f"latency={latency_ms:.0f}ms"
        )

        if emp_id and confidence >= CONFIDENCE_MIN:
            if voter.vote(emp_id):
                cooldown_ok = (now_ts - last_per_emp.get(emp_id, 0)) >= COOLDOWN_S
                if cooldown_ok:
                    last_per_emp[emp_id] = now_ts
                    voter.reset()
                    _print_full_person(data, latency_ms, hora)
                    _success_beep(is_checkin=(event == "check_in"))
                    overlay_total = 5.5
                    return AttendHandleResult(
                        overlay={
                            "recognized": True,
                            "employee_id": emp_id,
                            "full_name": full_name,
                            "employee_code": code,
                            "event_type": event,
                            "confidence": confidence,
                            "event_time_str": hora.strftime("%H:%M:%S"),
                            "raw": data,
                        },
                        overlay_total_s=overlay_total,
                        overlay_until_ts=now_ts + overlay_total,
                        diag=diag,
                        warn=None,
                    )
                else:
                    diag["msg"] = (
                        f"Cooldown ({COOLDOWN_S}s) — ya registrado recientemente"
                    )
        else:
            voter.vote(None)
        return AttendHandleResult(None, 0.0, 0.0, diag, None)

    # ── 404 / 422 — no match. El servidor manda detalle con distancia. ──────
    if sc in (404, 422):
        voter.vote(None)
        msg = detail or "Rostro no reconocido"
        # Si el servidor ya nos da algo como
        # "Nearest: <nombre> dist=0.6231 (threshold=0.55)" lo parseamos a campos.
        nearest_name, nearest_dist = _parse_no_match_detail(msg)
        print(f"[SRV {sc}] no-match  detail={msg!r}  latency={latency_ms:.0f}ms")
        return AttendHandleResult(
            overlay={"recognized": False},
            overlay_total_s=1.6,
            overlay_until_ts=now_ts + 1.6,
            diag={
                "kind": "no_match",
                "msg": msg,
                "nearest_name": nearest_name,
                "distance": nearest_dist,
                "latency_ms": latency_ms,
            },
            warn=None,
        )

    # ── 409 — ya completaste entrada y salida hoy ───────────────────────────
    if sc == 409:
        msg = detail or "Ya completo entrada y salida hoy"
        print(f"[SRV 409] conflict detail={msg!r} latency={latency_ms:.0f}ms")
        return AttendHandleResult(
            overlay=None, overlay_total_s=0.0, overlay_until_ts=0.0,
            diag={"kind": "conflict", "msg": msg, "latency_ms": latency_ms},
            warn=msg,
        )

    # ── 503 — DeepFace no disponible en el servidor ─────────────────────────
    if sc == 503:
        msg = detail or "Servidor sin motor de reconocimiento"
        print(f"[SRV 503] {msg}")
        return AttendHandleResult(
            overlay=None, overlay_total_s=0.0, overlay_until_ts=0.0,
            diag={"kind": "error", "msg": msg, "latency_ms": latency_ms},
            warn=msg,
        )

    # ── Cualquier otro ──────────────────────────────────────────────────────
    msg = detail or f"HTTP {sc}"
    print(f"[SRV {sc}] unhandled  detail={msg!r}  latency={latency_ms:.0f}ms")
    return AttendHandleResult(
        overlay=None, overlay_total_s=0.0, overlay_until_ts=0.0,
        diag={"kind": "error", "msg": msg, "latency_ms": latency_ms},
        warn=msg,
    )


def _parse_no_match_detail(text: str) -> tuple[str | None, float]:
    """
    Extrae nombre del mas cercano y distancia desde el detail del servidor.
    Acepta formatos como:
      'Nearest: Maria Fernanda Guzman Lugo dist=0.6231 (threshold=0.55)'
    """
    name: str | None = None
    dist: float = 0.0
    if "Nearest:" in text:
        try:
            rest = text.split("Nearest:", 1)[1].strip()
            if "dist=" in rest:
                name = rest.split("dist=", 1)[0].strip().rstrip(",").rstrip()
                dist_str = rest.split("dist=", 1)[1].split(" ", 1)[0].strip()
                dist = float(dist_str)
        except (ValueError, IndexError):
            pass
    return name, dist


def _success_beep(is_checkin: bool) -> None:
    """Beep no bloqueante en Windows. Ignora en otros sistemas."""
    if sys.platform != "win32":
        return
    try:
        import winsound  # type: ignore  # noqa: PLC0415
        # Frecuencia/duracion distintas para entrada y salida.
        if is_checkin:
            winsound.Beep(900, 90)
            winsound.Beep(1200, 110)
        else:
            winsound.Beep(1200, 90)
            winsound.Beep(700, 110)
    except Exception:
        # winsound no esta o el driver de sonido fallo. No es critico.
        pass


def run_attendance(auth: AuthSession, camera_index: int = -1) -> None:
    cap = open_camera(camera_index)
    detector = make_detector()
    tracker  = FaceTracker()
    voter    = ConsecutiveVoter(needed=VOTE_NEEDED, window=VOTE_WINDOW)
    fps_meter = FpsMeter()

    # Worker en hilo aparte: ninguna llamada HTTP bloquea el loop principal.
    worker = RecognitionWorker(
        send_fn=lambda b64: auth.post(
            "/face/check-in", {"image_base64": b64}, timeout=ATTEND_TIMEOUT_S
        ),
        timeout_s=ATTEND_TIMEOUT_S,
    )
    worker.start()

    last_submit_ts: float = 0.0
    last_per_emp: dict[str, float] = {}
    last_result:  Optional[dict]   = None
    result_started_at: float = 0.0  # cuando se mostro por primera vez
    result_until: float = 0.0
    result_total_s: float = 0.0     # duracion total del overlay (para animacion)
    transient_msg: Optional[str]   = None
    transient_until: float = 0.0
    # Snapshot de diagnostico — se actualiza con cada respuesta del servidor y se
    # dibuja como panel inferior tipo verify para que NUNCA queden "muerto".
    last_diag: dict | None = None
    last_diag_until: float = 0.0

    print("\n[ATTEND] Modo asistencia activo. Presiona ESC para salir.\n")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame  = cv2.flip(frame, 1)
            fh, fw = frame.shape[:2]
            now_ts = time.time()
            hora   = now_bogota()
            window = time_window()
            fps    = fps_meter.tick()

            # 1) Drena resultados del worker (siempre primero — son baratos).
            while True:
                res = worker.poll()
                if res is None:
                    break
                hr = _handle_recognition_result(res, voter, last_per_emp, hora)
                if hr.overlay is not None:
                    last_result        = hr.overlay
                    result_started_at  = now_ts
                    result_total_s     = hr.overlay_total_s
                    result_until       = hr.overlay_until_ts
                if hr.warn:
                    transient_msg   = hr.warn
                    transient_until = now_ts + 2.0
                # Diagnostico persistente (panel inferior tipo verify).
                last_diag        = hr.diag
                last_diag_until  = now_ts + 4.0

            # 2) Deteccion en frame reducido (el detector se encarga internamente).
            detections = detector.detect(frame)
            primary    = tracker.update(detections, frame.shape)
            extras     = tracker.extra_faces

            q_ok, q_msg = _check_attend_quality(frame, primary)

            # ── Panel superior ───────────────────────────────────────────────
            ov = frame.copy()
            cv2.rectangle(ov, (0, 0), (fw, 60), (14, 14, 14), -1)
            cv2.addWeighted(ov, 0.7, frame, 0.3, 0, frame)
            cv2.putText(
                frame, "RollCall - Asistencia",
                (12, 24), FONT_BOLD, 0.65, C_WHITE, 1, cv2.LINE_AA,
            )
            cv2.putText(
                frame, hora.strftime("%d/%m/%Y  %H:%M:%S"),
                (12, 48), FONT, 0.48, C_GRAY, 1, cv2.LINE_AA,
            )

            win_text = {
                "checkin":  "Ventana: ENTRADA (08:00-12:00)",
                "checkout": "Ventana: SALIDA  (14:00 en adelante)",
                "outside":  "Fuera de horario laboral",
            }[window]
            win_color = {
                "checkin": C_GREEN, "checkout": C_YELLOW, "outside": C_RED,
            }[window]
            put_text_bg(frame, win_text, (fw - 315, 22), fg=win_color, bg=(14, 14, 14))

            # FPS + estado del worker (esquina inferior derecha).
            status = "RX" if worker.busy else "OK"
            fps_color = C_GREEN if fps >= 15 else (C_YELLOW if fps >= 8 else C_RED)
            put_text_bg(
                frame, f"{fps:4.1f} FPS  [{status}]",
                (fw - 140, fh - 12), font_scale=0.45, fg=fps_color, bg=C_BLACK,
            )

            # ── Rostro principal + landmarks ─────────────────────────────────
            if primary is not None:
                x, y, w, h = primary["bbox"]
                color = C_GREEN if q_ok else C_BLUE
                draw_rounded_rect(frame, (x, y), (x + w, y + h), color, 2)
                draw_landmarks(frame, primary["landmarks"], color=color)
                if extras > 0:
                    put_text_bg(
                        frame,
                        f"{extras} rostro(s) ignorado(s) — solo se procesa el principal",
                        (12, fh - 48), fg=C_YELLOW,
                    )

            # ── Overlay resultado ────────────────────────────────────────────
            if last_result and now_ts < result_until:
                elapsed = now_ts - result_started_at
                _draw_result_overlay(
                    frame, last_result, fh, fw,
                    elapsed=elapsed, total=result_total_s,
                )

            # ── Submit al worker — NO bloqueante ─────────────────────────────
            can_submit = (
                q_ok
                and primary is not None
                and not worker.busy
                and (now_ts - last_submit_ts) >= RECOGNITION_EVERY_S
            )

            if can_submit:
                # IMPORTANTE: el pipeline AQUI debe ser IDENTICO al de enroll
                # (align_face_by_eyes con pad=0.40, out_size=256, sin CLAHE).
                # Si aplicas CLAHE solo en attend, el embedding ArcFace queda
                # desplazado ~0.1-0.2 en distancia coseno vs los enrolados ->
                # rechazo sistematico aunque sea la misma persona. ArcFace fue
                # entrenado sobre crops sin ecualizacion adaptativa de canal.
                face_crop = align_face_by_eyes(
                    frame, primary["bbox"], primary["landmarks"],
                    pad=0.40, out_size=256,
                )
                b64 = encode_frame(face_crop, quality=90)
                if worker.submit(b64):
                    last_submit_ts = now_ts
            elif primary is None:
                voter.vote(None)
                if not (last_result and now_ts < result_until):
                    put_text_bg(frame, "Sin rostro detectado", (20, fh - 18), fg=C_GRAY)
            elif not q_ok and q_msg:
                put_text_bg(frame, q_msg, (20, fh - 18), fg=C_ORANGE)

            # Panel de diagnostico persistente (igual filosofia que verify) —
            # SOLO cuando NO esta activo el overlay de exito (para que el
            # check-mark y "PUEDES IRTE" se vean limpios).
            no_success_overlay = not (last_result and now_ts < result_until
                                       and last_result.get("recognized"))
            if (
                no_success_overlay
                and last_diag
                and now_ts < last_diag_until
            ):
                _draw_diag_panel(frame, last_diag, fh, fw)

            # Mensaje transitorio (timeout/connection error).
            if transient_msg and now_ts < transient_until:
                put_text_bg(frame, transient_msg, (20, fh - 70), fg=C_ORANGE)

            cv2.imshow("RollCall - Asistencia", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        worker.stop()
        cap.release()
        cv2.destroyAllWindows()
        print("\n[ATTEND] Sesion cerrada.")


# ══════════════════════════════════════════════════════════════════════════════
# Modo Verify — diagnostico, no marca asistencia
# ══════════════════════════════════════════════════════════════════════════════

def _print_verify_match(data: dict, latency_ms: float) -> None:
    """Imprime en consola los datos del empleado reconocido en modo verify."""
    border = "=" * 72
    now = datetime.now(SCHEDULE_TZ)
    conf = float(data.get("confidence") or 0.0)
    dist = max(0.0, 2.0 * (1.0 - conf))
    print(f"\n{border}")
    print(f"  VERIFY — MATCH    [{now.strftime('%Y-%m-%d %H:%M:%S')} {_SCHEDULE_TZ_STR}]")
    print(border)
    print(f"  Nombre completo : {data.get('full_name') or '—'}")
    print(f"  Codigo empleado : {data.get('employee_code') or '—'}")
    print(f"  ID empleado     : {data.get('employee_id') or '—'}")
    print(f"  Confianza       : {conf:.2%}")
    print(f"  Distancia coseno: {dist:.4f}")
    if data.get("message"):
        print(f"  Mensaje servidor: {data['message']}")
    print(f"  Latencia red    : {latency_ms:.0f} ms")
    print(f"{border}\n")


def run_verify(auth: AuthSession, camera_index: int = -1) -> None:
    """
    Modo diagnostico. Envia el frame a /face/verify (no marca asistencia) y
    muestra en pantalla la distancia coseno al empleado mas cercano, su nombre
    y la confianza. Sirve para calibrar el threshold visualmente:

      - Posicionate enfrente de la camara con luz/angulo normales.
      - Si tu cara aparece reconocida con dist ~0.40-0.55, el threshold actual
        de 0.55 esta bien.
      - Si dist sale > 0.55 con tu cara real, el threshold esta muy estricto o
        falto enrollment con mas variedad de luces/angulos.
      - Si una persona DISTINTA aparece reconocida con dist < threshold,
        el threshold esta muy permisivo (riesgo de falsos positivos).
    """
    cap = open_camera(camera_index)
    detector = make_detector()
    tracker  = FaceTracker()
    fps_meter = FpsMeter()

    worker = RecognitionWorker(
        send_fn=lambda b64: auth.post(
            "/face/verify", {"image_base64": b64}, timeout=ATTEND_TIMEOUT_S
        ),
        timeout_s=ATTEND_TIMEOUT_S,
    )
    worker.start()

    last_submit_ts: float = 0.0
    last_payload: dict[str, Any] | None = None
    last_payload_until: float = 0.0
    last_latency_ms: float = 0.0

    print("\n[VERIFY] Modo diagnostico. ESC para salir.\n")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame  = cv2.flip(frame, 1)
            fh, fw = frame.shape[:2]
            now_ts = time.time()
            fps    = fps_meter.tick()

            # Drena resultados.
            while True:
                res = worker.poll()
                if res is None:
                    break
                last_latency_ms = (res.received_at - res.submitted_at) * 1000.0
                if res.error:
                    last_payload = {"error": res.error}
                else:
                    last_payload = res.payload or {}
                    if last_payload.get("recognized"):
                        _print_verify_match(last_payload, last_latency_ms)
                last_payload_until = now_ts + 3.0

            detections = detector.detect(frame)
            primary    = tracker.update(detections, frame.shape)
            q_ok, q_msg = _check_attend_quality(frame, primary)

            # Panel superior.
            ov = frame.copy()
            cv2.rectangle(ov, (0, 0), (fw, 60), (14, 14, 14), -1)
            cv2.addWeighted(ov, 0.7, frame, 0.3, 0, frame)
            cv2.putText(
                frame, "RollCall - Verify (diagnostico)",
                (12, 26), FONT_BOLD, 0.65, C_CYAN, 1, cv2.LINE_AA,
            )
            cv2.putText(
                frame, "No marca asistencia. Calibracion de threshold.",
                (12, 48), FONT, 0.46, C_GRAY, 1, cv2.LINE_AA,
            )

            # FPS + estado del worker.
            status = "RX" if worker.busy else "OK"
            fps_color = C_GREEN if fps >= 15 else (C_YELLOW if fps >= 8 else C_RED)
            put_text_bg(
                frame, f"{fps:4.1f} FPS  [{status}]  {last_latency_ms:.0f}ms",
                (fw - 230, fh - 12), font_scale=0.45, fg=fps_color, bg=C_BLACK,
            )

            if primary is not None:
                x, y, w, h = primary["bbox"]
                color = C_GREEN if q_ok else C_BLUE
                draw_rounded_rect(frame, (x, y), (x + w, y + h), color, 2)
                draw_landmarks(frame, primary["landmarks"], color=color)

            # Submit.
            can_submit = (
                q_ok
                and primary is not None
                and not worker.busy
                and (now_ts - last_submit_ts) >= RECOGNITION_EVERY_S
            )
            if can_submit:
                face_crop = align_face_by_eyes(
                    frame, primary["bbox"], primary["landmarks"],
                    pad=0.40, out_size=256,
                )
                b64 = encode_frame(face_crop, quality=90)
                if worker.submit(b64):
                    last_submit_ts = now_ts
            elif primary is None:
                put_text_bg(frame, "Sin rostro detectado", (20, fh - 18), fg=C_GRAY)
            elif not q_ok and q_msg:
                put_text_bg(frame, q_msg, (20, fh - 18), fg=C_ORANGE)

            # Overlay de diagnostico.
            if last_payload and now_ts < last_payload_until:
                panel_h = 88
                p = frame.copy()
                cv2.rectangle(p, (0, fh - panel_h), (fw, fh), (16, 16, 16), -1)
                cv2.addWeighted(p, 0.85, frame, 0.15, 0, frame)

                if "error" in last_payload:
                    cv2.putText(
                        frame, f"ERROR: {last_payload['error']}",
                        (16, fh - panel_h + 30),
                        FONT_BOLD, 0.6, C_RED, 1, cv2.LINE_AA,
                    )
                else:
                    recognized = bool(last_payload.get("recognized"))
                    name = last_payload.get("full_name") or "—"
                    conf = float(last_payload.get("confidence") or 0.0)
                    msg  = last_payload.get("message") or ""
                    # dist = 2*(1-conf) si tenemos conf, util como referencia
                    dist = max(0.0, 2.0 * (1.0 - conf)) if conf > 0 else 0.0

                    title_color = C_GREEN if recognized else C_ORANGE
                    title = "MATCH" if recognized else "SIN MATCH"
                    cv2.putText(
                        frame, title, (16, fh - panel_h + 28),
                        FONT_BOLD, 0.7, title_color, 1, cv2.LINE_AA,
                    )
                    cv2.putText(
                        frame, f"Nombre: {name}",
                        (16, fh - panel_h + 52),
                        FONT, 0.5, C_WHITE, 1, cv2.LINE_AA,
                    )
                    cv2.putText(
                        frame,
                        f"Distancia: {dist:.4f}    Confianza: {conf:.2%}",
                        (16, fh - panel_h + 74),
                        FONT, 0.5, C_CYAN, 1, cv2.LINE_AA,
                    )
                    # Mensaje del backend (incluye top votos cuando hay match).
                    if msg:
                        put_text_bg(
                            frame, msg[:80],
                            (fw - 460 if len(msg) > 40 else fw - 260, fh - panel_h + 28),
                            font_scale=0.42, fg=C_GRAY, bg=C_BLACK,
                        )

            cv2.imshow("RollCall - Verify", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        worker.stop()
        cap.release()
        cv2.destroyAllWindows()
        print("\n[VERIFY] Sesion cerrada.")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def prompt_credentials() -> tuple[str, str]:
    user = API_USER or input("Usuario API (email): ").strip()
    pwd  = API_PASSWORD
    if not pwd:
        import getpass
        pwd = getpass.getpass("Contrasena: ")
    return user, pwd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Open Roll Call - Cliente de Camara",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  python camera_client.py enroll 550e8400-e29b-41d4-a716-446655440000\n"
            "  python camera_client.py attend\n"
            "  python camera_client.py attend --camera 1\n"
            "  python camera_client.py verify   # diagnostico, no marca asistencia\n"
        ),
    )
    parser.add_argument("mode", choices=["enroll", "attend", "verify"])
    parser.add_argument("employee_id", nargs="?")
    parser.add_argument("--camera", type=int, default=-1)
    args = parser.parse_args()

    if args.mode == "enroll" and not args.employee_id:
        parser.error("El modo 'enroll' requiere employee_id.")

    # ── Cargar horario activo desde la API (endpoint público, sin token) ─────
    # Si falla (backend caído, sin red) se usan los defaults del módulo.
    load_active_schedule()

    user, pwd = prompt_credentials()
    auth = AuthSession(BASE_URL)
    try:
        auth.login(user, pwd)
    except RuntimeError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] No se puede conectar a {BASE_URL}")
        print("        Verifica que el backend este corriendo: uvicorn app.main:app --reload")
        sys.exit(1)

    try:
        if args.mode == "enroll":
            run_enrollment(args.employee_id, auth, args.camera)
        elif args.mode == "verify":
            run_verify(auth, args.camera)
        else:
            run_attendance(auth, args.camera)
    except RuntimeError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INFO] Interrumpido.")


if __name__ == "__main__":
    main()
