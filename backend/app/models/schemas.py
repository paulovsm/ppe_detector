"""
Pydantic schemas para validação de dados
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Detection(BaseModel):
    """Schema para uma detecção individual"""
    class_name: str = Field(..., description="Nome da classe detectada")
    confidence: float = Field(..., ge=0, le=1, description="Confiança da detecção")
    bbox: List[int] = Field(..., min_length=4, max_length=4, description="Bounding box [x1, y1, x2, y2]")


class DetectionResult(BaseModel):
    """Schema para resultado de detecção em um frame"""
    frame_number: int = Field(..., description="Número do frame")
    timestamp: Optional[str] = Field(None, description="Timestamp do frame")
    detections: List[Detection] = Field(default=[], description="Lista de detecções")
    violations: List[Detection] = Field(default=[], description="Lista de violações")
    processing_time_ms: float = Field(..., description="Tempo de processamento em ms")


class Alert(BaseModel):
    """Schema para alerta de violação"""
    id: int = Field(..., description="ID único do alerta")
    class_name: str = Field(..., alias="class", description="Classe da violação")
    confidence: float = Field(..., description="Confiança da detecção")
    bbox: List[int] = Field(..., description="Bounding box")
    frame_number: Optional[int] = Field(None, description="Número do frame")
    timestamp: str = Field(..., description="Timestamp do alerta")
    severity: str = Field(..., description="Severidade (high, medium, low)")
    acknowledged: bool = Field(default=False, description="Se foi reconhecido")


class AlertStats(BaseModel):
    """Schema para estatísticas de alertas"""
    total: int = Field(..., description="Total de alertas")
    unacknowledged: int = Field(..., description="Alertas não reconhecidos")
    by_class: dict = Field(default={}, description="Alertas por classe")
    by_severity: dict = Field(default={}, description="Alertas por severidade")


class EPISelection(BaseModel):
    """Schema para seleção de EPIs a monitorar"""
    selected_classes: List[str] = Field(
        default=["Hardhat", "Safety Vest", "Mask"],
        description="Classes de EPI selecionadas para monitoramento"
    )
    include_alerts: bool = Field(
        default=True,
        description="Incluir classes de alerta (NO-Hardhat, etc.)"
    )


class StreamConfig(BaseModel):
    """Schema para configuração de stream"""
    url: str = Field(..., description="URL da stream")
    protocol: str = Field(default="rtmp", description="Protocolo (rtmp, rtmps, srt)")


class VideoUploadResponse(BaseModel):
    """Schema para resposta de upload de vídeo"""
    message: str
    filename: str
    video_id: Optional[str] = None
    status: str


class ProcessingStats(BaseModel):
    """Schema para estatísticas de processamento"""
    total_frames: int = Field(..., description="Total de frames processados")
    total_detections: int = Field(..., description="Total de detecções")
    total_violations: int = Field(..., description="Total de violações")
    avg_processing_time_ms: float = Field(..., description="Tempo médio de processamento")
    fps: float = Field(..., description="Frames por segundo")
    detections_by_class: dict = Field(default={}, description="Detecções por classe")
