# 04 — Comparativo de Modelos Qwen

## Famílias de Modelos

A Alibaba Cloud (equipe Qwen) mantém duas gerações principais de modelos open-source relevantes para este laboratório:

| Família | Lançamento | Características |
|---------|-----------|-----------------|
| **Qwen 2.5** | Set/2024 | Modelos densos, estáveis, bem testados. Variantes "instruct" e "coder". |
| **Qwen 3** | Abr/2025 | Nova geração com modo híbrido "think/no-think". Inclui variantes MoE (Mixture of Experts). |

---

## Conceitos Fundamentais

### Instruct vs Coder

| Tipo | Treinamento | Uso ideal |
|------|------------|-----------|
| **instruct** | Fine-tuned para seguir instruções gerais | Chat, diagnóstico, documentação, análise de logs |
| **coder** | Fine-tuned para geração e análise de código | Scripts, automação, refatoração, debugging |

O modelo "coder" não é melhor em tudo — ele é **especializado em código**. Para tarefas de chat geral, diagnóstico de rede ou geração de documentação, o "instruct" tende a ser superior.

### Modelo Geral vs Modelo de Código

- **Geral (instruct):** Entende contexto amplo, segue instruções complexas, gera texto estruturado, analisa logs, responde perguntas técnicas.
- **Código (coder):** Gera código funcional, entende sintaxe de múltiplas linguagens, sugere correções, refatora, gera testes.

Para o debuga.ai, a recomendação é usar **instruct** como modelo principal (chat e diagnóstico) e **coder** como modelo secundário (geração de scripts e automação).

### Parâmetros: 7B vs 14B vs 32B

| Tamanho | Qualidade | Velocidade | VRAM (Q4) | Indicação |
|---------|-----------|-----------|-----------|-----------|
| **7B** | Boa para tarefas simples | Muito rápida (~40 tok/s na 3090) | ~5 GB | Desenvolvimento, testes, chat rápido |
| **14B** | Boa para tarefas complexas | Rápida (~20 tok/s na 3090) | ~9 GB | Produção com qualidade |
| **32B** | Excelente | Moderada (~8 tok/s na 3090) | ~20 GB | Máxima qualidade, análise profunda |

### Quantização

Quantização reduz a precisão dos pesos do modelo para economizar VRAM e aumentar velocidade, com perda mínima de qualidade:

| Quantização | Bits | VRAM relativa | Qualidade | Uso |
|-------------|------|--------------|-----------|-----|
| FP16 | 16 | 100% (baseline) | Máxima | Pesquisa, benchmark |
| Q8 | 8 | ~50% | Quase idêntica | Produção premium |
| Q5_K_M | 5 | ~35% | Muito boa | Produção balanceada |
| **Q4_K_M** | 4 | ~30% | Boa | **Recomendado para RTX 3090** |
| Q3_K_M | 3 | ~25% | Aceitável | Quando VRAM é crítica |
| Q2_K | 2 | ~20% | Degradada | Não recomendado |

O Ollama usa **Q4_K_M por padrão** ao baixar modelos (ex: `ollama pull qwen2.5:7b-instruct`).

### VRAM e Contexto

A VRAM é consumida por dois fatores:

1. **Pesos do modelo** — fixo, depende do tamanho e quantização
2. **KV Cache (contexto)** — cresce com o número de tokens na conversa

Fórmula aproximada:
```
VRAM total = Pesos do modelo + KV Cache
KV Cache ≈ 2 × num_layers × hidden_size × context_length × 2 bytes (FP16)
```

Na prática para RTX 3090 (24 GB):

| Modelo (Q4) | Pesos | VRAM livre para contexto | Contexto prático |
|-------------|-------|-------------------------|-----------------|
| 7B | ~5 GB | ~19 GB | 32K+ tokens |
| 14B | ~9 GB | ~15 GB | 16K-32K tokens |
| 32B | ~20 GB | ~4 GB | 4K-8K tokens |

### Velocidade vs Qualidade

| Prioridade | Modelo recomendado | Tokens/s (3090) | Cenário |
|-----------|-------------------|-----------------|---------|
| Velocidade | qwen2.5:7b-instruct | ~40 tok/s | Chat em tempo real, respostas rápidas |
| Equilíbrio | qwen2.5:14b ou qwen3:14b | ~20 tok/s | Produção, diagnóstico detalhado |
| Qualidade | qwen3:30b-a3b | ~15 tok/s | Análise complexa, relatórios |

---

## Tabela Comparativa Completa

| Modelo | Tipo | Parâmetros | VRAM (Q4) | Contexto | Cabe na RTX 3090? | Uso ideal | Observações |
|--------|------|-----------|-----------|----------|-------------------|-----------|-------------|
| qwen2.5:7b-instruct | Geral | 7B | ~5 GB | 128K (32K prático) | Sim, com folga | Chat, diagnóstico, docs | Modelo padrão do lab. Rápido e confiável. |
| qwen2.5-coder:7b | Código | 7B | ~5 GB | 128K (32K prático) | Sim, com folga | Scripts, automação, debug | Melhor que instruct para gerar código. |
| qwen2.5:14b | Geral | 14B | ~9 GB | 128K (16K prático) | Sim | Análise complexa, raciocínio | Upgrade de qualidade sobre 7B. |
| qwen2.5-coder:14b | Código | 14B | ~9 GB | 128K (16K prático) | Sim | Código complexo, refatoração | Melhor modelo de código que cabe confortável. |
| qwen2.5-coder:32b | Código | 32B | ~20 GB | 128K (4K prático) | Sim, apertado | Código avançado, arquitetura | Contexto limitado. Usar para tarefas curtas. |
| qwen3:8b | Geral | 8B | ~5.5 GB | 128K (32K prático) | Sim, com folga | Chat com raciocínio híbrido | Modo think/no-think. Mais novo que 2.5:7b. |
| qwen3:14b | Geral | 14B | ~10 GB | 128K (16K prático) | Sim | Raciocínio avançado, análise | Think mode para problemas complexos. |
| qwen3:30b-a3b | MoE | 30B total (3B ativos) | ~19 GB | 128K (8K prático) | Sim, justo | Máxima qualidade na 3090 | MoE: 128 experts, 8 ativos. Qualidade de 30B com velocidade de 3B. |
| qwen3:32b | Geral | 32B | ~20 GB | 128K (4K prático) | Sim, apertado | Análise profunda | Denso. Contexto muito limitado na 3090. |

---

## Recomendações para RTX 3090

### Cenário 1: Desenvolvimento e Testes

```bash
ollama pull qwen2.5:7b-instruct
```

Modelo leve, rápido, ideal para iterar. Contexto amplo. Perfeito para testar integração com debuga.ai.

### Cenário 2: Produção (Chat + Diagnóstico)

```bash
ollama pull qwen3:14b
```

Melhor equilíbrio qualidade/velocidade. Modo think/no-think permite respostas rápidas ou raciocínio profundo conforme necessidade.

### Cenário 3: Produção (Código + Automação)

```bash
ollama pull qwen2.5-coder:14b
```

Especializado em código. Ideal para gerar scripts, analisar configurações, sugerir correções.

### Cenário 4: Máxima Qualidade

```bash
ollama pull qwen3:30b-a3b
```

MoE com qualidade de modelo 30B mas velocidade aceitável (apenas 3B de parâmetros ativos por token). Usa ~19 GB de VRAM.

---

## Qwen 3: Modo Think/No-Think

Os modelos Qwen 3 introduzem um modo híbrido de raciocínio:

| Modo | Comportamento | Quando usar |
|------|--------------|-------------|
| **Think** | Modelo "pensa" internamente antes de responder (chain-of-thought) | Problemas complexos, matemática, lógica |
| **No-Think** | Resposta direta sem raciocínio explícito | Chat rápido, perguntas simples |

Para controlar o modo via API:

```bash
# Forçar modo think (raciocínio explícito)
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3:14b",
  "messages": [{"role": "user", "content": "/think Analise este log de erro..."}],
  "stream": false
}'

# Forçar modo no-think (resposta direta)
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3:14b",
  "messages": [{"role": "user", "content": "/no_think O que é DNS?"}],
  "stream": false
}'
```

---

## Múltiplos Modelos na Mesma GPU

O Ollama carrega um modelo por vez na VRAM por padrão. Para trocar:

```bash
# Modelo atual carregado
ollama ps

# Ao chamar outro modelo, o anterior é descarregado automaticamente
curl http://localhost:11434/api/generate -d '{"model": "qwen2.5-coder:7b", "prompt": "..."}'
```

Para manter dois modelos simultaneamente (se houver VRAM suficiente):

```bash
# Definir variável de ambiente antes de iniciar Ollama
OLLAMA_MAX_LOADED_MODELS=2
```

Exemplo: `qwen2.5:7b-instruct` (5 GB) + `qwen2.5-coder:7b` (5 GB) = 10 GB. Cabe na 3090 com folga.

---

## Próximo Passo

Agora que você conhece os modelos, aprenda a usar a API do Ollama. Veja [05-OLLAMA-API.md](05-OLLAMA-API.md).
