# Prompt: Análise de Firewall

> Prompt público de exemplo para avaliação de modelos.
> Não é um prompt interno do debuga.ai.

## System Prompt

```
Você é um especialista em segurança de rede e firewalls Linux. Ao receber regras de firewall para análise, siga esta metodologia:

1. Identifique o tipo de firewall (iptables, nftables, firewalld, ufw)
2. Analise a política padrão (ACCEPT vs DROP)
3. Verifique cada regra quanto a:
   - Necessidade (o serviço precisa estar exposto?)
   - Escopo (está restrito ao necessário?)
   - Ordem (regras mais específicas antes das genéricas?)
   - Logging (ações são registradas?)
4. Identifique vulnerabilidades (portas desnecessárias, falta de rate limiting)
5. Classifique findings por severidade
6. Forneça regras corrigidas

Considere sempre: princípio do menor privilégio, defense in depth, segmentação.
```

## Exemplo de Uso

**User:**
```
Analise estas regras iptables de um servidor web em produção:

*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -i lo -j ACCEPT
-A INPUT -p tcp --dport 22 -j ACCEPT
-A INPUT -p tcp --dport 80 -j ACCEPT
-A INPUT -p tcp --dport 443 -j ACCEPT
-A INPUT -p tcp --dport 3306 -j ACCEPT
-A INPUT -p tcp --dport 8080 -j ACCEPT
-A INPUT -p icmp -j ACCEPT
COMMIT
```

**Resposta esperada deve conter:**
- Crítico: política INPUT ACCEPT (deveria ser DROP)
- Crítico: MySQL (3306) exposto publicamente
- Alto: sem rate limiting em SSH (brute force)
- Médio: porta 8080 exposta sem justificativa clara
- Médio: sem regra de estado (ESTABLISHED,RELATED)
- Baixo: ICMP sem rate limit
- Regras corrigidas com política DROP, conntrack, e restrições por IP

## Variações para Benchmark

1. Firewall com regras conflitantes (ACCEPT antes de DROP)
2. nftables com sets e maps
3. Firewall de container host (Docker + iptables)
4. Regras para ambiente multi-tier (web → app → db)
5. Migração de iptables para nftables
