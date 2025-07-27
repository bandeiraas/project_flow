// frontend/js/colors.js

// Cores baseadas nas variáveis do nosso CSS para consistência
const themeColors = {
    primary: '#4A69BD',
    danger: '#E74C3C',
    warning: '#F39C12',
    success: '#2ECC71',
    purple: '#8E44AD',
    gray: '#95A5A6',
    blue: '#3498DB',
    green_dark: '#27ae60'
};

// Mapeamento de valores específicos para cores
export const statusColors = {
    'Aprovado': themeColors.success,
    'Pós GMUD': themeColors.success,
    'Em Desenvolvimento': themeColors.primary,
    'Em Homologação': themeColors.blue,
    'Pendente de Implantação': themeColors.warning,
    'Cancelado': themeColors.danger,
    'Em Definição': themeColors.gray,
    'Em Especificação': themeColors.gray,
    'default': themeColors.gray
};

export const priorityColors = {
    'Crítica': '#c0392b', // Vermelho mais escuro
    'Alta': themeColors.danger,
    'Média': themeColors.warning,
    'Baixa': themeColors.primary,
    'default': themeColors.gray
};

// Você pode adicionar outros mapeamentos aqui no futuro
// export const riskColors = { ... };