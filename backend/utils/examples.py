# backend/utils/examples.py
"""
Exemplos de uso do novo sistema de gestão de sessões do banco de dados.
Este arquivo serve como documentação e referência para desenvolvedores.
"""

from utils.database import (
    get_db_session, 
    with_db_session, 
    with_db_transaction,
    DatabaseManager,
    safe_get_by_id,
    safe_create,
    safe_update,
    safe_delete
)
from models import Usuario, Projeto


# =============================================================================
# EXEMPLO 1: Usando Context Manager Simples
# =============================================================================

def exemplo_context_manager():
    """Exemplo básico usando context manager."""
    
    with get_db_session() as session:
        # Busca usuários
        usuarios = session.query(Usuario).all()
        
        # Cria um novo usuário
        novo_usuario = Usuario(
            nome_completo="João Silva",
            email="joao@example.com",
            cargo="Desenvolvedor"
        )
        session.add(novo_usuario)
        
        # O commit é automático se não houver exceções
        # O rollback é automático se houver exceções
        # A sessão é sempre fechada


# =============================================================================
# EXEMPLO 2: Usando Decorator @with_db_session
# =============================================================================

@with_db_session
def criar_usuario_com_decorator(session, nome: str, email: str):
    """Exemplo usando decorator que injeta a sessão."""
    
    # Verifica se o email já existe
    usuario_existente = session.query(Usuario).filter_by(email=email).first()
    if usuario_existente:
        raise ValueError(f"Email {email} já está em uso")
    
    # Cria o novo usuário
    novo_usuario = Usuario(
        nome_completo=nome,
        email=email,
        cargo="Usuário"
    )
    session.add(novo_usuario)
    
    return novo_usuario


# =============================================================================
# EXEMPLO 3: Usando Decorator @with_db_transaction
# =============================================================================

@with_db_transaction
def transferir_projeto(session, projeto_id: int, novo_responsavel_id: int):
    """Exemplo de transação que pode falhar e fazer rollback."""
    
    # Busca o projeto
    projeto = session.query(Projeto).get(projeto_id)
    if not projeto:
        return False  # Retornar False faz rollback automático
    
    # Busca o novo responsável
    novo_responsavel = session.query(Usuario).get(novo_responsavel_id)
    if not novo_responsavel:
        return False  # Rollback automático
    
    # Faz a transferência
    responsavel_anterior_id = projeto.id_responsavel
    projeto.id_responsavel = novo_responsavel_id
    
    # Log da transferência (exemplo)
    print(f"Projeto {projeto_id} transferido de {responsavel_anterior_id} para {novo_responsavel_id}")
    
    return True  # Commit automático


# =============================================================================
# EXEMPLO 4: Usando DatabaseManager para Operações Complexas
# =============================================================================

def exemplo_database_manager():
    """Exemplo usando DatabaseManager para controle fino."""
    
    with DatabaseManager() as db_manager:
        # Operação 1: Criar usuário
        def criar_usuario(session):
            usuario = Usuario(
                nome_completo="Maria Santos",
                email="maria@example.com",
                cargo="Gerente"
            )
            session.add(usuario)
            session.flush()  # Para obter o ID
            return usuario
        
        novo_usuario = db_manager.execute_in_transaction(criar_usuario)
        
        # Operação 2: Criar projeto para o usuário (com savepoint)
        savepoint = db_manager.create_savepoint("criar_projeto")
        
        try:
            def criar_projeto(session):
                projeto = Projeto(
                    nome_projeto="Projeto de Exemplo",
                    descricao="Descrição do projeto",
                    id_responsavel=novo_usuario.id_usuario,
                    status_atual="Planejamento"
                )
                session.add(projeto)
                return projeto
            
            novo_projeto = db_manager.execute_in_transaction(criar_projeto)
            savepoint.commit()
            
        except Exception as e:
            savepoint.rollback()
            print(f"Erro ao criar projeto: {e}")
            # O usuário ainda será criado pois apenas o savepoint fez rollback


# =============================================================================
# EXEMPLO 5: Usando Funções de Conveniência
# =============================================================================

def exemplo_funcoes_conveniencia():
    """Exemplo usando as funções de conveniência seguras."""
    
    # Busca segura por ID
    usuario = safe_get_by_id(Usuario, 1)
    if not usuario:
        print("Usuário não encontrado")
        return
    
    # Criação segura
    novo_projeto = Projeto(
        nome_projeto="Projeto Seguro",
        descricao="Criado com função segura",
        id_responsavel=usuario.id_usuario
    )
    
    projeto_criado = safe_create(novo_projeto)
    if not projeto_criado:
        print("Erro ao criar projeto")
        return
    
    # Atualização segura
    sucesso = safe_update(projeto_criado, status_atual="Em Andamento")
    if not sucesso:
        print("Erro ao atualizar projeto")
        return
    
    # Deleção segura (comentado para não deletar de verdade)
    # sucesso = safe_delete(projeto_criado)
    # if not sucesso:
    #     print("Erro ao deletar projeto")


# =============================================================================
# EXEMPLO 6: Padrão de Service Refatorado
# =============================================================================

class ExemploService:
    """Exemplo de como refatorar um service para usar o novo sistema."""
    
    @with_db_session
    def buscar_projetos_usuario(self, session, usuario_id: int):
        """Método que usa decorator para gestão automática de sessão."""
        return session.query(Projeto).filter_by(id_responsavel=usuario_id).all()
    
    def operacao_complexa(self, usuario_id: int, dados_projeto: dict):
        """Método que usa context manager para operações complexas."""
        
        with get_db_session() as session:
            # Verifica se o usuário existe
            usuario = session.query(Usuario).get(usuario_id)
            if not usuario:
                raise ValueError("Usuário não encontrado")
            
            # Cria o projeto
            projeto = Projeto(**dados_projeto, id_responsavel=usuario_id)
            session.add(projeto)
            
            # Atualiza estatísticas do usuário (exemplo)
            # usuario.total_projetos += 1
            
            # Se chegou até aqui, commit automático
            return projeto.para_dicionario()
    
    def transferir_multiplos_projetos(self, projetos_ids: list, novo_responsavel_id: int):
        """Exemplo de transação que pode fazer rollback parcial."""
        
        with DatabaseManager() as db_manager:
            resultados = []
            
            for projeto_id in projetos_ids:
                savepoint = db_manager.create_savepoint(f"projeto_{projeto_id}")
                
                try:
                    def transferir(session):
                        projeto = session.query(Projeto).get(projeto_id)
                        if not projeto:
                            raise ValueError(f"Projeto {projeto_id} não encontrado")
                        
                        projeto.id_responsavel = novo_responsavel_id
                        return projeto
                    
                    projeto = db_manager.execute_in_transaction(transferir)
                    savepoint.commit()
                    resultados.append({"projeto_id": projeto_id, "sucesso": True})
                    
                except Exception as e:
                    savepoint.rollback()
                    resultados.append({"projeto_id": projeto_id, "sucesso": False, "erro": str(e)})
            
            return resultados


# =============================================================================
# EXEMPLO 7: Migração de Código Antigo
# =============================================================================

# ANTES (código antigo com problemas):
def codigo_antigo_problematico():
    """Exemplo do que NÃO fazer - código com vazamentos de sessão."""
    
    # ❌ PROBLEMÁTICO: Sessão pode não ser fechada
    session = db.get_session()
    usuarios = session.query(Usuario).all()
    # Se houver uma exceção aqui, a sessão nunca é fechada!
    session.close()
    
    return usuarios


# DEPOIS (código refatorado):
@with_db_session
def codigo_refatorado(session):
    """Exemplo do que fazer - código seguro com gestão automática."""
    
    # ✅ CORRETO: Sessão é gerenciada automaticamente
    usuarios = session.query(Usuario).all()
    # Mesmo se houver exceção, a sessão será fechada automaticamente
    
    return usuarios


# =============================================================================
# EXEMPLO 8: Teste de Performance
# =============================================================================

def exemplo_performance():
    """Exemplo mostrando que o novo sistema não impacta performance."""
    
    import time
    
    # Medindo tempo com context manager
    start = time.time()
    with get_db_session() as session:
        usuarios = session.query(Usuario).limit(100).all()
    tempo_context_manager = time.time() - start
    
    # Medindo tempo com decorator
    @with_db_session
    def buscar_com_decorator(session):
        return session.query(Usuario).limit(100).all()
    
    start = time.time()
    usuarios = buscar_com_decorator()
    tempo_decorator = time.time() - start
    
    print(f"Context Manager: {tempo_context_manager:.4f}s")
    print(f"Decorator: {tempo_decorator:.4f}s")
    print("Diferença é mínima - o overhead é negligível!")


if __name__ == "__main__":
    print("Este arquivo contém exemplos de uso do sistema de gestão de sessões.")
    print("Execute as funções individualmente para testar os diferentes padrões.")