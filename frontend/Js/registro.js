import { api } from './apiService.js';
import { showToast } from './toast.js';

const registerForm = document.getElementById('register-form');
const errorMessageDiv = document.getElementById('error-message');
const submitButton = registerForm.querySelector('button[type="submit"]');
const buttonText = submitButton.querySelector('.btn-text');
const buttonLoader = submitButton.querySelector('.loader-small');

registerForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    errorMessageDiv.style.display = 'none';

    const formData = new FormData(registerForm);
    const data = Object.fromEntries(formData.entries());

    if (data.senha.length < 6) {
        errorMessageDiv.textContent = 'A senha deve ter no mínimo 6 caracteres.';
        errorMessageDiv.style.display = 'block';
        return;
    }

    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonLoader.style.display = 'block';

    try {
        await api.register(data.nome_completo, data.email, data.senha);
        
        showToast('Registro realizado com sucesso! Você já pode fazer login.', 'success');
        
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);

    } catch (error) {
        errorMessageDiv.textContent = error.message;
        errorMessageDiv.style.display = 'block';
        
        submitButton.disabled = false;
        buttonText.style.display = 'block';
        buttonLoader.style.display = 'none';
    }
});