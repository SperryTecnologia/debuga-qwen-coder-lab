# Metodologia de benchmark

## Dois níveis diferentes

### 1. Transporte

Mede se o endpoint respondeu, latência, tokens e tamanho. O runner público cobre este nível.

### 2. Qualidade

Avalia correção, segurança, completude e aderência ao esperado. Requer revisão humana,
testes determinísticos ou um validador documentado. Não pode ser inferida apenas por HTTP 200.

## Artefatos obrigatórios

Cada execução deve conter:

- `manifest.json`;
- `responses.jsonl`;
- `metrics.csv`;
- hash do dataset;
- comando executado;
- observações da avaliação.

## Repetição

- faça warm-up;
- execute múltiplas repetições;
- mantenha parâmetros constantes;
- reporte falhas e timeouts;
- não selecione apenas as melhores execuções.

## Segurança

Não execute código gerado diretamente no host. Use sandbox descartável, sem credenciais,
sem acesso à rede interna e com limites de CPU, memória, tempo e filesystem.
