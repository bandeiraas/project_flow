// Importa as CLASSES dos componentes globais
import { Modal } from './modal.js';
import { ThemeToggle } from './theme-toggle.js';

// Importa as FUNÇÕES de utilidade
import { navigateWithTransition } from './navigation.js';
import authService from './authService.js';
import { showToast } from './toast.js';

// --- CACHE BUSTER HELPER ---
const cacheBuster = `?v=${new Date().getTime()}`;

/**
 * Importa o módulo de script de uma página dinamicamente.
 */
const importPageScript = (page) => {
    switch (page) {
        case 'index.html':
            return import(`./dashboard.js${cacheBuster}`);
        case 'projeto.html':
            return import(`./projeto.js${cacheBuster}`);
        case 'novo_projeto.html':
            return import(`./novo_projeto.js${cacheBuster}`);
        case 'editar_projeto.html':
            return import(`./editar_projeto.js${cacheBuster}`);
        case 'configuracoes.html':
            return import(`./configuracoes.js${cacheBuster}`);
        case 'perfil.html':
            return import(`./perfil.js${cacheBuster}`);
        case 'insights.html':
            return import(`./insights.js${cacheBuster}`);
        default:
            return Promise.reject(new Error(`Nenhum script encontrado para a página: ${page}`));
    }
};

// --- FUNÇÃO HELPER PARA AVATAR ---
const avatarColors = ['#4A69BD', '#1ABC9C', '#8E44AD', '#E74C3C', '#27AE60', '#2980B9', '#D35400'];
function criarAvatar(nomeCompleto, idUsuario) {
    if (!nomeCompleto || !idUsuario) return `<div class="user-avatar"><i class="fas fa-user"></i></div>`;
    const partesNome = nomeCompleto.trim().split(' ');
    let iniciais = partesNome[0].charAt(0);
    if (partesNome.length > 1) iniciais += partesNome[partesNome.length - 1].charAt(0);
    const cor = avatarColors[idUsuario % avatarColors.length];
    return `<div class="user-avatar" style="background-color: ${cor};">${iniciais.toUpperCase()}</div>`;
}

/**
 * Inicializa todas as funcionalidades GLOBAIS da UI.
 */
function initializeGlobalUI(dependencies) {
    console.log("[main.js] Inicializando UI Global...");
    const { auth } = dependencies;

    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const body = document.body;

    if (!sidebar || !overlay) {
        console.error("[main.js] Elementos da Sidebar/Overlay não encontrados.");
        return;
    }

    document.addEventListener('click', (event) => {
        const target = event.target;
        if (target.closest('#hamburger-btn')) {
            event.preventDefault();
            body.classList.toggle('sidebar-open');
            return;
        }
        if (target.closest('#overlay')) {
            body.classList.remove('sidebar-open');
            return;
        }
        const newProjectBtn = target.closest('.new-project-btn');
        if (newProjectBtn) {
            event.preventDefault();
            if (body.classList.contains('sidebar-open')) {
                body.classList.remove('sidebar-open');
            }
            dependencies.navigate('novo_projeto.html');
            return;
        }
        const logoutBtn = target.closest('#logout-btn');
        if (logoutBtn) {
            event.preventDefault();
            authService.logout();
            showToast('Você saiu com sucesso.', 'info');
            return;
        }
        const navLink = target.closest('a.nav-link, a.logo');
        if (navLink && navLink.getAttribute('href') !== '#') {
            event.preventDefault();
            const destination = navLink.getAttribute('href');
            if (body.classList.contains('sidebar-open')) {
                body.classList.remove('sidebar-open');
            }
            dependencies.navigate(destination);
            return;
        }
    });
    
    const user = auth.getUser();
    if (user) {
        const sidebarAvatar = document.getElementById('sidebar-avatar');
        const sidebarUsername = document.getElementById('sidebar-username');
        const sidebarUserRole = document.getElementById('sidebar-user-role');
        if (sidebarAvatar) {
            sidebarAvatar.innerHTML = criarAvatar(user.nome_completo, user.id_usuario);
        }
        if (sidebarUsername) {
            sidebarUsername.textContent = user.nome_completo;
        }
        if (sidebarUserRole) {
            sidebarUserRole.textContent = user.role;
        }
    }

    const allNavLinks = document.querySelectorAll('a.logo, a.nav-link');
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    allNavLinks.forEach(link => {
        const linkPage = link.getAttribute('href').split('/').pop();
        link.classList.remove('active');
        if (linkPage === currentPage || (currentPage === '' && linkPage === 'index.html')) {
            link.classList.add('active');
        }
    });
}

/**
 * Roteador que carrega e executa o código específico da página atual.
 */
function routePage(dependencies) {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    console.log(`[main.js] Roteando para a lógica da página: ${currentPage}`);
    
    importPageScript(currentPage)
        .then(pageModule => {
            if (pageModule.initializePage) {
                pageModule.initializePage(dependencies);
            } else {
                console.error(`[main.js] O módulo para '${currentPage}' não exporta 'initializePage'.`);
            }
        })
        .catch(error => {
            console.warn(`[main.js] Não foi possível carregar o script para '${currentPage}':`, error);
        });
}

/**
 * Ponto de entrada principal da aplicação.
 */
async function main() {
    console.log("[main.js] Função 'main' iniciada.");

    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const publicPages = ['login.html', 'registro.html'];
    const token = localStorage.getItem('accessToken');

    // --- FLUXO DE AUTENTICAÇÃO E ROTEAMENTO CORRIGIDO ---
    
    // 1. Se estamos em uma página protegida e não há token, redireciona imediatamente.
    if (!publicPages.includes(currentPage) && !token) {
        console.log("[main.js] Acesso negado (sem token). Redirecionando para o login.");
        window.location.href = 'login.html';
        return;
    }

    // 2. Se existe um token, TENTA buscar os dados do usuário.
    if (token) {
        try {
            await authService.fetchUser();
        } catch (error) {
            // Se fetchUser falhar (token inválido), o próprio authService já redireciona.
            // A execução aqui será interrompida, o que está correto.
            console.error("[main.js] Falha no fetchUser, o authService deve ter redirecionado.");
            return;
        }
    }

    // 3. AGORA que o estado de login está definido, fazemos as outras verificações.
    
    // Se o usuário está logado e tenta acessar uma página pública, redireciona para o dashboard.
    if (publicPages.includes(currentPage) && authService.isLoggedIn()) {
        console.log("[main.js] Usuário já logado em página pública. Redirecionando para o dashboard.");
        window.location.href = 'index.html';
        return;
    }

    // Se for uma página pública (e o usuário não está logado), apenas carrega o script da página.
    if (publicPages.includes(currentPage)) {
        console.log(`[main.js] Em página pública (${currentPage}), carregando script específico.`);
        routePage({}); // Passa um objeto vazio de dependências
        return;
    }
    
    // --- INICIALIZAÇÃO DA APLICAÇÃO (APENAS PARA PÁGINAS PROTEGIDAS) ---
    try {
        await window.loadLayout();
        console.log("[main.js] Layout HTML carregado.");

        const dependencies = {
            modal: new Modal(),
            themeToggle: new ThemeToggle(),
            navigate: navigateWithTransition,
            auth: authService
        };
        console.log("[main.js] Dependências globais instanciadas.");

        initializeGlobalUI(dependencies);
        routePage(dependencies);

    } catch (error) {
        console.error("[main.js] Erro fatal na inicialização da aplicação:", error);
        authService.logout();
    }
}

// Dispara a execução principal quando o DOM estiver pronto.
document.addEventListener('DOMContentLoaded', main);