# backend/utils/database.py
import logging
from contextlib import contextmanager
from functools import wraps
from typing import Generator, Any, Callable
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from flask import g, current_app
from extensions import db

logger = logging.getLogger(__name__)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager para gerenciar sessões do banco de dados.
    Garante que a sessão seja sempre fechada e faz rollback em caso de erro.
    
    Usage:
        with get_db_session() as session:
            user = session.query(Usuario).get(1)
            session.commit()
    """
    session = db.get_session()
    session_id = id(session)
    logger.debug(f"Sessão DB {session_id} aberta")
    
    try:
        yield session
        session.commit()
        logger.debug(f"Sessão DB {session_id} commitada com sucesso")
    except Exception as e:
        session.rollback()
        logger.error(f"Erro na sessão DB {session_id}, fazendo rollback: {e}")
        raise
    finally:
        session.close()
        logger.debug(f"Sessão DB {session_id} fechada")


@contextmanager
def get_db_session_with_savepoint() -> Generator[Session, None, None]:
    """
    Context manager com savepoint para operações aninhadas.
    Útil quando você precisa de transações dentro de transações.
    
    Usage:
        with get_db_session() as session:
            # operação principal
            with get_db_session_with_savepoint() as nested_session:
                # operação que pode falhar
                pass
    """
    session = db.get_session()
    session_id = id(session)
    logger.debug(f"Sessão DB {session_id} com savepoint aberta")
    
    savepoint = session.begin_nested()
    try:
        yield session
        savepoint.commit()
        logger.debug(f"Savepoint da sessão DB {session_id} commitado")
    except Exception as e:
        savepoint.rollback()
        logger.error(f"Erro no savepoint da sessão DB {session_id}, fazendo rollback: {e}")
        raise
    finally:
        session.close()
        logger.debug(f"Sessão DB {session_id} com savepoint fechada")


def with_db_session(func: Callable) -> Callable:
    """
    Decorator que injeta uma sessão do banco de dados como primeiro argumento.
    A sessão é automaticamente gerenciada (commit/rollback/close).
    
    Usage:
        @with_db_session
        def create_user(session, name, email):
            user = Usuario(name=name, email=email)
            session.add(user)
            return user
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with get_db_session() as session:
            return func(session, *args, **kwargs)
    return wrapper


def with_db_transaction(func: Callable) -> Callable:
    """
    Decorator que executa uma função dentro de uma transação.
    Se a função retornar False ou lançar uma exceção, faz rollback.
    
    Usage:
        @with_db_transaction
        def transfer_money(session, from_account, to_account, amount):
            # operações que devem ser atômicas
            if not validate_transfer(from_account, amount):
                return False  # Automaticamente faz rollback
            
            from_account.balance -= amount
            to_account.balance += amount
            return True
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with get_db_session() as session:
            try:
                result = func(session, *args, **kwargs)
                if result is False:
                    session.rollback()
                    logger.warning(f"Transação {func.__name__} retornou False, fazendo rollback")
                return result
            except Exception as e:
                session.rollback()
                logger.error(f"Erro na transação {func.__name__}: {e}")
                raise
    return wrapper


class DatabaseManager:
    """
    Classe para gerenciar operações complexas do banco de dados.
    Útil para operações que precisam de múltiplas sessões ou controle fino.
    """
    
    def __init__(self):
        self.session = None
    
    def __enter__(self):
        self.session = db.get_session()
        logger.debug(f"DatabaseManager: sessão {id(self.session)} aberta")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            try:
                if exc_type:
                    self.session.rollback()
                    logger.error(f"DatabaseManager: erro detectado, fazendo rollback da sessão {id(self.session)}")
                else:
                    self.session.commit()
                    logger.debug(f"DatabaseManager: sessão {id(self.session)} commitada")
            finally:
                self.session.close()
                logger.debug(f"DatabaseManager: sessão {id(self.session)} fechada")
    
    def execute_in_transaction(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa uma função dentro da transação atual.
        
        Args:
            func: Função a ser executada
            *args, **kwargs: Argumentos para a função
            
        Returns:
            Resultado da função
        """
        if not self.session:
            raise RuntimeError("DatabaseManager não está em um contexto ativo")
        
        return func(self.session, *args, **kwargs)
    
    def create_savepoint(self, name: str = None):
        """
        Cria um savepoint na transação atual.
        
        Args:
            name: Nome do savepoint (opcional)
            
        Returns:
            Objeto savepoint
        """
        if not self.session:
            raise RuntimeError("DatabaseManager não está em um contexto ativo")
        
        savepoint = self.session.begin_nested()
        logger.debug(f"Savepoint '{name or 'unnamed'}' criado na sessão {id(self.session)}")
        return savepoint


def get_or_create_session() -> Session:
    """
    Obtém a sessão atual do contexto da aplicação ou cria uma nova.
    Útil para funções que podem ser chamadas tanto dentro quanto fora de um contexto de sessão.
    
    Returns:
        Sessão do banco de dados
    """
    # Verifica se já existe uma sessão no contexto da aplicação
    if hasattr(g, 'db_session') and g.db_session:
        return g.db_session
    
    # Cria uma nova sessão e armazena no contexto
    session = db.get_session()
    g.db_session = session
    logger.debug(f"Nova sessão {id(session)} criada e armazenada no contexto da aplicação")
    return session


def close_session_on_teardown():
    """
    Fecha a sessão armazenada no contexto da aplicação.
    Deve ser chamada no teardown da aplicação.
    """
    session = g.pop('db_session', None)
    if session:
        try:
            session.close()
            logger.debug(f"Sessão {id(session)} fechada no teardown")
        except Exception as e:
            logger.error(f"Erro ao fechar sessão no teardown: {e}")


# Funções de conveniência para operações comuns
@with_db_session
def safe_get_by_id(session: Session, model_class, entity_id: int):
    """
    Busca uma entidade por ID de forma segura.
    
    Args:
        session: Sessão do banco
        model_class: Classe do modelo
        entity_id: ID da entidade
        
    Returns:
        Entidade encontrada ou None
    """
    try:
        return session.query(model_class).get(entity_id)
    except SQLAlchemyError as e:
        logger.error(f"Erro ao buscar {model_class.__name__} com ID {entity_id}: {e}")
        return None


@with_db_session
def safe_create(session: Session, model_instance):
    """
    Cria uma nova entidade de forma segura.
    
    Args:
        session: Sessão do banco
        model_instance: Instância do modelo a ser criada
        
    Returns:
        Instância criada ou None em caso de erro
    """
    try:
        session.add(model_instance)
        session.flush()  # Para obter o ID sem fazer commit
        return model_instance
    except SQLAlchemyError as e:
        logger.error(f"Erro ao criar {type(model_instance).__name__}: {e}")
        return None


@with_db_session
def safe_update(session: Session, model_instance, **kwargs):
    """
    Atualiza uma entidade de forma segura.
    
    Args:
        session: Sessão do banco
        model_instance: Instância a ser atualizada
        **kwargs: Campos a serem atualizados
        
    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    try:
        for key, value in kwargs.items():
            if hasattr(model_instance, key):
                setattr(model_instance, key, value)
        
        session.flush()
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erro ao atualizar {type(model_instance).__name__}: {e}")
        return False


@with_db_session
def safe_delete(session: Session, model_instance):
    """
    Deleta uma entidade de forma segura.
    
    Args:
        session: Sessão do banco
        model_instance: Instância a ser deletada
        
    Returns:
        True se deletado com sucesso, False caso contrário
    """
    try:
        session.delete(model_instance)
        session.flush()
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erro ao deletar {type(model_instance).__name__}: {e}")
        return False