import { api } from './apiService.js';
import { showToast } from './toast.js';
import { statusColors, priorityColors } from './colors.js';

// --- Variáveis de escopo do módulo ---
// Armazena as instâncias dos gráficos para podermos destruí-las e recriá-las.
const chartInstances = {};
// Armazena os dados dos projetos para evitar múltiplas chamadas à API.
let allProjectsData = [];

/**
 * Processa uma lista de projetos para contar a ocorrência de valores em uma chave.
 */
// Em relatorios.js

function processarDados(projetos, chave) {
    const contagem = {};
    for (const projeto of projetos) {
        let valor;
        // --- CORREÇÃO PARA OBJETOS ANINHADOS ---
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

/**
 * Renderiza um gráfico de pizza, configurando todas as cores dinamicamente.
 */
function renderizarGraficoPizza(canvasId, dadosGrafico, colorMap) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Destrói qualquer instância de gráfico anterior neste canvas.
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }

    const isDarkMode = document.body.classList.contains('dark-mode');
    const backgroundColors = dadosGrafico.labels.map(label => {
        const color = colorMap[label] || colorMap['default'];
        return isDarkMode ? `${color}40` : color;
    });
    const borderColor = isDarkMode ? '#1e1e1e' : '#ffffff';
    const textColor = isDarkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(54, 54, 54, 0.8)';

    // Cria e armazena a nova instância do gráfico.
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: dadosGrafico.labels,
            datasets: [{
                label: 'Nº de Projetos',
                data: dadosGrafico.data,
                backgroundColor: backgroundColors,
                borderColor: borderColor,
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: textColor
                    }
                },
                tooltip: {
                    titleColor: isDarkMode ? '#ffffff' : '#000000',
                    bodyColor: isDarkMode ? '#dddddd' : '#333333',
                    backgroundColor: isDarkMode ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
                }
            }
        }
    });
}

/**
 * Renderiza as estatísticas rápidas no topo da página.
 */
function renderizarEstatisticas(projetos) {
    document.getElementById('stat-total-projetos').textContent = projetos.length;
    document.getElementById('stat-projetos-ativos').textContent = projetos.filter(p => !["Pós GMUD", "Cancelado", "Projeto concluído"].includes(p.status_atual)).length;
    document.getElementById('stat-projetos-concluidos').textContent = projetos.filter(p => ["Pós GMUD", "Projeto concluído"].includes(p.status_atual)).length;
}

/**
 * Função que re-renderiza todos os gráficos na página.
 * É chamada na carga inicial e sempre que o tema muda.
 */
function renderAllCharts() {
    if (allProjectsData.length > 0) {
        const dadosStatus = processarDados(allProjectsData, 'status_atual');
        renderizarGraficoPizza('status-chart', dadosStatus, statusColors);

        const dadosPrioridade = processarDados(allProjectsData, 'prioridade');
        renderizarGraficoPizza('priority-chart', dadosPrioridade, priorityColors);
    }
}


// Adicione esta nova função em relatorios.js

/**
 * Renderiza um gráfico de barras horizontal.
 * @param {string} canvasId - O ID do elemento <canvas>.
 * @param {object} dadosGrafico - Os dados processados com labels e data.
 * @param {string} label - O rótulo para o dataset do gráfico.
 */
function renderizarGraficoBarras(canvasId, dadosGrafico, label) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Destrói qualquer instância de gráfico anterior neste canvas
    if (Chart.getChart(canvasId)) {
        Chart.getChart(canvasId).destroy();
    }

    const isDarkMode = document.body.classList.contains('dark-mode');
    
    // Usa a primeira cor da nossa paleta, com opacidade
    const barColor = isDarkMode ? '#74b9ff40' : '#4A69BD';
    const barBorderColor = isDarkMode ? '#74b9ff' : '#1e3799';

    new Chart(ctx, {
        type: 'bar', // Tipo do gráfico
        data: {
            labels: dadosGrafico.labels,
            datasets: [{
                label: label,
                data: dadosGrafico.data,
                backgroundColor: barColor,
                borderColor: barBorderColor,
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y', // --- Torna o gráfico de barras horizontal ---
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false // Não precisamos de legenda para um único dataset
                }
            },
            scales: {
                x: {
                    beginAtZero: true, // Garante que o eixo X comece no zero
                    ticks: {
                        // Garante que os ticks sejam apenas números inteiros
                        precision: 0
                    }
                }
            }
        }
    });
}


/**
 * Função de inicialização da página, chamada pelo main.js.
 */
export function initializePage(dependencies) {
    console.log("[relatorios.js] Inicializando a página de relatórios...");
    
    // Adiciona um listener que "ouve" as mudanças de tema anunciadas pelo ThemeToggle.
    document.addEventListener('theme:changed', () => {
        console.log("[relatorios.js] Evento de mudança de tema detectado. Re-renderizando gráficos...");
        renderAllCharts();
    });

    api.getTodosProjetos()
        .then(projetos => {
            allProjectsData = projetos; // Salva os dados para re-renderização
            const container = document.querySelector('.charts-grid');
            if (!container) return;

            if (projetos && projetos.length > 0) {
                renderizarEstatisticas(projetos);
                renderAllCharts(); // Renderiza os gráficos pela primeira vez
                
                
                // 1. Processa os dados agrupando pelo nome do responsável
                const dadosResponsavel = processarDados(projetos, 'responsavel');
                // 2. Renderiza o gráfico de barras
                renderizarGraficoBarras('responsavel-chart', dadosResponsavel, 'Nº de Projetos');

                // --- PREPARAÇÃO PARA O PRÓXIMO GRÁFICO ---
                const dadosArea = processarDados(projetos, 'area_solicitante');
                renderizarGraficoBarras('area-chart', dadosArea, 'Nº de Projetos');
            } else {
                container.innerHTML = '<p>Não há dados suficientes para gerar relatórios.</p>';
            }
        })
        
        
        .catch(error => {
            showToast(`Erro ao carregar dados para os relatórios: ${error.message}`, 'error');
        });
}