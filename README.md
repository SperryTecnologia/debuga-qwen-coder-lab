# debuga-qwen-coder-lab

> **Repositório exclusivo** — Acesso restrito à equipe Sperry Tecnologia, alunos autorizados e clientes com contrato vigente.

Laboratório prático de IA local com **Ollama**, modelos **Qwen** e GPU **NVIDIA RTX 3090** para integração com o [debuga.ai](https://debuga.ai).

---

## Objetivo

Este repositório documenta e organiza um laboratório funcional para:

- Executar modelos LLM localmente com GPU dedicada
- Avaliar modelos da família Qwen (2.5 e 3) para tarefas de infraestrutura, segurança e DevOps
- Integrar inferência local com a plataforma debuga.ai (homolog/produção)
- Servir como material didático para cursos e treinamentos OpenInfra

---

## Arquitetura do Laboratório

```
┌─────────────────────────────────────────────────────────────┐
│  Windows Server 2019 (Host)                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Hyper-V — Ubuntu 22.04 VM                            │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  RTX 3090 24GB (via DDA)                        │  │  │
│  │  │  ┌───────────────────────────────────────────┐  │  │  │
│  │  │  │  Docker + NVIDIA Container Toolkit        │  │  │  │
│  │  │  │  ┌─────────────────────────────────────┐  │  │  │  │
│  │  │  │  │  Ollama Container (--gpus all)      │  │  │  │  │
│  │  │  │  │  Modelo: qwen2.5:7b-instruct        │  │  │  │  │
│  │  │  │  │  API: http://localhost:11434        │  │  │  │  │
│  │  │  │  └─────────────────────────────────────┘  │  │  │  │
│  │  │  └───────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Hardware Utilizado

| Componente | Especificação |
|-----------|---------------|
| Host OS | Windows Server 2019 Datacenter |
| Hypervisor | Hyper-V com DDA (Discrete Device Assignment) |
| VM OS | Ubuntu 22.04 LTS |
| GPU | NVIDIA GeForce RTX 3090 (24 GB GDDR6X) |
| RAM VM | 32 GB |
| Disco VM | 200 GB SSD NVMe |
| Docker | 24.x + NVIDIA Container Toolkit |
| Ollama | Latest (container oficial) |

---

## Fluxo Completo de Implantação

```
1. Preparar Windows Server + Hyper-V
2. Configurar DDA para a RTX 3090
3. Criar VM Ubuntu 22.04
4. Instalar driver NVIDIA na VM
5. Instalar Docker + NVIDIA Container Toolkit
6. Subir Ollama em container com --gpus all
7. Baixar modelo (ollama pull qwen2.5:7b-instruct)
8. Testar API local (curl http://localhost:11434/api/generate)
9. Integrar com debuga.ai homolog (ENABLE_LOCAL_INFERENCE=true)
10. Executar benchmarks e validar respostas
```

---

## Pré-requisitos

- Windows Server 2019/2022 com Hyper-V habilitado
- GPU NVIDIA com suporte DDA (RTX 3090, A100, etc.)
- Ubuntu 22.04 na VM com driver NVIDIA 535+
- Docker 24+ com NVIDIA Container Toolkit
- Acesso ao repositório debuga-ai-homolog (para integração)

---

## Trilha Recomendada de Leitura

| Ordem | Documento | Tema |
|-------|-----------|------|
| 1 | [docs/01-OLLAMA-O-QUE-E.md](docs/01-OLLAMA-O-QUE-E.md) | O que é Ollama, CLI, API, Docker vs host |
| 2 | [docs/02-GPU-HYPERV-DDA-RTX3090.md](docs/02-GPU-HYPERV-DDA-RTX3090.md) | Passthrough de GPU via Hyper-V DDA |
| 3 | [docs/03-DOCKER-NVIDIA-TOOLKIT.md](docs/03-DOCKER-NVIDIA-TOOLKIT.md) | Docker + NVIDIA Container Toolkit |
| 4 | [docs/04-MODELOS-QWEN-COMPARATIVO.md](docs/04-MODELOS-QWEN-COMPARATIVO.md) | Comparativo de modelos Qwen 2.5 e 3 |
| 5 | [docs/05-OLLAMA-API.md](docs/05-OLLAMA-API.md) | API HTTP do Ollama (endpoints, exemplos) |
| 6 | [docs/06-SANDBOX-E-TOOL-CALLING.md](docs/06-SANDBOX-E-TOOL-CALLING.md) | Segurança: sandbox, tool calling, isolamento |
| 7 | [docs/07-INTEGRACAO-COM-DEBUGA-HOMOLOG.md](docs/07-INTEGRACAO-COM-DEBUGA-HOMOLOG.md) | Integração com debuga.ai homolog |
| 8 | [docs/08-BENCHMARKS-E-TESTES.md](docs/08-BENCHMARKS-E-TESTES.md) | Roteiro de testes e benchmarks |
| 9 | [docs/09-TROUBLESHOOTING.md](docs/09-TROUBLESHOOTING.md) | Problemas reais e soluções |

---

## Relação com debuga.ai

Este laboratório é complementar ao [debuga-ai-homolog](https://github.com/SperryTecnologia/debuga-ai-homolog):

| Repositório | Função |
|-------------|--------|
| **debuga-ai-homolog** | Aplicação SaaS completa (frontend, backend, auth, billing, chat) |
| **debuga-qwen-coder-lab** (este) | Laboratório de IA local (Ollama, GPU, modelos, benchmarks) |

O debuga.ai homolog pode operar em 3 modos:

1. **LLM Cloud** — usa API cloud (padrão, sem GPU local)
2. **Ollama local** — Ollama no mesmo docker-compose (profile `gpu`)
3. **Ollama externo** — Ollama em outro host/VM com GPU dedicada

Este laboratório documenta os modos 2 e 3.

---

## Estrutura do Repositório

```
debuga-qwen-coder-lab/
├── README.md                    ← Este arquivo
├── docs/                        ← Documentação didática (9 módulos)
│   ├── 01-OLLAMA-O-QUE-E.md
│   ├── 02-GPU-HYPERV-DDA-RTX3090.md
│   ├── 03-DOCKER-NVIDIA-TOOLKIT.md
│   ├── 04-MODELOS-QWEN-COMPARATIVO.md
│   ├── 05-OLLAMA-API.md
│   ├── 06-SANDBOX-E-TOOL-CALLING.md
│   ├── 07-INTEGRACAO-COM-DEBUGA-HOMOLOG.md
│   ├── 08-BENCHMARKS-E-TESTES.md
│   └── 09-TROUBLESHOOTING.md
├── benchmarks/                  ← Datasets sintéticos e script de avaliação
├── prompts/                     ← Prompts públicos de exemplo
├── scripts/                     ← Scripts auxiliares
├── notebooks/                   ← Guias em formato notebook
├── fine-tuning/                 ← Guias de fine-tuning LoRA
└── requirements.txt             ← Dependências Python
```

---

## Modelos Recomendados para RTX 3090 (24 GB)

| Modelo | Parâmetros | VRAM (Q4) | Uso ideal |
|--------|-----------|-----------|-----------|
| qwen2.5:7b-instruct | 7B | ~5 GB | Chat geral, diagnóstico, documentação |
| qwen2.5-coder:7b | 7B | ~5 GB | Geração de código, scripts, automação |
| qwen2.5:14b | 14B | ~9 GB | Análise complexa, raciocínio avançado |
| qwen2.5-coder:14b | 14B | ~9 GB | Código complexo, refatoração |
| qwen3:14b | 14B | ~10 GB | Raciocínio híbrido (think/no-think) |
| qwen3:30b-a3b (MoE) | 30B (3B ativos) | ~19 GB | Máxima qualidade que cabe na 3090 |

Veja [docs/04-MODELOS-QWEN-COMPARATIVO.md](docs/04-MODELOS-QWEN-COMPARATIVO.md) para tabela completa.

---

## Quick Start

```bash
# 1. Verificar GPU
nvidia-smi

# 2. Subir Ollama com GPU
docker run -d --gpus all \
  -v ollama-data:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  --restart unless-stopped \
  ollama/ollama

# 3. Baixar modelo
docker exec ollama ollama pull qwen2.5:7b-instruct

# 4. Testar
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b-instruct",
  "prompt": "Explique o que é um firewall em 3 linhas.",
  "stream": false
}'
```

---

## Ecossistema

| Repositório | Função |
|---|---|
| [debuga-llm-stack](https://github.com/SperryTecnologia/debuga-llm-stack) | Documentação central e arquitetura da stack (público) |
| **debuga-qwen-coder-lab** (este) | Avaliação, benchmarks e laboratório GPU (privado) |
| [debuga-ai-homolog](https://github.com/SperryTecnologia/debuga-ai-homolog) | Pacote de deploy homolog (privado) |
| [debuga-vllm-engine](https://github.com/SperryTecnologia/debuga-vllm-engine) | Motor de inferência vLLM (planejado) |
| [debuga-llm-gateway](https://github.com/SperryTecnologia/debuga-llm-gateway) | Gateway de roteamento (planejado) |

---

## Acesso e Distribuição

Este repositório é **privado** e seu conteúdo é restrito a:

- Equipe interna da Sperry Tecnologia
- Alunos matriculados em treinamentos autorizados
- Clientes com contrato Enterprise ou White Label vigente

A redistribuição, cópia ou publicação parcial/total sem autorização expressa é proibida.

---

## Uso em Treinamento

Este repositório serve como material de laboratório para:

- Cursos de infraestrutura com IA (OpenInfra)
- Treinamentos White Label com GPU dedicada
- Workshops de DevOps + LLM local
- Avaliação de modelos para produção

---

## Atribuições

- **Qwen2.5 / Qwen3** são famílias de modelos criadas pela [equipe Qwen/Alibaba Cloud](https://huggingface.co/Qwen), licenciadas sob Apache 2.0
- **Ollama** é mantido pela [equipe Ollama](https://ollama.com), licenciado sob MIT
- **NVIDIA Container Toolkit** é mantido pela [NVIDIA](https://github.com/NVIDIA/nvidia-container-toolkit)

A Sperry Tecnologia não é autora desses projetos upstream. Este laboratório é construído com base em ferramentas open-source.

---

## Aviso de Segurança

- Todos os dados neste repositório são **sintéticos e públicos**
- Nenhum dado de cliente do debuga.ai está presente
- Nenhum prompt interno de produção está publicado
- Nenhum peso de modelo ou adapter LoRA está incluído
- Nenhum secret, API key ou credencial está presente

---

## Licença

Proprietária — Sperry Tecnologia LTDA. Veja [LICENSE](./LICENSE) para termos completos.

---

Desenvolvido por [Sperry Tecnologia](https://www.sperrytecnologia.com.br) — Tecnologia e Segurança da Informação
