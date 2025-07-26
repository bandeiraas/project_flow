import { api } from './apiService.js';
import { showToast } from './toast.js';

function renderUserList(usuarios) {
    const tbody = document.getElementById('user-list-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    usuarios.forEach(user => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${user.nome_completo}</td>
            <td>${user.email}</td>
            <td>${user.cargo}</td>
            <td>
                <select class="role-select" data-user-id="${user.id_usuario}">
                    <option value="Membro" ${user.role === 'Membro' ? 'selected' : ''}>Membro</option>
                    <option value="Gerente" ${user.role === 'Gerente' ? 'selected' : ''}>Gerente</option>
                    <option value="Admin" ${user.role === 'Admin' ? 'selected' : ''}>Admin</option>
                </select>
            </td>
        `;
        tbody.appendChild(tr);
    });

    // Adiciona os listeners de mudança aos dropdowns
    document.querySelectorAll('.role-select').forEach(select => {
        select.addEventListener('change', async (event) => {
            const userId = event.target.dataset.userId;
            const newRole = event.target.value;
            
            try {
                await api.updateUserRole(userId, newRole);
                showToast(`Papel do usuário atualizado para ${newRole}.`, 'success');
            } catch (error) {
                showToast(`Erro ao atualizar papel: ${error.message}`, 'error');
                // Reverte a mudança visual em caso de erro
                event.target.value = user.role; 
            }
        });
    });
}

export function initializePage(dependencies) {
    const { auth } = dependencies;
    const adminPanel = document.getElementById('admin-panel');
    const nonAdminMessage = document.getElementById('non-admin-message');

    if (auth.getUser() && auth.getUser().role === 'Admin') {
        adminPanel.style.display = 'block';
        nonAdminMessage.style.display = 'none';

        api.getGeneric('/usuarios')
            .then(renderUserList)
            .catch(error => showToast(`Erro ao buscar usuários: ${error.message}`, 'error'));
    } else {
        adminPanel.style.display = 'none';
        nonAdminMessage.style.display = 'block';
    }
}