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
                <select class="role-select" data-user-id="${user.id_usuario}" data-original-role="${user.role}">
                    <option value="MEMBRO" ${user.role === 'MEMBRO' ? 'selected' : ''}>Membro</option>
                    <option value="GERENTE" ${user.role === 'GERENTE' ? 'selected' : ''}>Gerente</option>
                    <option value="ADMIN" ${user.role === 'ADMIN' ? 'selected' : ''}>Admin</option>
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
                // Atualiza o atributo originalRole após sucesso
                event.target.dataset.originalRole = newRole;
            } catch (error) {
                showToast(`Erro ao atualizar papel: ${error.message}`, 'error');
                // Reverte a mudança visual em caso de erro usando o atributo originalRole
                event.target.value = event.target.dataset.originalRole; 
            }
        });
    });
}

export function initializePage(dependencies) {
    const { auth } = dependencies;
    const adminPanel = document.getElementById('admin-panel');
    const nonAdminMessage = document.getElementById('non-admin-message');

    if (auth.getUser() && auth.getUser().role === 'ADMIN') {
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