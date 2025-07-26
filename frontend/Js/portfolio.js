import { api } from './apiService.js';
import { showToast } from './toast.js';
import { statusColors } from './colors.js';
import { renderEmptyState } from './uiHelpers.js';

/**
 * Renderiza um mini-gráfico de pizza para um objetivo estratégico.
 * @param {string} canvasId - O ID do elemento <canvas> para o gráfico.
 * @param {object} chartData - Os dados do gráfico com { labels, data }.
 */
function renderMiniChart(canvasId, chartData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`[portfolio.js] Canvas com ID '${canvasId}' não encontrado.`);
        return;
    }

    // Destrói qualquer gráfico anterior no mesmo canvas
    if (Chart.getChart(canvasId)) {
        Chart.getChart(canvasId).destroy();
    }

    const isDarkMode = document.body.classList.contains('dark-mode');
    const backgroundColors = chartData.labels.map(label => {
        const color = statusColors[label] || statusColors['default'];
        return isDarkMode ? `${color}40` : color;
    });
    const borderColor = isDarkMode ? '#2a2a2a' : '#ffffff'; // Cor de fundo do card
    const textColor = isDarkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)';

    new Chart(ctx, {
        type: 'doughnut', // Gráfico de rosca, mais moderno para mini-visualizações
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: backgroundColors,
                borderColor: borderColor,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'right', // Legenda à direita para economizar espaço vertical
                    labels: {
                        color: textColor,
                        boxWidth: 12,
                        padding: 10
                    }
                },
                tooltip: {
                    // Callbacks para customizar o tooltip
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed !== null) {
                                label += context.parsed;
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Renderiza o dashboard de portfólio completo na página.
 * @param {Array} dadosPortfolio - A lista de objetivos com seus projetos e métricas.
 * @param {object} dependencies - As dependências globais (ex: navigate).
 */
function renderPortfolio(dadosPortfolio, dependencies) {
    const container = document.getElementById('portfolio-container');
    if (!container) return;
    container.innerHTML = '';

    if (!dadosPortfolio || dadosPortfolio.length === 0) {
        renderEmptyState(container, {
            icon: 'fa-bullseye',
            title: 'Nenhum Objetivo Estratégico Encontrado',
            message: 'Crie objetivos e associe projetos a eles para ver o portfólio.'
        });
        return;
    }

    dadosPortfolio.forEach(objetivo => {
        const card = document.createElement('div');
        card.className = 'objetivo-card';

        const projetosHtml = objetivo.projetos.map(p => `
            <li class="objetivo-project-item">
                <a href="projeto.html?id=${p.id_projeto}" class="project-link">
                    <span class="status-dot" style="background-color: ${statusColors[p.status_atual] || statusColors['default']}"></span>
                    ${p.nome_projeto}
                </a>
            </li>
        `).join('');

        card.innerHTML = `
            <div class="objetivo-header">
                <h2>${objetivo.nome_objetivo}</h2>
                <p>${objetivo.descricao || ''}</p>
            </div>
            <div class="objetivo-body">
                <div class="objetivo-metrics">
                    <div class="metric-item">
                        <strong>Investimento Estimado</strong>
                        <span>R$ ${objetivo.custo_total_estimado.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                    </div>
                    <div class="metric-item">
                        <strong>Total de Projetos</strong>
                        <span>${objetivo.total_projetos}</span>
                    </div>
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

        // Renderiza o mini-gráfico para este objetivo
        renderMiniChart(`chart-obj-${objetivo.id_objetivo}`, objetivo.grafico_status);
    });
}

/**
 * Função de inicialização da página, chamada pelo main.js.
 */
export function initializePage(dependencies) {
    console.log("[portfolio.js] Inicializando a página de portfólio...");
    const mainContent = document.querySelector('.main-content');
    if (mainContent) mainContent.style.opacity = '0';

    api.getRelatorioPortfolio()
        .then(dadosPortfolio => {
            renderPortfolio(dadosPortfolio, dependencies);
        })
        .catch(error => {
            showToast(`Erro ao carregar dados do portfólio: ${error.message}`, 'error');
            const container = document.getElementById('portfolio-container');
            if (container) {
                renderEmptyState(container, {
                    icon: 'fa-exclamation-triangle',
                    title: 'Erro ao Carregar',
                    message: 'Não foi possível buscar os dados do portfólio.'
                });
            }
        })
        .finally(() => {
            if (mainContent) {
                mainContent.style.transition = 'opacity 0.5s ease-in-out';
                mainContent.style.opacity = '1';
            }
        });
}