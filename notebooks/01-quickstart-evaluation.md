# Notebook 01 — Quick Start: Avaliação de Qwen-Coder

> Este notebook guia a primeira avaliação de um modelo Qwen-Coder localmente.
> Para executar como Jupyter Notebook, renomeie para `.ipynb` ou use Jupytext.

## Pré-requisitos

```bash
# Instalar dependências
pip install -r requirements.txt

# Verificar GPU disponível
nvidia-smi

# Verificar VRAM disponível (mínimo 8GB para 7B AWQ)
nvidia-smi --query-gpu=memory.free --format=csv
```

## 1. Iniciar vLLM com Qwen-Coder-7B

```bash
# Opção A: Docker (recomendado)
docker run --gpus all -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9

# Opção B: Direto (se vLLM instalado)
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --max-model-len 4096
```

## 2. Verificar que o Modelo está Pronto

```python
import requests

response = requests.get("http://localhost:8000/v1/models")
print(response.json())
# Deve listar: Qwen/Qwen2.5-Coder-7B-Instruct
```

## 3. Primeira Consulta

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "model": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "messages": [
            {"role": "system", "content": "Você é um especialista em infraestrutura Linux."},
            {"role": "user", "content": "Como verificar se um servidor tem conexões em TIME_WAIT excessivas e como resolver?"}
        ],
        "temperature": 0.1,
        "max_tokens": 1024
    }
)

result = response.json()
print(result["choices"][0]["message"]["content"])
print(f"\nTokens: {result['usage']['total_tokens']}")
```

## 4. Rodar Benchmark Completo

```bash
python benchmarks/run-benchmark.py \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --dataset benchmarks/devops-tasks.jsonl \
  --api-url http://localhost:8000/v1
```

## 5. Comparar com Outro Modelo

```bash
# Trocar para 14B (precisa de mais VRAM)
# Parar o container anterior e iniciar com novo modelo

python benchmarks/run-benchmark.py \
  --model Qwen/Qwen2.5-Coder-14B-Instruct \
  --dataset benchmarks/devops-tasks.jsonl \
  --api-url http://localhost:8000/v1
```

## 6. Analisar Resultados

```python
import pandas as pd
import glob

# Carregar todos os resultados
files = glob.glob("benchmarks/results/*.csv")
for f in sorted(files):
    df = pd.read_csv(f)
    model = f.split("/")[-1]
    print(f"\n{model}")
    print(f"  Sucesso: {df['success'].mean()*100:.0f}%")
    print(f"  Latência: {df['latency_seconds'].mean():.2f}s")
    print(f"  Tokens: {df['tokens_used'].mean():.0f}")
```

## Próximos Passos

- Testar com quantização AWQ (ver `docs/quantization-guide.md`)
- Avaliar prompts específicos (ver `prompts/`)
- Comparar com datasets de segurança (`benchmarks/security-audit.jsonl`)
