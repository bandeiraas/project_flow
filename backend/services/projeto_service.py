import logging
from typing import Dict, List
import datetime

from extensions import db
from models import Projeto, StatusLog, Usuario, ObjetivoEstrategico, ProjectStatus
from models.usuario_model import Usuario
from data_sources.sqlite_source import get_all_projetos, get_projeto_by_id
from sqlalchemy.orm import joinedload
from utils.database import get_db_session, with_db_session, DatabaseManager

logger = logging.getLogger(__name__)


class BaseService:
    """
    Classe base para serviços que gerencia o ciclo de vida da sessão do DB.
    Refatorada para usar o novo sistema de gestão de sessões.
    """

    def __init__(self):
        # Não abre sessão no __init__ mais, usa context managers
        self.session = None
        logger.debug(f"BaseService {self.__class__.__name__} inicializado")

    def __enter__(self):
        # Usa o DatabaseManager para gestão automática
        self.db_manager = DatabaseManager()
        self.db_manager.__enter__()
        self.session = self.db_manager.session
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'db_manager'):
            return self.db_manager.__exit__(exc_type, exc_val, exc_tb)
    
    def execute_with_session(self, func, *args, **kwargs):
        """
        Executa uma função com a sessão atual do serviço.
        Se não houver sessão ativa, cria uma temporária.
        """
        if self.session:
            return func(self.session, *args, **kwargs)
        else:
            with get_db_session() as session:
                return func(session, *args, **kwargs)


class ProjetoService(BaseService):
    """
    Encapsula toda a lógica de negócio para a entidade Projeto.
    Cada método gerencia seu próprio ciclo de vida de sessão para garantir
    a atomicidade e o estado correto dos dados.
    """
    # Em services/homologacao_service.py

    def get_relatorio_portfolio(self, usuario: Usuario) -> List[Dict]:
        """
        Gera os dados para o dashboard de portfólio, agrupando projetos por objetivo.
        Refatorado para usar o novo sistema de gestão de sessões.
        """
        def _generate_portfolio(session):
            logger.info(f"Serviço: get_relatorio_portfolio para o usuário ID {usuario.id_usuario}")
            
            objetivos = session.query(ObjetivoEstrategico).filter_by(status='Ativo').all()
            
            todos_projetos_visiveis = get_all_projetos(session)
            if usuario.role == 'Membro':
                todos_projetos_visiveis = [p for p in todos_projetos_visiveis if p.id_responsavel == usuario.id_usuario]

            portfolio_data = []
            for objetivo in objetivos:
                projetos_do_objetivo = [
                    p for p in todos_projetos_visiveis if objetivo in p.objetivos_estrategicos
                ]
                
                if not projetos_do_objetivo:
                    continue

                custo_total_estimado = sum(p.custo_estimado or 0 for p in projetos_do_objetivo)
                
                status_counts = {}
                for p in projetos_do_objetivo:
                    status_counts[p.status_atual] = status_counts.get(p.status_atual, 0) + 1

                objetivo_dict = objetivo.para_dicionario()
                objetivo_dict['projetos'] = [p.para_dicionario() for p in projetos_do_objetivo]
                objetivo_dict['total_projetos'] = len(projetos_do_objetivo)
                objetivo_dict['custo_total_estimado'] = custo_total_estimado
                
                # --- CORREÇÃO CRÍTICA AQUI ---
                # Monta a estrutura de dados no formato que o Chart.js espera
                objetivo_dict['grafico_status'] = {
                    'labels': list(status_counts.keys()),
                    'datasets': [{
                        'data': list(status_counts.values())
                    }]
                }
                
                portfolio_data.append(objetivo_dict)
                
            return portfolio_data
        
        return self.execute_with_session(_generate_portfolio)

    def get_all_for_user(self, usuario: Usuario) -> List[Dict]:
        """
        Busca todos os projetos, aplicando as regras de permissão.
        Este método utiliza a sessão gerenciada pelo contexto do serviço (with ProjetoService() as service:).
        """
        logger.info(f"Serviço: get_all_for_user para o usuário ID {usuario.id_usuario} ({usuario.role})")
        
        # Utiliza a sessão da instância do serviço, que é gerenciada pelo context manager
        todos_projetos = get_all_projetos(self.session)

        if usuario.role in ['Admin', 'Gerente']:
            projetos_visiveis = todos_projetos
        else:
            projetos_visiveis = [p for p in todos_projetos if p.id_responsavel == usuario.id_usuario]

        logger.info(f"Retornando {len(projetos_visiveis)} projetos visíveis para o usuário.")
        return [p.para_dicionario() for p in projetos_visiveis]

    def get_by_id(self, id_projeto: int) -> Dict | None:
        """Busca um projeto por ID."""
        logger.info(f"Serviço: get_by_id para o ID: {id_projeto}")
        session = db.get_session()
        try:
            projeto = get_projeto_by_id(session, id_projeto)
            return projeto.para_dicionario() if projeto else None
        finally:
            session.close()

    def criar_projeto(self, dados_projeto: Dict, usuario_logado: Usuario) -> Dict:
        """
        Cria um novo projeto completo, construindo o objeto de forma explícita e segura.
        """
        logger.info(f"Serviço: criar_projeto chamado por {usuario_logado.email}")
        session = db.get_session()
        try:
            # 1. Lógica de permissão (já correta)
            if usuario_logado.role == 'Membro':
                dados_projeto['id_responsavel'] = usuario_logado.id_usuario

            # 2. Extrai os dados para os relacionamentos
            ids_da_equipe = dados_projeto.get('equipe_ids', [])
            ids_dos_objetivos = dados_projeto.get('objetivo_ids', [])

            # 3. Cria a instância do Projeto passando APENAS os argumentos que o __init__ espera
            novo_projeto = Projeto(
                nome_projeto=dados_projeto.get('nome_projeto'),
                descricao=dados_projeto.get('descricao'),
                numero_topdesk=dados_projeto.get('numero_topdesk'),
                id_responsavel=dados_projeto.get('id_responsavel'),
                id_area_solicitante=dados_projeto.get('id_area_solicitante'),
                prioridade=dados_projeto.get('prioridade'),
                complexidade=dados_projeto.get('complexidade'),
                risco=dados_projeto.get('risco'),
                custo_estimado=float(dados_projeto.get('custo_estimado', 0.0) if dados_projeto.get('custo_estimado') is not None else 0.0),
                link_documentacao=dados_projeto.get('link_documentacao'),
                data_inicio_prevista=dados_projeto.get('data_inicio_prevista'),
                data_fim_prevista=dados_projeto.get('data_fim_prevista')
            )

            # 4. Associa os relacionamentos ao objeto já criado
            if ids_da_equipe:
                membros_da_equipe = session.query(Usuario).filter(Usuario.id_usuario.in_(ids_da_equipe)).all()
                novo_projeto.equipe = membros_da_equipe

            if ids_dos_objetivos:
                objetivos = session.query(ObjetivoEstrategico).filter(
                    ObjetivoEstrategico.id_objetivo.in_(ids_dos_objetivos)).all()
                novo_projeto.objetivos_estrategicos = objetivos

            # 5. Adiciona à sessão e faz o flush para obter o ID
            session.add(novo_projeto)
            session.flush()

            # 6. Cria o log inicial
            primeiro_log = StatusLog(
                id_projeto=novo_projeto.id_projeto,
                status="Em Definição",
                data=novo_projeto.data_criacao,
                id_usuario=usuario_logado.id_usuario,
                observacao="Projeto criado."
            )
            session.add(primeiro_log)

            # 7. Faz o commit da transação inteira
            session.commit()
            id_criado = novo_projeto.id_projeto

            # 8. Retorna o objeto completo e atualizado
            projeto_final = get_projeto_by_id(session, id_criado)
            return projeto_final.para_dicionario()

        except Exception as e:
            logger.error(f"Erro no serviço 'criar_projeto': {e}", exc_info=True)
            session.rollback()
            raise e
        finally:
            session.close()

    def atualizar_status(self, id_projeto: int, novo_status: str, id_usuario: int, observacao: str) -> Dict:
        """Atualiza o status de um projeto."""
        logger.info(f"Serviço: atualizar_status para o projeto ID {id_projeto}")
        session = db.get_session()
        try:
            projeto = get_projeto_by_id(session, id_projeto)
            if not projeto:
                raise ValueError(f"Projeto com ID {id_projeto} não encontrado.")

            # Converte a string novo_status para o enum ProjectStatus
            try:
                novo_status_enum = ProjectStatus(novo_status)
            except ValueError:
                raise ValueError(f"Status '{novo_status}' não é um status de projeto válido.")

            projeto.mudar_status(
                novo_status=novo_status_enum,
                id_usuario=id_usuario,
                observacao=observacao
            )

            session.commit()

            projeto_atualizado = get_projeto_by_id(session, id_projeto)
            return projeto_atualizado.para_dicionario()
        except Exception as e:
            logger.error(f"Erro no serviço 'atualizar_status': {e}", exc_info=True)
            session.rollback()
            raise e
        finally:
            session.close()

    def editar_projeto(self, id_projeto: int, dados_atualizacao: Dict) -> Dict:
        """Edita um projeto existente (este método usa o contexto da BaseService)."""
        logger.info(f"Serviço: editar_projeto para o projeto ID {id_projeto}")

        # Este método depende da sessão aberta pelo __init__ da BaseService
        projeto = get_projeto_by_id(self.session, id_projeto)
        if not projeto:
            raise ValueError(f"Projeto com ID {id_projeto} não encontrado.")

        # --- LÓGICA DE ATUALIZAÇÃO DE EQUIPE E OBJETIVOS ---
        if 'equipe_ids' in dados_atualizacao:
            ids_da_equipe = dados_atualizacao.pop('equipe_ids', [])
            membros_da_equipe = self.session.query(Usuario).filter(Usuario.id_usuario.in_(ids_da_equipe)).all()
            projeto.equipe = membros_da_equipe

        if 'objetivo_ids' in dados_atualizacao:
            ids_dos_objetivos = dados_atualizacao.pop('objetivo_ids', [])
            objetivos = self.session.query(ObjetivoEstrategico).filter(
                ObjetivoEstrategico.id_objetivo.in_(ids_dos_objetivos)).all()
            projeto.objetivos_estrategicos = objetivos

        # --- CONVERSÃO DE TIPO PARA CUSTO ---
        if 'custo_estimado' in dados_atualizacao and dados_atualizacao['custo_estimado'] is not None:
            try:
                dados_atualizacao['custo_estimado'] = float(dados_atualizacao['custo_estimado'])
            except (ValueError, TypeError):
                # Mantém o valor original ou define um padrão se a conversão falhar
                dados_atualizacao.pop('custo_estimado') 
                logger.warning(f"Não foi possível converter 'custo_estimado' para float. O campo não será atualizado.")


        # Atualiza os outros campos
        for key, value in dados_atualizacao.items():
            if hasattr(projeto, key):
                setattr(projeto, key, value)
        
        # O commit/rollback será feito pelo __exit__ da BaseService
        self.session.flush() # Garante que as mudanças sejam enviadas ao DB antes do commit
        self.session.refresh(projeto) # Atualiza o objeto com os dados da sessão
        return projeto.para_dicionario()


    def deletar_projeto(self, id_projeto: int) -> bool:
        """Deleta um projeto existente."""
        logger.info(f"Serviço 'deletar_projeto' chamado para o projeto ID {id_projeto}.")
        session = db.get_session()
        try:
            projeto = get_projeto_by_id(session, id_projeto)
            if not projeto:
                raise ValueError(f"Tentativa de deletar projeto inexistente com ID {id_projeto}.")

            session.delete(projeto)
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Erro no serviço 'deletar_projeto': {e}", exc_info=True)
            session.rollback()
            raise e
        finally:
            session.close()

    # --- NOVO MÉTODO PARA "MEUS PROJETOS" ---
    def get_projetos_por_responsavel(self, id_usuario: int) -> List[Dict]:
        """
        Busca todos os projetos ativos onde um usuário específico é o responsável.
        """
        logger.info(f"Serviço: buscando projetos onde o usuário ID {id_usuario} é responsável.")

        # Status que indicam que um projeto não está mais "ativo" (usando o Enum)
        status_finalizados = [ProjectStatus.POS_GMUD, ProjectStatus.PROJETO_CONCLUIDO, ProjectStatus.CANCELADO]
        
        # Filtra os projetos pelo ID do responsável e que não estejam em um status final
        projetos = self.session.query(Projeto)\
            .options(joinedload(Projeto.responsavel), joinedload(Projeto.area_solicitante))\
            .filter(Projeto.id_responsavel == id_usuario)\
            .filter(Projeto.status_atual.notin_(status_finalizados))\
            .order_by(Projeto.data_fim_prevista.asc())\
            .all()
            
        return [p.para_dicionario() for p in projetos]          
