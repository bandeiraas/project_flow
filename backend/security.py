import logging
from functools import wraps
from flask import abort
from flask_jwt_extended import get_jwt_identity

# Importa os modelos necessários para as verificações
from models.enums import UserRole
from models.usuario_model import Usuario
from models.projeto_model import Projeto

# Importa a instância 'db' para poder fazer consultas
from extensions import db

logger = logging.getLogger(__name__)

def get_usuario_atual() -> Usuario | None:
    """
    Busca o objeto completo do usuário logado no banco de dados.
    Lê o ID do usuário a partir do token JWT.
    Retorna o objeto Usuario ou None se não encontrado.
    """
    try:
        # get_jwt_identity() retorna o que salvamos no token (o ID do usuário como string)
        id_usuario_logado = int(get_jwt_identity())
    except (ValueError, TypeError):
        # Acontece se o token estiver ausente ou malformado
        return None

    session = db.get_session()
    try:
        # Busca o usuário no banco de dados pelo ID
        usuario = session.query(Usuario).get(id_usuario_logado)
        return usuario
    finally:
        session.close()

# --- PONTO ÚNICO DE VERDADE PARA AS REGRAS DE PERMISSÃO ---

# Em backend/security.py

# ... (função get_usuario_atual() continua a mesma) ...

# --- PONTO ÚNICO DE VERDADE PARA AS NOVAS REGRAS DE PERMISSÃO ---

class Permissions:
    """
    Centraliza todas as regras de autorização da aplicação.
    """
    
    @staticmethod
    def pode_criar_projeto(usuario: Usuario):
        """
        REGRA: Membros, Gerentes e ADMINS podem criar projetos.
        """
        if not usuario:
            return False
        # Se qualquer usuário logado pode criar, a regra é simples.
        return usuario.role in [UserRole.ADMIN, UserRole.GERENTE, UserRole.MEMBRO]

    @staticmethod
    def pode_ver_projeto(usuario: Usuario, projeto: Projeto):
        """
        REGRA: ADMINS e Gerentes podem ver qualquer projeto.
               Membros só podem ver os projetos dos quais são responsáveis.
        """
        if not usuario or not projeto:
            return False
        
        if usuario.role in [UserRole.ADMIN, UserRole.GERENTE]:
            return True
        
        # Se for Membro, verifica se ele é o responsável
        return usuario.id_usuario == projeto.id_responsavel

    @staticmethod
    def pode_editar_projeto(usuario: Usuario, projeto: Projeto):
        """
        REGRA: ADMINS e Gerentes podem editar qualquer projeto.
               Membros só podem editar os projetos dos quais são responsáveis.
        """
        if not usuario or not projeto:
            return False
        
        if usuario.role in [UserRole.ADMIN, UserRole.GERENTE]:
            return True
        
        return usuario.id_usuario == projeto.id_responsavel

    @staticmethod
    def pode_deletar_projeto(usuario: Usuario, projeto: Projeto):
        """
        REGRA: ADMINS e Gerentes podem deletar qualquer projeto.
               Membros só podem deletar os projetos dos quais são responsáveis.
        """
        if not usuario or not projeto:
            return False
        
        if usuario.role in [UserRole.ADMIN, UserRole.GERENTE]:
            return True
        
        return usuario.id_usuario == projeto.id_responsavel

    @staticmethod
    def pode_mudar_status(usuario: Usuario, projeto: Projeto):
        """
        REGRA: Admins e Gerentes podem mudar o status de qualquer projeto.
               Membros só podem mudar o status dos projetos dos quais são responsáveis.
        """
        # A lógica é idêntica à de edição, então podemos reutilizá-la.
        return Permissions.pode_editar_projeto(usuario, projeto)

    # --- NOVAS REGRAS PARA RELATÓRIOS E CONFIGURAÇÕES ---

    @staticmethod
    def pode_ver_relatorios_completos(usuario: Usuario):
        """
        REGRA: Apenas Admins e Gerentes podem ver os relatórios de todos os usuários.
        """
        if not usuario:
            return False
        return usuario.role in [UserRole.ADMIN, UserRole.GERENTE]

    @staticmethod
    def pode_editar_roles(usuario: Usuario):
        """
        REGRA: Apenas Admins podem editar os papéis de outros usuários.
        """
        if not usuario:
            return False
        return usuario.role == UserRole.ADMIN