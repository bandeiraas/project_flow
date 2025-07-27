// frontend/js/theme-toggle.js

export class ThemeToggle {
    constructor() {
        this.themeToggleButton = document.getElementById('theme-toggle-btn');
        this.body = document.body;

        if (!this.themeToggleButton) {
            console.error("[ThemeToggle] Botão de tema não encontrado no DOM.");
            return;
        }

        this._addEventListeners();
        this._applyInitialTheme();
        console.log("[ThemeToggle] Componente instanciado e inicializado.");
    }

    _addEventListeners() {
        this.themeToggleButton.addEventListener('click', () => {
            const newTheme = this.body.classList.contains('dark-mode') ? 'light' : 'dark';
            localStorage.setItem('theme', newTheme);
            this._applyTheme(newTheme);
        });
    }

    _applyInitialTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this._applyTheme(savedTheme);
    }

    /**
     * Aplica o tema visualmente e dispara um evento para notificar outros componentes.
     * @param {string} theme - O tema a ser aplicado ('light' ou 'dark').
     */
    _applyTheme(theme) {
        // Aplica a classe ao body e atualiza o ícone
        if (theme === 'dark') {
            this.body.classList.add('dark-mode');
            this.themeToggleButton.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            this.body.classList.remove('dark-mode');
            this.themeToggleButton.innerHTML = '<i class="fas fa-moon"></i>';
        }

        // --- LÓGICA DE EVENTO ---
        // Dispara um evento customizado no documento para que outros módulos
        // possam "ouvir" a mudança de tema sem acoplamento direto.
        console.log(`[ThemeToggle] Disparando evento 'theme:changed' com o tema: ${theme}`);
        document.dispatchEvent(new CustomEvent('theme:changed', { 
            detail: { theme: theme } 
        }));
    }
}