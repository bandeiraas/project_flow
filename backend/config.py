import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# Pega o caminho absoluto do diretório onde config.py está
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Classe de configuração centralizada para a aplicação.
    Lê as configurações das variáveis de ambiente, com valores padrão (fallbacks).
    """
    
    # Configuração do Banco de Dados
    # Se DATABASE_URL não estiver no .env, usa 'projectflow_default.db'
    DATABASE_URL = os.environ.get('DATABASE_URL', 'projectflow_default.db')
    
    # Configuração de Logging
    # Permite definir o nível de log via .env (ex: LOG_LEVEL=DEBUG)
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
  
  
  # --- NOVA CONFIGURAÇÃO PARA JWT ---
    # Esta chave é usada para assinar os tokens. Deve ser um segredo!
    # Em produção, use um valor longo e aleatório.
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super-secret-key-change-in-production')  
    
    
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    
