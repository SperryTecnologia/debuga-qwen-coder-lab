# Formato de Dataset para Fine-Tuning

## Formato Esperado: ChatML (JSONL)

O Qwen-Coder usa o formato ChatML internamente. Cada linha do arquivo JSONL deve conter uma conversa completa:

```json
{
  "messages": [
    {"role": "system", "content": "Você é um especialista em infraestrutura Linux e segurança."},
    {"role": "user", "content": "O servidor web retorna 502 Bad Gateway intermitentemente. Nginx como reverse proxy, backend em Node.js."},
    {"role": "assistant", "content": "O erro 502 Bad Gateway indica que o Nginx não consegue se comunicar com o backend. Vamos diagnosticar:\n\n1. **Verificar status do backend:**\n```bash\nsystemctl status node-app\nss -tlnp | grep 3000\n```\n\n2. **Verificar logs do Nginx:**\n```bash\ntail -100 /var/log/nginx/error.log | grep 502\n```\n\n3. **Causas comuns:**\n- Backend crashando por falta de memória (verificar `dmesg | grep -i oom`)\n- Timeout do upstream (ajustar `proxy_read_timeout` no Nginx)\n- Socket file com permissões incorretas\n- Backend não escutando no endereço correto (127.0.0.1 vs 0.0.0.0)\n\n4. **Correção mais provável:**\nSe o backend está reiniciando, adicione ao Nginx:\n```nginx\nupstream backend {\n    server 127.0.0.1:3000;\n    keepalive 32;\n}\n\nserver {\n    location / {\n        proxy_pass http://backend;\n        proxy_connect_timeout 5s;\n        proxy_read_timeout 60s;\n        proxy_next_upstream error timeout;\n    }\n}\n```"}
  ]
}
```

## Regras de Qualidade

1. **Respostas completas**: cada resposta do assistant deve ser uma solução completa, não parcial
2. **Comandos reais**: todos os comandos devem ser executáveis em Linux real
3. **Explicações**: não apenas o comando, mas por que ele resolve o problema
4. **Contexto**: o system prompt deve definir o domínio de especialidade
5. **Diversidade**: variar entre diagnóstico, correção, prevenção, automação

## Categorias Recomendadas

| Categoria | Exemplos | Quantidade Sugerida |
|-----------|----------|-------------------|
| Diagnóstico de rede | DNS, firewall, routing, latência | 50-100 |
| Segurança | Hardening, auditoria, CVEs, WAF | 50-100 |
| Containers | Docker, Kubernetes, compose | 30-50 |
| Monitoramento | Logs, métricas, alertas | 30-50 |
| Automação | Bash, Python, Ansible, cron | 30-50 |
| Banco de dados | MySQL, PostgreSQL, backup, tuning | 20-30 |
| Web servers | Nginx, Apache, SSL/TLS | 20-30 |
| Cloud | AWS, GCP, Azure, Terraform | 20-30 |

**Total recomendado**: 250-440 exemplos para uma primeira iteração de fine-tuning.

## Conversão dos Benchmarks

Os arquivos em `benchmarks/*.jsonl` contêm tarefas com `expected_keywords`, mas sem respostas completas. Para usá-los como dataset de treino:

1. Gerar respostas com um modelo forte (ex.: GPT-4, Claude)
2. Validar cada resposta com um especialista humano
3. Converter para o formato ChatML acima

```python
import json

# Exemplo de conversão (requer respostas validadas)
with open("benchmarks/devops-tasks.jsonl") as f:
    for line in f:
        task = json.loads(line)
        training_example = {
            "messages": [
                {"role": "system", "content": task["system_prompt"]},
                {"role": "user", "content": task["user_prompt"]},
                # ADICIONAR: resposta validada por especialista
                # {"role": "assistant", "content": "..."}
            ]
        }
```

## Diretório de Dados

```
fine-tuning/
  data/
    train.jsonl      # Dataset de treino (80%)
    val.jsonl         # Dataset de validação (20%)
    raw/              # Dados brutos antes de processar
```

Os arquivos `train.jsonl` e `val.jsonl` não estão incluídos neste repositório. Devem ser gerados seguindo as instruções acima.
