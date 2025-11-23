# Portal TSE - Pipeline de Dados Eleitorais

Pipeline de ingestão e processamento de dados do Portal de Dados Abertos do Tribunal Superior Eleitoral (TSE) com otimização de cache HTTP.

## 📋 Sobre o Projeto

Este projeto tem como objetivo automatizar a coleta, transformação e análise de dados eleitorais disponibilizados pelo TSE. O pipeline está sendo desenvolvido em etapas, seguindo a arquitetura de processamento de dados moderna com foco em eficiência e escalabilidade.

## 🏗️ Estrutura do Projeto

```
portal-tse/
├── data/                          # Diretório de armazenamento de dados
│   └── raw/                       # Dados brutos baixados do TSE (Bronze Layer)
│       ├── candidatos/            # Dados de candidatos
│       ├── cassacao_candidatos/   # Motivos de cassações de candidatos
│       ├── bens_candidatos/       # Bens declarados por candidatos
│       ├── votacao_partido_munzona/    # Votação por partido
│       ├── votacao_candidato_munzona/  # Votação nominal por candidato
│       └── tse_cache_metadata.json     # Metadados de cache HTTP
│
├── src/                           # Código fonte do projeto
│   ├── extract/                   # ✅ Módulo de ingestão de dados
│   │   ├── config_ingest.py       # Configurações de consultas TSE
│   │   ├── download_data.py       # Função principal de download
│   │   ├── metadata_handler.py    # Gerenciador de cache HTTP
│   │   └── test_download.py       # Script interativo de download
│   │
│   └── transform/                 # 🚧 Módulo de transformação (em desenvolvimento)
│
├── requirements.txt               # Dependências do projeto
└── README.md                      # Este arquivo
```

## ✅ Funcionalidades Implementadas

### 📥 Extract (Ingestão de Dados)

O módulo de **extract** é responsável por baixar dados do Portal de Dados Abertos do TSE e armazená-los localmente com otimização inteligente de cache.

#### Tipos de Consulta Disponíveis:

| Tipo | Descrição | Pasta de Destino |
|------|-----------|------------------|
| `cand` | Dados de candidatos | `data/raw/candidatos/{ano}/` |
| `cassacao` | Motivos de cassação de candidatos | `data/raw/cassacao_candidatos/{ano}/` |
| `bens` | Bens declarados por candidatos | `data/raw/bens_candidatos/{ano}/` |
| `vot_partido` | Votação por partido, município e zona | `data/raw/votacao_partido_munzona/{ano}/` |
| `vot_cand` | Votação nominal por candidato, município e zona | `data/raw/votacao_candidato_munzona/{ano}/` |

#### Características:

- ✅ **Download automático** de arquivos ZIP do TSE
- ✅ **Otimização de cache HTTP** usando ETag e Last-Modified
- ✅ **Extração inteligente** do arquivo `*_BRASIL.csv` de cada ZIP
- ✅ **Controle de versão** por data de ingestão (formato: `YYYYMMDD`)
- ✅ **Tratamento de erros** e logging detalhado
- ✅ **Validação de entrada** (tipo de consulta e ano)
- ✅ **Armazenamento organizado** por tipo e ano
- ✅ **Caminhos customizáveis** para flexibilidade de armazenamento
- ✅ **Metadados rastreáveis** com caminhos relativos para portabilidade

### 🚀 Sistema de Cache HTTP

O pipeline implementa um sistema inteligente de cache que **evita downloads desnecessários**, economizando:
- ⚡ **Tempo**: Verifica em ~1 segundo vs. download de 5-10 segundos
- 💾 **Banda**: Requisição HEAD (~500 bytes) vs. arquivo completo (50-200 MB)
- 🌐 **Carga no servidor**: Reduz requisições pesadas ao TSE

#### Como Funciona:

1. **Requisição HEAD**: Antes de baixar, consulta apenas os headers do arquivo
2. **Comparação de ETag**: Verifica se o arquivo mudou no servidor
3. **Fallback Last-Modified**: Usa data de modificação se ETag não disponível
4. **Download Condicional**: Só baixa se o arquivo foi atualizado

#### Arquivo de Metadados:

O cache é gerenciado através do arquivo `data/raw/tse_cache_metadata.json`:

```json
{
  "cand_2022": {
    "ETag": "\"abc123\"",
    "Last-Modified": "Wed, 21 Oct 2020 07:28:00 GMT",
    "file_path": "candidatos/2022/consulta_cand_2022_BRASIL_20251123.csv"
  }
}
```

**Campos:**
- `ETag`: Identificador único do arquivo no servidor (verificação primária)
- `Last-Modified`: Data de última modificação (verificação secundária)
- `file_path`: Caminho relativo ao `base_path` (portabilidade)

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

2. Crie e ative um ambiente virtual (Recomendado):
```bash
# No Windows:
python -m venv venv
.\venv\Scripts\Activate

# No Linux/macOS:
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:
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
4. **Verificar cache** antes de baixar
5. Baixar e armazenar automaticamente (se necessário)

**Exemplo de execução:**
```
============================================================
DOWNLOAD DE DADOS DO TSE - Portal de Dados Abertos
============================================================

Tipos de consulta disponíveis:
  1. [cand] - Dados de candidatos
  ...

Digite o tipo de consulta: cand
Digite o ano eleitoral: 2022

🚀 Iniciando download...

INFO - Verificando cache para: https://...
INFO - Cache válido para cand_2022 (ETag match). Download não necessário.

✅ CACHE VÁLIDO - DOWNLOAD NÃO NECESSÁRIO!
Os dados já estão atualizados. Nenhum download foi realizado.
```

### Download de Dados (Programático)

Você também pode importar e usar a função diretamente em seus scripts:

```python
from src.extract.download_data import download_tse_data

# Baixar dados de candidatos de 2022 (caminho padrão)
caminho = download_tse_data('cand', 2022)
if caminho:
    print(f"Arquivo salvo em: {caminho}")
else:
    print("Cache válido - download não necessário")

# Baixar com caminho customizado
caminho = download_tse_data('bens', 2020, base_path="D:/meu_datalake")
```

**Retornos possíveis:**
- `str`: Caminho completo do arquivo baixado
- `None`: Cache válido, download não foi necessário

### Caminhos Customizados

O sistema suporta caminhos de armazenamento customizados:

```python
# Caminho absoluto
download_tse_data('cand', 2022, base_path="D:/datalake/bronze")

# Caminho relativo (a partir do diretório de execução)
download_tse_data('cand', 2022, base_path="./dados_tse")
```

> [!NOTE]
> Se o diretório especificado não existir, ele será **criado automaticamente** com um aviso no log.

## 📂 Armazenamento de Dados

Todos os dados são armazenados seguindo a estrutura:

```
{base_path}/{tipo_consulta}/{ano}/{consulta}_{ano}_BRASIL_{data_ingestao}.csv
```

**Exemplo (caminho padrão):**
```
data/raw/candidatos/2022/consulta_cand_2022_BRASIL_20251123.csv
data/raw/bens_candidatos/2022/bem_candidato_2022_BRASIL_20251123.csv
```

**Exemplo (caminho customizado: `D:/datalake`):**
```
D:/datalake/candidatos/2022/consulta_cand_2022_BRASIL_20251123.csv
D:/datalake/bens_candidatos/2022/bem_candidato_2022_BRASIL_20251123.csv
```

O sufixo `{data_ingestao}` permite controle de versões, possibilitando:
- ✅ Rastrear quando os dados foram baixados
- ✅ Manter múltiplas versões do mesmo arquivo
- ✅ Comparar dados baixados em datas diferentes

### 🏛️ Arquitetura de Dados (Medallion Architecture)

A estrutura de pastas segue a **arquitetura medalhão** (Medallion Architecture), garantindo organização escalável e rastreabilidade:

**Camadas implementadas/planejadas:**
- **`data/raw/`** (Bronze): ✅ Dados brutos, exatamente como obtidos da fonte
- **`data/processed/`** (Silver): 🚧 Dados limpos e transformados *(em desenvolvimento)*
- **`data/curated/`** (Gold): 📋 Dados agregados e prontos para análise *(planejado)*

Esta abordagem facilita:
- ✅ Rastreabilidade dos dados desde a origem
- ✅ Separação clara entre diferentes estágios de processamento
- ✅ Reprodutibilidade das transformações
- ✅ Organização escalável conforme o projeto cresce
- ✅ Migração futura para cloud (S3, Azure Blob, GCP Storage)

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

### Tipos de Consulta

As configurações de consultas estão centralizadas em `src/extract/config_ingest.py`. Para adicionar novos tipos de consulta:

1. Edite o dicionário `CONSULTAS_CONFIG`
2. Adicione a nova entrada com:
   - `consulta`: Nome da consulta no portal TSE
   - `pasta_destino`: Pasta onde os dados serão armazenados
   - `descricao`: Descrição amigável da consulta

### Cache HTTP

O cache é gerenciado automaticamente, mas você pode:

- **Forçar novo download**: Delete o arquivo `data/raw/tse_cache_metadata.json`
- **Invalidar cache específico**: Edite o JSON e remova a entrada desejada
- **Verificar metadados**: Inspecione o arquivo JSON para ver ETags e caminhos

## 🚧 Roadmap

- [x] **Extract**: Ingestão de dados do TSE
  - [x] Download automatizado
  - [x] Extração de arquivos ZIP
  - [x] Controle de versão por data
  - [x] Script interativo
  - [x] Sistema de cache HTTP (ETag/Last-Modified)
  - [x] Gerenciamento de metadados
  - [x] Suporte a caminhos customizados
  - [x] Caminhos relativos para portabilidade
- [ ] **Transform**: Transformação e limpeza de dados
  - [ ] Padronização de schemas
  - [ ] Tratamento de valores nulos
  - [ ] Agregações e derivações
  - [ ] Conversão para formatos otimizados (Parquet)
- [ ] **Load**: Carregamento em banco de dados
  - [ ] Integração com PostgreSQL/MySQL
  - [ ] Suporte a Data Warehouses (BigQuery, Redshift)
- [ ] **Análise**: Dashboards e relatórios
  - [ ] Dashboards interativos
  - [ ] Análises estatísticas

## 📊 Fonte dos Dados

Os dados são obtidos do [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br/).

**URL Base:** `https://cdn.tse.jus.br/estatistica/sead/odsele/`

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **requests**: Download de arquivos e requisições HTTP
- **pathlib**: Manipulação de caminhos de forma portável
- **zipfile**: Extração de arquivos compactados
- **json**: Gerenciamento de metadados de cache
- **logging**: Sistema de logs detalhado

## 📝 Licença

Este projeto é de código aberto e está disponível para uso educacional e de pesquisa.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---

**Desenvolvido para facilitar a aquisição e análise de dados eleitorais brasileiros com eficiência e escalabilidade.**
