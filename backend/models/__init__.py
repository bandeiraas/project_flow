# backend/models/__init__.py

# Importa a Base de um dos modelos para ser o ponto central
from .usuario_model import Base

# Importa TODAS as suas classes de modelo para registrá-las
from .usuario_model import Usuario
from .area_model import Area
from .projeto_model import Projeto, StatusLog
from .homologacao_model import Homologacao
from .tarefa_model import Tarefa
from .objetivo_model import ObjetivoEstrategico
from .enums import ProjectStatus

# --- ADICIONE ESTAS IMPORTAÇÕES ---
# Importa as tabelas de associação para que fiquem disponíveis no pacote 'models'
from .projeto_model import projeto_equipe_association, projeto_objetivo_association
from .teste_executado_model import TesteExecutado