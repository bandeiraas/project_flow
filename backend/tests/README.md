# 🧪 Testes do Backend ProjectFlow

Este diretório contém todos os testes automatizados do backend, organizados em uma estrutura clara e abrangente.

## 📁 Estrutura dos Testes

```
tests/
├── __init__.py                 # Configuração do pacote de testes
├── conftest.py                 # Fixtures globais e configurações do pytest
├── README.md                   # Esta documentação
├── fixtures/                   # Factories e fixtures reutilizáveis
│   ├── __init__.py
│   └── factories.py            # Factories com Factory Boy
├── unit/                       # Testes unitários
│   ├── __init__.py
│   ├── test_models.py          # Testes dos models
│   ├── test_services.py        # Testes dos services
│   ├── test_schemas.py         # Testes dos schemas
│   └── test_utils.py           # Testes das utilidades
└── integration/                # Testes de integração
    ├── __init__.py
    ├── test_auth_api.py         # Testes das APIs de autenticação
    ├── test_project_api.py      # Testes das APIs de projetos
    ├── test_user_api.py         # Testes das APIs de usuários
    └── test_database.py         # Testes de integração com banco
```

## 🏷️ Marcadores de Teste

Os testes são organizados usando marcadores pytest:

- `@pytest.mark.unit` - Testes unitários (componentes isolados)
- `@pytest.mark.integration` - Testes de integração (interação entre componentes)
- `@pytest.mark.api` - Testes de endpoints da API
- `@pytest.mark.auth` - Testes relacionados à autenticação
- `@pytest.mark.database` - Testes que interagem com banco de dados
- `@pytest.mark.security` - Testes de segurança
- `@pytest.mark.slow` - Testes que demoram mais para executar

## 🚀 Como Executar os Testes

### Pré-requisitos

```bash
# Instalar dependências de teste
pip install -r requirements.txt
```

### Execução Básica

```bash
# Todos os testes
python -m pytest

# Ou usando o script personalizado
python run_tests.py
```

### Execução por Categoria

```bash
# Apenas testes unitários
python run_tests.py --unit

# Apenas testes de integração
python run_tests.py --integration

# Apenas testes de autenticação
python run_tests.py --auth

# Apenas testes de API
python run_tests.py --api

# Apenas testes de segurança
python run_tests.py --security
```

### Execução com Relatórios

```bash
# Com cobertura de código
python run_tests.py --coverage

# Com relatório HTML de cobertura
python run_tests.py --html-report

# Com relatório XML (para CI/CD)
python run_tests.py --xml-report

# Modo verboso
python run_tests.py --verbose
```

### Execução Rápida

```bash
# Pula testes lentos
python run_tests.py --fast

# Execução em paralelo (requer pytest-xdist)
python run_tests.py --parallel
```

### Filtros Específicos

```bash
# Testes que correspondem a um padrão
python run_tests.py --pattern "test_login"

# Apenas um arquivo específico
python run_tests.py --file tests/unit/test_models.py

# Combinando filtros
python run_tests.py --unit --pattern "Usuario" --verbose
```

### Cenários Pré-definidos

```bash
# Testes de smoke (básicos, rápidos)
python run_tests.py smoke

# Testes de regressão (completos)
python run_tests.py regression

# Testes de segurança
python run_tests.py security

# Testes de performance
python run_tests.py performance
```

## 🏭 Factories e Fixtures

### Usando Factories

```python
from tests.fixtures.factories import UsuarioFactory, ProjetoFactory

# Criar um usuário de teste
usuario = UsuarioFactory()

# Criar com atributos específicos
admin = UsuarioFactory(role='Admin', email='admin@teste.com')

# Criar múltiplos objetos
usuarios = UsuarioFactory.create_batch(5)

# Criar sem salvar no banco (para testes unitários)
usuario_mock = UsuarioFactory.build()
```

### Usando Fixtures

```python
def test_exemplo(sample_user, sample_projeto, db_session):
    """Teste usando fixtures pré-definidas."""
    assert sample_user.id_usuario is not None
    assert sample_projeto.id_responsavel == sample_user.id_usuario
```

### Fixtures Disponíveis

- `app` - Instância da aplicação Flask
- `client` - Cliente de teste Flask
- `db_session` - Sessão do banco de dados
- `clean_db` - Banco de dados limpo
- `sample_user` - Usuário de exemplo
- `admin_user` - Usuário administrador
- `sample_area` - Área de exemplo
- `sample_projeto` - Projeto de exemplo
- `auth_headers` - Headers de autenticação
- `admin_auth_headers` - Headers de autenticação de admin
- `mock_file_upload` - Mock de upload de arquivo

## ✍️ Escrevendo Novos Testes

### Testes Unitários

```python
import pytest
from models import Usuario

@pytest.mark.unit
def test_usuario_creation():
    """Testa criação de usuário."""
    usuario = Usuario(
        nome_completo="João Silva",
        email="joao@teste.com",
        cargo="Dev"
    )
    
    assert usuario.nome_completo == "João Silva"
    assert usuario.email == "joao@teste.com"
```

### Testes de Integração

```python
import pytest
import json

@pytest.mark.integration
@pytest.mark.api
def test_create_user_api(client, clean_db):
    """Testa criação de usuário via API."""
    user_data = {
        'nome_completo': 'Maria Santos',
        'email': 'maria@teste.com',
        'senha': 'senha123'
    }
    
    response = client.post(
        '/api/auth/register',
        data=json.dumps(user_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    assert response.get_json()['email'] == 'maria@teste.com'
```

### Testes com Autenticação

```python
@pytest.mark.integration
@pytest.mark.auth
def test_protected_endpoint(client, auth_headers):
    """Testa endpoint protegido."""
    response = client.get('/api/projetos', headers=auth_headers)
    assert response.status_code == 200
```

### Testes de Banco de Dados

```python
@pytest.mark.unit
@pytest.mark.database
def test_user_relationship(db_session, sample_user, sample_projeto):
    """Testa relacionamento entre usuário e projeto."""
    assert sample_projeto.responsavel == sample_user
    assert sample_user.id_usuario == sample_projeto.id_responsavel
```

## 📊 Relatórios de Cobertura

### Visualizar Cobertura

```bash
# Gerar relatório HTML
python run_tests.py --html-report

# Abrir no navegador
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

### Metas de Cobertura

- **Mínimo aceitável**: 70%
- **Meta ideal**: 85%
- **Crítico**: 95% (para módulos de segurança)

### Arquivos Excluídos da Cobertura

- Arquivos de teste (`test_*.py`)
- Migrações de banco
- Arquivos de configuração
- Scripts de deploy

## 🔧 Configuração do Ambiente de Teste

### Variáveis de Ambiente

```bash
# Configuração automática pelo conftest.py
FLASK_ENV=testing
DATABASE_URL=sqlite:///:memory:
JWT_SECRET_KEY=test-secret-key
```

### Banco de Dados de Teste

- Usa SQLite em memória por padrão
- Cada teste roda em transação isolada
- Dados são limpos automaticamente

### Configurações Personalizadas

```python
# Em conftest.py, você pode personalizar:
@pytest.fixture(scope='session')
def app():
    test_config = {
        'TESTING': True,
        'DATABASE_URL': 'sqlite:///:memory:',
        # Suas configurações personalizadas
    }
    return create_app(test_config)
```

## 🚨 Boas Práticas

### Nomenclatura

- Arquivos: `test_*.py`
- Classes: `TestNomeDoComponente`
- Métodos: `test_descricao_do_que_testa`

### Estrutura de Teste

```python
def test_nome_descritivo(fixtures_necessarias):
    """
    Docstring explicando o que o teste faz.
    
    Given: Estado inicial
    When: Ação executada
    Then: Resultado esperado
    """
    # Arrange (preparação)
    dados = {'campo': 'valor'}
    
    # Act (ação)
    resultado = funcao_testada(dados)
    
    # Assert (verificação)
    assert resultado.status == 'esperado'
    assert 'campo_esperado' in resultado.data
```

### Isolamento

- Cada teste deve ser independente
- Use fixtures para setup/teardown
- Não dependa da ordem de execução

### Dados de Teste

- Use factories para dados realistas
- Não use dados hardcoded em produção
- Crie cenários edge case

### Performance

- Testes unitários devem ser rápidos (< 100ms)
- Use `@pytest.mark.slow` para testes demorados
- Mock dependências externas

## 🔄 Integração Contínua

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py --xml-report
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Hooks de Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: Run tests
        entry: python run_tests.py --fast
        language: system
        pass_filenames: false
```

## 🐛 Debugging de Testes

### Executar Teste Específico

```bash
# Um teste específico
python -m pytest tests/unit/test_models.py::TestUsuarioModel::test_criar_usuario_basico -v

# Com debugger
python -m pytest tests/unit/test_models.py::test_funcao --pdb
```

### Logs Durante Testes

```python
import logging

def test_com_logs(caplog):
    """Teste que captura logs."""
    with caplog.at_level(logging.INFO):
        funcao_que_loga()
    
    assert "Mensagem esperada" in caplog.text
```

### Fixtures de Debug

```python
@pytest.fixture
def debug_db(db_session):
    """Fixture que não limpa o banco para debug."""
    yield db_session
    # Não faz rollback para inspecionar dados
```

## 📚 Recursos Adicionais

### Documentação

- [Pytest Documentation](https://docs.pytest.org/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.0.x/testing/)

### Plugins Úteis

- `pytest-cov` - Cobertura de código
- `pytest-mock` - Mocking avançado
- `pytest-xdist` - Execução paralela
- `pytest-flask` - Helpers para Flask

### Comandos Úteis

```bash
# Listar todos os testes
python -m pytest --collect-only

# Executar testes que falharam na última execução
python -m pytest --lf

# Executar apenas novos testes
python -m pytest --nf

# Mostrar os 10 testes mais lentos
python -m pytest --durations=10
```

---

## 🤝 Contribuindo

1. Escreva testes para toda nova funcionalidade
2. Mantenha cobertura acima de 70%
3. Use factories para dados de teste
4. Documente casos edge
5. Execute todos os testes antes do commit

```bash
# Antes de fazer commit
python run_tests.py --coverage
```

Para dúvidas ou sugestões, abra uma issue ou discuta com a equipe! 🚀
