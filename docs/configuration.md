# Guia de Configuração

Este documento detalha as variáveis de ambiente e configurações disponíveis para o sistema.

## Variáveis de Ambiente

As configurações são gerenciadas principalmente através do `docker-compose.yml` ou de um arquivo `.env` na raiz do backend.

### Backend

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `MODEL_PATH` | Caminho para o arquivo de pesos do YOLO (.pt) | `models/ppe.pt` |
| `CONFIDENCE_THRESHOLD` | Nível mínimo de confiança para considerar uma detecção válida (0.0 a 1.0) | `0.5` |
| `CORS_ORIGINS` | Lista de origens permitidas para CORS (separadas por vírgula) | `*` |
| `MAX_UPLOAD_SIZE` | Tamanho máximo permitido para upload de vídeos | `100MB` |

### Frontend

As variáveis do frontend devem começar com `VITE_` e são definidas no momento do build.

| Variável | Descrição | Valor Padrão |
|----------|-----------|--------------|
| `VITE_API_URL` | URL base da API do Backend | `http://localhost:8000` (dev) ou `/api` (prod) |
| `VITE_WS_URL` | URL base para conexão WebSocket | `ws://localhost:8000` (dev) or `/ws` (prod) |

## Configuração do Modelo YOLO

O sistema utiliza o modelo YOLOv8. O arquivo de pesos padrão é o `ppe.pt`.

### Alterando o Modelo
Para usar um modelo customizado:
1. Coloque seu arquivo `.pt` na pasta `backend/models/`.
2. Atualize a variável `MODEL_PATH` no `docker-compose.yml` para apontar para o novo arquivo (ex: `/app/models/meu-modelo.pt`).
3. Reinicie o container do backend.

## Configuração de Alertas

Os alertas são configurados no `AlertManager` (backend).

- **Cooldown**: O tempo padrão entre alertas repetidos para a mesma violação é de **5 segundos**.
- **Classes de Alerta**: Por padrão, as classes que geram alerta são:
  - `NO-Hardhat`
  - `NO-Mask`
  - `NO-Safety Vest`

Para alterar essas configurações, é necessário editar o arquivo `backend/app/services/alert_manager.py` ou `backend/app/services/detector.py`.
