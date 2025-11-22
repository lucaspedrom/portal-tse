import os
import requests
import zipfile
from datetime import datetime
from pathlib import Path
import tempfile
import logging

# Importar configurações
from config_ingest import CONSULTAS_CONFIG, TSE_BASE_URL

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_tse_data(tipo_consulta: str, ano: int, base_path: str = None) -> str:
    """
    Baixa dados do portal TSE, extrai o arquivo BRASIL.csv e armazena localmente.
    
    Args:
        tipo_consulta (str): Tipo de consulta ('cand', 'cassacao', 'bens', 'vot_partido', 'vot_cand')
        ano (int): Ano dos dados desejados
        base_path (str, optional): Caminho base para armazenamento. Default: ../../data/raw
    
    Returns:
        str: Caminho completo do arquivo salvo
    
    Raises:
        ValueError: Se o tipo de consulta for inválido
        requests.RequestException: Se houver erro no download
        FileNotFoundError: Se o arquivo BRASIL.csv não for encontrado no ZIP
    """
    
    # Validação do tipo de consulta
    if tipo_consulta not in CONSULTAS_CONFIG:
        raise ValueError(
            f"Tipo de consulta inválido: '{tipo_consulta}'. "
            f"Opções válidas: {list(CONSULTAS_CONFIG.keys())}"
        )
    
    # Obter configurações da consulta
    config = CONSULTAS_CONFIG[tipo_consulta]
    consulta_nome = config['consulta']
    pasta_destino = config['pasta_destino']
    
    # Definir caminho base
    if base_path is None:
        script_dir = Path(__file__).parent
        base_path = script_dir / '../../data/raw'
    else:
        base_path = Path(base_path)
    
    # Construir URL de download
    arquivo_zip = f"{consulta_nome}_{ano}.zip"
    url = f"{TSE_BASE_URL}/{consulta_nome}/{arquivo_zip}"
    
    logger.info(f"Iniciando download de: {url}")
    
    # Criar diretório temporário para download
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_zip_path = Path(temp_dir) / arquivo_zip
        
        # Download do arquivo ZIP
        try:
            response = requests.get(url, timeout=300, stream=True)
            response.raise_for_status()
            
            # Salvar arquivo ZIP temporariamente
            with open(temp_zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Download concluído: {temp_zip_path}")
            
        except requests.RequestException as e:
            logger.error(f"Erro ao baixar arquivo ZIP: {e}")
            raise requests.RequestException(
                f"Não foi possível baixar o arquivo de {url}. Erro: {e}"
            )
        
        # Extrair arquivo BRASIL.csv do ZIP
        arquivo_brasil = f"{consulta_nome}_{ano}_BRASIL.csv"
        arquivo_encontrado = False
        
        try:
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                # Listar arquivos no ZIP
                arquivos_no_zip = zip_ref.namelist()
                
                # Procurar pelo arquivo BRASIL.csv
                for arquivo in arquivos_no_zip:
                    if arquivo.endswith('_BRASIL.csv') or arquivo == arquivo_brasil:
                        arquivo_encontrado = True
                        arquivo_brasil = arquivo
                        
                        # Extrair arquivo
                        zip_ref.extract(arquivo, temp_dir)
                        logger.info(f"Arquivo extraído: {arquivo}")
                        break
                
                if not arquivo_encontrado:
                    logger.error(f"Arquivos encontrados no ZIP: {arquivos_no_zip}")
                    raise FileNotFoundError(
                        f"Arquivo BRASIL.csv não encontrado no ZIP. "
                        f"Arquivos disponíveis: {arquivos_no_zip}"
                    )
        
        except zipfile.BadZipFile as e:
            logger.error(f"Erro ao extrair ZIP: arquivo corrompido")
            raise zipfile.BadZipFile(f"Arquivo ZIP corrompido: {e}")
        
        # Preparar caminho de destino com data de ingestão
        data_ingestao = datetime.now().strftime('%Y%m%d')
        nome_arquivo_final = f"{consulta_nome}_{ano}_BRASIL_{data_ingestao}.csv"
        
        destino_dir = base_path / pasta_destino / str(ano)
        destino_dir.mkdir(parents=True, exist_ok=True)
        
        caminho_final = (destino_dir / nome_arquivo_final).resolve()
        
        # Mover arquivo extraído para destino final
        arquivo_extraido = Path(temp_dir) / arquivo_brasil
        
        try:
            # Copiar arquivo para destino
            with open(arquivo_extraido, 'rb') as src, open(caminho_final, 'wb') as dst:
                dst.write(src.read())
            
            logger.info(f"Arquivo armazenado com sucesso em: {caminho_final}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo final: {e}")
            raise IOError(f"Não foi possível salvar o arquivo em {caminho_final}: {e}")
    
    return str(caminho_final)
