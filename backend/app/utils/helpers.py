"""
Funções auxiliares
"""
import base64
import numpy as np
from typing import Optional
import os


def frame_to_base64(frame: np.ndarray, format: str = "jpeg") -> str:
    """
    Converte frame numpy para string base64
    
    Args:
        frame: Frame de vídeo (numpy array BGR)
        format: Formato de imagem (jpeg, png)
    
    Returns:
        String base64 da imagem
    """
    import cv2
    try:
        if format == "jpeg":
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        else:
            _, buffer = cv2.imencode('.png', frame)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception:
        return ""


def base64_to_frame(base64_string: str) -> Optional[np.ndarray]:
    """
    Converte string base64 para frame numpy
    
    Args:
        base64_string: String base64 da imagem
    
    Returns:
        Frame de vídeo ou None
    """
    import cv2
    try:
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception:
        return None


def get_file_extension(filename: str) -> str:
    """
    Retorna extensão do arquivo em minúsculas
    
    Args:
        filename: Nome do arquivo
    
    Returns:
        Extensão sem ponto
    """
    if "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


def ensure_dir(directory: str) -> bool:
    """
    Garante que diretório existe, criando se necessário
    
    Args:
        directory: Caminho do diretório
    
    Returns:
        True se existe ou foi criado
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception:
        return False


def calculate_iou(box1: list, box2: list) -> float:
    """
    Calcula Intersection over Union entre duas bounding boxes
    
    Args:
        box1: [x1, y1, x2, y2]
        box2: [x1, y1, x2, y2]
    
    Returns:
        Valor IoU entre 0 e 1
    """
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    union = area1 + area2 - intersection
    
    if union == 0:
        return 0
    
    return intersection / union


def format_timestamp(seconds: float) -> str:
    """
    Formata segundos em timestamp HH:MM:SS
    
    Args:
        seconds: Tempo em segundos
    
    Returns:
        String formatada
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
