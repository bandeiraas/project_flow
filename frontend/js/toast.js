/**
 * Exibe uma notificação (toast) na tela.
 * @param {string} message - A mensagem a ser exibida.
 * @param {string} [type='info'] - O tipo de toast ('info', 'success', 'error').
 * @param {number} [duration=4000] - A duração em milissegundos que o toast ficará visível.
 */
export function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container');
    if (!container) {
        console.error("Container de toast (#toast-container) não encontrado no DOM.");
        return;
    }

    // 1. Cria o elemento do toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    // 2. Adiciona o toast ao container
    container.appendChild(toast);

    // 3. Força o "repaint" do navegador e adiciona a classe 'show' para a animação de entrada
    //    O setTimeout garante que a transição CSS seja acionada.
    setTimeout(() => {
        toast.classList.add('show');
    }, 10); // Um pequeno delay é suficiente

    // 4. Define um timer para remover o toast
    setTimeout(() => {
        // Inicia a animação de saída
        toast.classList.remove('show');
        
        // --- LÓGICA CORRIGIDA ---
        // Define um outro timer para remover o elemento do DOM DEPOIS
        // que a animação de saída (definida no CSS) terminar.
        // Isso evita depender do evento 'transitionend'.
        setTimeout(() => {
            // Verifica se o toast ainda existe no DOM antes de tentar removê-lo
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 500); // Este tempo deve ser igual ou maior que a duração da transição no CSS

    }, duration);
}