import requests
import zipfile
from datetime import datetime
from pathlib import Path
import tempfile
import logging

# Importar configurações
from config_ingest import CONSULTAS_CONFIG, TSE_BASE_URL

# Importar gerenciador de metadados de cache
from metadata_handler import (
    check_if_download_needed,
    update_metadata_after_download
)

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
    
    # Obter configurações da consulta (Qual base de dados será baixada e qual o caminho padrão do armazenamento)
    config = CONSULTAS_CONFIG[tipo_consulta]
    consulta_nome = config['consulta'] # Nome da consulta
    pasta_destino = config['pasta_destino'] # Caminho padrão do armazenamento
    
    # Definir caminho base de armazenamento do arquivo
    if base_path is None:
        # Caso não tenha um caminho personalizado informado - usa o caminho padrão de armazenamento portal-tse/data/raw/
        script_dir = Path(__file__).parent
        base_path = script_dir / '../../data/raw'
    else:
        # Caso tenha um caminho personalizado informado - usa o caminho informado
        base_path = Path(base_path)
        
        # Verificar se o diretório base existe
        if not base_path.exists():
            logger.info(f"Diretório base '{base_path}' não encontrado. Será criado automaticamente.")
    
    # Construir URL de download
    arquivo_zip = f"{consulta_nome}_{ano}.zip" # Cria o nome do arquivo zip, por exemplo: consulta_cand_2022.zip
    url = f"{TSE_BASE_URL}/{consulta_nome}/{arquivo_zip}" # Cria a URL de download
    
    # Definir caminho do arquivo de metadados de cache
        # IMPORTANTE - O arquivo metadata é essencial para verificação de necessidade do download. 
        # Caso o caminho informado não contenha o arquivo metadata, permitindo todos os primeiros downloads.
    metadata_file_path = base_path / 'tse_cache_metadata.json'
    
    # Constante de configuração para retry
    MAX_RETRIES = 3
    
    # Executar requisição HEAD com retry para verificar se download é necessário
    logger.info(f"Verificando cache para: {url}")
    head_success = False
    last_head_error = None
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug(f"Tentativa {attempt}/{MAX_RETRIES} de requisição HEAD")
            head_response = requests.head(url, timeout=30)
            head_response.raise_for_status()
            head_success = True
            logger.debug(f"Requisição HEAD bem-sucedida na tentativa {attempt}")
            break
            
        except requests.RequestException as e:
            last_head_error = e
            if attempt < MAX_RETRIES:
                logger.warning(f"Tentativa {attempt}/{MAX_RETRIES} falhou: {e}. Tentando novamente...")
            else:
                logger.error(f"Todas as {MAX_RETRIES} tentativas de HEAD request falharam.")
    
    # Se HEAD falhou após todas as tentativas, abortar
    if not head_success:
        logger.error(f"Não foi possível verificar cache. Última tentativa falhou com: {last_head_error}")
        raise requests.RequestException(
            f"Falha ao verificar cache após {MAX_RETRIES} tentativas. "
            f"Não é seguro prosseguir sem verificação de cache. Erro: {last_head_error}"
        )
    
    # Verificar se download é necessário (HEAD foi bem-sucedido)
    if not check_if_download_needed(
        metadata_file_path,
        tipo_consulta,
        ano,
        head_response.headers
    ):
        logger.info(f"Cache válido. Download pulado para {tipo_consulta}_{ano}")
        return None
    
    logger.info(f"Cache inválido ou inexistente. Prosseguindo com download.")
    
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
            
            # Atualizar metadados de cache após download bem-sucedido
            # IMPORTANTE: Usar headers da resposta GET (response.headers), não do HEAD
            # Isso garante que os metadados reflitam o arquivo realmente baixado
            try:
                update_metadata_after_download(
                    metadata_file_path,
                    tipo_consulta,
                    ano,
                    response.headers,  # Headers do GET bem-sucedido, não do HEAD
                    caminho_final,  # Caminho do arquivo salvo
                    base_path  # Caminho base para cálculo relativo
                )
            except Exception as e:
                logger.warning(f"Erro ao atualizar metadados de cache: {e}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo final: {e}")
            raise IOError(f"Não foi possível salvar o arquivo em {caminho_final}: {e}")
    
    return str(caminho_final)
