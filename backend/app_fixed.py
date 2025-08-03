#!/usr/bin/env python3
"""App.py corrigido para funcionar igual ao simple_server.py"""

import logging
import os
from flask import Flask, request, g, jsonify
from config import get_config
from extensions import db, cors, jwt

# Importa a função que registra as rotas
from routes import register_routes

def create_app(config_name=None):
    """Application Factory simplificado"""
    app = Flask(__name__)
    
    # Configuração básica
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Extensões básicas
    db.init_app(app)
    jwt.init_app(app)
    
    # CORS PERMISSIVO (igual ao simple_server.py)
    cors.init_app(
        app,
        origins="*",
        allow_headers="*", 
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        supports_credentials=True
    )
    
    # Logs simples
    logging.basicConfig(level=logging.INFO)
    
    # Hooks de sessão
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        from utils.database import close_session_on_teardown
        close_session_on_teardown()
    
    # Registra rotas
    register_routes(app)
    
    # Logs de debug (igual ao simple_server.py)
    @app.before_request
    def log_request():
        print(f"📥 {request.method} {request.path} - Origin: {request.headers.get('Origin', 'None')}")
    
    @app.after_request
    def after_request(response):
        print(f"📤 Response: {response.status_code}")
        return response
    
    return app

if __name__ == "__main__":
    app = create_app()
    
    print("🚀 Iniciando app.py corrigido...")
    print("🌐 Acessível em:")
    print("   - http://localhost:5000")
    
    if os.environ.get('CODESPACES'):
        codespace = os.environ.get('CODESPACE_NAME', 'codespace')
        print(f"   - https://{codespace}-5000.app.github.dev")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False,
        threaded=True
    )