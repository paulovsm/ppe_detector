"""
Serviço de suavização de detecções (Debouncing/Tracking)
"""
import numpy as np
from app.utils.helpers import calculate_iou


class DetectionSmoother:
    """
    Implementa rastreamento simples e suavização para evitar 'flickering' nas detecções.
    
    Funcionalidades:
    1. Debouncing: Só mostra detecção após N frames consecutivos (min_hits)
    2. Persistência: Mantém detecção por M frames após perda (max_disappeared)
    3. Associação: Usa IoU para associar detecções entre frames
    """
    
    def __init__(self, max_disappeared: int = 5, min_hits: int = 3, iou_threshold: float = 0.3):
        self.next_object_id = 0
        self.objects = {}  # id -> {bbox, class_name, confidence, hits, missing}
        self.max_disappeared = max_disappeared
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold

    def update(self, detections: list) -> list:
        """
        Atualiza o estado do rastreador com novas detecções
        
        Args:
            detections: Lista de dicts {'bbox': [], 'class_name': '', 'confidence': float}
            
        Returns:
            Lista de detecções suavizadas
        """
        # Se não há detecções novas
        if len(detections) == 0:
            for obj_id in list(self.objects.keys()):
                self.objects[obj_id]['missing'] += 1
                if self.objects[obj_id]['missing'] > self.max_disappeared:
                    self.deregister(obj_id)
            return self.get_active_objects()

        # Se não há objetos rastreados
        if len(self.objects) == 0:
            for det in detections:
                self.register(det)
            return self.get_active_objects()

        # Associar objetos existentes com novas detecções
        object_ids = list(self.objects.keys())
        object_bboxes = [self.objects[obj_id]['bbox'] for obj_id in object_ids]
        
        # Matriz de IoU (Linhas: Objetos, Colunas: Detecções)
        iou_matrix = np.zeros((len(object_ids), len(detections)))
        for i, obj_bbox in enumerate(object_bboxes):
            for j, det in enumerate(detections):
                iou_matrix[i, j] = calculate_iou(obj_bbox, det['bbox'])

        # Matching guloso (Greedy)
        # Encontrar pares com maior IoU
        candidates = []
        for i in range(len(object_ids)):
            for j in range(len(detections)):
                if iou_matrix[i, j] >= self.iou_threshold:
                    candidates.append((i, j, iou_matrix[i, j]))
        
        # Ordenar por IoU decrescente
        candidates.sort(key=lambda x: x[2], reverse=True)
        
        used_rows = set()
        used_cols = set()
        
        for r, c, iou in candidates:
            if r in used_rows or c in used_cols:
                continue
                
            obj_id = object_ids[r]
            
            # Verificar consistência de classe (opcional, mas recomendado para evitar trocas)
            # Se a classe mudar, tratamos como novo objeto ou atualização?
            # Para evitar flickering de classe, idealmente mantemos a classe original ou usamos votação.
            # Aqui vamos permitir atualização se for a mesma classe, senão ignoramos o match (tratando como novo obj)
            if self.objects[obj_id]['class_name'] == detections[c]['class_name']:
                self.objects[obj_id]['bbox'] = detections[c]['bbox']
                self.objects[obj_id]['confidence'] = detections[c]['confidence']
                self.objects[obj_id]['hits'] += 1
                self.objects[obj_id]['missing'] = 0
                
                used_rows.add(r)
                used_cols.add(c)
        
        # Tratar objetos não pareados (Missing)
        for i in range(len(object_ids)):
            if i not in used_rows:
                obj_id = object_ids[i]
                self.objects[obj_id]['missing'] += 1
                if self.objects[obj_id]['missing'] > self.max_disappeared:
                    self.deregister(obj_id)
                    
        # Tratar detecções não pareadas (Novos objetos)
        for i in range(len(detections)):
            if i not in used_cols:
                self.register(detections[i])
                
        return self.get_active_objects()

    def register(self, detection):
        """Registra novo objeto"""
        self.objects[self.next_object_id] = {
            'bbox': detection['bbox'],
            'class_name': detection['class_name'],
            'confidence': detection['confidence'],
            'hits': 1,
            'missing': 0
        }
        self.next_object_id += 1

    def deregister(self, obj_id):
        """Remove objeto do rastreamento"""
        del self.objects[obj_id]

    def get_active_objects(self) -> list:
        """Retorna objetos ativos (que satisfazem critérios de exibição)"""
        active = []
        for obj in self.objects.values():
            # Critério: Ter sido detectado pelo menos min_hits vezes
            # E não ter desaparecido por completo (embora se missing > 0 e < max, ainda mostramos)
            if obj['hits'] >= self.min_hits:
                 active.append({
                     'bbox': obj['bbox'],
                     'class_name': obj['class_name'],
                     'confidence': obj['confidence']
                 })
        return active
