"""
Gerenciador de alertas de violações de EPI
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid
from app.config import ALERT_CLASSES


class AlertManager:
    """
    Gerenciador de alertas para violações de EPI
    """
    
    def __init__(self, cooldown_seconds: float = 5.0):
        self.alerts: List[dict] = []
        self.alert_classes = ALERT_CLASSES
        self.max_alerts = 1000  # Limite de alertas em memória
        self.cooldown_seconds = cooldown_seconds
        self.last_alerts: Dict[str, datetime] = {}  # violation_type -> last_time
    
    def process_violations(self, violations: List[dict], frame_number: int = None) -> List[dict]:
        """
        Processa lista de violações e gera alertas respeitando cooldown
        
        Args:
            violations: Lista de violações detectadas no frame
            frame_number: Número do frame atual
            
        Returns:
            Lista de novos alertas gerados
        """
        new_alerts = []
        current_time = datetime.now()
        
        for violation in violations:
            violation_type = violation.get("class_name")
            
            # Verificar cooldown
            if self.should_alert(violation_type, current_time):
                alert = self.create_alert(
                    violation_class=violation_type,
                    confidence=violation.get("confidence", 0.0),
                    bbox=violation.get("bbox"),
                    frame_number=frame_number,
                    timestamp=current_time.isoformat()
                )
                self.add_alert(alert)
                new_alerts.append(alert)
                self.last_alerts[violation_type] = current_time
                
        return new_alerts

    def should_alert(self, violation_type: str, current_time: datetime) -> bool:
        """Verifica se deve gerar alerta baseado no cooldown"""
        if violation_type not in self.last_alerts:
            return True
            
        time_diff = (current_time - self.last_alerts[violation_type]).total_seconds()
        return time_diff >= self.cooldown_seconds

    def add_alert(self, alert: dict):
        """Adiciona alerta ao histórico"""
        self.alerts.insert(0, alert)  # Mais recente primeiro
        if len(self.alerts) > self.max_alerts:
            self.alerts.pop()

    def get_recent_alerts(self, limit: int = 10) -> List[dict]:
        """Retorna alertas mais recentes"""
        return self.alerts[:limit]

    def create_alert(
        self, 
        violation_class: str, 
        confidence: float,
        bbox: List[int],
        frame_number: int = None,
        timestamp: str = None
    ) -> dict:
        """
        Cria um objeto de alerta (sem salvar)
        """
        return {
            "id": str(uuid.uuid4()), # Use UUID for unique IDs
            "class": violation_class,
            "confidence": round(confidence, 2),
            "bbox": bbox,
            "frame_number": frame_number,
            "timestamp": timestamp or datetime.now().isoformat(),
            "severity": self._get_severity(violation_class),
            "acknowledged": False
        }
    
    def _get_severity(self, violation_class: str) -> str:
        """
        Determina severidade do alerta
        
        Args:
            violation_class: Classe da violação
        
        Returns:
            Nível de severidade (high, medium, low)
        """
        high_severity = ['NO-Hardhat']
        medium_severity = ['NO-Safety Vest']
        
        if violation_class in high_severity:
            return "high"
        elif violation_class in medium_severity:
            return "medium"
        return "low"
    
    def get_alerts(
        self, 
        limit: int = 50, 
        severity: str = None,
        unacknowledged_only: bool = False
    ) -> List[dict]:
        """
        Retorna lista de alertas
        
        Args:
            limit: Número máximo de alertas
            severity: Filtrar por severidade
            unacknowledged_only: Apenas não reconhecidos
        
        Returns:
            Lista de alertas
        """
        alerts = self.alerts.copy()
        
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
        
        if unacknowledged_only:
            alerts = [a for a in alerts if not a["acknowledged"]]
        
        return alerts[-limit:][::-1]  # Mais recentes primeiro
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """
        Marca alerta como reconhecido
        
        Args:
            alert_id: ID do alerta
        
        Returns:
            True se reconhecido com sucesso
        """
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                return True
        return False
    
    def get_stats(self) -> dict:
        """
        Retorna estatísticas dos alertas
        
        Returns:
            Dict com estatísticas
        """
        total = len(self.alerts)
        unacknowledged = sum(1 for a in self.alerts if not a["acknowledged"])
        
        by_class = {}
        by_severity = {"high": 0, "medium": 0, "low": 0}
        
        for alert in self.alerts:
            cls = alert["class"]
            by_class[cls] = by_class.get(cls, 0) + 1
            by_severity[alert["severity"]] += 1
        
        return {
            "total": total,
            "unacknowledged": unacknowledged,
            "by_class": by_class,
            "by_severity": by_severity
        }
    
    def clear_alerts(self):
        """Limpa todos os alertas"""
        self.alerts = []

alert_manager = AlertManager()

