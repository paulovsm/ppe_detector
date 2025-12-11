# PPE Detection System

Sistema de monitoramento de EPIs (Equipamentos de Proteção Individual) para áreas de mineração utilizando Visão Computacional e Deep Learning.

![Status](https://img.shields.io/badge/Status-Concluído-success)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-18-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)

## 📋 Visão Geral

Este sistema detecta o uso correto de EPIs em tempo real através de streams de vídeo ou upload de arquivos. Utiliza o modelo YOLOv8 treinado especificamente para identificar capacetes, coletes e máscaras, gerando alertas visuais e sonoros em caso de violações.

### Principais Funcionalidades

- **Detecção em Tempo Real**: Processamento de vídeo via WebSocket.
- **Suporte a Múltiplas Fontes**: Upload de arquivos (MP4, AVI) e Streaming (RTMP/SRT).
- **Sistema de Alertas**: Notificações visuais para ausência de EPIs.
- **Dashboard Interativo**: Interface moderna para monitoramento e configuração.
- **Containerização**: Deploy simplificado com Docker e Docker Compose.

## 🚀 Quick Start

A maneira mais rápida de rodar o projeto é utilizando Docker Compose.

### Pré-requisitos
- Docker Engine (24.x+)
- Docker Compose (2.x+)
- NVIDIA Container Toolkit (para suporte a GPU)

### Rodando a Aplicação

1. Clone o repositório:
   ```bash
   git clone <repository-url>
   cd ppe-detection-app
   ```

2. Inicie os containers:

   **Modo CPU (Padrão):**
   ```bash
   docker-compose up --build
   ```

   **Modo GPU (Requer NVIDIA Container Toolkit):**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
   ```

3. Acesse a aplicação:
   - **Frontend**: http://localhost
   - **API Docs**: http://localhost/api/docs

1. Certifique-se de ter os drivers NVIDIA e o **NVIDIA Container Toolkit** instalados no host.
2. O serviço `backend` irá detectar a GPU e utilizar CUDA para aceleração do modelo YOLO.
3. Para verificar se a GPU está sendo utilizada, verifique os logs:
   ```bash
   docker-compose logs backend | grep "Usando GPU"
   ```

## 📚 Documentação

Para guias detalhados, consulte a pasta `docs/`:

- [Guia de Instalação](docs/installation.md) - Requisitos e passos detalhados de instalação.
- [Guia de Configuração](docs/configuration.md) - Variáveis de ambiente e ajustes do modelo.
- [Guia de Uso](docs/usage.md) - Como utilizar o dashboard e configurar streams (OBS).
- [Referência da API](docs/api.md) - Endpoints REST e protocolo WebSocket.

## 🛠️ Tech Stack

- **Backend**: FastAPI, OpenCV, Ultralytics YOLOv8
- **Frontend**: React, Vite, TailwindCSS
- **Infraestrutura**: Docker, Nginx

## 📄 Licença

Este projeto está sob a licença MIT.
