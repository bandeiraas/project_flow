# backend/utils/cors_middleware.py
"""
Middleware personalizado para CORS com suporte flexível ao GitHub Codespaces.
"""

from flask import request, make_response
import re


class FlexibleCORSMiddleware:
    """
    Middleware CORS personalizado que permite padrões flexíveis para desenvolvimento.
    """
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o middleware com a aplicação Flask."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Processa requisições OPTIONS para CORS preflight."""
        if request.method == 'OPTIONS':
            response = make_response()
            return self.add_cors_headers(response)
    
    def after_request(self, response):
        """Adiciona headers CORS a todas as respostas."""
        return self.add_cors_headers(response)
    
    def add_cors_headers(self, response):
        """Adiciona headers CORS apropriados à resposta."""
        origin = request.headers.get('Origin')
        
        if self.is_origin_allowed(origin):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            response.headers['Access-Control-Allow-Headers'] = (
                'Content-Type, Authorization, Accept, Origin, X-Requested-With, '
                'Access-Control-Allow-Credentials, Cache-Control'
            )
            response.headers['Access-Control-Max-Age'] = '86400'  # 24 horas
        
        return response
    
    def is_origin_allowed(self, origin):
        """
        Verifica se a origem é permitida.
        
        Args:
            origin: URL de origem da requisição
            
        Returns:
            bool: True se a origem for permitida
        """
        if not origin:
            return False
        
        # Lista de padrões permitidos
        allowed_patterns = [
            # Localhost para desenvolvimento
            r'^https?://localhost:\d+$',
            r'^https?://127\.0\.0\.1:\d+$',
            
            # GitHub Codespaces
            r'^https://[a-zA-Z0-9\-]+\.app\.github\.dev$',
            r'^https://[a-zA-Z0-9\-]+-\d+\.app\.github\.dev$',
            
            # GitHub Preview (backup)
            r'^https://[a-zA-Z0-9\-]+\.githubpreview\.dev$',
            r'^https://[a-zA-Z0-9\-]+-\d+\.githubpreview\.dev$',
            
            # Outros domínios GitHub
            r'^https://[a-zA-Z0-9\-]+\.github\.dev$',
        ]
        
        # Verifica se a origem corresponde a algum padrão
        for pattern in allowed_patterns:
            if re.match(pattern, origin):
                return True
        
        # Em desenvolvimento, permite origens específicas configuradas
        from flask import current_app
        if current_app and current_app.config.get('FLASK_ENV') == 'development':
            configured_origins = current_app.config.get('CORS_ORIGINS', [])
            if origin in configured_origins:
                return True
        
        return False


def setup_flexible_cors(app):
    """
    Configura CORS flexível para a aplicação.
    
    Args:
        app: Instância da aplicação Flask
    """
    middleware = FlexibleCORSMiddleware(app)
    app.logger.info("🔧 CORS flexível configurado com suporte ao GitHub Codespaces")
    return middleware