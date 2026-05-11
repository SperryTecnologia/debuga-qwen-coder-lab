# Deploy de Qwen-Coder com vLLM

> Este guia cobre o deploy de modelos Qwen-Coder usando [vLLM](https://github.com/vllm-project/vllm) como engine de inferência.

## Por que vLLM?

O vLLM é um engine de inferência de alto desempenho para LLMs, com as seguintes vantagens:

- **PagedAttention**: gerenciamento eficiente de memória KV-cache
- **Continuous batching**: throughput maximizado para múltiplos usuários
- **API compatível com OpenAI**: drop-in replacement para clientes existentes
- **Suporte a quantização**: AWQ, GPTQ, FP8 nativamente
- **Tensor parallelism**: distribuir modelo em múltiplas GPUs
- **LoRA serving**: múltiplos adaptadores no mesmo modelo base

## Arquiteturas de Deploy

### 1. Single GPU (Desenvolvimento/Testes)

```bash
docker run --gpus all -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-Coder-7B-Instruct-AWQ \
  --quantization awq \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9
```

### 2. Multi-GPU com Tensor Parallelism

```bash
docker run --gpus all -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-Coder-32B-Instruct \
  --tensor-parallel-size 2 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.9
```

### 3. Produção com Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  vllm:
    image: vllm/vllm-openai:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    ports:
      - "8000:8000"
    volumes:
      - ./models:/root/.cache/huggingface  # Cache de modelos
    command: >
      --model Qwen/Qwen2.5-Coder-7B-Instruct-AWQ
      --quantization awq
      --max-model-len 4096
      --gpu-memory-utilization 0.9
      --max-num-seqs 32
      --enable-prefix-caching
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Opcional: proxy reverso
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      vllm:
        condition: service_healthy
    restart: unless-stopped
```

## Parâmetros Importantes

| Parâmetro | Descrição | Valor Sugerido |
|-----------|-----------|---------------|
| `--max-model-len` | Contexto máximo (tokens) | 4096-8192 |
| `--gpu-memory-utilization` | Fração da VRAM a usar | 0.85-0.95 |
| `--max-num-seqs` | Requests simultâneos | 16-64 |
| `--enable-prefix-caching` | Cache de prefixos comuns | Sempre habilitar |
| `--tensor-parallel-size` | Número de GPUs | 1, 2, 4, 8 |
| `--quantization` | Método de quantização | awq, gptq, fp8 |
| `--enforce-eager` | Desabilitar CUDA graphs | Apenas para debug |

## API Compatível com OpenAI

O vLLM expõe uma API idêntica à da OpenAI:

```python
import requests

# Chat Completions
response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "Qwen/Qwen2.5-Coder-7B-Instruct-AWQ",
        "messages": [
            {"role": "system", "content": "Você é um especialista em DevOps."},
            {"role": "user", "content": "Como configurar rate limiting no Nginx?"}
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
        "stream": True  # Streaming suportado
    },
    stream=True
)

# Streaming
for line in response.iter_lines():
    if line:
        print(line.decode())
```

### Com OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # vLLM não requer API key por padrão
)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-Coder-7B-Instruct-AWQ",
    messages=[
        {"role": "system", "content": "Você é um especialista em segurança."},
        {"role": "user", "content": "Analise este log de auth: ..."}
    ],
    temperature=0.1
)

print(response.choices[0].message.content)
```

## Monitoramento

### Health Check

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

### Métricas Prometheus

O vLLM expõe métricas em `/metrics`:

```bash
curl http://localhost:8000/metrics
```

Métricas importantes:
- `vllm:num_requests_running` — requests em processamento
- `vllm:num_requests_waiting` — requests na fila
- `vllm:gpu_cache_usage_perc` — uso do KV-cache
- `vllm:avg_generation_throughput_toks_per_s` — throughput

### Integração com Grafana

```yaml
# prometheus.yml
scrape_configs:
  - job_name: "vllm"
    static_configs:
      - targets: ["vllm:8000"]
    metrics_path: "/metrics"
```

## Segurança em Produção

1. **Não expor porta 8000 diretamente** — usar reverse proxy (Nginx/Traefik)
2. **Adicionar autenticação** — API key no proxy ou `--api-key` no vLLM
3. **Rate limiting** — configurar no proxy
4. **TLS** — terminar SSL no proxy
5. **Rede isolada** — vLLM em rede interna, apenas proxy exposto

## Referências

- [vLLM Documentation](https://docs.vllm.ai/)
- [vLLM GitHub](https://github.com/vllm-project/vllm)
- [Qwen2.5-Coder](https://huggingface.co/collections/Qwen/qwen25-coder-66eaa22e6f99801bf65b0c2f)
