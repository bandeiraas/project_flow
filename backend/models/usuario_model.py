from sqlalchemy import Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
import datetime
from .enums import UserRole

# --- PONTO ÚNICO DE DEFINIÇÃO DA BASE DECLARATIVA ---
# Todos os outros modelos importarão esta 'Base'.
class Base(DeclarativeBase):
    pass

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id_usuario: Mapped[int] = mapped_column(primary_key=True)
    nome_completo: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    cargo: Mapped[str]
    senha_hash: Mapped[str]    
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.MEMBRO)
    
    telefone: Mapped[Optional[str]]
    foto_perfil_url: Mapped[Optional[str]]
    data_criacao: Mapped[str] = mapped_column(default=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    ultimo_login: Mapped[Optional[str]]
    ativo: Mapped[bool] = mapped_column(default=True)

    def definir_senha(self, senha):
        """Gera um hash seguro para a senha fornecida."""
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return check_password_hash(self.senha_hash, senha)

    def para_dicionario(self):
        """Converte a instância em um dicionário para a API, omitindo a senha."""
        return {
            "id_usuario": self.id_usuario,
            "nome_completo": self.nome_completo,
            "email": self.email,
            "cargo": self.cargo,
            "role": self.role,
            "telefone": self.telefone,
            "foto_perfil_url": self.foto_perfil_url,
            "data_criacao": self.data_criacao,
            "ultimo_login": self.ultimo_login,
            "ativo": self.ativo
        }

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id_usuario}, nome='{self.nome_completo}')>"