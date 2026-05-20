# debuga-qwen-coder-lab

**Laboratório de avaliação de modelos Qwen-Coder para automação técnica, DevOps, infraestrutura e segurança.**

Desenvolvida por [Sperry Tecnologia](https://www.sperrytecnologia.com.br).

---

## O que é

Este repositório é um laboratório de **pesquisa aplicada** dedicado à avaliação da família de modelos Qwen-Coder para tarefas de automação técnica. O objetivo é validar a viabilidade de modelos open-source especializados em código para o domínio de infraestrutura de TI, segurança da informação e DevOps.

Este é um repositório de **pesquisa e experimentação**, não contém código de produção.

---

## Status

| Aspecto | Classificação |
|---------|--------------|
| Tipo | Pesquisa aplicada |
| Código de produção | Não incluso |
| Uso | Avaliação de modelos e benchmarks |
| Hardware de referência | NVIDIA RTX 3090 (24 GB VRAM) |

---

## Como se conecta à debuga.ai

A [debuga.ai](https://github.com/SperryTecnologia/debuga-ai) utiliza inferência local via GPU como camada primária de IA. Este laboratório avalia quais modelos são mais adequados para as tarefas técnicas da plataforma, informando decisões de:

- Qual modelo servir via Ollama em produção
- Quais tarefas podem ser resolvidas localmente vs. cloud
- Qual o trade-off entre tamanho do modelo e qualidade para cada caso de uso
- Configurações de quantização ideais para o hardware disponível

---

## Cenários de Teste

| Cenário | Descrição | Complexidade |
|---------|-----------|-------------|
| Geração de scripts Bash | Automação de tarefas de infraestrutura | Média |
| Análise de logs | Identificação de padrões e anomalias | Alta |
| Configuração de rede | Geração de configs para roteadores/switches | Média |
| Troubleshooting | Diagnóstico de falhas a partir de sintomas | Alta |
| Segurança | Análise de vulnerabilidades e hardening | Alta |
| Docker/Compose | Geração e revisão de Dockerfiles | Média |
| Terraform/Ansible | IaC para provisionamento | Alta |
| SQL/Database | Queries de diagnóstico e otimização | Média |

---

## Prompts Técnicos

O laboratório utiliza prompts especializados para o domínio técnico:

- **System prompts** otimizados para contexto de infraestrutura
- **Few-shot examples** com saídas esperadas para cada cenário
- **Avaliação de tool calling** — capacidade do modelo de invocar ferramentas
- **Raciocínio em cadeia** — decomposição de problemas complexos
- **Geração estruturada** — JSON, YAML, scripts com formato específico

---

## Avaliação de Qualidade

Critérios de avaliação para cada modelo:

| Critério | Peso | Descrição |
|----------|------|-----------|
| Correção | Alto | O código/resposta está correto? |
| Completude | Alto | Cobre todos os aspectos do problema? |
| Segurança | Alto | Não introduz vulnerabilidades? |
| Eficiência | Médio | Solução é performática? |
| Clareza | Médio | Código é legível e bem documentado? |
| Latência | Médio | Tempo de resposta aceitável? |
| Consistência | Baixo | Respostas similares para prompts similares? |

---

## Benchmarks Práticos

Resultados de referência com NVIDIA RTX 3090:

| Modelo | Tokens/s | Latência (first token) | Qualidade (0-10) |
|--------|---------|----------------------|-----------------|
| Qwen 2.5 Coder 7B (Q4) | ~45 t/s | ~800ms | 7.2 |
| Qwen 2.5 Coder 7B (Q8) | ~35 t/s | ~1.1s | 7.8 |
| Qwen 2.5 14B Instruct (Q4) | ~25 t/s | ~1.5s | 8.1 |
| Qwen 2.5 Coder 32B (Q4) | ~12 t/s | ~3.0s | 8.7 |

> Benchmarks são indicativos. Resultados variam conforme hardware, quantização, contexto e tipo de tarefa.

---

## Infraestrutura de Referência

| Componente | Especificação |
|-----------|--------------|
| GPU | NVIDIA RTX 3090 (24 GB VRAM) |
| Host | Hyper-V com DDA (Direct Device Assignment) |
| OS | Ubuntu 22.04 / 24.04 |
| Runtime | Ollama + nvidia-container-toolkit |
| Quantização | GGUF (Q4_K_M, Q8_0) |

---

## Arquitetura do Laboratório

```
┌─────────────────────────────────────────┐
│           Host (Windows + Hyper-V)      │
├─────────────────────────────────────────┤
│  VM Ubuntu (DDA GPU passthrough)        │
│  ├── Ollama (serving de modelos)        │
│  ├── Scripts de benchmark               │
│  ├── Prompts de avaliação               │
│  └── Coleta de métricas                 │
└─────────────────────────────────────────┘
```

---

## Uso Previsto

- Avaliar novos modelos antes de adotá-los na plataforma
- Comparar quantizações para o hardware disponível
- Validar capacidade de tool calling
- Documentar trade-offs entre velocidade e qualidade
- Informar decisões de infraestrutura GPU

---

## Limitações

- Resultados são específicos para o hardware de referência
- Modelos evoluem rapidamente; benchmarks podem ficar desatualizados
- Avaliação de qualidade tem componente subjetivo
- Este repositório não contém código de produção da plataforma

---

## Roadmap

| Item | Status |
|------|--------|
| Avaliação Qwen 2.5 Coder 7B | Concluído |
| Avaliação Qwen 2.5 14B | Concluído |
| Benchmarks com RTX 3090 | Concluído |
| Avaliação de tool calling | Em andamento |
| Fine-tuning para domínio técnico | Planejado |
| Comparação com DeepSeek Coder | Planejado |
| Testes com múltiplas GPUs | Planejado |

---

## Licença

Documentação e scripts de benchmark sob licença MIT. O código de produção da plataforma é privado.

---

## Sperry Tecnologia

Desenvolvido por [Sperry Tecnologia](https://www.sperrytecnologia.com.br) — infraestrutura, segurança, DevOps e automação com IA.
