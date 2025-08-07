import enum


class UserRole(str, enum.Enum):
    """Define os papéis (roles) de usuário permitidos no sistema."""
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    MEMBRO = "MEMBRO"


class ProjectStatus(str, enum.Enum):
    """Define os status de projeto permitidos no sistema."""
    EM_DEFINICAO = "Em Definição"
    EM_ESPECIFICACAO = "Em Especificação"
    ESPECIFICACAO_APROVADA = "Especificação Aprovada"
    EM_DESENVOLVIMENTO = "Em Desenvolvimento"
    EM_HOMOLOGACAO = "Em Homologação"
    PENDENTE_IMPLANTACAO = "Pendente de Implantação"
    POS_GMUD = "Pós GMUD"
    PROJETO_CONCLUIDO = "Projeto concluído"
    CANCELADO = "Cancelado"