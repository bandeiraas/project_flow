import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload, subqueryload

# --- IMPORTAÇÃO CENTRALIZADA DE TODOS OS MODELOS ---
# Importamos a Base e todas as classes de modelo do nosso ponto de entrada.
from models import (
    Base, Usuario, Area, Projeto, StatusLog, 
    Homologacao, Tarefa, ObjetivoEstrategico
)

class Database:
    """
    Classe responsável por inicializar a conexão com o banco de dados,
    criar as tabelas e popular com dados iniciais (seeding).
    """
    def __init__(self, app=None):
        self.Session = None
        self.app = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Inicializa o banco de dados com a configuração do app Flask.
        """
        self.app = app
        db_file = self.app.config.get('DATABASE_URL', 'fallback_projectflow.db')
        self.app.logger.info(f"Inicializando banco de dados em: {db_file}")
        
        db_exists = os.path.exists(db_file)
        self.engine = create_engine(f'sqlite:///{db_file}')
        
        # --- LÓGICA SIMPLIFICADA ---
        # Base.metadata já conhece todas as tabelas e seus relacionamentos
        # definidos diretamente nas classes de modelo.
        Base.metadata.create_all(self.engine)
        
        self.Session = sessionmaker(bind=self.engine)
        
        if not db_exists:
            with self.app.app_context():
                 self._seed_data()

    def get_session(self):
        """Retorna uma nova sessão do banco de dados."""
        if not self.Session:
            raise RuntimeError("A fábrica de sessões não foi inicializada.")
        return self.Session()

    def _seed_data(self):
        """Popula o banco com dados iniciais se ele estiver vazio."""
        session = self.get_session()
        try:
            if session.query(Usuario).count() == 0:
                self.app.logger.info("Banco de dados vazio. Populando com dados iniciais...")
                
                # Cria Usuários com papéis
                user1 = Usuario(nome_completo="Ana Silva", email="ana.silva@email.com", cargo="Gerente de Projetos Sr.", role="Gerente")
                user1.definir_senha("senha123")
                user2 = Usuario(nome_completo="Bruno Costa", email="bruno.costa@email.com", cargo="Arquiteto de Soluções", role="Membro")
                user2.definir_senha("senha123")
                user3 = Usuario(nome_completo="Carlos Lima", email="carlos.lima@email.com", cargo="Diretor de TI", role="Admin")
                user3.definir_senha("senha123")
                session.add_all([user1, user2, user3])
                session.commit()

                # Cria Áreas
                area1 = Area(nome_area="Vendas", id_gestor=user3.id_usuario)
                area2 = Area(nome_area="TI", id_gestor=user3.id_usuario)
                area3 = Area(nome_area="Marketing", id_gestor=user1.id_usuario)
                session.add_all([area1, area2, area3])
                session.commit()

                # Cria Objetivos Estratégicos
                obj1 = ObjetivoEstrategico(nome_objetivo="Aumentar Retenção de Clientes Q4/2025", ano_fiscal=2025)
                obj2 = ObjetivoEstrategico(nome_objetivo="Reduzir Custos Operacionais em 5%", ano_fiscal=2025)
                session.add_all([obj1, obj2])
                session.commit()

                # Cria Projetos de Exemplo
                proj1 = Projeto(nome_projeto="Implementar Portal de Fidelidade", descricao="...", numero_topdesk="TD-PROJ-01", id_responsavel=1, id_area_solicitante=3, prioridade="Alta", complexidade="Alta", risco="Média", custo_estimado=150000.00)
                proj1.objetivos_estrategicos.append(obj1)
                proj1.equipe.append(user1)
                proj1.equipe.append(user2)
                
                proj2 = Projeto(nome_projeto="Otimização de Infraestrutura Cloud", descricao="...", numero_topdesk="TD-PROJ-02", id_responsavel=2, id_area_solicitante=2, prioridade="Média", complexidade="Alta", risco="Baixo", custo_estimado=80000.00)
                proj2.objetivos_estrategicos.append(obj2)
                proj2.equipe.append(user2)
                
                session.add_all([proj1, proj2])
                session.commit()
                self.app.logger.info("Dados iniciais de exemplo criados.")
        finally:
            session.close()

# --- FUNÇÕES DO REPOSITÓRIO ---

def get_projeto_by_id(session, id_projeto: int):
    """Busca um único projeto pelo ID, carregando todos os seus relacionamentos."""
    return session.query(Projeto).options(
        subqueryload(Projeto.historico_status).joinedload(StatusLog.usuario),
        subqueryload(Projeto.ciclos_homologacao).joinedload(Homologacao.responsavel_teste),
        subqueryload(Projeto.equipe),
        subqueryload(Projeto.objetivos_estrategicos),
        subqueryload(Projeto.tarefas)
    ).filter_by(id_projeto=id_projeto).first()

def get_all_projetos(session):
    """Busca todos os projetos, carregando os relacionamentos principais."""
    return session.query(Projeto).options(
        joinedload(Projeto.responsavel),
        joinedload(Projeto.area_solicitante),
        joinedload(Projeto.equipe)
    ).all()