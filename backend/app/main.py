"""
PPE Detection API - Entrada principal FastAPI
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS, DEBUG
from app.api.routes import router as api_router
from app.api.websocket import router as ws_router

app = FastAPI(
    title="PPE Detection API",
    description="API para detecção de Equipamentos de Proteção Individual usando YOLOv8",
    version="1.0.0",
    debug=DEBUG
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    print(f"Headers: {request.headers}")
    response = await call_next(request)
    return response

# Rotas
app.include_router(api_router, prefix="/api", tags=["API"])
app.include_router(ws_router, prefix="/api", tags=["WebSocket"])


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "PPE Detection API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ppe-detection-api"
    }
