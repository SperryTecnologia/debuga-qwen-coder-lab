# Notebook 02 — Quantização AWQ para Qwen-Coder

> Guia para quantizar modelos Qwen-Coder com AWQ (Activation-aware Weight Quantization).
> Baseado em [AutoAWQ](https://github.com/casper-hansen/AutoAWQ) e [vLLM](https://github.com/vllm-project/vllm).

## Contexto

A quantização AWQ reduz o tamanho do modelo de FP16 para INT4, diminuindo o consumo de VRAM em aproximadamente 75% com perda mínima de qualidade. Isso permite rodar modelos maiores em GPUs com menos memória.

| Modelo | FP16 (VRAM) | AWQ INT4 (VRAM) | Redução |
|--------|-------------|-----------------|---------|
| Qwen2.5-Coder-7B | ~14 GB | ~4 GB | ~71% |
| Qwen2.5-Coder-14B | ~28 GB | ~8 GB | ~71% |
| Qwen2.5-Coder-32B | ~64 GB | ~18 GB | ~72% |

## Pré-requisitos

```bash
pip install autoawq transformers torch
# ou
pip install -r requirements.txt
```

## 1. Usar Modelos AWQ Pré-quantizados (Recomendado)

A Qwen disponibiliza versões AWQ oficiais no Hugging Face:

```bash
# Download do modelo AWQ pré-quantizado
# Requer: huggingface-cli login (se modelo gated)

# 7B AWQ (~4 GB)
huggingface-cli download Qwen/Qwen2.5-Coder-7B-Instruct-AWQ

# 14B AWQ (~8 GB)
huggingface-cli download Qwen/Qwen2.5-Coder-14B-Instruct-AWQ
```

### Servir com vLLM

```bash
# Direto com modelo AWQ
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-7B-Instruct-AWQ \
  --quantization awq \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9

# Docker
docker run --gpus all -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-Coder-7B-Instruct-AWQ \
  --quantization awq \
  --max-model-len 4096
```

## 2. Quantizar Manualmente com AutoAWQ

Se precisar de uma quantização customizada (ex.: dataset de calibração específico):

```python
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model_path = "Qwen/Qwen2.5-Coder-7B-Instruct"
quant_path = "./qwen-coder-7b-awq"

# Configuração de quantização
quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,
    "version": "GEMM"
}

# Carregar modelo
model = AutoAWQForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

# Quantizar (usa dataset de calibração interno)
model.quantize(tokenizer, quant_config=quant_config)

# Salvar
model.save_quantized(quant_path)
tokenizer.save_pretrained(quant_path)

print(f"Modelo quantizado salvo em: {quant_path}")
```

### Quantização com Dataset de Calibração Customizado

Para domínios específicos (DevOps, segurança), usar exemplos do domínio como calibração pode melhorar a qualidade:

```python
import json

# Carregar exemplos do domínio como calibração
calibration_data = []
with open("benchmarks/devops-tasks.jsonl") as f:
    for line in f:
        task = json.loads(line)
        # Formatar como texto contínuo para calibração
        text = f"System: {task['system_prompt']}\nUser: {task['user_prompt']}"
        calibration_data.append(text)

# Quantizar com calibração customizada
model.quantize(
    tokenizer,
    quant_config=quant_config,
    calib_data=calibration_data
)
```

## 3. Benchmark: FP16 vs AWQ

```bash
# Rodar benchmark com FP16
python benchmarks/run-benchmark.py \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --dataset benchmarks/devops-tasks.jsonl \
  --output benchmarks/results/7b-fp16.csv

# Rodar benchmark com AWQ
python benchmarks/run-benchmark.py \
  --model Qwen/Qwen2.5-Coder-7B-Instruct-AWQ \
  --dataset benchmarks/devops-tasks.jsonl \
  --output benchmarks/results/7b-awq.csv
```

### Comparar Resultados

```python
import pandas as pd

fp16 = pd.read_csv("benchmarks/results/7b-fp16.csv")
awq = pd.read_csv("benchmarks/results/7b-awq.csv")

comparison = pd.DataFrame({
    "Métrica": ["Sucesso (%)", "Latência média (s)", "Tokens/s", "VRAM (GB)"],
    "FP16": [
        f"{fp16['success'].mean()*100:.1f}",
        f"{fp16['latency_seconds'].mean():.2f}",
        f"{fp16['tokens_used'].sum() / fp16['latency_seconds'].sum():.1f}",
        "~14"
    ],
    "AWQ INT4": [
        f"{awq['success'].mean()*100:.1f}",
        f"{awq['latency_seconds'].mean():.2f}",
        f"{awq['tokens_used'].sum() / awq['latency_seconds'].sum():.1f}",
        "~4"
    ]
})

print(comparison.to_markdown(index=False))
```

## 4. Quando Usar Quantização

| Cenário | Recomendação |
|---------|-------------|
| GPU com 8 GB VRAM | AWQ obrigatório para 7B |
| GPU com 16 GB VRAM | AWQ para 14B, FP16 para 7B |
| GPU com 24 GB VRAM | AWQ para 32B, FP16 para 14B |
| Multi-GPU (2x 24 GB) | FP16 para 32B com tensor parallelism |
| Máxima qualidade | FP16 sempre que a VRAM permitir |
| Máximo throughput | AWQ (menor VRAM = mais batch) |

## Referências

- [AutoAWQ](https://github.com/casper-hansen/AutoAWQ) — biblioteca de quantização
- [vLLM Quantization](https://docs.vllm.ai/en/latest/quantization/) — documentação oficial
- [Qwen2.5-Coder Models](https://huggingface.co/collections/Qwen/qwen25-coder-66eaa22e6f99801bf65b0c2f) — modelos no Hugging Face
