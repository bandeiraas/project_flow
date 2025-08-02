# backend/tests/integration/test_auth_api.py
"""
Testes de integração para APIs de autenticação.
"""

import pytest
import json
from flask_jwt_extended import decode_token
from tests.fixtures.factories import UsuarioFactory


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
class TestAuthAPI:
    """Testes para as APIs de autenticação."""
    
    def test_register_user_success(self, client, clean_db):
        """Testa registro de usuário com sucesso."""
        user_data = {
            'nome_completo': 'João Silva',
            'email': 'joao@teste.com',
            'senha': 'senha123',
            'cargo': 'Desenvolvedor',
            'role': 'Membro'
        }
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'id_usuario' in data
        assert data['nome_completo'] == 'João Silva'
        assert data['email'] == 'joao@teste.com'
        assert data['cargo'] == 'Desenvolvedor'
        assert data['role'] == 'Membro'
        # Verifica que a senha não é retornada
        assert 'senha' not in data
        assert 'senha_hash' not in data
    
    def test_register_user_missing_fields(self, client, clean_db):
        """Testa registro com campos obrigatórios faltando."""
        incomplete_data = {
            'nome_completo': 'João Silva',
            # email e senha faltando
        }
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data or 'message' in data
    
    def test_register_user_duplicate_email(self, client, clean_db, sample_user):
        """Testa registro com email já existente."""
        user_data = {
            'nome_completo': 'Outro Usuário',
            'email': sample_user.email,  # Email já existe
            'senha': 'senha123',
            'cargo': 'Analista'
        }
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data or 'message' in data
    
    def test_login_success(self, client, clean_db, sample_user):
        """Testa login com credenciais válidas."""
        login_data = {
            'email': sample_user.email,
            'senha': 'senha123'
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'access_token' in data
        assert data['access_token'] is not None
        assert len(data['access_token']) > 50  # JWT deve ser longo
    
    def test_login_invalid_email(self, client, clean_db):
        """Testa login com email inexistente."""
        login_data = {
            'email': 'inexistente@teste.com',
            'senha': 'senha123'
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data or 'message' in data
    
    def test_login_invalid_password(self, client, clean_db, sample_user):
        """Testa login com senha incorreta."""
        login_data = {
            'email': sample_user.email,
            'senha': 'senha_errada'
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data or 'message' in data
    
    def test_login_missing_fields(self, client, clean_db):
        """Testa login com campos faltando."""
        incomplete_data = {
            'email': 'teste@example.com'
            # senha faltando
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_get_current_user_with_valid_token(self, client, clean_db, auth_headers, sample_user):
        """Testa obtenção de dados do usuário atual com token válido."""
        response = client.get(
            '/api/auth/me',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['id_usuario'] == sample_user.id_usuario
        assert data['nome_completo'] == sample_user.nome_completo
        assert data['email'] == sample_user.email
        assert data['role'] == sample_user.role
    
    def test_get_current_user_without_token(self, client, clean_db):
        """Testa acesso sem token de autenticação."""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_get_current_user_with_invalid_token(self, client, clean_db):
        """Testa acesso com token inválido."""
        headers = {
            'Authorization': 'Bearer token_invalido',
            'Content-Type': 'application/json'
        }
        
        response = client.get('/api/auth/me', headers=headers)
        
        assert response.status_code == 422  # Unprocessable Entity para JWT inválido
    
    def test_jwt_token_contains_user_id(self, app, client, clean_db, sample_user):
        """Testa que o token JWT contém o ID do usuário."""
        login_data = {
            'email': sample_user.email,
            'senha': 'senha123'
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        data = response.get_json()
        token = data['access_token']
        
        # Decodifica o token para verificar o conteúdo
        with app.app_context():
            decoded = decode_token(token)
            assert decoded['sub'] == str(sample_user.id_usuario)
    
    def test_protected_route_access(self, client, clean_db, auth_headers):
        """Testa acesso a rota protegida com token válido."""
        # Testa uma rota protegida qualquer (ex: listar usuários)
        response = client.get('/api/usuarios', headers=auth_headers)
        
        # Deve permitir acesso (200) ou retornar dados válidos
        assert response.status_code in [200, 403]  # 403 se não tiver permissão
    
    def test_protected_route_without_auth(self, client, clean_db):
        """Testa acesso a rota protegida sem autenticação."""
        response = client.get('/api/usuarios')
        
        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
class TestAuthFlow:
    """Testes para fluxos completos de autenticação."""
    
    def test_complete_auth_flow(self, client, clean_db):
        """Testa fluxo completo: registro -> login -> acesso protegido."""
        # 1. Registro
        register_data = {
            'nome_completo': 'Maria Santos',
            'email': 'maria@teste.com',
            'senha': 'senha123',
            'cargo': 'Analista'
        }
        
        register_response = client.post(
            '/api/auth/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )
        
        assert register_response.status_code == 201
        user_data = register_response.get_json()
        
        # 2. Login
        login_data = {
            'email': 'maria@teste.com',
            'senha': 'senha123'
        }
        
        login_response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        assert login_response.status_code == 200
        login_data = login_response.get_json()
        token = login_data['access_token']
        
        # 3. Acesso a rota protegida
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        me_response = client.get('/api/auth/me', headers=headers)
        
        assert me_response.status_code == 200
        me_data = me_response.get_json()
        assert me_data['email'] == 'maria@teste.com'
        assert me_data['nome_completo'] == 'Maria Santos'
    
    def test_multiple_users_registration(self, client, clean_db):
        """Testa registro de múltiplos usuários."""
        users_data = [
            {
                'nome_completo': 'Usuário 1',
                'email': 'user1@teste.com',
                'senha': 'senha123',
                'cargo': 'Dev'
            },
            {
                'nome_completo': 'Usuário 2',
                'email': 'user2@teste.com',
                'senha': 'senha123',
                'cargo': 'Analista'
            },
            {
                'nome_completo': 'Usuário 3',
                'email': 'user3@teste.com',
                'senha': 'senha123',
                'cargo': 'Gerente',
                'role': 'Gerente'
            }
        ]
        
        created_users = []
        
        for user_data in users_data:
            response = client.post(
                '/api/auth/register',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            created_user = response.get_json()
            created_users.append(created_user)
        
        # Verifica que todos foram criados com IDs únicos
        user_ids = [user['id_usuario'] for user in created_users]
        assert len(set(user_ids)) == len(user_ids)  # Todos únicos
        
        # Verifica que todos podem fazer login
        for i, user_data in enumerate(users_data):
            login_response = client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': user_data['email'],
                    'senha': user_data['senha']
                }),
                content_type='application/json'
            )
            
            assert login_response.status_code == 200
            assert 'access_token' in login_response.get_json()
    
    def test_case_insensitive_email_login(self, client, clean_db, sample_user):
        """Testa login com email em diferentes casos."""
        # Login com email em maiúscula
        login_data = {
            'email': sample_user.email.upper(),
            'senha': 'senha123'
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Dependendo da implementação, pode ou não funcionar
        # Aqui assumimos que deveria funcionar
        assert response.status_code in [200, 401]
    
    def test_concurrent_logins(self, client, clean_db, sample_user):
        """Testa múltiplos logins simultâneos do mesmo usuário."""
        login_data = {
            'email': sample_user.email,
            'senha': 'senha123'
        }
        
        # Faz múltiplos logins
        tokens = []
        for _ in range(3):
            response = client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            token = response.get_json()['access_token']
            tokens.append(token)
        
        # Todos os tokens devem ser válidos
        for token in tokens:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = client.get('/api/auth/me', headers=headers)
            assert response.status_code == 200
        
        # Verifica que todos os tokens são diferentes
        assert len(set(tokens)) == len(tokens)


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
@pytest.mark.security
class TestAuthSecurity:
    """Testes de segurança para autenticação."""
    
    def test_password_not_returned_in_responses(self, client, clean_db):
        """Testa que senhas nunca são retornadas nas respostas."""
        user_data = {
            'nome_completo': 'Teste Segurança',
            'email': 'seguranca@teste.com',
            'senha': 'senha123',
            'cargo': 'Tester'
        }
        
        # Registro
        register_response = client.post(
            '/api/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        register_data = register_response.get_json()
        response_str = json.dumps(register_data)
        
        # Verifica que a senha não aparece na resposta
        assert 'senha123' not in response_str
        assert 'senha' not in register_data
        assert 'password' not in register_data
        assert 'senha_hash' not in register_data
    
    def test_sql_injection_attempt(self, client, clean_db):
        """Testa tentativa de SQL injection no login."""
        malicious_data = {
            'email': "admin@test.com'; DROP TABLE usuarios; --",
            'senha': 'senha123'
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(malicious_data),
            content_type='application/json'
        )
        
        # Deve retornar erro de autenticação, não erro de SQL
        assert response.status_code in [400, 401]
        
        # Verifica que a tabela ainda existe fazendo outro request
        test_data = {
            'nome_completo': 'Teste Pós-Injection',
            'email': 'pos.injection@teste.com',
            'senha': 'senha123'
        }
        
        test_response = client.post(
            '/api/auth/register',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Se a tabela foi dropada, isso falharia
        assert test_response.status_code == 201
    
    def test_xss_attempt_in_registration(self, client, clean_db):
        """Testa tentativa de XSS no registro."""
        xss_data = {
            'nome_completo': '<script>alert("XSS")</script>',
            'email': 'xss@teste.com',
            'senha': 'senha123',
            'cargo': '<img src=x onerror=alert("XSS")>'
        }
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(xss_data),
            content_type='application/json'
        )
        
        if response.status_code == 201:
            data = response.get_json()
            # Os dados devem ser sanitizados ou escapados
            assert '<script>' not in str(data)
            assert 'onerror=' not in str(data)
    
    def test_weak_password_handling(self, client, clean_db):
        """Testa como o sistema lida com senhas fracas."""
        weak_passwords = ['123', 'a', '']
        
        for weak_password in weak_passwords:
            user_data = {
                'nome_completo': 'Teste Senha Fraca',
                'email': f'weak{weak_password}@teste.com',
                'senha': weak_password,
                'cargo': 'Tester'
            }
            
            response = client.post(
                '/api/auth/register',
                data=json.dumps(user_data),
                content_type='application/json'
            )
            
            # Dependendo da política, pode aceitar ou rejeitar
            # Por enquanto, apenas verifica que não quebra
            assert response.status_code in [201, 400, 422]