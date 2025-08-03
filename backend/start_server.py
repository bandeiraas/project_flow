#!/usr/bin/env python3
# backend/start_server.py
"""
Script para iniciar o servidor backend com configurações adequadas.
"""

import os
import sys
from app import create_app

def main():
    """Inicia o servidor com configurações adequadas para o ambiente."""
    
    # Detecta se está rodando no GitHub Codespaces
    is_codespaces = os.environ.get('CODESPACES') == 'true'
    
    # Configura variáveis de ambiente se necessário
    if is_codespaces:
        print("🚀 Detectado GitHub Codespaces - Configurando para ambiente de desenvolvimento")
        os.environ['FLASK_ENV'] = 'development'
        # No Codespaces, o host deve ser 0.0.0.0 para ser acessível externamente
        host = '0.0.0.0'
        port = 5000
    else:
        print("🏠 Ambiente local detectado")
        host = '127.0.0.1'
        port = 5000
    
    # Cria a aplicação
    app = create_app()
    
    print(f"🔧 Configurações:")
    print(f"   - Ambiente: {app.config.get('FLASK_ENV', 'development')}")
    print(f"   - Host: {host}")
    print(f"   - Porta: {port}")
    print(f"   - Debug: {app.config.get('DEBUG', False)}")
    print(f"   - CORS Origins: {app.config.get('CORS_ORIGINS', [])}")
    
    if is_codespaces:
        print(f"🌐 Servidor será acessível em: https://{os.environ.get('CODESPACE_NAME', 'codespace')}-5000.app.github.dev")
    else:
        print(f"🌐 Servidor será acessível em: http://{host}:{port}")
    
    print("\n" + "="*60)
    print("🚀 INICIANDO SERVIDOR BACKEND")
    print("="*60)
    
    # Inicia o servidor
    try:
        app.run(
            host=host,
            port=port,
            debug=app.config.get('DEBUG', True),
            use_reloader=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n⚠️  Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()