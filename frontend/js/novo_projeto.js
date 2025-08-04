import { api } from './apiService.js';
import { showToast } from './toast.js';
import { navigateWithTransition } from './navigation.js';
import { renderFormFromSchema } from './form-builder.js';

// --- Variáveis de escopo do módulo para guardar as instâncias do Tom Select ---
let tomSelectEquipe = null;
let tomSelectObjetivos = null;

/**
 * Lida com o evento de submit do formulário de CRIAÇÃO.
 * @param {Event} event - O evento de submit.
 * @param {object} dependencies - O objeto com as dependências globais (navigate).
 */
// Em novo_projeto.js

async function handleCreateFormSubmit(event, dependencies) {
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
    
    // --- COLETA DE DADOS CORRIGIDA ---
    const data = {
        ...Object.fromEntries(formData.entries()),
        equipe_ids: formData.getAll('equipe_ids').map(id => parseInt(id)),
        objetivo_ids: formData.getAll('objetivo_ids').map(id => parseInt(id))
    };

    // Garante que o custo seja um número, permitindo 0
    if (data.custo_estimado !== undefined && data.custo_estimado !== '') {
        const valor = parseFloat(data.custo_estimado);
        data.custo_estimado = isNaN(valor) ? null : valor;
    } else {
        data.custo_estimado = null;
    }

    // Lógica de limpeza para outros campos opcionais
    for (const key in data) {
        if (!Array.isArray(data[key]) && data[key] === '') {
            delete data[key];
        }
    }

    // Formatação de datas
    if (data.data_inicio_prevista) data.data_inicio_prevista = new Date(data.data_inicio_prevista + 'T00:00:00').toISOString();
    if (data.data_fim_prevista) data.data_fim_prevista = new Date(data.data_fim_prevista + 'T00:00:00').toISOString();

    console.log("[novo_projeto.js] Enviando dados FINAIS para a API:", data);

    // Feedback visual no botão
    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonLoader.style.display = 'block';

    try {
        const novoProjeto = await api.createProjeto(data);
        showToast(`Projeto "${novoProjeto.nome_projeto}" criado com sucesso!`, 'success');
        setTimeout(() => {
            dependencies.navigate(`projeto.html?id=${novoProjeto.id_projeto}`);
        }, 1500);
    } catch (error) {
        showToast(`Erro ao criar projeto: ${error.message}`, 'error');
        submitButton.disabled = false;
        buttonText.style.display = 'block';
        buttonLoader.style.display = 'none';
    }
}

/**
 * Função de inicialização da página, chamada pelo main.js.
 * Orquestra o carregamento do schema e a renderização do formulário.
 * @param {object} dependencies - Objeto contendo as dependências globais.
 */
export async function initializePage(dependencies) {
    console.log("[novo_projeto.js] Inicializando a página de novo projeto...");
    
    const form = document.getElementById('form-novo-projeto');
    const { auth } = dependencies;
    
    if (!form) {
        console.error("Elemento #form-novo-projeto não encontrado no DOM.");
        return;
    }

    try {
        // 1. Busca o schema do formulário na API.
        const schema = await api.getProjetoSchema();

        // 2. Chama o construtor de formulários para renderizar todos os campos.
        //    O construtor agora é inteligente e já busca os dados para os selects.
        await renderFormFromSchema(form, schema.form, auth);
        
        console.log("[novo_projeto.js] Formulário renderizado com sucesso.");

        // 3. Adiciona o listener de submit ao formulário.
        form.addEventListener('submit', (event) => handleCreateFormSubmit(event, dependencies));

    } catch (error) {
        showToast(`Erro fatal ao carregar o formulário: ${error.message}`, 'error');
        console.error("Erro ao inicializar a página de novo projeto:", error);
    }
}