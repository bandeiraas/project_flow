import { api } from './apiService.js';
import { showToast } from './toast.js';
import { statusColors, priorityColors } from './colors.js';
import { renderEmptyState, renderGraficoLinha} from './uiHelpers.js';

// --- Variáveis de estado para armazenar os dados em cache ---
let dadosVisaoGeral = null;
let dadosPortfolio = null;
let dadosRoadmap = null;
let dadosVisaoQualidade = null;

// --- FUNÇÕES DE PROCESSAMENTO DE DADOS ---

function processarDadosAgrupados(projetos, chave) {
    const contagem = {};
    for (const projeto of projetos) {
        let valor;
        if (chave === 'responsavel') {
            valor = projeto.responsavel?.nome_completo || 'Não definido';
        } else if (chave === 'area_solicitante') {
            valor = projeto.area_solicitante?.nome_area || 'Não definido';
        } else {
            valor = projeto[chave] || 'Não definido';
        }
        contagem[valor] = (contagem[valor] || 0) + 1;
    }
    return {
        labels: Object.keys(contagem),
        data: Object.values(contagem)
    };
}

function formatarProjetosParaGantt(projetos) {
    return projetos
        .filter(p => p.data_inicio_prevista && p.data_fim_prevista)
        .map(p => ({
            id: `proj_${p.id_projeto}`,
            name: p.nome_projeto,
            start: p.data_inicio_prevista.split('T')[0],
            end: p.data_fim_prevista.split('T')[0],
            progress: 100,
            custom_class: `bar-status-${p.status_atual.toLowerCase().replace(/ /g, '-')}`
        }));
}

// --- FUNÇÕES DE RENDERIZAÇÃO ---

function renderizarGrafico(canvasId, tipo, dados, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    if (Chart.getChart(canvasId)) {
        Chart.getChart(canvasId).destroy();
    }

    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(54, 54, 54, 0.8)';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    const borderColor = isDarkMode ? '#1e1e1e' : '#ffffff';
    
    new Chart(ctx, {
        type: tipo,
        data: dados,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    display: options.showLegend !== false,
                    labels: { color: textColor }
                }
            },
            scales: options.scales || {},
            indexAxis: options.indexAxis || 'x'
        }
    });
}

function renderizarVisaoGeral(projetos) {
    const container = document.querySelector('#view-geral');
    if (!container) return;
    const statsGrid = container.querySelector('.stats-grid');
    const chartsGrid = container.querySelector('.charts-grid');
    
    const total = projetos.length;
    const ativos = projetos.filter(p => !["Pós GMUD", "Projeto concluído", "Cancelado"].includes(p.status_atual)).length;
    const concluidos = projetos.filter(p => ["Pós GMUD", "Projeto concluído"].includes(p.status_atual)).length;
    statsGrid.innerHTML = `<div class="stat-card"><h3>Total</h3><p>${total}</p></div><div class="stat-card"><h3>Ativos</h3><p>${ativos}</p></div><div class="stat-card"><h3>Concluídos</h3><p>${concluidos}</p></div>`;
    
    chartsGrid.innerHTML = `<div class="chart-container"><h2>Por Status</h2><div class="chart-canvas-wrapper"><canvas id="status-chart"></canvas></div></div><div class="chart-container"><h2>Por Prioridade</h2><div class="chart-canvas-wrapper"><canvas id="priority-chart"></canvas></div></div><div class="chart-container"><h2>Por Responsável</h2><div class="chart-canvas-wrapper"><canvas id="responsavel-chart"></canvas></div></div><div class="chart-container"><h2>Por Área</h2><div class="chart-canvas-wrapper"><canvas id="area-chart"></canvas></div></div>`;
    
    renderizarGrafico('status-chart', 'pie', { labels: processarDadosAgrupados(projetos, 'status_atual').labels, datasets: [{ data: processarDadosAgrupados(projetos, 'status_atual').data, backgroundColor: processarDadosAgrupados(projetos, 'status_atual').labels.map(l => statusColors[l] || '#ccc') }] });
    renderizarGrafico('priority-chart', 'pie', { labels: processarDadosAgrupados(projetos, 'prioridade').labels, datasets: [{ data: processarDadosAgrupados(projetos, 'prioridade').data, backgroundColor: processarDadosAgrupados(projetos, 'prioridade').labels.map(l => priorityColors[l] || '#ccc') }] });
    renderizarGrafico('responsavel-chart', 'bar', { labels: processarDadosAgrupados(projetos, 'responsavel').labels, datasets: [{ label: 'Projetos', data: processarDadosAgrupados(projetos, 'responsavel').data, backgroundColor: '#4A69BD' }] }, { indexAxis: 'y', showLegend: false, scales: { x: { beginAtZero: true, ticks: { precision: 0 } } } });
    renderizarGrafico('area-chart', 'bar', { labels: processarDadosAgrupados(projetos, 'area_solicitante').labels, datasets: [{ label: 'Projetos', data: processarDadosAgrupados(projetos, 'area_solicitante').data, backgroundColor: '#1ABC9C' }] }, { indexAxis: 'y', showLegend: false, scales: { x: { beginAtZero: true, ticks: { precision: 0 } } } });
}

/**
 * Renderiza o dashboard de portfólio completo na página.
 * @param {Array} dadosPortfolio - A lista de objetivos com seus projetos e métricas.
 * @param {object} dependencies - As dependências globais (ex: navigate).
 */

function renderPortfolio(dadosPortfolio, dependencies) {
    const container = document.querySelector('#view-portfolio .portfolio-grid');
    if (!container) return;
    container.innerHTML = '';

    if (!dadosPortfolio || dadosPortfolio.length === 0) {
        renderEmptyState(container, {
            icon: 'fa-bullseye',
            title: 'Nenhum Objetivo Encontrado',
            message: 'Crie objetivos e associe projetos a eles.'
        });
        return;
    }

    // ETAPA 1: Construir e adicionar todo o HTML
    dadosPortfolio.forEach(objetivo => {
        const card = document.createElement('div');
        card.className = 'objetivo-card';
        const projetosHtml = objetivo.projetos.map(p => `<li><a href="projeto.html?id=${p.id_projeto}" class="project-link"><span class="status-dot" style="background-color: ${statusColors[p.status_atual] || ''}"></span>${p.nome_projeto}</a></li>`).join('');
        
        card.innerHTML = `
            <div class="objetivo-header"><h2>${objetivo.nome_objetivo}</h2><p>${objetivo.descricao || ''}</p></div>
            <div class="objetivo-body">
                <div class="objetivo-metrics">
                    <div class="metric-item"><strong>Investimento Estimado</strong><span>R$ ${objetivo.custo_total_estimado.toLocaleString('pt-BR')}</span></div>
                    <div class="metric-item"><strong>Total de Projetos</strong><span>${objetivo.total_projetos}</span></div>
                    <div class="mini-chart-container">
                        <canvas id="chart-obj-${objetivo.id_objetivo}"></canvas>
                    </div>
                </div>
                <div class="objetivo-projects">
                    <h3>Projetos Associados</h3>
                    <ul class="objetivo-projects-list">${projetosHtml}</ul>
                </div>
            </div>
        `;
        container.appendChild(card);
    });

    // ETAPA 2: DEPOIS que todo o HTML está no DOM, inicializar os gráficos
    setTimeout(() => {
        dadosPortfolio.forEach(objetivo => {
            const canvasId = `chart-obj-${objetivo.id_objetivo}`;
            const chartData = objetivo.grafico_status;

            // --- CORREÇÃO CRÍTICA AQUI ---
            // Verifica a estrutura de dados correta:
            // chartData existe, datasets é um array com pelo menos um item,
            // e o array 'data' dentro do primeiro dataset tem itens.
            if (chartData && chartData.datasets && chartData.datasets[0] && chartData.datasets[0].data.length > 0) {
                console.log(`[Portfolio] DADOS VÁLIDOS ENCONTRADOS. Chamando renderizarGrafico para ${canvasId}.`);
                renderizarGrafico(
                    canvasId, 
                    'doughnut', 
                    chartData, // Passa o objeto completo
                    statusColors
                );
            } else {
                console.warn(`[Portfolio] Sem dados de gráfico para o objetivo: ${objetivo.nome_objetivo}`);
                const chartContainer = document.getElementById(canvasId)?.parentNode;
                if (chartContainer) {
                    chartContainer.innerHTML = '<p class="empty-text-small">Sem dados para o gráfico.</p>';
                }
            }
        });
    }, 100);
}

function renderRoadmap(projetos) {
    const container = document.querySelector('#view-roadmap .gantt-container');
    if (!container) return;
    container.innerHTML = '';
    const projetosFormatados = formatarProjetosParaGantt(projetos);
    if (projetosFormatados.length === 0) {
        container.innerHTML = '<p class="empty-text">Nenhum projeto com datas para exibir no roadmap.</p>';
        return;
    }
    try {
        const gantt = new Gantt(container, projetosFormatados, {
            view_mode: 'Month',
            on_click: (p) => window.location.href = `projeto.html?id=${p.id.replace('proj_', '')}`,
            custom_popup_html: (p) => `<div class="gantt-tooltip-content"><h4>${p.name}</h4></div>`
        });
        const zoomToggle = document.querySelector('#view-roadmap .gantt-zoom-toggle');
        if (zoomToggle) {
            zoomToggle.addEventListener('click', (e) => {
                const target = e.target.closest('.zoom-btn');
                if (!target) return;
                zoomToggle.querySelector('.active')?.classList.remove('active');
                target.classList.add('active');
                gantt.change_view_mode(target.dataset.viewMode);
            });
        }
    } catch (error) {
        console.error("[Roadmap] Erro ao inicializar o Gantt:", error);
    }
}

/**
 * Renderiza o gráfico de barras empilhadas para a distribuição de testes.
 * @param {string} canvasId - O ID do elemento <canvas>.
 * @param {object} dados - Os dados para o gráfico, com { labels, datasets }.
 */
function renderGraficoDistribuicaoTestes(canvasId, dados) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    if (Chart.getChart(canvasId)) {
        Chart.getChart(canvasId).destroy();
    }

    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(54, 54, 54, 0.8)';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

    // Cores específicas para os status dos testes
    const colors = {
        Aprovados: isDarkMode ? '#2ECC71' : '#27ae60',
        Reprovados: isDarkMode ? '#ff7675' : '#c0392b',
        Bloqueados: isDarkMode ? '#b2bec3' : '#7f8c8d'
    };

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dados.labels,
            datasets: dados.datasets.map(dataset => ({
                label: dataset.label,
                data: dataset.data,
                backgroundColor: colors[dataset.label]
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: textColor }
                }
            },
            scales: {
                x: {
                    stacked: true, // Empilha as barras no eixo X
                    ticks: { color: textColor },
                    grid: { color: gridColor }
                },
                y: {
                    stacked: true, // Empilha as barras no eixo Y
                    beginAtZero: true,
                    ticks: { precision: 0, color: textColor },
                    grid: { color: gridColor }
                }
            }
        }
    });
}

/**
 * Função principal que renderiza todo o conteúdo da visão de Qualidade.
 * @param {object} qaData - Os dados completos de QA vindos da API.
 */
function renderizarVisaoQualidade(qaData) {
    const container = document.querySelector('#view-qualidade');
    if (!container) return;

    const chartsGrid = container.querySelector('.charts-grid');
    if (!chartsGrid) return;

    // Garante que os containers para os canvas existam
    chartsGrid.innerHTML = `
        <div class="chart-container">
            <h2>Taxa de Sucesso Histórica (%)</h2>
            <p class="chart-subtitle">Evolução da qualidade dos ciclos de teste ao longo do tempo.</p>
            <div class="chart-canvas-wrapper">
                <canvas id="qa-taxa-sucesso-chart"></canvas>
            </div>
        </div>
        <div class="chart-container">
            <h2>Distribuição de Testes por Projeto</h2>
            <p class="chart-subtitle">Total de testes aprovados, reprovados e bloqueados por projeto.</p>
            <div class="chart-canvas-wrapper">
                <canvas id="qa-distribuicao-chart"></canvas>
            </div>
        </div>
    `;
    
    // Verifica se os dados existem antes de tentar renderizar os gráficos
    if (qaData && qaData.taxa_sucesso_historica && qaData.distribuicao_por_projeto) {
        renderGraficoTaxaSucesso('qa-taxa-sucesso-chart', qaData.taxa_sucesso_historica);
        renderGraficoDistribuicaoTestes('qa-distribuicao-chart', qaData.distribuicao_por_projeto);
    } else {
        renderEmptyState(chartsGrid, { 
            icon: 'fa-shield-alt', 
            title: 'Sem Dados de QA', 
            message: 'Finalize ciclos de homologação com métricas para ver os relatórios.' 
        });
    }
}

// --- FUNÇÕES DE CARREGAMENTO DE DADOS ---

function carregarVisaoGeral(dependencies) {
    const container = document.querySelector('#view-geral');
    if (!container) return;
    container.innerHTML = '<div class="stats-grid"><div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div></div><div class="charts-grid"><div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div></div>';
    api.getTodosProjetos().then(projetos => {
        dadosVisaoGeral = projetos;
        renderizarVisaoGeral(projetos);
    });
}

function carregarPortfolio(dependencies) {
    const container = document.querySelector('#view-portfolio .portfolio-grid');
    if (container) container.innerHTML = '<div class="skeleton-card"></div>';
    api.getRelatorioPortfolio().then(data => renderPortfolio(data, dependencies));
}

function carregarRoadmap() {
    const container = document.querySelector('#view-roadmap .gantt-container');
    if (container) container.innerHTML = '<div class="skeleton-card"></div>';
    api.getTodosProjetos().then(renderRoadmap);
}

function carregarVisaoQualidade() {
    const container = document.querySelector('#view-qualidade');
    if (!container) return;
    
    const chartsGrid = container.querySelector('.charts-grid');
    if (chartsGrid) chartsGrid.innerHTML = '<div class="skeleton-card"></div><div class="skeleton-card"></div>';
    
    api.getRelatorioQa()
        .then(qaData => {
            if (chartsGrid) {
                chartsGrid.innerHTML = `
                    <div class="chart-container"><h2>Taxa de Sucesso Histórica (%)</h2><div class="chart-canvas-wrapper"><canvas id="qa-taxa-sucesso-chart"></canvas></div></div>
                    <div class="chart-container"><h2>Distribuição de Testes por Projeto</h2><div class="chart-canvas-wrapper"><canvas id="qa-distribuicao-chart"></canvas></div></div>
                `;
            }
            
            if (qaData && qaData.taxa_sucesso_historica && qaData.distribuicao_por_projeto) {
                renderGraficoLinha('qa-taxa-sucesso-chart', qaData.taxa_sucesso_historica);
                renderGraficoDistribuicaoTestes('qa-distribuicao-chart', qaData.distribuicao_por_projeto);
            } else {
                renderEmptyState(chartsGrid, { icon: 'fa-shield-alt', title: 'Sem Dados de QA', message: 'Finalize ciclos de homologação com métricas para ver os relatórios.' });
            }
        })
        .catch(error => {
            showToast(`Erro ao carregar dados de QA: ${error.message}`, 'error');
        });
}

// --- FUNÇÃO DE INICIALIZAÇÃO PRINCIPAL ---

export function initializePage(dependencies) {
    console.log("[insights.js] Inicializando a página de Insights...");
    
    document.addEventListener('theme:changed', () => {
        console.log("[insights.js] Tema alterado. Re-renderizando visões...");
        if (dadosVisaoGeral) renderizarVisaoGeral(dadosVisaoGeral);
        if (dadosPortfolio) renderPortfolio(dadosPortfolio, dependencies);
        if (dadosRoadmap) renderRoadmap(dadosRoadmap);
        if (dadosVisaoQualidade) renderizarVisaoQualidade(dadosVisaoQualidade);
    });

    const navButtons = document.querySelectorAll('.insights-nav .nav-btn');
    const viewPanes = document.querySelectorAll('.insights-content .view-pane');

    const switchView = (viewId) => {
        navButtons.forEach(btn => btn.classList.toggle('active', btn.dataset.view === viewId));
        viewPanes.forEach(pane => pane.classList.toggle('active', pane.id === `view-${viewId}`));
        const targetButton = document.querySelector(`.nav-btn[data-view="${viewId}"]`);
        if (targetButton && !targetButton.dataset.loaded) {
            loadViewData(viewId, dependencies);
            targetButton.dataset.loaded = 'true';
        }
    };

    const loadViewData = (viewId, dependencies) => {
        switch (viewId) {
            case 'geral': carregarVisaoGeral(dependencies); break;
            case 'portfolio': carregarPortfolio(dependencies); break;
            case 'roadmap': carregarRoadmap(dependencies); break;
            case 'qualidade': carregarVisaoQualidade(dependencies); break;
        }
    };

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => switchView(btn.dataset.view));
    });

    switchView('geral');
}