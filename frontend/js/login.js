// Importa apenas o que é necessário para esta página
import { api } from './apiService.js';
import { showToast } from './toast.js';

const loginForm = document.getElementById('login-form');
const errorMessageDiv = document.getElementById('error-message');
const submitButton = loginForm.querySelector('button[type="submit"]');
const buttonText = submitButton.querySelector('.btn-text');
const buttonLoader = submitButton.querySelector('.loader-small');

loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    errorMessageDiv.style.display = 'none'; // Esconde mensagens de erro antigas

    const formData = new FormData(loginForm);
    const data = Object.fromEntries(formData.entries());

    // UX: Feedback de carregamento no botão
    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonLoader.style.display = 'block';

    try {
        // Chama a nova função da API para fazer login
        const response = await api.login(data.email, data.senha);
        
        // Se o login for bem-sucedido, a API retorna um objeto com 'access_token'
        if (response.access_token) {
          console.log("Token recebido da API:", response.access_token);
            // Salva o token no localStorage
            localStorage.setItem('accessToken', response.access_token);
            
            showToast('Login bem-sucedido!', 'success');
            
            // Redireciona para o dashboard após um pequeno delay
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);
        } else {
            throw new Error('Resposta da API inválida.');
        }

    } catch (error) {
        // Mostra a mensagem de erro da API (ex: "Credenciais inválidas")
        errorMessageDiv.textContent = error.message;
        errorMessageDiv.style.display = 'block';
        
        // Restaura o botão
        submitButton.disabled = false;
        buttonText.style.display = 'block';
        buttonLoader.style.display = 'none';
    }
});