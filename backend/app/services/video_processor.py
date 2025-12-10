"""
Serviço de processamento de vídeo
"""
import numpy as np
import cv2
from typing import Generator, Optional
from app.config import FRAME_RESIZE_WIDTH, FRAME_RESIZE_HEIGHT


class VideoProcessor:
    """
    Processador de vídeos para análise de EPIs
    """
    
    def __init__(self):
        self.cap = None
        self.frame_count = 0
        self.fps = 0
        self.width = 0
        self.height = 0
    
    def open_file(self, file_path: str) -> bool:
        """
        Abre arquivo de vídeo para processamento
        
        Args:
            file_path: Caminho do arquivo de vídeo
        
        Returns:
            True se aberto com sucesso
        """
        try:
            self.cap = cv2.VideoCapture(file_path)
            if not self.cap.isOpened():
                return False
                
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            return True
        except Exception as e:
            print(f"Erro ao abrir vídeo: {e}")
            return False
    
    def get_frames(self) -> Generator[np.ndarray, None, None]:
        """
        Generator que retorna frames do vídeo
        
        Yields:
            Frame de vídeo (numpy array BGR)
        """
        if not self.cap or not self.cap.isOpened():
            return
            
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Redimensionar se necessário
            if self.width > FRAME_RESIZE_WIDTH or self.height > FRAME_RESIZE_HEIGHT:
                frame = self.resize_frame(frame, FRAME_RESIZE_WIDTH, FRAME_RESIZE_HEIGHT)
                
            yield frame
            
        self.release()
    
    def resize_frame(self, frame: np.ndarray, width: int = None, height: int = None) -> np.ndarray:
        """
        Redimensiona frame para tamanho especificado mantendo aspect ratio
        
        Args:
            frame: Frame original
            width: Largura desejada
            height: Altura desejada
        
        Returns:
            Frame redimensionado
        """
        if frame is None:
            return None
            
        h, w = frame.shape[:2]
        
        if width is None and height is None:
            return frame
            
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))
            
        return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    
    def release(self):
        """Libera recursos do vídeo"""
        if self.cap:
            self.cap.release()
            self.cap = None
    
    @property
    def video_info(self) -> dict:
        """Retorna informações do vídeo"""
        return {
            "frame_count": self.frame_count,
            "fps": self.fps,
            "width": self.width,
            "height": self.height
        }
