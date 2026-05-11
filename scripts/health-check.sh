#!/usr/bin/env bash
# ============================================================
# health-check.sh — Verificar status do vLLM e modelo
# ============================================================
# Uso:
#   ./scripts/health-check.sh                    # localhost:8000
#   ./scripts/health-check.sh http://gpu:8000    # servidor remoto
# ============================================================

set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
TIMEOUT=5

echo "============================================================"
echo "Health Check: $BASE_URL"
echo "============================================================"
echo ""

# 1. Verificar se o servidor responde
echo "1. Conectividade..."
if curl -sf --max-time "$TIMEOUT" "$BASE_URL/health" > /dev/null 2>&1; then
    echo "   ✓ Servidor respondendo"
else
    echo "   ✗ Servidor não responde em $BASE_URL"
    echo "   Verifique se o vLLM está rodando:"
    echo "     docker ps | grep vllm"
    echo "     curl -v $BASE_URL/health"
    exit 1
fi

# 2. Listar modelos carregados
echo ""
echo "2. Modelos carregados..."
MODELS_RESPONSE=$(curl -sf --max-time "$TIMEOUT" "$BASE_URL/v1/models" 2>/dev/null || echo "")
if [[ -n "$MODELS_RESPONSE" ]]; then
    MODEL_ID=$(echo "$MODELS_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('data', []):
    print(f\"   ✓ {m['id']}\")
" 2>/dev/null || echo "   ✗ Erro ao parsear resposta")
    echo "$MODEL_ID"
else
    echo "   ✗ Não foi possível listar modelos"
fi

# 3. Teste de inferência
echo ""
echo "3. Teste de inferência..."
INFERENCE_START=$(date +%s%N)
INFERENCE_RESPONSE=$(curl -sf --max-time 30 "$BASE_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{
        "model": "'"$(echo "$MODELS_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['id'])" 2>/dev/null || echo "default")"'",
        "messages": [{"role": "user", "content": "Responda apenas: OK"}],
        "max_tokens": 10,
        "temperature": 0
    }' 2>/dev/null || echo "")
INFERENCE_END=$(date +%s%N)

if [[ -n "$INFERENCE_RESPONSE" ]]; then
    LATENCY_MS=$(( (INFERENCE_END - INFERENCE_START) / 1000000 ))
    CONTENT=$(echo "$INFERENCE_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
c = data['choices'][0]['message']['content']
u = data.get('usage', {})
print(f'   ✓ Resposta: {c[:50]}')
print(f'   ✓ Tokens: {u.get(\"total_tokens\", \"?\")} (prompt: {u.get(\"prompt_tokens\", \"?\")}, completion: {u.get(\"completion_tokens\", \"?\")})')
" 2>/dev/null || echo "   ✗ Erro ao parsear resposta de inferência")
    echo "$CONTENT"
    echo "   ✓ Latência: ${LATENCY_MS}ms"
else
    echo "   ✗ Inferência falhou"
fi

# 4. Métricas (se disponíveis)
echo ""
echo "4. Métricas..."
METRICS=$(curl -sf --max-time "$TIMEOUT" "$BASE_URL/metrics" 2>/dev/null || echo "")
if [[ -n "$METRICS" ]]; then
    GPU_CACHE=$(echo "$METRICS" | grep "vllm:gpu_cache_usage_perc" | tail -1 | awk '{printf "%.1f%%", $2*100}' 2>/dev/null || echo "N/A")
    RUNNING=$(echo "$METRICS" | grep "vllm:num_requests_running" | tail -1 | awk '{print $2}' 2>/dev/null || echo "N/A")
    WAITING=$(echo "$METRICS" | grep "vllm:num_requests_waiting" | tail -1 | awk '{print $2}' 2>/dev/null || echo "N/A")
    echo "   GPU KV-Cache: $GPU_CACHE"
    echo "   Requests running: $RUNNING"
    echo "   Requests waiting: $WAITING"
else
    echo "   ⚠ Métricas não disponíveis (endpoint /metrics)"
fi

echo ""
echo "============================================================"
echo "Health check concluído"
echo "============================================================"
