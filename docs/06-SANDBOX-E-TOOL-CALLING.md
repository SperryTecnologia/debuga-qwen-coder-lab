# 06 — Sandbox, Segurança e Tool Calling

## O que Ollama NÃO faz

Este é um dos pontos mais importantes para entender antes de integrar o Ollama com qualquer aplicação:

| O que o Ollama faz | O que o Ollama NÃO faz |
|-------------------|------------------------|
| Recebe texto, gera texto | Executar código |
| Carrega modelos na GPU | Acessar a rede/internet |
| Expõe API HTTP | Ler/escrever arquivos do sistema |
| Gerencia VRAM | Interagir com bancos de dados |
| Streaming de tokens | Enviar emails ou notificações |

> O Ollama é um **gerador de texto**. Ele não tem braços, não tem olhos, não tem acesso a nada além da sua própria memória de pesos e do contexto que você envia na requisição.

---

## Arquitetura de Segurança

A segurança em sistemas com LLM local segue o princípio de **separação de responsabilidades**:

```
┌─────────────────────────────────────────────────────────────┐
│  Usuário (Browser)                                          │
│  ↓ HTTPS                                                    │
├─────────────────────────────────────────────────────────────┤
│  Nginx (TLS termination, rate limiting)                     │
│  ↓                                                          │
├─────────────────────────────────────────────────────────────┤
│  Backend debuga.ai (Node.js)                                │
│  - Autenticação (Google OAuth)                              │
│  - Autorização (planos, limites)                            │
│  - Validação de input                                       │
│  - Sanitização de output                                    │
│  - Orquestração de tool calling                             │
│  - Logging e auditoria                                      │
│  ↓ HTTP interno (rede Docker)                               │
├─────────────────────────────────────────────────────────────┤
│  Ollama (API :11434)                                        │
│  - Apenas gera texto                                        │
│  - Sem acesso à rede externa                                │
│  - Sem acesso ao filesystem do host                         │
│  - Sem autenticação própria                                 │
└─────────────────────────────────────────────────────────────┘
```

### Princípios

1. **O Ollama nunca é exposto diretamente ao usuário** — sempre atrás do backend.
2. **O backend valida tudo** — input do usuário, output do modelo, permissões.
3. **O Ollama roda em rede interna Docker** — não acessível de fora do host.
4. **Tool calling é executado pelo backend** — o modelo apenas sugere qual ferramenta usar.

---

## O que é Tool Calling

Tool calling (ou function calling) é um padrão onde o modelo LLM pode **sugerir** a execução de uma função/ferramenta, mas **não executa** diretamente.

### Fluxo de Tool Calling

```
1. Usuário pergunta: "Qual o status do servidor web?"
2. Backend envia ao Ollama com lista de tools disponíveis
3. Ollama responde: "Quero chamar a tool 'check_service' com args: {service: 'nginx'}"
4. Backend VALIDA a chamada (permissões, rate limit, sanitização)
5. Backend EXECUTA a tool (ex: systemctl status nginx)
6. Backend envia o resultado de volta ao Ollama
7. Ollama gera resposta final: "O Nginx está rodando normalmente..."
8. Backend envia ao usuário
```

### Exemplo de Tool Calling com Ollama

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:7b-instruct",
  "messages": [
    {"role": "system", "content": "Você é um assistente de infraestrutura."},
    {"role": "user", "content": "Verifique se o DNS está respondendo para google.com"}
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "dns_lookup",
        "description": "Resolve um domínio DNS e retorna os IPs",
        "parameters": {
          "type": "object",
          "properties": {
            "domain": {"type": "string", "description": "Domínio a resolver"},
            "record_type": {"type": "string", "enum": ["A", "AAAA", "MX", "CNAME"]}
          },
          "required": ["domain"]
        }
      }
    }
  ],
  "stream": false
}'
```

### Resposta do Ollama (tool call)

```json
{
  "message": {
    "role": "assistant",
    "content": "",
    "tool_calls": [
      {
        "function": {
          "name": "dns_lookup",
          "arguments": {"domain": "google.com", "record_type": "A"}
        }
      }
    ]
  }
}
```

O modelo **não executou** o DNS lookup. Ele apenas **sugeriu** que a ferramenta `dns_lookup` seja chamada com esses argumentos. Cabe ao backend decidir se executa ou não.

---

## Por que o Backend é o Guardião

O backend do debuga.ai é responsável por:

### 1. Validação de Input

Antes de enviar ao Ollama, o backend deve:
- Limitar tamanho do prompt (evitar abuse de contexto)
- Sanitizar caracteres especiais (evitar injection)
- Verificar se o usuário tem permissão (plano ativo)
- Rate limiting (evitar DDoS no Ollama)

### 2. Validação de Tool Calls

Quando o Ollama sugere uma tool call, o backend deve:
- Verificar se a tool existe na whitelist
- Verificar se os argumentos são válidos
- Verificar se o usuário tem permissão para aquela tool
- Aplicar timeout na execução
- Sanitizar o resultado antes de devolver ao modelo

### 3. Sanitização de Output

Antes de enviar a resposta ao usuário, o backend deve:
- Filtrar conteúdo inadequado (se aplicável)
- Remover informações internas (IPs, paths, secrets)
- Formatar para exibição (Markdown, etc.)

---

## Isolamento de Rede

No docker-compose do ambiente de teste, o Ollama roda em rede interna:

```yaml
services:
  app:
    networks:
      - internal
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434

  ollama:
    image: ollama/ollama
    networks:
      - internal  # Apenas rede interna, sem porta exposta ao host
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

networks:
  internal:
    driver: bridge
```

**O Ollama não tem porta exposta ao host** (sem `ports: - "11434:11434"`). Apenas o container `app` pode acessá-lo via rede Docker interna.

---

## Riscos e Mitigações

| Risco | Descrição | Mitigação |
|-------|-----------|-----------|
| Prompt injection | Usuário tenta fazer o modelo executar comandos | Backend valida e sanitiza input |
| Data exfiltration | Modelo tenta vazar dados via tool calling | Whitelist de tools, validação de args |
| Denial of Service | Muitas requisições simultâneas | Rate limiting no backend e Nginx |
| Context overflow | Prompt muito longo consome toda a VRAM | Limite de tokens no backend |
| Model hallucination | Modelo inventa informações | Disclaimer no frontend, validação de fatos |
| Jailbreak | Usuário tenta bypassar system prompt | System prompt robusto, filtros de output |

---

## Boas Práticas

1. **Nunca exponha a porta 11434 ao público** — use apenas rede Docker interna ou localhost.

2. **Defina uma whitelist de tools** — o modelo só pode sugerir tools que existem na lista aprovada.

3. **Valide argumentos de tool calls** — não confie nos argumentos gerados pelo modelo. Trate como input não confiável.

4. **Aplique timeout em tool calls** — se uma tool demorar mais que X segundos, cancele.

5. **Registre tudo em log** — cada requisição ao Ollama, cada tool call, cada resposta. Auditoria é essencial.

6. **Limite o contexto** — não envie todo o histórico de conversa. Mantenha um window de N mensagens.

7. **Separe modelos por função** — use um modelo para chat geral e outro para code generation. Cada um com system prompt e tools diferentes.

8. **Monitore VRAM** — se a GPU ficar sem memória, o Ollama pode travar. Monitore com `nvidia-smi`.

---

## O que NÃO é Sandbox

Algumas confusões comuns:

| Conceito | É sandbox? | Explicação |
|----------|-----------|------------|
| Container Docker do Ollama | Parcial | Isola filesystem e rede, mas não isola a GPU |
| O modelo LLM em si | Não | Não executa código, mas pode gerar texto malicioso |
| Tool calling | Não | O modelo sugere, mas o backend executa |
| Rede Docker interna | Parcial | Isola do mundo externo, mas containers se comunicam |

Para sandbox real de execução de código (ex: se o modelo gerar um script e você quiser executá-lo), seria necessário:
- Container efêmero com timeout
- Sem acesso à rede
- Sem acesso ao filesystem do host
- Limites de CPU/RAM/tempo
- Descartado após execução

Isso está **fora do escopo** do Ollama e deste laboratório. O debuga.ai não executa código gerado pelo modelo — apenas exibe para o usuário.

---

## Próximo Passo

Agora que você entende a segurança, aprenda a integrar o Ollama com o ambiente de teste. Veja [07-INTEGRACAO-COM-DEBUGA-HOMOLOG.md](07-INTEGRACAO-COM-DEBUGA-HOMOLOG.md).
