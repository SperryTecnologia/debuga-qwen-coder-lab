# 02 — GPU Passthrough com Hyper-V DDA (RTX 3090)

## O que é Hyper-V DDA

**DDA (Discrete Device Assignment)** é a tecnologia da Microsoft que permite atribuir um dispositivo PCIe físico diretamente a uma máquina virtual Hyper-V. Diferente de GPU-P (particionamento), o DDA entrega a GPU **inteira** à VM — a VM vê o dispositivo como se fosse hardware nativo.

> DDA é o equivalente Microsoft ao PCI Passthrough do KVM/QEMU (VFIO).

### Requisitos para DDA

| Requisito | Detalhe |
|-----------|---------|
| Windows Server | 2016, 2019 ou 2022 Datacenter |
| CPU | Intel VT-d ou AMD-Vi habilitado na BIOS |
| GPU | NVIDIA com suporte SR-IOV/DDA (RTX 3090, A100, etc.) |
| Slot PCIe | Deve ser "assignable" segundo o SurveyDDA |
| VM Generation | Generation 2 |
| Secure Boot | Desabilitado na VM |

---

## Por que a RTX 3090 precisa aparecer como "Assignable"

O script `SurveyDDA.ps1` da Microsoft verifica se o dispositivo PCIe atende aos critérios de DDA. A GPU deve aparecer como:

```
Device is assignable: True
```

Se aparecer `False`, o dispositivo **não pode** ser atribuído à VM. As causas mais comuns são:

1. **ACS (Access Control Services) não suportado** no slot PCIe
2. **Slot PCIe não suporta FLR** (Function Level Reset)
3. **IOMMU não habilitado** na BIOS
4. **Driver do host está usando o dispositivo** (precisa desmontar)

---

## O Erro "Traffic from this device may be redirected"

Este aviso aparece no SurveyDDA quando o slot PCIe da GPU está em uma topologia onde o tráfego pode ser interceptado por outro dispositivo (bridge, switch PCIe compartilhado).

```
DVHCI: Traffic from this device may be redirected to other devices
```

### Por que mudar de slot PCIe resolveu

A RTX 3090 estava em um slot PCIe que compartilhava um switch/bridge com outros dispositivos. Ao mover para um slot PCIe **diretamente conectado ao root complex** (sem bridge intermediário), o SurveyDDA passou a reportar `Assignable: True`.

**Regra prática:** Use o slot PCIe x16 mais próximo do processador (geralmente o slot 1).

---

## Identificando o Dispositivo

### InstanceId

O `InstanceId` identifica unicamente o dispositivo no Windows:

```powershell
# Listar GPUs
Get-PnpDevice -Class Display

# Obter InstanceId da RTX 3090
$gpu = Get-PnpDevice -FriendlyName "*RTX 3090*"
$gpu.InstanceId
# Exemplo: PCI\VEN_10DE&DEV_2204&SUBSYS_...&REV_A1\4&1234ABCD&0&0008
```

### LocationPath

O `LocationPath` identifica o slot PCIe físico:

```powershell
$locationPath = (Get-PnpDeviceProperty -InstanceId $gpu.InstanceId `
  -KeyName DEVPKEY_Device_LocationPaths).Data[0]
# Exemplo: PCIROOT(0)#PCI(0100)#PCI(0000)
```

---

## Comandos PowerShell para DDA

### 1. Executar SurveyDDA

```powershell
# Baixar e executar o script de survey
.\SurveyDDA.ps1
```

### 2. Desmontar a GPU do Host

```powershell
# Desabilitar o dispositivo no host
Disable-PnpDevice -InstanceId $gpu.InstanceId -Confirm:$false

# Desmontar do host (liberar para DDA)
Dismount-VMHostAssignableDevice -LocationPath $locationPath -Force
```

### 3. Atribuir à VM

```powershell
# Nome da VM
$vmName = "Ubuntu-GPU"

# Desligar a VM (obrigatório)
Stop-VM -Name $vmName -Force

# Configurar a VM para DDA
Set-VM -Name $vmName -AutomaticStopAction TurnOff
Set-VM -Name $vmName -GuestControlledCacheTypes $true
Set-VM -Name $vmName -LowMemoryMappedIoSpace 3Gb
Set-VM -Name $vmName -HighMemoryMappedIoSpace 33280Mb

# Atribuir a GPU
Add-VMAssignableDevice -VMName $vmName -LocationPath $locationPath

# Iniciar a VM
Start-VM -Name $vmName
```

### 4. Verificar atribuição

```powershell
Get-VMAssignableDevice -VMName $vmName
```

---

## Validação dentro do Ubuntu

### Verificar se a GPU aparece

```bash
# Listar dispositivos PCIe (deve mostrar a RTX 3090)
lspci | grep -i nvidia
# Saída esperada:
# 00:05.0 3D controller: NVIDIA Corporation GA102 [GeForce RTX 3090] (rev a1)

# Verificar driver NVIDIA
nvidia-smi
```

### Saída esperada do nvidia-smi

```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.183.01   Driver Version: 535.183.01   CUDA Version: 12.2     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce RTX 3090  |   00000000:00:05.0 Off|                  N/A |
| 30%   35C    P8    20W / 350W |      0MiB / 24576MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

### Se nvidia-smi não funcionar

```bash
# Instalar driver NVIDIA
sudo apt update
sudo apt install -y nvidia-driver-535

# Reiniciar
sudo reboot

# Verificar novamente
nvidia-smi
```

---

## Como Devolver a GPU ao Host

Se precisar remover a GPU da VM e devolvê-la ao host:

```powershell
# 1. Desligar a VM
Stop-VM -Name $vmName -Force

# 2. Remover o dispositivo da VM
Remove-VMAssignableDevice -VMName $vmName -LocationPath $locationPath

# 3. Montar de volta no host
Mount-VMHostAssignableDevice -LocationPath $locationPath

# 4. Habilitar o dispositivo
Enable-PnpDevice -InstanceId $gpu.InstanceId -Confirm:$false
```

Após esses comandos, o host volta a ter acesso à GPU (útil para manutenção ou atualização de driver).

---

## Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `Device is not assignable` | Slot PCIe não suporta DDA | Mover GPU para outro slot PCIe |
| `Traffic may be redirected` | Slot compartilha bridge | Usar slot direto no root complex |
| `Failed to assign device` | VM ligada ou Gen 1 | Desligar VM, usar Gen 2 |
| `MMIO space insufficient` | HighMemoryMappedIoSpace baixo | Aumentar para 33280Mb |
| GPU não aparece no Ubuntu | Driver não instalado | Instalar nvidia-driver-535 |
| `nvidia-smi` retorna erro | Driver incompatível | Reinstalar driver correto |

---

## Próximo Passo

Com a GPU funcionando no Ubuntu, instalar Docker e NVIDIA Container Toolkit. Veja [03-DOCKER-NVIDIA-TOOLKIT.md](03-DOCKER-NVIDIA-TOOLKIT.md).
