import logging
from flask import Flask
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

    # --- INICIALIZAÇÃO DAS EXTENSÕES ---
    # Inicializa o banco de dados e o CORS com a configuração do app
    db.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)

    # --- CONFIGURAÇÃO DO LOGGING ---
    logging.basicConfig(
        level=app.config['LOG_LEVEL'], 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Aplicação Flask criada. Banco de dados em: {app.config['DATABASE_URL']}")

    # --- REGISTRO DAS ROTAS ---
    # Chama a função do arquivo routes.py para registrar todos os endpoints
    register_routes(app)

    return app

# --- PONTO DE ENTRADA DA APLICAÇÃO ---
if __name__ == "__main__":
    # Cria a instância da aplicação usando a fábrica
    app = create_app()
    # Executa o servidor de desenvolvimento
    app.run(host='0.0.0.0', port=5000, debug=True)
           