# debuga-qwen-coder-lab

Laboratório de avaliação de modelos [Qwen2.5-Coder](https://huggingface.co/Qwen) para tarefas de DevOps, infraestrutura de TI e segurança da informação. Parte da stack LLM do [debuga.ai](https://debuga.ai).

## Sobre

O **debuga-qwen-coder-lab** é um ambiente de experimentação para avaliar, comparar e otimizar modelos da família Qwen-Coder em tarefas técnicas específicas do domínio de TI e segurança. Todos os dados utilizados são **sintéticos e públicos** — nenhum dado de cliente, conversa real ou prompt interno do debuga.ai está presente neste repositório.

## Ecossistema

| Repositório | Função |
|---|---|
| [debuga-llm-stack](https://github.com/SperryTecnologia/debuga-llm-stack) | Documentação central e arquitetura da stack |
| **debuga-qwen-coder-lab** (este) | Avaliação e benchmarks de modelos |
| [debuga-vllm-engine](https://github.com/SperryTecnologia/debuga-vllm-engine) | Motor de inferência vLLM (planejado) |
| [debuga-llm-gateway](https://github.com/SperryTecnologia/debuga-llm-gateway) | Gateway de roteamento (planejado) |

## Tarefas Avaliadas

| Categoria | Tarefas |
|---|---|
| **Diagnóstico de Rede** | DNS resolution, traceroute analysis, latência |
| **Segurança** | Auditoria SSL/TLS, análise de firewall, hardening |
| **Resposta a Incidentes** | Triagem, contenção, análise de logs |
| **Containers** | Docker troubleshooting, compose debugging |
| **Automação** | Geração de scripts Bash/Python, cron jobs |
| **Configuração** | Server hardening, análise de configs |

## Quick Start

```bash
# Clone
git clone https://github.com/SperryTecnologia/debuga-qwen-coder-lab.git
cd debuga-qwen-coder-lab

# Instale dependências
pip install -r requirements.txt

# Execute benchmarks (requer vLLM rodando ou API compatível)
python benchmarks/run-benchmark.py \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --dataset benchmarks/devops-tasks.jsonl \
  --output benchmarks/results/
```

## Estrutura

```
benchmarks/          ← Datasets sintéticos e script de avaliação
  devops-tasks.jsonl ← Tarefas de DevOps (sintéticas)
  security-audit.jsonl ← Tarefas de segurança (sintéticas)
  network-diag.jsonl ← Tarefas de rede (sintéticas)
  run-benchmark.py   ← Script para executar avaliações
  results/           ← Resultados de benchmarks

notebooks/           ← Jupyter notebooks de avaliação
  01-model-comparison.ipynb
  02-devops-evaluation.ipynb
  03-security-tasks.ipynb
  04-quantization-impact.ipynb

prompts/             ← Prompts públicos de exemplo
  dns-diagnosis.md
  ssl-audit.md
  server-hardening.md
  incident-response.md
  docker-troubleshooting.md
  firewall-review.md
  bash-python-automation.md

datasets/            ← Datasets sintéticos para avaliação
  synthetic/         ← Gerados artificialmente, sem dados reais

fine-tuning/         ← Guias e scripts para fine-tuning LoRA
  prepare-dataset.py
  train-lora.py
  configs/

docs/                ← Documentação do laboratório
  evaluation-methodology.md
  model-selection.md
  safety-and-privacy.md
  roadmap.md
```

## Modelos Avaliados

| Modelo | Parâmetros | Quantização | Status |
|---|---|---|---|
| Qwen2.5-Coder-7B-Instruct | 7B | FP16, AWQ | Avaliado |
| Qwen2.5-Coder-14B-Instruct | 14B | FP16, AWQ | Avaliado |
| Qwen2.5-Coder-32B-Instruct | 32B | AWQ | Planejado |

## Metodologia

A avaliação segue critérios objetivos para cada tarefa:

1. **Correção técnica** — A resposta resolve o problema proposto?
2. **Completude** — Todos os passos necessários estão presentes?
3. **Segurança** — A solução não introduz vulnerabilidades?
4. **Clareza** — A explicação é compreensível para um profissional de TI?
5. **Eficiência** — A solução é otimizada para o cenário?

Veja [docs/evaluation-methodology.md](docs/evaluation-methodology.md) para detalhes.

## Atribuições

- **Qwen2.5-Coder** é uma família de modelos criada pela [equipe Qwen/Alibaba Cloud](https://huggingface.co/Qwen), licenciada sob Apache 2.0
- **HuggingFace Transformers** é mantido pela [Hugging Face](https://huggingface.co), licenciado sob Apache 2.0
- **PEFT** é mantido pela [Hugging Face](https://github.com/huggingface/peft), licenciado sob Apache 2.0

A Sperry Tecnologia não é autora desses projetos upstream. Este laboratório é compatível com (compatible with) modelos Qwen-Coder e construído com base em ferramentas open-source.

## Aviso de Segurança

- Todos os dados neste repositório são **sintéticos e públicos**
- Nenhum dado de cliente do debuga.ai está presente
- Nenhum prompt interno de produção está publicado
- Nenhum peso de modelo ou adapter LoRA está incluído
- Nenhum secret, API key ou credencial está presente
- Os prompts de exemplo são **genéricos e educacionais**, não representam os prompts reais do debuga.ai

## Licença

[Apache License 2.0](./LICENSE)

---

Desenvolvido por [Sperry Tecnologia](https://www.sperrytecnologia.com.br) — Tecnologia e Segurança da Informação
