# Integração com um ambiente de teste

> O nome do arquivo é mantido por compatibilidade de links. O conteúdo é genérico e não
> descreve a topologia interna do debuga.ai.

## Objetivo

Conectar uma aplicação de teste a um endpoint Ollama ou OpenAI-compatible sem expor a API
à internet e sem usar dados reais.

## Opção A — mesma rede Docker

```yaml
services:
  app:
    environment:
      LLM_BASE_URL: http://ollama:11434
  ollama:
    image: ollama/ollama:latest
    expose:
      - "11434"
```

A porta não precisa ser publicada no host quando apenas a aplicação a consome.

## Opção B — host separado

Use uma rede privada ou VPN, firewall por origem e proxy com autenticação/TLS. Exemplo com
endereço reservado para documentação:

```dotenv
LLM_BASE_URL=http://192.0.2.20:11434
```

Não exponha `11434` diretamente à internet.

## Validação

```bash
curl -fsS "$LLM_BASE_URL/api/tags"
```

Para endpoints OpenAI-compatible, valide `/v1/models` e uma resposta curta.

## Checklist

```text
[ ] dados sintéticos
[ ] endpoint restrito por rede
[ ] autenticação quando disponível
[ ] timeout configurado
[ ] logs sem segredos
[ ] fallback desabilitado ou explicitamente autorizado
[ ] rollback documentado
```
