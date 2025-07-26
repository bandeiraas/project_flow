from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

# Importa a Base e o Usuario para o relacionamento
from .usuario_model import Base, Usuario

class Area(Base):
    __tablename__ = 'areas'
    
    id_area: Mapped[int] = mapped_column(primary_key=True)
    nome_area: Mapped[str] = mapped_column(unique=True)
    id_gestor: Mapped[int] = mapped_column(ForeignKey('usuarios.id_usuario'))
    
    # Relacionamento
    gestor: Mapped[Optional[Usuario]] = relationship(lazy='joined')

    def para_dicionario(self):
        """Converte a instância em um dicionário para a API."""
        return {
            "id_area": self.id_area,
            "nome_area": self.nome_area,
            "id_gestor": self.id_gestor,
            "gestor": self.gestor.para_dicionario() if self.gestor else None
        }

    def __repr__(self) -> str:
        return f"<Area(id={self.id_area}, nome='{self.nome_area}')>"