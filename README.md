# Video Slice Core

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=11soat-hackton-videoslice_video-slice-core&metric=alert_status&token=5972a76179f55b35b86a31bd473e55cfbd14c222)](https://sonarcloud.io/summary/new_code?id=11soat-hackton-videoslice_video-slice-core)
[![Test, Build e Publish video-slice core](https://github.com/11soat-hackathon-videoslice/video-slice-core/actions/workflows/build_test_deploy_lambda.yaml/badge.svg)](https://github.com/11soat-hackathon-videoslice/video-slice-core/actions/workflows/build_test_deploy_lambda.yaml)
[![Release](https://img.shields.io/badge/release-v1.0.0-blue)](https://github.com/11soat-hackathon-videoslice/video-slice-core/releases/tag/v1.0.0)

Biblioteca core para processamento de vídeos com arquitetura limpa e segregação de domínios.

## 📋 Visão Geral

A **video-slice-core** é uma biblioteca Python que implementa a lógica de negócio central para processamento de vídeos, seguindo os princípios da **Clean Architecture**. A biblioteca é organizada em domínios segregados e camadas bem definidas, facilitando a manutenção, testabilidade e extensibilidade do código.

### Domínios

#### Domínio Principal

**Slice**: Responsável pelo processamento de vídeos, incluindo:
- Extração de frames de vídeos
- Redimensionamento de frames
- Aplicação de filtros e transformações
- Geração de slices de vídeo
- Gerenciamento de metadados de processamento

#### Domínios Secundários

**URL**: Responsável pela geração de URLs pré-assinadas para:
- Download de vídeos originais
- Upload de vídeos processados
- Acesso temporário a recursos S3

**Notifications**: Responsável pelo envio de notificações para:
- Canal **E-mail**: notificações por correio eletrônico
- Canal **Web**: notificações via AppSync/GraphQL

## 🏗️ Arquitetura

A biblioteca segue os princípios da **Clean Architecture**, com segregação clara de responsabilidades em camadas:


### Camadas da Arquitetura

#### **Adaptadores | Adapters**
- **Controllers**: Orquestram o fluxo de dados entre a camada externa e os use cases
- **Gateways**: Implementam a comunicação com serviços externos (AWS, APIs, etc.)
- **Presenters**: Formatam os dados de saída para a camada externa

#### **Casos de Uso | Applications**
- Contêm a lógica de aplicação e orquestração de regras de negócio
- Independentes de frameworks e bibliotecas externas
- Coordenam o fluxo entre domínios

#### **Domínio | Domain**
- Entidades de negócio puras
- Contêm as regras de negócio fundamentais
- Independentes de qualquer framework ou tecnologia

#### **DTOs | Data Transfer Objects**
- Objetos para transferência de dados entre camadas
- Validação e serialização de dados

#### **Interfaces**
- Contratos que definem comportamentos esperados
- Inversão de dependência (Dependency Inversion Principle)
- Facilitam testes e substituição de implementações

## 🚀 Como Utilizar

### Instalação

Adicione a biblioteca ao seu `requirements.txt`:

```text
vdsc-core @ git+https://github.com/11soat-hackathon-videoslice/video-slice-core.git@v1.0.0
```

**Nota**: É necessário configurar um `GITHUB_TOKEN` (Personal Access Token) com permissões de leitura para acessar o repositório privado.

## 📦 Projetos de Implementação

Esta biblioteca é utilizada pelos seguintes projetos:

- **ms-video-slice**: Microserviço Lambda para processamento de vídeos
- **ms-video-url-generator**: Microserviço Lambda para geração de URLs pré-assinadas
- **ms-notification-email**: Microserviço Lambda para envio de notificações por e-mail
- **ms-notification-web**: Microserviço Lambda para envio de notificações web

## 🧪 Testes

A biblioteca possui cobertura de testes de no mínimo 80%. Para executar os testes:

```bash
pytest tests/unit/ --cov=src/core --cov-report=xml --cov-report=html --cov-report=term --junitxml=test-results.xml -v --cov-fail-under=80
```

## 📚 Documentação Adicional

- [Release v1.0.0](https://github.com/11soat-hackathon-videoslice/video-slice-core/releases/tag/v1.0.0)
- [Pipeline de CI/CD](https://github.com/11soat-hackathon-videoslice/video-slice-core/actions/runs/22137804661)
- [Análise de Qualidade - SonarCloud](https://sonarcloud.io/summary/new_code?id=11soat-hackton-videoslice_video-slice-core)

