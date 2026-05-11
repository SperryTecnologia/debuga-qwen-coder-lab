# Qwen2.5-Coder-7B-Instruct — Resultados de Avaliação

> Avaliação realizada com dados sintéticos em ambiente de laboratório.
> Não representa performance em produção.

## Configuração

| Parâmetro | Valor |
|---|---|
| Modelo | Qwen2.5-Coder-7B-Instruct |
| Quantização | FP16 |
| Motor | vLLM 0.4.x |
| GPU | 1x NVIDIA RTX 4090 (24GB) |
| Max tokens | 2048 |
| Temperature | 0.1 |

## Resultados por Categoria

| Categoria | Tarefas | Sucesso | Latência Média | Tokens Médios |
|---|---|---|---|---|
| DNS | 3 | 3/3 | 2.1s | 850 |
| Docker | 2 | 2/2 | 3.4s | 1200 |
| Automação | 3 | 3/3 | 4.2s | 1450 |
| Segurança | 4 | 3/4 | 3.8s | 1100 |
| Rede | 3 | 2/3 | 2.9s | 950 |
| Kubernetes | 2 | 1/2 | 4.5s | 1350 |

## Observações

O modelo 7B apresenta bom desempenho em tarefas de diagnóstico direto (DNS, Docker, automação simples). Em tarefas complexas que exigem raciocínio multi-step (Kubernetes scheduling, incident response com múltiplas variáveis), o modelo tende a omitir passos intermediários.

## Pontos Fortes

- Geração de comandos Linux/Bash precisa
- Boa estruturação de respostas em formato de runbook
- Diagnóstico de problemas de rede com comandos corretos

## Pontos Fracos

- Dificuldade com cálculos de recursos (memory requests vs capacity)
- Respostas de compliance tendem a ser genéricas
- Pode sugerir ferramentas que não existem em distribuições padrão

## Próximos Passos

- Avaliar impacto de quantização AWQ na qualidade
- Comparar com modelo 14B nas tarefas que falharam
- Testar com prompts mais estruturados (chain-of-thought)
