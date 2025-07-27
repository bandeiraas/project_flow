// --- CONSTANTES DE UI ---

// Mapeamento de status para ícones do Font Awesome
export const statusIcons = { 
  "Em Definição": "fas fa-search", 
  "Em Especificação": "fas fa-pencil-ruler", 
  "Espeficação Aprovada": "fas fa-check-double",
  "Em Desenvolvimento": "fas fa-code", 
  "Em Homologação": "fas fa-vial", 
  "Pendente de Implantação": "fas fa-box-open", 
  "Pós GMUD": "fas fa-flag-checkered", 
  "Projeto concluído": "fas fa-check-double",
  "Cancelado": "fas fa-times-circle" 
};

// Paleta de cores para os avatares de usuário
export const avatarColors = [
    '#4A69BD', '#1ABC9C', '#8E44AD', '#E74C3C', 
    '#27AE60', '#2980B9', '#D35400'
];


// --- FUNÇÕES HELPER DE FORMATAÇÃO E CÁLCULO ---

/**
 * Formata uma data ISO para o padrão brasileiro (DD/MM/AAAA).
 */
export function formatarData(isoString) { 
    if (!isoString) return 'N/D'; 
    return new Date(isoString).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' }); 
}

/**
 * Calcula a diferença em dias entre duas datas no formato ISO.
 */
export function calcularDiferencaDias(dataInicioISO, dataFimISO) { 
    if (!dataInicioISO || !dataFimISO) return null; 
    const inicio = new Date(dataInicioISO); 
    const fim = new Date(dataFimISO); 
    if (isNaN(inicio) || isNaN(fim)) return null; 
    const diffTime = fim.getTime() - inicio.getTime(); 
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
}

/**
 * Calcula a "saúde" de um projeto com base em suas métricas.
 */
export function calcularSaudeProjeto(projeto) {
    const hoje = new Date();
    const fimPrevisto = projeto.data_fim_prevista ? new Date(projeto.data_fim_prevista) : null;

    if (fimPrevisto && hoje > fimPrevisto && !projeto.data_fim_real) {
        return { health: 'danger', description: 'Projeto Atrasado' };
    }
    if (projeto.prioridade === 'Crítica' && projeto.risco === 'Alto') {
        return { health: 'danger', description: 'Prioridade Crítica com Risco Alto' };
    }
    if (projeto.risco === 'Alto') {
        return { health: 'warning', description: 'Risco Alto' };
    }
    if (projeto.complexidade === 'Alta') {
        return { health: 'warning', description: 'Complexidade Alta' };
    }
    if (fimPrevisto && !projeto.data_fim_real) {
        const diffDays = calcularDiferencaDias(hoje.toISOString(), projeto.data_fim_prevista);
        if (diffDays <= 7 && diffDays >= 0) {
            return { health: 'warning', description: `Prazo terminando em ${diffDays} dia(s)` };
        }
    }
    return { health: 'success', description: 'No Prazo e com riscos controlados' };
}


// --- FUNÇÕES HELPER DE MANIPULAÇÃO DO DOM ---

/**
 * Gera o HTML para um avatar de usuário com iniciais e cor consistente.
 */
export function criarAvatar(nomeCompleto, idUsuario) {
    if (!nomeCompleto || !idUsuario) return `<div class="user-avatar"><i class="fas fa-user"></i></div>`;
    const partesNome = nomeCompleto.trim().split(' ');
    let iniciais = partesNome[0].charAt(0);
    if (partesNome.length > 1) iniciais += partesNome[partesNome.length - 1].charAt(0);
    const cor = avatarColors[idUsuario % avatarColors.length];
    return `<div class="user-avatar" style="background-color: ${cor};">${iniciais.toUpperCase()}</div>`;
}

/**
 * Adiciona um ícone "copiar" ao lado de um elemento.
 */
export function addCopyToClipboard(elementId, textToCopy, showToast) {
    const element = document.getElementById(elementId);
    if (!element || !textToCopy) return;
    // Evita adicionar múltiplos ícones
    if (element.parentNode.querySelector('.copy-icon')) return;

    const icon = document.createElement('i');
    icon.className = 'fas fa-copy copy-icon';
    icon.title = 'Copiar';
    icon.addEventListener('click', (e) => {
        e.stopPropagation();
        navigator.clipboard.writeText(textToCopy).then(() => showToast(`'${textToCopy}' copiado!`, 'success'));
    });
    element.parentNode.appendChild(icon);
}

/**
 * Renderiza um componente de estado vazio ou de erro em um container.
 */
export function renderEmptyState(container, { icon, title, message, action }) {
    if (!container) return;
    container.innerHTML = `
        <div class="empty-state">
            <i class="fas ${icon}"></i>
            <h3>${title}</h3>
            <p>${message}</p>
            ${action ? `<button id="empty-state-action-btn" class="btn-primary">${action.text}</button>` : ''}
        </div>
    `;

    if (action && action.onClick) {
        const actionButton = document.getElementById('empty-state-action-btn');
        if (actionButton) {
            actionButton.addEventListener('click', action.onClick);
        }
    }
}

// Em uiHelpers.js

// ... (outras funções exportadas) ...

/**
 * Renderiza um gráfico de linha genérico.
 * @param {string} canvasId - O ID do elemento <canvas>.
 * @param {object} dados - Os dados para o gráfico, com { labels, data }.
 * @param {string} label - O rótulo para o dataset.
 */
export function renderGraficoLinha(canvasId, dados, label) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    if (Chart.getChart(canvasId)) {
        Chart.getChart(canvasId).destroy();
    }

    const isDarkMode = document.body.classList.contains('dark-mode');
    const textColor = isDarkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(54, 54, 54, 0.8)';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    const lineColor = isDarkMode ? '#74b9ff' : '#4A69BD';

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dados.labels,
            datasets: [{
                label: label,
                data: dados.data,
                borderColor: lineColor,
                backgroundColor: `${lineColor}33`,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { color: textColor },
                    grid: { color: gridColor }
                },
                x: {
                    ticks: { color: textColor },
                    grid: { color: gridColor }
                }
            }
        }
    });
}