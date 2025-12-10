"""
Rotas da API REST
"""
import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, YOLO_CLASSES, POSITIVE_CLASSES, ALERT_CLASSES
from app.services.video_processor import VideoProcessor
from app.services.stream_handler import StreamHandler
from app.services.alert_manager import alert_manager

router = APIRouter()
stream_handler = StreamHandler()


@router.get("/alerts")
async def get_alerts(limit: int = 50):
    """Retorna alertas recentes"""
    return alert_manager.get_recent_alerts(limit)

@router.get("/alerts/stats")
async def get_alert_stats():
    """Retorna estatísticas de alertas"""
    return alert_manager.get_stats()


@router.get("/status")
async def get_status():
    """Retorna status da API e configurações"""
    return {
        "status": "online",
        "model_loaded": True,
        "available_classes": YOLO_CLASSES,
        "positive_classes": POSITIVE_CLASSES,
        "alert_classes": ALERT_CLASSES
    }


@router.get("/classes")
async def get_classes():
    """Retorna classes de EPI disponíveis para monitoramento"""
    return {
        "all_classes": YOLO_CLASSES,
        "positive_classes": POSITIVE_CLASSES,
        "alert_classes": ALERT_CLASSES,
        "selectable_classes": POSITIVE_CLASSES + ALERT_CLASSES
    }


@router.post("/video/upload")
async def upload_video(
    file: UploadFile = File(...),
    selected_epis: str = Form(default="[]")
):
    """
    Recebe upload de vídeo para processamento
    """
    # Validar extensão
    if file.filename:
        extension = file.filename.split(".")[-1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato não suportado. Use: {', '.join(ALLOWED_EXTENSIONS)}"
            )
    
    # Criar diretório temporário se não existir
    os.makedirs("temp_videos", exist_ok=True)
    
    # Gerar nome único
    file_id = str(uuid.uuid4())
    file_path = f"temp_videos/{file_id}.{extension}"
    
    # Salvar arquivo
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
        
    # Validar se é um vídeo válido
    processor = VideoProcessor()
    if not processor.open_file(file_path):
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Arquivo de vídeo inválido ou corrompido")
    
    video_info = processor.video_info
    processor.release()
    
    return JSONResponse(
        content={
            "message": "Upload realizado com sucesso",
            "filename": file.filename,
            "video_id": file_id,
            "file_path": file_path,
            "video_info": video_info,
            "selected_epis": selected_epis,
            "status": "ready_for_processing"
        },
        status_code=200
    )


@router.post("/stream/connect")
async def connect_stream(stream_url: str = Form(...), protocol: str = Form(default="rtmp")):
    """
    Conecta a uma stream de vídeo RTMP ou SRT
    """
    valid_protocols = ["rtmp", "rtmps", "srt"]
    if protocol.lower() not in valid_protocols:
        raise HTTPException(
            status_code=400,
            detail=f"Protocolo não suportado. Use: {', '.join(valid_protocols)}"
        )
    
    stream_id = await stream_handler.connect(stream_url, protocol)
    
    if not stream_id:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível conectar à stream. Verifique a URL e se a fonte está ativa."
        )
    
    return JSONResponse(
        content={
            "message": "Stream conectada com sucesso",
            "stream_id": stream_id,
            "stream_url": stream_url,
            "protocol": protocol,
            "status": "active"
        },
        status_code=200
    )


@router.post("/stream/disconnect")
async def disconnect_stream(stream_id: str = Form(...)):
    """
    Desconecta de uma stream ativa
    """
    success = await stream_handler.disconnect(stream_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Stream não encontrada ou já desconectada"
        )
        
    return JSONResponse(
        content={
            "message": "Stream desconectada",
            "stream_id": stream_id,
            "status": "disconnected"
        },
        status_code=200
    )
