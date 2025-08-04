# backend/tests/conftest.py
"""
Configurações globais e fixtures para todos os testes.
"""

import os
import pytest
import tempfile
from unittest.mock import patch

# Configurar ambiente de teste ANTES de importar o app
os.environ['FLASK_ENV'] = 'testing'

from app import create_app
from extensions import db
from models import Usuario, Projeto, Area, ObjetivoEstrategico
from utils.database import get_db_session
from flask_jwt_extended import create_access_token


@pytest.fixture(scope='session')
def app():
    """
    Fixture que cria uma instância da aplicação Flask para testes.
    Usa configuração de teste com banco em memória.
    """
    # Cria um arquivo temporário para o banco de teste
    db_fd, db_path = tempfile.mkstemp()
    
    # Configura variáveis de ambiente para teste
    test_config = {
        'TESTING': True,
        'DATABASE_URL': f'sqlite:///{db_path}',
        'JWT_SECRET_KEY': 'test-secret-key-super-safe-for-testing-only',
        'WTF_CSRF_ENABLED': False,
        'RATELIMIT_ENABLED': False
    }
    
    # Cria a aplicação com configuração de teste
    app = create_app('testing')
    
    # Sobrescreve configurações específicas
    for key, value in test_config.items():
        app.config[key] = value
    
    with app.app_context():
        # Cria todas as tabelas
        db.init_app(app)
        
        yield app
        
        # Cleanup
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture
def client(app):
    """
    Fixture que fornece um cliente de teste Flask.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Fixture que fornece um runner de comandos CLI.
    """
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """
    Fixture que fornece uma sessão de banco de dados para testes.
    Cada teste roda em uma transação que é revertida no final.
    """
    with get_db_session() as session:
        yield session
        # O rollback é automático pelo context manager


@pytest.fixture
def clean_db(app):
    """
    Fixture que garante um banco de dados limpo para cada teste.
    """
    with app.app_context():
        # Limpa todas as tabelas
        with get_db_session() as session:
            # Remove dados em ordem para evitar problemas de FK
            session.query(Projeto).delete()
            session.query(Usuario).delete()
            session.query(Area).delete()
            session.query(ObjetivoEstrategico).delete()
            session.commit()
        
        yield
        
        # Cleanup após o teste (opcional, pois cada teste limpa antes)


@pytest.fixture
def sample_user(db_session):
    """
    Fixture que cria um usuário de exemplo para testes.
    """
    user = Usuario(
        nome_completo="João Teste",
        email="joao@teste.com",
        cargo="Desenvolvedor",
        role="Membro"
    )
    user.definir_senha("senha123")
    
    db_session.add(user)
    db_session.flush()  # Para obter o ID
    
    return user


@pytest.fixture
def admin_user(db_session):
    """
    Fixture que cria um usuário administrador para testes.
    """
    admin = Usuario(
        nome_completo="Admin Teste",
        email="admin@teste.com",
        cargo="Administrador",
        role="Admin"
    )
    admin.definir_senha("admin123")
    
    db_session.add(admin)
    db_session.flush()
    
    return admin


@pytest.fixture
def sample_area(db_session):
    """
    Fixture que cria uma área de exemplo para testes.
    """
    area = Area(
        nome="TI",
        descricao="Tecnologia da Informação"
    )
    
    db_session.add(area)
    db_session.flush()
    
    return area


@pytest.fixture
def sample_objetivo(db_session):
    """
    Fixture que cria um objetivo estratégico de exemplo para testes.
    """
    objetivo = ObjetivoEstrategico(
        nome="Modernização Tecnológica",
        descricao="Modernizar a infraestrutura tecnológica da empresa",
        status="Ativo"
    )
    
    db_session.add(objetivo)
    db_session.flush()
    
    return objetivo


@pytest.fixture
def sample_projeto(db_session, sample_user, sample_area):
    """
    Fixture que cria um projeto de exemplo para testes.
    """
    projeto = Projeto(
        nome_projeto="Projeto Teste",
        descricao="Descrição do projeto de teste",
        numero_topdesk="TOP-12345",
        id_responsavel=sample_user.id_usuario,
        id_area_solicitante=sample_area.id_area,
        prioridade="Alta",
        complexidade="Média",
        risco="Baixo",
        status_atual="Em Planejamento",
        custo_estimado=10000.0
    )
    
    db_session.add(projeto)
    db_session.flush()
    
    return projeto


@pytest.fixture
def auth_headers(app, sample_user):
    """
    Fixture que fornece headers de autenticação para testes de API.
    """
    with app.app_context():
        access_token = create_access_token(identity=str(sample_user.id_usuario))
    
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def admin_auth_headers(app, admin_user):
    """
    Fixture que fornece headers de autenticação de admin para testes de API.
    """
    with app.app_context():
        access_token = create_access_token(identity=str(admin_user.id_usuario))
    
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def mock_file_upload():
    """
    Fixture que cria um mock de upload de arquivo para testes.
    """
    from io import BytesIO
    from werkzeug.datastructures import FileStorage
    
    file_content = b"Conteudo do arquivo de teste"
    file_obj = BytesIO(file_content)
    
    return FileStorage(
        stream=file_obj,
        filename="test_file.txt",
        content_type="text/plain"
    )


# Fixtures para dados em lote
@pytest.fixture
def multiple_users(db_session):
    """
    Fixture que cria múltiplos usuários para testes.
    """
    users = []
    
    for i in range(5):
        user = Usuario(
            nome_completo=f"Usuário {i+1}",
            email=f"user{i+1}@teste.com",
            cargo="Funcionário",
            role="Membro" if i < 3 else "Gerente"
        )
        user.definir_senha(f"senha{i+1}")
        db_session.add(user)
        users.append(user)
    
    db_session.flush()
    return users


@pytest.fixture
def multiple_projetos(db_session, multiple_users, sample_area):
    """
    Fixture que cria múltiplos projetos para testes.
    """
    projetos = []
    status_list = ["Em Planejamento", "Em Andamento", "Pausado", "Concluído"]
    
    for i in range(4):
        projeto = Projeto(
            nome_projeto=f"Projeto {i+1}",
            descricao=f"Descrição do projeto {i+1}",
            numero_topdesk=f"TOP-{12345+i}",
            id_responsavel=multiple_users[i % len(multiple_users)].id_usuario,
            id_area_solicitante=sample_area.id_area,
            prioridade=["Alta", "Média", "Baixa"][i % 3],
            complexidade=["Alta", "Média", "Baixa"][i % 3],
            risco=["Alto", "Médio", "Baixo"][i % 3],
            status_atual=status_list[i],
            custo_estimado=10000.0 * (i + 1)
        )
        db_session.add(projeto)
        projetos.append(projeto)
    
    db_session.flush()
    return projetos


# Utilitários para testes
def create_test_user(db_session, **kwargs):
    """
    Função utilitária para criar usuários personalizados em testes.
    """
    defaults = {
        'nome_completo': 'Usuário Teste',
        'email': 'teste@example.com',
        'cargo': 'Funcionário',
        'role': 'Membro'
    }
    defaults.update(kwargs)
    
    user = Usuario(**defaults)
    if 'senha' in kwargs:
        user.definir_senha(kwargs.pop('senha'))
    else:
        user.definir_senha('senha123')
    
    db_session.add(user)
    db_session.flush()
    
    return user


def create_test_projeto(db_session, **kwargs):
    """
    Função utilitária para criar projetos personalizados em testes.
    """
    defaults = {
        'nome_projeto': 'Projeto Teste',
        'descricao': 'Descrição teste',
        'numero_topdesk': 'TOP-TEST',
        'prioridade': 'Média',
        'complexidade': 'Média',
        'risco': 'Médio',
        'status_atual': 'Em Planejamento'
    }
    defaults.update(kwargs)
    
    projeto = Projeto(**defaults)
    db_session.add(projeto)
    db_session.flush()
    
    return projeto


# Marcadores de teste customizados
def pytest_configure(config):
    """
    Configuração customizada do pytest.
    """
    # Registra marcadores customizados
    config.addinivalue_line(
        "markers", "unit: marca um teste como teste unitário"
    )
    config.addinivalue_line(
        "markers", "integration: marca um teste como teste de integração"
    )
    config.addinivalue_line(
        "markers", "slow: marca um teste como lento"
    )
    config.addinivalue_line(
        "markers", "auth: testes relacionados à autenticação"
    )
    config.addinivalue_line(
        "markers", "database: testes que interagem com o banco de dados"
    )
    config.addinivalue_line(
        "markers", "api: testes de API/endpoints"
    )
    config.addinivalue_line(
        "markers", "security: testes de segurança"
    )