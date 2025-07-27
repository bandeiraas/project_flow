import logging
from flask import Flask, request, g
import os
from config import Config
from extensions import db, cors, jwt

# Importa a função que registra as rotas
from routes import register_routes

def create_app(config_object=Config):
    """
    Application Factory: cria e configura a instância do app Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # --- GARANTIR QUE A PASTA DE UPLOAD EXISTA ---
    # Adicionado para evitar erros de 'File not found' ao salvar uploads.
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        app.logger.info(f"Pasta de upload criada em: {app.config['UPLOAD_FOLDER']}")

    # --- INICIALIZAÇÃO DAS EXTENSÕES ---
    # Inicializa o banco de dados e o CORS com a configuração do app
    db.init_app(app)
    # Configuração de CORS simplificada para depuração.
    # Aplica as permissões a TODAS as rotas da aplicação, removendo a restrição
    # 'resources' que pode estar causando o problema de preflight no upload.
    cors.init_app(app,
                  origins="*",
                  allow_headers="*",
                  supports_credentials=True)
    jwt.init_app(app)

    # --- CONFIGURAÇÃO DO LOGGING ---
    logging.basicConfig(
        level=app.config['LOG_LEVEL'], 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Aplicação Flask criada. Banco de dados em: {app.config['DATABASE_URL']}")

    # --- HOOKS DE GERENCIAMENTO DE SESSÃO ---
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Fecha a sessão do banco de dados ao final da requisição."""
        db_session = g.pop('db_session', None)
        if db_session is not None:
            db_session.close()

    # --- REGISTRO DAS ROTAS ---
    # Chama a função do arquivo routes.py para registrar todos os endpoints
    register_routes(app)

    # --- DEBUGGING HOOK ---
    # Adiciona um log para CADA requisição que chega, ANTES de ser processada.
    # Isso nos ajudará a ver se a requisição OPTIONS está chegando ao Flask.
    @app.before_request
    def log_request_info():
        # Usamos o logger do app para manter o formato consistente
        app.logger.debug(f"Request: {request.method} {request.path} - Headers: {request.headers}")

    return app

# --- PONTO DE ENTRADA DA APLICAÇÃO ---
if __name__ == "__main__":
    # Cria a instância da aplicação usando a fábrica
    app = create_app()
    # Executa o servidor de desenvolvimento.
    # 'debug=True' mantém o depurador interativo para erros.
    # 'use_reloader=False' impede que o servidor reinicie a cada upload de arquivo,
    # o que estava limpando os logs do terminal e impedindo a depuração.
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
           