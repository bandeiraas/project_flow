# ProjectFlow - Sistema de Gestão de Projetos

![ProjectFlow Screenshot](https://via.placeholder.com/800x400.png?text=ProjectFlow+Dashboard)
*(Sugestão: Substitua o link acima por um screenshot real do seu dashboard)*

**ProjectFlow** é uma aplicação web full-stack para o gerenciamento do ciclo de vida de projetos, construída com uma arquitetura moderna e profissional. A plataforma permite o acompanhamento detalhado de projetos, desde a criação até a conclusão, com um sistema de autenticação seguro e permissões baseadas em papéis (roles).

A interface é limpa, totalmente responsiva, com modo escuro, e se adapta dinamicamente às permissões do usuário logado, oferecendo uma experiência de usuário (UX) coesa e intuitiva.

---

## ✨ Funcionalidades Principais

*   **Sistema de Autenticação Seguro:**
    *   Login e Registro de usuários.
    *   Uso de **JSON Web Tokens (JWT)** para proteger a API.
    *   Armazenamento seguro de senhas com hashing.

*   **Controle de Acesso Baseado em Papéis (RBAC):**
    *   Três níveis de permissão: **Membro**, **Gerente** e **Admin**.
    *   A interface se adapta dinamicamente, escondendo ações não permitidas para o usuário logado.
    *   **Membros:** Podem criar e gerenciar apenas seus próprios projetos.
    *   **Gerentes e Admins:** Têm acesso total ao portfólio de projetos.

*   **Gestão de Projetos Completa (CRUD):**
    *   Criação, visualização, edição e exclusão de projetos.
    *   Formulários dinâmicos gerados a partir de um esquema fornecido pelo backend, facilitando a adição de novos campos.

*   **Ciclo de Vida e Auditoria:**
    *   Fluxo de trabalho de status customizável.
    *   Módulo de **Homologação** detalhado, com múltiplos ciclos de teste.
    *   Cronograma completo (timeline) que registra **quem** fez cada mudança de status e **quando**, com observações.

*   **Dashboard e Relatórios:**
    *   Dashboard interativo com busca e filtros em tempo real.
    *   Indicadores visuais de "saúde" do projeto (atrasado, em risco, etc.).
    *   Página de relatórios com gráficos (pizza e barras) para análise de portfólio (Projetos por Status, Prioridade, etc.).

*   **UI/UX Polida:**
    *   Design limpo, moderno e totalmente responsivo.
    *   **Modo Escuro** completo e consistente.
    *   Transições de página suaves e animações sutis.
    *   Componentes interativos como modais de confirmação e notificações (toasts).

---

## 🛠️ Arquitetura e Tecnologias

O projeto foi desenvolvido com uma forte separação de responsabilidades entre o backend e o frontend.

### Backend
*   **Python 3** com **Flask** para a API RESTful.
*   **SQLAlchemy (ORM 2.0):** Mapeamento Declarativo para interação com o banco de dados.
*   **Pydantic:** Validação de dados robusta e segura na camada da API.
*   **Flask-JWT-Extended:** Para gerenciamento de autenticação com JSON Web Tokens.
*   **Arquitetura de 3 Camadas:**
    1.  **API (`routes.py`):** Controladores que lidam com requisições HTTP.
    2.  **Serviço (`services/`):** Encapsula a lógica de negócio pura.
    3.  **Dados (`data_sources/` e `models/`):** Define os modelos e a interação com o banco de dados.
*   **Configuração Centralizada:** Uso de `.env` e um arquivo `config.py` para gerenciar as configurações do ambiente.
*   **SQLite:** Banco de dados relacional.

### Frontend
*   **Vanilla JavaScript (ES6+):** Sem frameworks, com foco em código modular e moderno.
*   **Arquitetura Modular:**
    *   **`main.js` como orquestrador:** Ponto de entrada único que gerencia a inicialização.
    *   **Injeção de Dependência:** Componentes globais (Modal, Auth) são instanciados no `main.js` e "injetados" nas páginas que precisam deles.
    *   **Componentes Reutilizáveis:** O layout (header, modal) é carregado dinamicamente.
*   **CSS Moderno:** Organizado em módulos (base, layout, componentes) e com uso de variáveis para temas (claro/escuro).
*   **Chart.js:** Para a criação de gráficos interativos na página de relatórios.

---

## 🚀 Configuração e Execução

*Ambiente de desenvolvimento testado no Android com Termux.*

### Pré-requisitos
*   Python 3.8+ e `pip`.
*   (No Termux) Ferramentas de build: `pkg install rust clang make`.
*   `live-server` (via `npm install -g live-server`).

### 1. Backend
```bash
cd backend
# Crie um ambiente virtual (recomendado)
# python -m venv venv
# source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Crie o arquivo .env a partir do .env.example
cp .env.example .env

# Execute o servidor
python app.py
```

### 2. Frontend
```bash
cd frontend
# Execute o servidor de desenvolvimento
live-server
```
Acesse **`http://127.0.0.1:8080/login.html`** para começar.

---

## 📝 Arquivos de Configuração

### `backend/requirements.txt`
```
Flask
Flask-Cors
SQLAlchemy
python-dotenv
pydantic<2
Flask-JWT-Extended
Werkzeug
```

### `backend/.env.example` (Exemplo)
```
# Copie este arquivo para .env e ajuste se necessário
DATABASE_URL="projectflow.db"
JWT_SECRET_KEY="sua-chave-secreta-super-forte-aqui"
```

---

## 🔮 Próximos Passos

*   [X] **CRUD Completo**
*   [X] **Autenticação com JWT**
*   [X] **Sistema de Permissões (RBAC)**
*   [ ] **Auditoria Completa:** Usar o ID do usuário do token em todas as operações.
*   [ ] **Gráfico de Gantt:** Implementar um cronograma de tarefas.
*   [ ] **Página de Administração:** UI para gerenciar usuários e papéis.
*   [ ] **Testes Automatizados:** Adicionar testes unitários e de integração.
```