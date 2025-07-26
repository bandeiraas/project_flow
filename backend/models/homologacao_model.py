from sqlalchemy import ForeignKey, Text, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING


# Importa a Base e o Usuario para o relacionamento
from .usuario_model import Base, Usuario
from .teste_executado_model import TesteExecutado

# Usa TYPE_CHECKING para evitar importação circular
if TYPE_CHECKING:
    from .projeto_model import Projeto

class Homologacao(Base):
    __tablename__ = 'homologacoes'
    
    id_homologacao: Mapped[int] = mapped_column(primary_key=True)
    id_projeto: Mapped[int] = mapped_column(ForeignKey('projetos.id_projeto', ondelete="CASCADE"))
    
    data_inicio: Mapped[str]
    data_fim: Mapped[Optional[str]]
    id_responsavel_teste: Mapped[int] = mapped_column(ForeignKey('usuarios.id_usuario'))
    resultado: Mapped[Optional[str]] # Ex: "Aprovado", "Reprovado"
    ambiente: Mapped[str]
    versao_testada: Mapped[str]
    observacoes: Mapped[Optional[str]] = mapped_column(Text)
    
    # --- NOVO CAMPO PARA O CAMINHO DO ARQUIVO ---
    caminho_relatorio_zip: Mapped[Optional[str]]
    
    # --- NOVOS CAMPOS PARA MÉTRICAS DE TESTE ---
    tipo_teste: Mapped[str] = mapped_column(default='Manual') # Ex: Manual, Automatizado
    link_relatorio_allure: Mapped[Optional[str]]
    total_testes: Mapped[Optional[int]] = mapped_column(Integer)
    testes_aprovados: Mapped[Optional[int]] = mapped_column(Integer)
    testes_reprovados: Mapped[Optional[int]] = mapped_column(Integer)
    testes_bloqueados: Mapped[Optional[int]] = mapped_column(Integer)
    taxa_sucesso: Mapped[Optional[float]] = mapped_column(Float)
    
    # Relacionamento
    responsavel_teste: Mapped[Optional[Usuario]] = relationship(lazy='joined')
    # --- NOVO RELACIONAMENTO COM TESTES EXECUTADOS ---
    testes_executados: Mapped[List[TesteExecutado]] = relationship(cascade="all, delete-orphan")
    projeto: Mapped["Projeto"] = relationship(back_populates="ciclos_homologacao")

    def para_dicionario(self):
        """Converte a instância em um dicionário para a API."""
        return {
            "id_homologacao": self.id_homologacao,
            "id_projeto": self.id_projeto,
            "data_inicio": self.data_inicio,
            "data_fim": self.data_fim,
            "id_responsavel_teste": self.id_responsavel_teste,
            "resultado": self.resultado,
            "ambiente": self.ambiente,
            "versao_testada": self.versao_testada,
            "observacoes": self.observacoes,
            "caminho_relatorio_zip": self.caminho_relatorio_zip,
            # Adiciona os novos campos à resposta da API
            "tipo_teste": self.tipo_teste,
            "link_relatorio_allure": self.link_relatorio_allure,
            "total_testes": self.total_testes,
            "testes_aprovados": self.testes_aprovados,
            "testes_reprovados": self.testes_reprovados,
            "testes_bloqueados": self.testes_bloqueados,
            "taxa_sucesso": self.taxa_sucesso,
            "responsavel_teste": self.responsavel_teste.para_dicionario() if self.responsavel_teste else None,
            # --- ADICIONA OS TESTES À RESPOSTA DA API ---
            "testes_executados": [t.para_dicionario() for t in self.testes_executados]
        }