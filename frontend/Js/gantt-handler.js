/**
 * Renderiza ou atualiza o gráfico de Gantt com opções de customização.
 * @param {Array} tarefas - A lista de tarefas do projeto.
 * @param {object} handlers - Um objeto contendo as funções de callback para eventos (ex: onTaskClick).
 */
export function renderGanttChart(tarefas, handlers) {
    const container = document.getElementById('gantt-chart-container');
    if (!container) {
        console.error("[Gantt] Container #gantt-chart-container não encontrado.");
        return;
    }
    container.innerHTML = '';

    if (!tarefas || tarefas.length === 0) {
        container.innerHTML = '<p class="empty-text">Nenhuma tarefa cadastrada para este projeto.</p>';
        return;
    }

    const tarefasProcessadas = tarefas.map(t => ({
        ...t,
        custom_class: t.progress === 100 ? 'bar-milestone' : ''
    }));

    // Adia a inicialização para garantir que a biblioteca esteja 100% pronta
    setTimeout(() => {
        try {
            const ganttInstance = new Gantt(container, tarefasProcessadas, {
                // --- OPÇÕES DE CUSTOMIZAÇÃO ---
                header_height: 50,
                bar_height: 24,
                bar_corner_radius: 4,
                padding: 18,
                view_mode: 'Week',
                date_format: 'YYYY-MM-DD',

                // --- TOOLTIP E INTERATIVIDADE ---
                custom_popup_html: function(task) {
                    const startDate = new Date(task._start).toLocaleDateString('pt-BR');
                    const endDate = new Date(task._end).toLocaleDateString('pt-BR');
                    const duration = Math.ceil((task._end.getTime() - task._start.getTime()) / (1000 * 60 * 60 * 24)) + 1;

                    return `
                        <div class="gantt-tooltip-content">
                            <h4>${task.name}</h4>
                            <p><strong>Prazo:</strong> ${startDate} - ${endDate}</p>
                            <p><strong>Duração:</strong> ${duration} dia(s)</p>
                            <p><strong>Progresso:</strong> ${task.progress}%</p>
                        </div>
                    `;
                },
                
                // --- LÓGICA DE EVENTOS (AJUSTADA) ---
                // O evento on_click agora chama o handler que foi passado pelo controlador (projeto.js)
                on_click: (task) => {
                    if (handlers && handlers.onTaskClick) {
                        handlers.onTaskClick(task);
                    }
                },
                on_date_change: (task, start, end) => {
                    console.log(`Tarefa ${task.id} movida. Novo início: ${start}, Novo fim: ${end}`);
                    showToast(`Tarefa "${task.name}" teve seu prazo alterado.`, 'info');
                    // TODO: Chamar a API para salvar as novas datas da tarefa
                },
                on_progress_change: (task, progress) => {
                    console.log(`Progresso da tarefa ${task.id} alterado para ${progress}%`);
                    // TODO: Chamar a API para salvar o novo progresso
                },
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
                    ganttInstance.change_view_mode(viewMode);
                });
            }

        } catch (error) {
            console.error("[Gantt] Erro ao inicializar o Frappe Gantt:", error);
            container.innerHTML = '<p class="empty-text" style="color: red;">Erro ao renderizar o gráfico.</p>';
        }
    }, 0);
}