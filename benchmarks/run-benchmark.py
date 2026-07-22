#!/usr/bin/env python3
"""Runner de transporte para endpoints OpenAI-compatible.

Coleta respostas brutas e métricas. Não atribui nota de correção semântica.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from tqdm import tqdm


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_dataset(path: Path) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    with path.open('r', encoding='utf-8') as fh:
        for line_number, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            for field in ('id', 'category', 'difficulty', 'task'):
                if field not in item:
                    raise ValueError(f'{path}:{line_number}: campo ausente: {field}')
            tasks.append(item)
    if not tasks:
        raise ValueError(f'dataset vazio: {path}')
    return tasks


def query_model(api_url: str, model: str, task: str, system_prompt: str,
                temperature: float, max_tokens: int, timeout: int) -> dict[str, Any]:
    headers = {'Content-Type': 'application/json'}
    api_key = os.environ.get('LLM_API_KEY', '')
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': task},
        ],
        'temperature': temperature,
        'max_tokens': max_tokens,
    }
    start = time.perf_counter()
    try:
        response = requests.post(
            f"{api_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout,
        )
        elapsed = time.perf_counter() - start
        response.raise_for_status()
        body = response.json()
        content = body['choices'][0]['message'].get('content', '')
        usage = body.get('usage', {})
        return {
            'request_success': True,
            'http_status': response.status_code,
            'latency_seconds': round(elapsed, 4),
            'content': content,
            'usage': usage,
            'error': None,
        }
    except Exception as exc:  # noqa: BLE001 - registrado no artefato
        return {
            'request_success': False,
            'http_status': getattr(getattr(exc, 'response', None), 'status_code', None),
            'latency_seconds': round(time.perf_counter() - start, 4),
            'content': '',
            'usage': {},
            'error': str(exc),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description='debuga Qwen Coder Lab transport runner')
    parser.add_argument('--model', default='Qwen/Qwen2.5-Coder-7B-Instruct')
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--output', default='benchmarks/results/runs')
    parser.add_argument('--api-url', default='http://localhost:8000/v1')
    parser.add_argument('--temperature', type=float, default=0.1)
    parser.add_argument('--max-tokens', type=int, default=2048)
    parser.add_argument('--timeout', type=int, default=120)
    args = parser.parse_args()

    dataset = Path(args.dataset).resolve()
    output_root = Path(args.output).resolve()
    tasks = load_dataset(dataset)
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run_dir = output_root / f'{dataset.stem}-{timestamp}'
    run_dir.mkdir(parents=True, exist_ok=False)

    system_prompt = (
        'Você é um especialista em infraestrutura, DevOps e segurança defensiva. '
        'Responda de forma técnica, objetiva e indique incertezas. '
        'Não presuma acesso ao ambiente real.'
    )

    manifest = {
        'schema_version': 1,
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'model': args.model,
        'api_url': args.api_url,
        'dataset': str(dataset),
        'dataset_sha256': sha256_file(dataset),
        'task_count': len(tasks),
        'temperature': args.temperature,
        'max_tokens': args.max_tokens,
        'timeout_seconds': args.timeout,
        'python': sys.version,
        'platform': platform.platform(),
        'semantic_scoring': 'not_performed',
        'note': 'request_success mede transporte HTTP, não correção técnica',
    }
    (run_dir / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )

    rows: list[dict[str, Any]] = []
    responses_path = run_dir / 'responses.jsonl'
    with responses_path.open('w', encoding='utf-8') as raw:
        for task in tqdm(tasks, desc='Consultando endpoint'):
            result = query_model(
                args.api_url, args.model, task['task'], system_prompt,
                args.temperature, args.max_tokens, args.timeout,
            )
            record = {
                'task': task,
                'result': result,
                'evaluation': {'status': 'not_scored'},
            }
            raw.write(json.dumps(record, ensure_ascii=False) + '\n')
            usage = result.get('usage', {})
            rows.append({
                'id': task['id'],
                'category': task['category'],
                'difficulty': task['difficulty'],
                'request_success': result['request_success'],
                'http_status': result['http_status'],
                'latency_seconds': result['latency_seconds'],
                'response_chars': len(result.get('content', '')),
                'prompt_tokens': usage.get('prompt_tokens', 0),
                'completion_tokens': usage.get('completion_tokens', 0),
                'total_tokens': usage.get('total_tokens', 0),
                'evaluation_status': 'not_scored',
                'error': result.get('error') or '',
            })

    metrics_path = run_dir / 'metrics.csv'
    with metrics_path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    successes = sum(bool(row['request_success']) for row in rows)
    print(f'Run: {run_dir}')
    print(f'Requisições HTTP bem-sucedidas: {successes}/{len(rows)}')
    print('Avaliação semântica: não realizada')
    return 0 if successes == len(rows) else 2


if __name__ == '__main__':
    raise SystemExit(main())
