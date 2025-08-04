// Importa a URL base da API do arquivo de configuração central.
import API_BASE_URL from './config.js';

/**
 * Função INTERNA para lidar com erros da API.
 * Trata diferentes tipos de erros HTTP e retorna mensagens apropriadas.
 */
async function _handleApiError(response) {
    let errorMessage = `Erro ${response.status}: ${response.statusText}`;
    
    try {
        const errorData = await response.json();
        if (errorData.detail) {
            errorMessage = errorData.detail;
        } else if (errorData.message) {
            errorMessage = errorData.message;
        }
    } catch (e) {
        // Se não conseguir ler o JSON, usa a mensagem padrão.
        // Logar o erro de parsing é útil para depuração.
        console.warn('[apiService] Falha ao analisar o corpo do erro como JSON.', e);
    }
    
    const error = new Error(errorMessage);
    error.status = response.status;
    error.statusText = response.statusText;
    
    console.error(`[apiService] Erro da API (${response.status}):`, errorMessage);
    throw error;
}

/**
 * Função genérica INTERNA para fazer requisições fetch.
 * Automaticamente adiciona o token de autenticação e lida com erros comuns.
 */
// Em apiService.js
/**
 * Função genérica INTERNA para fazer requisições fetch.
 * Automaticamente adiciona o token de autenticação e lida com erros comuns.
 * Lida corretamente com requisições JSON e uploads de arquivos (FormData).
 */
async function _request(endpoint, options = {}) {
    // Pega o token salvo no localStorage a cada requisição
    const token = localStorage.getItem('accessToken');

    // Inicia com os cabeçalhos que foram passados (se houver)
    const headers = new Headers(options.headers || {});

    // --- LÓGICA DE CABEÇALHO CORRIGIDA ---
    // Se o corpo da requisição existe E NÃO é um FormData,
    // então assumimos que é um JSON e definimos o Content-Type.
    // Se for um FormData, NÃO definimos o Content-Type, pois o navegador
    // precisa fazer isso automaticamente (com o 'boundary' correto).
    if (options.body && !(options.body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
    }

    // Se um token existir, adiciona-o ao cabeçalho 'Authorization'
    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options, // Mantém as opções originais (method, body)
            headers: headers // Usa os novos cabeçalhos
        });

        // Se a resposta não for OK, trata os erros
        if (!response.ok) {
            await _handleApiError(response);
        }
        
        // Se a resposta for '204 No Content', retorna null.
        if (response.status === 204) return null;
        
        // Se tudo deu certo, retorna o JSON.
        return response.json();

    } catch (error) {
        // Melhora a mensagem de erro para problemas de conexão.
        if (error instanceof TypeError && error.message === 'Failed to fetch') {
            const connectionError = new Error(
                `Erro de Conexão: Não foi possível se comunicar com o servidor. ` +
                `Verifique se o backend está rodando em ${API_BASE_URL} e se não há problemas de rede ou CORS.`
            );
            console.error(`[apiService] Falha de conexão para ${endpoint}:`, connectionError, error);
            throw connectionError;
        }
        console.error(`[apiService] Erro inesperado na chamada para ${endpoint}:`, error);
        throw error; // Propaga outros erros
    }
}

/**
 * Objeto que centraliza todas as funções de chamada à API.
 */
export const api = {
    // --- MÉTODOS DE AUTENTICAÇÃO ---
    login: (email, senha) => {
        return _request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, senha })
        });
    },
    // Adicione register aqui se precisar no futuro

    // --- MÉTODOS GENÉRICOS E DE PROJETO ---
    getGeneric: (endpoint) => _request(endpoint),
    getProjetoSchema: () => _request('/projetos/schema'),
    getTodosProjetos: () => _request('/projetos'),
    getProjetoPorId: (id) => _request(`/projetos/${id}`),
    createProjeto: (data) => _request('/projetos', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    updateProjeto: (id, data) => _request(`/projetos/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    updateStatusProjeto: (id, data) => _request(`/projetos/${id}/status`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    deleteProjeto: (id) => _request(`/projetos/${id}`, {
        method: 'DELETE'
    }),
    iniciarCicloHomologacao: (idProjeto, data) => _request(`/projetos/${idProjeto}/homologacao/iniciar`, {
        method: 'POST',
        body: JSON.stringify(data)
    }),
// Em apiService.js, dentro do objeto 'api'

    finalizarCicloHomologacao: (idProjeto, data) => {
        // --- CORREÇÃO AQUI ---
        // A função agora aceita apenas o ID do projeto e o objeto de dados.
        // Ela não envia mais o 'novo_status_alvo'.
        return _request(`/projetos/${idProjeto}/homologacao/finalizar`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    // Em apiService.js, dentro do objeto 'export const api = { ... }'
    getMe: () => {
        return _request('/auth/me');
    },
    // Em apiService.js, dentro do objeto 'export const api = { ... }'

    // --- NOVO MÉTODO PARA REGISTRO ---
    register: (nome_completo, email, senha) => {
        return _request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ nome_completo, email, senha })
        });
    },
    updateUserRole: (userId, newRole) => {
    return _request(`/admin/users/${userId}/role`, {
        method: 'PUT',
        body: JSON.stringify({ role: newRole })
    });
    },
    // Em apiService.js
    updateProfile: (data) => {
        return _request('/profile', {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    getRelatorioPortfolio: () => {
        return _request('/relatorios/portfolio');
    },
    // Em apiService.js
    createTarefa: (idProjeto, data) => {
        return _request(`/projetos/${idProjeto}/tarefas`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    // Em apiService.js
    updateTarefa: (idTarefa, data) => {
        return _request(`/tarefas/${idTarefa}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    // Em apiService.js
    deleteTarefa: (idTarefa) => {
        return _request(`/tarefas/${idTarefa}`, {
            method: 'DELETE'
        });
    },
    // Em apiService.js
    getMinhasTarefas: () => {
        return _request('/me/tarefas');
    },
    // Em apiService.js
    getMeusProjetos: () => {
        return _request('/me/projetos');
    },
    uploadRelatorio: (idHomologacao, formData) => {
        return _request(`/homologacoes/${idHomologacao}/upload-zip`, {
            method: 'POST',
            body: formData // Passa o FormData diretamente
        });
    },
    // Em apiService.js
    processarRelatorio: (idHomologacao) => {
        return _request(`/homologacoes/${idHomologacao}/processar-relatorio`, {
            method: 'POST'
        });
    },
    getTestesDoCiclo: (idHomologacao) => {
        return _request(`/homologacoes/${idHomologacao}/testes`);
    },
    // Em apiService.js
    getRelatorioQa: () => {
        return _request('/relatorios/qa');
    },
};
