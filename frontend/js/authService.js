
import { api } from './apiService.js';

// Objeto que manterá os dados do usuário em memória
let currentUser = null;

const authService = {
    /**
     * Busca os dados do usuário da API (/api/auth/me) e os armazena.
     * Deve ser chamado no início da aplicação.
     * @returns {Promise<object|null>}
     */
    async fetchUser() {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            currentUser = null;
            return null;
        }
        try {
            // api.getMe() será adicionado ao apiService.js
            currentUser = await api.getMe();
            console.log("[authService] Dados do usuário carregados:", currentUser);
            return currentUser;
        } catch (error) {
            console.error("[authService] Falha ao buscar dados do usuário, limpando sessão:", error);
            this.logout();
            return null;
        }
    },

    /**
     * Retorna os dados do usuário atualmente logado.
     * @returns {object|null}
     */
    getUser() {
        return currentUser;
    },

    /**
     * Verifica se o usuário está logado.
     * @returns {boolean}
     */
    isLoggedIn() {
        return !!currentUser;
    },

    /**
     * Faz o logout do usuário, limpando o estado e o token.
     */
    logout() {
        currentUser = null;
        localStorage.removeItem('accessToken');
        window.location.href = 'login.html';
    },

    // --- FUNÇÕES DE VERIFICAÇÃO DE PERMISSÃO ---
    // Estas funções espelham as regras definidas no security.py do backend.

    canCreateProject() {
        if (!this.isLoggedIn()) return false;
        return ['Admin', 'Gerente', 'Membro'].includes(currentUser.role);
    },

    canEditProject(projeto) {
        if (!this.isLoggedIn() || !projeto || !projeto.responsavel) return false;
        return ['Admin', 'Gerente'].includes(currentUser.role) || currentUser.id_usuario === projeto.responsavel.id_usuario;
    },

    canDeleteProject(projeto) {
        if (!this.isLoggedIn() || !projeto || !projeto.responsavel) return false;
        return ['Admin', 'Gerente'].includes(currentUser.role) || currentUser.id_usuario === projeto.responsavel.id_usuario;
    }
};

export default authService;