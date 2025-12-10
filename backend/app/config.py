"""
Configurações da aplicação
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do Servidor
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Configurações CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:8080,http://127.0.0.1:8080").split(",")

# Configurações do Modelo YOLO
MODEL_PATH = os.getenv("MODEL_PATH", "models/ppe.pt")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.5))

# Configurações de Vídeo
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 500 * 1024 * 1024))  # 500MB
ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm"}
FRAME_RESIZE_WIDTH = int(os.getenv("FRAME_RESIZE_WIDTH", 640))
FRAME_RESIZE_HEIGHT = int(os.getenv("FRAME_RESIZE_HEIGHT", 640))

# Configurações de Streaming
STREAM_RECONNECT_ATTEMPTS = int(os.getenv("STREAM_RECONNECT_ATTEMPTS", 3))
STREAM_RECONNECT_DELAY = int(os.getenv("STREAM_RECONNECT_DELAY", 5))
STREAM_BUFFER_SIZE = int(os.getenv("STREAM_BUFFER_SIZE", 30))

# Classes do modelo YOLO (conforme repositório de referência)
YOLO_CLASSES = [
    'Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 
    'NO-Safety Vest', 'Person', 'Safety Cone', 
    'Safety Vest', 'machinery', 'vehicle'
]

ALERT_CLASSES = ['NO-Hardhat', 'NO-Mask', 'NO-Safety Vest']
POSITIVE_CLASSES = ['Hardhat', 'Mask', 'Safety Vest']
