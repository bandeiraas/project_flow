#!/usr/bin/env python3
"""Teste muito simples"""

from flask import Flask, jsonify, request
from flask_cors import CORS

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
        "message": "Teste funcionando!",
        "port": 9999
    })

@app.route('/api/auth/me', methods=['GET', 'OPTIONS'])
def me():
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        "message": "Rota /api/auth/me funcionando!",
        "user": {
            "id": 1,
            "email": "teste@exemplo.com"
        }
    })

@app.before_request
def log_request():
    print(f"📥 {request.method} {request.path} - Origin: {request.headers.get('Origin', 'None')}")

@app.after_request
def after_request(response):
    print(f"📤 Response: {response.status_code}")
    return response

if __name__ == '__main__':
    print("🚀 Iniciando teste simples...")
    print("🌐 Acessível em: http://localhost:9999")
    
    app.run(
        host='0.0.0.0',
        port=9999,
        debug=False,
        use_reloader=False,
        threaded=True
    )