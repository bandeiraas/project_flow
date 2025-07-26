import logging
from flask import jsonify, abort, request, current_app
from pydantic import ValidationError
from sqlalchemy import inspect

# Importa as ferramentas de autenticação
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os

# Importa os modelos
from models import Projeto, Usuario, Area
from models.objetivo_model import ObjetivoEstrategico

# Importa as CLASSES de serviço e os schemas
from services.projeto_service import ProjetoService
from services.homologacao_service import HomologacaoService
from services.usuario_service import UsuarioService
from services.tarefa_service import TarefaService


from schemas.projeto_schema import ProjetoCreateSchema, StatusUpdateSchema, ProjetoUpdateSchema
from schemas.homologacao_schema import HomologacaoStartSchema, HomologacaoEndSchema
from schemas.usuario_schema import UserRoleUpdateSchema, ProfileUpdateSchema
from schemas.tarefa_schema import TarefaCreateSchema, TarefaUpdateSchema

# Importa a instância do banco de dados e as ferramentas de segurança
from extensions import db
from security import get_usuario_atual, Permissions

logger = logging.getLogger(__name__)


def register_routes(app):
    """Registra todas as rotas da API na instância do app Flask."""

    # --- ROTAS DE AUTENTICAÇÃO (PÚBLICAS) ---
    @app.route("/api/auth/register", methods=['POST'])
    def register_user():
        dados = request.get_json()
        if not dados or not all(k in dados for k in ['email', 'senha', 'nome_completo']):
            abort(400, description="Nome completo, email e senha são obrigatórios.")

        session = db.get_session()
        try:
            if session.query(Usuario).filter_by(email=dados['email']).first():
                abort(409, description="Email já cadastrado.")

            novo_usuario = Usuario(
                nome_completo=dados['nome_completo'],
                email=dados['email'],
                cargo=dados.get('cargo', 'Usuário'),
                role=dados.get('role', 'Membro')
            )
            novo_usuario.definir_senha(dados['senha'])
            
            session.add(novo_usuario)
            session.commit()
            
            logger.info(f"Novo usuário registrado: {dados['email']}")
            return jsonify(novo_usuario.para_dicionario()), 201
        finally:
            session.close()

    @app.route("/api/auth/login", methods=['POST'])
    def login_user():
        dados = request.get_json()
        if not dados or not all(k in dados for k in ['email', 'senha']):
            abort(400, description="Email e senha são obrigatórios.")

        session = db.get_session()
        try:
            usuario = session.query(Usuario).filter_by(email=dados['email']).first()
            
            if usuario and usuario.verificar_senha(dados['senha']):
                identity = str(usuario.id_usuario)
                access_token = create_access_token(identity=identity)
                logger.info(f"Login bem-sucedido para o usuário: {dados['email']}")
                return jsonify(access_token=access_token)
            
            logger.warning(f"Tentativa de login falhou para o email: {dados['email']}")
            abort(401, description="Credenciais inválidas.")
        finally:
            session.close()

    @app.route("/api/auth/me", methods=['GET'])
    @jwt_required()
    def get_current_user_data():
        usuario_atual = get_usuario_atual()
        if not usuario_atual:
            abort(401, description="Usuário não encontrado a partir do token.")
        return jsonify(usuario_atual.para_dicionario())

    # --- ROTAS DE DADOS AUXILIARES (PROTEGIDAS) ---
    @app.route("/api/usuarios", methods=['GET'])
    @jwt_required()
    def get_usuarios():
        session = db.get_session()
        try:
            usuarios = session.query(Usuario).all()
            return jsonify([u.para_dicionario() for u in usuarios])
        finally:
            session.close()

    @app.route("/api/areas", methods=['GET'])
    @jwt_required()
    def get_areas():
        session = db.get_session()
        try:
            areas = session.query(Area).all()
            return jsonify([a.para_dicionario() for a in areas])
        finally:
            session.close()
     
    @app.route("/api/objetivos", methods=['GET'])
    @jwt_required()
    def get_objetivos():
        session = db.get_session()
        try:
            objetivos = session.query(ObjetivoEstrategico).all()
            return jsonify([obj.para_dicionario() for obj in objetivos])
        finally:
            session.close()        

    # --- ROTA DO ESQUEMA (PROTEGIDA) ---
    @app.route("/api/projetos/schema", methods=['GET'])
    @jwt_required()
    def get_projeto_schema():
        schema = {'form': []}
        
        metadados_form = {
            'nome_projeto': {'label': 'Nome do Projeto', 'type': 'text', 'required': True},
            'descricao': {'label': 'Descrição Detalhada', 'type': 'textarea', 'required': True},
            'numero_topdesk': {'label': 'Chamado (Topdesk)', 'type': 'text', 'required': True},
            'id_responsavel': {'label': 'Responsável', 'type': 'select_api', 'endpoint': '/usuarios', 'option_value': 'id_usuario', 'option_label': 'nome_completo'},
            'id_area_solicitante': {'label': 'Área Solicitante', 'type': 'select_api', 'endpoint': '/areas', 'option_value': 'id_area', 'option_label': 'nome_area'},
            'equipe_ids': {'label': 'Equipe do Projeto', 'type': 'multiselect_api', 'endpoint': '/usuarios', 'option_value': 'id_usuario', 'option_label': 'nome_completo'},
            
            # --- NOVOS CAMPOS ADICIONADOS AO SCHEMA ---
            'objetivo_ids': {'label': 'Objetivos Estratégicos', 'type': 'multiselect_api', 'endpoint': '/objetivos', 'option_value': 'id_objetivo', 'option_label': 'nome_objetivo'},
            'custo_estimado': {'label': 'Custo Estimado (R$)', 'type': 'number', 'step': '0.01', 'placeholder': 'Ex: 50000.00'},
            
            'prioridade': {'label': 'Prioridade', 'type': 'select', 'options': ["Baixa", "Média", "Alta", "Crítica"]},
            'complexidade': {'label': 'Complexidade', 'type': 'select', 'options': ["Baixa", "Média", "Alta"]},
            'risco': {'label': 'Risco Associado', 'type': 'select', 'options': ["Baixo", "Médio", "Alto"]},
            'link_documentacao': {'label': 'Link da Documentação', 'type': 'url'},
            'data_inicio_prevista': {'label': 'Início Previsto', 'type': 'date'},
            'data_fim_prevista': {'label': 'Fim Previsto', 'type': 'date'},
        }

        for name, meta in metadados_form.items():
            field_info = meta.copy()
            field_info['name'] = name
            schema['form'].append(field_info)
                
        return jsonify(schema)

    # --- ROTAS DE PROJETO (PROTEGIDAS E REATORADAS) ---
    @app.route("/api/projetos", methods=['GET'])
    @jwt_required()
    def get_todos_projetos():
        usuario_atual = get_usuario_atual()
        try:
            with ProjetoService() as service:
                projetos_dict = service.get_all_for_user(usuario_atual)
            return jsonify(projetos_dict)
        except Exception as e:
            logger.error(f"Erro em GET /api/projetos: {e}", exc_info=True)
            abort(500)

    @app.route("/api/projetos/<int:id_projeto>", methods=['GET'])
    @jwt_required()
    def get_projeto_por_id_route(id_projeto):
        usuario_atual = get_usuario_atual()
        session = db.get_session()
        try:
            projeto_obj = session.query(Projeto).get(id_projeto)
            if not projeto_obj:
                abort(404, description="Projeto não encontrado.")
            if not Permissions.pode_ver_projeto(usuario_atual, projeto_obj):
                abort(403, description="Você não tem permissão para ver este projeto.")
            return jsonify(projeto_obj.para_dicionario())
        finally:
            session.close()

    @app.route("/api/projetos", methods=['POST'])
    @jwt_required()
    def criar_novo_projeto():
        usuario_atual = get_usuario_atual()
        if not Permissions.pode_criar_projeto(usuario_atual):
            abort(403, description="Você não tem permissão para criar projetos.")

        dados_brutos = request.get_json()
        if not dados_brutos:
            abort(400, description="Corpo da requisição não pode ser vazio.")
        try:
            dados_validados = ProjetoCreateSchema(**dados_brutos)
            with ProjetoService() as service:
                projeto_final_dict = service.criar_projeto(
                    dados_validados.dict(), 
                    usuario_atual
                )
            return jsonify(projeto_final_dict), 201
        except ValidationError as e:
            return jsonify({"detail": e.errors()}), 422
        except Exception as e:
            logger.error(f"Erro inesperado ao criar projeto: {e}", exc_info=True)
            abort(500)

    @app.route("/api/projetos/<int:id_projeto>", methods=['PUT'])
    @jwt_required()
    def editar_projeto_route(id_projeto):
        logger.info(f"Requisição recebida: PUT /api/projetos/{id_projeto}")
        usuario_atual = get_usuario_atual()
        
        try:
            dados_brutos = request.get_json()
            if not dados_brutos:
                abort(400, description="Corpo da requisição não pode ser vazio.")
            
            dados_validados = ProjetoUpdateSchema(**dados_brutos)
            dados_para_atualizar = dados_validados.dict(exclude_unset=True)
            if not dados_para_atualizar:
                abort(400, description="Nenhum dado válido para atualização foi fornecido.")

            with ProjetoService() as service:
                projeto_obj = service.session.query(Projeto).get(id_projeto)
                if not projeto_obj:
                    abort(404, description="Projeto não encontrado.")
                
                if not Permissions.pode_editar_projeto(usuario_atual, projeto_obj):
                    logger.warning(f"Usuário ID {usuario_atual.id_usuario} ({usuario_atual.role}) tentou editar projeto ID {id_projeto} sem permissão.")
                    abort(403, description="Você não tem permissão para editar este projeto.")

                projeto_atualizado_dict = service.editar_projeto(id_projeto, dados_para_atualizar)
            
            return jsonify(projeto_atualizado_dict)

        except ValidationError as e:
            logger.warning(f"Erro de validação ao editar projeto {id_projeto}: {e.errors()}")
            return jsonify({"detail": e.errors()}), 422
        except ValueError as e:
            logger.warning(f"Erro de valor ao editar projeto {id_projeto}: {e}")
            abort(404, description=str(e))
        except Exception as e:
            logger.error(f"Erro inesperado ao editar projeto {id_projeto}: {e}", exc_info=True)
            abort(500)

    @app.route("/api/projetos/<int:id_projeto>/status", methods=['PUT'])
    @jwt_required()
    def atualizar_status_projeto_route(id_projeto):
        usuario_atual = get_usuario_atual()
        
        try:
            dados_brutos = request.get_json()
            if not dados_brutos:
                abort(400, description="Corpo da requisição não pode ser vazio.")
            
            dados_validados = StatusUpdateSchema(**dados_brutos)

            with ProjetoService() as service:
                projeto_obj = service.session.query(Projeto).get(id_projeto)
                if not projeto_obj:
                    abort(404, description="Projeto não encontrado.")

                if not Permissions.pode_mudar_status(usuario_atual, projeto_obj):
                    abort(403, description="Você não tem permissão para mudar o status deste projeto.")

                projeto_atualizado_dict = service.atualizar_status(
                    id_projeto=id_projeto,
                    novo_status=dados_validados.status,
                    id_usuario=usuario_atual.id_usuario,
                    observacao=dados_validados.observacao
                )
            return jsonify(projeto_atualizado_dict)
        except ValidationError as e:
            return jsonify({"detail": e.errors()}), 422
        except ValueError as e: 
            abort(400, description=str(e))
        except Exception as e:
            logger.error(f"Erro inesperado ao atualizar status: {e}", exc_info=True)
            abort(500)

    @app.route("/api/projetos/<int:id_projeto>", methods=['DELETE'])
    @jwt_required()
    def deletar_projeto_route(id_projeto):
        usuario_atual = get_usuario_atual()
        
        try:
            with ProjetoService() as service:
                projeto_obj = service.session.query(Projeto).get(id_projeto)
                if not projeto_obj:
                    abort(404, description="Projeto não encontrado.")

                if not Permissions.pode_deletar_projeto(usuario_atual, projeto_obj):
                    abort(403, description="Você não tem permissão para deletar este projeto.")

                service.deletar_projeto(id_projeto)
                
            return '', 204
        except ValueError as e:
            abort(404, description=str(e))
        except Exception as e:
            logger.error(f"Erro inesperado ao deletar projeto {id_projeto}: {e}", exc_info=True)
            abort(500)

    # --- ROTAS DE HOMOLOGAÇÃO ---
    @app.route("/api/projetos/<int:id_projeto>/homologacao/iniciar", methods=['POST'])
    @jwt_required()
    def iniciar_ciclo_homologacao_route(id_projeto):
        usuario_atual = get_usuario_atual()

        try:
            dados_brutos = request.get_json()
            if not dados_brutos:
                abort(400, description="Corpo da requisição não pode ser vazio.")
            
            dados_validados = HomologacaoStartSchema(**dados_brutos)
            
            with HomologacaoService() as service:
                projeto_obj = service.session.query(Projeto).get(id_projeto)
                if not projeto_obj:
                    abort(404, description="Projeto não encontrado.")
                if not Permissions.pode_mudar_status(usuario_atual, projeto_obj):
                    abort(403, description="Você não tem permissão para iniciar a homologação.")
                
                projeto_atualizado = service.iniciar_ciclo(id_projeto, dados_validados.dict())
            
            return jsonify(projeto_atualizado)
        except (ValidationError, ValueError) as e:
            abort(400, description=str(e))
        except Exception as e:
            logger.error(f"Erro ao iniciar ciclo de homologação: {e}", exc_info=True)
            abort(500)

    @app.route("/api/projetos/<int:id_projeto>/homologacao/finalizar", methods=['POST'])
    @jwt_required()
    def finalizar_ciclo_homologacao_route(id_projeto):
        """
        Finaliza o ciclo de homologação mais recente de um projeto.
        A lógica de negócio no serviço determinará o próximo status do projeto.
        """
        logger.info(f"Requisição recebida: POST /api/projetos/{id_projeto}/homologacao/finalizar")
        usuario_atual = get_usuario_atual()
        session = db.get_session()

        try:
            # 1. Busca o objeto do projeto para verificação de permissão
            projeto_obj = session.query(Projeto).get(id_projeto)
            if not projeto_obj:
                abort(404, description="Projeto não encontrado.")

            # 2. VERIFICAÇÃO DE PERMISSÃO
            if not Permissions.pode_mudar_status(usuario_atual, projeto_obj):
                logger.warning(f"Usuário ID {usuario_atual.id_usuario} tentou finalizar homologação do projeto ID {id_projeto} sem permissão.")
                abort(403, description="Você não tem permissão para finalizar a homologação deste projeto.")

            # 3. Valida os dados de entrada
            dados_brutos = request.get_json()
            if not dados_brutos:
                abort(400, description="Corpo da requisição não pode ser vazio.")
            
            # Adiciona o ID do usuário logado aos dados antes de validar
            dados_brutos['id_usuario'] = usuario_atual.id_usuario
            dados_validados = HomologacaoEndSchema(**dados_brutos)
            
            # 4. Chama o serviço de negócio (sem passar o status alvo)
            with HomologacaoService() as service:
                resposta_servico = service.finalizar_ciclo(id_projeto, dados_validados.dict())
            
            return jsonify(resposta_servico)
            
        except ValidationError as e:
            return jsonify({"detail": e.errors()}), 422
        except ValueError as e:
            abort(400, description=str(e))
        except Exception as e:
            logger.error(f"Erro ao finalizar ciclo de homologação para o projeto {id_projeto}: {e}", exc_info=True)
            abort(500)
        finally:
            session.close()

    # --- ROTAS DE ADMINISTRAÇÃO DE USUÁRIOS ---
    @app.route("/api/admin/users/<int:id_usuario>/role", methods=['PUT'])
    @jwt_required()
    def update_user_role(id_usuario):
        usuario_atual = get_usuario_atual()
        
        if not Permissions.pode_editar_roles(usuario_atual):
            abort(403, description="Você não tem permissão para editar papéis de usuários.")

        dados_brutos = request.get_json()
        if not dados_brutos:
            abort(400)
        
        try:
            dados_validados = UserRoleUpdateSchema(**dados_brutos)
            
            with UsuarioService() as service:
                usuario_atualizado_dict = service.atualizar_role_usuario(
                    id_usuario=id_usuario,
                    novo_role=dados_validados.role
                )
            
            return jsonify(usuario_atualizado_dict)

        except ValidationError as e:
            return jsonify({"detail": e.errors()}), 422
        except ValueError as e:
            abort(404, description=str(e))
        except Exception as e:
            logger.error(f"Erro ao atualizar role do usuário {id_usuario}: {e}", exc_info=True)
            abort(500)

    # --- ROTA PARA ATUALIZAR O PERFIL DO PRÓPRIO USUÁRIO ---
    @app.route("/api/profile", methods=['PUT'])
    @jwt_required()
    def update_current_user_profile():
        id_usuario_logado = int(get_jwt_identity())
        
        dados_brutos = request.get_json()
        if not dados_brutos:
            abort(400)
        
        try:
            dados_validados = ProfileUpdateSchema(**dados_brutos)
            dados_para_atualizar = dados_validados.dict(exclude_unset=True)

            if not dados_para_atualizar:
                abort(400, description="Nenhum dado válido para atualização foi fornecido.")

            with UsuarioService() as service:
                usuario_atualizado_dict = service.atualizar_perfil(id_usuario_logado, dados_para_atualizar)
            
            return jsonify(usuario_atualizado_dict)

        except ValidationError as e:
            return jsonify({"detail": e.errors()}), 422
        except ValueError as e:
            abort(404, description=str(e))
        except Exception as e:
            logger.error(f"Erro ao atualizar perfil do usuário {id_usuario_logado}: {e}", exc_info=True)
            abort(500)
            
    # Em routes.py

    # --- ROTA PARA O DASHBOARD DE PORTFÓLIO (CORRIGIDA) ---
    @app.route("/api/relatorios/portfolio", methods=['GET'])
    @jwt_required()
    def get_relatorio_portfolio_route():
        """
        Retorna os dados agregados para a visão de portfólio.
        """
        usuario_atual = get_usuario_atual()
        try:
            # --- CORREÇÃO AQUI: Usa ProjetoService ---
            with ProjetoService() as service:
                portfolio_data = service.get_relatorio_portfolio(usuario_atual)
            return jsonify(portfolio_data)
        except Exception as e:
            logger.error(f"Erro em GET /api/relatorios/portfolio: {e}", exc_info=True)
            abort(500)        
            
    @app.route("/api/projetos/<int:id_projeto>/tarefas", methods=['POST'])
    @jwt_required()
    def criar_tarefa_route(id_projeto):
        """
        Cria uma nova tarefa associada a um projeto específico.
        """
        logger.info(f"Requisição recebida: POST /api/projetos/{id_projeto}/tarefas")
        usuario_atual = get_usuario_atual()
        session = db.get_session()
        
        try:
            # 1. Busca o objeto do projeto para verificação de permissão
            projeto_obj = session.query(Projeto).get(id_projeto)
            if not projeto_obj:
                abort(404, description="Projeto não encontrado.")

            # 2. VERIFICAÇÃO DE PERMISSÃO
            # Reutilizamos a regra 'pode_editar_projeto', pois quem pode editar
            # o projeto também pode adicionar tarefas a ele.
            if not Permissions.pode_editar_projeto(usuario_atual, projeto_obj):
                logger.warning(f"Usuário ID {usuario_atual.id_usuario} tentou criar tarefa no projeto ID {id_projeto} sem permissão.")
                abort(403, description="Você não tem permissão para adicionar tarefas a este projeto.")

            # 3. Valida os dados de entrada
            dados_brutos = request.get_json()
            if not dados_brutos:
                abort(400, description="Corpo da requisição não pode ser vazio.")
            
            dados_validados = TarefaCreateSchema(**dados_brutos)
            
            # 4. Chama o serviço de negócio
            with TarefaService() as service:
                nova_tarefa_dict = service.criar_tarefa(id_projeto, dados_validados.dict())
            
            # Retorna a tarefa recém-criada com o status 201 (Created)
            return jsonify(nova_tarefa_dict), 201

        except ValidationError as e:
            return jsonify({"detail": e.errors()}), 422
        except ValueError as e:
            abort(400, description=str(e))
        except Exception as e:
            logger.error(f"Erro ao criar tarefa para o projeto {id_projeto}: {e}", exc_info=True)
            abort(500)
        finally:
            session.close()        
            
    # --- NOVA ROTA PARA EDITAR TAREFA ---
    @app.route("/api/tarefas/<int:id_tarefa>", methods=['PUT'])
    @jwt_required()
    def atualizar_tarefa_route(id_tarefa):
        usuario_atual = get_usuario_atual()
        # TODO: Adicionar verificação de permissão (usuário pode editar tarefas neste projeto?)
        
        dados_brutos = request.get_json()
        if not dados_brutos:
            abort(400)
        
        try:
            dados_validados = TarefaUpdateSchema(**dados_brutos)
            dados_para_atualizar = dados_validados.dict(exclude_unset=True)

            if not dados_para_atualizar:
                abort(400, description="Nenhum dado válido para atualização foi fornecido.")

            with TarefaService() as service:
                tarefa_atualizada_dict = service.atualizar_tarefa(id_tarefa, dados_para_atualizar)
            
            return jsonify(tarefa_atualizada_dict)

        except ValidationError as e:
            return jsonify({"detail": e.errors()}), 422
        except ValueError as e:
            abort(404, description=str(e))
        except Exception as e:
            logger.error(f"Erro ao atualizar tarefa {id_tarefa}: {e}", exc_info=True)
            abort(500)        
            
    # --- NOVA ROTA PARA DELETAR TAREFA ---
    @app.route("/api/tarefas/<int:id_tarefa>", methods=['DELETE'])
    @jwt_required()
    def deletar_tarefa_route(id_tarefa):
        usuario_atual = get_usuario_atual()
        # TODO: Adicionar verificação de permissão (usuário pode deletar tarefas neste projeto?)
        
        logger.info(f"Requisição recebida: DELETE /api/tarefas/{id_tarefa}")
        try:
            with TarefaService() as service:
                sucesso = service.deletar_tarefa(id_tarefa)
            
            if not sucesso:
                # Este caso é redundante se o serviço lança ValueError, mas é uma segurança extra
                abort(404, description=f"Tarefa com ID {id_tarefa} não encontrada.")

            # Retorna uma resposta vazia com status 204 (No Content)
            return '', 204

        except ValueError as e:
            abort(404, description=str(e))
        except Exception as e:
            logger.error(f"Erro ao deletar tarefa {id_tarefa}: {e}", exc_info=True)
            abort(500)        
            
    # Em routes.py, dentro da função register_routes(app)

    # ... (rota /api/auth/me existente) ...

    # --- NOVA ROTA PARA "MINHAS TAREFAS" ---
    @app.route("/api/me/tarefas", methods=['GET'])
    @jwt_required()
    def get_minhas_tarefas_route():
        """Retorna a lista de tarefas abertas para o usuário logado."""
        usuario_atual = get_usuario_atual()
        if not usuario_atual:
            abort(401)

        try:
            with TarefaService() as service:
                tarefas_dict = service.get_tarefas_por_usuario(usuario_atual.id_usuario)
            return jsonify(tarefas_dict)
        except Exception as e:
            logger.error(f"Erro ao buscar tarefas para o usuário {usuario_atual.id_usuario}: {e}", exc_info=True)
            abort(500)        
            
    # --- NOVA ROTA PARA "MEUS PROJETOS" ---
    @app.route("/api/me/projetos", methods=['GET'])
    @jwt_required()
    def get_meus_projetos_route():
        """Retorna a lista de projetos ativos para o usuário logado."""
        usuario_atual = get_usuario_atual()
        if not usuario_atual:
            abort(401)

        try:
            with ProjetoService() as service:
                projetos_dict = service.get_projetos_por_responsavel(usuario_atual.id_usuario)
            return jsonify(projetos_dict)
        except Exception as e:
            logger.error(f"Erro ao buscar projetos para o usuário {usuario_atual.id_usuario}: {e}", exc_info=True)
            abort(500)        

    @app.route("/api/homologacoes/<int:id_homologacao>/upload-zip", methods=['POST'])
    @jwt_required()
    def upload_relatorio_homologacao_route(id_homologacao):
        usuario_atual = get_usuario_atual()
        # TODO: Adicionar verificação de permissão

        if 'reportFile' not in request.files:
            abort(400, description="Nenhum arquivo enviado.")
        
        file = request.files['reportFile']
        if file.filename == '' or not file.filename.endswith('.zip'):
            abort(400, description="Nenhum arquivo .zip selecionado.")

        try:
            with HomologacaoService() as service:
                # --- CHAMADA ÚNICA E SIMPLIFICADA ---
                ciclo_atualizado_dict = service.processar_upload_de_relatorio(
                    id_homologacao=id_homologacao,
                    file_stream=file,
                    upload_folder=current_app.config['UPLOAD_FOLDER']
                )
            return jsonify(ciclo_atualizado_dict)
        except ValueError as e:
            abort(400, description=str(e))
        except Exception as e:
            logger.error(f"Erro no upload para o ciclo {id_homologacao}: {e}", exc_info=True)
            abort(500)
          
    @app.route("/api/homologacoes/<int:id_homologacao>/processar-relatorio", methods=['POST'])
    @jwt_required()
    def processar_relatorio_route(id_homologacao):
        usuario_atual = get_usuario_atual()
        # TODO: Adicionar verificação de permissão

        try:
            with HomologacaoService() as service:
                ciclo_atualizado_dict = service.processar_relatorio(id_homologacao)
            
            return jsonify(ciclo_atualizado_dict)
        except ValueError as e:
            abort(400, description=str(e))
        except Exception as e:
            logger.error(f"Erro ao processar relatório para homologação {id_homologacao}: {e}", exc_info=True)
            abort(500)
            
    # --- NOVA ROTA PARA OBTER TESTES DE UM CICLO ---
    @app.route("/api/homologacoes/<int:id_homologacao>/testes", methods=['GET'])
    @jwt_required()
    def get_testes_do_ciclo_route(id_homologacao):
        """
        Retorna a lista de testes executados para um ciclo de homologação específico.
        """
        logger.info(f"Requisição recebida: GET /api/homologacoes/{id_homologacao}/testes")
        usuario_atual = get_usuario_atual()
        
        # TODO: Adicionar uma verificação de permissão mais granular.
        # Por exemplo, buscar o ciclo, pegar o projeto dele e verificar
        # se o usuário pode ver aquele projeto.
        # if not Permissions.pode_ver_projeto(...): abort(403)

        try:
            with HomologacaoService() as service:
                testes_dict = service.get_testes_por_ciclo(id_homologacao)
            
            return jsonify(testes_dict)

        except ValueError as e:
            # Captura o erro se o ciclo de homologação não for encontrado
            abort(404, description=str(e))
        except Exception as e:
            logger.error(f"Erro ao buscar testes para o ciclo {id_homologacao}: {e}", exc_info=True)
            abort(500)        
          
    # --- NOVA ROTA PARA O DASHBOARD DE QA ---
    @app.route("/api/relatorios/qa", methods=['GET'])
    @jwt_required()
    def get_relatorio_qa_route():
        """Retorna os dados agregados para o dashboard de Qualidade."""
        usuario_atual = get_usuario_atual()
        # Apenas Admins e Gerentes podem ver os relatórios completos de QA
        if not Permissions.pode_ver_relatorios_completos(usuario_atual):
            abort(403, description="Você não tem permissão para acessar os relatórios de qualidade.")

        try:
            with HomologacaoService() as service:
                qa_data = service.get_relatorio_qa_geral()
            return jsonify(qa_data)
        except Exception as e:
            logger.error(f"Erro em GET /api/relatorios/qa: {e}", exc_info=True)
            abort(500)        
