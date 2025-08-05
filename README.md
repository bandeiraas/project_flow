# ProjectFlow - Sistema de Gestão de Projetos e Portfólio


*(Sugestão: Substitua o link acima por um screenshot real do seu dashboard)*
Com essas alterações, seu projeto está com a configuração de log mais adequada para uso geral e com uma documentação completa e profissional, pronta para ser compartilhada ou consultada no futuro.


**ProjectFlow** é uma aplicação web full-stack para o gerenciamento do ciclo de vida de projetos e portfólio, construída com uma arquitetura moderna e profissional. A plataforma permite o acompanhamento detalhado de projetos, desde a criação até a conclusão, com um sistema de autenticação seguro, permissões baseadas em papéis (RBAC), e dashboards analíticos para QA e gestão de portfólio.

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
    *   **Gerentes e Admins:** Têm acesso total ao portfólio de projetos e relatórios.

*   **Gestão de Projetos Completa:**
    *   Criação, visualização, edição e exclusão de projetos.
    *   Formulários dinâmicos gerados a partir de um esquema fornecido pelo backend, facilitando a adição de novos campos.
    *   Associação de projetos a objetivos estratégicos, equipes e áreas.

*   **Módulo de Homologação Avançado:**
    *   Fluxo de trabalho de status customizável.
    *   Criação de múltiplos ciclos de teste por projeto.
    *   **Upload e Parsing de Relatórios:** Anexe um relatório `.zip` do Allure e o sistema extrai automaticamente as métricas e a lista de testes executados.
    *   Visualização detalhada dos testes de cada ciclo (aprovados, reprovados, etc.).
    *   Criação de tarefas de correção (bugs) diretamente a partir de um teste reprovado.

*   **Gestão de Tarefas e Cronograma:**
    *   Criação, edição e exclusão de tarefas dentro de um projeto.
    *   Visualização do cronograma do projeto em um **Gráfico de Gantt** interativo.

*   **Dashboards e Relatórios:**
    *   **Dashboard Unificado:** Alterne entre a "Visão Geral" do portfólio e o "Meu Painel" (minhas tarefas e projetos).
    *   **Dashboard de QA:** Análise da saúde da qualidade, com histórico de taxa de sucesso e distribuição de resultados por projeto.
    *   **Dashboard de Portfólio:** Visão estratégica com projetos agrupados por objetivos, custos e status.
    *   Filtros e busca em tempo real.
    *   Cronograma completo (timeline) que registra **quem** fez cada mudança de status e **quando**, com observações.

*   **UI/UX Polida:**
    *   Design limpo, moderno e totalmente responsivo.
    *   **Modo Escuro** completo e consistente.
    *   Transições de página suaves e animações sutis.
    *   Componentes interativos como modais, toasts e loaders.

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
*   **SQLite:** Banco de dados relacional, ideal para desenvolvimento e portabilidade.

### Frontend
*   **Vanilla JavaScript (ES6+):** Sem frameworks, com foco em código modular e moderno.
*   **Arquitetura Modular:**
    *   **`main.js` como orquestrador:** Ponto de entrada único que gerencia a inicialização.
    *   **Injeção de Dependência:** Componentes globais (Modal, Auth) são instanciados no `main.js` e "injetados" nas páginas que precisam deles.
    *   **Componentes Reutilizáveis:** O layout (header, modal) é carregado dinamicamente.
*   **CSS Moderno:** Organizado em módulos (base, layout, componentes) e com uso de variáveis para temas (claro/escuro).
*   **Chart.js:** Para a criação de gráficos interativos na página de relatórios.
*   **Frappe Gantt:** Para a renderização do gráfico de Gantt de tarefas.

---

## 🚀 Configuração e Execução

*Ambiente de desenvolvimento testado em Linux (Codespaces) e Android (Termux).*

### Pré-requisitos
*   Python 3.8+ e `pip`.
*   Node.js e `npm`.

### 1. Configuração do Ambiente
Execute estes comandos na raiz do projeto para configurar tanto o backend quanto o frontend.

```bash
# a. Crie e ative o ambiente virtual do Python
python -m venv .venv
source .venv/bin/activate  # No Linux/macOS
# .venv\Scripts\activate    # No Windows

# b. Instale as dependências do Python
pip install -r requirements.txt

# c. Configure as variáveis de ambiente para o backend
# Copie o arquivo de exemplo e ajuste a JWT_SECRET_KEY para um valor seguro.
cp backend/.env.example .env

# d. Instale o servidor de desenvolvimento para o frontend (globalmente)
# (Você só precisa fazer isso uma vez)
npm install -g live-server
```
**Para executar o servidor:**
```bash
# Ainda dentro da pasta 'backend'
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
annotated-types==0.7.0
anyio==4.9.0
blinker==1.9.0
CacheControl==0.14.3
cachetools==5.5.2
certifi==2025.7.14
cffi==1.17.1
charset-normalizer==3.4.2
click==8.2.1
cloudevents==1.11.0
cryptography==45.0.5
deprecation==2.1.0
dotenv==0.9.9
firebase-functions==0.4.3
firebase_admin==7.0.0
Flask==3.1.1
flask-cors==6.0.1
Flask-JWT-Extended==4.7.1
functions-framework==3.9.1
google-api-core==2.25.1
google-auth==2.40.3
google-cloud-core==2.4.3
google-cloud-firestore==2.21.0
google-cloud-storage==3.2.0
google-crc32c==1.7.1
google-events==0.5.0
google-resumable-media==2.7.2
googleapis-common-protos==1.70.0
greenlet==3.2.3
grpcio==1.74.0
grpcio-status==1.74.0
gunicorn==23.0.0
h11==0.16.0
h2==4.2.0
hpack==4.1.0
httpcore==1.0.9
httpx==0.28.1
hyperframe==6.1.0
idna==3.10
itsdangerous==2.2.0
Jinja2==3.1.6
livereload==2.7.1
MarkupSafe==3.0.2
msgpack==1.1.1
packaging==25.0
proto-plus==1.26.1
protobuf==6.31.1
pyasn1==0.6.1
pyasn1_modules==0.4.2
pycparser==2.22
pydantic==2.11.7
pydantic_core==2.33.2
PyJWT==2.10.1
python-dotenv==1.1.1
PyYAML==6.0.2
requests==2.32.4
rsa==4.9.1
sniffio==1.3.1
SQLAlchemy==2.0.41
starlette==0.47.2
tornado==6.5.1
typing-inspection==0.4.1
typing_extensions==4.14.1
urllib3==2.5.0
uvicorn==0.35.0
uvicorn-worker==0.3.0
watchdog==6.0.0
Werkzeug==3.1.3

```

### `backend/.env.example` (Exemplo)
```
# Copie este arquivo para .env e ajuste se necessário
DATABASE_URL="projectflow.db"
JWT_SECRET_KEY="sua-chave-secreta-super-forte-aqui"
```

---

## 🔮 Próximos Passos

### Funcionalidades
*   [ ] **Página de Administração:** UI para gerenciar usuários e papéis.
*   [ ] **Notificações por Email:** Enviar alertas sobre prazos e mudanças de status.

### Testes e Qualidade
*   [ ] **Testes Automatizados:** Adicionar testes unitários e de integração para garantir a estabilidade.

### Melhorias de Arquitetura e Refatoração (Backend)
*   [ ] **Centralizar Gerenciamento de Sessão:** Usar hooks do Flask para gerenciar sessões do DB automaticamente, removendo código repetitivo das rotas.
*   [ ] **Adotar Enums:** Substituir "magic strings" (ex: status, roles) por Enums para maior segurança e legibilidade do código.
*   [ ] **Decoradores de Permissão:** Refatorar a lógica de verificação de permissões para decoradores personalizados (ex: `@permission_required`).
*   [ ] **Configuração de CORS para Produção:** Tornar a política de CORS mais restritiva usando variáveis de ambiente.
*   [ ] **Otimizar Reloader:** Configurar o reloader do Flask para ignorar a pasta `uploads` e melhorar a experiência de desenvolvimento.
```