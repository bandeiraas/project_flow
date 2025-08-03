import logging
import os
from flask import Flask, request, g
from config import get_config
from extensions import db, cors, jwt

# Importa a função que registra as rotas
from routes import register_routes

# Importa o middleware CORS personalizado
from utils.cors_middleware import setup_flexible_cors


def create_app(config_name=None):
    """
    Application Factory: cria e configura a instância do app Flask.
    
    Args:
        config_name: Nome da configuração a ser usada (development, testing, production)
                    Se None, usa a configuração baseada em FLASK_ENV
    """
    app = Flask(__name__)
    
    # Carrega a configuração apropriada
    if config_name:
        from config import config
        config_class = config.get(config_name, config['default'])
    else:
        config_class = get_config()
    
    app.config.from_object(config_class)
    
    # Chama init_app se existir (para configurações específicas de produção)
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)

    # --- GARANTIR QUE A PASTA DE UPLOAD EXISTA ---
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        app.logger.info(f"Pasta de upload criada em: {app.config['UPLOAD_FOLDER']}")

    # --- INICIALIZAÇÃO DAS EXTENSÕES ---
    db.init_app(app)
    
    # Configuração de CORS mais flexível para desenvolvimento
    cors_origins = app.config.get('CORS_ORIGINS', ['http://localhost:3000'])
    
    # Em desenvolvimento, permite GitHub Codespaces com padrão mais flexível
    if app.config.get('FLASK_ENV') == 'development':
        # Adiciona suporte para qualquer subdomínio do GitHub Codespaces
        cors_origins.extend([
            'https://*.app.github.dev',
            'https://*.githubpreview.dev',
            'https://*.github.dev'
        ])
        
        # Log das origens permitidas para debug
        app.logger.info(f"CORS Origins configuradas: {cors_origins}")
    
    # CORS muito permissivo para desenvolvimento (igual ao simple_server.py)
    if app.config.get('FLASK_ENV') == 'development':
        cors.init_app(
            app,
            origins="*",
            allow_headers="*", 
            methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            supports_credentials=True
        )
    else:
        cors.init_app(
            app,
            origins=cors_origins,
            allow_headers=[
                "Content-Type", 
                "Authorization", 
                "Access-Control-Allow-Credentials",
                "Accept",
                "Origin",
                "X-Requested-With"
            ],
            supports_credentials=True,
            methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
        )
    
    # Adiciona middleware CORS personalizado para máxima compatibilidade
    if app.config.get('FLASK_ENV') == 'development':
        setup_flexible_cors(app)
    
    jwt.init_app(app)

    # --- CONFIGURAÇÃO DO LOGGING ---
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']), 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Aplicação Flask criada. Ambiente: {app.config.get('FLASK_ENV', 'development')}")
    logger.info(f"Banco de dados: {app.config['DATABASE_URL']}")

    # --- HOOKS DE GERENCIAMENTO DE SESSÃO ---
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Fecha a sessão do banco de dados ao final da requisição."""
        from utils.database import close_session_on_teardown
        close_session_on_teardown()

    # --- REGISTRO DAS ROTAS ---
    register_routes(app)

    # --- DEBUGGING HOOK (apenas em desenvolvimento) ---
    if app.config.get('DEBUG', False):
        @app.before_request
        def log_request_info():
            print(f"📥 {request.method} {request.path} - Origin: {request.headers.get('Origin', 'None')}")
            app.logger.debug(f"Request: {request.method} {request.path} - Headers: {dict(request.headers)}")
            if request.headers.get('Origin'):
                app.logger.debug(f"Origin: {request.headers.get('Origin')}")
        
        @app.after_request
        def after_request(response):
            print(f"📤 Response: {response.status_code}")
            return response

    # --- TRATAMENTO DE ERROS GLOBAL ---
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Requisição inválida', 'message': str(error.description)}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Não autorizado', 'message': 'Token de acesso inválido ou expirado'}, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Acesso negado', 'message': 'Você não tem permissão para acessar este recurso'}, 403

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Recurso não encontrado', 'message': str(error.description)}, 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Erro interno do servidor: {error}")
        return {'error': 'Erro interno do servidor', 'message': 'Algo deu errado. Tente novamente mais tarde.'}, 500

    return app


# --- PONTO DE ENTRADA DA APLICAÇÃO ---
if __name__ == "__main__":
    # Cria a instância da aplicação usando a fábrica
    app = create_app()
    
    # Configurações do servidor baseadas no ambiente
    debug_mode = app.config.get('DEBUG', False)
    
    # Executa o servidor de desenvolvimento
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=debug_mode, 
        use_reloader=debug_mode  # Só usa reloader em modo debug
    )
           