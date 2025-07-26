from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

# Importa a classe Base do nosso modelo principal de usuário
from .usuario_model import Base

class ObjetivoEstrategico(Base):
    __tablename__ = 'objetivos_estrategicos'
    
    id_objetivo: Mapped[int] = mapped_column(primary_key=True)
    nome_objetivo: Mapped[str] = mapped_column(unique=True)
    descricao: Mapped[Optional[str]]
    ano_fiscal: Mapped[int]
    status: Mapped[str] = mapped_column(default='Ativo') # Ex: Ativo, Concluído

    def para_dicionario(self):
        return {
            "id_objetivo": self.id_objetivo,
            "nome_objetivo": self.nome_objetivo,
            "descricao": self.descricao,
            "ano_fiscal": self.ano_fiscal,
            "status": self.status
        }