import { api } from './apiService.js';
import { showToast } from './toast.js';
import { renderProjectDetails } from './projectRenderer.js';

// --- LÓGICA DE CONTROLE DAS ABAS ---
function initializeTabs() {
    const tabsContainer = document.querySelector('.tabs-container');
    if (!tabsContainer) return;

    const tabLinksContainer = tabsContainer.querySelector('.tabs-nav');
    if (!tabLinksContainer) return;

    // Remove qualquer listener antigo para evitar duplicidade
    if (tabLinksContainer.eventListener) {
        tabLinksContainer.removeEventListener('click', tabLinksContainer.eventListener);
    }

    tabLinksContainer.eventListener = (event) => {
        const clickedLink = event.target.closest('.tab-link');
        if (!clickedLink) return;

        const tabId = clickedLink.dataset.tab;
        const tabPanesContainer = tabsContainer.querySelector('.tabs-content');

        tabLinksContainer.querySelectorAll('.tab-link').forEach(l => l.classList.remove('active'));
        tabPanesContainer.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

        clickedLink.classList.add('active');
        const targetPane = document.getElementById(tabId);
        if (targetPane) {
            targetPane.classList.add('active');
        }
    };
    tabLinksContainer.addEventListener('click', tabLinksContainer.eventListener);
}

/**
 * Lida com o clique em um botão de mudança de status.
 * Orquestra qual modal mostrar e qual chamada de API fazer com base no contexto.
 * @param {number} id - O ID do projeto a ser atualizado.
 * @param {string} novoStatus - O novo status para o qual o projeto será movido.
 * @param {Event} event - O objeto do evento de clique.
 * @param {object} dependencies - As dependências globais (modal, navigate).
 */
async function handleStatusChange(id, novoStatus, event, dependencies) {
    const clickedButton = event.currentTarget;
    const actionButtonsContainer = document.getElementById('action-buttons');
    const statusAnterior = document.getElementById('status-atual-container').querySelector('.status-tag').textContent.trim();

    // --- ROTEADOR DE FLUXO ---

    if (novoStatus === 'Em Homologação') {
        // --- FLUXO DE INÍCIO DE HOMOLOGAÇÃO ---
        try {
            const usuarios = await api.getGeneric('/usuarios');
            const optionsHtml = usuarios.map(u => `<option value="${u.id_usuario}">${u.nome_completo}</option>`).join('');
            const modalHtmlContent = `<p>Preencha os detalhes para iniciar o novo ciclo de homologação.</p><div class="form-group" style="text-align: left; margin-top: 1rem;"><label for="versao_testada">Versão a ser Testada</label><input type="text" id="versao_testada" class="modal-input" required placeholder="Ex: v1.2.4"></div><div class="form-group" style="text-align: left;"><label for="tipo_teste">Tipo de Teste</label><select id="tipo_teste" class="modal-input" required><option value="Manual">Manual</option><option value="Automatizado - API">Automatizado - API</option><option value="Automatizado - UI">Automatizado - UI</option><option value="Performance">Performance</option></select></div><div class="form-group" style="text-align: left;"><label for="ambiente">Ambiente de Testes</label><input type="text" id="ambiente" class="modal-input" required placeholder="Ex: UAT, Staging"></div><div class="form-group" style="text-align: left;"><label for="id_responsavel_teste">Responsável pelo Teste</label><select id="id_responsavel_teste" class="modal-input" required><option value="">Selecione um usuário...</option>${optionsHtml}</select></div>`;
            
            const { confirmed, modalContainer } = await dependencies.modal.show({ title: 'Iniciar Ciclo de Homologação', htmlContent: modalHtmlContent, confirmText: 'Iniciar Ciclo' });
            if (!confirmed) return;

            const data = { versao_testada: modalContainer.querySelector('#versao_testada').value, tipo_teste: modalContainer.querySelector('#tipo_teste').value, ambiente: modalContainer.querySelector('#ambiente').value, id_responsavel_teste: parseInt(modalContainer.querySelector('#id_responsavel_teste').value) };
            if (!data.versao_testada || !data.ambiente || !data.id_responsavel_teste) { showToast("Todos os campos são obrigatórios.", "error"); return; }
            
            actionButtonsContainer.querySelectorAll('.action-btn').forEach(btn => btn.disabled = true);
            clickedButton.classList.add('loading');
            await api.iniciarCicloHomologacao(id, data);
            showToast(`Ciclo de homologação iniciado!`, 'success');
            setTimeout(() => { window.location.reload(); }, 1500);
        } catch (error) {
            showToast(`Erro: ${error.message}`, 'error');
            actionButtonsContainer.querySelectorAll('.action-btn').forEach(btn => { btn.disabled = false; btn.classList.remove('loading'); });
        }

    } else if (statusAnterior.includes('Em Homologação')) {
        // --- FLUXO DE FIM DE HOMOLOGAÇÃO (REATORADO) ---
        const modalHtmlContent = `
            <p>Finalize o ciclo registrando o resultado.</p>
            <div class="form-group" style="text-align: left; margin-top: 1rem;">
                <label for="resultado">Resultado Final</label>
                <select id="resultado" class="modal-input" required>
                    <option value="">Selecione...</option>
                    <option value="Aprovado">Aprovado</option>
                    <option value="Reprovado">Reprovado</option>
                    <option value="Aprovado com Ressalvas">Aprovado com Ressalvas</option>
                </select>
            </div>
            <p style="margin-top: 1.5rem; text-align: left; font-weight: 600;">Como deseja evidenciar o resultado?</p>
            <div class="input-type-toggle">
                <button class="toggle-btn active" data-type="manual">Inserir Métricas Manuais</button>
                <button class="toggle-btn" data-type="upload">Anexar Relatório (.zip)</button>
            </div>
            <hr style="margin: 1rem 0; border-color: var(--border-color);">
            
            <div id="manual-input-section">
                <div class="metrics-grid">
                    <div class="form-group"><label for="total_testes">Total</label><input type="number" id="total_testes" class="modal-input" min="0"></div>
                    <div class="form-group"><label for="testes_aprovados">Aprovados</label><input type="number" id="testes_aprovados" class="modal-input" min="0"></div>
                    <div class="form-group"><label for="testes_reprovados">Reprovados</label><input type="number" id="testes_reprovados" class="modal-input" min="0"></div>
                    <div class="form-group"><label for="testes_bloqueados">Bloqueados</label><input type="number" id="testes_bloqueados" class="modal-input" min="0"></div>
                </div>
            </div>
            <div id="upload-section" style="display: none;">
                <div class="form-group" style="text-align: left;">
                    <label for="reportFile">Relatório de Testes (.zip)</label>
                    <input type="file" id="reportFile" class="modal-input" accept=".zip">
                </div>
            </div>
            <div class="form-group" style="text-align: left; margin-top: 1rem;">
                <label for="observacoes">Observações Finais</label>
                <textarea id="observacoes" class="modal-textarea" rows="3"></textarea>
            </div>
        `;

        const modalPromise = dependencies.modal.show({ title: 'Finalizar Ciclo de Homologação', htmlContent: modalHtmlContent, confirmText: 'Finalizar Ciclo' });

        // Adiciona a lógica do toggle após o modal ser criado
        setTimeout(() => {
            const modalNode = document.getElementById('modal-container');
            if (!modalNode) return;
            const manualSection = modalNode.querySelector('#manual-input-section');
            const uploadSection = modalNode.querySelector('#upload-section');
            modalNode.querySelectorAll('.toggle-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    modalNode.querySelector('.toggle-btn.active')?.classList.remove('active');
                    btn.classList.add('active');
                    if (manualSection) manualSection.style.display = btn.dataset.type === 'manual' ? 'block' : 'none';
                    if (uploadSection) uploadSection.style.display = btn.dataset.type === 'upload' ? 'block' : 'none';
                });
            });
        }, 0);

        const { confirmed, modalContainer } = await modalPromise;
        if (!confirmed) return;

        actionButtonsContainer.querySelectorAll('.action-btn').forEach(btn => btn.disabled = true);
        clickedButton.classList.add('loading');

        try {
            const dadosParaFinalizar = {
                resultado: modalContainer.querySelector('#resultado').value,
                observacoes: modalContainer.querySelector('#observacoes').value,
                total_testes: modalContainer.querySelector('#total_testes').value,
                testes_aprovados: modalContainer.querySelector('#testes_aprovados').value,
                testes_reprovados: modalContainer.querySelector('#testes_reprovados').value,
                testes_bloqueados: modalContainer.querySelector('#testes_bloqueados').value
            };
            
            if (!dadosParaFinalizar.resultado) {
                throw new Error("O campo 'Resultado Final' é obrigatório.");
            }
            
            for (const key of ['total_testes', 'testes_aprovados', 'testes_reprovados', 'testes_bloqueados']) { dadosParaFinalizar[key] = dadosParaFinalizar[key] ? parseInt(dadosParaFinalizar[key]) : null; }
            
            const response = await api.finalizarCicloHomologacao(id, dadosParaFinalizar);
            const idHomologacaoFinalizado = response.id_homologacao_finalizado;
            
            const reportFile = modalContainer.querySelector('#reportFile').files[0];
            if (reportFile) {
                showToast('Enviando e processando relatório...', 'info');
                const formData = new FormData();
                formData.append('reportFile', reportFile);
                await api.uploadRelatorio(idHomologacaoFinalizado, formData);
            }

            showToast('Ciclo de homologação finalizado com sucesso!', 'success');
            setTimeout(() => { window.location.reload(); }, 1500);
        } catch (error) {
            showToast(`Erro ao finalizar ciclo: ${error.message}`, 'error', 8000);
            actionButtonsContainer.querySelectorAll('.action-btn').forEach(btn => { btn.disabled = false; btn.classList.remove('loading'); });
        }

    } else {
        // --- FLUXO PADRÃO (COM OBSERVAÇÃO) ---
        const modalHtmlContent = `<p>Você tem certeza que deseja mover o projeto para o status <strong>${novoStatus}</strong>?</p><div class="form-group" style="text-align: left; margin-top: 1rem;"><label for="status-observation">Adicionar observação (opcional):</label><textarea id="status-observation" class="modal-textarea" rows="3"></textarea></div>`;
        const { confirmed, modalContainer } = await dependencies.modal.show({ title: `Confirmar Mudança para "${novoStatus}"`, htmlContent: modalHtmlContent, confirmText: 'Sim, Mudar Status' });
        if (!confirmed) return;
        const observacao = modalContainer.querySelector('#status-observation').value;
        
        actionButtonsContainer.querySelectorAll('.action-btn').forEach(btn => btn.disabled = true);
        clickedButton.classList.add('loading');
        try {
            await api.updateStatusProjeto(id, { status: novoStatus, observacao: observacao });
            showToast(`Operação realizada com sucesso!`, 'success');
            setTimeout(() => { window.location.reload(); }, 1500);
        } catch (error) {
            showToast(`Erro: ${error.message}`, 'error');
            actionButtonsContainer.querySelectorAll('.action-btn').forEach(btn => { btn.disabled = false; btn.classList.remove('loading'); });
        }
    }
}

async function handleDeleteProject(id, nome, dependencies) {
    const { confirmed } = await dependencies.modal.show({ title: 'Confirmar Exclusão', message: `Excluir permanentemente o projeto "${nome}"?`, confirmText: 'Sim, Excluir', cancelText: 'Cancelar' });
    if (!confirmed) { showToast('Exclusão cancelada.', 'info'); return; }
    try {
        await api.deleteProjeto(id);
        showToast('Projeto excluído com sucesso!', 'success');
        setTimeout(() => { dependencies.navigate('index.html'); }, 1500);
    } catch (error) {
        showToast(`Erro ao excluir projeto: ${error.message}`, 'error');
    }
}

async function handleNewTask(idProjeto, dependencies) {
    let optionsHtml = '<option value="">Ninguém</option>';
    try {
        const usuarios = await api.getGeneric('/usuarios');
        optionsHtml += usuarios.map(u => `<option value="${u.id_usuario}">${u.nome_completo}</option>`).join('');
    } catch (error) { showToast("Erro ao carregar lista de usuários.", "error"); }
    const modalHtmlContent = `<p>Preencha os detalhes da nova tarefa.</p><div class="form-group" style="text-align: left; margin-top: 1rem;"><label for="nome_tarefa">Nome da Tarefa</label><input type="text" id="nome_tarefa" class="modal-input" required></div><div class="form-group" style="text-align: left;"><label for="data_inicio">Data de Início</label><input type="date" id="data_inicio" class="modal-input" required></div><div class="form-group" style="text-align: left;"><label for="data_fim">Data de Fim</label><input type="date" id="data_fim" class="modal-input" required></div><div class="form-group" style="text-align: left;"><label for="id_responsavel_tarefa">Atribuir a</label><select id="id_responsavel_tarefa" class="modal-input">${optionsHtml}</select></div>`;
    const { confirmed, modalContainer } = await dependencies.modal.show({ title: 'Criar Nova Tarefa', htmlContent: modalHtmlContent, confirmText: 'Salvar Tarefa' });
    if (!confirmed) return;
    const data = { nome_tarefa: modalContainer.querySelector('#nome_tarefa').value, data_inicio: modalContainer.querySelector('#data_inicio').value, data_fim: modalContainer.querySelector('#data_fim').value, id_responsavel_tarefa: modalContainer.querySelector('#id_responsavel_tarefa').value };
    if (!data.nome_tarefa || !data.data_inicio || !data.data_fim) { showToast("Nome e datas da tarefa são obrigatórios.", "error"); return; }
    if (data.id_responsavel_tarefa) { data.id_responsavel_tarefa = parseInt(data.id_responsavel_tarefa); } else { delete data.id_responsavel_tarefa; }
    try {
        await api.createTarefa(idProjeto, data);
        showToast('Tarefa criada com sucesso!', 'success');
        window.location.reload();
    } catch (error) {
        showToast(`Erro ao criar tarefa: ${error.message}`, 'error');
    }
}

async function handleEditTask(task, dependencies) {
    let optionsHtml = '<option value="">Ninguém</option>';
    try {
        const usuarios = await api.getGeneric('/usuarios');
        optionsHtml += usuarios.map(u => { const isSelected = task.responsavel && task.responsavel.id_usuario === u.id_usuario; return `<option value="${u.id_usuario}" ${isSelected ? 'selected' : ''}>${u.nome_completo}</option>`; }).join('');
    } catch (error) { showToast("Erro ao carregar lista de usuários.", "error"); }
    const modalHtmlContent = `<p>Editando a tarefa: <strong>${task.name}</strong></p><div class="form-group" style="text-align: left; margin-top: 1rem;"><label for="task-name">Nome da Tarefa</label><input type="text" id="task-name" class="modal-input" value="${task.name}" required></div><div class="form-group" style="text-align: left;"><label for="task-progress">Progresso (%)</label><input type="number" id="task-progress" class="modal-input" value="${task.progress}" min="0" max="100" required></div><div class="form-group" style="text-align: left;"><label for="id_responsavel_tarefa">Atribuir a</label><select id="id_responsavel_tarefa" class="modal-input">${optionsHtml}</select></div>`;
    const result = await dependencies.modal.show({ title: 'Editar Tarefa', htmlContent: modalHtmlContent, confirmText: 'Salvar Alterações', extraButton: { text: 'Excluir Tarefa', className: 'danger' } });
    if (result.confirmed === 'extra') { const deleteResult = await dependencies.modal.show({ title: 'Confirmar Exclusão', message: `Excluir a tarefa "${task.name}"?`, confirmText: 'Sim, Excluir' }); if (deleteResult.confirmed) { try { await api.deleteTarefa(task.id); showToast('Tarefa excluída!', 'success'); window.location.reload(); } catch (error) { showToast(`Erro: ${error.message}`, 'error'); } } return; }
    if (result.confirmed) { const { modalContainer } = result; const data = { nome_tarefa: modalContainer.querySelector('#task-name').value, progresso: parseInt(modalContainer.querySelector('#task-progress').value), id_responsavel_tarefa: modalContainer.querySelector('#id_responsavel_tarefa').value }; if (data.id_responsavel_tarefa) { data.id_responsavel_tarefa = parseInt(data.id_responsavel_tarefa); } else { data.id_responsavel_tarefa = null; } if (!data.nome_tarefa || isNaN(data.progresso)) { showToast("Preencha os campos corretamente.", "error"); return; } try { await api.updateTarefa(task.id, data); showToast('Tarefa atualizada!', 'success'); window.location.reload(); } catch (error) { showToast(`Erro: ${error.message}`, 'error'); } }
}

// Em frontend/js/projeto.js

// --- NOVO HANDLER PARA VER OS TESTES ---
/**
 * Lida com o clique no botão "Ver Testes" de um ciclo de homologação.
 * Busca os detalhes dos testes e os exibe em um modal.
 * @param {string} idCiclo - O ID do ciclo de homologação.
 * @param {object} dependencies - As dependências globais (modal).
 */
async function handleViewTests(idCiclo, dependencies) {
    showToast("Buscando detalhes dos testes...", "info");
    try {
        // 1. Chama a nova API para buscar os testes do ciclo específico
        const testes = await api.getTestesDoCiclo(idCiclo);
        
        // 2. Gera o HTML da tabela de testes
        const tableHtml = `
            <div class="table-wrapper" style="max-height: 60vh; overflow-y: auto;">
                <table class="data-table compact">
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Teste</th>
                            <th>Feature</th>
                            <th>Severidade</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${testes.length > 0 ? testes.map(teste => `
                            <tr>
                                <td><span class="status-tag" data-status="${teste.status}">${teste.status}</span></td>
                                <td title="${teste.nome_teste}">${teste.nome_teste}</td>
                                <td>${teste.feature || 'N/A'}</td>
                                <td>${teste.severity || 'N/A'}</td>
                            </tr>
                        `).join('') : '<tr><td colspan="4">Nenhum teste detalhado encontrado para este ciclo.</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;

        // 3. Mostra a tabela dentro de um modal
        await dependencies.modal.show({
            title: `Testes Executados no Ciclo #${idCiclo}`,
            htmlContent: tableHtml,
            confirmText: 'Fechar',
            cancelText: '' // Esconde o botão de cancelar para um modal informativo
        });

    } catch (error) {
        showToast(`Erro ao buscar detalhes dos testes: ${error.message}`, 'error');
    }
}

// ... (suas outras funções: handleStatusChange, handleDeleteProject, carregarDetalhesProjeto, etc.) ...

/**
 * Lida com o clique no botão "Criar Tarefa" a partir de um teste reprovado.
 * Abre o modal de nova tarefa, pré-preenchido com os detalhes do bug.
 * @param {object} testeReprovado - O objeto do teste que falhou.
 * @param {number} idProjeto - O ID do projeto ao qual a nova tarefa pertencerá.
 * @param {object} dependencies - As dependências globais (modal, etc.).
 */
async function handleCreateTaskFromFailure(testeReprovado, idProjeto, dependencies) {
    console.log("Criando tarefa a partir do teste reprovado:", testeReprovado);

    // Pré-preenche o nome da tarefa e a descrição com os detalhes do bug
    const nomeTarefaSugerido = `[BUG] Corrigir: ${testeReprovado.nome_teste}`;
    
    // Usamos <textarea> para a descrição, que será enviada no corpo da requisição
    // mas não precisa ser um campo visível no modal. A descrição da tarefa
    // será o resumo do erro.
    const descricaoSugerida = `
        Teste Reprovado: ${testeReprovado.nome_teste}
        Feature: ${testeReprovado.feature || 'N/A'}
        Severidade: ${testeReprovado.severity || 'N/A'}
        ---
        Mensagem de Erro:
        ${testeReprovado.mensagem_erro || 'Nenhuma mensagem de erro detalhada.'}
    `.trim();

    // Busca a lista de usuários para popular o dropdown de responsável
    let optionsHtml = '<option value="">Ninguém</option>';
    try {
        const usuarios = await api.getGeneric('/usuarios');
        optionsHtml += usuarios.map(u => `<option value="${u.id_usuario}">${u.nome_completo}</option>`).join('');
    } catch (error) {
        showToast("Erro ao carregar lista de usuários.", "error");
    }

    // Monta o HTML do formulário para o corpo do modal
    const modalHtmlContent = `
        <p>Uma nova tarefa será criada com base no teste reprovado. Atribua um responsável e defina as datas.</p>
        <div class="form-group" style="text-align: left; margin-top: 1rem;">
            <label for="nome_tarefa">Nome da Tarefa</label>
            <input type="text" id="nome_tarefa" class="modal-input" value="${nomeTarefaSugerido}" required>
        </div>
        <div class="form-group" style="text-align: left;">
            <label for="data_inicio">Data de Início</label>
            <input type="date" id="data_inicio" class="modal-input" required>
        </div>
        <div class="form-group" style="text-align: left;">
            <label for="data_fim">Data de Fim</label>
            <input type="date" id="data_fim" class="modal-input" required>
        </div>
        <div class="form-group" style="text-align: left;">
            <label for="id_responsavel_tarefa">Atribuir a</label>
            <select id="id_responsavel_tarefa" class="modal-input">
                ${optionsHtml}
            </select>
        </div>
    `;

    const { confirmed, modalContainer } = await dependencies.modal.show({
        title: 'Criar Tarefa de Correção',
        htmlContent: modalHtmlContent,
        confirmText: 'Criar Tarefa'
    });

    if (!confirmed) return;

    // Coleta os dados do formulário
    const data = {
        nome_tarefa: modalContainer.querySelector('#nome_tarefa').value,
        data_inicio: modalContainer.querySelector('#data_inicio').value,
        data_fim: modalContainer.querySelector('#data_fim').value,
        id_responsavel_tarefa: modalContainer.querySelector('#id_responsavel_tarefa').value,
        // Adiciona a descrição detalhada aos dados a serem enviados
        descricao: descricaoSugerida 
    };

    if (!data.nome_tarefa || !data.data_inicio || !data.data_fim) {
        showToast("Nome e datas da tarefa são obrigatórios.", "error");
        return;
    }

    if (data.id_responsavel_tarefa) {
        data.id_responsavel_tarefa = parseInt(data.id_responsavel_tarefa);
    } else {
        delete data.id_responsavel_tarefa;
    }

    try {
        await api.createTarefa(idProjeto, data);
        showToast('Tarefa de correção criada com sucesso!', 'success');
        // Recarrega a página para que a nova tarefa apareça no Gráfico de Gantt
        window.location.reload();
    } catch (error) {
        showToast(`Erro ao criar tarefa: ${error.message}`, 'error');
    }
}

/**
 * Busca os dados do projeto, orquestra a renderização e adiciona os listeners de eventos.
 * @param {object} dependencies - O objeto com as dependências globais.
 */
/**
 * Busca os dados do projeto, orquestra a renderização e adiciona os listeners de eventos.
 * @param {object} dependencies - O objeto com as dependências globais.
 */
async function carregarDetalhesProjeto(dependencies) {
    console.log("[projeto.js] Iniciando carregamento dos detalhes do projeto...");
    const urlParams = new URLSearchParams(window.location.search);
    const idDoProjeto = urlParams.get('id');
    const mainTitle = document.getElementById('nome-projeto');
    const mainContent = document.querySelector('.main-content');

    if (!mainContent) {
        console.error("[projeto.js] Container principal '.main-content' não encontrado.");
        return;
    }
    
    mainContent.style.opacity = '0';

    if (!idDoProjeto) {
        if (mainTitle) mainTitle.textContent = 'ID do projeto não fornecido na URL.';
        mainContent.style.opacity = '1';
        return;
    }

    try {
        const projeto = await api.getProjetoPorId(idDoProjeto);
        
        if (projeto) {
            // 1. Cria o objeto com todas as funções de callback (handlers)
            const handlers = {
                onStatusChange: (id, status, event) => handleStatusChange(id, status, event, dependencies),
                onDelete: (id, nome) => handleDeleteProject(id, nome, dependencies),
                onNewTask: () => handleNewTask(projeto.id_projeto, dependencies),
                onTaskClick: (task) => handleEditTask(task, dependencies),
                onCreateTaskFromFailure: (teste) => handleCreateTaskFromFailure(teste, projeto.id_projeto, dependencies)
            };
            
            // 2. Chama a função que constrói todo o HTML da página
            renderProjectDetails(projeto, dependencies, handlers);
            
            // 3. Após a UI ser construída, inicializa as funcionalidades interativas
            initializeTabs();

            // --- LÓGICA DE LISTENERS PÓS-RENDERIZAÇÃO ---

            // Listener para o botão "Nova Tarefa" na aba Gantt
            const newTaskBtn = document.getElementById('new-task-btn');
            if (newTaskBtn) {
                // O renderer já esconde o botão se não houver permissão,
                // mas adicionamos o listener aqui no controlador.
                newTaskBtn.addEventListener('click', () => handlers.onNewTask());
            }

            // Listener para os botões "Ver Testes" na aba Homologação (usando delegação de eventos)
            const homologationContainer = document.getElementById('homologation-history');
            if (homologationContainer) {
                homologationContainer.addEventListener('click', (event) => {
                    const target = event.target.closest('.view-tests-btn');
                    if (target) {
                        const cycleId = target.dataset.cycleId;
                        handleViewTests(cycleId, dependencies);
                    }
                });
            }
        } else {
            if (mainTitle) mainTitle.textContent = `Projeto com ID ${idDoProjeto} não encontrado.`;
        }
    } catch (error) {
        if (mainTitle) mainTitle.textContent = `Erro ao carregar projeto: ${error.message}`;
        console.error("[projeto.js] Erro na chamada da API para getProjetoPorId:", error);
    } finally {
        // Garante que o conteúdo da página seja revelado com uma animação suave
        mainContent.style.transition = 'opacity 0.5s ease-in-out';
        mainContent.style.opacity = '1';
    }
}

// --- PONTO DE ENTRADA ---

export function initializePage(dependencies) {
    console.log("[projeto.js] Inicializando a página de detalhes do projeto...");
    if (!dependencies || !dependencies.modal || !dependencies.navigate || !dependencies.auth) {
        console.error("[projeto.js] Dependências essenciais não foram fornecidas.");
        return;
    }
    carregarDetalhesProjeto(dependencies);
}