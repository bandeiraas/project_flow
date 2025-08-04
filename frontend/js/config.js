// frontend/js/config.js

// Centraliza a URL base da API para ser usada em toda a aplicação.
// A URL deve incluir o prefixo /api que o backend espera.

// Detecta automaticamente se está rodando no GitHub Codespaces
const isCodespaces = window.location.hostname.includes('.app.github.dev');

let API_BASE_URL;

if (isCodespaces) {
    // Em GitHub Codespaces, extrai o nome do codespace e constrói a URL do backend
    const hostname = window.location.hostname;
    console.log('🔍 Hostname atual:', hostname);
    
    // Extrai o nome base do codespace (parte antes da primeira porta)
    // Exemplo: "stunning-happiness-wqxqv69j6xfg956-8080.app.github.dev" 
    // -> "stunning-happiness-wqxqv69j6xfg956"
    const codespaceName = hostname.split('-').slice(0, -1).join('-');
    console.log('📝 Nome do codespace extraído:', codespaceName);
    
    // Constrói a URL do backend na porta 5000
    API_BASE_URL = `https://${codespaceName}-5000.app.github.dev/api`;
} else {
    // Em desenvolvimento local, usa localhost
    API_BASE_URL = 'http://localhost:5000/api';
}

console.log('🔗 API Base URL configurada:', API_BASE_URL);

export default API_BASE_URL;