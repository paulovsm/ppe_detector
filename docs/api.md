# Referência da API

Documentação técnica dos endpoints da API REST e do protocolo WebSocket.

## API REST

A API segue o padrão RESTful. A documentação interativa (Swagger UI) está disponível em `/docs` ou `/api/docs` quando rodando via Nginx.

### Health Check
- **GET** `/health`
- **Descrição**: Verifica se a API está online.
- **Resposta**: `{"status": "healthy"}`

### Upload de Vídeo
- **POST** `/api/video/upload`
- **Content-Type**: `multipart/form-data`
- **Parâmetros**:
  - `file`: Arquivo de vídeo (binário).
- **Resposta**: Retorna o vídeo processado (stream).

## WebSocket Protocol

O sistema utiliza WebSockets para comunicação bidirecional em tempo real, enviando frames processados e recebendo configurações.

**Endpoint**: `/ws/video/{client_id}`

### Mensagens Enviadas pelo Cliente (Frontend)

#### 1. Configuração de Detecção
Enviado quando o usuário altera os EPIs selecionados.
```json
{
  "type": "config",
  "data": {
    "selected_epis": ["Hardhat", "Mask", "Safety Vest"]
  }
}
```

### Mensagens Recebidas do Servidor (Backend)

#### 1. Frame Processado
Contém a imagem processada em base64 e os dados das detecções.
```json
{
  "type": "frame",
  "data": "base64_encoded_image_string...",
  "detections": [
    {
      "class": "NO-Hardhat",
      "confidence": 0.85,
      "bbox": [100, 200, 150, 250]
    }
  ]
}
```

#### 2. Alerta de Violação
Enviado quando uma regra de segurança é violada.
```json
{
  "type": "alert",
  "data": {
    "id": "unique_alert_id",
    "violation_type": "NO-Hardhat",
    "timestamp": "2023-10-27T10:00:00",
    "confidence": 0.92
  }
}
```

#### 3. Estatísticas
Enviado periodicamente com dados de performance.
```json
{
  "type": "stats",
  "data": {
    "fps": 24.5,
    "total_detections": 150
  }
}
```
