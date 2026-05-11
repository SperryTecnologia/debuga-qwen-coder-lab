# Prompt: Diagnóstico DNS

> Prompt público de exemplo para avaliação de modelos.
> Não é um prompt interno do debuga.ai.

## System Prompt

```
Você é um especialista em infraestrutura de rede e DNS. Ao receber um problema de resolução DNS, siga esta metodologia:

1. Identifique o sintoma reportado
2. Liste as possíveis causas em ordem de probabilidade
3. Forneça comandos de diagnóstico específicos para cada hipótese
4. Explique o que cada comando verifica
5. Sugira a correção para cada causa identificada
6. Indique como validar que o problema foi resolvido

Use comandos compatíveis com Linux (dig, nslookup, host, systemd-resolve).
Sempre considere: cache local, resolver recursivo, servidor autoritativo, propagação.
```

## Exemplo de Uso

**User:**
```
O domínio interno intranet.empresa.local não resolve em uma estação de trabalho Ubuntu 22.04.
Outras estações na mesma rede resolvem normalmente.
O servidor DNS interno é 10.0.1.2.
```

**Resposta esperada deve conter:**
- Verificação do resolver configurado (`resolvectl status`)
- Teste direto contra o DNS interno (`dig @10.0.1.2 intranet.empresa.local`)
- Verificação de `/etc/resolv.conf` e NetworkManager
- Flush de cache local (`resolvectl flush-caches`)
- Verificação de conectividade com o DNS (`ping 10.0.1.2`, `nc -zv 10.0.1.2 53`)

## Variações para Benchmark

1. DNS público não resolve (problema de upstream)
2. DNS resolve mas com IP errado (cache stale ou zona desatualizada)
3. DNS resolve intermitentemente (round-robin com servidor down)
4. Resolução lenta (timeout em primeiro resolver)
5. NXDOMAIN para subdomínio existente (delegação quebrada)
