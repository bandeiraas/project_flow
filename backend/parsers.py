# backend/parsers.py
import zipfile
import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

def _extrair_label(labels: List[Dict], nome_label: str) -> str | None:
    """Função helper para encontrar o valor de um label específico na lista."""
    for label in labels:
        if label.get('name') == nome_label:
            return label.get('value')
    return None

def parse_allure_zip(zip_file_path: str) -> Dict:
    """
    Analisa um arquivo .zip do Allure, extrai métricas agregadas e os detalhes
    de cada teste individual.
    """
    logger.info(f"Iniciando parsing detalhado do arquivo Allure: {zip_file_path}")
    
    metricas = {
        'total_testes': 0,
        'testes_aprovados': 0,
        'testes_reprovados': 0, # failed + broken
        'testes_bloqueados': 0  # skipped
    }
    testes_detalhados = []
    
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Encontra todos os arquivos de resultado
            arquivos_resultado = [f for f in zip_ref.namelist() if f.endswith('-result.json')]

            if not arquivos_resultado:
                raise ValueError("O arquivo ZIP não parece ser um relatório Allure válido (nenhum arquivo '-result.json' encontrado).")

            for filename in arquivos_resultado:
                metricas['total_testes'] += 1
                
                with zip_ref.open(filename) as json_file:
                    try:
                        data = json.load(json_file)
                        status = data.get('status', 'unknown').lower()
                        
                        # Contabiliza as métricas agregadas
                        if status == 'passed':
                            metricas['testes_aprovados'] += 1
                        elif status in ['failed', 'broken']:
                            metricas['testes_reprovados'] += 1
                        elif status == 'skipped':
                            metricas['testes_bloqueados'] += 1
                        
                        # Extrai os detalhes do teste individual
                        detalhes_teste = {
                            "uuid": data.get('uuid'),
                            "nome_teste": data.get('name'),
                            "status": status,
                            "mensagem_erro": data.get('statusDetails', {}).get('message'),
                            "feature": _extrair_label(data.get('labels', []), 'feature'),
                            "severity": _extrair_label(data.get('labels', []), 'severity')
                        }
                        testes_detalhados.append(detalhes_teste)
                            
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Não foi possível analisar o arquivo {filename} no ZIP: {e}")
                        continue
    
    except (FileNotFoundError, zipfile.BadZipFile) as e:
        logger.error(f"Erro ao abrir o arquivo ZIP: {e}")
        raise ValueError("Arquivo de relatório inválido ou não encontrado.")

    return {
        "metricas": metricas,
        "testes": testes_detalhados
    }