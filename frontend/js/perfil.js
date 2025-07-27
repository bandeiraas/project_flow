import { api } from './apiService.js';
import { showToast } from './toast.js';

function preencherDados(user) {
    if (!user) return;
    // Preenche a seção de visualização
    document.getElementById('profile-nome').textContent = user.nome_completo || '';
    document.getElementById('profile-email').textContent = user.email || '';
    document.getElementById('profile-cargo').textContent = user.cargo || '';
    document.getElementById('profile-telefone').textContent = user.telefone || '';
    document.getElementById('profile-role').textContent = user.role || '';

    // Preenche o formulário de edição
    document.getElementById('nome_completo').value = user.nome_completo || '';
    document.getElementById('cargo').value = user.cargo || '';
    document.getElementById('telefone').value = user.telefone || '';
}

async function handleProfileSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const buttonText = submitButton.querySelector('.btn-text');
    const buttonLoader = submitButton.querySelector('.loader-small');

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonLoader.style.display = 'block';

    try {
        const usuarioAtualizado = await api.updateProfile(data);
        showToast('Perfil atualizado com sucesso!', 'success');
        // Atualiza os dados na tela com a resposta da API
        preencherDados(usuarioAtualizado);
    } catch (error) {
        showToast(`Erro ao atualizar perfil: ${error.message}`, 'error');
    } finally {
        submitButton.disabled = false;
        buttonText.style.display = 'block';
        buttonLoader.style.display = 'none';
    }
}

export function initializePage(dependencies) {
    const { auth } = dependencies;
    const user = auth.getUser(); // Pega os dados do usuário já carregados pelo main.js

    if (user) {
        preencherDados(user);
    } else {
        showToast('Não foi possível carregar os dados do usuário.', 'error');
    }

    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileSubmit);
    }
}