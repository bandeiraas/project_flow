#!/usr/bin/env python3
"""Servidor Flask que funciona igual ao simple_server.py mas com todas as rotas do app.py"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
import logging

# Importa as dependências do app.py
from config import get_config
from extensions import db, jwt
from routes import register_routes

app = Flask(__name__)

# Configuração básica
config_class = get_config()
app.config.from_object(config_class)

# CORS muito permissivo para teste (igual ao simple_server.py)
CORS(app, 
     origins="*",
     allow_headers="*", 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

# Inicializa extensões
db.init_app(app)
jwt.init_app(app)

# Registra todas as rotas do app.py
register_routes(app)

@app.route('/')
def home():
    return jsonify({
        "message": "Backend funcionando com todas as rotas!",
        "port": 5000,
        "cors": "enabled"
    })

@app.before_request
def log_request():
    print(f"📥 {request.method} {request.path} - Origin: {request.headers.get('Origin', 'None')}")

@app.after_request
def after_request(response):
    print(f"📤 Response: {response.status_code}")
    return response

if __name__ == '__main__':
    print("🚀 Iniciando servidor com todas as rotas...")
    print("🌐 Acessível em:")
    print("   - http://localhost:5000")
    
    if os.environ.get('CODESPACES'):
        codespace = os.environ.get('CODESPACE_NAME', 'codespace')
        print(f"   - https://{codespace}-5000.app.github.dev")
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)