#!/usr/bin/env python3
"""Servidor Flask simples para testar CORS"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

app = Flask(__name__)

# CORS muito permissivo para teste
CORS(app, 
     origins="*",
     allow_headers="*", 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

@app.route('/')
def home():
    return jsonify({
        "message": "Backend funcionando!",
        "port": 5000,
        "cors": "enabled"
    })

@app.route('/api/usuarios')
def usuarios():
    return jsonify({
        "message": "Endpoint usuarios funcionando!",
        "data": []
    })

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        "message": "Login endpoint funcionando!",
        "access_token": "test_token_123"
    })

@app.before_request
def log_request():
    print(f"📥 {request.method} {request.path} - Origin: {request.headers.get('Origin', 'None')}")

@app.after_request
def after_request(response):
    print(f"📤 Response: {response.status_code}")
    return response

if __name__ == '__main__':
    print("🚀 Iniciando servidor simples...")
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