from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

# Importa a classe Base do nosso modelo principal de usuário
from .usuario_model import Base

@Base.registry.mapped
class TesteExecutado:
    __tablename__ = 'testes_executados'
  
  # Garante que a combinação de um ciclo e um teste seja única
    __table_args__ = (
        UniqueConstraint('id_homologacao', 'uuid', name='_homologacao_uuid_uc'),
    )
    
    id_execucao: Mapped[int] = mapped_column(primary_key=True)
    id_homologacao: Mapped[int] = mapped_column(ForeignKey('homologacoes.id_homologacao', ondelete="CASCADE"))
    
    uuid: Mapped[str]
    nome_teste: Mapped[str]
    status: Mapped[str] # ex: passed, failed, broken, skipped
    
    mensagem_erro: Mapped[Optional[str]] = mapped_column(Text)
    feature: Mapped[Optional[str]]
    severity: Mapped[Optional[str]]

    def para_dicionario(self):
        return {
            "id_execucao": self.id_execucao,
            "id_homologacao": self.id_homologacao,
            "uuid": self.uuid,
            "nome_teste": self.nome_teste,
            "status": self.status,
            "mensagem_erro": self.mensagem_erro,
            "feature": self.feature,
            "severity": self.severity
        }