from repositories.projeto_repository import ProjetoRepository
from models.projeto_model import Projeto

class InMemoryProjetoSource(ProjetoRepository):
    """
    Implementação do repositório de projetos usando um dicionário em memória.
    """
    def __init__(self):
        # O banco de dados agora vive dentro desta classe
        self._db_projetos = {}
        self._load_initial_data()

    def _load_initial_data(self):
        # Cria os dados de exemplo iniciais
        projeto1 = Projeto(
            id_projeto=1, nome_projeto="Dashboard Vendas Q3",
            descricao="Desenvolver novo dashboard de vendas...", responsavel="Ana Silva",
            area_solicitante="Vendas", numero_topdesk="TD-12345", prioridade="Alta"
        )
        projeto1.mudar_status("Aprovado", "Carlos Lima", "Escopo aprovado.")
        
        projeto2 = Projeto(
            id_projeto=2, nome_projeto="Migração Cloud AWS",
            descricao="Migração completa do servidor de banco de dados...", responsavel="Bruno Costa",
            area_solicitante="TI", numero_topdesk="TD-67890", prioridade="Crítica"
        )
        
        self._db_projetos = {1: projeto1, 2: projeto2}

    def get_by_id(self, id_projeto):
        return self._db_projetos.get(id_projeto)

    def get_all(self):
        return list(self._db_projetos.values())

    def save(self, projeto):
        # Se o projeto já tem um ID, é uma atualização. Se não, é uma criação.
        if not projeto.id_projeto:
            projeto.id_projeto = self.get_next_id()
        self._db_projetos[projeto.id_projeto] = projeto
        print(f"Projeto salvo na memória: {projeto}")
        return projeto

    def delete(self, id_projeto):
        if id_projeto in self._db_projetos:
            del self._db_projetos[id_projeto]
            return True
        return False

    def get_next_id(self):
        return max(self._db_projetos.keys()) + 1 if self._db_projetos else 1

# Apague o arquivo database.py original.