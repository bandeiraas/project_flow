import { api } from './apiService.js';
import { renderEmptyState, calcularSaudeProjeto } from './uiHelpers.js';

// --- VARIÁVEIS DE ESTADO DO MÓDULO ---
let todosOsProjetos = [];
let minhasTarefas = [];
let meusProjetos = [];
let filtrosAtivos = {
    busca: '',
    status: 'Todos'
};

// --- FUNÇÕES DE RENDERIZAÇÃO (Visão Geral) ---

function renderGeralProjectCards(projetos, dependencies) {
    const projectGrid = document.getElementById('project-grid');
    if (!projectGrid) return;
    projectGrid.innerHTML = '';

    if (projetos.length === 0) {
        const termoBusca = filtrosAtivos.busca.trim();
        if (termoBusca) {
            renderEmptyState(projectGrid, { icon: 'fa-search-minus', title: `Nenhum resultado para "${termoBusca}"`, message: 'Tente um termo de busca diferente.' });
        } else {
            renderEmptyState(projectGrid, { icon: 'fa-folder-open', title: 'Nenhum Projeto Encontrado', message: 'Não há projetos que correspondam ao filtro de status.' });
        }
        return;
    }

    projetos.forEach((projeto, index) => {
        const card = document.createElement('div');
        card.className = 'project-card';
        card.addEventListener('click', () => {
            const state = { scrollPos: window.scrollY, filters: filtrosAtivos };
            dependencies.navigate(`projeto.html?id=${projeto.id_projeto}`, state);
        });
        const saude = calcularSaudeProjeto(projeto);
        card.innerHTML = `<div class="card-header"><div class="health-indicator ${saude.health}" title="${saude.description}"></div><h3>${projeto.nome_projeto}</h3><span class="priority-tag" data-priority="${projeto.prioridade}">${projeto.prioridade}</span></div><p class="card-description">${projeto.descricao}</p><div class="card-meta"><span><i class="fas fa-user-tie"></i> ${projeto.responsavel?.nome_completo || 'N/D'}</span><span><i class="fas fa-ticket-alt"></i> ${projeto.numero_topdesk}</span></div><div class="status-info"><span>Status Atual</span><span class="status-tag" data-status="${projeto.status_atual}">${projeto.status_atual}</span></div>`;
        projectGrid.appendChild(card);
        card.style.animation = `fadeInCard 0.5s ease-out ${index * 0.07}s forwards`;
    });
}

function renderStatusFilters(dependencies) {
    const container = document.getElementById('status-filters');
    if (!container) return;
    const statusUnicos = ['Todos', ...new Set(todosOsProjetos.map(p => p.status_atual))];
    container.innerHTML = statusUnicos.map(status => `<button class="filter-btn ${status === filtrosAtivos.status ? 'active' : ''}" data-status="${status}">${status}</button>`).join('');
    container.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            container.querySelector('.active')?.classList.remove('active');
            btn.classList.add('active');
            filtrosAtivos.status = btn.dataset.status;
            aplicarFiltros(dependencies);
        });
    });
}

function renderSkeletonLoader(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    let skeletonHTML = '';
    const skeletonType = containerId.includes('grid') ? 'card' : 'list';
    for (let i = 0; i < (skeletonType === 'card' ? 3 : 4); i++) {
        skeletonHTML += skeletonType === 'card' 
            ? `<div class="skeleton-card"></div>` 
            : `<div class="skeleton-list-item"></div>`;
    }
    container.innerHTML = skeletonHTML;
}

// --- FUNÇÕES DE RENDERIZAÇÃO (Meu Painel) ---

function renderMinhasTarefas(tarefas, dependencies) {
    const container = document.getElementById('minhas-tarefas-lista');
    if (!container) return;
    container.innerHTML = '';
    if (!tarefas || tarefas.length === 0) {
        renderEmptyState(container, { icon: 'fa-check-circle', title: 'Tudo em dia!', message: 'Você não tem nenhuma tarefa aberta no momento.' });
        return;
    }
    const list = document.createElement('ul');
    list.className = 'task-list';
    tarefas.forEach(tarefa => {
        const item = document.createElement('li');
        item.className = 'task-item';
        const hoje = new Date();
        const prazo = new Date(tarefa.end);
        hoje.setHours(0, 0, 0, 0);
        const isOverdue = prazo < hoje;
        const nomeDoProjeto = tarefa.nome_projeto || `Projeto #${tarefa.id_projeto}`;
        item.innerHTML = `<div class="task-info"><a href="projeto.html?id=${tarefa.id_projeto}" class="task-name">${tarefa.name}</a><span class="task-project">${nomeDoProjeto}</span></div><div class="task-deadline ${isOverdue ? 'overdue' : ''}"><span>Prazo: ${new Date(tarefa.end).toLocaleDateString('pt-BR')}</span></div>`;
        item.addEventListener('click', (e) => { e.preventDefault(); dependencies.navigate(`projeto.html?id=${tarefa.id_projeto}`); });
        list.appendChild(item);
    });
    container.appendChild(list);
}

function renderMeusProjetosCards(projetos, dependencies) {
    const container = document.getElementById('meus-projetos-grid');
    if (!container) return;
    container.innerHTML = '';

    if (!projetos || projetos.length === 0) {
        container.innerHTML = '<p class="empty-text">Você não é responsável por nenhum projeto ativo.</p>';
        return;
    }

    projetos.forEach((projeto, index) => {
        const card = document.createElement('div');
        card.className = 'project-card small-card'; // Usa uma classe para um cartão menor
        card.addEventListener('click', () => {
            dependencies.navigate(`projeto.html?id=${projeto.id_projeto}`);
        });
        const saude = calcularSaudeProjeto(projeto);
        card.innerHTML = `
            <div class="card-header">
                <div class="health-indicator ${saude.health}" title="${saude.description}"></div>
                <h3>${projeto.nome_projeto}</h3>
            </div>
            <div class="status-info">
                <span>Status Atual</span>
                <span class="status-tag" data-status="${projeto.status_atual}">${projeto.status_atual}</span>
            </div>
        `;
        container.appendChild(card);
        card.style.animation = `fadeInCard 0.5s ease-out ${index * 0.07}s forwards`;
    });
}

// --- FUNÇÕES DE LÓGICA ---

function aplicarFiltros(dependencies) {
    const projetosFiltrados = todosOsProjetos.filter(projeto => {
        const busca = filtrosAtivos.busca.toLowerCase().trim();
        const correspondeBusca = !busca || (projeto.nome_projeto && projeto.nome_projeto.toLowerCase().includes(busca)) || (projeto.numero_topdesk && projeto.numero_topdesk.toLowerCase().includes(busca));
        const correspondeStatus = filtrosAtivos.status === 'Todos' || projeto.status_atual === filtrosAtivos.status;
        return correspondeBusca && correspondeStatus;
    });
    renderGeralProjectCards(projetosFiltrados, dependencies);
}

async function carregarVisaoGeral(dependencies) {
    renderSkeletonLoader('project-grid');
    try {
        todosOsProjetos = await api.getTodosProjetos();
        if (todosOsProjetos.length === 0) {
            renderEmptyState(document.getElementById('project-grid'), { icon: 'fa-folder-open', title: 'Bem-vindo!', message: 'Crie seu primeiro projeto para começar.', action: { text: 'Criar Novo Projeto', onClick: () => dependencies.navigate('novo_projeto.html') } });
        } else {
            renderStatusFilters(dependencies);
            aplicarFiltros(dependencies);
        }
    } catch (error) {
        renderEmptyState(document.getElementById('project-grid'), { icon: 'fa-exclamation-triangle', title: 'Erro ao Carregar', message: `Não foi possível carregar os projetos. (Erro: ${error.message})`, action: { text: 'Tentar Novamente', onClick: () => carregarVisaoGeral(dependencies) } });
    }
}

async function carregarMeuPainel(dependencies) {
    renderSkeletonLoader('minhas-tarefas-lista');
    renderSkeletonLoader('meus-projetos-grid');
    try {
        const [tarefas, projetos] = await Promise.all([
            api.getMinhasTarefas(),
            api.getMeusProjetos()
        ]);
        renderMinhasTarefas(tarefas, dependencies);
        renderMeusProjetosCards(projetos, dependencies);
    } catch (error) {
        showToast(`Erro ao carregar dados do seu painel: ${error.message}`, 'error');
        const tarefasContainer = document.getElementById('minhas-tarefas-lista');
        const projetosContainer = document.getElementById('meus-projetos-grid');
        if (tarefasContainer) renderEmptyState(tarefasContainer, { icon: 'fa-exclamation-triangle', title: 'Erro', message: 'Não foi possível carregar suas tarefas.' });
        if (projetosContainer) renderEmptyState(projetosContainer, { icon: 'fa-exclamation-triangle', title: 'Erro', message: 'Não foi possível carregar seus projetos.' });
    }
}

// --- FUNÇÃO DE INICIALIZAÇÃO ---

export function initializePage(dependencies) {
    console.log("[dashboard.js] Inicializando o dashboard unificado...");
    
    const toggle = document.getElementById('dashboard-toggle');
    const visaoGeralContainer = document.getElementById('visao-geral-container');
    const meuPainelContainer = document.getElementById('meu-painel-container');

    function switchView(isMeuPainel) {
        if (isMeuPainel) {
            visaoGeralContainer.classList.remove('active');
            meuPainelContainer.classList.add('active');
            if (!meuPainelContainer.dataset.loaded) {
                carregarMeuPainel(dependencies);
                meuPainelContainer.dataset.loaded = 'true';
            }
        } else {
            meuPainelContainer.classList.remove('active');
            visaoGeralContainer.classList.add('active');
            if (!visaoGeralContainer.dataset.loaded) {
                carregarVisaoGeral(dependencies);
                visaoGeralContainer.dataset.loaded = 'true';
            }
        }
    }

    if (toggle && visaoGeralContainer && meuPainelContainer) {
        toggle.addEventListener('change', (event) => {
            switchView(event.target.checked);
        });
        switchView(false);
    }

    const newProjectBtn = document.querySelector('.new-project-btn');
    if (newProjectBtn && !dependencies.auth.canCreateProject()) {
        newProjectBtn.style.display = 'none';
    }

    let debounceTimer;
    const savedStateJSON = sessionStorage.getItem('appState');
    if (savedStateJSON) {
        try {
            const state = JSON.parse(savedStateJSON);
            if (state && typeof state.filters === 'object') {
                filtrosAtivos = state.filters;
            }
            sessionStorage.removeItem('appState');
        } catch (e) {
            sessionStorage.removeItem('appState');
        }
    }

    if (savedStateJSON) {
        try {
            const state = JSON.parse(savedStateJSON);
            if (state && typeof state.scrollPos === 'number') {
                // A rolagem é restaurada após o carregamento dos projetos
            }
        } catch(e) { /* Ignora */ }
    }

    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = filtrosAtivos.busca;
        searchInput.addEventListener('keyup', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                filtrosAtivos.busca = e.target.value;
                aplicarFiltros(dependencies);
            }, 300);
        });
    }
}