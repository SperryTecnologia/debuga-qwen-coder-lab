# 05 — API HTTP do Ollama

## Visão Geral

O Ollama expõe uma API REST na porta **11434**. A API é compatível com o formato OpenAI para os endpoints de chat, facilitando integração com aplicações existentes.

Base URL:
```
http://localhost:11434
```

---

## Endpoints Principais

| Endpoint | Método | Função |
|----------|--------|--------|
| `/` | GET | Health check |
| `/api/generate` | POST | Geração de texto (completion) |
| `/api/chat` | POST | Chat com histórico de mensagens |
| `/api/tags` | GET | Listar modelos locais |
| `/api/show` | POST | Informações detalhadas de um modelo |
| `/api/pull` | POST | Baixar modelo do registry |
| `/api/delete` | DELETE | Remover modelo local |
| `/api/ps` | GET | Modelos carregados na memória |

---

## /api/generate

Gera texto a partir de um prompt simples (sem histórico de conversa).

### Requisição

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b-instruct",
  "prompt": "Explique o que é um firewall em 3 linhas.",
  "stream": false
}'
```

### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `model` | string | Sim | Nome do modelo (ex: `qwen2.5:7b-instruct`) |
| `prompt` | string | Sim | Texto de entrada |
| `stream` | boolean | Não | `true` = streaming (padrão), `false` = resposta completa |
| `system` | string | Não | System prompt |
| `temperature` | float | Não | Criatividade (0.0 = determinístico, 1.0 = criativo) |
| `num_predict` | int | Não | Máximo de tokens a gerar |
| `context` | array | Não | Contexto de conversa anterior (retornado em respostas) |

### Resposta (stream: false)

```json
{
  "model": "qwen2.5:7b-instruct",
  "created_at": "2025-01-15T10:30:00Z",
  "response": "Um firewall é um sistema de segurança...",
  "done": true,
  "total_duration": 1234567890,
  "load_duration": 100000000,
  "prompt_eval_count": 15,
  "eval_count": 45,
  "eval_duration": 900000000
}
```

### Resposta (stream: true — padrão)

Cada chunk é um JSON separado por newline:

```json
{"model":"qwen2.5:7b-instruct","response":"Um ","done":false}
{"model":"qwen2.5:7b-instruct","response":"firewall ","done":false}
{"model":"qwen2.5:7b-instruct","response":"é ","done":false}
...
{"model":"qwen2.5:7b-instruct","response":"","done":true,"total_duration":...}
```

---

## /api/chat

Chat com histórico de mensagens. Formato compatível com OpenAI.

### Requisição

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:7b-instruct",
  "messages": [
    {"role": "system", "content": "Você é um especialista em infraestrutura de TI."},
    {"role": "user", "content": "O que pode causar timeout em DNS?"}
  ],
  "stream": false
}'
```

### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `model` | string | Sim | Nome do modelo |
| `messages` | array | Sim | Histórico de mensagens |
| `stream` | boolean | Não | Streaming (padrão: true) |
| `tools` | array | Não | Definição de ferramentas (tool calling) |
| `options` | object | Não | Parâmetros de geração (temperature, num_predict, etc.) |

### Formato de Mensagens

```json
{
  "messages": [
    {"role": "system", "content": "Instruções do sistema"},
    {"role": "user", "content": "Pergunta do usuário"},
    {"role": "assistant", "content": "Resposta anterior do modelo"},
    {"role": "user", "content": "Nova pergunta"}
  ]
}
```

### Resposta (stream: false)

```json
{
  "model": "qwen2.5:7b-instruct",
  "created_at": "2025-01-15T10:30:00Z",
  "message": {
    "role": "assistant",
    "content": "O timeout em DNS pode ser causado por..."
  },
  "done": true,
  "total_duration": 2345678901,
  "eval_count": 120
}
```

---

## Streaming vs Stream False

### Quando usar streaming (`stream: true`)

- Chat em tempo real (frontend exibe token por token)
- Experiência de "digitação" para o usuário
- Respostas longas (o usuário vê o início antes do fim)

### Quando usar stream false (`stream: false`)

- Scripts de automação
- Testes e benchmarks
- Processamento em lote
- Quando precisa da resposta completa antes de agir

### Exemplo de consumo de streaming em Python

```python
import requests
import json

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen2.5:7b-instruct",
        "messages": [{"role": "user", "content": "O que é DNS?"}],
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        print(chunk["message"]["content"], end="", flush=True)
        if chunk.get("done"):
            break
```

---

## Listar Modelos

### GET /api/tags

```bash
curl http://localhost:11434/api/tags
```

Resposta:

```json
{
  "models": [
    {
      "name": "qwen2.5:7b-instruct",
      "model": "qwen2.5:7b-instruct",
      "modified_at": "2025-01-15T10:00:00Z",
      "size": 4700000000,
      "digest": "sha256:abc123...",
      "details": {
        "parent_model": "",
        "format": "gguf",
        "family": "qwen2",
        "families": ["qwen2"],
        "parameter_size": "7.6B",
        "quantization_level": "Q4_K_M"
      }
    }
  ]
}
```

---

## Remover Modelo

### DELETE /api/delete

```bash
curl -X DELETE http://localhost:11434/api/delete -d '{
  "name": "qwen2.5:7b-instruct"
}'
```

Resposta: HTTP 200 (sem corpo) se sucesso.

---

## Manter Modelo Carregado na Memória

Por padrão, o Ollama descarrega o modelo da VRAM após 5 minutos de inatividade. Para manter carregado:

### Opção 1: keep_alive na requisição

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b-instruct",
  "prompt": "",
  "keep_alive": -1
}'
```

Valores de `keep_alive`:
- `-1` = manter para sempre
- `0` = descarregar imediatamente
- `"5m"` = manter por 5 minutos (padrão)
- `"1h"` = manter por 1 hora

### Opção 2: Variável de ambiente

```bash
# No docker-compose ou docker run:
OLLAMA_KEEP_ALIVE=-1
```

### Verificar modelos carregados

```bash
curl http://localhost:11434/api/ps
```

Resposta:

```json
{
  "models": [
    {
      "name": "qwen2.5:7b-instruct",
      "model": "qwen2.5:7b-instruct",
      "size": 5000000000,
      "digest": "sha256:...",
      "expires_at": "0001-01-01T00:00:00Z"
    }
  ]
}
```

---

## Exemplos Práticos

### Diagnóstico de rede

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:7b-instruct",
  "messages": [
    {"role": "system", "content": "Você é um engenheiro de redes sênior. Responda de forma técnica e objetiva."},
    {"role": "user", "content": "O traceroute mostra timeout no hop 5 (10.0.0.1). O que pode estar acontecendo?"}
  ],
  "stream": false
}' | jq '.message.content'
```

### Geração de script

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5-coder:7b",
  "messages": [
    {"role": "system", "content": "Gere apenas código bash, sem explicações."},
    {"role": "user", "content": "Script para monitorar uso de disco e alertar se > 90%"}
  ],
  "stream": false
}' | jq -r '.message.content'
```

### Análise de log

```bash
LOG="Jan 15 10:30:01 server sshd[12345]: Failed password for invalid user admin from 192.168.1.100 port 54321 ssh2"

curl http://localhost:11434/api/chat -d "{
  \"model\": \"qwen2.5:7b-instruct\",
  \"messages\": [
    {\"role\": \"system\", \"content\": \"Analise logs de segurança. Identifique: tipo de evento, severidade, IP de origem, recomendação.\"},
    {\"role\": \"user\", \"content\": \"$LOG\"}
  ],
  \"stream\": false
}" | jq '.message.content'
```

---

## Testar se a API Está Respondendo

```bash
# Health check simples
curl -s http://localhost:11434 && echo " OK" || echo " FALHOU"

# Verificar se modelo está disponível
curl -s http://localhost:11434/api/tags | jq '.models[].name'

# Teste rápido de geração
curl -s http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b-instruct",
  "prompt": "Responda apenas: OK",
  "stream": false
}' | jq -r '.response'
```

---

## Próximo Passo

Agora que você domina a API, entenda por que Ollama **não é sandbox** e como criar uma arquitetura segura. Veja [06-SANDBOX-E-TOOL-CALLING.md](06-SANDBOX-E-TOOL-CALLING.md).
