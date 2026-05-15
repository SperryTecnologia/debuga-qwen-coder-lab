# 03 — Docker + NVIDIA Container Toolkit

## Por que este passo vem antes do Ollama

O Ollama em container precisa acessar a GPU NVIDIA. Para isso, o Docker precisa do **NVIDIA Container Toolkit** instalado e configurado. Sem ele, `--gpus all` não funciona e o Ollama roda apenas em CPU (extremamente lento para modelos 7B+).

A ordem correta é:

```
1. Driver NVIDIA no host/VM  ← já feito (doc 02)
2. Docker Engine             ← este documento
3. NVIDIA Container Toolkit  ← este documento
4. Ollama em container       ← próximo passo
```

---

## Instalação do Docker

### Ubuntu 22.04

```bash
# Remover versões antigas
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null

# Instalar dependências
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Adicionar chave GPG oficial do Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Adicionar repositório
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Adicionar usuário ao grupo docker (evitar sudo)
sudo usermod -aG docker $USER
newgrp docker
```

### Verificar instalação

```bash
docker --version
# Docker version 24.x.x, build ...

docker run hello-world
# Deve mostrar "Hello from Docker!"
```

---

## Instalação do NVIDIA Container Toolkit

### Adicionar repositório NVIDIA

```bash
# Configurar repositório
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Instalar
sudo apt update
sudo apt install -y nvidia-container-toolkit

# Configurar Docker para usar o runtime NVIDIA
sudo nvidia-ctk runtime configure --runtime=docker

# Reiniciar Docker
sudo systemctl restart docker
```

### Verificar configuração

```bash
# Verificar que o runtime nvidia está configurado
cat /etc/docker/daemon.json
# Deve conter: "default-runtime": "nvidia" ou "runtimes": {"nvidia": {...}}
```

---

## Testes de Validação

### Teste 1: Hello World Docker (sem GPU)

```bash
docker run --rm hello-world
```

**Resultado esperado:** Mensagem "Hello from Docker!" confirmando que o Docker funciona.

### Teste 2: NVIDIA CUDA com nvidia-smi

```bash
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

**Resultado esperado:** Mesma saída do `nvidia-smi` do host, mostrando a RTX 3090 com 24 GB.

```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.183.01   Driver Version: 535.183.01   CUDA Version: 12.2     |
|-------------------------------+----------------------+----------------------+
|   0  NVIDIA GeForce RTX 3090  |   00000000:00:05.0 Off|                  N/A |
| 30%   35C    P8    20W / 350W |      0MiB / 24576MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

### Teste 3: GPU específica (se houver múltiplas)

```bash
# Usar apenas GPU 0
docker run --rm --gpus '"device=0"' nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi

# Usar todas as GPUs
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

---

## Erros Comuns

### `docker: Error response from daemon: could not select device driver`

**Causa:** NVIDIA Container Toolkit não instalado ou Docker não reiniciado.

**Solução:**
```bash
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### `nvidia-smi: command not found` (dentro do container)

**Causa:** Imagem base não inclui nvidia-smi, ou toolkit não configurado.

**Solução:** Usar imagem `nvidia/cuda:*-base-*` que inclui nvidia-smi. Verificar que `--gpus all` está no comando.

### `Failed to initialize NVML: Unknown Error`

**Causa:** Driver do host incompatível com a versão CUDA do container.

**Solução:**
```bash
# Verificar versão do driver no host
nvidia-smi
# Se Driver Version < 535, atualizar:
sudo apt install -y nvidia-driver-535
sudo reboot
```

### `docker: permission denied`

**Causa:** Usuário não está no grupo docker.

**Solução:**
```bash
sudo usermod -aG docker $USER
# Fazer logout/login ou:
newgrp docker
```

### Container roda mas GPU não é usada

**Causa:** Faltou `--gpus all` no comando docker run.

**Solução:** Sempre incluir `--gpus all` ou `--gpus '"device=0"'`.

---

## Configuração do daemon.json (Referência)

Após instalar o toolkit, o `/etc/docker/daemon.json` deve conter:

```json
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "args": [],
      "path": "nvidia-container-runtime"
    }
  }
}
```

Se `default-runtime` for `nvidia`, todos os containers terão acesso à GPU automaticamente (sem precisar de `--gpus all`). Caso contrário, `--gpus all` é obrigatório.

---

## Checklist de Validação

```
[ ] docker --version retorna 24.x+
[ ] docker run hello-world funciona
[ ] nvidia-container-toolkit está instalado
[ ] /etc/docker/daemon.json contém runtime nvidia
[ ] docker run --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi mostra a GPU
[ ] VRAM total mostra 24576 MiB (RTX 3090)
[ ] Docker está reiniciado após configurar toolkit
```

---

## Próximo Passo

Com Docker + GPU funcionando, é hora de entender os modelos disponíveis. Veja [04-MODELOS-QWEN-COMPARATIVO.md](04-MODELOS-QWEN-COMPARATIVO.md).
