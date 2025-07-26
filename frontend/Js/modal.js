export class Modal {
    constructor() {
        this.modalContainer = document.getElementById('modal-container');
        this.modalContent = this.modalContainer?.querySelector('.modal-content');
        this.modalTitle = document.getElementById('modal-title');
        this.modalBody = document.getElementById('modal-body'); 
        this.modalActions = this.modalContainer?.querySelector('.modal-actions');
        this.confirmBtn = document.getElementById('modal-confirm-btn');
        this.cancelBtn = document.getElementById('modal-cancel-btn');
        this.resolvePromise = null;

        if (!this.modalContainer || !this.confirmBtn || !this.cancelBtn || !this.modalBody) {
            console.error("[Modal] Elementos essenciais do modal não encontrados. A inicialização falhou.");
            return;
        }

        this._addEventListeners();
        console.log("[Modal] Componente instanciado e inicializado.");
    }

    /**
     * Adiciona os listeners de evento usando delegação para maior robustez.
     */
    _addEventListeners() {
        // Adiciona um único listener ao container do modal
        this.modalContainer.addEventListener('click', (event) => {
            const target = event.target;

            // Se o clique foi no botão de confirmação
            if (target.closest('#modal-confirm-btn')) {
                this._resolve(true);
                return;
            }

            // Se o clique foi no botão de cancelar
            if (target.closest('#modal-cancel-btn')) {
                this._resolve(false);
                return;
            }

            // Se o clique foi no botão extra
            if (target.closest('#modal-extra-btn')) {
                this._resolve('extra'); // Resolve com um valor especial
                return;
            }

            // Se o clique foi no fundo (overlay)
            if (target === this.modalContainer) {
                this._resolve(false);
                return;
            }
        });
    }

    /**
     * Resolve a promessa do modal com o valor apropriado.
     * @param {boolean|string} value - O resultado da interação do usuário.
     */
    _resolve(value) {
        if (this.resolvePromise) {
            // Retorna um objeto com o status da confirmação e o container do modal
            this.resolvePromise({ 
                confirmed: value, 
                modalContainer: this.modalContainer 
            });
        }
        this._hide();
    }

    /**
     * Esconde o modal e limpa o estado da promessa.
     */
    _hide() {
        this.modalContainer.classList.remove('show');
        this.resolvePromise = null;
    }

    /**
     * Mostra o modal com conteúdo e botões customizados.
     * @returns {Promise<{confirmed: boolean|string, modalContainer: HTMLElement}>}
     */
    show({ title, message, htmlContent, confirmText = 'Confirmar', cancelText = 'Cancelar', extraButton = null }) {
        if (!this.modalContainer) {
            console.error("O modal não foi inicializado corretamente.");
            return Promise.resolve({ confirmed: false, modalContainer: null });
        }

        this.modalTitle.textContent = title;
        
        if (htmlContent) {
            this.modalBody.innerHTML = htmlContent;
        } else {
            this.modalBody.innerHTML = `<p>${message || ''}</p>`;
        }

        this.confirmBtn.textContent = confirmText;
        this.cancelBtn.textContent = cancelText;
        
        // --- LÓGICA PARA RENDERIZAR O BOTÃO EXTRA ---
        // Remove qualquer botão extra antigo para evitar duplicatas
        this.modalActions.querySelector('#modal-extra-btn')?.remove();

        if (extraButton) {
            const btn = document.createElement('button');
            btn.id = 'modal-extra-btn';
            btn.className = `modal-btn ${extraButton.className || 'secondary'}`;
            btn.textContent = extraButton.text;
            // Insere o botão extra no início da área de ações
            this.modalActions.prepend(btn);
        }

        this.modalContainer.classList.add('show');

        return new Promise((resolve) => {
            this.resolvePromise = resolve;
        });
    }
}