"""
Script interativo para download de dados do TSE

Este script permite ao usuário escolher interativamente qual tipo de consulta
e ano deseja baixar do portal de dados abertos do TSE.

    Grupos de URLs e Armazenamento
    URL Padrão: https://cdn.tse.jus.br/estatistica/sead/odsele/{consulta}/{arquivo}

    Candidatos - cand:
        Consulta: consulta_cand
        Arquivo: consulta_cand_{ano}.zip
        Armazenamento: ../../data/raw/candidatos/{ano}/consulta_cand_{ano}_BRASIL_{data_ingestao}.csv

    Motivo Cassação - cassacao:
        Consulta: motivo_cassacao
        Arquivo: motivo_cassacao_{ano}.zip
        Armazenamento: ../../data/raw/candidatos/{ano}/motivo_cassacao_{ano}_BRASIL_{data_ingestao}.csv

    Bens de Candidatos - bens:
        Consulta: bem_candidato
        Arquivo: bem_candidato_{ano}.zip
        Armazenamento: ../../data/raw/candidatos/{ano}/bem_candidato_{ano}_BRASIL_{data_ingestao}.csv

    Votação Partido Município e Zona - vot_partido:
        Consulta: votacao_partido_munzona
        Arquivo: votacao_partido_munzona_{ano}.zip
        Armazenamento: ../../data/raw/votacao_partido_munzona/{ano}/votacao_partido_munzona_{ano}_BRASIL_{data_ingestao}.csv

    Votacao Nominal Município e Zona - vot_cand:
        Consulta: votacao_candidato_munzona
        Arquivo: votacao_candidato_munzona_{ano}.zip
        Armazenamento: ../../data/raw/votacao_candidato_munzona/{ano}/votacao_candidato_munzona_{ano}_BRASIL_{data_ingestao}.csv
"""

from download_data import download_tse_data
from config_ingest import CONSULTAS_CONFIG
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def exibir_opcoes():
    """Exibe as opções de consulta disponíveis"""
    print("\n" + "="*60)
    print("DOWNLOAD DE DADOS DO TSE - Portal de Dados Abertos")
    print("="*60)
    print("\nTipos de consulta disponíveis:\n")
    
    for idx, (chave, config) in enumerate(CONSULTAS_CONFIG.items(), 1):
        descricao = config.get('descricao', 'Sem descrição')
        print(f"  {idx}. [{chave}] - {descricao}")
    
    print("\n" + "="*60)


def obter_tipo_consulta():
    """Solicita ao usuário o tipo de consulta"""
    while True:
        tipo = input("\nDigite o tipo de consulta (ex: cand, bens, vot_partido): ").strip().lower()
        
        if tipo in CONSULTAS_CONFIG:
            return tipo
        else:
            print(f"❌ Tipo inválido! Opções válidas: {list(CONSULTAS_CONFIG.keys())}")


def obter_ano():
    """Solicita ao usuário o ano desejado"""
    while True:
        try:
            ano_input = input("\nDigite o ano eleitoral desejado (ex: 2022): ").strip()
            ano = int(ano_input)

            if 2010 <= ano <= 2024:  # Validação básica de ano
                return ano
            else:
                print("❌ Ano inválido! Digite um ano entre 2010 e 2024.")
        except ValueError:
            print("❌ Por favor, digite um número válido para o ano.")


def main():
    """Função principal do script interativo"""
    
    try:
        # Exibir opções disponíveis
        exibir_opcoes()
        
        # Obter tipo de consulta
        tipo_consulta = obter_tipo_consulta()
        
        # Obter ano
        ano = obter_ano()
        
        # Executar download
        print("\n🚀 Iniciando download...\n")
        caminho_salvo = download_tse_data(tipo_consulta, ano)
        
        # Sucesso
        print("\n" + "="*60)
        print("✅ DOWNLOAD CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print(f"Arquivo salvo em:\n{caminho_salvo}")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário (Ctrl+C).")
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERRO NO DOWNLOAD")
        print("="*60)
        print(f"Erro: {e}")
        print("="*60 + "\n")


if __name__ == "__main__":
    main()
