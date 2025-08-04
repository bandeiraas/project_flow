#!/usr/bin/env python3
# backend/test_server.py
"""
Servidor Flask mínimo para testar se o ambiente está funcionando.
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# CORS permissivo para teste
CORS(app, origins="*", supports_credentials=True)

@app.route('/')
def hello():
    return jsonify({
        "message": "🚀 Servidor Flask funcionando!",
        "status": "OK",
        "environment": os.environ.get('CODESPACES', 'local')
    })

@app.route('/api/test')
def api_test():
    return jsonify({
        "message": "✅ API funcionando!",
        "cors": "enabled",
        "port": 5000
    })

@app.route('/api/usuarios')
def usuarios_test():
    return jsonify({
        "message": "🔧 Endpoint /api/usuarios funcionando!",
        "users": ["test_user"],
        "count": 1
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor de teste...")
    print("🌐 Será acessível em:")
    print("   - Local: http://localhost:5000")
    if os.environ.get('CODESPACES'):
        codespace_name = os.environ.get('CODESPACE_NAME', 'codespace')
        print(f"   - Codespaces: https://{codespace_name}-5000.app.github.dev")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )