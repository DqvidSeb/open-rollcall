#!/usr/bin/env python3
"""
RollCall — Cliente de Cámara
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
import sys
import time
from collections import deque
from datetime import datetime
from typing import Optional
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
BOGOTA_TZ    = ZoneInfo("America/Bogota")

# Ventanas horarias Colombia
CHECKIN_START  = 8
CHECKIN_END    = 12
CHECKOUT_START = 14
CHECKOUT_END   = 18

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
RECOGNITION_EVERY_S   = 1.2    # intervalo mínimo entre llamadas al servidor
CONFIDENCE_MIN        = 0.55   # confianza mínima cliente (servidor ya filtra por distancia)
ATTEND_TIMEOUT_S      = 20     # timeout HTTP para check-in
ATTEND_BLUR_MIN       = 22.0   # nitidez mínima para enviar al servidor
ATTEND_FACE_AREA_MIN  = 0.03   # 3% del frame
ATTEND_EYE_DIST_MIN   = 28     # px
VOTE_NEEDED           = 2      # reconocimientos consecutivos antes de registrar
VOTE_WINDOW           = 3      # tamaño de la ventana de votación

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


def apply_clahe(gray: np.ndarray) -> np.ndarray:
    """Ecualización adaptativa de contraste (CLAHE) — normaliza iluminación."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


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
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
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

        if self._input_size != (w, h):
            self._detector.setInputSize((w, h))
            self._input_size = (w, h)

        _ok, faces = self._detector.detect(frame_bgr)

        if faces is None or len(faces) == 0:
            return []

        out: list[Detection] = []

        for face in faces:
            x, y, bw, bh = face[:4]
            score = float(face[14])

            x = max(0, int(x))
            y = max(0, int(y))
            bw = min(w - x, int(bw))
            bh = min(h - y, int(bh))

            if bw <= 0 or bh <= 0:
                continue

            # YuNet: right_eye, left_eye, nose, right_mouth, left_mouth
            landmarks = [
                (int(face[4]), int(face[5])),
                (int(face[6]), int(face[7])),
                (int(face[8]), int(face[9])),
                (int((face[10] + face[12]) / 2), int((face[11] + face[13]) / 2)),
                (int(face[10]), int(face[11])),
                (int(face[12]), int(face[13])),
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

def open_camera(index: int = -1) -> cv2.VideoCapture:
    indices = [index] if index >= 0 else list(range(5))
    for i in indices:
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)
            # Buffer pequeno => menor latencia (sino los frames se acumulan)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            print(f"[CAM] Camara abierta en indice {i}.")
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

                    cv2.imshow("RollCall — Enrollment", cf)
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

        cv2.imshow("RollCall — Enrollment", frame)
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
# Modo Asistencia
# ══════════════════════════════════════════════════════════════════════════════

def now_bogota() -> datetime:
    return datetime.now(BOGOTA_TZ)


def time_window() -> str:
    h = now_bogota().hour
    if CHECKIN_START <= h < CHECKIN_END:
        return "checkin"
    if CHECKOUT_START <= h < CHECKOUT_END:
        return "checkout"
    return "outside"


def _draw_result_overlay(frame: np.ndarray, result: dict, h: int, w: int) -> None:
    if result.get("recognized"):
        event = result.get("event_type", "check_in")
        color = C_GREEN if event == "check_in" else C_YELLOW
        icon  = "ENTRADA" if event == "check_in" else "SALIDA"
        name  = result.get("full_name", "")
        code  = result.get("employee_code", "")
        conf  = result.get("confidence", 0.0)

        panel_h = 82
        ov = frame.copy()
        cv2.rectangle(ov, (0, h - panel_h), (w, h), (18, 18, 18), -1)
        cv2.addWeighted(ov, 0.8, frame, 0.2, 0, frame)
        cv2.line(frame, (0, h - panel_h), (w, h - panel_h), color, 2)

        cv2.putText(frame, icon, (16, h - panel_h + 30), FONT_BOLD, 0.9, color, 1, cv2.LINE_AA)
        cv2.putText(frame, name, (120, h - panel_h + 28), FONT_BOLD, 0.7, C_WHITE, 1, cv2.LINE_AA)
        cv2.putText(frame, f"Codigo: {code}", (120, h - panel_h + 52), FONT, 0.5, C_GRAY, 1, cv2.LINE_AA)
        cv2.putText(frame, f"Confianza: {conf:.1%}", (w - 185, h - panel_h + 30), FONT, 0.5, color, 1, cv2.LINE_AA)
    else:
        ov = frame.copy()
        cv2.rectangle(ov, (0, h - 48), (w, h), (20, 20, 40), -1)
        cv2.addWeighted(ov, 0.8, frame, 0.2, 0, frame)
        cv2.line(frame, (0, h - 48), (w, h - 48), C_RED, 2)
        cv2.putText(frame, "Rostro no reconocido", (16, h - 16), FONT_BOLD, 0.65, C_RED, 1, cv2.LINE_AA)


def run_attendance(auth: AuthSession, camera_index: int = -1) -> None:
    cap = open_camera(camera_index)
    detector = make_detector()
    tracker  = FaceTracker()
    voter    = ConsecutiveVoter(needed=VOTE_NEEDED, window=VOTE_WINDOW)

    last_call_ts: float = 0.0
    last_per_emp: dict[str, float] = {}
    last_result:  Optional[dict]  = None
    result_until: float = 0.0

    print("\n[ATTEND] Modo asistencia activo. Presiona ESC para salir.\n")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame  = cv2.flip(frame, 1)
        fh, fw = frame.shape[:2]
        now_ts = time.time()
        hora   = now_bogota()
        window = time_window()

        detections = detector.detect(frame)
        primary    = tracker.update(detections, frame.shape)
        extras     = tracker.extra_faces

        q_ok, q_msg = _check_attend_quality(frame, primary)

        # ── Panel superior ─────────────────────────────────────────────────────
        ov = frame.copy()
        cv2.rectangle(ov, (0, 0), (fw, 60), (14, 14, 14), -1)
        cv2.addWeighted(ov, 0.7, frame, 0.3, 0, frame)
        cv2.putText(frame, "RollCall — Asistencia", (12, 24), FONT_BOLD, 0.65, C_WHITE, 1, cv2.LINE_AA)
        cv2.putText(frame, hora.strftime("%d/%m/%Y  %H:%M:%S"), (12, 48), FONT, 0.48, C_GRAY, 1, cv2.LINE_AA)

        win_text = {
            "checkin":  "Ventana: ENTRADA (08:00-12:00)",
            "checkout": "Ventana: SALIDA  (14:00-18:00)",
            "outside":  "Fuera de horario laboral",
        }[window]
        win_color = {
            "checkin": C_GREEN, "checkout": C_YELLOW, "outside": C_RED,
        }[window]
        put_text_bg(frame, win_text, (fw - 315, 22), fg=win_color, bg=(14, 14, 14))

        # ── Rostro principal + landmarks ───────────────────────────────────────
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

        # ── Overlay resultado ──────────────────────────────────────────────────
        if last_result and now_ts < result_until:
            _draw_result_overlay(frame, last_result, fh, fw)

        # ── Reconocimiento ─────────────────────────────────────────────────────
        can_call = q_ok and (now_ts - last_call_ts) >= RECOGNITION_EVERY_S and primary is not None

        if can_call:
            last_call_ts = now_ts
            face_crop = align_face_by_eyes(
                frame, primary["bbox"], primary["landmarks"],
                pad=0.40, out_size=256,
            )
            face_proc = preprocess_for_recognition(face_crop)
            b64       = encode_frame(face_proc, quality=90)

            try:
                resp = auth.post("/face/check-in", {"image_base64": b64}, timeout=ATTEND_TIMEOUT_S)

                if resp.status_code in (200, 201):
                    data       = resp.json()
                    emp_id     = str(data.get("employee_id", ""))
                    confidence = data.get("confidence") or 0.0
                    full_name  = data.get("full_name") or "—"
                    code       = data.get("employee_code") or "—"
                    event      = data.get("event_type", "check_in")

                    # /check-in solo responde 201 cuando hubo reconocimiento;
                    # filtramos adicionalmente por confianza minima del cliente.
                    if emp_id and confidence >= CONFIDENCE_MIN:
                        consensus = voter.vote(emp_id)
                        pending_result = {
                            "recognized": True,
                            "employee_id": emp_id,
                            "full_name": full_name,
                            "employee_code": code,
                            "event_type": event,
                            "confidence": confidence,
                        }

                        if consensus:
                            cooldown_ok = (now_ts - last_per_emp.get(emp_id, 0)) >= COOLDOWN_S
                            if cooldown_ok:
                                last_per_emp[emp_id] = now_ts
                                last_result  = pending_result
                                result_until = now_ts + 5.0
                                voter.reset()
                                icon = "→ ENTRADA" if event == "check_in" else "← SALIDA"
                                print(
                                    f"[{hora.strftime('%H:%M:%S')}] {icon}  "
                                    f"{full_name}  cod:{code}  "
                                    f"confianza:{confidence:.1%}"
                                )
                    else:
                        voter.vote(None)

                elif resp.status_code in (404, 422):
                    voter.vote(None)
                    last_result  = {"recognized": False}
                    result_until = now_ts + 1.5

                elif resp.status_code == 503:
                    put_text_bg(frame, "Servidor sin DeepFace", (20, fh - 20), fg=C_RED)

            except requests.exceptions.ReadTimeout:
                put_text_bg(frame, "Servidor lento — timeout", (20, fh - 20), fg=C_ORANGE)
            except requests.exceptions.ConnectionError:
                put_text_bg(frame, f"Sin conexion a {BASE_URL}", (20, fh - 20), fg=C_RED)

        elif primary is None:
            voter.vote(None)
            put_text_bg(frame, "Sin rostro detectado", (20, fh - 18), fg=C_GRAY)
        elif not q_ok and q_msg:
            put_text_bg(frame, q_msg, (20, fh - 18), fg=C_ORANGE)

        cv2.imshow("RollCall — Asistencia", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n[ATTEND] Sesion cerrada.")


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
        description="RollCall — Cliente de Camara",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  python camera_client.py enroll 550e8400-e29b-41d4-a716-446655440000\n"
            "  python camera_client.py attend\n"
            "  python camera_client.py attend --camera 1\n"
        ),
    )
    parser.add_argument("mode", choices=["enroll", "attend"])
    parser.add_argument("employee_id", nargs="?")
    parser.add_argument("--camera", type=int, default=-1)
    args = parser.parse_args()

    if args.mode == "enroll" and not args.employee_id:
        parser.error("El modo 'enroll' requiere employee_id.")

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
        else:
            run_attendance(auth, args.camera)
    except RuntimeError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INFO] Interrumpido.")


if __name__ == "__main__":
    main()
