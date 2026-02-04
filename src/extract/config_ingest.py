"""
Configurações para download de dados do Portal TSE

Este arquivo centraliza as configurações de consultas disponíveis no portal
de dados abertos do TSE, incluindo os nomes das consultas e os caminhos de
armazenamento para cada tipo de dado.

URL Base: https://cdn.tse.jus.br/estatistica/sead/odsele/{consulta}/{arquivo}
"""

# Mapeamento de consultas para configurações
CONSULTAS_CONFIG = {
    'cand': {
        'consulta': 'consulta_cand',
        'pasta_destino': 'candidatos',
        'descricao': 'Dados de candidatos'
    },
    'cassacao': {
        'consulta': 'motivo_cassacao',
        'pasta_destino': 'cassacao_candidatos',
        'descricao': 'Motivos de cassação de candidatos'
    },
    'bens': {
        'consulta': 'bem_candidato',
        'pasta_destino': 'bens_candidatos',
        'descricao': 'Bens declarados por candidatos'
    },
    'vot_partido': {
        'consulta': 'votacao_partido_munzona',
        'pasta_destino': 'votacao_partido_munzona',
        'descricao': 'Votação por partido, município e zona'
    },
    'vot_cand': {
        'consulta': 'votacao_candidato_munzona',
        'pasta_destino': 'votacao_candidato_munzona',
        'descricao': 'Votação nominal por candidato, município e zona'
    },
    'comparecimento': {
        'consulta': 'perfil_comparecimento_abstencao',
        'pasta_destino': 'comparecimento_abstencao',
        'descricao': 'Comparecimento e Abstenção das eleições'
    }
}

# URL base do portal TSE
TSE_BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele"

# Caminho base padrão para armazenamento (relativo ao diretório do script)
DEFAULT_BASE_PATH = "../../data/raw"
