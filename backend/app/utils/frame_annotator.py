"""
Utilitário para anotação de frames com bounding boxes
"""
import numpy as np
import cv2
from typing import List, Tuple


class FrameAnnotator:
    """
    Responsável por desenhar bounding boxes e labels nos frames
    
    Esquema de cores baseado no código de referência:
    https://github.com/Vinayakmane47/PPE_detection_YOLO/blob/main/YOLO_Video.py
    """
    
    # Cores em BGR (formato OpenCV)
    COLORS = {
        'Hardhat': (0, 255, 0),         # Verde - EPI presente
        'Safety Vest': (0, 255, 0),     # Verde
        'Mask': (0, 255, 0),            # Verde
        'NO-Hardhat': (0, 0, 255),      # Vermelho - Alerta (violação)
        'NO-Safety Vest': (0, 0, 255),  # Vermelho - Alerta (violação)
        'NO-Mask': (0, 0, 255),         # Vermelho - Alerta (violação)
        'Person': (255, 45, 85),        # Rosa/Magenta
        'Safety Cone': (255, 165, 0),   # Laranja
        'machinery': (255, 149, 0),     # Laranja claro
        'vehicle': (255, 149, 0),       # Laranja claro
    }
    
    DEFAULT_COLOR = (128, 128, 128)  # Cinza para classes desconhecidas
    
    def __init__(self):
        self.font_scale = 0.6
        self.font_thickness = 2
        self.box_thickness = 2
        self.font = cv2.FONT_HERSHEY_SIMPLEX
    
    def annotate(
        self, 
        frame: np.ndarray, 
        detections: List[dict],
        show_labels: bool = True,
        show_confidence: bool = True
    ) -> np.ndarray:
        """
        Desenha bounding boxes e labels no frame
        
        Args:
            frame: Frame de vídeo (numpy array BGR)
            detections: Lista de detecções com class_name, confidence, bbox
            show_labels: Mostrar labels das classes
            show_confidence: Mostrar valores de confiança
        
        Returns:
            Frame anotado
        """
        annotated = frame.copy()
        
        for det in detections:
            class_name = det.get('class_name', 'Unknown')
            confidence = det.get('confidence', 0.0)
            bbox = det.get('bbox', [])
            
            if len(bbox) != 4:
                continue
                
            x1, y1, x2, y2 = bbox
            color = self.COLORS.get(class_name, self.DEFAULT_COLOR)
            
            # Desenhar retângulo
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, self.box_thickness)
            
            if show_labels:
                label = class_name
                if show_confidence:
                    label += f" {confidence:.2f}"
                
                # Tamanho do texto para fundo
                (w, h), _ = cv2.getTextSize(label, self.font, self.font_scale, self.font_thickness)
                
                # Fundo do texto
                cv2.rectangle(annotated, (x1, y1 - 20), (x1 + w, y1), color, -1)
                
                # Texto
                text_color = (255, 255, 255) if sum(color) < 400 else (0, 0, 0)
                cv2.putText(annotated, label, (x1, y1 - 5), self.font, self.font_scale, text_color, self.font_thickness)
                
        return annotated
    
    def draw_alert_overlay(
        self, 
        frame: np.ndarray, 
        violations: List[dict],
        alpha: float = 0.3
    ) -> np.ndarray:
        """
        Adiciona overlay de alerta quando há violações
        
        Args:
            frame: Frame de vídeo
            violations: Lista de violações detectadas
            alpha: Transparência do overlay
        
        Returns:
            Frame com overlay de alerta
        """
        if not violations:
            return frame
            
        overlay = frame.copy()
        h, w = frame.shape[:2]
        
        # Desenhar borda vermelha grossa
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 255), 20)
        
        # Adicionar texto de alerta piscante (simulado aqui apenas com texto fixo)
        text = f"ALERTA: {len(violations)} VIOLACOES DETECTADAS"
        (tw, th), _ = cv2.getTextSize(text, self.font, 1.0, 2)
        
        cv2.rectangle(overlay, (w//2 - tw//2 - 10, 50 - th - 10), (w//2 + tw//2 + 10, 50 + 10), (0, 0, 255), -1)
        cv2.putText(overlay, text, (w//2 - tw//2, 50), self.font, 1.0, (255, 255, 255), 2)
        
        # Aplicar transparência
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
    
    def add_stats_overlay(
        self, 
        frame: np.ndarray, 
        stats: dict,
        position: str = "top-left"
    ) -> np.ndarray:
        """
        Adiciona overlay com estatísticas no frame
        
        Args:
            frame: Frame de vídeo
            stats: Estatísticas para exibir
            position: Posição do overlay
        
        Returns:
            Frame com overlay de estatísticas
        """
        overlay = frame.copy()
        
        lines = [
            f"Total Detections: {stats.get('total_detections', 0)}",
            f"Violations: {stats.get('violations_count', 0)}",
            f"FPS: {stats.get('fps', 0):.1f}"
        ]
        
        x, y = 10, 30
        
        for line in lines:
            # Fundo semi-transparente para texto
            (w, h), _ = cv2.getTextSize(line, self.font, 0.6, 1)
            cv2.rectangle(overlay, (x - 5, y - h - 5), (x + w + 5, y + 5), (0, 0, 0), -1)
            
            cv2.putText(overlay, line, (x, y), self.font, 0.6, (255, 255, 255), 1)
            y += 30
            
        # Aplicar transparência apenas no fundo do texto seria ideal, mas aqui aplicamos direto
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        return frame
import numpy as np
from typing import List, Tuple


class FrameAnnotator:
    """
    Responsável por desenhar bounding boxes e labels nos frames
    
    Esquema de cores baseado no código de referência:
    https://github.com/Vinayakmane47/PPE_detection_YOLO/blob/main/YOLO_Video.py
    """
    
    # Cores em BGR (formato OpenCV)
    COLORS = {
        'Hardhat': (0, 255, 0),         # Verde - EPI presente
        'Safety Vest': (0, 255, 0),     # Verde
        'Mask': (0, 255, 0),            # Verde
        'NO-Hardhat': (0, 0, 255),      # Vermelho - Alerta (violação)
        'NO-Safety Vest': (0, 0, 255),  # Vermelho - Alerta (violação)
        'NO-Mask': (0, 0, 255),         # Vermelho - Alerta (violação)
        'Person': (255, 45, 85),        # Rosa/Magenta
        'Safety Cone': (255, 165, 0),   # Laranja
        'machinery': (255, 149, 0),     # Laranja claro
        'vehicle': (255, 149, 0),       # Laranja claro
    }
    
    DEFAULT_COLOR = (128, 128, 128)  # Cinza para classes desconhecidas
    
    def __init__(self):
        self.font_scale = 0.6
        self.font_thickness = 2
        self.box_thickness = 2
    
    def annotate(
        self, 
        frame: np.ndarray, 
        detections: List[dict],
        show_labels: bool = True,
        show_confidence: bool = True
    ) -> np.ndarray:
        """
        Desenha bounding boxes e labels no frame
        
        Args:
            frame: Frame de vídeo (numpy array BGR)
            detections: Lista de detecções com class_name, confidence, bbox
            show_labels: Mostrar labels das classes
            show_confidence: Mostrar valores de confiança
        
        Returns:
            Frame anotado
        """
        # Será implementado completamente na Fase 2
        # import cv2
        # annotated = frame.copy()
        # for det in detections:
        #     color = self.COLORS.get(det['class_name'], self.DEFAULT_COLOR)
        #     x1, y1, x2, y2 = det['bbox']
        #     cv2.rectangle(annotated, (x1, y1), (x2, y2), color, self.box_thickness)
        #     ...
        return frame
    
    def draw_alert_overlay(
        self, 
        frame: np.ndarray, 
        violations: List[dict],
        alpha: float = 0.3
    ) -> np.ndarray:
        """
        Adiciona overlay de alerta quando há violações
        
        Args:
            frame: Frame de vídeo
            violations: Lista de violações detectadas
            alpha: Transparência do overlay
        
        Returns:
            Frame com overlay de alerta
        """
        # Será implementado na Fase 2
        return frame
    
    def add_stats_overlay(
        self, 
        frame: np.ndarray, 
        stats: dict,
        position: str = "top-left"
    ) -> np.ndarray:
        """
        Adiciona overlay com estatísticas no frame
        
        Args:
            frame: Frame de vídeo
            stats: Estatísticas para exibir
            position: Posição do overlay
        
        Returns:
            Frame com overlay de estatísticas
        """
        # Será implementado na Fase 2
        return frame
    
    def get_color(self, class_name: str) -> Tuple[int, int, int]:
        """
        Retorna cor para uma classe
        
        Args:
            class_name: Nome da classe
        
        Returns:
            Tupla BGR
        """
        return self.COLORS.get(class_name, self.DEFAULT_COLOR)
