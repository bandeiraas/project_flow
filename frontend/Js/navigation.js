/**
 * Navega para uma nova URL com uma animação de fade-out.
 * Opcionalmente, salva um estado na sessionStorage antes de navegar.
 * @param {string} url - A URL de destino.
 * @param {object} [stateToSave={}] - Um objeto opcional para salvar na sessionStorage.
 */
export function navigateWithTransition(url, stateToSave = {}) {
    // Salva o estado na sessionStorage para ser recuperado na próxima página.
    // Usado para lembrar a posição de rolagem e os filtros.
    sessionStorage.setItem('appState', JSON.stringify(stateToSave));

    // Aplica a animação de fade-out ao corpo da página.
    document.body.style.animation = 'fadeOutPage 0.3s ease-in-out forwards';
    
    // Espera a animação terminar (300ms) antes de realmente mudar de página.
    setTimeout(() => {
        window.location.href = url;
    }, 300);
}

/**
 * Adiciona os keyframes da animação de fade-out ao CSS da página.
 * Isso é feito via JS para manter a lógica de navegação encapsulada.
 */
function addAnimationStyles() {
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes fadeOutPage {
            from { opacity: 1; }
            to { opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}

// Adiciona os estilos de animação assim que o script é carregado.
addAnimationStyles();