# backend/tests/fixtures/factories.py
"""
Factories para criação de dados de teste usando factory_boy.
"""

import factory
from faker import Faker
from models import Usuario, Projeto, Area, ObjetivoEstrategico, Homologacao, Tarefa
from utils.database import get_db_session

fake = Faker('pt_BR')  # Usar locale brasileiro


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory base que configura a sessão do banco."""
    
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override para usar nosso sistema de sessões."""
        with get_db_session() as session:
            cls._meta.sqlalchemy_session = session
            instance = super()._create(model_class, *args, **kwargs)
            session.commit()
            return instance


class AreaFactory(BaseFactory):
    """Factory para criar áreas."""
    
    class Meta:
        model = Area
    
    nome = factory.LazyFunction(lambda: fake.company_suffix())
    descricao = factory.LazyFunction(lambda: fake.catch_phrase())


class ObjetivoEstrategicoFactory(BaseFactory):
    """Factory para criar objetivos estratégicos."""
    
    class Meta:
        model = ObjetivoEstrategico
    
    nome = factory.LazyFunction(lambda: fake.bs().title())
    descricao = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    status = factory.Iterator(['Ativo', 'Inativo', 'Em Revisão'])


class UsuarioFactory(BaseFactory):
    """Factory para criar usuários."""
    
    class Meta:
        model = Usuario
    
    nome_completo = factory.LazyFunction(lambda: fake.name())
    email = factory.LazyFunction(lambda: fake.unique.email())
    cargo = factory.Iterator([
        'Desenvolvedor', 'Analista', 'Gerente', 'Coordenador', 
        'Diretor', 'Estagiário', 'Consultor'
    ])
    role = factory.Iterator(['Membro', 'Gerente', 'Admin'], weights=[70, 25, 5])
    
    @factory.post_generation
    def senha(self, create, extracted, **kwargs):
        """Define uma senha padrão para o usuário."""
        if create:
            senha = extracted or 'senha123'
            self.definir_senha(senha)


class AdminUsuarioFactory(UsuarioFactory):
    """Factory para criar usuários administradores."""
    
    role = 'Admin'
    cargo = 'Administrador'


class GerenteUsuarioFactory(UsuarioFactory):
    """Factory para criar usuários gerentes."""
    
    role = 'Gerente'
    cargo = factory.Iterator(['Gerente', 'Coordenador', 'Diretor'])


class ProjetoFactory(BaseFactory):
    """Factory para criar projetos."""
    
    class Meta:
        model = Projeto
    
    nome_projeto = factory.LazyFunction(lambda: fake.catch_phrase())
    descricao = factory.LazyFunction(lambda: fake.text(max_nb_chars=500))
    numero_topdesk = factory.LazyFunction(lambda: f"TOP-{fake.random_int(10000, 99999)}")
    
    # Relacionamentos
    id_responsavel = factory.SubFactory(UsuarioFactory)
    id_area_solicitante = factory.SubFactory(AreaFactory)
    
    # Campos de configuração
    prioridade = factory.Iterator(['Alta', 'Média', 'Baixa'])
    complexidade = factory.Iterator(['Alta', 'Média', 'Baixa'])
    risco = factory.Iterator(['Alto', 'Médio', 'Baixo'])
    status_atual = factory.Iterator([
        'Em Planejamento', 'Em Andamento', 'Pausado', 
        'Concluído', 'Cancelado'
    ])
    
    # Datas
    data_inicio_prevista = factory.LazyFunction(lambda: fake.date_between(start_date='-30d', end_date='+30d').isoformat())
    data_fim_prevista = factory.LazyFunction(lambda: fake.date_between(start_date='+30d', end_date='+180d').isoformat())
    
    # Valores
    custo_estimado = factory.LazyFunction(lambda: fake.pyfloat(left_digits=5, right_digits=2, positive=True))
    
    # Links
    link_documentacao = factory.LazyFunction(lambda: fake.url())


class ProjetoEmAndamentoFactory(ProjetoFactory):
    """Factory para projetos em andamento."""
    
    status_atual = 'Em Andamento'
    data_inicio_prevista = factory.LazyFunction(lambda: fake.date_between(start_date='-60d', end_date='-1d').isoformat())


class ProjetoConcluidoFactory(ProjetoFactory):
    """Factory para projetos concluídos."""
    
    status_atual = 'Concluído'
    data_inicio_prevista = factory.LazyFunction(lambda: fake.date_between(start_date='-180d', end_date='-60d').isoformat())
    data_fim_prevista = factory.LazyFunction(lambda: fake.date_between(start_date='-60d', end_date='-1d').isoformat())


class TarefaFactory(BaseFactory):
    """Factory para criar tarefas."""
    
    class Meta:
        model = Tarefa
    
    titulo = factory.LazyFunction(lambda: fake.sentence(nb_words=4))
    descricao = factory.LazyFunction(lambda: fake.text(max_nb_chars=300))
    status = factory.Iterator(['Pendente', 'Em Andamento', 'Concluída', 'Cancelada'])
    prioridade = factory.Iterator(['Alta', 'Média', 'Baixa'])
    
    # Relacionamentos
    id_projeto = factory.SubFactory(ProjetoFactory)
    id_responsavel = factory.SubFactory(UsuarioFactory)
    
    # Datas
    data_criacao = factory.LazyFunction(lambda: fake.date_time_between(start_date='-30d', end_date='now').isoformat())
    data_vencimento = factory.LazyFunction(lambda: fake.date_between(start_date='now', end_date='+30d').isoformat())


class HomologacaoFactory(BaseFactory):
    """Factory para criar homologações."""
    
    class Meta:
        model = Homologacao
    
    nome_ciclo = factory.LazyFunction(lambda: f"Ciclo {fake.word().title()} - {fake.month_name()}")
    descricao = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    status = factory.Iterator(['Em Preparação', 'Em Execução', 'Finalizado'])
    
    # Relacionamentos
    id_projeto = factory.SubFactory(ProjetoFactory)
    id_responsavel = factory.SubFactory(UsuarioFactory)
    
    # Datas
    data_inicio = factory.LazyFunction(lambda: fake.date_between(start_date='-30d', end_date='now').isoformat())
    data_fim = factory.LazyFunction(lambda: fake.date_between(start_date='now', end_date='+30d').isoformat())


# Factories especializadas para cenários específicos
class ProjetoComEquipeFactory(ProjetoFactory):
    """Factory para projetos com equipe."""
    
    @factory.post_generation
    def equipe(self, create, extracted, **kwargs):
        """Adiciona membros à equipe do projeto."""
        if not create:
            return
        
        if extracted:
            # Se uma equipe específica foi passada
            for membro in extracted:
                self.equipe.append(membro)
        else:
            # Cria uma equipe aleatória de 2-5 membros
            num_membros = fake.random_int(min=2, max=5)
            membros = UsuarioFactory.create_batch(num_membros)
            for membro in membros:
                self.equipe.append(membro)


class ProjetoComObjetivosFactory(ProjetoFactory):
    """Factory para projetos com objetivos estratégicos."""
    
    @factory.post_generation
    def objetivos(self, create, extracted, **kwargs):
        """Adiciona objetivos estratégicos ao projeto."""
        if not create:
            return
        
        if extracted:
            # Se objetivos específicos foram passados
            for objetivo in extracted:
                self.objetivos_estrategicos.append(objetivo)
        else:
            # Cria 1-3 objetivos aleatórios
            num_objetivos = fake.random_int(min=1, max=3)
            objetivos = ObjetivoEstrategicoFactory.create_batch(num_objetivos)
            for objetivo in objetivos:
                self.objetivos_estrategicos.append(objetivo)


# Funções utilitárias para criar cenários complexos
def criar_cenario_empresa_pequena():
    """
    Cria um cenário de teste para uma empresa pequena.
    
    Returns:
        dict: Dicionário com os objetos criados
    """
    # Cria estrutura básica
    areas = AreaFactory.create_batch(3)  # TI, RH, Financeiro
    objetivos = ObjetivoEstrategicoFactory.create_batch(2)
    
    # Cria usuários
    admin = AdminUsuarioFactory()
    gerentes = GerenteUsuarioFactory.create_batch(2)
    membros = UsuarioFactory.create_batch(5)
    
    # Cria projetos
    projetos_ativos = ProjetoEmAndamentoFactory.create_batch(3)
    projetos_concluidos = ProjetoConcluidoFactory.create_batch(2)
    
    return {
        'areas': areas,
        'objetivos': objetivos,
        'admin': admin,
        'gerentes': gerentes,
        'membros': membros,
        'projetos_ativos': projetos_ativos,
        'projetos_concluidos': projetos_concluidos
    }


def criar_cenario_projeto_completo():
    """
    Cria um projeto completo com todos os relacionamentos.
    
    Returns:
        dict: Projeto e objetos relacionados
    """
    # Cria dependências
    area = AreaFactory()
    objetivo = ObjetivoEstrategicoFactory()
    responsavel = GerenteUsuarioFactory()
    equipe = UsuarioFactory.create_batch(3)
    
    # Cria projeto com relacionamentos
    projeto = ProjetoComEquipeFactory(
        id_responsavel=responsavel.id_usuario,
        id_area_solicitante=area.id_area,
        equipe=equipe
    )
    
    # Adiciona objetivo
    projeto.objetivos_estrategicos.append(objetivo)
    
    # Cria tarefas para o projeto
    tarefas = TarefaFactory.create_batch(5, id_projeto=projeto.id_projeto)
    
    # Cria homologação
    homologacao = HomologacaoFactory(
        id_projeto=projeto.id_projeto,
        id_responsavel=responsavel.id_usuario
    )
    
    return {
        'projeto': projeto,
        'area': area,
        'objetivo': objetivo,
        'responsavel': responsavel,
        'equipe': equipe,
        'tarefas': tarefas,
        'homologacao': homologacao
    }


# Traits para modificar comportamento das factories
class Trait:
    """Classe base para traits (modificadores de factory)."""
    pass


class ProjetoUrgenteTrait(Trait):
    """Trait para projetos urgentes."""
    prioridade = 'Alta'
    complexidade = 'Alta'
    status_atual = 'Em Andamento'


class ProjetoSimplesTrait(Trait):
    """Trait para projetos simples."""
    prioridade = 'Baixa'
    complexidade = 'Baixa'
    custo_estimado = factory.LazyFunction(lambda: fake.pyfloat(left_digits=3, right_digits=2, positive=True))


# Função para aplicar traits
def aplicar_trait(factory_class, trait_class, **kwargs):
    """
    Aplica um trait a uma factory.
    
    Args:
        factory_class: Classe da factory
        trait_class: Classe do trait
        **kwargs: Argumentos adicionais
        
    Returns:
        Instância criada com o trait aplicado
    """
    trait_attrs = {
        key: value for key, value in trait_class.__dict__.items()
        if not key.startswith('_')
    }
    
    return factory_class(**{**trait_attrs, **kwargs})