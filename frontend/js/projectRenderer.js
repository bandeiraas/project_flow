// Importa as funções "helper" que serão usadas para construir a UI
import { 
    statusIcons, 
    formatarData, 
    calcularDiferencaDias, 
    criarAvatar, 
    addCopyToClipboard, 
    calcularSaudeProjeto,
    renderGraficoLinha,
    renderEmptyState
} from './uiHelpers.js';
import { showToast } from './toast.js';
// Importa a função de renderização do Gantt
import { renderGanttChart } from './gantt-handler.js';
import { api } from './apiService.js';


// --- FUNÇÕES DE RENDERIZAÇÃO DE SUB-COMPONENTES ---

function renderEquipe(equipe) {
    const container = document.getElementById('painel-equipe');
    if (!container) return;
    container.innerHTML = '';
    if (!equipe || equipe.length === 0) {
        container.innerHTML = '<p class="empty-text">Nenhum membro alocado.</p>';
        return;
    }
    equipe.forEach(membro => {
        const avatarHtml = criarAvatar(membro.nome_completo, membro.id_usuario);
        const item = document.createElement('div');
        item.className = 'avatar-item';
        item.innerHTML = `${avatarHtml}<div class="avatar-info"><span>${membro.nome_completo}</span><small>${membro.cargo}</small></div>`;
        container.appendChild(item);
    });
}

function renderTimelineAsList(container, logs) {
    const list = document.createElement('ul');
    list.id = 'cronograma-lista';
    logs.forEach(log => {
        const listItem = document.createElement('li');
        const dataFormatada = new Date(log.data).toLocaleString('pt-BR');
        const itemIcon = statusIcons[log.status] || 'fas fa-question-circle';
        const nomeUsuario = log.usuario?.nome_completo || 'N/D';
        listItem.innerHTML = `<div class="log-header"><i class="${itemIcon}"></i><strong>${log.status}</strong><span class="log-meta">por ${nomeUsuario} em ${dataFormatada}</span></div>${log.observacao ? `<p class="log-observation">${log.observacao}</p>` : ''}`;
        listItem.classList.add('completed-item');
        list.appendChild(listItem);
    });
    container.innerHTML = '';
    container.appendChild(list);
}

function renderTimelineAsTable(container, logs) {
    // 1. Cria o div wrapper que permitirá a rolagem
    const tableWrapper = document.createElement('div');
    tableWrapper.className = 'table-wrapper';

    // 2. Cria a tabela que ficará dentro do wrapper
    const table = document.createElement('table');
    table.className = 'timeline-table';
    
    // 3. Gera o HTML completo da tabela (cabeçalho e corpo)
    table.innerHTML = `
        <thead>
            <tr>
                <th>Status</th>
                <th>Data</th>
                <th>Usuário</th>
                <th>Observação</th>
            </tr>
        </thead>
        <tbody>
            ${logs.map(log => {
                const statusIcon = statusIcons[log.status] || 'fas fa-question-circle';
                const nomeUsuario = log.usuario?.nome_completo || 'N/D';
                const idUsuario = log.usuario?.id_usuario || 0;
                const avatarHtml = criarAvatar(nomeUsuario, idUsuario);
                
                return `
                    <tr>
                        <td>
                            <span class="status-tag" data-status="${log.status}">
                                <i class="${statusIcon}"></i> ${log.status}
                            </span>
                        </td>
                        <td>${new Date(log.data).toLocaleString('pt-BR')}</td>
                        <td>
                            <div class="user-cell">
                                ${avatarHtml}
                                <span>${nomeUsuario}</span>
                            </div>
                        </td>
                        <td>${log.observacao || '-'}</td>
                    </tr>
                `;
            }).join('')}
        </tbody>
    `;

    // 4. Adiciona a tabela DENTRO do wrapper
    tableWrapper.appendChild(table);
    
    // 5. Limpa o container principal e adiciona o WRAPPER (que agora contém a tabela)
    container.innerHTML = '';
    container.appendChild(tableWrapper);
}

/**
 * Renderiza os botões de próximas ações com ícones.
 * @param {object} projeto - O objeto do projeto.
 * @param {object} handlers - As funções de callback para os eventos.
 */
function renderActionButtons(projeto, handlers) {
    const container = document.getElementById('action-buttons');
    if (!container) return;
    container.innerHTML = '';

    if (!projeto.proximos_status || projeto.proximos_status.length === 0) {
        container.innerHTML = '<p>Nenhuma ação disponível.</p>';
        return;
    }

    projeto.proximos_status.forEach(status => {
        const button = document.createElement('button');
        const isDanger = status === 'Cancelado';
        button.className = `action-btn ${isDanger ? 'danger' : 'primary'}`;

        // --- LÓGICA CORRIGIDA ---
        // Reutiliza a constante 'statusIcons' que já importamos do uiHelpers.js
        const iconClass = statusIcons[status] || 'fas fa-arrow-right'; // Usa um ícone de seta como padrão

        // Adiciona o ícone ao lado do texto
        button.innerHTML = `
            <i class="${iconClass}"></i>
            <span class="btn-text">${status}</span>
            <div class="loader-small"></div>
        `;

        button.addEventListener('click', (event) => handlers.onStatusChange(projeto.id_projeto, status, event));
        container.appendChild(button);
    });
}

function renderMiniHomologationChart(ciclo) {
    const canvasId = `homolog-chart-${ciclo.id_homologacao}`;
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (Chart.getChart(canvasId)) {
        Chart.getChart(canvasId).destroy();
    }

    const data = {
        labels: ['Aprovados', 'Reprovados', 'Bloqueados'],
        datasets: [{
            data: [
                ciclo.testes_aprovados || 0,
                ciclo.testes_reprovados || 0,
                ciclo.testes_bloqueados || 0
            ],
            backgroundColor: ['#2ECC71', '#E74C3C', '#95A5A6'],
            borderColor: document.body.classList.contains('dark-mode') ? '#2a2a2a' : '#ffffff',
            borderWidth: 2
        }]
    };

    new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: true }
            }
        }
    });
}

/**
 * Renderiza a tabela de testes reprovados dentro de um componente expansível.
 * @param {number} idCiclo - O ID do ciclo para encontrar o container correto.
 * @param {Array} testesReprovados - A lista de testes com status 'failed' ou 'broken'.
 * @param {object} handlers - O objeto com as funções de callback para eventos.
 */
function renderFailedTestsTable(idCiclo, testesReprovados, handlers) {
    const container = document.getElementById(`failed-tests-${idCiclo}`);
    if (!container) {
        console.error(`[Renderer] Container para testes reprovados do ciclo ${idCiclo} não encontrado.`);
        return;
    }

    if (!testesReprovados || testesReprovados.length === 0) {
        // Se a função foi chamada, mas não há testes reprovados, limpa o container.
        container.innerHTML = '';
        return;
    }

    // --- LÓGICA DO COMPONENTE EXPANSÍVEL ---
    const detailsHtml = `
        <details class="failed-tests-details">
            <summary class="details-summary">
                Ver ${testesReprovados.length} Teste(s) Reprovado(s)
            </summary>
            <div class="table-wrapper" style="margin-top: 1rem;">
                <table class="data-table compact">
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Teste</th>
                            <th>Feature</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${testesReprovados.map(teste => `
                            <tr data-testid="${teste.uuid}">
                                <td><span class="status-tag" data-status="${teste.status}">${teste.status}</span></td>
                                <td title="${teste.nome_teste}">${teste.nome_teste}</td>
                                <td>${teste.feature || 'N/A'}</td>
                                <td>
                                    <button class="btn-secondary small create-task-from-failure-btn" title="Criar tarefa de correção para este bug">
                                        <i class="fas fa-bug"></i> Criar Tarefa
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </details>
    `;
    container.innerHTML = detailsHtml;

    // --- ADICIONA OS LISTENERS AOS NOVOS BOTÕES ---
    // A lógica de adicionar listeners permanece a mesma, pois o HTML da tabela
    // agora está dentro do container.
    container.querySelectorAll('.create-task-from-failure-btn').forEach(button => {
        const row = button.closest('tr');
        if (!row) return;
        
        const testId = row.dataset.testid;
        const teste = testesReprovados.find(t => t.uuid === testId);
        
        if (teste) {
            button.addEventListener('click', (e) => {
                e.preventDefault(); // Previne que o <details> feche ao clicar no botão
                if (handlers && handlers.onCreateTaskFromFailure) {
                    handlers.onCreateTaskFromFailure(teste);
                }
            });
        }
    });
}

/**
 * Renderiza a seção completa do histórico de homologação.
 * @param {Array} ciclos - A lista de ciclos de homologação do projeto.
 * @param {object} handlers - O objeto com as funções de callback para eventos.
 */
// Em projectRenderer.js

function renderHomologationHistory(ciclos, handlers) {
    const container = document.getElementById('homologation-history');
    if (!container) return;
    container.innerHTML = '';

    if (!ciclos || ciclos.length === 0) {
        container.innerHTML = '<p class="empty-text">Nenhum ciclo de homologação registrado.</p>';
        return;
    }

    ciclos.sort((a, b) => new Date(b.data_inicio) - new Date(a.data_inicio));

    ciclos.forEach((ciclo, index) => {
        // --- ESTRUTURA DE ACORDEÃO COM <details> ---
        const detailsElement = document.createElement('details');
        detailsElement.className = 'homologation-cycle-accordion';
        
        // O primeiro ciclo (o mais recente) começa aberto
        if (index === 0) {
            detailsElement.open = true;
        }

        const resultadoTag = ciclo.resultado 
            ? `<span class="status-tag" data-status="${ciclo.resultado}">${ciclo.resultado}</span>`
            : `<span class="status-tag" data-status="Em Andamento">Em Andamento</span>`;

        let progressBarHtml = '';
        if (ciclo.taxa_sucesso !== null && ciclo.taxa_sucesso >= 0) {
            // ... (lógica da barra de progresso, sem alterações) ...
        }

        // O <summary> é o cabeçalho visível do acordeão
        const summaryHtml = `
            <summary class="cycle-summary">
                <span class="summary-title">Versão: ${ciclo.versao_testada}</span>
                <div class="summary-meta">
                    <span>${new Date(ciclo.data_inicio).toLocaleDateString('pt-BR')}</span>
                    ${resultadoTag}
                </div>
            </summary>
        `;

        // O .cycle-content é o corpo que expande/recolhe
        const contentHtml = `
            <div class="cycle-content">
                <div class="cycle-grid">
                    <div class="cycle-details">
                        <div class="cycle-header">
                            <h3>Detalhes do Ciclo (${ciclo.tipo_teste})</h3>
                            <button class="btn-secondary small view-tests-btn" data-cycle-id="${ciclo.id_homologacao}"><i class="fas fa-list-ul"></i> Ver Testes</button>
                        </div>
                        <div class="cycle-meta">
                            <span><i class="fas fa-user-check"></i> ${ciclo.responsavel_teste?.nome_completo || 'N/D'}</span>
                            <span><i class="far fa-calendar-check"></i> Fim: ${ciclo.data_fim ? new Date(ciclo.data_fim).toLocaleString('pt-BR') : 'Em aberto'}</span>
                        </div>
                        ${progressBarHtml}
                        <div class="failed-tests-container" id="failed-tests-${ciclo.id_homologacao}"></div>
                    </div>
                    <div class="cycle-chart-container">
                        <div class="mini-chart-wrapper"><canvas id="homolog-chart-${ciclo.id_homologacao}"></canvas></div>
                        ${ciclo.taxa_sucesso !== null ? `<p>${ciclo.taxa_sucesso.toFixed(1)}% de Sucesso</p>` : ''}
                    </div>
                </div>
            </div>
        `;

        detailsElement.innerHTML = summaryHtml + contentHtml;
        container.appendChild(detailsElement);

        // Renderiza o mini-gráfico e busca os testes (lógica existente)
        if (ciclo.total_testes && ciclo.total_testes > 0) {
            renderMiniHomologationChart(ciclo);
        }
        if (ciclo.resultado && ciclo.testes_reprovados > 0) {
            const failedContainer = document.getElementById(`failed-tests-${ciclo.id_homologacao}`);
            if (failedContainer) failedContainer.innerHTML = '<p class="loading-text">Carregando...</p>';
            api.getTestesDoCiclo(ciclo.id_homologacao)
                .then(testesExecutados => {
                    const testesReprovados = testesExecutados.filter(t => t.status === 'failed' || t.status === 'broken');
                    renderFailedTestsTable(ciclo.id_homologacao, testesReprovados, handlers);
                });
        }
    });
}

// --- FUNÇÕES DE RENDERIZAÇÃO DAS SEÇÕES PRINCIPAIS ---

function renderHeader(projeto, dependencies, handlers) {
    const { auth, navigate } = dependencies;
    document.getElementById('nome-projeto').textContent = projeto.nome_projeto;
    document.getElementById('status-atual-container').innerHTML = `<span class="status-tag" data-status="${projeto.status_atual}"><i class="${statusIcons[projeto.status_atual] || ''}"></i> ${projeto.status_atual}</span>`;

    const editButton = document.getElementById('edit-project-btn');
    if (editButton) {
        editButton.style.display = auth.canEditProject(projeto) ? 'flex' : 'none';
        editButton.onclick = () => navigate(`editar_projeto.html?id=${projeto.id_projeto}`);
    }

    const deleteButton = document.getElementById('delete-project-btn');
    if (deleteButton) {
        deleteButton.style.display = auth.canDeleteProject(projeto) ? 'flex' : 'none';
        deleteButton.onclick = () => handlers.onDelete(projeto.id_projeto, projeto.nome_projeto);
    }
}

function renderKpiPanel(projeto) {
    const saude = calcularSaudeProjeto(projeto);
    document.getElementById('kpi-responsavel').innerHTML = `${criarAvatar(projeto.responsavel?.nome_completo, projeto.responsavel?.id_usuario)} ${projeto.responsavel?.nome_completo || 'N/D'}`;
    document.getElementById('kpi-prioridade').innerHTML = `<span class="metric-tag" data-metric-type="prioridade" data-metric-value="${projeto.prioridade}">${projeto.prioridade}</span>`;
    document.getElementById('kpi-saude').innerHTML = `<div class="health-indicator ${saude.health}" title="${saude.description}"></div> ${saude.description}`;
    
    const prazoStatusEl = document.getElementById('kpi-prazo');
    if (prazoStatusEl) {
        if (projeto.data_fim_real && projeto.data_fim_prevista) {
            const dias = calcularDiferencaDias(projeto.data_fim_prevista, projeto.data_fim_real);
            prazoStatusEl.innerHTML = dias <= 0 ? `<span class="prazo-tag concluido-prazo">Concluído no prazo</span>` : `<span class="prazo-tag concluido-atraso">Concluído com atraso</span>`;
        } else if (projeto.data_fim_prevista) {
            const dias = calcularDiferencaDias(new Date().toISOString(), projeto.data_fim_prevista);
            prazoStatusEl.innerHTML = dias < 0 ? `<span class="prazo-tag atrasado">Atrasado</span>` : `<span class="prazo-tag no-prazo">No prazo</span>`;
        } else {
            prazoStatusEl.textContent = 'N/D';
        }
    }
}

function renderTabVisaoGeral(projeto) {
    document.getElementById('descricao-projeto').textContent = projeto.descricao;

    const painelDetalhes = document.getElementById('painel-detalhes');
    if (painelDetalhes) {
        painelDetalhes.innerHTML = `
            <div class="info-item"><strong><i class="fas fa-ticket-alt"></i> Topdesk:</strong> <span id="topdesk-info">${projeto.numero_topdesk || 'N/D'}</span></div>
            <div class="info-item"><strong><i class="fas fa-building"></i> Área:</strong> <span>${projeto.area_solicitante?.nome_area || 'N/D'}</span></div>
            <div class="info-item"><strong><i class="fas fa-link"></i> Docs:</strong> <span id="link-doc-info"></span></div>
        `;
        const linkDoc = document.getElementById('link-doc-info');
        if (projeto.link_documentacao) { linkDoc.innerHTML = `<a href="${projeto.link_documentacao}" target="_blank">Acessar</a>`; } else { linkDoc.textContent = 'N/A'; }
        addCopyToClipboard('topdesk-info', projeto.numero_topdesk, showToast);
    }

    renderEquipe(projeto.equipe);

    const painelObjetivos = document.getElementById('painel-objetivos');
    if (painelObjetivos) {
        painelObjetivos.innerHTML = '';
        if (projeto.objetivos_estrategicos?.length > 0) {
            projeto.objetivos_estrategicos.forEach(obj => {
                const tag = document.createElement('span');
                tag.className = 'objective-tag';
                tag.textContent = obj.nome_objetivo;
                painelObjetivos.appendChild(tag);
            });
        } else {
            painelObjetivos.innerHTML = '<p class="empty-text">Nenhum objetivo associado.</p>';
        }
    }

    const painelFinanceiro = document.getElementById('painel-financeiro');
    if (painelFinanceiro) {
        const custo = projeto.custo_estimado || 0;
        painelFinanceiro.innerHTML = `<div class="info-item"><strong><i class="fas fa-dollar-sign"></i> Custo Estimado:</strong> <span>R$ ${custo.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span></div>`;
    }
}

function renderTabCronograma(projeto, dependencies, handlers) {
    const { auth } = dependencies;
    const actionContainer = document.getElementById('action-container');
    if (actionContainer) {
        if (auth.canEditProject(projeto)) {
            actionContainer.style.display = 'block';
            renderActionButtons(projeto, handlers);
        } else {
            actionContainer.style.display = 'none';
        }
    }

    const cronogramaContent = document.getElementById('cronograma-content');
    const viewListBtn = document.getElementById('view-list-btn');
    const viewTableBtn = document.getElementById('view-table-btn');
    if (cronogramaContent && viewListBtn && viewTableBtn) {
        let currentView = 'list';
        const logs = projeto.historico_status.sort((a, b) => new Date(b.data) - new Date(a.data));
        const renderCurrentView = () => {
            if (currentView === 'list') { renderTimelineAsList(cronogramaContent, logs); } else { renderTimelineAsTable(cronogramaContent, logs); }
        };
        viewListBtn.addEventListener('click', () => { currentView = 'list'; viewTableBtn.classList.remove('active'); viewListBtn.classList.add('active'); renderCurrentView(); });
        viewTableBtn.addEventListener('click', () => { currentView = 'table'; viewListBtn.classList.remove('active'); viewTableBtn.classList.add('active'); renderCurrentView(); });
        renderCurrentView();
    }
}

// Em projectRenderer.js

function renderTabHomologacao(projeto, handlers) {
    const container = document.getElementById('homologacao');
    if (!container) return;

    // Adiciona os placeholders para o gráfico e para o histórico
    container.innerHTML = `
        <div class="details-panel">
            <h2><i class="fas fa-chart-line"></i> Evolução da Qualidade do Projeto</h2>
            <div class="chart-canvas-wrapper" style="height: 250px;">
                <canvas id="ciclo-evolucao-chart"></canvas>
            </div>
        </div>
        <div class="details-panel" style="margin-top: 2rem;">
            <h2><i class="fas fa-clipboard-check"></i> Histórico de Ciclos</h2>
            <div id="homologation-history"></div>
        </div>
    `;

    // Renderiza o histórico de cards (código existente)
    renderHomologationHistory(projeto.ciclos_homologacao, handlers);

    // --- LÓGICA DO GRÁFICO DE EVOLUÇÃO (CORRIGIDA) ---
    const chartContainer = container.querySelector('.chart-canvas-wrapper');
    const ciclosFinalizados = projeto.ciclos_homologacao
        .filter(c => c.resultado && c.taxa_sucesso !== null)
        .sort((a, b) => new Date(a.data_fim) - new Date(b.data_fim));

    // Se houver PELO MENOS UM ciclo finalizado, renderiza o gráfico
    if (ciclosFinalizados.length > 0) {
        const chartData = {
            labels: ciclosFinalizados.map(c => `Versão ${c.versao_testada}`),
            data: ciclosFinalizados.map(c => c.taxa_sucesso)
        };
        
        // Chama a função helper que já temos no uiHelpers.js
        renderGraficoLinha('ciclo-evolucao-chart', chartData, 'Taxa de Sucesso (%)');
    } else {
        // Se não houver ciclos suficientes, mostra uma mensagem
        if (chartContainer) {
            renderEmptyState(chartContainer, {
                icon: 'fa-history',
                title: 'Aguardando Dados',
                message: 'O gráfico de evolução aparecerá aqui quando houver ciclos de homologação finalizados.'
            });
        }
    }
}


// --- NOVA FUNÇÃO PARA RENDERIZAR A ABA GANTT ---

function renderTabGantt(projeto, dependencies, handlers) {
    const { auth } = dependencies;

    const newTaskBtn = document.getElementById('new-task-btn');
    if (newTaskBtn) {
        // Verifica a permissão
        if (auth.canEditProject(projeto)) {
            newTaskBtn.style.display = 'inline-flex';
            // Adiciona o listener que chama o handler passado pelo controlador
            newTaskBtn.onclick = () => handlers.onNewTask();
        } else {
            newTaskBtn.style.display = 'none';
        }
    }

    // Passa as tarefas e os handlers para a função de renderização do gráfico
    renderGanttChart(projeto.tarefas, handlers);
}

// --- FUNÇÃO PRINCIPAL DE RENDERIZAÇÃO (EXPORTADA) ---

export function renderProjectDetails(projeto, dependencies, handlers) {
    renderHeader(projeto, dependencies, handlers);
    renderKpiPanel(projeto);
    renderTabVisaoGeral(projeto);
    renderTabCronograma(projeto, dependencies, handlers);
    renderTabHomologacao(projeto, handlers);
    renderTabGantt(projeto, dependencies, handlers);
}