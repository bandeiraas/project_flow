from pydantic import BaseModel, Field
from typing import Optional, Literal

class HomologacaoStartSchema(BaseModel):
    """Schema para validar os dados para INICIAR um ciclo de homologação."""
    id_responsavel_teste: int = Field(..., gt=0)
    ambiente: str = Field(..., min_length=2)
    versao_testada: str = Field(..., min_length=1)
    # --- NOVO CAMPO ---
    tipo_teste: Literal["Manual", "Automatizado - API", "Automatizado - UI", "Performance"]

    class Config:
        smart_union = True

class HomologacaoEndSchema(BaseModel):
    """Schema para validar os dados para FINALIZAR um ciclo de homologação."""
    resultado: Literal["Aprovado", "Reprovado", "Aprovado com Ressalvas"]
    id_usuario: int = Field(..., gt=0) # Usuário que está finalizando
    observacoes: Optional[str] = ""
    
    # --- NOVOS CAMPOS ---
    link_relatorio_allure: Optional[str] = None
    total_testes: Optional[int] = Field(None, ge=0) # ge = greater or equal
    testes_aprovados: Optional[int] = Field(None, ge=0)
    testes_reprovados: Optional[int] = Field(None, ge=0)
    testes_bloqueados: Optional[int] = Field(None, ge=0)

    class Config:
        smart_union = True