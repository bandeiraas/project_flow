import datetime
import logging
from typing import List, Optional, Dict, TYPE_CHECKING
from sqlalchemy import ForeignKey, Text, Table, Column, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

logger = logging.getLogger(__name__)

# Importa a Base e as classes que não causam ciclo
from .usuario_model import Base, Usuario
from .area_model import Area
from .enums import ProjectStatus
from .homologacao_model import Homologacao
from .objetivo_model import ObjetivoEstrategico

# Usa TYPE_CHECKING para importar 'Tarefa' apenas para análise de tipo,
# evitando o erro de importação circular em tempo de execução.
if TYPE_CHECKING:
    from .tarefa_model import Tarefa

# --- TABELAS DE ASSOCIAÇÃO ---
projeto_equipe_association = Table(
    'projeto_equipe', Base.metadata,
    Column('projeto_id', ForeignKey('projetos.id_projeto'), primary_key=True),
    Column('usuario_id', ForeignKey('usuarios.id_usuario'), primary_key=True)
)

projeto_objetivo_association = Table(
    'projeto_objetivo', Base.metadata,
    Column('projeto_id', ForeignKey('projetos.id_projeto'), primary_key=True),
    Column('objetivo_id', ForeignKey('objetivos_estrategicos.id_objetivo'), primary_key=True)
)

class StatusLog(Base):
    __tablename__ = 'status_logs'
    
    id_log: Mapped[int] = mapped_column(primary_key=True)
    id_projeto: Mapped[int] = mapped_column(ForeignKey('projetos.id_projeto', ondelete="CASCADE"))
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus))
    data: Mapped[str]
    id_usuario: Mapped[int] = mapped_column(ForeignKey('usuarios.id_usuario'))
    observacao: Mapped[str] = mapped_column(Text)
    
    # Relacionamentos
    usuario: Mapped[Optional[Usuario]] = relationship(lazy='joined')
    projeto: Mapped["Projeto"] = relationship(back_populates="historico_status")

    def para_dicionario(self):
        return {
            "id_log": self.id_log,
            "id_projeto": self.id_projeto,
            "status": self.status,
            "data": self.data,
            "id_usuario": self.id_usuario,
            "observacao": self.observacao,
            "usuario": self.usuario.para_dicionario() if self.usuario else None
        }

class Projeto(Base):
    __tablename__ = 'projetos'
    
    # --- COLUNAS ---
    id_projeto: Mapped[int] = mapped_column(primary_key=True)
    nome_projeto: Mapped[str]
    descricao: Mapped[str] = mapped_column(Text)
    numero_topdesk: Mapped[str]
    id_responsavel: Mapped[int] = mapped_column(ForeignKey('usuarios.id_usuario'))
    id_area_solicitante: Mapped[int] = mapped_column(ForeignKey('areas.id_area'))
    prioridade: Mapped[str]
    complexidade: Mapped[str]
    risco: Mapped[str]
    custo_estimado: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    custo_real: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    link_documentacao: Mapped[Optional[str]]
    data_inicio_prevista: Mapped[Optional[str]]
    data_fim_prevista: Mapped[Optional[str]]
    data_criacao: Mapped[str] = mapped_column(default=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    data_fim_real: Mapped[Optional[str]]
    status_atual: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.EM_DEFINICAO)
    
    # --- RELACIONAMENTOS ---
    responsavel: Mapped[Optional[Usuario]] = relationship(foreign_keys=[id_responsavel], lazy='joined')
    area_solicitante: Mapped[Optional[Area]] = relationship(lazy='joined')
    historico_status: Mapped[List[StatusLog]] = relationship(cascade="all, delete-orphan", back_populates="projeto")
    ciclos_homologacao: Mapped[List[Homologacao]] = relationship(cascade="all, delete-orphan")
    equipe: Mapped[List[Usuario]] = relationship(secondary=projeto_equipe_association, lazy="joined")
    objetivos_estrategicos: Mapped[List[ObjetivoEstrategico]] = relationship(secondary=projeto_objetivo_association, lazy="joined")
    tarefas: Mapped[List["Tarefa"]] = relationship(cascade="all, delete-orphan", back_populates="projeto")
    ciclos_homologacao: Mapped[List["Homologacao"]] = relationship(
        cascade="all, delete-orphan",
        back_populates="projeto")

    def get_proximos_status(self) -> List[ProjectStatus]:
        """
        Retorna uma lista de próximos status válidos com base no status atual.
        """
        WORKFLOW = list(ProjectStatus)
        
        # Se o projeto já está em um estado final, não há próximos status.
        if self.status_atual in [ProjectStatus.PROJETO_CONCLUIDO, ProjectStatus.CANCELADO]:
            return []
        
        try:
            # Encontra o índice do status atual na lista de fluxo de trabalho.
            indice_atual = WORKFLOW.index(self.status_atual)
            
            # O próximo status é o item seguinte na lista.
            proximos = [WORKFLOW[indice_atual + 1]]
            
            # Permite cancelar o projeto de qualquer etapa (exceto se já for o próximo passo).
            if ProjectStatus.CANCELADO not in proximos:
                proximos.append(ProjectStatus.CANCELADO)
                
            return proximos
        except ValueError:
            # Caso o status atual não seja encontrado na lista (não deve acontecer).
            return []

    def mudar_status(self, novo_status: ProjectStatus, id_usuario: int, observacao: str = ""):
        """
        Muda o status do projeto, validando a transição e adicionando um novo log ao histórico.
        """
        logger.debug(f"mudar_status recebido: tipo={type(novo_status)}, valor={novo_status}")
        if not isinstance(novo_status, ProjectStatus):
            raise ValueError(f"Status '{novo_status}' não é válido.")
        
        # Status que podem ser visitados mais de uma vez (ciclos de retrabalho).
        STATUS_CICLICOS = [ProjectStatus.EM_DESENVOLVIMENTO, ProjectStatus.EM_HOMOLOGACAO]

        # A verificação de status repetido só se aplica se o novo status NÃO for cíclico.
        if novo_status not in STATUS_CICLICOS:
            if any(h.status == novo_status for h in self.historico_status):
                raise ValueError(f"Projeto já passou pelo status '{novo_status}'.")
        # Atualiza o status principal do projeto.
        self.status_atual = novo_status
        
        # Cria um novo objeto de log para registrar esta mudança.
        novo_log = StatusLog(
            id_projeto=self.id_projeto,
            status=novo_status, 
            data=datetime.datetime.now(datetime.timezone.utc).isoformat(), 
            id_usuario=id_usuario, 
            observacao=observacao
        )
        # Adiciona o novo log à lista de histórico. O SQLAlchemy cuidará do salvamento.
        self.historico_status.append(novo_log)

        # Se o projeto for concluído, registra a data de fim real.
        if novo_status == ProjectStatus.PROJETO_CONCLUIDO:
            self.data_fim_real = novo_log.data

    def para_dicionario(self) -> Dict:
        return {
            "id_projeto": self.id_projeto,
            "nome_projeto": self.nome_projeto,
            "descricao": self.descricao,
            "numero_topdesk": self.numero_topdesk,
            "prioridade": self.prioridade,
            "complexidade": self.complexidade,
            "risco": self.risco,
            "custo_estimado": self.custo_estimado,
            "custo_real": self.custo_real,
            "link_documentacao": self.link_documentacao,
            "data_inicio_prevista": self.data_inicio_prevista,
            "data_fim_prevista": self.data_fim_prevista,
            "data_criacao": self.data_criacao,
            "data_fim_real": self.data_fim_real,
            "status_atual": self.status_atual,
            "responsavel": self.responsavel.para_dicionario() if self.responsavel else None,
            "area_solicitante": self.area_solicitante.para_dicionario() if self.area_solicitante else None,
            "historico_status": [log.para_dicionario() for log in self.historico_status],
            "ciclos_homologacao": [h.para_dicionario() for h in self.ciclos_homologacao],
            "equipe": [membro.para_dicionario() for membro in self.equipe],
            "objetivos_estrategicos": [obj.para_dicionario() for obj in self.objetivos_estrategicos],
            "tarefas": [t.para_dicionario() for t in self.tarefas],
            "proximos_status": self.get_proximos_status()
        }