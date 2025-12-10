"""
Handler para streams de vídeo RTMP e SRT
"""
import numpy as np
import cv2
import time
import asyncio
from typing import Dict, Optional
from app.config import STREAM_RECONNECT_ATTEMPTS, STREAM_RECONNECT_DELAY, STREAM_BUFFER_SIZE


import threading

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
        Registra uma stream e inicia o processo de conexão em background
        
        Args:
            stream_url: URL da stream
            protocol: Protocolo (rtmp, rtmps, srt)
        
        Returns:
            stream_id para referência
        """
        if not self._validate_url(stream_url, protocol):
            print(f"URL inválida para protocolo {protocol}: {stream_url}")
            return None
        
        # Gerar ID único para a stream
        import uuid
        stream_id = str(uuid.uuid4())[:8]
        
        print(f"Registrando stream: {stream_url}")
        
        self.active_streams[stream_id] = {
            "url": stream_url,
            "protocol": protocol,
            "status": "pending",
            "cap": None,
            "last_frame": None,
            "last_frame_time": 0,
            "reconnect_count": 0,
            "stop_signal": False,
            "thread": None
        }
        
        # Iniciar loop de conexão em background
        asyncio.create_task(self._connection_loop(stream_id))
        
        return stream_id

    async def _connection_loop(self, stream_id: str):
        """Loop que mantém a conexão ativa"""
        print(f"Iniciando loop de conexão para {stream_id}")
        
        while True:
            if stream_id not in self.active_streams:
                break
                
            stream = self.active_streams[stream_id]
            
            if stream["stop_signal"]:
                break
                
            if stream["status"] in ["pending", "reconnecting", "failed"]:
                try:
                    # Usar thread separada para não bloquear o loop de eventos
                    cap = await asyncio.to_thread(cv2.VideoCapture, stream["url"])
                    
                    if cap.isOpened():
                        # Tentar ler um frame para garantir
                        ret, _ = await asyncio.to_thread(cap.read)
                        if ret:
                            print(f"Stream {stream_id} conectada com sucesso!")
                            stream["cap"] = cap
                            stream["status"] = "active"
                            stream["reconnect_count"] = 0
                            
                            # Iniciar thread de leitura de frames
                            read_thread = threading.Thread(target=self._read_frames_thread, args=(stream_id,))
                            read_thread.daemon = True
                            read_thread.start()
                            stream["thread"] = read_thread
                        else:
                            cap.release()
                            print(f"Stream {stream_id} aberta mas sem dados. Tentando novamente...")
                            await asyncio.sleep(2)
                    else:
                        await asyncio.sleep(2)
                        
                except Exception as e:
                    print(f"Erro ao conectar stream {stream_id}: {e}")
                    await asyncio.sleep(2)
            
            elif stream["status"] == "active":
                # Monitorar se a thread de leitura ainda está viva
                if stream["thread"] and not stream["thread"].is_alive():
                    print(f"Thread de leitura da stream {stream_id} morreu. Reiniciando conexão.")
                    stream["status"] = "reconnecting"
                    if stream["cap"]:
                        stream["cap"].release()
                        stream["cap"] = None
                
                await asyncio.sleep(1)
        
        print(f"Encerrando loop de conexão para {stream_id}")
        if stream_id in self.active_streams:
            if self.active_streams[stream_id].get("cap"):
                self.active_streams[stream_id]["cap"].release()

    def _read_frames_thread(self, stream_id: str):
        """Thread dedicada para ler frames o mais rápido possível"""
        if stream_id not in self.active_streams:
            return

        stream = self.active_streams[stream_id]
        cap = stream["cap"]
        
        print(f"Iniciando thread de leitura para {stream_id}")
        
        while not stream["stop_signal"]:
            if not cap or not cap.isOpened():
                break
                
            ret, frame = cap.read()
            
            if not ret:
                print(f"Falha na leitura (EOF ou erro) para {stream_id}")
                break
                
            # Atualizar o último frame disponível
            # Isso descarta frames antigos automaticamente se o consumidor for lento
            stream["last_frame"] = frame
            stream["last_frame_time"] = time.time()
            
            # Pequeno sleep para não consumir 100% de CPU se o FPS for baixo,
            # mas baixo o suficiente para não perder frames de 60fps (16ms)
            time.sleep(0.001)
            
        print(f"Thread de leitura encerrada para {stream_id}")

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
        
        self.active_streams[stream_id]["stop_signal"] = True
        
        # Aguardar um pouco para o loop encerrar
        await asyncio.sleep(0.5)
        
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]
            
        return True
    
    async def get_frame(self, stream_id: str) -> Optional[np.ndarray]:
        """
        Retorna o frame mais recente da stream
        
        Args:
            stream_id: ID da stream
        
        Returns:
            Frame de vídeo ou None
        """
        if stream_id not in self.active_streams:
            return None
            
        stream = self.active_streams[stream_id]
        
        if stream["status"] != "active":
            return None
            
        # Retornar o último frame capturado pela thread
        frame = stream.get("last_frame")
        
        # Opcional: Limpar o frame após leitura para evitar processar o mesmo frame duas vezes?
        # Depende da lógica do detector. Se o detector for mais rápido que o vídeo, vai pegar duplicado.
        # Se for mais lento, vai pular frames (o que é desejado para "realtime").
        # Vamos manter assim por enquanto.
        
        return frame

    
    # Método _reconnect removido pois a lógica agora está no loop principal
    
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
