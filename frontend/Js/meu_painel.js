import { api } from './apiService.js';
import { showToast } from './toast.js';
import { renderEmptyState } from './uiHelpers.js';

/**
 * Renderiza a lista de tarefas atribuídas ao usuário no painel.
 * @param {Array} tarefas - A lista de tarefas vinda da API (já com dados do projeto).
 * @param {object} dependencies - As dependências globais (ex: navigate).
 */
function renderMinhasTarefas(tarefas, dependencies) {
    const container = document.getElementById('minhas-tarefas-lista');
    if (!container) {
        console.error("[meu_painel.js] Container #minhas-tarefas-lista não encontrado.");
        return;
    }
    container.innerHTML = '';

    if (!tarefas || tarefas.length === 0) {
        renderEmptyState(container, {
            icon: 'fa-check-circle',
            title: 'Tudo em dia!',
            message: 'Você não tem nenhuma tarefa aberta no momento.'
        });
        return;
    }

    const list = document.createElement('ul');
    list.className = 'task-list';

    tarefas.forEach(tarefa => {
        const item = document.createElement('li');
        item.className = 'task-item';

        // Lógica para verificar se a tarefa está atrasada
        const hoje = new Date();
        const prazo = new Date(tarefa.end);
        hoje.setHours(0, 0, 0, 0); // Zera o horário para comparar apenas as datas
        
        const isOverdue = prazo < hoje;

        // --- CORREÇÃO PRINCIPAL AQUI ---
        // Usa o 'nome_projeto' que agora vem da API.
        // Se, por algum motivo, ele não vier, usa o ID como fallback.
        const nomeDoProjeto = tarefa.nome_projeto || `Projeto #${tarefa.id_projeto}`;

        item.innerHTML = `
            <div class="task-info">
                <a href="projeto.html?id=${tarefa.id_projeto}" class="task-name">${tarefa.name}</a>
                <span class="task-project">${nomeDoProjeto}</span>
            </div>
            <div class="task-deadline ${isOverdue ? 'overdue' : ''}">
                <span>Prazo: ${new Date(tarefa.end).toLocaleDateString('pt-BR')}</span>
            </div>
        `;

        // Adiciona o listener de clique para usar a navegação com transição.
        // Adicionamos ao item inteiro para uma área de clique maior.
        item.addEventListener('click', (e) => {
            e.preventDefault();
            dependencies.navigate(`projeto.html?id=${tarefa.id_projeto}`);
        });

        list.appendChild(item);
    });
    container.appendChild(list);
}

/**
 * Função de inicialização da página, chamada pelo main.js.
 * @param {object} dependencies - Objeto contendo as dependências globais.
 */
export function initializePage(dependencies) {
    console.log("[meu_painel.js] Inicializando a página Meu Painel...");
    const mainContent = document.querySelector('.main-content');
    if (mainContent) mainContent.style.opacity = '0';

    // Chama a nova API para buscar apenas as tarefas do usuário logado
    api.getMinhasTarefas()
        .then(tarefas => {
            renderMinhasTarefas(tarefas, dependencies);
        })
        .catch(error => {
            showToast(`Erro ao carregar suas tarefas: ${error.message}`, 'error');
            const container = document.getElementById('minhas-tarefas-lista');
            if (container) {
                renderEmptyState(container, {
                    icon: 'fa-exclamation-triangle',
                    title: 'Erro ao Carregar Tarefas',
                    message: 'Não foi possível buscar suas tarefas. Tente novamente mais tarde.'
                });
            }
        })
        .finally(() => {
            // Garante que o conteúdo da página apareça com a animação de fade-in
            if (mainContent) {
                mainContent.style.transition = 'opacity 0.5s ease-in-out';
                mainContent.style.opacity = '1';
            }
        });
}