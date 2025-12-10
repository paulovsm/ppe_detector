# Guia de Uso

Este guia explica como utilizar as principais funcionalidades do Sistema de Monitoramento de EPIs.

## Dashboard Principal

Ao acessar a aplicação, você verá o Dashboard principal dividido em três áreas:
1. **Área de Vídeo**: Onde o vídeo processado é exibido.
2. **Painel de Controle (Esquerda)**: Configurações de fonte de vídeo e seleção de EPIs.
3. **Painel de Alertas (Direita)**: Histórico de violações detectadas.

## Modos de Operação

### 1. Upload de Vídeo
Ideal para analisar gravações pré-existentes.

1. No painel esquerdo, selecione a aba **"Upload"**.
2. Arraste um arquivo de vídeo (MP4, AVI) para a área indicada ou clique para selecionar.
3. O processamento iniciará automaticamente.
4. O vídeo processado aparecerá na tela central com as caixas delimitadoras (bounding boxes).

### 2. Streaming em Tempo Real (OBS Studio)
Ideal para simular câmeras de segurança ou feeds ao vivo.

1. No painel esquerdo, selecione a aba **"Stream"**.
2. Você verá uma URL de conexão (ex: `ws://localhost/ws/video/client_id`).
3. **Configuração no OBS Studio (ou similar):**
   - O sistema atual utiliza WebSocket para receber frames do frontend ou processar uploads.
   - *Nota: A implementação atual foca em processamento via upload ou câmera local simulada. Para integração direta com câmeras IP (RTSP), seria necessário configurar o backend para consumir a URL RTSP diretamente.*

   **Para simular uma câmera local:**
   - O navegador pode solicitar permissão para usar sua webcam se a funcionalidade estiver habilitada no frontend.

## Seleção de EPIs

Você pode filtrar quais EPIs o sistema deve monitorar:

1. No painel "Configuração de Detecção", marque ou desmarque os itens:
   - **Capacete**: Detecta `Hardhat` e alerta `NO-Hardhat`.
   - **Máscara**: Detecta `Mask` e alerta `NO-Mask`.
   - **Colete**: Detecta `Safety Vest` e alerta `NO-Safety Vest`.

## Interpretando a Visualização

- **Caixa Verde**: EPI detectado corretamente (Conformidade).
- **Caixa Vermelha**: Ausência de EPI (Violação).
- **Caixa Laranja/Rosa**: Outros objetos (Pessoas, Máquinas).

## Alertas

Quando uma violação é detectada (ex: pessoa sem capacete):
1. Uma notificação (Toast) aparece no canto superior direito.
2. O evento é registrado no **Painel de Alertas** à direita com o horário e o tipo de violação.
3. O sistema aguarda alguns segundos (cooldown) antes de alertar novamente sobre a mesma pessoa para evitar spam.
