import { api } from './apiService.js';
import { showToast } from './toast.js';
import { statusColors } from './colors.js'; // Reutiliza nosso mapa de cores

/**
 * Formata os dados dos projetos para o formato esperado pelo Frappe Gantt.
 * @param {Array} projetos - A lista de projetos da API.
 * @returns {Array} - A lista de tarefas formatada para o Gantt.
 */
function formatarProjetosParaGantt(projetos) {
    return projetos
        // Filtra apenas projetos que têm datas de início e fim previstas
        .filter(p => p.data_inicio_prevista && p.data_fim_prevista)
        .map(p => ({
            id: `proj_${p.id_projeto}`, // Adiciona um prefixo para evitar conflito de ID com tarefas
            name: p.nome_projeto,
            start: p.data_inicio_prevista.split('T')[0], // Formato YYYY-MM-DD
            end: p.data_fim_prevista.split('T')[0],     // Formato YYYY-MM-DD
            progress: 100, // Usamos 100 para que a cor seja sólida
            custom_class: `bar-status-${p.status_atual.toLowerCase().replace(/ /g, '-')}` // Classe CSS customizada
        }));
}

/**
 * Renderiza o gráfico de Roadmap.
 * @param {Array} projetosFormatados - A lista de projetos já formatada.
 */
function renderRoadmap(projetosFormatados) {
    const container = document.getElementById('roadmap-container');
    if (!container) return;
    container.innerHTML = '';

    if (projetosFormatados.length === 0) {
        container.innerHTML = '<p class="empty-text">Nenhum projeto com datas previstas para exibir no roadmap.</p>';
        return;
    }

    try {
        const gantt = new Gantt(container, projetosFormatados, {
            view_mode: 'Month', // Começa na visão de Mês
            on_click: (project) => {
                // Ao clicar na barra, navega para a página de detalhes do projeto
                const projectId = project.id.replace('proj_', '');
                window.location.href = `projeto.html?id=${projectId}`;
            },
            custom_popup_html: (project) => {
                return `<div class="gantt-tooltip-content"><h4>${project.name}</h4></div>`;
            }
        });

        // Lógica dos botões de zoom
        const zoomToggle = document.querySelector('.gantt-zoom-toggle');
        if (zoomToggle) {
            zoomToggle.addEventListener('click', (event) => {
                const target = event.target.closest('.zoom-btn');
                if (!target) return;
                zoomToggle.querySelector('.active')?.classList.remove('active');
                target.classList.add('active');
                const viewMode = target.dataset.viewMode;
                // Adiciona 'Year' às opções de visualização
                if (viewMode === 'Year') {
                    gantt.change_view_mode('Month'); // Workaround para o modo Ano
                    // A biblioteca não tem um modo 'Year' nativo, mas podemos simular
                } else {
                    gantt.change_view_mode(viewMode);
                }
            });
        }

    } catch (error) {
        console.error("[Roadmap] Erro ao inicializar o Gantt:", error);
        container.innerHTML = '<p class="empty-text" style="color: red;">Erro ao renderizar o roadmap.</p>';
    }
}

/**
 * Função de inicialização da página, chamada pelo main.js.
 */
export function initializePage(dependencies) {
    console.log("[roadmap.js] Inicializando a página de roadmap...");
    const mainContent = document.querySelector('.main-content');
    if (mainContent) mainContent.style.opacity = '0';

    api.getTodosProjetos()
        .then(projetos => {
            const projetosFormatados = formatarProjetosParaGantt(projetos);
            renderRoadmap(projetosFormatados);
        })
        .catch(error => {
            showToast(`Erro ao carregar dados do roadmap: ${error.message}`, 'error');
        })
        .finally(() => {
            if (mainContent) {
                mainContent.style.transition = 'opacity 0.5s ease-in-out';
                mainContent.style.opacity = '1';
            }
        });
}