#!/usr/bin/env python3
"""Teste simples do app.py"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("🚀 Iniciando servidor de teste...")
    print("🌐 Acessível em:")
    print("   - http://localhost:8080")
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False,
        use_reloader=False,
        threaded=True
    )