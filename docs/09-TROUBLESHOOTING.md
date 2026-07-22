# 09 — Troubleshooting

## Problemas com GPU

### nvidia-smi: command not found

**Causa:** Driver NVIDIA não instalado na VM.

**Solução:**
```bash
sudo apt update
sudo apt install -y nvidia-driver-535
sudo reboot
nvidia-smi
```

### nvidia-smi: No devices were found

**Causa:** GPU não atribuída à VM via DDA, ou DDA não configurado corretamente.

**Solução:**
1. No host Windows, verificar se a GPU está atribuída:
```powershell
Get-VMAssignableDevice -VMName "Ubuntu-GPU"
```
2. Se vazio, reatribuir (VM deve estar desligada):
```powershell
Stop-VM -Name "Ubuntu-GPU" -Force
Add-VMAssignableDevice -VMName "Ubuntu-GPU" -LocationPath $locationPath
Start-VM -Name "Ubuntu-GPU"
```
3. Verificar se Secure Boot está desabilitado na VM (obrigatório para DDA).

### CUDA out of memory (OOM)

**Causa:** Modelo muito grande para a VRAM disponível, ou contexto muito longo.

**Sintomas:**
```
Error: CUDA out of memory. Tried to allocate X MiB
```

**Solução:**
```bash
# Verificar uso atual de VRAM
nvidia-smi

# Descarregar modelo atual
curl http://localhost:11434/api/generate -d '{"model": "qwen2.5:7b-instruct", "keep_alive": 0}'

# Usar modelo menor
docker exec ollama ollama pull qwen2.5:7b-instruct  # 5 GB vs 9 GB do 14B

# Ou limitar contexto
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:14b",
  "prompt": "...",
  "options": {"num_ctx": 4096}
}'
```

### GPU utilization 0% mas modelo carregado

**Causa:** Modelo carregado na VRAM mas sem requisições ativas. Isso é normal — a GPU só é utilizada durante a geração.

**Verificação:**
```bash
# Enviar uma requisição e observar GPU-Util subir
watch -n 1 nvidia-smi
# Em outro terminal:
curl http://localhost:11434/api/generate -d '{"model": "qwen2.5:7b-instruct", "prompt": "Conte até 100", "stream": false}'
```

---

## Problemas com Docker

### docker: Error response from daemon: could not select device driver

**Causa:** NVIDIA Container Toolkit não instalado ou Docker não reiniciado.

**Solução:**
```bash
# Instalar toolkit
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Testar
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

### Container Ollama reinicia em loop (restart loop)

**Causa:** GPU não acessível, ou VRAM insuficiente para carregar.

**Diagnóstico:**
```bash
docker logs ollama --tail=50
```

**Soluções comuns:**
- Verificar se `--gpus all` está no docker run ou no docker-compose
- Verificar se NVIDIA Container Toolkit está configurado
- Verificar se outro processo está usando a GPU

### Permission denied ao acessar GPU no container

**Causa:** Usuário não tem permissão ou cgroups não configurados.

**Solução:**
```bash
# Verificar grupos
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Se persistir, rodar container como root
docker run --rm --gpus all --user root nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

---

## Problemas com Ollama

### Ollama não responde (connection refused)

**Causa:** Ollama não está rodando ou está em outra porta.

**Diagnóstico:**
```bash
# Verificar se container está rodando
docker ps | grep ollama

# Verificar logs
docker logs ollama --tail=20

# Verificar porta
docker port ollama
# Deve mostrar: 11434/tcp -> 0.0.0.0:11434
```

**Solução:**
```bash
# Reiniciar
docker restart ollama

# Se não resolver, recriar
docker rm -f ollama
docker run -d --gpus all \
  -v ollama-data:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  --restart unless-stopped \
  ollama/ollama
```

### Modelo não encontrado (model not found)

**Causa:** Modelo não foi baixado ou nome incorreto.

**Solução:**
```bash
# Listar modelos disponíveis
docker exec ollama ollama list

# Baixar modelo (nome exato)
docker exec ollama ollama pull qwen2.5:7b-instruct

# Nomes comuns:
# qwen2.5:7b-instruct (NÃO qwen2.5-7b-instruct)
# qwen2.5-coder:7b (NÃO qwen2.5:coder-7b)
# qwen3:14b (NÃO qwen3-14b)
```

### Resposta muito lenta (< 5 tok/s com modelo 7B)

**Causa:** Modelo rodando em CPU em vez de GPU.

**Diagnóstico:**
```bash
# Verificar se GPU está sendo usada durante geração
nvidia-smi  # GPU-Util deve subir durante geração

# Verificar logs do Ollama
docker logs ollama 2>&1 | grep -i "gpu\|cuda\|cpu"
```

**Solução:**
```bash
# Garantir que container tem acesso à GPU
docker rm -f ollama
docker run -d --gpus all \
  -v ollama-data:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  --restart unless-stopped \
  ollama/ollama

# Verificar
docker exec ollama nvidia-smi
```

### Ollama trava após contexto longo

**Causa:** KV cache excedeu a VRAM disponível.

**Solução:**
```bash
# Limitar contexto
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b-instruct",
  "prompt": "...",
  "options": {"num_ctx": 4096}
}'

# Ou reiniciar Ollama para limpar memória
docker restart ollama
```

---

## Problemas com Hyper-V DDA

### SurveyDDA mostra "Device is not assignable"

**Causa:** Slot PCIe não suporta DDA (sem ACS ou FLR).

**Solução:**
1. Mover GPU para outro slot PCIe (preferencialmente x16 mais próximo do CPU)
2. Verificar BIOS: habilitar IOMMU/VT-d/AMD-Vi
3. Verificar BIOS: habilitar ACS (Access Control Services) se disponível
4. Atualizar firmware da placa-mãe

### "Traffic from this device may be redirected"

**Causa:** GPU está em slot PCIe que compartilha bridge com outros dispositivos.

**Solução:** Mover GPU para slot direto no root complex (sem bridge intermediário). Geralmente é o slot x16 primário.

### VM não inicia após atribuir GPU

**Causa:** Configuração de MMIO insuficiente.

**Solução:**
```powershell
Stop-VM -Name "Ubuntu-GPU" -Force
Set-VM -Name "Ubuntu-GPU" -LowMemoryMappedIoSpace 3Gb
Set-VM -Name "Ubuntu-GPU" -HighMemoryMappedIoSpace 33280Mb
Start-VM -Name "Ubuntu-GPU"
```

### GPU desaparece da VM após reboot do host

**Causa:** DDA não persiste automaticamente em alguns cenários.

**Solução:** Criar script de startup no host:
```powershell
# Salvar como C:\Scripts\reassign-gpu.ps1
$vmName = "Ubuntu-GPU"
$locationPath = "PCIROOT(0)#PCI(0100)#PCI(0000)"

if ((Get-VM -Name $vmName).State -eq "Off") {
    Add-VMAssignableDevice -VMName $vmName -LocationPath $locationPath -ErrorAction SilentlyContinue
    Start-VM -Name $vmName
}
```

---

## Problemas de Integração com debuga.ai

### App não consegue conectar ao Ollama

**Causa:** URL incorreta ou rede Docker não compartilhada.

**Diagnóstico:**
```bash
# Testar de dentro do container app
docker exec debuga-app curl -s http://ollama:11434
# Deve retornar: "Ollama is running"
```

**Se falhar:**
```bash
# Verificar se estão na mesma rede
docker network inspect projeto-teste_default | grep -A5 "ollama\|app"

# Verificar nome do serviço no docker-compose
grep "ollama" docker/docker-compose.yml
```

### ENABLE_LOCAL_INFERENCE=true mas app usa cloud

**Causa:** Variável não chegou ao container (rebuild necessário).

**Solução:**
```bash
# Verificar variável dentro do container
docker exec debuga-app env | grep LOCAL_INFERENCE

# Se não aparecer, rebuild
docker compose -f docker/docker-compose.yml up -d --build app
```

### Timeout ao gerar resposta

**Causa:** Modelo muito grande, contexto muito longo, ou primeira requisição (cold start).

**Solução:**
```bash
# Pré-carregar modelo (warm up)
docker exec debuga-ollama curl -s http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b-instruct",
  "prompt": "Olá",
  "keep_alive": -1
}'

# Aumentar timeout no backend (se configurável)
# Ou usar modelo menor para respostas mais rápidas
```

---

## Problemas de Performance

### VRAM fragmentada (modelo não carrega mesmo com espaço)

**Causa:** Fragmentação de memória GPU após múltiplos load/unload.

**Solução:**
```bash
# Reiniciar Ollama para limpar VRAM
docker restart ollama

# Verificar VRAM limpa
nvidia-smi
# Memory-Usage deve mostrar ~0 MiB
```

### Temperatura da GPU muito alta (>85°C)

**Causa:** Ventilação insuficiente ou carga contínua prolongada.

**Monitoramento:**
```bash
nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader -l 5
```

**Solução:**
- Verificar ventilação do servidor/rack
- Limitar concorrência (uma requisição por vez)
- Usar modelo menor (menos carga na GPU)
- Configurar power limit:
```bash
sudo nvidia-smi -pl 300  # Limitar a 300W (padrão 350W na 3090)
```

---

## Diagnóstico Rápido (Checklist)

```bash
#!/bin/bash
echo "=== Diagnóstico Rápido ==="

echo -n "1. nvidia-smi: "
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader 2>/dev/null || echo "FALHOU"

echo -n "2. Docker: "
docker --version 2>/dev/null || echo "FALHOU"

echo -n "3. NVIDIA Toolkit: "
nvidia-ctk --version 2>/dev/null || echo "FALHOU"

echo -n "4. Container Ollama: "
docker ps --filter name=ollama --format "{{.Status}}" 2>/dev/null || echo "FALHOU"

echo -n "5. Ollama API: "
curl -s http://localhost:11434 2>/dev/null || echo "FALHOU"

echo -n "6. Modelos: "
curl -s http://localhost:11434/api/tags 2>/dev/null | jq -r '.models[].name' 2>/dev/null || echo "NENHUM"

echo -n "7. GPU no container: "
docker exec ollama nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo "FALHOU"

echo "=== Fim ==="
```

---

## Quando Escalar

| Sintoma | Causa provável | Solução |
|---------|---------------|---------|
| Respostas lentas com modelo 7B | GPU saturada por concorrência | Limitar requisições simultâneas |
| OOM frequente com 14B | VRAM insuficiente para contexto | Limitar num_ctx ou usar 7B |
| Latência alta (>5s TTFT) | Cold start (modelo descarregado) | keep_alive=-1 |
| Qualidade insuficiente | Modelo pequeno demais | Upgrade para 14B ou 30B-a3b |
| Múltiplos usuários simultâneos | Single-GPU não escala | Adicionar segunda GPU ou usar vLLM |

---

## Referências Úteis

- [Ollama GitHub Issues](https://github.com/ollama/ollama/issues) — problemas conhecidos e workarounds
- [NVIDIA Container Toolkit Docs](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/) — documentação oficial
- [Hyper-V DDA Guide](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/deploy/deploying-graphics-devices-using-dda) — guia Microsoft oficial
