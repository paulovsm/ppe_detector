"""
Serviço de detecção de EPIs usando YOLOv8
"""
import numpy as np
from typing import List, Optional
import time
from ultralytics import YOLO
from app.config import MODEL_PATH, CONFIDENCE_THRESHOLD, YOLO_CLASSES, ALERT_CLASSES, POSITIVE_CLASSES


class PPEDetector:
    """
    Serviço de detecção de EPIs usando YOLOv8
    
    Utiliza o modelo pré-treinado do repositório de referência:
    https://github.com/Vinayakmane47/PPE_detection_YOLO
    """
    
    CLASSES = YOLO_CLASSES
    ALERT_CLASSES = ALERT_CLASSES
    POSITIVE_CLASSES = POSITIVE_CLASSES
    DEFAULT_MODEL_PATH = MODEL_PATH
    
    def __init__(self, model_path: str = None):
        """
        Inicializa o detector com o modelo YOLO
        
        Args:
            model_path: Caminho para o arquivo de pesos do modelo (ppe.pt)
        """
        self.model_path = model_path or self.DEFAULT_MODEL_PATH
        self.model = None
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        self._model_loaded = False
    
    def load_model(self):
        """
        Carrega o modelo YOLO
        """
        if not self._model_loaded:
            try:
                self.model = YOLO(self.model_path)
                self._model_loaded = True
                print(f"Modelo carregado com sucesso: {self.model_path}")
            except Exception as e:
                print(f"Erro ao carregar modelo: {e}")
                raise e
    
    @property
    def is_loaded(self) -> bool:
        """Verifica se o modelo está carregado"""
        return self._model_loaded
    
    def detect(
        self, 
        frame: np.ndarray, 
        selected_classes: List[str] = None,
        confidence_threshold: float = None
    ) -> dict:
        """
        Executa inferência no frame e retorna detecções filtradas
        
        Args:
            frame: Frame de vídeo (numpy array BGR)
            selected_classes: Lista de classes para filtrar
            confidence_threshold: Threshold de confiança (padrão: 0.5)
        
        Returns:
            dict com detecções, violações e estatísticas
        """
        if not self.is_loaded:
            self.load_model()
            
        conf = confidence_threshold or self.confidence_threshold
        start_time = time.time()
        
        # Executar inferência
        results = self.model(frame, conf=conf, verbose=False)
        
        detections = []
        
        # Processar resultados
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Bounding Box
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                bbox = [int(x1), int(y1), int(x2), int(y2)]
                
                # Confiança
                confidence = float(box.conf[0])
                
                # Classe
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id]
                
                # Mapear nomes de classes se necessário (garantir compatibilidade)
                # O modelo pode retornar nomes ligeiramente diferentes, mas assumimos que bate com YOLO_CLASSES
                
                detection = {
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": bbox
                }
                
                detections.append(detection)
        
        # Filtrar por classes selecionadas
        if selected_classes:
            detections = self.filter_by_classes(detections, selected_classes)
            
        # Identificar violações
        violations = self.get_violations(detections)
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "detections": detections,
            "violations": violations,
            "stats": {
                "total_detections": len(detections),
                "violations_count": len(violations),
                "processing_time_ms": processing_time
            }
        }
    
    def get_violations(self, detections: List[dict]) -> List[dict]:
        """
        Retorna lista de violações detectadas (ausência de EPIs)
        
        Args:
            detections: Lista de detecções
        
        Returns:
            Lista de violações
        """
        violations = []
        for detection in detections:
            if detection.get("class_name") in self.ALERT_CLASSES:
                violations.append(detection)
        return violations
    
    def filter_by_classes(self, detections: List[dict], selected_classes: List[str]) -> List[dict]:
        """
        Filtra detecções pelas classes selecionadas
        
        Args:
            detections: Lista de detecções
            selected_classes: Classes para manter
        
        Returns:
            Lista filtrada de detecções
        """
        if not selected_classes:
            return detections
        return [d for d in detections if d.get("class_name") in selected_classes]
