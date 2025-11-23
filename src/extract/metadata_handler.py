"""
Gerenciador de metadados de cache para otimização de downloads do TSE

Este módulo implementa lógica de cache baseada em HTTP headers (ETag e Last-Modified)
para evitar downloads desnecessários quando os dados não foram atualizados no servidor.

Os metadados são armazenados em formato JSON com a seguinte estrutura:
{
    "cand_2022": {
        "ETag": "\"abc123\"",
        "Last-Modified": "Wed, 21 Oct 2020 07:28:00 GMT",
        "file_path": "portal-tse/data/raw/candidatos/2022/consulta_cand_2022_BRASIL_20251123.csv"
    }
}
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def load_metadata(metadata_path: Path) -> Dict:
    """
    Carrega metadados de cache do arquivo JSON.
    
    Args:
        metadata_path (Path): Caminho para o arquivo JSON de metadados
    
    Returns:
        Dict: Dicionário com metadados de cache. Retorna dict vazio se arquivo não existir.
    """
    if not metadata_path.exists():
        logger.debug(f"Arquivo de metadados não encontrado: {metadata_path}")
        return {}
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"Metadados carregados: {len(data)} entradas")
            return data
    except json.JSONDecodeError as e:
        logger.warning(f"Erro ao decodificar JSON de metadados: {e}. Retornando dict vazio.")
        return {}
    except Exception as e:
        logger.error(f"Erro ao carregar metadados: {e}")
        return {}


def save_metadata(metadata_path: Path, data: Dict) -> None:
    """
    Salva metadados de cache no arquivo JSON de forma segura.
    
    Args:
        metadata_path (Path): Caminho para o arquivo JSON de metadados
        data (Dict): Dicionário com metadados a serem salvos
    """
    try:
        # Criar diretório pai se não existir
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Salvar com formatação legível
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Metadados salvos com sucesso: {metadata_path}")
    except Exception as e:
        logger.error(f"Erro ao salvar metadados: {e}")
        raise


def check_if_download_needed(
    metadata_path: Path,
    tipo_consulta: str,
    ano: int,
    current_headers: Dict
) -> bool:
    """
    Verifica se o download é necessário comparando headers HTTP com metadados salvos.
    
    A verificação segue esta lógica:
    1. Compara ETag (se disponível) - método mais confiável
    2. Fallback para Last-Modified se ETag não estiver presente
    3. Se nenhum header coincidir ou não houver metadados salvos, download é necessário
    
    Args:
        metadata_path (Path): Caminho para o arquivo JSON de metadados
        tipo_consulta (str): Tipo de consulta ('cand', 'bens', etc.)
        ano (int): Ano dos dados
        current_headers (Dict): Headers HTTP da requisição HEAD atual
    
    Returns:
        bool: True se download é necessário, False se cache está atualizado
    """
    # Gerar chave de cache
    cache_key = f"{tipo_consulta}_{ano}"
    
    # Carregar metadados salvos
    metadata = load_metadata(metadata_path)
    
    # Se não há metadados para esta chave, download é necessário
    if cache_key not in metadata:
        logger.info(f"Nenhum cache encontrado para {cache_key}. Download necessário.")
        return True
    
    saved_meta = metadata[cache_key]
    
    # Extrair headers atuais (case-insensitive)
    current_etag = current_headers.get('ETag') or current_headers.get('etag')
    current_last_modified = current_headers.get('Last-Modified') or current_headers.get('last-modified')
    
    # Verificação primária: ETag
    if current_etag and saved_meta.get('ETag'):
        if current_etag == saved_meta['ETag']:
            logger.info(f"Cache válido para {cache_key} (ETag match). Download não necessário.")
            return False
        else:
            logger.info(f"ETag diferente para {cache_key}. Download necessário.")
            return True
    
    # Fallback: Last-Modified
    if current_last_modified and saved_meta.get('Last-Modified'):
        if current_last_modified == saved_meta['Last-Modified']:
            logger.info(f"Cache válido para {cache_key} (Last-Modified match). Download não necessário.")
            return False
        else:
            logger.info(f"Last-Modified diferente para {cache_key}. Download necessário.")
            return True
    
    # Se nenhum header útil está disponível, assumir que download é necessário
    logger.info(f"Headers de cache não disponíveis para {cache_key}. Download necessário por segurança.")
    return True


def update_metadata_after_download(
    metadata_path: Path,
    tipo_consulta: str,
    ano: int,
    new_headers: Dict,
    file_path: Path = None,
    base_path: Path = None
) -> None:
    """
    Atualiza metadados de cache após download bem-sucedido.
    
    Args:
        metadata_path (Path): Caminho para o arquivo JSON de metadados
        tipo_consulta (str): Tipo de consulta ('cand', 'bens', etc.)
        ano (int): Ano dos dados
        new_headers (Dict): Headers HTTP da requisição que levou ao download
        file_path (Path, optional): Caminho completo do arquivo baixado
        base_path (Path, optional): Caminho base usado no download
    """
    # Gerar chave de cache
    cache_key = f"{tipo_consulta}_{ano}"
    
    # Carregar metadados existentes
    metadata = load_metadata(metadata_path)
    
    # Extrair headers relevantes (case-insensitive)
    etag = new_headers.get('ETag') or new_headers.get('etag')
    last_modified = new_headers.get('Last-Modified') or new_headers.get('last-modified')
    
    # Calcular caminho relativo ao base_path
    relative_path = None
    if file_path and base_path:
        try:
            file_path_obj = Path(file_path).resolve()
            base_path_obj = Path(base_path).resolve()
            
            # Calcular caminho relativo ao base_path
            relative_path_obj = file_path_obj.relative_to(base_path_obj)
            
            # Converter para string com barras Unix (/) para portabilidade
            relative_path = str(relative_path_obj).replace('\\', '/')
            
            logger.debug(f"Caminho relativo calculado: {relative_path}")
            
        except ValueError as e:
            # Se não conseguir calcular relativo (arquivo fora do base_path)
            logger.warning(f"Não foi possível calcular caminho relativo: {e}. Usando caminho absoluto.")
            relative_path = str(file_path)
        except Exception as e:
            logger.warning(f"Erro ao calcular caminho relativo: {e}")
            relative_path = str(file_path)
    elif file_path:
        # Se não tiver base_path, usar apenas o nome do arquivo
        relative_path = Path(file_path).name
    
    # Atualizar entrada
    metadata[cache_key] = {
        'ETag': etag,
        'Last-Modified': last_modified,
        'file_path': relative_path
    }
    
    # Salvar metadados atualizados
    save_metadata(metadata_path, metadata)
    
    logger.info(f"Metadados atualizados para {cache_key}")
