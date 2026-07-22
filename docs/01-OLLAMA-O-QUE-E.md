# 01 — O que é Ollama

## Definição

O **Ollama** é uma plataforma open-source que simplifica a execução de modelos de linguagem (LLMs) localmente. Ele abstrai a complexidade de download, quantização e servir modelos, oferecendo uma CLI intuitiva e uma API HTTP compatível com o padrão OpenAI.

> Em resumo: Ollama é para LLMs o que Docker é para aplicações — um runtime que padroniza a execução.

---

## Conceitos Fundamentais

### Diferença entre Ollama, Modelo e Aplicação

| Conceito | O que é | Analogia |
|----------|---------|----------|
| **Ollama** | Runtime/servidor que carrega e serve modelos | Docker Engine |
| **Modelo** | Arquivo de pesos (ex: qwen2.5:7b-instruct) | Imagem Docker |
| **Aplicação** | Software que consome a API do Ollama (ex: debuga.ai) | Container rodando |

O Ollama **não é** uma IA por si só. Ele é o motor que executa modelos de IA. Sem um modelo baixado, o Ollama não faz nada.

---

## Porta Padrão

O Ollama escuta na porta **11434** por padrão:

```
http://localhost:11434
```

Essa porta expõe:
- API HTTP para geração de texto (`/api/generate`, `/api/chat`)
- Endpoints de gerenciamento (`/api/tags`, `/api/pull`, `/api/delete`)
- Health check na raiz (`GET /` retorna "Ollama is running")

---

## CLI Básica

### Comandos Essenciais

```bash
# Verificar se Ollama está rodando
ollama --version

# Listar modelos disponíveis localmente
ollama list

# Baixar um modelo
ollama pull qwen2.5:7b-instruct

# Rodar modelo interativamente (chat no terminal)
ollama run qwen2.5:7b-instruct

# Remover um modelo
ollama rm qwen2.5:7b-instruct

# Ver informações de um modelo
ollama show qwen2.5:7b-instruct

# Copiar modelo com novo nome (alias)
ollama cp qwen2.5:7b-instruct meu-modelo
```

### Comandos de Diagnóstico

```bash
# Ver modelos carregados na memória
ollama ps

# Ver logs do Ollama (quando rodando como serviço)
journalctl -u ollama -f

# Testar se a API responde
curl http://localhost:11434
# Resposta esperada: "Ollama is running"
```

---

## API HTTP

O Ollama expõe uma API REST na porta 11434. Os principais endpoints são:

| Endpoint | Método | Função |
|----------|--------|--------|
| `/` | GET | Health check |
| `/api/generate` | POST | Gerar texto (completion) |
| `/api/chat` | POST | Chat com histórico de mensagens |
| `/api/tags` | GET | Listar modelos locais |
| `/api/pull` | POST | Baixar modelo |
| `/api/delete` | DELETE | Remover modelo |
| `/api/show` | POST | Informações do modelo |
| `/api/ps` | GET | Modelos carregados na memória |

Exemplo rápido:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b-instruct",
  "prompt": "O que é DNS?",
  "stream": false
}'
```

Veja [05-OLLAMA-API.md](05-OLLAMA-API.md) para documentação completa da API.

---

## Rodar no Host vs Rodar em Docker

### Opção 1: Instalação direta no host

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Vantagens:**
- Acesso direto à GPU sem camada extra
- Mais simples para uso pessoal/desenvolvimento
- Menor overhead

**Desvantagens:**
- Polui o sistema operacional
- Difícil de versionar e reproduzir
- Conflitos com outros serviços

### Opção 2: Container Docker (recomendado para produção)

```bash
docker run -d --gpus all \
  -v ollama-data:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  --restart unless-stopped \
  ollama/ollama
```

**Vantagens:**
- Isolamento completo
- Reproduzível (docker-compose)
- Fácil de atualizar, parar, reiniciar
- Integra com o ambiente de teste via docker-compose

**Desvantagens:**
- Requer NVIDIA Container Toolkit para GPU
- Pequeno overhead de rede/IO

### Recomendação

Para o laboratório e integração com debuga.ai, **usar Docker** é a abordagem recomendada. O docker-compose do ambiente de teste já inclui um serviço Ollama no profile `gpu`.

---

## Volume de Modelos

Os modelos baixados pelo Ollama são armazenados em:

| Ambiente | Caminho |
|----------|---------|
| Host Linux | `~/.ollama/models/` |
| Container Docker | `/root/.ollama/models/` (mapeado via volume) |

O volume `ollama-data` persiste os modelos entre reinicializações do container. Sem o volume, os modelos seriam perdidos ao recriar o container.

**Tamanhos típicos:**

| Modelo | Tamanho em disco (Q4) |
|--------|----------------------|
| qwen2.5:7b-instruct | ~4.7 GB |
| qwen2.5:14b | ~8.9 GB |
| qwen2.5-coder:7b | ~4.7 GB |
| qwen3:14b | ~9.2 GB |
| qwen3:30b-a3b | ~18 GB |

---

## Limitações do Ollama

1. **Não é sandbox** — Ollama não executa código, não acessa rede, não manipula arquivos. Ele apenas gera texto.

2. **Sem tool calling nativo real** — Embora suporte o formato de tool calling na API, a execução das ferramentas deve ser feita pelo backend da aplicação (ex: debuga.ai).

3. **Single-model por vez (padrão)** — Por padrão, apenas um modelo fica carregado na VRAM. Trocar de modelo requer descarregar o anterior.

4. **Sem autenticação** — A API não tem auth nativo. Em produção, deve ficar atrás de um proxy ou em rede interna.

5. **Sem rate limiting** — Não há controle de concorrência nativo. Múltiplas requisições simultâneas podem causar OOM na GPU.

6. **Contexto limitado pela VRAM** — Quanto maior o contexto, mais VRAM é consumida. Em RTX 3090 com modelo 14B, o contexto prático é ~8K-16K tokens.

7. **Sem fine-tuning** — Ollama serve modelos pré-treinados. Para fine-tuning, usar ferramentas como vLLM, Unsloth ou HuggingFace PEFT.

---

## Próximo Passo

Antes de instalar o Ollama, é necessário configurar a GPU na VM. Veja [02-GPU-HYPERV-DDA-RTX3090.md](02-GPU-HYPERV-DDA-RTX3090.md).
