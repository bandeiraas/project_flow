import logging
from typing import Dict, List
from sqlalchemy.orm import joinedload

# Importa a instância 'db' e a BaseService para gerenciamento de sessão
from extensions import db
from .projeto_service import BaseService

# Importa os modelos necessários
from models.tarefa_model import Tarefa
from models.projeto_model import Projeto

logger = logging.getLogger(__name__)

class TarefaService(BaseService):
    """
    Encapsula toda a lógica de negócio para a entidade Tarefa.
    Herda de BaseService para obter o gerenciamento de sessão com 'with'.
    """

    def get_tarefas_por_projeto(self, id_projeto: int) -> List[Dict]:
        """Busca todas as tarefas de um projeto específico."""
        logger.info(f"Serviço: buscando tarefas para o projeto ID {id_projeto}")
        
        tarefas = self.session.query(Tarefa).filter_by(id_projeto=id_projeto).all()
        return [t.para_dicionario() for t in tarefas]

    def criar_tarefa(self, id_projeto: int, dados_tarefa: Dict) -> Dict:
        """Cria uma nova tarefa para um projeto."""
        logger.info(f"Serviço: criando nova tarefa para o projeto ID {id_projeto}")
        
        projeto = self.session.query(Projeto).get(id_projeto)
        if not projeto:
            raise ValueError(f"Projeto com ID {id_projeto} não encontrado.")

        nova_tarefa = Tarefa(id_projeto=id_projeto, **dados_tarefa)
        
        self.session.add(nova_tarefa)
        # O commit é feito automaticamente pelo __exit__ da BaseService
        
        return nova_tarefa.para_dicionario()

    def atualizar_tarefa(self, id_tarefa: int, dados_atualizacao: Dict) -> Dict:
        """Atualiza os dados de uma tarefa existente."""
        logger.info(f"Serviço: atualizando tarefa ID {id_tarefa}")
        
        tarefa = self.session.query(Tarefa).get(id_tarefa)
        if not tarefa:
            raise ValueError(f"Tarefa com ID {id_tarefa} não encontrada.")

        for key, value in dados_atualizacao.items():
            if hasattr(tarefa, key):
                setattr(tarefa, key, value)
        
        # O commit é feito automaticamente pelo __exit__ da BaseService
        return tarefa.para_dicionario()

    def deletar_tarefa(self, id_tarefa: int) -> bool:
        """Deleta uma tarefa existente."""
        logger.info(f"Serviço: deletando tarefa ID {id_tarefa}")
        
        tarefa = self.session.query(Tarefa).get(id_tarefa)
        if not tarefa:
            raise ValueError(f"Tarefa com ID {id_tarefa} não encontrada.")
        
        self.session.delete(tarefa)
        # O commit é feito automaticamente pelo __exit__
        
        return True
        
    def get_tarefas_por_usuario(self, id_usuario: int) -> List[Dict]:
        """
        Busca todas as tarefas abertas de um usuário, incluindo o nome do projeto.
        """
        logger.info(f"Serviço: buscando tarefas para o usuário ID {id_usuario}")
        
        # Envolve a consulta em parênteses para permitir quebras de linha limpas
        tarefas = (
            self.session.query(Tarefa)
            .options(joinedload(Tarefa.projeto)) # Carrega o projeto relacionado
            .filter(Tarefa.id_responsavel_tarefa == id_usuario)
            .filter(Tarefa.progresso < 100)
            .order_by(Tarefa.data_fim.asc())
            .all()
        )
            
        return [t.para_dicionario() for t in tarefas]