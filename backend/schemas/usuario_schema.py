# backend/schemas/usuario_schema.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

class UserRoleUpdateSchema(BaseModel):
    """Schema para validar a atualização do papel de um usuário."""
    # Restringe o papel a apenas um dos valores válidos
    role: Literal["Admin", "Gerente", "Membro"]
    
class ProfileUpdateSchema(BaseModel):
    """Schema para validar os dados que um usuário pode editar em seu próprio perfil."""
    # Todos os campos são opcionais
    nome_completo: Optional[str] = Field(None, min_length=3, max_length=150)
    cargo: Optional[str] = Field(None, max_length=100)
    telefone: Optional[str] = Field(None, max_length=20)    