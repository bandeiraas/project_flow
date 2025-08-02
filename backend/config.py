import os
import secrets
from dotenv import load_dotenv

# Pega o caminho absoluto do diretório onde config.py está
basedir = os.path.abspath(os.path.dirname(__file__))

# --- CARREGAMENTO DO .ENV A PARTIR DA RAIZ DO PROJETO ---
# Constrói o caminho para o arquivo .env na pasta pai (raiz do projeto)
dotenv_path = os.path.join(basedir, '..', '.env')
# Carrega as variáveis do arquivo .env especificado
load_dotenv(dotenv_path=dotenv_path)


class Config:
    """
    Classe de configuração base para a aplicação.
    Lê as configurações das variáveis de ambiente, com valores padrão seguros.
    """
    
    # Configuração do Banco de Dados
    DATABASE_URL = os.environ.get('DATABASE_URL', 'projectflow_default.db')
    
    # Configuração de Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # --- CONFIGURAÇÕES DE SEGURANÇA MELHORADAS ---
    # Gera uma chave secreta aleatória se não estiver definida
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        # Em desenvolvimento, gera uma chave temporária
        # Em produção, isso deve SEMPRE estar definido no .env
        JWT_SECRET_KEY = secrets.token_urlsafe(32)
        print("⚠️  AVISO: JWT_SECRET_KEY não definida. Usando chave temporária.")
        print("⚠️  DEFINA JWT_SECRET_KEY no arquivo .env para produção!")
    
    # Configuração de CORS mais restritiva
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Configurações de segurança para uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'json'}
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('SESSION_LIFETIME', 3600))  # 1 hora
    
    # Rate limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    @staticmethod
    def validate_config():
        """Valida se todas as configurações críticas estão definidas."""
        required_vars = []
        
        # Em produção, JWT_SECRET_KEY é obrigatória
        if os.environ.get('FLASK_ENV') == 'production':
            if not os.environ.get('JWT_SECRET_KEY'):
                required_vars.append('JWT_SECRET_KEY')
        
        if required_vars:
            raise ValueError(f"Variáveis de ambiente obrigatórias não definidas: {', '.join(required_vars)}")


class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento."""
    DEBUG = True
    TESTING = False
    
    # CORS mais permissivo em desenvolvimento
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5173']


class TestingConfig(Config):
    """Configuração para ambiente de testes."""
    TESTING = True
    DEBUG = True
    
    # Banco de dados em memória para testes
    DATABASE_URL = 'sqlite:///:memory:'
    
    # Desabilita rate limiting nos testes
    RATELIMIT_ENABLED = False
    
    # JWT com chave fixa para testes
    JWT_SECRET_KEY = 'test-secret-key-do-not-use-in-production'


class ProductionConfig(Config):
    """Configuração para ambiente de produção."""
    DEBUG = False
    TESTING = False
    
    # Em produção, validações mais rigorosas
    @classmethod
    def init_app(cls, app):
        Config.validate_config()
        
        # Log para arquivo em produção
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            file_handler = RotatingFileHandler(
                'logs/projectflow.log', maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)


# Mapeamento de configurações por ambiente
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Retorna a configuração baseada na variável de ambiente FLASK_ENV."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
    
