import { api } from './apiService.js';
import { showToast } from './toast.js';

// Mapeamento de ícones para os campos do formulário
const fieldIcons = {
    nome_projeto: 'fa-signature',
    descricao: 'fa-align-left',
    numero_topdesk: 'fa-ticket-alt',
    id_responsavel: 'fa-user-tie',
    id_area_solicitante: 'fa-building',
    equipe_ids: 'fa-users',
    prioridade: 'fa-layer-group',
    complexidade: 'fa-puzzle-piece',
    risco: 'fa-exclamation-triangle',
    link_documentacao: 'fa-link',
    data_inicio_prevista: 'fa-calendar-day',
    data_fim_prevista: 'fa-calendar-check'
};


/**
 * Gera um único campo de formulário com base em sua definição no esquema.
 * @param {object} field - O objeto de definição do campo.
 * @param {object} auth - A instância do authService para verificação de permissões.
 * @returns {Promise<HTMLElement>} - Uma promessa que resolve com o elemento do campo.
 */
async function createFormField(field, auth) {
    const formGroup = document.createElement('div');
    formGroup.className = 'form-group';

    const iconClass = fieldIcons[field.name] || 'fa-question-circle';
    const isRequired = field.required ? 'required' : '';

    let fieldHtml = `<label for="${field.name}"><i class="fas ${iconClass}"></i> ${field.label}</label>`;
    
    // Lógica de permissão para o campo 'id_responsavel'
    if (field.name === 'id_responsavel') {
        const user = auth.getUser();
        if (user && !['Admin', 'Gerente'].includes(user.role)) {
            fieldHtml += `<input type="text" class="disabled-input" value="${user.nome_completo}" disabled>`;
            fieldHtml += `<input type="hidden" id="id_responsavel" name="id_responsavel" value="${user.id_usuario}">`;
            formGroup.innerHTML = fieldHtml;
            return formGroup;
        }
    }
    
    // Lógica padrão de renderização
    switch (field.type) {
        case 'textarea':
            fieldHtml += `<textarea id="${field.name}" name="${field.name}" rows="4" ${isRequired}></textarea>`;
            break;
        
        case 'select':
            const optionsHtml = field.options.map(opt => 
                `<option value="${opt}" ${opt === field.defaultValue ? 'selected' : ''}>${opt}</option>`
            ).join('');
            fieldHtml += `<select id="${field.name}" name="${field.name}" ${isRequired}>${optionsHtml}</select>`;
            break;

        case 'select_api':
            try {
                const items = await api.getGeneric(field.endpoint);
                const apiOptionsHtml = items.map(item => 
                    `<option value="${item[field.option_value]}">${item[field.option_label]}</option>`
                ).join('');
                fieldHtml += `<select id="${field.name}" name="${field.name}" ${isRequired}><option value="">Selecione...</option>${apiOptionsHtml}</select>`;
            } catch (error) {
                fieldHtml += `<select id="${field.name}" name="${field.name}" disabled><option>Erro ao carregar</option></select>`;
                showToast(`Erro ao carregar dados para ${field.label}: ${error.message}`, 'error');
            }
            break;

        case 'multiselect_api':
            try {
                // Busca os dados para popular o select
                const items = await api.getGeneric(field.endpoint);
                const multiOptionsHtml = items.map(item => 
                    `<option value="${item[field.option_value]}">${item[field.option_label]}</option>`
                ).join('');
                
                // Cria o <select multiple> nativo com as opções já preenchidas
                fieldHtml += `<select id="${field.name}" name="${field.name}" multiple>${multiOptionsHtml}</select>`;
            } catch (error) {
                fieldHtml += `<select id="${field.name}" name="${field.name}" multiple disabled></select>`;
                showToast(`Erro ao carregar opções para ${field.label}: ${error.message}`, 'error');
            }
            break;

        default: // 'text', 'date', 'url', 'number', etc.
            fieldHtml += `<input type="${field.type}" id="${field.name}" name="${field.name}" ${isRequired}>`;
            break;
    }
    
    formGroup.innerHTML = fieldHtml;
    return formGroup;
}

/**
 * Gera o formulário completo dinamicamente a partir de um esquema.
 * @param {HTMLElement} formElement - O elemento <form> onde o conteúdo será inserido.
 * @param {Array} schema - O array 'form' do esquema.
 */
export async function renderFormFromSchema(formElement, schema, auth) {
    const formGrid = document.createElement('div');
    formGrid.className = 'form-grid';

    // Repassa o 'auth' para cada chamada de createFormField
    const fieldPromises = schema.map(field => createFormField(field, auth));
    const formFields = await Promise.all(fieldPromises);
    
    formFields.forEach(fieldElement => formGrid.appendChild(fieldElement));

    const formActions = formElement.querySelector('.form-actions');
    formElement.insertBefore(formGrid, formActions);
}