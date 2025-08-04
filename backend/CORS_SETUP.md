# 🌐 Configuração de CORS para GitHub Codespaces

Este guia explica como resolver problemas de CORS entre frontend e backend no GitHub Codespaces.

## 🔍 Problema Identificado

O erro `"Não foi possível se comunicar com o servidor"` ocorre porque:

1. **URLs dinâmicas**: GitHub Codespaces gera URLs únicas para cada sessão
2. **CORS restritivo**: Backend não permite origens do GitHub Codespaces
3. **Configuração desatualizada**: URLs hardcoded no frontend

## ✅ Soluções Implementadas

### 1. **CORS Flexível Automático**
- ✅ Detecta automaticamente GitHub Codespaces
- ✅ Permite padrões de URL dinâmicos (`*.app.github.dev`)
- ✅ Middleware personalizado para máxima compatibilidade

### 2. **Configuração Automática de URLs**
- ✅ Frontend detecta automaticamente a URL do backend
- ✅ Substitui URLs hardcoded por detecção dinâmica
- ✅ Funciona tanto localmente quanto no Codespaces

### 3. **Logging Melhorado**
- ✅ Logs detalhados de requisições CORS
- ✅ Debug de origens permitidas/negadas
- ✅ Informações de configuração no startup

## 🚀 Como Usar

### **Opção 1: Script Automático (Recomendado)**
```bash
cd backend
python start_server.py
```

### **Opção 2: Comando Tradicional**
```bash
cd backend
python app.py
```

### **Opção 3: Com Gunicorn (Produção)**
```bash
cd backend
gunicorn --bind 0.0.0.0:5000 --workers 4 app:create_app()
```

## 🔧 Configurações Aplicadas

### **Backend (.env)**
```env
# CORS Origins - Inclui GitHub Codespaces
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,https://*.app.github.dev

# Logs em DEBUG para desenvolvimento
LOG_LEVEL=DEBUG

# Rate limiting desabilitado em desenvolvimento
RATELIMIT_ENABLED=false
```

### **Frontend (config.js)**
```javascript
// Detecção automática de ambiente
const isCodespaces = window.location.hostname.includes('.app.github.dev');

if (isCodespaces) {
    // URL dinâmica para Codespaces
    API_BASE_URL = currentUrl.replace(/:\d+/, '') + '-5000.app.github.dev/api';
} else {
    // URL local
    API_BASE_URL = 'http://localhost:5000/api';
}
```

## 🛠️ Troubleshooting

### **1. Erro: "Access to fetch blocked by CORS policy"**

**Solução:**
```bash
# Verifique se o backend está rodando
ps aux | grep python

# Reinicie o backend
cd backend
python start_server.py
```

### **2. Erro: "Connection refused"**

**Solução:**
```bash
# Verifique a porta do backend
netstat -tlnp | grep :5000

# Certifique-se que está usando 0.0.0.0, não 127.0.0.1
```

### **3. URLs não correspondem**

**Solução:**
```bash
# Limpe o cache do navegador
# Recarregue a página com Ctrl+Shift+R
# Verifique o console do navegador para logs
```

## 📊 Verificação de Status

### **1. Verifique se o backend está acessível:**
```bash
# No terminal do Codespaces
curl -I http://localhost:5000/api/usuarios
```

### **2. Teste CORS manualmente:**
```bash
# Teste preflight OPTIONS
curl -X OPTIONS \
  -H "Origin: https://sua-url-frontend.app.github.dev" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -v http://localhost:5000/api/usuarios
```

### **3. Verifique logs do backend:**
```bash
# Os logs devem mostrar:
# 🔧 CORS flexível configurado com suporte ao GitHub Codespaces
# 🔗 CORS Origins configuradas: [lista de URLs]
```

## 🔍 Debug Avançado

### **Ativar logs detalhados:**
```bash
# No .env
LOG_LEVEL=DEBUG

# Reinicie o backend
python start_server.py
```

### **Verificar headers CORS:**
```javascript
// No console do navegador
fetch('/api/usuarios', {
  method: 'OPTIONS',
  headers: {
    'Origin': window.location.origin,
    'Access-Control-Request-Method': 'GET'
  }
}).then(response => {
  console.log('CORS Headers:', response.headers);
});
```

## 📝 Configurações por Ambiente

### **Desenvolvimento Local**
```env
FLASK_ENV=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
LOG_LEVEL=DEBUG
```

### **GitHub Codespaces**
```env
FLASK_ENV=development
CORS_ORIGINS=https://*.app.github.dev,http://localhost:3000
LOG_LEVEL=DEBUG
```

### **Produção**
```env
FLASK_ENV=production
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
RATELIMIT_ENABLED=true
```

## ✅ Checklist de Verificação

- [ ] Backend rodando na porta 5000
- [ ] Frontend acessível via browser
- [ ] URLs do .env incluem GitHub Codespaces
- [ ] Logs mostram CORS configurado
- [ ] Console do navegador sem erros de CORS
- [ ] Requisições de login funcionando

## 📞 Suporte

Se ainda houver problemas:

1. **Verifique os logs** do backend e frontend
2. **Teste as URLs** manualmente com curl
3. **Limpe o cache** do navegador
4. **Reinicie** ambos os serviços

---

**Configurações implementadas em:** `2025-08-02`  
**Compatível com:** GitHub Codespaces, desenvolvimento local, produção