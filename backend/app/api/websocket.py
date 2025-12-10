"""
WebSocket handlers para streaming em tempo real
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json
import asyncio
import cv2
import base64
import time
import os
from app.services.video_processor import VideoProcessor
from app.services.detector import PPEDetector
from app.utils.frame_annotator import FrameAnnotator
from app.services.smoother import DetectionSmoother
from app.services.alert_manager import alert_manager

router = APIRouter()


class ConnectionManager:
    """Gerenciador de conexões WebSocket"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Aceita conexão WebSocket"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        """Remove conexão do gerenciador"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_message(self, client_id: str, message: dict):
        """Envia mensagem JSON para cliente específico"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def send_frame(self, client_id: str, frame_data: dict):
        """Envia frame processado para cliente"""
        await self.send_message(client_id, {
            "type": "frame",
            "data": frame_data
        })
    
    async def send_alert(self, client_id: str, alert: dict):
        """Envia alerta para cliente"""
        await self.send_message(client_id, {
            "type": "alert",
            "data": alert
        })
    
    async def send_stats(self, client_id: str, stats: dict):
        """Envia estatísticas para cliente"""
        await self.send_message(client_id, {
            "type": "stats",
            "data": stats
        })
    
    async def broadcast(self, message: dict):
        """Envia mensagem para todos os clientes conectados"""
        for client_id in self.active_connections:
            await self.send_message(client_id, message)


# Instância global do gerenciador de conexões
manager = ConnectionManager()

# Dicionário para controlar tarefas de processamento
processing_tasks = {}
# Dicionário para controlar configurações do cliente
client_configs = {}

async def process_video_stream(client_id: str, source: str, video_id: str = None):
    """
    Task de processamento de vídeo em background
    """
    processor = VideoProcessor()
    detector = PPEDetector()
    annotator = FrameAnnotator()
    # Reduzir min_hits para 1 para garantir que detecções apareçam mesmo com baixo FPS
    smoother = DetectionSmoother(min_hits=1, max_disappeared=5)
    
    # Tentar abrir vídeo (arquivo ou stream)
    if not processor.open_file(source):
        await manager.send_message(client_id, {"type": "error", "message": "Erro ao abrir vídeo"})
        return

    # Carregar modelo
    try:
        detector.load_model()
    except Exception as e:
        await manager.send_message(client_id, {"type": "error", "message": f"Erro ao carregar modelo: {str(e)}"})
        return
    
    try:
        fps_limit = 30
        frame_duration = 1.0 / fps_limit
        frame_count = 0
        skip_frames = 3
        last_detections = []
        last_stats = {}
        
        for frame in processor.get_frames():
            start_time = time.time()
            frame_count += 1
            
            # Verificar se cliente ainda está conectado
            if client_id not in manager.active_connections:
                break
            
            # Verificar se tarefa foi cancelada
            if client_id not in processing_tasks:
                break
            
            # Obter configurações do cliente
            config = client_configs.get(client_id, {"show_boxes": True})
            show_boxes = config.get("show_boxes", True)

            # Redimensionar frame para garantir performance (se VideoProcessor não tiver feito)
            # Forçar resize para 640x480 se for maior
            h, w = frame.shape[:2]
            if w > 640 or h > 640:
                frame = cv2.resize(frame, (640, 480))

            # Lógica de Skip Frames para Detecção
            if frame_count % skip_frames == 0:
                # 1. Detecção
                result = detector.detect(frame)
                raw_detections = result["detections"]
                last_stats = result["stats"]
                
                # 2. Suavização (Debouncing)
                smoothed_detections = smoother.update(raw_detections)
                last_detections = smoothed_detections
                
                # 3. Recalcular violações com base nas detecções suavizadas
                violations = detector.get_violations(smoothed_detections)
                
                # Processar alertas com cooldown
                new_alerts = alert_manager.process_violations(violations)
                
                # Enviar alertas se houver NOVOS alertas
                for alert in new_alerts:
                    await manager.send_alert(client_id, alert)
                
                # Enviar estatísticas
                await manager.send_stats(client_id, last_stats)
            
            # 4. Anotação (usando as últimas detecções conhecidas)
            if show_boxes:
                annotated_frame = annotator.annotate(frame, last_detections)
            else:
                annotated_frame = frame
            
            # 5. Encoding (Qualidade reduzida para performance)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            ret, buffer = cv2.imencode('.jpg', annotated_frame, encode_param)
            if not ret:
                continue
            frame_b64 = base64.b64encode(buffer).decode('utf-8')
            
            # 6. Enviar para cliente
            await manager.send_frame(client_id, frame_b64)
            
            # Enviar estatísticas (atualizar FPS)
            current_fps = 1.0 / (time.time() - start_time) if (time.time() - start_time) > 0 else 30.0
            if last_stats:
                last_stats["fps"] = current_fps
                await manager.send_stats(client_id, last_stats)
            
            # Controle de FPS
            process_time = time.time() - start_time
            sleep_time = max(0, frame_duration - process_time)
            await asyncio.sleep(sleep_time)
            
    except Exception as e:
        print(f"Erro no processamento: {e}")
        await manager.send_message(client_id, {"type": "error", "message": str(e)})
    finally:
        processor.release()
        if client_id in processing_tasks:
            del processing_tasks[client_id]
        if client_id in client_configs:
            del client_configs[client_id]
            
        # Remover arquivo temporário se for um upload
        if video_id and source and os.path.exists(source):
            try:
                os.remove(source)
                print(f"Arquivo temporário removido: {source}")
            except Exception as e:
                print(f"Erro ao remover arquivo temporário {source}: {e}")

        await manager.send_message(client_id, {"type": "status", "message": "Processamento finalizado"})


@router.websocket("/ws/video/{client_id}")
async def video_websocket(websocket: WebSocket, client_id: str):
    """
    WebSocket para streaming de vídeo processado
    """
    print(f"WebSocket connection attempt: {client_id}")
    print(f"Headers: {websocket.headers}")
    await manager.connect(websocket, client_id)
    
    try:
        # Enviar mensagem de conexão estabelecida
        await manager.send_message(client_id, {
            "type": "connection",
            "status": "connected",
            "client_id": client_id
        })
        
        while True:
            # Aguardar mensagens do cliente
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Processar comandos do cliente
            if message.get("action") == "ping":
                await manager.send_message(client_id, {
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                })
            
            elif message.get("action") == "update_config":
                # Atualizar configurações em tempo real
                config = message.get("config", {})
                if client_id not in client_configs:
                    client_configs[client_id] = {}
                client_configs[client_id].update(config)
            
            elif message.get("action") == "start_processing":
                video_id = message.get("video_id")
                stream_url = message.get("stream_url")
                
                source = None
                if video_id:
                    # Tentar usar o path fornecido ou procurar
                    source = message.get("file_path")
                    if not source:
                         import glob
                         files = glob.glob(f"temp_videos/{video_id}.*")
                         if files:
                             source = files[0]
                elif stream_url:
                    source = stream_url
                
                if source:
                    # Cancelar tarefa anterior se existir
                    if client_id in processing_tasks:
                        processing_tasks[client_id].cancel()
                    
                    # Iniciar nova tarefa
                    task = asyncio.create_task(process_video_stream(client_id, source, video_id))
                    processing_tasks[client_id] = task
                    
                    await manager.send_message(client_id, {
                        "type": "status",
                        "message": "Processamento iniciado",
                        "source": source
                    })
                else:
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": "Fonte de vídeo não especificada ou não encontrada"
                    })
            
            elif message.get("action") == "stop_processing":
                if client_id in processing_tasks:
                    processing_tasks[client_id].cancel()
                    del processing_tasks[client_id]
                
                await manager.send_message(client_id, {
                    "type": "status",
                    "message": "Processamento parado"
                })
    
    except WebSocketDisconnect:
        if client_id in processing_tasks:
            processing_tasks[client_id].cancel()
            del processing_tasks[client_id]
        manager.disconnect(client_id)
    except Exception as e:
        if client_id in processing_tasks:
            processing_tasks[client_id].cancel()
            del processing_tasks[client_id]
        manager.disconnect(client_id)
        print(f"Erro no websocket: {e}")


@router.websocket("/ws/alerts/{client_id}")
async def alerts_websocket(websocket: WebSocket, client_id: str):
    """
    WebSocket dedicado para alertas em tempo real
    """
    await manager.connect(websocket, f"alerts_{client_id}")
    
    try:
        await manager.send_message(f"alerts_{client_id}", {
            "type": "connection",
            "status": "connected",
            "channel": "alerts"
        })
        
        while True:
            data = await websocket.receive_text()
            # Manter conexão ativa
    
    except WebSocketDisconnect:
        manager.disconnect(f"alerts_{client_id}")
