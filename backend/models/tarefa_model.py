from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

# Importa a Base e o Usuario, que não causam ciclo
from .usuario_model import Base, Usuario

# Usa TYPE_CHECKING para importar 'Projeto' apenas para análise de tipo,
# evitando o erro de importação circular em tempo de execução.
if TYPE_CHECKING:
    from .projeto_model import Projeto

class Tarefa(Base):
    __tablename__ = 'tarefas'
    
    # --- COLUNAS ---
    id_tarefa: Mapped[int] = mapped_column(primary_key=True)
    id_projeto: Mapped[int] = mapped_column(ForeignKey('projetos.id_projeto', ondelete="CASCADE"))
    
    nome_tarefa: Mapped[str]
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    data_inicio: Mapped[str]
    data_fim: Mapped[str]
    progresso: Mapped[int] = mapped_column(default=0)
    dependencias: Mapped[Optional[str]]
    
    id_responsavel_tarefa: Mapped[Optional[int]] = mapped_column(ForeignKey('usuarios.id_usuario'))
    
    # --- RELACIONAMENTOS ---
    responsavel: Mapped[Optional[Usuario]] = relationship(lazy='joined')
    # Usa a string 'Projeto' para a anotação de tipo para evitar o ciclo de importação
    projeto: Mapped["Projeto"] = relationship(back_populates="tarefas")

    def para_dicionario(self):
        """Converte a instância Tarefa em um dicionário para a API."""
        return {
            "id": str(self.id_tarefa),
            "name": self.nome_tarefa,
            "descricao": self.descricao,
            "start": self.data_inicio,
            "end": self.data_fim,
            "progress": self.progresso,
            "dependencies": self.dependencias,
            "responsavel": self.responsavel.para_dicionario() if self.responsavel else None,
            "id_projeto": self.id_projeto,
            "nome_projeto": self.projeto.nome_projeto if self.projeto else "Projeto não encontrado"
        }