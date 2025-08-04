import { api } from './apiService.js';
import { showToast } from './toast.js';
import { renderFormFromSchema } from './form-builder.js';

/**
 * Preenche os campos de um formulário já renderizado com os dados de um projeto.
 * @param {HTMLFormElement} form - O elemento do formulário.
 * @param {object} projeto - Os dados do projeto vindos da API.
 */
function preencherFormulario(form, projeto) {
    console.log("[editar_projeto.js] Preenchendo formulário com dados:", projeto);
    
    // Preenche os campos de texto, data, etc.
    for (const key in projeto) {
        if (form.elements[key]) {
            const field = form.elements[key];
            if (field.type === 'date' && projeto[key]) {
                field.value = projeto[key].split('T')[0];
            } else if (field.type !== 'select-multiple') { // Ignora os selects múltiplos por enquanto
                field.value = projeto[key];
            }
        }
    }
    // Preenche os selects de valor único
    if (form.elements.id_responsavel && projeto.responsavel) {
        form.elements.id_responsavel.value = projeto.responsavel.id_usuario;
    }
    if (form.elements.id_area_solicitante && projeto.area_solicitante) {
        form.elements.id_area_solicitante.value = projeto.area_solicitante.id_area;
    }

    // --- LÓGICA PARA PRÉ-SELECIONAR OS SELECTS MÚLTIPLOS ---
    const equipeIds = projeto.equipe.map(m => m.id_usuario.toString());
    Array.from(form.elements.equipe_ids.options).forEach(option => {
        option.selected = equipeIds.includes(option.value);
    });

    const objetivoIds = projeto.objetivos_estrategicos.map(o => o.id_objetivo.toString());
    Array.from(form.elements.objetivo_ids.options).forEach(option => {
        option.selected = objetivoIds.includes(option.value);
    });
}

/**
 * Lida com o evento de submit do formulário de EDIÇÃO.
 * @param {Event} event - O evento de submit.
 * @param {number} idDoProjeto - O ID do projeto que está sendo editado.
 * @param {object} dependencies - O objeto com as dependências globais (navigate).
 */
async function handleEditFormSubmit(event, idDoProjeto, dependencies) {
    event.preventDefault();
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const buttonText = submitButton.querySelector('.btn-text');
    const buttonLoader = submitButton.querySelector('.loader-small');

    if (!form.checkValidity()) {
        form.reportValidity();
        showToast("Por favor, preencha todos os campos obrigatórios.", "error");
        return;
    }

    const formData = new FormData(form);
    
    // Coleta os dados, usando getAll para os campos de seleção múltipla
    const data = {
        ...Object.fromEntries(formData.entries()),
        equipe_ids: formData.getAll('equipe_ids').map(id => parseInt(id)),
        objetivo_ids: formData.getAll('objetivo_ids').map(id => parseInt(id))
    };

    // Limpa chaves com valores vazios e trata campos numéricos
    for (const key in data) {
        if (!Array.isArray(data[key])) {
            if (data[key] === '') {
                data[key] = null;
            } else if (key === 'custo_estimado' && data[key] !== null) {
                // Converte custo_estimado para número, permitindo 0
                const valor = parseFloat(data[key]);
                data[key] = isNaN(valor) ? null : valor;
            }
        }
    }

    if (data.data_inicio_prevista) data.data_inicio_prevista = new Date(data.data_inicio_prevista + 'T00:00:00').toISOString();
    if (data.data_fim_prevista) data.data_fim_prevista = new Date(data.data_fim_prevista + 'T00:00:00').toISOString();

    console.log("[editar_projeto.js] Enviando dados FINAIS para a API:", data);

    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonLoader.style.display = 'block';

    try {
        await api.updateProjeto(idDoProjeto, data);
        showToast('Projeto atualizado com sucesso!', 'success');
        setTimeout(() => {
            window.location.href = `projeto.html?id=${idDoProjeto}`;
        }, 1500);
    } catch (error) {
        showToast(`Erro ao atualizar projeto: ${error.message}`, 'error');
        submitButton.disabled = false;
        buttonText.style.display = 'block';
        buttonLoader.style.display = 'none';
    }
}

/**
 * Função de inicialização da página, chamada pelo main.js.
 */
export async function initializePage(dependencies) {
    console.log("[editar_projeto.js] Inicializando a página de edição...");
    
    const form = document.getElementById('form-novo-projeto');
    const urlParams = new URLSearchParams(window.location.search);
    const idDoProjeto = urlParams.get('id');
    const { auth } = dependencies;

    if (!idDoProjeto || !form) {
        const container = document.querySelector('.container');
        if (container) {
            container.innerHTML = '<h1>Erro: ID do projeto não fornecido ou formulário não encontrado.</h1>';
        }
        return;
    }

    try {
        // Busca o schema e os dados do projeto em paralelo
        const [schema, projeto] = await Promise.all([
            api.getProjetoSchema(),
            api.getProjetoPorId(idDoProjeto)
        ]);

        // Renderiza o formulário (o form-builder já busca os dados dos selects)
        await renderFormFromSchema(form, schema.form, auth);
        
        // Preenche o formulário com os dados do projeto
        preencherFormulario(form, projeto);
        
        // Adiciona o listener de submit
        if (form.submitHandler) {
            form.removeEventListener('submit', form.submitHandler);
        }
        form.submitHandler = (e) => handleEditFormSubmit(e, idDoProjeto, dependencies);
        form.addEventListener('submit', form.submitHandler);

    } catch (error) {
        showToast(`Erro ao inicializar página de edição: ${error.message}`, 'error');
        console.error("Erro durante a inicialização da página de edição:", error);
    }
}