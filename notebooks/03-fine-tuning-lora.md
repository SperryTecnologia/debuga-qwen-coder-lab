# Notebook 03 — Fine-Tuning com LoRA para Qwen-Coder

> Guia para fine-tuning de modelos Qwen-Coder com LoRA (Low-Rank Adaptation).
> Baseado em [PEFT](https://github.com/huggingface/peft) e [TRL](https://github.com/huggingface/trl).

## Contexto

O fine-tuning com LoRA permite adaptar o modelo para tarefas específicas de DevOps e segurança sem retreinar todos os parâmetros. Apenas uma fração dos pesos é atualizada, reduzindo drasticamente o custo computacional.

| Aspecto | Full Fine-Tuning | LoRA |
|---------|-----------------|------|
| Parâmetros treinados | 100% (~7B) | ~0.1% (~7M) |
| VRAM necessária (7B) | ~60 GB | ~16 GB |
| Tempo de treino (1k exemplos) | ~8h (A100) | ~1h (A100) |
| Risco de catastrophic forgetting | Alto | Baixo |
| Adaptadores reutilizáveis | Não | Sim (merge ou swap) |

## Pré-requisitos

```bash
pip install torch transformers peft trl datasets accelerate bitsandbytes
# ou
pip install -r requirements.txt
```

## 1. Preparar Dataset

O formato esperado é ChatML (compatível com Qwen-Coder):

```json
{
  "messages": [
    {"role": "system", "content": "Você é um especialista em infraestrutura Linux."},
    {"role": "user", "content": "O servidor está com load average 45.2. O que fazer?"},
    {"role": "assistant", "content": "Load average de 45.2 indica sobrecarga severa..."}
  ]
}
```

### Converter Benchmarks para Dataset de Treino

```python
import json

training_data = []

# Usar benchmarks como base (adicionar respostas de referência)
for jsonl_file in ["benchmarks/devops-tasks.jsonl", "benchmarks/security-audit.jsonl"]:
    with open(jsonl_file) as f:
        for line in f:
            task = json.loads(line)
            # Nota: expected_keywords não é resposta completa
            # Em produção, usar respostas validadas por especialistas
            training_data.append({
                "messages": [
                    {"role": "system", "content": task["system_prompt"]},
                    {"role": "user", "content": task["user_prompt"]},
                    # {"role": "assistant", "content": "<resposta validada>"}
                ]
            })

print(f"Exemplos base: {len(training_data)}")
print("ATENÇÃO: Adicione respostas validadas por especialistas antes de treinar.")
```

### Formato do Dataset Final

Salve como JSONL:

```python
with open("fine-tuning/data/train.jsonl", "w") as f:
    for example in training_data:
        f.write(json.dumps(example, ensure_ascii=False) + "\n")
```

## 2. Configuração LoRA

```python
from peft import LoraConfig, TaskType

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,                    # Rank (8-64, maior = mais capacidade)
    lora_alpha=32,           # Scaling factor (geralmente 2x rank)
    lora_dropout=0.05,       # Dropout para regularização
    target_modules=[         # Módulos do Qwen para adaptar
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj"
    ],
    bias="none"
)
```

### Escolha de Hiperparâmetros

| Parâmetro | Valor Sugerido | Notas |
|-----------|---------------|-------|
| `r` (rank) | 16 | 8 para datasets pequenos, 32-64 para grandes |
| `lora_alpha` | 32 | Geralmente 2x o rank |
| `lora_dropout` | 0.05 | 0.1 se overfitting |
| `learning_rate` | 2e-4 | Reduzir para 1e-4 se instável |
| `epochs` | 3 | 1-2 para datasets grandes (>10k) |
| `batch_size` | 4 | Ajustar conforme VRAM |
| `gradient_accumulation` | 4 | Simula batch_size maior |

## 3. Script de Treino

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import get_peft_model, LoraConfig, TaskType
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset

# Modelo base
model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"

# Quantização 4-bit para treino (QLoRA)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True
)

# Carregar modelo
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# Aplicar LoRA
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
    bias="none"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Saída esperada: trainable params: ~7M || all params: ~7B || trainable%: ~0.1%

# Dataset
dataset = load_dataset("json", data_files="fine-tuning/data/train.jsonl", split="train")

# Configuração de treino
training_config = SFTConfig(
    output_dir="./fine-tuning/output/qwen-coder-7b-devops-lora",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    weight_decay=0.01,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    logging_steps=10,
    save_strategy="epoch",
    bf16=True,
    max_seq_length=2048,
    dataset_text_field="text",  # ou usar formatting_func
)

# Trainer
trainer = SFTTrainer(
    model=model,
    args=training_config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)

# Treinar
trainer.train()

# Salvar adaptador LoRA
trainer.save_model("./fine-tuning/output/qwen-coder-7b-devops-lora/final")
```

## 4. Merge e Deploy

### Opção A: Servir com Adaptador Separado (vLLM)

```bash
# vLLM suporta LoRA adapters nativamente
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --enable-lora \
  --lora-modules devops=./fine-tuning/output/qwen-coder-7b-devops-lora/final \
  --max-lora-rank 16
```

### Opção B: Merge para Modelo Único

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# Carregar modelo base (FP16)
base_model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    torch_dtype=torch.float16,
    device_map="auto"
)

# Carregar e mergear adaptador
model = PeftModel.from_pretrained(
    base_model,
    "./fine-tuning/output/qwen-coder-7b-devops-lora/final"
)
merged_model = model.merge_and_unload()

# Salvar modelo mergeado
merged_model.save_pretrained("./models/qwen-coder-7b-devops-merged")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-7B-Instruct")
tokenizer.save_pretrained("./models/qwen-coder-7b-devops-merged")
```

## 5. Avaliar Modelo Fine-Tuned

```bash
# Benchmark com modelo fine-tuned
python benchmarks/run-benchmark.py \
  --model ./models/qwen-coder-7b-devops-merged \
  --dataset benchmarks/devops-tasks.jsonl \
  --output benchmarks/results/7b-finetuned.csv

# Comparar com base
python benchmarks/run-benchmark.py \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --dataset benchmarks/devops-tasks.jsonl \
  --output benchmarks/results/7b-base.csv
```

## Referências

- [PEFT](https://github.com/huggingface/peft) — Parameter-Efficient Fine-Tuning
- [TRL](https://github.com/huggingface/trl) — Transformer Reinforcement Learning
- [QLoRA Paper](https://arxiv.org/abs/2305.14314) — Efficient Finetuning of Quantized LLMs
- [Qwen2.5-Coder Technical Report](https://arxiv.org/abs/2409.12186) — detalhes da arquitetura
