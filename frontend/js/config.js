// frontend/js/config.js

// Centraliza a URL base da API para ser usada em toda a aplicação.
// A URL deve incluir o prefixo /api que o backend espera.

// Detecta automaticamente se está rodando no GitHub Codespaces
const isCodespaces = window.location.hostname.includes('.app.github.dev');

let API_BASE_URL;

if (isCodespaces) {
    // Em GitHub Codespaces, usa a URL atual mas troca a porta para 5000
    const currentUrl = window.location.origin;
    // Substitui a porta atual por 5000 para o backend
    API_BASE_URL = currentUrl.replace(/:\d+/, '') + '-5000.app.github.dev/api';
} else {
    // Em desenvolvimento local, usa localhost
    API_BASE_URL = 'http://localhost:5000/api';
}

console.log('🔗 API Base URL configurada:', API_BASE_URL);

export default API_BASE_URL;