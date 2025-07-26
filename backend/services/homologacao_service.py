import logging
from typing import Dict, List
import datetime
import os
from sqlalchemy.orm import joinedload

from extensions import db
from models import Projeto, Homologacao, Usuario, TesteExecutado
from .projeto_service import BaseService
from parsers import parse_allure_zip

logger = logging.getLogger(__name__)


class HomologacaoService(BaseService):
    """
    Encapsula a lógica de negócio para os ciclos de homologação.
    """
    def iniciar_ciclo(self, id_projeto: int, dados_inicio: Dict) -> Dict:
        """Inicia um novo ciclo de homologação para um projeto."""
        logger.info(f"Serviço: iniciar_ciclo para projeto ID {id_projeto}")

        projeto = self.session.query(Projeto).get(id_projeto)
        if not projeto:
            raise ValueError(f"Projeto com ID {id_projeto} não encontrado.")

        projeto.mudar_status(
            novo_status="Em Homologação",
            id_usuario=dados_inicio['id_responsavel_teste'],
            observacao=f"Início do ciclo de homologação ({dados_inicio['tipo_teste']}) da versão {dados_inicio['versao_testada']}."
        )

        novo_ciclo = Homologacao(
            id_projeto=id_projeto,
            data_inicio=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            **dados_inicio
        )
        self.session.add(novo_ciclo)

        return projeto.para_dicionario()

    def finalizar_ciclo(self, id_projeto: int, dados_fim: Dict) -> Dict:
        """Finaliza o ciclo de homologação mais recente de um projeto."""
        logger.info(f"Serviço: finalizar_ciclo para projeto ID {id_projeto} com dados: {dados_fim}")

        projeto = self.session.query(Projeto).get(id_projeto)
        if not projeto or projeto.status_atual != "Em Homologação":
            raise ValueError("Projeto não encontrado ou não está em homologação.")

        ciclo_ativo = self.session.query(Homologacao)\
            .filter_by(id_projeto=id_projeto, data_fim=None)\
            .order_by(Homologacao.data_inicio.desc()).first()
        
        if not ciclo_ativo:
            raise ValueError("Nenhum ciclo de homologação ativo encontrado para este projeto.")

        resultado_final = dados_fim.get('resultado')
        if not resultado_final:
            raise ValueError("O campo 'resultado' é obrigatório para finalizar um ciclo.")

        ciclo_ativo.data_fim = datetime.datetime.now(datetime.timezone.utc).isoformat()
        ciclo_ativo.resultado = resultado_final
        ciclo_ativo.observacoes = dados_fim.get('observacoes')
        ciclo_ativo.link_relatorio_allure = dados_fim.get('link_relatorio_allure')
        ciclo_ativo.total_testes = dados_fim.get('total_testes')
        ciclo_ativo.testes_aprovados = dados_fim.get('testes_aprovados')
        ciclo_ativo.testes_reprovados = dados_fim.get('testes_reprovados')
        ciclo_ativo.testes_bloqueados = dados_fim.get('testes_bloqueados')

        if ciclo_ativo.total_testes and ciclo_ativo.total_testes > 0 and ciclo_ativo.testes_aprovados is not None:
            ciclo_ativo.taxa_sucesso = (ciclo_ativo.testes_aprovados / ciclo_ativo.total_testes) * 100
        else:
            ciclo_ativo.taxa_sucesso = None

        if resultado_final in ["Aprovado", "Aprovado com Ressalvas"]:
            proximo_status = "Pendente de Implantação"
        else:
            proximo_status = "Em Desenvolvimento"
        
        projeto.mudar_status(
            novo_status=proximo_status,
            id_usuario=dados_fim['id_usuario'],
            observacao=f"Fim do ciclo de homologação. Resultado: {resultado_final}."
        )
        
        return {
            "projeto": projeto.para_dicionario(),
            "id_homologacao_finalizado": ciclo_ativo.id_homologacao
        }
        
    # --- NOVO MÉTODO ADICIONADO ---
    def get_testes_por_ciclo(self, id_homologacao: int) -> List[Dict]:
        """Busca todos os testes executados de um ciclo de homologação específico."""
        logger.info(f"Serviço: buscando testes para o ciclo de homologação ID {id_homologacao}")
        
        testes = self.session.query(TesteExecutado)\
            .filter_by(id_homologacao=id_homologacao)\
            .order_by(TesteExecutado.status.asc(), TesteExecutado.nome_teste.asc())\
            .all()
            
        return [t.para_dicionario() for t in testes]

    # --- NOVO MÉTODO PARA O DASHBOARD DE QA ---
    def get_relatorio_qa_geral(self) -> Dict:
        """
        Busca e processa dados de todos os ciclos de homologação para o dashboard de QA.
        """
        logger.info("Serviço: gerando relatório geral de QA")
        
        # Busca todos os ciclos finalizados, carregando o projeto relacionado
        ciclos_finalizados = self.session.query(Homologacao)\
            .options(joinedload(Homologacao.projeto))\
            .filter(Homologacao.resultado.isnot(None))\
            .order_by(Homologacao.data_fim.asc())\
            .all()
            
        # 1. Dados para o Gráfico de Linha (Taxa de Sucesso Histórica)
        taxa_sucesso_data = {
            "labels": [datetime.datetime.fromisoformat(c.data_fim).strftime('%d/%m') for c in ciclos_finalizados if c.taxa_sucesso is not None],
            "data": [c.taxa_sucesso for c in ciclos_finalizados if c.taxa_sucesso is not None]
        }

        # 2. Dados para o Gráfico de Barras (Distribuição por Projeto)
        projetos_data = {}
        for ciclo in ciclos_finalizados:
            nome_projeto = ciclo.projeto.nome_projeto
            if nome_projeto not in projetos_data:
                projetos_data[nome_projeto] = {"aprovados": 0, "reprovados": 0, "bloqueados": 0}
            
            projetos_data[nome_projeto]["aprovados"] += ciclo.testes_aprovados or 0
            projetos_data[nome_projeto]["reprovados"] += ciclo.testes_reprovados or 0
            projetos_data[nome_projeto]["bloqueados"] += ciclo.testes_bloqueados or 0

        distribuicao_projetos_data = {
            "labels": list(projetos_data.keys()),
            "datasets": [
                {"label": "Aprovados", "data": [v['aprovados'] for v in projetos_data.values()]},
                {"label": "Reprovados", "data": [v['reprovados'] for v in projetos_data.values()]},
                {"label": "Bloqueados", "data": [v['bloqueados'] for v in projetos_data.values()]}
            ]
        }

        return {
            "taxa_sucesso_historica": taxa_sucesso_data,
            "distribuicao_por_projeto": distribuicao_projetos_data
        }    

    # --- NOVO MÉTODO ÚNICO E UNIFICADO ---
    def processar_upload_de_relatorio(self, id_homologacao: int, file_stream, upload_folder: str) -> Dict:
        """
        Salva o arquivo ZIP, o processa, extrai as métricas e os detalhes dos testes,
        e atualiza o registro do ciclo de homologação no banco de dados.
        """
        logger.info(f"Serviço: processando upload para homologação ID {id_homologacao}")
        
        ciclo = self.session.query(Homologacao).get(id_homologacao)
        if not ciclo:
            raise ValueError(f"Ciclo de homologação com ID {id_homologacao} não encontrado.")

        # 1. Organiza e salva o arquivo
        project_folder = os.path.join(upload_folder, str(ciclo.id_projeto))
        os.makedirs(project_folder, exist_ok=True)
        novo_filename = f"{id_homologacao}.zip"
        caminho_arquivo = os.path.join(project_folder, novo_filename)
        file_stream.save(caminho_arquivo)
        ciclo.caminho_relatorio_zip = caminho_arquivo
        logger.info(f"Arquivo salvo em: {caminho_arquivo}")

        # 2. Processa o arquivo salvo
        try:
            dados_allure = parse_allure_zip(caminho_arquivo)
            metricas = dados_allure['metricas']
            testes_detalhados = dados_allure['testes']

            # 3. Atualiza o ciclo com as métricas
            ciclo.total_testes = metricas.get('total_testes')
            ciclo.testes_aprovados = metricas.get('testes_aprovados')
            ciclo.testes_reprovados = metricas.get('testes_reprovados')
            ciclo.testes_bloqueados = metricas.get('testes_bloqueados')

            if ciclo.total_testes and ciclo.total_testes > 0 and ciclo.testes_aprovados is not None:
                ciclo.taxa_sucesso = (ciclo.testes_aprovados / ciclo.total_testes) * 100
            else:
                ciclo.taxa_sucesso = 0.0
            
            # 4. Atualiza os detalhes dos testes
            ciclo.testes_executados.clear()
            self.session.flush()
            for teste_data in testes_detalhados:
                novo_teste = TesteExecutado(**teste_data)
                ciclo.testes_executados.append(novo_teste)
            
            logger.info(f"{len(testes_detalhados)} testes processados para o ciclo {id_homologacao}.")
            return ciclo.para_dicionario()

        except ValueError as e:
            # Se o parser falhar, deleta o arquivo inválido
            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)
            ciclo.caminho_relatorio_zip = None
            raise e

    