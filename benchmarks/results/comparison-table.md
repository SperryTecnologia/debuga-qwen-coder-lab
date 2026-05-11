# Tabela Comparativa — Modelos Qwen-Coder

> Resultados de laboratório com dados sintéticos. Não representa performance em produção.

## Resumo Geral

| Modelo | Parâmetros | Quant. | GPU | Sucesso | Latência | Tokens | Custo/h |
|---|---|---|---|---|---|---|---|
| Qwen2.5-Coder-7B | 7B | FP16 | RTX 4090 | 82% | 3.1s | 1100 | ~$1.50 |
| Qwen2.5-Coder-7B | 7B | AWQ | RTX 4090 | 78% | 2.4s | 1050 | ~$1.50 |
| Qwen2.5-Coder-14B | 14B | FP16 | A100 40GB | 100% | 4.8s | 1430 | ~$4.00 |
| Qwen2.5-Coder-14B | 14B | AWQ | RTX 4090 | 96% | 3.5s | 1380 | ~$1.50 |
| Qwen2.5-Coder-32B | 32B | AWQ | 2x A100 | Planejado | — | — | ~$8.00 |

## Por Categoria de Tarefa

| Categoria | 7B FP16 | 7B AWQ | 14B FP16 | 14B AWQ |
|---|---|---|---|---|
| DNS/Rede simples | 100% | 100% | 100% | 100% |
| Docker/Containers | 100% | 100% | 100% | 100% |
| Automação Bash/Python | 100% | 100% | 100% | 100% |
| Segurança/Hardening | 75% | 75% | 100% | 100% |
| Kubernetes complexo | 50% | 50% | 100% | 100% |
| Incident Response | 67% | 50% | 100% | 83% |
| Compliance/Normas | 50% | 50% | 100% | 100% |

## Impacto da Quantização AWQ

| Modelo | FP16 → AWQ | Perda de Qualidade | Ganho de Velocidade | Redução de VRAM |
|---|---|---|---|---|
| 7B | FP16 → AWQ | -4% sucesso | +23% mais rápido | 14GB → 8GB |
| 14B | FP16 → AWQ | -4% sucesso | +27% mais rápido | 28GB → 16GB |

## Recomendação por Cenário

| Cenário | Modelo Recomendado | Justificativa |
|---|---|---|
| Chat interativo (baixa latência) | 7B AWQ | Resposta rápida, suficiente para diagnósticos simples |
| Tarefas críticas (segurança, compliance) | 14B FP16 | Máxima qualidade, raciocínio multi-step |
| Melhor custo-benefício | 14B AWQ | 96% sucesso com custo de GPU do 7B |
| Produção com roteamento | 7B AWQ + 14B FP16 | Simples → 7B, Complexo → 14B |

## Notas

- Resultados baseados em datasets sintéticos (25 tarefas DevOps + 8 segurança + 7 rede)
- Avaliação binária (sucesso/falha) — não mede qualidade parcial
- Latência medida end-to-end (inclui network overhead local)
- Custos estimados com base em preços de cloud GPU (RunPod/Lambda)
