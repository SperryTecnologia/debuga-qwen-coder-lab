# Guia de Seleção de Modelos Qwen-Coder

## Família Qwen2.5-Coder

A família [Qwen2.5-Coder](https://huggingface.co/collections/Qwen/qwen25-coder-66eaa22e6f99801bf65b0c2f) é uma série de modelos de linguagem especializados em código, desenvolvidos pela equipe Qwen (Alibaba). Os modelos são open-weight e disponíveis sob licença Apache 2.0.

## Modelos Disponíveis

| Modelo | Parâmetros | VRAM (FP16) | VRAM (AWQ) | Contexto | Uso Recomendado |
|--------|-----------|-------------|------------|----------|-----------------|
| Qwen2.5-Coder-1.5B-Instruct | 1.5B | ~3 GB | ~1 GB | 32K | Autocompletar, tarefas simples |
| Qwen2.5-Coder-3B-Instruct | 3B | ~6 GB | ~2 GB | 32K | Scripts curtos, diagnóstico básico |
| Qwen2.5-Coder-7B-Instruct | 7B | ~14 GB | ~4 GB | 32K | DevOps, segurança, automação |
| Qwen2.5-Coder-14B-Instruct | 14B | ~28 GB | ~8 GB | 32K | Análise complexa, multi-step |
| Qwen2.5-Coder-32B-Instruct | 32B | ~64 GB | ~18 GB | 32K | Máxima qualidade, raciocínio avançado |

## Critérios de Seleção

### 1. Hardware Disponível

| GPU | VRAM | Modelo Máximo (FP16) | Modelo Máximo (AWQ) |
|-----|------|---------------------|---------------------|
| RTX 3060 | 12 GB | 3B | 7B |
| RTX 3070 Ti | 8 GB | 3B | 7B |
| RTX 3090 / 4090 | 24 GB | 14B | 32B (apertado) |
| A10G | 24 GB | 14B | 32B (apertado) |
| A100 40 GB | 40 GB | 14B | 32B |
| A100 80 GB | 80 GB | 32B | 32B + batch grande |
| H100 80 GB | 80 GB | 32B | 32B + batch grande |

### 2. Tipo de Tarefa

| Tarefa | Modelo Mínimo | Modelo Recomendado |
|--------|--------------|-------------------|
| Autocompletar código | 1.5B | 3B |
| Gerar scripts Bash simples | 3B | 7B |
| Diagnóstico de rede | 7B | 14B |
| Auditoria de segurança | 7B | 14B |
| Análise de logs complexos | 14B | 32B |
| Planejamento de incident response | 14B | 32B |
| Geração de relatórios técnicos | 14B | 32B |
| Raciocínio multi-step (cadeia de diagnóstico) | 14B | 32B |

### 3. Requisitos de Latência

| Cenário | Latência Aceitável | Modelo Sugerido |
|---------|-------------------|-----------------|
| Chat interativo | < 2s primeiro token | 7B AWQ |
| Análise sob demanda | < 5s primeiro token | 14B AWQ |
| Batch processing | Sem limite | 32B FP16 |
| Autocompletar IDE | < 500ms | 1.5B-3B |

### 4. Throughput vs Qualidade

```
Throughput alto + Qualidade boa    → 7B AWQ (melhor tokens/s)
Qualidade alta + Throughput médio  → 14B AWQ (melhor trade-off)
Máxima qualidade                   → 32B FP16 (mais lento, melhor resultado)
```

## Recomendação para debuga.ai

Para o contexto de DevOps, segurança e infraestrutura:

### Fase 1 — Avaliação (Atual)

- **Modelo**: Qwen2.5-Coder-7B-Instruct-AWQ
- **Hardware**: 1x GPU com 8+ GB VRAM
- **Motivo**: menor custo, suficiente para validar a abordagem

### Fase 2 — Produção Inicial

- **Modelo**: Qwen2.5-Coder-14B-Instruct-AWQ
- **Hardware**: 1x GPU com 16+ GB VRAM
- **Motivo**: melhor qualidade para tarefas de segurança e diagnóstico

### Fase 3 — Produção com Fine-Tuning

- **Modelo**: Qwen2.5-Coder-14B-Instruct + LoRA DevOps
- **Hardware**: 1x GPU com 24 GB VRAM
- **Motivo**: modelo adaptado ao domínio, qualidade superior ao 32B genérico em tarefas específicas

### Fase 4 — Escala

- **Modelo**: Qwen2.5-Coder-32B-Instruct (ou futuro Qwen3-Coder)
- **Hardware**: 2x GPU com 24+ GB VRAM (tensor parallel)
- **Motivo**: máxima qualidade para clientes Enterprise

## Comparação com Outros Modelos

| Modelo | Parâmetros | Licença | Foco | Notas |
|--------|-----------|---------|------|-------|
| Qwen2.5-Coder | 1.5B-32B | Apache 2.0 | Código | Melhor open-weight para código |
| DeepSeek-Coder-V2 | 16B/236B | Proprietária | Código | Forte, mas licença restritiva |
| CodeLlama | 7B-70B | Llama 2 | Código | Boa base, comunidade grande |
| StarCoder2 | 3B-15B | BigCode | Código | Foco em autocompletar |
| Mistral/Mixtral | 7B/8x7B | Apache 2.0 | Geral | Bom, mas não especializado em código |

**Nota**: esta comparação reflete o estado em meados de 2025. Novos modelos são lançados frequentemente.

## Referências

- [Qwen2.5-Coder Technical Report](https://arxiv.org/abs/2409.12186)
- [Qwen2.5-Coder Models](https://huggingface.co/collections/Qwen/qwen25-coder-66eaa22e6f99801bf65b0c2f)
- [vLLM Supported Models](https://docs.vllm.ai/en/latest/models/supported_models.html)
