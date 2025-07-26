// frontend/js/layout-loader.js

/**
 * Carrega um único componente HTML em um elemento placeholder.
 */
async function loadComponent(elementId, filePath) {
    const placeholder = document.getElementById(elementId);
    if (!placeholder) {
        console.warn(`[Layout Loader] Placeholder '${elementId}' não encontrado.`);
        return;
    }
    try {
        const response = await fetch(filePath);
        if (!response.ok) throw new Error(`Falha ao buscar ${filePath}`);
        const html = await response.text();
        placeholder.outerHTML = html;
    } catch (error) {
        console.error(`[Layout Loader] Erro ao carregar '${filePath}':`, error);
        placeholder.innerHTML = `<p style="color: red;">Erro ao carregar componente.</p>`;
    }
}

/**
 * Orquestra o carregamento de todos os componentes reutilizáveis do layout.
 * ESTA FUNÇÃO PRECISA SER EXPORTADA para que o main.js possa importá-la.
 * @returns {Promise<void>}
 */
async function loadLayout() {
    console.log("[Layout Loader] Iniciando carregamento de todos os componentes...");
    
    const componentPromises = [
        loadComponent('main-header-placeholder', 'components/header.html'),
        loadComponent('modal-placeholder', 'components/modal.html')
    ];

    return Promise.all(componentPromises);
}
