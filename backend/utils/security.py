# backend/utils/security.py
import os
import hashlib
import magic
from werkzeug.utils import secure_filename
from flask import current_app
from typing import Tuple, Optional


def allowed_file(filename: str) -> bool:
    """
    Verifica se o arquivo tem uma extensão permitida.
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        True se a extensão for permitida, False caso contrário
    """
    if not filename or '.' not in filename:
        return False
        
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in current_app.config.get('ALLOWED_EXTENSIONS', set())


def validate_file_content(file_path: str, expected_extensions: set = None) -> bool:
    """
    Valida o conteúdo do arquivo usando python-magic para verificar o tipo MIME.
    Isso previne ataques onde arquivos maliciosos são renomeados com extensões seguras.
    
    Args:
        file_path: Caminho para o arquivo
        expected_extensions: Extensões esperadas (opcional)
        
    Returns:
        True se o conteúdo for válido, False caso contrário
    """
    try:
        # Mapeia tipos MIME para extensões seguras
        safe_mime_types = {
            'text/plain': ['txt'],
            'application/pdf': ['pdf'],
            'image/jpeg': ['jpg', 'jpeg'],
            'image/png': ['png'],
            'image/gif': ['gif'],
            'application/zip': ['zip'],
            'application/json': ['json'],
            'text/csv': ['csv']
        }
        
        # Detecta o tipo MIME real do arquivo
        mime_type = magic.from_file(file_path, mime=True)
        
        # Se não temos extensões esperadas, usa as configuradas
        if expected_extensions is None:
            expected_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())
        
        # Verifica se o tipo MIME corresponde às extensões permitidas
        allowed_extensions_for_mime = safe_mime_types.get(mime_type, [])
        
        # Verifica se há interseção entre extensões permitidas e extensões do MIME
        return bool(set(allowed_extensions_for_mime) & expected_extensions)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao validar conteúdo do arquivo {file_path}: {e}")
        return False


def generate_secure_filename(filename: str, user_id: int = None) -> str:
    """
    Gera um nome de arquivo seguro e único.
    
    Args:
        filename: Nome original do arquivo
        user_id: ID do usuário (opcional, para adicionar ao hash)
        
    Returns:
        Nome de arquivo seguro e único
    """
    # Sanitiza o nome do arquivo
    secure_name = secure_filename(filename)
    
    if not secure_name:
        secure_name = "arquivo"
    
    # Separa nome e extensão
    name, ext = os.path.splitext(secure_name)
    
    # Cria um hash único baseado no nome, timestamp e user_id
    import time
    hash_input = f"{name}_{int(time.time())}"
    if user_id:
        hash_input += f"_{user_id}"
    
    file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    # Retorna nome seguro com hash
    return f"{name}_{file_hash}{ext}"


def validate_file_size(file_size: int, max_size: Optional[int] = None) -> bool:
    """
    Valida o tamanho do arquivo.
    
    Args:
        file_size: Tamanho do arquivo em bytes
        max_size: Tamanho máximo permitido em bytes (opcional)
        
    Returns:
        True se o tamanho for válido, False caso contrário
    """
    if max_size is None:
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
    
    return file_size <= max_size


def sanitize_path(path: str) -> str:
    """
    Sanitiza um caminho para prevenir path traversal attacks.
    
    Args:
        path: Caminho a ser sanitizado
        
    Returns:
        Caminho sanitizado
    """
    # Remove caracteres perigosos
    dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    
    sanitized = path
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    
    return sanitized


class FileUploadValidator:
    """
    Classe para validação completa de uploads de arquivos.
    """
    
    def __init__(self, allowed_extensions: set = None, max_size: int = None):
        self.allowed_extensions = allowed_extensions or current_app.config.get('ALLOWED_EXTENSIONS', set())
        self.max_size = max_size or current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
    
    def validate(self, file, filename: str = None) -> Tuple[bool, str]:
        """
        Valida um arquivo de upload completamente.
        
        Args:
            file: Objeto de arquivo do Flask
            filename: Nome do arquivo (opcional, usa file.filename se não fornecido)
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if not file:
            return False, "Nenhum arquivo fornecido"
        
        filename = filename or file.filename
        
        if not filename:
            return False, "Nome do arquivo não fornecido"
        
        # Valida extensão
        if not allowed_file(filename):
            return False, f"Tipo de arquivo não permitido. Extensões permitidas: {', '.join(self.allowed_extensions)}"
        
        # Valida tamanho (se possível determinar)
        try:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Volta para o início
            
            if not validate_file_size(file_size, self.max_size):
                return False, f"Arquivo muito grande. Tamanho máximo: {self.max_size / (1024*1024):.1f}MB"
        except Exception:
            # Se não conseguir determinar o tamanho, continua
            pass
        
        return True, "Arquivo válido"
    
    def save_file(self, file, upload_folder: str, user_id: int = None) -> Tuple[bool, str, Optional[str]]:
        """
        Salva um arquivo validado no diretório de upload.
        
        Args:
            file: Objeto de arquivo do Flask
            upload_folder: Pasta de destino
            user_id: ID do usuário (opcional)
            
        Returns:
            Tuple (success, message, filepath)
        """
        # Valida primeiro
        is_valid, error_msg = self.validate(file)
        if not is_valid:
            return False, error_msg, None
        
        try:
            # Gera nome seguro
            secure_name = generate_secure_filename(file.filename, user_id)
            
            # Cria o caminho completo
            file_path = os.path.join(upload_folder, secure_name)
            
            # Garante que o diretório existe
            os.makedirs(upload_folder, exist_ok=True)
            
            # Salva o arquivo
            file.save(file_path)
            
            # Valida o conteúdo após salvar
            if not validate_file_content(file_path, self.allowed_extensions):
                os.remove(file_path)  # Remove arquivo inválido
                return False, "Conteúdo do arquivo não corresponde à extensão", None
            
            return True, "Arquivo salvo com sucesso", file_path
            
        except Exception as e:
            current_app.logger.error(f"Erro ao salvar arquivo: {e}")
            return False, "Erro interno ao salvar arquivo", None