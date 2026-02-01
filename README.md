# video-slice-core

Biblioteca core da aplicação Video Slice para processamento de vídeos.

## 📋 Descrição

Esta biblioteca fornece os componentes principais (core) para processamento de vídeos, incluindo:
- Modelos de domínio (Domain Models)
- DTOs (Data Transfer Objects)
- Casos de uso (Use Cases)
- Interfaces e contratos
- Enums e exceções customizadas
- Utilitários

## 🚀 Instalação

### Como dependência local

```bash
pip install -e /path/to/video-slice-core
```

### Como dependência do Git

```bash
pip install git+https://github.com/11soat-hackton-videoslice/video-slice-core.git
```

### Para desenvolvimento

```bash
git clone https://github.com/11soat-hackton-videoslice/video-slice-core.git
cd video-slice-core
pip install -e .
```

## 📦 Dependências

- `requests>=2.25.0`
- `opencv-python-headless==4.10.0.84`
- `Pillow==10.4.0`
- `numpy==1.26.4`

## 🔧 Uso

### Importando componentes

```python
# Adapters
from vdsc_core import VdscController, VdscProcessUseCase

# Domain
from vdsc_core import LogEntry, VdscMetadata

# DTOs
from vdsc_core import EventDTO, VdscMetadataDTO

# Enums
from vdsc_core import VdscStatusEnum, VideoQuality

# Exceptions
from vdsc_core import VdscException

# Interfaces
from vdsc_core import (
    VdscControllerInterface,
    VdscDataProxyInterface,
    VdscGatewayInferface
)
```

### Exemplo de uso

```python
from vdsc_core import VdscMetadataDTO, VdscMetadata, VdscStatusEnum, LogEntry

# Criar um DTO
dto = VdscMetadataDTO(
    video_id="video123",
    file_name="video.mp4",
    extension_file="mp4",
    status="UPLOADED",
    created="2026-01-13T00:00:00Z",
    user_id="user123",
    total_time=3600,
    unit_time="s",
    start_time=0,
    end_time=60,
    time_interval=[10],
    max_retry=3,
    retries=0,
    quality="high",
    logs=[]
)

# Converter DTO para entidade de domínio
metadata = VdscMetadata(dto=dto)

# Adicionar log
metadata.add_log(LogEntry("Processamento iniciado"))

# Alterar status
metadata.mark_as_processing()

# Validar
metadata.validate()

# Converter de volta para dict
data = metadata.to_dict()
```

## 🧪 Testes

### Executar testes unitários

```bash
pytest tests/unit/ -v
```

### Executar testes com cobertura

```bash
pytest tests/unit/ --cov=src --cov-report=term-missing --cov-report=html
```

### Cobertura atual

**91%** de cobertura de código ✅

## 📁 Estrutura do Projeto

```
video-slice-core/
├── src/
│   └── core/
│       ├── adapters/       # Adaptadores e controladores
│       ├── applications/   # Casos de uso
│       ├── domain/         # Modelos de domínio
│       ├── dtos/           # Data Transfer Objects
│       ├── enums/          # Enumerações
│       ├── exceptions/     # Exceções customizadas
│       ├── interfaces/     # Contratos e interfaces
│       └── utils/          # Utilitários
├── tests/
│   └── unit/              # Testes unitários
├── pyproject.toml         # Configuração do projeto
└── README.md              # Este arquivo
```

## 🔑 Principais Componentes

### Domain Models
- `VdscMetadata`: Metadados do vídeo com lógica de negócio
- `LogEntry`: Entradas de log com timestamp ISO8601

### DTOs
- `VdscMetadataDTO`: DTO para transferência de metadados
- `EventDTO`: DTO para eventos

### Use Cases
- `VdscProcessUseCase`: Processamento de vídeo com captura de frames

### Enums
- `VdscStatusEnum`: Status do processamento (UPLOADED, PROCESSING, FINISHED, FAILED, RETRYING)
- `VideoQuality`: Qualidades de vídeo (HIGH, MEDIUM, LOW)

### Exceptions
- `VdscException`: Exceção customizada com metadados

## 📝 Licença

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autor

**Tito Parizotto** - [titoparizotto@gmail.com](mailto:titoparizotto@gmail.com)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📊 Status

[![Tests](https://img.shields.io/badge/tests-174%20passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
