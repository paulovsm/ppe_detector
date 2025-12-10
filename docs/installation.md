# Guia de Instalação

Este guia descreve como configurar e executar o Sistema de Monitoramento de EPIs.

## Pré-requisitos

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas:

- **Docker**: [Instalar Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Instalar Docker Compose](https://docs.docker.com/compose/install/)
- **Git**: [Instalar Git](https://git-scm.com/downloads)

Para desenvolvimento local (sem Docker), você precisará de:
- Python 3.11+
- Node.js 18+

## Instalação via Docker (Recomendado)

Esta é a forma mais simples de rodar a aplicação completa (Frontend + Backend + Nginx).

1. **Clone o repositório:**
   ```bash
   git clone <seu-repositorio>
   cd ppe-detection-app
   ```

2. **Verifique o arquivo de configuração:**
   O arquivo `docker-compose.yml` já vem configurado com valores padrão. Se necessário, ajuste as variáveis de ambiente (veja [Configuração](configuration.md)).

3. **Construa e inicie os containers:**
   ```bash
   docker-compose up --build -d
   ```
   O flag `-d` roda os containers em background.

4. **Verifique os logs (opcional):**
   ```bash
   docker-compose logs -f
   ```

5. **Acesse a aplicação:**
   Abra seu navegador em `http://localhost`.

## Instalação Manual (Desenvolvimento)

Se você deseja rodar os serviços individualmente para desenvolvimento:

### 1. Backend

1. Navegue até a pasta do backend:
   ```bash
   cd backend
   ```

2. Crie um ambiente virtual e ative-o:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   # venv\Scripts\activate  # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicie o servidor:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 2. Frontend

1. Navegue até a pasta do frontend:
   ```bash
   cd frontend
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

3. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

4. Acesse `http://localhost:5173`.

## Troubleshooting

### Erro: Porta em uso
Se você receber um erro informando que a porta 80 ou 8000 já está em uso, pare o serviço que está utilizando essa porta ou altere o mapeamento de portas no `docker-compose.yml`.

### Erro: Modelo não encontrado
Certifique-se de que o arquivo de pesos do YOLO (`ppe.pt`) está presente em `backend/models/`. O Dockerfile copia este diretório para dentro do container.
