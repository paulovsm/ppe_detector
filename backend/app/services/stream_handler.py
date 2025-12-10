"""
Handler para streams de vídeo RTMP e SRT
"""
import numpy as np
import cv2
import time
import asyncio
from typing import Dict, Optional
from app.config import STREAM_RECONNECT_ATTEMPTS, STREAM_RECONNECT_DELAY, STREAM_BUFFER_SIZE


class StreamHandler:
    """
    Handler para streams de vídeo RTMP e SRT
    Suporta integração com OBS Studio
    """
    
    def __init__(self):
        self.active_streams: Dict[str, dict] = {}
        self.reconnect_attempts = STREAM_RECONNECT_ATTEMPTS
        self.reconnect_delay = STREAM_RECONNECT_DELAY
        self.buffer_size = STREAM_BUFFER_SIZE
    
    async def connect(self, stream_url: str, protocol: str) -> Optional[str]:
        """
        Conecta a uma stream RTMP ou SRT
        
        Args:
            stream_url: URL da stream
            protocol: Protocolo (rtmp, rtmps, srt)
        
        Returns:
            stream_id para referência ou None se falhar
        """
        if not self._validate_url(stream_url, protocol):
            print(f"URL inválida para protocolo {protocol}: {stream_url}")
            return None
        
        # Gerar ID único para a stream
        import uuid
        stream_id = str(uuid.uuid4())[:8]
        
        # Tentar conectar
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            print(f"Falha ao conectar na stream: {stream_url}")
            return None
            
        self.active_streams[stream_id] = {
            "url": stream_url,
            "protocol": protocol,
            "status": "active",
            "cap": cap,
            "last_frame_time": time.time(),
            "reconnect_count": 0
        }
        
        return stream_id
    
    async def disconnect(self, stream_id: str) -> bool:
        """
        Desconecta de uma stream ativa
        
        Args:
            stream_id: ID da stream
        
        Returns:
            True se desconectado com sucesso
        """
        if stream_id not in self.active_streams:
            return False
        
        stream = self.active_streams[stream_id]
        if stream.get("cap"):
            stream["cap"].release()
        
        del self.active_streams[stream_id]
        return True
    
    async def get_frame(self, stream_id: str) -> Optional[np.ndarray]:
        """
        Retorna próximo frame da stream
        
        Args:
            stream_id: ID da stream
        
        Returns:
            Frame de vídeo ou None
        """
        if stream_id not in self.active_streams:
            return None
            
        stream = self.active_streams[stream_id]
        cap = stream["cap"]
        
        if not cap or not cap.isOpened():
            # Tentar reconectar
            if await self._reconnect(stream_id):
                cap = self.active_streams[stream_id]["cap"]
            else:
                return None
        
        ret, frame = cap.read()
        
        if not ret:
            # Falha na leitura, tentar reconectar
            if await self._reconnect(stream_id):
                # Tentar ler novamente após reconexão
                cap = self.active_streams[stream_id]["cap"]
                ret, frame = cap.read()
                if not ret:
                    return None
            else:
                return None
                
        stream["last_frame_time"] = time.time()
        stream["reconnect_count"] = 0  # Resetar contador após sucesso
        
        return frame
    
    async def _reconnect(self, stream_id: str) -> bool:
        """
        Tenta reconectar a stream
        """
        stream = self.active_streams[stream_id]
        
        if stream["reconnect_count"] >= self.reconnect_attempts:
            stream["status"] = "failed"
            return False
            
        stream["status"] = "reconnecting"
        stream["reconnect_count"] += 1
        
        # Liberar recurso anterior
        if stream["cap"]:
            stream["cap"].release()
            
        # Aguardar delay
        await asyncio.sleep(self.reconnect_delay)
        
        # Tentar nova conexão
        cap = cv2.VideoCapture(stream["url"])
        if cap.isOpened():
            stream["cap"] = cap
            stream["status"] = "active"
            return True
            
        return False
    
    def _validate_url(self, url: str, protocol: str) -> bool:
        """
        Valida URL de stream
        
        Args:
            url: URL para validar
            protocol: Protocolo esperado
        
        Returns:
            True se válida
        """
        if protocol == "rtmp":
            return url.startswith("rtmp://")
        elif protocol == "rtmps":
            return url.startswith("rtmps://")
        elif protocol == "srt":
            return url.startswith("srt://")
        return False
    
    def get_active_streams(self) -> Dict[str, dict]:
        """Retorna streams ativas"""
        return {
            sid: {
                "protocol": s["protocol"],
                "status": s["status"]
            }
            for sid, s in self.active_streams.items()
        }
