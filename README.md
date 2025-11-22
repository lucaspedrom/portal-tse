# Portal TSE - Pipeline de Dados Eleitorais

Pipeline de ingestão e processamento de dados do Portal de Dados Abertos do Tribunal Superior Eleitoral (TSE).

## 📋 Sobre o Projeto

Este projeto tem como objetivo automatizar a coleta, transformação e análise de dados eleitorais disponibilizados pelo TSE. O pipeline está sendo desenvolvido em etapas, seguindo a arquitetura de processamento de dados moderna.

## 🏗️ Estrutura do Projeto

```
portal-tse/
├── data/                          # Diretório de armazenamento de dados
│   └── raw/                       # Dados brutos baixados do TSE
│       ├── candidatos/            # Dados de candidatos
│       ├── cassacao_candidatos/   # Motivos da cassações de candidatos
│       ├── bens_candidatos/       # Bens declarados por candidatos
│       ├── votacao_partido_munzona/    # Votação por partido
│       └── votacao_candidato_munzona/  # Votação nominal por candidato
│
├── src/                           # Código fonte do projeto
│   ├── extract/                   # ✅ Módulo de ingestão de dados
│   │   ├── config_ingest.py       # Configurações de consultas TSE
│   │   ├── download_data.py       # Função principal de download
│   │   └── test_download.py       # Script interativo de download
│   │
│   └── transform/                 # 🚧 Módulo de transformação (em desenvolvimento)
│
├── requirements.txt               # Dependências do projeto
└── README.md                      # Este arquivo
```

## ✅ Funcionalidades Implementadas

### 📥 Extract (Ingestão de Dados)

O módulo de **extract** é responsável por baixar dados do Portal de Dados Abertos do TSE e armazená-los localmente.

#### Tipos de Consulta Disponíveis:

| Tipo | Descrição | Pasta de Destino |
|------|-----------|------------------|
| `cand` | Dados de candidatos | `data/raw/candidatos/{ano}/` |
| `cassacao` | Motivos de cassação de candidatos | `data/raw/cassacao_candidatos/{ano}/` |
| `bens` | Bens declarados por candidatos | `data/raw/bens_candidatos/{ano}/` |
| `vot_partido` | Votação por partido, município e zona | `data/raw/votacao_partido_munzona/{ano}/` |
| `vot_cand` | Votação nominal por candidato, município e zona | `data/raw/votacao_candidato_munzona/{ano}/` |

#### Características:

- ✅ Download automático de arquivos ZIP do TSE
- ✅ Extração do arquivo `*_BRASIL.csv` de cada ZIP
- ✅ Controle de versão por data de ingestão (formato: `YYYYMMDD`)
- ✅ Tratamento de erros e logging detalhado
- ✅ Validação de entrada (tipo de consulta e ano)
- ✅ Armazenamento organizado por tipo e ano

## 🚀 Como Usar

### Instalação

> [!IMPORTANT]
> **Requisito:** Python 3.4 ou superior
> 
> Este projeto requer Python 3.4+ devido ao uso de bibliotecas da standard library como `pathlib`. Recomenda-se usar Python 3.8 ou superior para melhor compatibilidade e performance.

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd portal-tse
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Download de Dados (Modo Interativo)

Execute o script interativo para baixar dados:

```bash
python src/extract/test_download.py
```

O script irá:
1. Exibir as opções de consulta disponíveis
2. Solicitar o tipo de consulta desejado
3. Solicitar o ano eleitoral (entre 2010 e 2024)
4. Baixar e armazenar automaticamente o arquivo

### Download de Dados (Programático)

Você também pode importar e usar a função diretamente em seus scripts:

```python
from src.extract.download_data import download_tse_data

# Baixar dados de candidatos de 2022
caminho = download_tse_data('cand', 2022)
print(f"Arquivo salvo em: {caminho}")

# Baixar bens de candidatos de 2020
caminho = download_tse_data('bens', 2020)
```

## 📂 Armazenamento de Dados

Todos os dados são armazenados na pasta `data/` seguindo a estrutura:

```
data/raw/{tipo_consulta}/{ano}/{consulta}_{ano}_BRASIL_{data_ingestao}.csv
```

**Exemplo:**
```
data/raw/candidatos/2022/consulta_cand_2022_BRASIL_20251122.csv
data/raw/bens_candidatos/2022/bem_candidato_2022_BRASIL_20251122.csv
```

O sufixo `{data_ingestao}` permite controle de versões, possibilitando:
- Rastrear quando os dados foram baixados
- Manter múltiplas versões do mesmo arquivo
- Comparar dados baixados em datas diferentes

### 🏛️ Arquitetura de Dados

A estrutura de pastas dentro do diretório `data/` é um **modelo planejado** que se baseia, parcialmente, na **arquitetura medalhão** (Medallion Architecture), garantindo maior organização para quem for utilizar o repositório.

**Camadas planejadas:**
- **`data/raw/`** (Bronze): Dados brutos, exatamente como obtidos da fonte
- **`data/processed/`** (Silver): Dados limpos e transformados *(em desenvolvimento)*
- **`data/curated/`** (Gold): Dados agregados e prontos para análise *(planejado)*

Esta abordagem facilita:
- ✅ Rastreabilidade dos dados desde a origem
- ✅ Separação clara entre diferentes estágios de processamento
- ✅ Reprodutibilidade das transformações
- ✅ Organização escalável conforme o projeto cresce

> [!NOTE]
> **Sobre os Dados no Repositório**
> 
> Os dados adquiridos através dos scripts **não estão incluídos neste repositório** pelos seguintes motivos:
> - 📦 **Tamanho**: Os arquivos CSV do TSE são muito grandes (alguns com centenas de MB)
> - 🎯 **Uso Individual**: Cada usuário deve baixar os dados específicos para sua finalidade e período de interesse
> - 🔄 **Atualização**: Os dados do TSE são atualizados periodicamente, e cada usuário pode precisar de versões diferentes
> 
> A pasta `data/` será criada automaticamente quando você executar os scripts de download pela primeira vez.

## 🔧 Configuração

As configurações de consultas estão centralizadas em `src/extract/config_ingest.py`. Para adicionar novos tipos de consulta:

1. Edite o dicionário `CONSULTAS_CONFIG`
2. Adicione a nova entrada com:
   - `consulta`: Nome da consulta no portal TSE
   - `pasta_destino`: Pasta onde os dados serão armazenados
   - `descricao`: Descrição amigável da consulta

## 🚧 Roadmap

- [x] **Extract**: Ingestão de dados do TSE
  - [x] Download automatizado
  - [x] Extração de arquivos ZIP
  - [x] Controle de versão por data
  - [x] Script interativo
- [ ] **Transform**: Transformação e limpeza de dados
  - [ ] Padronização de schemas
  - [ ] Tratamento de valores nulos
  - [ ] Agregações e derivações
- [ ] **Load**: Carregamento em banco de dados
- [ ] **Análise**: Dashboards e relatórios

## 📊 Fonte dos Dados

Os dados são obtidos do [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br/).

**URL Base:** `https://cdn.tse.jus.br/estatistica/sead/odsele/`

## 📝 Licença

Este projeto é de código aberto e está disponível para uso educacional e de pesquisa.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---

**Desenvolvido para facilitar a aquisição e análise de dados eleitorais brasileiros.**
