from pydantic import BaseModel, Field
from typing import Optional, List

# ===================================================================
# 1. SCHEMA BASE
# ===================================================================
class ProjetoBaseSchema(BaseModel):
    """
    Contém todos os campos que podem ser enviados pelo cliente.
    Todos são definidos como opcionais aqui, servindo como base para os outros schemas.
    """
    nome_projeto: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = None
    numero_topdesk: Optional[str] = None
    id_responsavel: Optional[int] = None
    id_area_solicitante: Optional[int] = None
    prioridade: Optional[str] = None
    complexidade: Optional[str] = None
    risco: Optional[str] = None
    link_documentacao: Optional[str] = None
    data_inicio_prevista: Optional[str] = None
    data_fim_prevista: Optional[str] = None
    custo_estimado: Optional[float] = Field(None, ge=0)
    equipe_ids: Optional[List[int]] = Field(None, description="Lista de IDs dos usuários na equipe.")
    objetivo_ids: Optional[List[int]] = Field(None, description="Lista de IDs dos objetivos estratégicos.")

    # Configuração para Pydantic v1
    class Config:
        smart_union = True

# ===================================================================
# 2. SCHEMA DE CRIAÇÃO
# ===================================================================
class ProjetoCreateSchema(ProjetoBaseSchema):
    """
    Herda de ProjetoBaseSchema e torna os campos necessários obrigatórios.
    Isso é feito simplesmente re-declarando os campos sem 'Optional' e sem valor padrão.
    """
    nome_projeto: str
    descricao: str
    numero_topdesk: str
    id_responsavel: int
    id_area_solicitante: int
    prioridade: str
    complexidade: str
    risco: str

# ===================================================================
# 3. SCHEMA DE ATUALIZAÇÃO (EDIÇÃO)
# ===================================================================
class ProjetoUpdateSchema(BaseModel):
    """
    Schema para validar os dados ao ATUALIZAR um projeto.
    Todos os campos são opcionais, permitindo atualizações parciais.
    Pydantic ainda validará o tipo e as restrições (ex: min_length) se o campo for fornecido.
    """
    nome_projeto: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = None
    numero_topdesk: Optional[str] = None
    id_responsavel: Optional[int] = None
    id_area_solicitante: Optional[int] = None
    prioridade: Optional[str] = None
    complexidade: Optional[str] = None
    risco: Optional[str] = None
    link_documentacao: Optional[str] = None
    data_inicio_prevista: Optional[str] = None
    data_fim_prevista: Optional[str] = None
    custo_estimado: Optional[float] = Field(None, ge=0)
    equipe_ids: Optional[List[int]] = Field(None, description="Lista de IDs dos usuários na equipe.")
    objetivo_ids: Optional[List[int]] = Field(None, description="Lista de IDs dos objetivos estratégicos.")

# ===================================================================
# 4. SCHEMA DE ATUALIZAÇÃO DE STATUS (sem alterações)
# ===================================================================
class StatusUpdateSchema(BaseModel):
    """
    Schema específico para a rota de atualização de status.
    """
    status: str
    usuario: str = "Usuário Padrão"
    observacao: str = ""