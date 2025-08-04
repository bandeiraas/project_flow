#!/usr/bin/env python3
"""Versão simplificada do app.py que funciona igual ao simple_server.py"""

import logging
import os
from flask import Flask, request, g, jsonify
from config import get_config
from extensions import db, cors, jwt

# Importa a função que registra as rotas
from routes import register_routes

def create_app(config_name=None):
    """
    Application Factory: cria e configura a instância do app Flask.
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
    
    # CORS muito permissivo (igual ao simple_server.py)
    cors.init_app(
        app,
        origins="*",
        allow_headers="*", 
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        supports_credentials=True
    )
    
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

    # --- DEBUGGING HOOK (igual ao simple_server.py) ---
    @app.before_request
    def log_request():
        print(f"📥 {request.method} {request.path} - Origin: {request.headers.get('Origin', 'None')}")

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
    
    print("🚀 Iniciando servidor simplificado...")
    print("🌐 Acessível em:")
    print("   - http://localhost:5000")
    
    if os.environ.get('CODESPACES'):
        codespace = os.environ.get('CODESPACE_NAME', 'codespace')
        print(f"   - https://{codespace}-5000.app.github.dev")
    
    # Executa o servidor de desenvolvimento
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=False,
        use_reloader=False,
        threaded=True
    )