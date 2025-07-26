from pydantic import BaseModel, Field
from typing import Optional

class TarefaCreateSchema(BaseModel):
    nome_tarefa: str
    descricao: Optional[str] = None
    data_inicio: str # Espera "YYYY-MM-DD"
    data_fim: str    # Espera "YYYY-MM-DD"
    id_responsavel_tarefa: Optional[int] = None
    
class TarefaUpdateSchema(BaseModel):
    """Schema para validar os dados ao ATUALIZAR uma tarefa."""
    nome_tarefa: Optional[str] = None
    descricao: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    id_responsavel_tarefa: Optional[int] = None
    progresso: Optional[int] = Field(None, ge=0, le=100) # ge=greater or equal, le=less or equal
    dependencias: Optional[str] = None    