# 08 — Benchmarks e Testes

## Objetivo

Este documento define um roteiro prático para avaliar modelos LLM locais no contexto do debuga.ai. Os benchmarks medem:

1. **Velocidade** — tokens por segundo (tok/s)
2. **Qualidade** — relevância e precisão das respostas
3. **Consistência** — mesma pergunta, mesma qualidade em múltiplas execuções
4. **Adequação** — o modelo responde dentro do escopo esperado (infra, segurança, DevOps)

---

## Métricas Fundamentais

| Métrica | O que mede | Como calcular | Meta (RTX 3090) |
|---------|-----------|---------------|-----------------|
| **Tokens/s (geração)** | Velocidade de output | `eval_count / (eval_duration / 1e9)` | >20 tok/s (7B), >10 tok/s (14B) |
| **Time to First Token (TTFT)** | Latência inicial | `prompt_eval_duration` | <2s (modelo já carregado) |
| **Total Duration** | Tempo total da requisição | `total_duration` | <10s para respostas curtas |
| **Prompt Eval Speed** | Velocidade de processamento do input | `prompt_eval_count / (prompt_eval_duration / 1e9)` | >100 tok/s |

---

## Script de Benchmark Básico

### benchmark.sh

```bash
#!/bin/bash
# Benchmark básico para Ollama
# Uso: ./benchmark.sh <modelo> [num_runs]

MODEL=${1:-"qwen2.5:7b-instruct"}
RUNS=${2:-5}
OLLAMA_URL=${OLLAMA_URL:-"http://localhost:11434"}

echo "=== Benchmark: $MODEL ==="
echo "Runs: $RUNS"
echo "URL: $OLLAMA_URL"
echo ""

PROMPTS=(
  "Explique o que é um firewall em 3 linhas."
  "Liste 5 comandos Linux para diagnóstico de rede."
  "O que pode causar timeout em uma conexão SSH?"
  "Gere um script bash para verificar uso de disco."
  "Analise este log: 'Jan 15 10:30:01 server sshd[12345]: Failed password for root from 192.168.1.100 port 54321 ssh2'"
)

total_tokens=0
total_time=0

for i in $(seq 1 $RUNS); do
  PROMPT_IDX=$(( (i - 1) % ${#PROMPTS[@]} ))
  PROMPT="${PROMPTS[$PROMPT_IDX]}"

  echo "--- Run $i: ${PROMPT:0:50}..."

  RESPONSE=$(curl -s "$OLLAMA_URL/api/generate" -d "{
    \"model\": \"$MODEL\",
    \"prompt\": \"$PROMPT\",
    \"stream\": false
  }")

  EVAL_COUNT=$(echo "$RESPONSE" | jq '.eval_count')
  EVAL_DURATION=$(echo "$RESPONSE" | jq '.eval_duration')
  TOTAL_DURATION=$(echo "$RESPONSE" | jq '.total_duration')

  if [ "$EVAL_DURATION" != "null" ] && [ "$EVAL_DURATION" != "0" ]; then
    TOKS=$(echo "scale=2; $EVAL_COUNT / ($EVAL_DURATION / 1000000000)" | bc)
    TOTAL_SEC=$(echo "scale=2; $TOTAL_DURATION / 1000000000" | bc)

    echo "  Tokens: $EVAL_COUNT | Speed: ${TOKS} tok/s | Total: ${TOTAL_SEC}s"

    total_tokens=$((total_tokens + EVAL_COUNT))
    total_time=$(echo "$total_time + $TOTAL_SEC" | bc)
  else
    echo "  ERRO: resposta inválida"
  fi
done

echo ""
echo "=== Resumo ==="
echo "Total tokens gerados: $total_tokens"
echo "Tempo total: ${total_time}s"
if [ "$total_time" != "0" ]; then
  AVG=$(echo "scale=2; $total_tokens / $total_time" | bc)
  echo "Média geral: ${AVG} tok/s"
fi
```

### Uso

```bash
chmod +x benchmark.sh

# Benchmark com modelo padrão
./benchmark.sh qwen2.5:7b-instruct 10

# Benchmark com modelo maior
./benchmark.sh qwen3:14b 5

# Benchmark apontando para Ollama externo
OLLAMA_URL=http://192.0.2.20:11434 ./benchmark.sh qwen2.5:7b-instruct 10
```

---

## Testes de Qualidade

### Categorias de Teste

| Categoria | O que testa | Exemplo de prompt |
|-----------|------------|-------------------|
| **Diagnóstico de rede** | Capacidade de analisar problemas de rede | "O traceroute mostra timeout no hop 5. O que pode ser?" |
| **Segurança** | Identificação de ameaças e recomendações | "Analise este log de SSH e identifique se é ataque." |
| **Geração de código** | Qualidade do código gerado | "Gere um script bash para backup incremental." |
| **Documentação** | Capacidade de explicar conceitos | "Explique a diferença entre TCP e UDP para um iniciante." |
| **Análise de logs** | Extração de informações de logs | "Extraia IP, porta e serviço deste log: ..." |
| **Recomendação** | Sugestões práticas e acionáveis | "Recomende hardening para um servidor Ubuntu exposto." |

### Dataset de Teste (prompts/test_prompts.json)

```json
[
  {
    "id": "net-001",
    "category": "network",
    "prompt": "O comando 'ping 8.8.8.8' funciona mas 'ping google.com' falha. O que está acontecendo?",
    "expected_keywords": ["DNS", "resolução", "nameserver", "/etc/resolv.conf"],
    "difficulty": "easy"
  },
  {
    "id": "sec-001",
    "category": "security",
    "prompt": "Recebi 500 tentativas de login SSH em 10 minutos do mesmo IP. O que devo fazer imediatamente?",
    "expected_keywords": ["fail2ban", "firewall", "bloquear", "ufw", "iptables"],
    "difficulty": "easy"
  },
  {
    "id": "code-001",
    "category": "code",
    "prompt": "Gere um script bash que monitore o uso de CPU e envie alerta se ultrapassar 90% por mais de 5 minutos.",
    "expected_keywords": ["#!/bin/bash", "top", "mpstat", "if", "mail", "sleep"],
    "difficulty": "medium"
  },
  {
    "id": "net-002",
    "category": "network",
    "prompt": "Um container Docker não consegue acessar a internet mas consegue pingar outros containers na mesma rede. Diagnóstico?",
    "expected_keywords": ["NAT", "iptables", "bridge", "DNS", "gateway", "docker network"],
    "difficulty": "medium"
  },
  {
    "id": "sec-002",
    "category": "security",
    "prompt": "Encontrei um processo chamado 'kworker' usando 100% de CPU. É normal ou pode ser minerador?",
    "expected_keywords": ["kworker", "kernel", "minerador", "top", "strace", "hash"],
    "difficulty": "hard"
  }
]
```

---

## Script de Avaliação de Qualidade

### evaluate.py

```python
#!/usr/bin/env python3
"""
Avaliador de qualidade para respostas do Ollama.
Verifica se keywords esperadas aparecem na resposta.
"""

import json
import requests
import sys
from datetime import datetime

OLLAMA_URL = "http://localhost:11434"

def evaluate_prompt(model: str, test_case: dict) -> dict:
    """Envia prompt ao Ollama e avalia a resposta."""
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": test_case["prompt"],
            "stream": False
        },
        timeout=60
    )

    data = response.json()
    answer = data.get("response", "").lower()

    # Verificar keywords
    found = []
    missing = []
    for kw in test_case["expected_keywords"]:
        if kw.lower() in answer:
            found.append(kw)
        else:
            missing.append(kw)

    score = len(found) / len(test_case["expected_keywords"]) * 100

    return {
        "id": test_case["id"],
        "category": test_case["category"],
        "difficulty": test_case["difficulty"],
        "score": score,
        "found_keywords": found,
        "missing_keywords": missing,
        "tokens": data.get("eval_count", 0),
        "duration_s": data.get("total_duration", 0) / 1e9
    }


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5:7b-instruct"
    test_file = sys.argv[2] if len(sys.argv) > 2 else "prompts/test_prompts.json"

    with open(test_file) as f:
        tests = json.load(f)

    print(f"=== Avaliação de Qualidade: {model} ===")
    print(f"Data: {datetime.now().isoformat()}")
    print(f"Testes: {len(tests)}")
    print()

    results = []
    for test in tests:
        print(f"  [{test['id']}] {test['prompt'][:60]}...")
        result = evaluate_prompt(model, test)
        results.append(result)
        print(f"    Score: {result['score']:.0f}% | Tokens: {result['tokens']} | Tempo: {result['duration_s']:.1f}s")
        if result['missing_keywords']:
            print(f"    Missing: {', '.join(result['missing_keywords'])}")

    # Resumo
    avg_score = sum(r["score"] for r in results) / len(results)
    avg_tokens = sum(r["tokens"] for r in results) / len(results)
    avg_time = sum(r["duration_s"] for r in results) / len(results)

    print()
    print("=== Resumo ===")
    print(f"Score médio: {avg_score:.1f}%")
    print(f"Tokens médios: {avg_tokens:.0f}")
    print(f"Tempo médio: {avg_time:.1f}s")

    # Salvar resultados
    output_file = f"benchmarks/results_{model.replace(':', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "model": model,
            "date": datetime.now().isoformat(),
            "summary": {
                "avg_score": avg_score,
                "avg_tokens": avg_tokens,
                "avg_time_s": avg_time
            },
            "results": results
        }, f, indent=2)
    print(f"Resultados salvos em: {output_file}")


if __name__ == "__main__":
    main()
```

### Uso

```bash
# Instalar dependências
pip install requests

# Executar avaliação
python evaluate.py qwen2.5:7b-instruct prompts/test_prompts.json
python evaluate.py qwen3:14b prompts/test_prompts.json

# Comparar resultados
ls benchmarks/results_*.json
```

---

## Resultados Esperados (RTX 3090)

### Velocidade

| Modelo | Tokens/s (Q4) | TTFT | Observação |
|--------|--------------|------|------------|
| qwen2.5:7b-instruct | 35-45 tok/s | <1s | Muito rápido, ideal para chat |
| qwen2.5-coder:7b | 35-45 tok/s | <1s | Similar ao instruct |
| qwen2.5:14b | 18-25 tok/s | 1-2s | Bom para produção |
| qwen3:14b | 15-22 tok/s | 1-2s | Ligeiramente mais lento (think mode) |
| qwen3:30b-a3b | 12-18 tok/s | 2-3s | MoE, qualidade alta |

### Qualidade (Score médio esperado)

| Modelo | Rede | Segurança | Código | Docs | Geral |
|--------|------|-----------|--------|------|-------|
| qwen2.5:7b-instruct | 70-80% | 65-75% | 60-70% | 80-90% | 70-80% |
| qwen2.5-coder:7b | 60-70% | 55-65% | 80-90% | 70-80% | 65-75% |
| qwen2.5:14b | 80-90% | 75-85% | 70-80% | 85-95% | 80-85% |
| qwen3:14b | 85-90% | 80-85% | 75-85% | 85-95% | 82-88% |

---

## Teste de Estresse

### Concorrência

```bash
#!/bin/bash
# Teste de concorrência: N requisições simultâneas
CONCURRENT=${1:-5}
MODEL="qwen2.5:7b-instruct"

echo "=== Teste de Estresse: $CONCURRENT requisições simultâneas ==="

for i in $(seq 1 $CONCURRENT); do
  (
    START=$(date +%s%N)
    curl -s http://localhost:11434/api/generate -d "{
      \"model\": \"$MODEL\",
      \"prompt\": \"Explique DNS em 2 linhas.\",
      \"stream\": false
    }" > /dev/null
    END=$(date +%s%N)
    ELAPSED=$(echo "scale=2; ($END - $START) / 1000000000" | bc)
    echo "  Request $i: ${ELAPSED}s"
  ) &
done

wait
echo "=== Concluído ==="
```

### Monitoramento de VRAM durante estresse

```bash
# Em outro terminal, monitorar VRAM
watch -n 1 nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader
```

---

## Teste de Contexto Longo

```bash
# Gerar prompt longo (simular conversa com histórico)
LONG_PROMPT=$(python3 -c "
import json
msgs = [{'role': 'user', 'content': f'Mensagem {i}: Explique o conceito {i} de redes.'} for i in range(20)]
msgs.append({'role': 'user', 'content': 'Resuma todos os conceitos mencionados acima.'})
print(json.dumps({'model': 'qwen2.5:7b-instruct', 'messages': msgs, 'stream': False}))
")

echo "$LONG_PROMPT" | curl -s http://localhost:11434/api/chat -d @- | jq '{
  eval_count: .eval_count,
  prompt_eval_count: .prompt_eval_count,
  total_duration_s: (.total_duration / 1e9)
}'
```

---

## Checklist de Testes

```
[ ] nvidia-smi mostra GPU com VRAM disponível
[ ] Ollama respondendo (curl http://localhost:11434)
[ ] Modelo carregado (ollama ps)
[ ] benchmark.sh executa sem erros
[ ] Velocidade dentro do esperado (>20 tok/s para 7B)
[ ] evaluate.py executa sem erros
[ ] Score médio >70% para modelo 7B
[ ] Teste de estresse não causa OOM
[ ] Contexto longo não trava o modelo
[ ] Resultados salvos em benchmarks/
```

---

## Próximo Passo

Se encontrar problemas durante os testes, consulte [09-TROUBLESHOOTING.md](09-TROUBLESHOOTING.md).
