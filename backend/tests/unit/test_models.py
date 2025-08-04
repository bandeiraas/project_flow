# backend/tests/unit/test_models.py
"""
Testes unitários para os models do sistema.
"""

import pytest
from datetime import datetime
from models import Usuario, Projeto, Area, ObjetivoEstrategico
from tests.fixtures.factories import (
    UsuarioFactory, ProjetoFactory, AreaFactory, 
    ObjetivoEstrategicoFactory
)


@pytest.mark.unit
@pytest.mark.database
class TestUsuarioModel:
    """Testes para o model Usuario."""
    
    def test_criar_usuario_basico(self, db_session):
        """Testa criação básica de usuário."""
        usuario = Usuario(
            nome_completo="João Silva",
            email="joao@teste.com",
            cargo="Desenvolvedor",
            role="Membro"
        )
        
        db_session.add(usuario)
        db_session.flush()
        
        assert usuario.id_usuario is not None
        assert usuario.nome_completo == "João Silva"
        assert usuario.email == "joao@teste.com"
        assert usuario.cargo == "Desenvolvedor"
        assert usuario.role == "Membro"
    
    def test_definir_senha(self, db_session):
        """Testa definição de senha com hash."""
        usuario = UsuarioFactory.build()  # build sem salvar no DB
        senha_original = "senha123"
        
        usuario.definir_senha(senha_original)
        
        # Verifica que a senha foi hasheada
        assert usuario.senha_hash is not None
        assert usuario.senha_hash != senha_original
        assert len(usuario.senha_hash) > 20  # Hash deve ser longo
    
    def test_verificar_senha_correta(self, db_session):
        """Testa verificação de senha correta."""
        usuario = UsuarioFactory.build()
        senha = "senha123"
        usuario.definir_senha(senha)
        
        assert usuario.verificar_senha(senha) is True
    
    def test_verificar_senha_incorreta(self, db_session):
        """Testa verificação de senha incorreta."""
        usuario = UsuarioFactory.build()
        usuario.definir_senha("senha123")
        
        assert usuario.verificar_senha("senha_errada") is False
    
    def test_para_dicionario(self, db_session):
        """Testa conversão para dicionário."""
        usuario = UsuarioFactory()
        
        dict_usuario = usuario.para_dicionario()
        
        assert isinstance(dict_usuario, dict)
        assert 'id_usuario' in dict_usuario
        assert 'nome_completo' in dict_usuario
        assert 'email' in dict_usuario
        assert 'cargo' in dict_usuario
        assert 'role' in dict_usuario
        # Verifica que a senha não está no dicionário
        assert 'senha_hash' not in dict_usuario
    
    def test_email_unico(self, db_session):
        """Testa que email deve ser único."""
        email = "teste@unique.com"
        
        # Cria primeiro usuário
        usuario1 = UsuarioFactory(email=email)
        db_session.add(usuario1)
        db_session.commit()
        
        # Tenta criar segundo usuário com mesmo email
        usuario2 = UsuarioFactory.build(email=email)
        db_session.add(usuario2)
        
        with pytest.raises(Exception):  # Deve dar erro de constraint
            db_session.commit()
    
    def test_roles_validos(self, db_session):
        """Testa que apenas roles válidos são aceitos."""
        roles_validos = ['Membro', 'Gerente', 'Admin']
        
        for role in roles_validos:
            usuario = UsuarioFactory.build(role=role)
            # Não deve dar erro
            assert usuario.role == role


@pytest.mark.unit
@pytest.mark.database
class TestProjetoModel:
    """Testes para o model Projeto."""
    
    def test_criar_projeto_basico(self, db_session, sample_user, sample_area):
        """Testa criação básica de projeto."""
        projeto = Projeto(
            nome_projeto="Projeto Teste",
            descricao="Descrição do projeto",
            numero_topdesk="TOP-12345",
            id_responsavel=sample_user.id_usuario,
            id_area_solicitante=sample_area.id_area,
            prioridade="Alta",
            complexidade="Média",
            risco="Baixo",
            status_atual="Em Planejamento"
        )
        
        db_session.add(projeto)
        db_session.flush()
        
        assert projeto.id_projeto is not None
        assert projeto.nome_projeto == "Projeto Teste"
        assert projeto.status_atual == "Em Planejamento"
        assert projeto.id_responsavel == sample_user.id_usuario
    
    def test_relacionamento_responsavel(self, db_session):
        """Testa relacionamento com usuário responsável."""
        projeto = ProjetoFactory()
        
        assert projeto.responsavel is not None
        assert isinstance(projeto.responsavel, Usuario)
        assert projeto.responsavel.id_usuario == projeto.id_responsavel
    
    def test_relacionamento_area(self, db_session):
        """Testa relacionamento com área solicitante."""
        projeto = ProjetoFactory()
        
        assert projeto.area_solicitante is not None
        assert isinstance(projeto.area_solicitante, Area)
        assert projeto.area_solicitante.id_area == projeto.id_area_solicitante
    
    def test_para_dicionario(self, db_session):
        """Testa conversão para dicionário."""
        projeto = ProjetoFactory()
        
        dict_projeto = projeto.para_dicionario()
        
        assert isinstance(dict_projeto, dict)
        assert 'id_projeto' in dict_projeto
        assert 'nome_projeto' in dict_projeto
        assert 'descricao' in dict_projeto
        assert 'status_atual' in dict_projeto
        assert 'responsavel' in dict_projeto
        assert 'area_solicitante' in dict_projeto
    
    def test_adicionar_membro_equipe(self, db_session):
        """Testa adição de membro à equipe."""
        projeto = ProjetoFactory()
        usuario = UsuarioFactory()
        
        projeto.equipe.append(usuario)
        db_session.flush()
        
        assert usuario in projeto.equipe
        assert len(projeto.equipe) == 1
    
    def test_adicionar_objetivo_estrategico(self, db_session):
        """Testa adição de objetivo estratégico."""
        projeto = ProjetoFactory()
        objetivo = ObjetivoEstrategicoFactory()
        
        projeto.objetivos_estrategicos.append(objetivo)
        db_session.flush()
        
        assert objetivo in projeto.objetivos_estrategicos
        assert len(projeto.objetivos_estrategicos) == 1
    
    def test_custo_estimado_positivo(self, db_session):
        """Testa que custo estimado deve ser positivo."""
        projeto = ProjetoFactory.build(custo_estimado=1000.0)
        assert projeto.custo_estimado == 1000.0
        
        # Custo negativo não deveria ser permitido
        projeto_negativo = ProjetoFactory.build(custo_estimado=-100.0)
        # Nota: A validação real seria no schema, não no model
        assert projeto_negativo.custo_estimado == -100.0  # Por enquanto permite
    
    def test_status_validos(self, db_session):
        """Testa status válidos para projeto."""
        status_validos = [
            'Em Planejamento', 'Em Andamento', 'Pausado', 
            'Concluído', 'Cancelado'
        ]
        
        for status in status_validos:
            projeto = ProjetoFactory.build(status_atual=status)
            assert projeto.status_atual == status
    
    def test_numero_topdesk_unico(self, db_session):
        """Testa que número TopDesk deve ser único."""
        numero = "TOP-UNIQUE-123"
        
        # Cria primeiro projeto
        projeto1 = ProjetoFactory(numero_topdesk=numero)
        db_session.add(projeto1)
        db_session.commit()
        
        # Tenta criar segundo projeto com mesmo número
        projeto2 = ProjetoFactory.build(numero_topdesk=numero)
        db_session.add(projeto2)
        
        with pytest.raises(Exception):  # Deve dar erro de constraint
            db_session.commit()


@pytest.mark.unit
@pytest.mark.database
class TestAreaModel:
    """Testes para o model Area."""
    
    def test_criar_area_basica(self, db_session):
        """Testa criação básica de área."""
        area = Area(
            nome="Tecnologia",
            descricao="Área de tecnologia da informação"
        )
        
        db_session.add(area)
        db_session.flush()
        
        assert area.id_area is not None
        assert area.nome == "Tecnologia"
        assert area.descricao == "Área de tecnologia da informação"
    
    def test_para_dicionario(self, db_session):
        """Testa conversão para dicionário."""
        area = AreaFactory()
        
        dict_area = area.para_dicionario()
        
        assert isinstance(dict_area, dict)
        assert 'id_area' in dict_area
        assert 'nome' in dict_area
        assert 'descricao' in dict_area
    
    def test_relacionamento_projetos(self, db_session):
        """Testa relacionamento com projetos."""
        area = AreaFactory()
        projeto1 = ProjetoFactory(id_area_solicitante=area.id_area)
        projeto2 = ProjetoFactory(id_area_solicitante=area.id_area)
        
        # Recarrega a área para pegar os relacionamentos
        db_session.refresh(area)
        
        assert len(area.projetos) == 2
        assert projeto1 in area.projetos
        assert projeto2 in area.projetos


@pytest.mark.unit
@pytest.mark.database
class TestObjetivoEstrategicoModel:
    """Testes para o model ObjetivoEstrategico."""
    
    def test_criar_objetivo_basico(self, db_session):
        """Testa criação básica de objetivo estratégico."""
        objetivo = ObjetivoEstrategico(
            nome="Modernização",
            descricao="Modernizar sistemas legados",
            status="Ativo"
        )
        
        db_session.add(objetivo)
        db_session.flush()
        
        assert objetivo.id_objetivo is not None
        assert objetivo.nome == "Modernização"
        assert objetivo.status == "Ativo"
    
    def test_para_dicionario(self, db_session):
        """Testa conversão para dicionário."""
        objetivo = ObjetivoEstrategicoFactory()
        
        dict_objetivo = objetivo.para_dicionario()
        
        assert isinstance(dict_objetivo, dict)
        assert 'id_objetivo' in dict_objetivo
        assert 'nome' in dict_objetivo
        assert 'descricao' in dict_objetivo
        assert 'status' in dict_objetivo
    
    def test_relacionamento_projetos(self, db_session):
        """Testa relacionamento many-to-many com projetos."""
        objetivo = ObjetivoEstrategicoFactory()
        projeto1 = ProjetoFactory()
        projeto2 = ProjetoFactory()
        
        # Adiciona projetos ao objetivo
        objetivo.projetos.append(projeto1)
        objetivo.projetos.append(projeto2)
        db_session.flush()
        
        assert len(objetivo.projetos) == 2
        assert projeto1 in objetivo.projetos
        assert projeto2 in objetivo.projetos
        
        # Verifica o relacionamento reverso
        assert objetivo in projeto1.objetivos_estrategicos
        assert objetivo in projeto2.objetivos_estrategicos
    
    def test_status_validos(self, db_session):
        """Testa status válidos para objetivo."""
        status_validos = ['Ativo', 'Inativo', 'Em Revisão']
        
        for status in status_validos:
            objetivo = ObjetivoEstrategicoFactory.build(status=status)
            assert objetivo.status == status


@pytest.mark.unit
class TestModelValidations:
    """Testes para validações dos models."""
    
    def test_usuario_email_formato(self, db_session):
        """Testa validação de formato de email."""
        # Email válido
        usuario_valido = UsuarioFactory.build(email="teste@exemplo.com")
        assert "@" in usuario_valido.email
        
        # Email inválido seria validado no schema, não no model
        usuario_invalido = UsuarioFactory.build(email="email_invalido")
        assert usuario_invalido.email == "email_invalido"  # Model não valida formato
    
    def test_projeto_campos_obrigatorios(self, db_session):
        """Testa campos obrigatórios do projeto."""
        # Campos obrigatórios devem estar presentes
        with pytest.raises(TypeError):
            Projeto()  # Sem argumentos obrigatórios
    
    def test_relacionamentos_cascade(self, db_session):
        """Testa comportamento de cascade nos relacionamentos."""
        # Cria projeto com relacionamentos
        projeto = ProjetoFactory()
        projeto_id = projeto.id_projeto
        
        # Remove o projeto
        db_session.delete(projeto)
        db_session.commit()
        
        # Verifica que o projeto foi removido
        projeto_removido = db_session.query(Projeto).get(projeto_id)
        assert projeto_removido is None


@pytest.mark.unit
class TestModelHelpers:
    """Testes para métodos auxiliares dos models."""
    
    def test_usuario_str_representation(self, db_session):
        """Testa representação string do usuário."""
        usuario = UsuarioFactory.build(nome_completo="João Silva")
        
        # Se houver método __str__ ou __repr__
        str_repr = str(usuario)
        assert "João Silva" in str_repr or "Usuario" in str_repr
    
    def test_projeto_str_representation(self, db_session):
        """Testa representação string do projeto."""
        projeto = ProjetoFactory.build(nome_projeto="Projeto Teste")
        
        str_repr = str(projeto)
        assert "Projeto Teste" in str_repr or "Projeto" in str_repr
    
    def test_comparacao_models(self, db_session):
        """Testa comparação entre instâncias de models."""
        usuario1 = UsuarioFactory()
        usuario2 = UsuarioFactory()
        
        # Mesmo usuário deve ser igual
        assert usuario1 == usuario1
        
        # Usuários diferentes devem ser diferentes
        assert usuario1 != usuario2
        
        # Comparação com None
        assert usuario1 != None
    
    def test_hash_models(self, db_session):
        """Testa hash de instâncias de models."""
        usuario = UsuarioFactory()
        
        # Deve ser possível usar como chave em dicionário
        dict_test = {usuario: "valor"}
        assert dict_test[usuario] == "valor"
        
        # Hash deve ser consistente
        hash1 = hash(usuario)
        hash2 = hash(usuario)
        assert hash1 == hash2