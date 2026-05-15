# 07 — Integração com debuga.ai Homolog

## Modos de Operação

O debuga.ai homolog suporta 3 modos de inferência LLM:

| Modo | Variável `.env` | Infraestrutura | Latência | Custo |
|------|----------------|----------------|----------|-------|
| **Cloud** | `ENABLE_LOCAL_INFERENCE=false` | API cloud (padrão) | ~1-3s | Por token |
| **Ollama local** | `ENABLE_LOCAL_INFERENCE=true` + profile `gpu` | Ollama no mesmo docker-compose | ~0.5-1s | Fixo (GPU) |
| **Ollama externo** | `ENABLE_LOCAL_INFERENCE=true` + `OLLAMA_BASE_URL` customizado | Ollama em outro host/VM | ~0.5-2s | Fixo (GPU) |

---

## Modo 1: Cloud (Padrão)

O modo padrão não usa Ollama. O backend do debuga.ai se comunica com uma API LLM cloud.

```env
# .env
ENABLE_LOCAL_INFERENCE=false
```

Neste modo, o serviço Ollama **não é iniciado** (está no profile `gpu` que não é ativado por padrão).

```bash
# Deploy sem GPU
docker compose -f docker/docker-compose.yml up -d
```

---

## Modo 2: Ollama Local (Mesmo Docker Compose)

O Ollama roda como serviço no mesmo docker-compose, usando a GPU local.

### Configuração

```env
# .env
ENABLE_LOCAL_INFERENCE=true
OLLAMA_BASE_URL=http://ollama:11434
LOCAL_MODEL_NAME=qwen2.5:7b-instruct
```

### Deploy

```bash
# Subir com profile gpu (inclui Ollama)
docker compose -f docker/docker-compose.yml --profile gpu up -d

# Baixar modelo
docker exec debuga-ollama ollama pull qwen2.5:7b-instruct

# Verificar
docker exec debuga-ollama ollama list
```

### Verificação

```bash
# Testar se Ollama responde (de dentro da rede Docker)
docker exec debuga-app curl -s http://ollama:11434
# Resposta: "Ollama is running"

# Testar geração
docker exec debuga-app curl -s http://ollama:11434/api/generate -d '{
  "model": "qwen2.5:7b-instruct",
  "prompt": "Teste",
  "stream": false
}' | head -c 200
```

---

## Modo 3: Ollama Externo (Outro Host/VM)

O Ollama roda em uma máquina separada (ex: VM com GPU dedicada) e o debuga.ai se conecta via rede.

### Cenário Típico

```
┌─────────────────────┐         ┌─────────────────────┐
│  VPS (debuga.ai)    │         │  VM GPU (Ollama)    │
│  - app              │  HTTP   │  - RTX 3090         │
│  - postgres         │ ──────► │  - Ollama :11434    │
│  - minio            │         │  - qwen2.5:7b       │
│  - nginx            │         │                     │
└─────────────────────┘         └─────────────────────┘
```

### Configuração no debuga.ai

```env
# .env
ENABLE_LOCAL_INFERENCE=true
OLLAMA_BASE_URL=http://192.168.1.100:11434
LOCAL_MODEL_NAME=qwen2.5:7b-instruct
```

### Configuração no Host GPU

```bash
# No host com GPU, subir Ollama expondo a porta
docker run -d --gpus all \
  -v ollama-data:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  --restart unless-stopped \
  -e OLLAMA_HOST=0.0.0.0 \
  ollama/ollama

# Baixar modelo
docker exec ollama ollama pull qwen2.5:7b-instruct
```

### Segurança para Ollama Externo

Quando o Ollama está em outro host com porta exposta, é necessário proteger:

**Opção A: Firewall (recomendado)**

```bash
# No host GPU, permitir apenas o IP da VPS
sudo ufw allow from 10.0.0.5 to any port 11434
sudo ufw deny 11434
```

**Opção B: VPN/WireGuard**

Conectar os dois hosts via VPN e usar IP interno:

```env
OLLAMA_BASE_URL=http://10.10.0.2:11434
```

**Opção C: Nginx reverse proxy com auth**

```nginx
server {
    listen 11434 ssl;
    server_name ollama.internal.debuga.ai;

    ssl_certificate /etc/letsencrypt/live/.../fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/.../privkey.pem;

    location / {
        auth_basic "Ollama";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:11434;
    }
}
```

---

## Variáveis de Ambiente Relevantes

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `ENABLE_LOCAL_INFERENCE` | `true` ou `false` | Habilita/desabilita inferência local |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | URL do Ollama (interno ou externo) |
| `LOCAL_MODEL_NAME` | `qwen2.5:7b-instruct` | Modelo padrão para inferência |
| `LOCAL_MODEL_TEMPERATURE` | `0.7` | Temperatura padrão |
| `LOCAL_MODEL_MAX_TOKENS` | `2048` | Máximo de tokens por resposta |

---

## Fluxo de Requisição

```
1. Usuário envia mensagem no chat
2. Backend verifica ENABLE_LOCAL_INFERENCE
3. Se true:
   a. Monta payload com system prompt + histórico + mensagem
   b. Envia POST para OLLAMA_BASE_URL/api/chat
   c. Recebe resposta (streaming ou completa)
   d. Retorna ao frontend
4. Se false:
   a. Usa API cloud (comportamento padrão)
```

---

## Trocar de Modelo em Runtime

Para trocar o modelo sem reiniciar o container:

```bash
# Baixar novo modelo
docker exec debuga-ollama ollama pull qwen3:14b

# Atualizar .env
LOCAL_MODEL_NAME=qwen3:14b

# Reiniciar apenas o app (não precisa reiniciar Ollama)
docker compose -f docker/docker-compose.yml restart app
```

---

## Monitoramento

### Verificar uso de GPU

```bash
# No host com GPU
nvidia-smi

# Monitoramento contínuo (atualiza a cada 2s)
watch -n 2 nvidia-smi
```

### Verificar modelos carregados

```bash
docker exec debuga-ollama curl -s http://localhost:11434/api/ps | jq
```

### Verificar logs do Ollama

```bash
docker logs debuga-ollama --tail=50 -f
```

### Health check do app

```bash
# Verificar se o app consegue se comunicar com Ollama
docker exec debuga-app curl -s http://ollama:11434
# Deve retornar: "Ollama is running"
```

---

## Checklist de Integração

```
[ ] ENABLE_LOCAL_INFERENCE=true no .env
[ ] OLLAMA_BASE_URL correto (interno: http://ollama:11434, externo: http://IP:11434)
[ ] LOCAL_MODEL_NAME definido
[ ] Modelo baixado (ollama list mostra o modelo)
[ ] Ollama respondendo (curl http://ollama:11434 retorna "Ollama is running")
[ ] App consegue acessar Ollama (docker exec debuga-app curl http://ollama:11434)
[ ] Geração funciona (testar via chat no frontend)
[ ] GPU sendo utilizada (nvidia-smi mostra uso de VRAM)
```

---

## Próximo Passo

Com a integração funcionando, execute benchmarks para avaliar a qualidade e velocidade. Veja [08-BENCHMARKS-E-TESTES.md](08-BENCHMARKS-E-TESTES.md).
