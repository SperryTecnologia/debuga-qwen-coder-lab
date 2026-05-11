#!/usr/bin/env bash
# ============================================================
# download-model.sh — Baixar modelos Qwen-Coder do Hugging Face
# ============================================================
# Uso:
#   ./scripts/download-model.sh 7b          # Qwen2.5-Coder-7B-Instruct
#   ./scripts/download-model.sh 7b-awq      # Qwen2.5-Coder-7B-Instruct-AWQ
#   ./scripts/download-model.sh 14b         # Qwen2.5-Coder-14B-Instruct
#   ./scripts/download-model.sh 14b-awq     # Qwen2.5-Coder-14B-Instruct-AWQ
#   ./scripts/download-model.sh 32b         # Qwen2.5-Coder-32B-Instruct
# ============================================================

set -euo pipefail

MODEL_SIZE="${1:-}"
CACHE_DIR="${HF_HOME:-$HOME/.cache/huggingface}"

declare -A MODELS=(
    ["1.5b"]="Qwen/Qwen2.5-Coder-1.5B-Instruct"
    ["3b"]="Qwen/Qwen2.5-Coder-3B-Instruct"
    ["7b"]="Qwen/Qwen2.5-Coder-7B-Instruct"
    ["7b-awq"]="Qwen/Qwen2.5-Coder-7B-Instruct-AWQ"
    ["14b"]="Qwen/Qwen2.5-Coder-14B-Instruct"
    ["14b-awq"]="Qwen/Qwen2.5-Coder-14B-Instruct-AWQ"
    ["32b"]="Qwen/Qwen2.5-Coder-32B-Instruct"
    ["32b-awq"]="Qwen/Qwen2.5-Coder-32B-Instruct-AWQ"
)

if [[ -z "$MODEL_SIZE" ]] || [[ -z "${MODELS[$MODEL_SIZE]+x}" ]]; then
    echo "Uso: $0 <modelo>"
    echo ""
    echo "Modelos disponíveis:"
    for key in $(echo "${!MODELS[@]}" | tr ' ' '\n' | sort); do
        echo "  $key  →  ${MODELS[$key]}"
    done
    echo ""
    echo "Exemplos:"
    echo "  $0 7b-awq    # Recomendado para GPUs com 8+ GB VRAM"
    echo "  $0 14b-awq   # Recomendado para GPUs com 16+ GB VRAM"
    exit 1
fi

MODEL_NAME="${MODELS[$MODEL_SIZE]}"

echo "============================================================"
echo "Baixando: $MODEL_NAME"
echo "Cache: $CACHE_DIR"
echo "============================================================"

# Verificar se huggingface-cli está instalado
if ! command -v huggingface-cli &> /dev/null; then
    echo "ERRO: huggingface-cli não encontrado."
    echo "Instale com: pip install huggingface_hub[cli]"
    exit 1
fi

# Verificar espaço em disco (estimativa)
declare -A SIZES=(
    ["1.5b"]="3" ["3b"]="6" ["7b"]="14" ["7b-awq"]="4"
    ["14b"]="28" ["14b-awq"]="8" ["32b"]="64" ["32b-awq"]="18"
)
REQUIRED_GB="${SIZES[$MODEL_SIZE]}"
AVAILABLE_GB=$(df -BG "$CACHE_DIR" 2>/dev/null | tail -1 | awk '{print $4}' | tr -d 'G')

if [[ -n "$AVAILABLE_GB" ]] && (( AVAILABLE_GB < REQUIRED_GB + 5 )); then
    echo "AVISO: Espaço disponível (~${AVAILABLE_GB} GB) pode ser insuficiente."
    echo "       O modelo requer ~${REQUIRED_GB} GB + margem."
    read -p "Continuar? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Download
echo ""
echo "Iniciando download..."
huggingface-cli download "$MODEL_NAME" --cache-dir "$CACHE_DIR"

echo ""
echo "============================================================"
echo "Download concluído: $MODEL_NAME"
echo "============================================================"
echo ""
echo "Para servir com vLLM:"
echo "  python -m vllm.entrypoints.openai.api_server \\"
echo "    --model $MODEL_NAME \\"
if [[ "$MODEL_SIZE" == *"-awq"* ]]; then
    echo "    --quantization awq \\"
fi
echo "    --max-model-len 4096"
