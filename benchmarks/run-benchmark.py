#!/usr/bin/env python3
"""
debuga-qwen-coder-lab - Benchmark Runner

Executa tarefas de avaliação contra um modelo via API OpenAI-compatible
(vLLM, Ollama, ou qualquer endpoint compatível).

Uso:
    python run-benchmark.py \
        --model Qwen/Qwen2.5-Coder-7B-Instruct \
        --dataset benchmarks/devops-tasks.jsonl \
        --output benchmarks/results/ \
        --api-url http://localhost:8000/v1

Requisitos:
    pip install requests pandas tqdm pydantic
"""

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm


def load_dataset(path: str) -> list[dict]:
    """Carrega dataset JSONL."""
    tasks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks


def query_model(
    api_url: str,
    model: str,
    task: str,
    system_prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 2048,
) -> dict:
    """Envia tarefa para o modelo e retorna resposta."""
    headers = {"Content-Type": "application/json"}

    # Adicionar API key se configurada
    api_key = os.environ.get("LLM_API_KEY", "")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    start_time = time.time()
    try:
        response = requests.post(
            f"{api_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()
        elapsed = time.time() - start_time

        return {
            "success": True,
            "content": result["choices"][0]["message"]["content"],
            "tokens_used": result.get("usage", {}).get("total_tokens", 0),
            "latency_seconds": round(elapsed, 2),
        }
    except Exception as e:
        return {
            "success": False,
            "content": "",
            "error": str(e),
            "latency_seconds": round(time.time() - start_time, 2),
        }


def run_benchmark(
    dataset_path: str,
    model: str,
    api_url: str,
    output_dir: str,
) -> pd.DataFrame:
    """Executa benchmark completo e salva resultados."""
    tasks = load_dataset(dataset_path)
    dataset_name = Path(dataset_path).stem

    system_prompt = (
        "Você é um especialista em infraestrutura de TI, DevOps e segurança da informação. "
        "Responda de forma técnica, objetiva e completa. "
        "Inclua comandos específicos quando aplicável. "
        "Estruture sua resposta com diagnóstico, causa raiz e solução."
    )

    results = []
    print(f"\n{'='*60}")
    print(f"  debuga-qwen-coder-lab - Benchmark Runner")
    print(f"  Model: {model}")
    print(f"  Dataset: {dataset_name} ({len(tasks)} tasks)")
    print(f"  API: {api_url}")
    print(f"{'='*60}\n")

    for task in tqdm(tasks, desc="Evaluating"):
        response = query_model(
            api_url=api_url,
            model=model,
            task=task["task"],
            system_prompt=system_prompt,
        )

        results.append({
            "id": task["id"],
            "category": task["category"],
            "difficulty": task["difficulty"],
            "task_preview": task["task"][:100] + "...",
            "success": response["success"],
            "response_length": len(response["content"]),
            "tokens_used": response.get("tokens_used", 0),
            "latency_seconds": response["latency_seconds"],
            "error": response.get("error", ""),
        })

    # Criar DataFrame
    df = pd.DataFrame(results)

    # Salvar resultados
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_short = model.split("/")[-1].lower().replace("-", "_")

    csv_path = os.path.join(output_dir, f"{dataset_name}_{model_short}_{timestamp}.csv")
    df.to_csv(csv_path, index=False)

    # Gerar resumo
    print(f"\n{'='*60}")
    print(f"  RESULTADOS")
    print(f"{'='*60}")
    print(f"  Total de tarefas: {len(df)}")
    print(f"  Sucesso: {df['success'].sum()}/{len(df)}")
    print(f"  Latência média: {df['latency_seconds'].mean():.2f}s")
    print(f"  Tokens médios: {df['tokens_used'].mean():.0f}")
    print(f"\n  Por categoria:")
    for cat, group in df.groupby("category"):
        print(f"    {cat}: {group['success'].sum()}/{len(group)} OK, "
              f"avg {group['latency_seconds'].mean():.2f}s")
    print(f"\n  Resultados salvos em: {csv_path}")
    print(f"{'='*60}\n")

    return df


def main():
    parser = argparse.ArgumentParser(
        description="debuga-qwen-coder-lab Benchmark Runner"
    )
    parser.add_argument(
        "--model",
        default="Qwen/Qwen2.5-Coder-7B-Instruct",
        help="Model ID (default: Qwen/Qwen2.5-Coder-7B-Instruct)",
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Path to JSONL dataset file",
    )
    parser.add_argument(
        "--output",
        default="benchmarks/results/",
        help="Output directory for results (default: benchmarks/results/)",
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000/v1",
        help="OpenAI-compatible API URL (default: http://localhost:8000/v1)",
    )

    args = parser.parse_args()
    run_benchmark(args.dataset, args.model, args.api_url, args.output)


if __name__ == "__main__":
    main()
