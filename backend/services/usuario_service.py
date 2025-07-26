# backend/services/usuario_service.py
import logging
from typing import Dict
from extensions import db
from models.usuario_model import Usuario

logger = logging.getLogger(__name__)

# Reutiliza a BaseService que já temos para o gerenciamento de sessão
from .projeto_service import BaseService

class UsuarioService(BaseService):
    """
    Encapsula a lógica de negócio para a entidade Usuario.
    """
    def atualizar_role_usuario(self, id_usuario: int, novo_role: str) -> Dict:
        """
        Atualiza o papel (role) de um usuário existente e retorna seus dados como um dicionário.
        """
        logger.info(f"Serviço: atualizando role do usuário ID {id_usuario} para '{novo_role}'")
        
        # O objeto 'usuario' está ligado à sessão gerenciada pela BaseService
        usuario = self.session.query(Usuario).get(id_usuario)
        if not usuario:
            raise ValueError(f"Usuário com ID {id_usuario} não encontrado.")
        
        usuario.role = novo_role
        
        # O commit é feito automaticamente pelo __exit__ da BaseService.
        # Após o commit, o objeto 'usuario' é expirado.
        
        # --- CORREÇÃO AQUI ---
        # Para evitar o DetachedInstanceError, convertemos para dicionário
        # ANTES que a sessão seja fechada pelo __exit__.
        usuario_dict = usuario.para_dicionario()
        
        return usuario_dict
        
    # Em services/usuario_service.py, dentro da classe UsuarioService

    def atualizar_perfil(self, id_usuario: int, dados_atualizacao: Dict) -> Dict:
        """Atualiza os dados do perfil de um usuário."""
        logger.info(f"Serviço: atualizando perfil do usuário ID {id_usuario}")
        
        usuario = self.session.query(Usuario).get(id_usuario)
        if not usuario:
            raise ValueError(f"Usuário com ID {id_usuario} não encontrado.")
        
        # Itera sobre os dados validados e atualiza o objeto
        for key, value in dados_atualizacao.items():
            if hasattr(usuario, key):
                setattr(usuario, key, value)
        
        # O commit é feito automaticamente pelo __exit__
        
        return usuario.para_dicionario()