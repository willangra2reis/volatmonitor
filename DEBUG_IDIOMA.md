# 🔍 Debug do Sistema de Idioma - Guia de Teste

## 🎯 Problema Identificado

O arquivo `saved_login.dat` está salvando corretamente:
```json
{
  "email": "...",
  "language": "es",
  "remember": true
}
```

Mas o dashboard abre em Português (idioma padrão) em vez de Espanhol.

---

## ✅ Correções Aplicadas

### 1. **Melhorado carregamento do idioma no Dashboard**
- Agora aguarda o `i18n.js` carregar completamente
- Retry automático se `window.i18n` não estiver disponível
- Logs detalhados para debug

### 2. **Adicionados Logs de Debug**
- `[LOGIN]` - Mostra idioma carregado do arquivo
- `[LOGIN]` - Mostra idioma salvo na sessão
- `[DASHBOARD]` - Mostra idioma recebido da sessão
- `[IDIOMA DEBUG]` - Logs no console do navegador

---

## 🧪 Como Testar Agora

### Passo 1: Limpar Tudo
```bash
# 1. Feche a aplicação se estiver rodando

# 2. Abra o console Python
python

# 3. Execute:
from credentials_manager import clear_saved_credentials
clear_saved_credentials()
exit()
```

### Passo 2: Fazer Login com Espanhol
```bash
# 1. Inicie a aplicação
python ws7_launcher.py

# 2. Na tela de login:
   - Clique no botão de idioma (🌐)
   - Selecione "Español"
   - Digite seu email
   - Marque "Recordar inicio de sesión" ✅
   - Clique "Iniciar sesión"

# 3. Observe os logs no console:
[LOGIN] 💾 Credenciais salvas - Email: seu@email.com | Idioma: es
[CREDENTIALS] ✅ Credenciais salvas - Email: seu@email.com | Idioma: es
```

### Passo 3: Verificar Arquivo
```bash
# Verifique o conteúdo do arquivo
type user_credentials\saved_login.dat

# Deve mostrar:
{"email": "...", "language": "es", "remember": true}
```

### Passo 4: Fechar e Reabrir
```bash
# 1. Feche a aplicação (Ctrl+C no console)

# 2. Abra novamente
python ws7_launcher.py

# 3. Observe os logs no console:
[CREDENTIALS] 📧 Credencial carregada - Email: seu@email.com | Idioma: es
[LOGIN] 🔍 Tentando login automático - Email: seu@email.com | Idioma: es
[LOGIN] ✅ Login automático bem-sucedido: seu@email.com
[LOGIN] 🌐 Idioma salvo na sessão: es
[DASHBOARD] 🌐 Renderizando dashboard - Idioma da sessão: 'es'
```

### Passo 5: Verificar Console do Navegador
```
# Abra o DevTools (F12) e veja o Console:

[IDIOMA DEBUG] Idioma recebido do servidor: es
[IDIOMA DEBUG] window.i18n disponível? true
[IDIOMA] ✅ Aplicando idioma salvo do login automático: es
[IDIOMA] ✅ Idioma aplicado com sucesso: es
```

---

## 🔍 O Que Verificar

### No Console Python (Terminal):
```
✅ [CREDENTIALS] 📧 Credencial carregada - Email: ... | Idioma: es
✅ [LOGIN] 🔍 Tentando login automático - Email: ... | Idioma: es
✅ [LOGIN] 🌐 Idioma salvo na sessão: es
✅ [DASHBOARD] 🌐 Renderizando dashboard - Idioma da sessão: 'es'
```

### No Console do Navegador (F12):
```
✅ [IDIOMA DEBUG] Idioma recebido do servidor: es
✅ [IDIOMA DEBUG] window.i18n disponível? true
✅ [IDIOMA] ✅ Aplicando idioma salvo do login automático: es
✅ [IDIOMA] ✅ Idioma aplicado com sucesso: es
```

### Na Tela:
```
✅ Todos os textos devem estar em ESPANHOL
✅ Botões: "Cerrar Todas", "Cerrar Positivas", etc.
✅ Cards: "Saldo", "Equity", "G/P del Día", etc.
✅ Gráficos com labels em espanhol
```

---

## ❌ Se Ainda Não Funcionar

### Cenário 1: Console Python mostra idioma vazio
```
[DASHBOARD] 🌐 Renderizando dashboard - Idioma da sessão: ''
```

**Problema**: Sessão não está persistindo o idioma

**Solução**: Verificar se `session.permanent = True` está sendo executado

---

### Cenário 2: Console do Navegador mostra idioma vazio
```
[IDIOMA DEBUG] Idioma recebido do servidor: 
```

**Problema**: Template Jinja2 não está renderizando a variável

**Solução**: Verificar se `{{ session.get("saved_language", "") }}` está correto

---

### Cenário 3: Console mostra idioma correto mas tela em português
```
[IDIOMA] ✅ Idioma aplicado com sucesso: es
```

**Problema**: `applyTranslations()` não está funcionando

**Solução**: 
1. Verificar se `i18n.js` está carregando
2. Verificar se há erros no console do navegador
3. Verificar se `localStorage.getItem('volatforex_language')` está correto

---

## 🔧 Comandos de Debug Úteis

### No Console do Navegador (F12):
```javascript
// Verificar idioma atual
console.log('Idioma atual:', localStorage.getItem('volatforex_language'));

// Verificar se i18n está disponível
console.log('i18n disponível?', typeof window.i18n !== 'undefined');

// Verificar idioma do i18n
console.log('Idioma do i18n:', window.i18n ? window.i18n.currentLanguage : 'N/A');

// Forçar aplicação de idioma
if (window.i18n) {
    window.i18n.setLanguage('es');
    applyTranslations();
}
```

### No Console Python:
```python
# Verificar credenciais salvas
from credentials_manager import get_saved_credentials
print(get_saved_credentials())

# Verificar sessão (durante execução)
# Adicione este código temporariamente na rota do dashboard:
print(f"DEBUG SESSION: {dict(session)}")
```

---

## 📋 Checklist de Verificação

- [ ] Arquivo `saved_login.dat` existe e contém `"language": "es"`
- [ ] Log `[LOGIN] 🌐 Idioma salvo na sessão: es` aparece
- [ ] Log `[DASHBOARD] 🌐 Renderizando dashboard - Idioma da sessão: 'es'` aparece
- [ ] Console do navegador mostra `[IDIOMA DEBUG] Idioma recebido do servidor: es`
- [ ] Console do navegador mostra `[IDIOMA] ✅ Idioma aplicado com sucesso: es`
- [ ] Dashboard está em espanhol

---

## 🎯 Próximos Passos

1. **Execute o teste completo** seguindo os passos acima
2. **Copie TODOS os logs** do console Python
3. **Copie TODOS os logs** do console do navegador (F12)
4. **Tire um screenshot** da tela do dashboard
5. **Me envie** essas informações para análise

---

## 💡 Dica Extra

Se o problema persistir, pode ser cache do navegador. Tente:

1. **Limpar cache do navegador**: Ctrl + Shift + Delete
2. **Modo anônimo**: Ctrl + Shift + N
3. **Hard refresh**: Ctrl + F5

---

**Vamos descobrir exatamente onde está o problema!** 🔍
