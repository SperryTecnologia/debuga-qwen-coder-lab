# Guia de Quantização para Qwen-Coder

## Visão Geral

A quantização reduz a precisão numérica dos pesos do modelo (FP16 → INT4/INT8), diminuindo o consumo de VRAM e aumentando o throughput, com perda mínima de qualidade para a maioria das tarefas.

## Métodos Suportados

| Método | Precisão | Qualidade | Velocidade | Complexidade |
|--------|----------|-----------|------------|-------------|
| **AWQ** (INT4) | 4-bit | Alta | Rápida | Baixa |
| **GPTQ** (INT4) | 4-bit | Alta | Rápida | Média |
| **SqueezeLLM** (INT4) | 4-bit | Muito alta | Média | Alta |
| **FP8** | 8-bit | Muito alta | Rápida | Baixa |
| **BitsAndBytes** (NF4) | 4-bit | Alta | Média | Baixa |

**Recomendação**: AWQ para produção com vLLM. BitsAndBytes NF4 para treino (QLoRA).

## Requisitos de VRAM por Modelo e Método

| Modelo | FP16 | FP8 | AWQ/GPTQ (INT4) |
|--------|------|-----|-----------------|
| Qwen2.5-Coder-1.5B | ~3 GB | ~2 GB | ~1 GB |
| Qwen2.5-Coder-7B | ~14 GB | ~8 GB | ~4 GB |
| Qwen2.5-Coder-14B | ~28 GB | ~16 GB | ~8 GB |
| Qwen2.5-Coder-32B | ~64 GB | ~36 GB | ~18 GB |

**Nota**: valores aproximados. O consumo real depende de `max_model_len`, batch size e overhead do framework.

## AWQ com vLLM (Produção)

### Usar Modelos Pré-quantizados

A Qwen disponibiliza versões AWQ oficiais:

```bash
# Servir diretamente (vLLM detecta AWQ automaticamente)
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-7B-Instruct-AWQ \
  --quantization awq \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9
```

### Quantizar Manualmente

Ver `notebooks/02-quantization-awq.md` para o guia completo com AutoAWQ.

## FP8 com vLLM (Hopper/Ada GPUs)

Para GPUs com suporte nativo a FP8 (H100, L40S, RTX 4090):

```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --quantization fp8 \
  --max-model-len 8192
```

**Vantagem**: qualidade quase idêntica a FP16 com ~50% menos VRAM.

## Impacto na Qualidade

Resultados observados em benchmarks de DevOps (ver `benchmarks/results/`):

| Modelo | Método | Sucesso (%) | Latência (s) | Notas |
|--------|--------|------------|--------------|-------|
| 7B | FP16 | Baseline | Baseline | Referência |
| 7B | AWQ | -1 a -3% | -20 a -30% | Excelente trade-off |
| 7B | GPTQ | -1 a -3% | -15 a -25% | Similar ao AWQ |
| 14B | AWQ | Baseline 14B | -20 a -30% | Melhor que 7B FP16 |

**Conclusão**: um modelo 14B quantizado (AWQ) geralmente supera um 7B em FP16, usando VRAM similar (~8 GB vs ~14 GB).

## Recomendações por Hardware

| GPU | VRAM | Modelo Recomendado |
|-----|------|--------------------|
| RTX 3060 | 12 GB | 7B AWQ |
| RTX 3090 / 4090 | 24 GB | 14B AWQ ou 7B FP16 |
| A100 40 GB | 40 GB | 14B FP16 ou 32B AWQ |
| A100 80 GB | 80 GB | 32B FP16 |
| 2x RTX 3090 | 48 GB | 32B AWQ (tensor parallel) |
| 2x A100 80 GB | 160 GB | 32B FP16 + batch grande |

## Referências

- [vLLM Quantization Docs](https://docs.vllm.ai/en/latest/quantization/)
- [AutoAWQ](https://github.com/casper-hansen/AutoAWQ)
- [Qwen2.5-Coder AWQ Models](https://huggingface.co/Qwen)
