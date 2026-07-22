# Qwen2.5-Coder-14B-Instruct — Resultados de Avaliação

> [!WARNING]
> **ARQUIVO HISTÓRICO NÃO HOMOLOGADO.** Este snapshot não inclui respostas brutas,
> manifesto completo e método de scoring suficientes para reprodução independente.
> Os números abaixo são mantidos como material ilustrativo e não devem orientar produção.

> Avaliação realizada com dados sintéticos em ambiente de laboratório.
> Não representa performance em produção.

## Configuração

| Parâmetro | Valor |
|---|---|
| Modelo | Qwen2.5-Coder-14B-Instruct |
| Quantização | FP16 |
| Motor | vLLM 0.4.x |
| GPU | 1x NVIDIA A100 40GB |
| Max tokens | 2048 |
| Temperature | 0.1 |

## Resultados por Categoria

| Categoria | Tarefas | Sucesso | Latência Média | Tokens Médios |
|---|---|---|---|---|
| DNS | 3 | 3/3 | 3.2s | 1050 |
| Docker | 2 | 2/2 | 4.8s | 1500 |
| Automação | 3 | 3/3 | 5.6s | 1800 |
| Segurança | 4 | 4/4 | 5.1s | 1400 |
| Rede | 3 | 3/3 | 4.1s | 1200 |
| Kubernetes | 2 | 2/2 | 6.2s | 1650 |

## Observações

O modelo 14B resolve todas as tarefas do benchmark com sucesso, incluindo as que falharam no 7B (Kubernetes scheduling, incident response complexo). A latência é ~50% maior que o 7B, mas a qualidade das respostas justifica o trade-off para tarefas críticas.

## Pontos Fortes

- Raciocínio multi-step consistente
- Cálculos de recursos corretos (memory, CPU scheduling)
- Respostas de compliance mais detalhadas e com referências a normas
- Melhor estruturação de runbooks complexos

## Pontos Fracos

- Latência maior pode impactar UX em chat interativo
- Custo de GPU significativamente maior (A100 vs RTX 4090)
- Respostas mais longas nem sempre são mais úteis para operadores experientes

## Comparação com 7B

| Métrica | 7B | 14B | Delta |
|---|---|---|---|
| Taxa de sucesso | 82% | 100% | +18% |
| Latência média | 3.1s | 4.8s | +55% |
| Tokens médios | 1100 | 1430 | +30% |
| Custo GPU/hora | ~$1.50 | ~$4.00 | +167% |

## Recomendação

Para o debuga.ai, a estratégia recomendada é roteamento por complexidade: tarefas simples (DNS, comandos diretos) vão para o 7B (mais rápido e barato), enquanto tarefas complexas (incident response, compliance, multi-step) vão para o 14B.
