# 🌐 Sistema de Salvamento de Idioma - Documentação

## 📋 Visão Geral

O sistema agora salva **email E idioma** quando o usuário marca "Lembrar login". Na próxima vez que abrir a aplicação, tanto o login quanto o idioma são restaurados automaticamente.

---

## ✅ O Que Foi Implementado

### 1. **Salvamento de Idioma com Email**
- Idioma é capturado automaticamente do localStorage ao fazer login
- Salvo junto com o email em `user_credentials/saved_login.dat`
- Formato do arquivo:
  ```json
  {
    "email": "base64_encoded_email",
    "language": "pt",
    "remember": true
  }
  ```

### 2. **Aplicação Automática do Idioma**
- **Tela de Login**: Idioma salvo é aplicado automaticamente
- **Dashboard**: Idioma é restaurado após login automático
- **LocalStorage**: Sincronizado com idioma salvo

### 3. **Fluxo Completo**

#### Primeiro Login:
```
1. Usuário seleciona idioma (ex: Inglês)
2. Digita email
3. Marca "Lembrar login" ✅
4. Clica "Entrar"
   ↓
5. Sistema captura idioma do localStorage
6. Salva: email + idioma (en)
   ↓
7. Arquivo criado:
   {
     "email": "encoded",
     "language": "en",
     "remember": true
   }
```

#### Próximas Aberturas:
```
1. Usuário abre aplicação
   ↓
2. Sistema carrega credenciais salvas
   ↓
3. Detecta: email + idioma (en)
   ↓
4. Faz login automático
   ↓
5. Aplica idioma Inglês automaticamente
   ↓
6. Dashboard abre em Inglês ✅
```

---

## 🔄 Sincronização de Idioma

### Tela de Login:
1. **Ao carregar**: Aplica idioma salvo do arquivo
2. **Ao mudar idioma**: Atualiza campo hidden no formulário
3. **Ao fazer login**: Envia idioma atual para o servidor

### Dashboard:
1. **Login automático**: Recebe idioma da sessão
2. **Aplica automaticamente**: Via JavaScript
3. **Sincroniza localStorage**: Mantém consistência

---

## 📁 Arquivos Modificados

### 1. **`credentials_manager.py`**
```python
# ANTES
def save_credentials(self, email):
    data = {
        'email': self._encode(email),
        'remember': True
    }

# DEPOIS
def save_credentials(self, email, language='pt'):
    data = {
        'email': self._encode(email),
        'language': language,  # ✅ NOVO
        'remember': True
    }
```

### 2. **`ws7.py` - Rota de Login (POST)**
```python
# Captura idioma do formulário
language = request.form.get('language', 'pt')

# Salva email + idioma
if remember_me:
    save_user_credentials(email, language)
    print(f"[LOGIN] 💾 Credenciais salvas - Email: {email} | Idioma: {language}")
```

### 3. **`ws7.py` - Rota de Login (GET - Login Automático)**
```python
# Carrega credenciais (email + idioma)
saved_creds = get_saved_credentials()
if saved_creds:
    saved_email = saved_creds.get('email')
    saved_language = saved_creds.get('language', 'pt')
    
    # Salva idioma na sessão
    session['saved_language'] = saved_language
```

### 4. **`templates/login.html`**
```html
<!-- Campo hidden para enviar idioma -->
<input type="hidden" id="language" name="language" value="pt">

<script>
// Aplica idioma salvo ao carregar
const savedLanguage = '{{ saved_language }}' || localStorage.getItem('volatforex_language') || 'pt';
if (savedLanguage && savedLanguage !== 'None') {
    window.i18n.setLanguage(savedLanguage);
    document.getElementById('language').value = savedLanguage;
}

// Atualiza campo hidden ao mudar idioma
document.addEventListener('languageChanged', function() {
    const currentLanguage = localStorage.getItem('volatforex_language') || 'pt';
    document.getElementById('language').value = currentLanguage;
});
</script>
```

### 5. **`ws7.py` - Dashboard HTML Template**
```javascript
// Aplica idioma salvo do login automático
const savedLanguageFromServer = '{{ session.get("saved_language", "") }}';
if (savedLanguageFromServer && savedLanguageFromServer !== '') {
    console.log('[IDIOMA] Aplicando idioma salvo:', savedLanguageFromServer);
    window.i18n.setLanguage(savedLanguageFromServer);
}
```

---

## 📊 Logs Esperados

### Login com "Lembrar" Marcado:
```
[LOGIN] ✅ user@email.com autenticado
[LOGIN] 💾 Credenciais salvas - Email: user@email.com | Idioma: en
[CREDENTIALS] ✅ Credenciais salvas - Email: user@email.com | Idioma: en
```

### Login Automático (Próxima Abertura):
```
[CREDENTIALS] 📧 Credencial carregada - Email: user@email.com | Idioma: en
[LOGIN] 🔍 Tentando login automático - Email: user@email.com | Idioma: en
[LOGIN] ✅ Login automático bem-sucedido: user@email.com
[IDIOMA] Aplicando idioma salvo do login automático: en
```

### Logout:
```
[LOGOUT] 👋 user@email.com desconectado
[LOGOUT] 🗑️ Credenciais de login automático removidas (email + idioma)
[CREDENTIALS] 🗑️ Credenciais removidas
```

---

## 🧪 Como Testar

### Teste Completo:

1. **Abra a aplicação:**
   ```bash
   python ws7_launcher.py
   ```

2. **Selecione um idioma diferente:**
   - Clique no botão de idioma (🌐)
   - Selecione "English"
   - Tela de login muda para inglês

3. **Faça login:**
   - Digite seu email
   - **Marque "Remember login"** ✅
   - Clique "Login"

4. **Verifique logs:**
   ```
   [LOGIN] 💾 Credenciais salvas - Email: seu@email.com | Idioma: en
   [CREDENTIALS] ✅ Credenciais salvas - Email: seu@email.com | Idioma: en
   ```

5. **Verifique arquivo:**
   ```bash
   type user_credentials\saved_login.dat
   ```
   Deve mostrar:
   ```json
   {
     "email": "...",
     "language": "en",
     "remember": true
   }
   ```

6. **Feche a aplicação**

7. **Abra novamente:**
   ```bash
   python ws7_launcher.py
   ```

8. **Resultado esperado:**
   - ✅ Login automático
   - ✅ Dashboard abre em **Inglês**
   - ✅ Todos os textos em inglês
   - ✅ Sem precisar selecionar idioma novamente

9. **Verifique console do navegador:**
   ```
   [IDIOMA] Aplicando idioma salvo do login automático: en
   ```

---

## 🎯 Cenários de Uso

### Cenário 1: Usuário Português
```
1. Primeira vez: Mantém Português (padrão)
2. Marca "Lembrar login"
3. Próximas vezes: Abre em Português ✅
```

### Cenário 2: Usuário Inglês
```
1. Primeira vez: Muda para English
2. Marca "Remember login"
3. Próximas vezes: Abre em English ✅
```

### Cenário 3: Usuário Muda de Idioma
```
1. Estava usando Português
2. Muda para Español
3. Faz login novamente (com "Lembrar")
4. Sistema atualiza: Salva Español
5. Próximas vezes: Abre em Español ✅
```

### Cenário 4: Logout
```
1. Usuário faz logout
2. Sistema remove credenciais (email + idioma)
3. Próxima vez: Precisa fazer login novamente
4. Idioma volta ao padrão (Português)
```

---

## 🔧 Funções Disponíveis

### No `credentials_manager.py`:

```python
# Salvar email + idioma
save_user_credentials(email, language='pt')

# Carregar credenciais completas
creds = get_saved_credentials()
# Retorna: {'email': str, 'language': str, 'remember': bool}

# Pegar apenas email
email = get_saved_email()

# Pegar apenas idioma
language = get_saved_language()

# Limpar credenciais
clear_saved_credentials()

# Verificar se existe
has_saved_login()
```

---

## 📦 Estrutura do Arquivo

### `user_credentials/saved_login.dat`:
```json
{
  "email": "dXNlckBlbWFpbC5jb20=",  // Base64 encoded
  "language": "en",                  // Idioma selecionado
  "remember": true                   // Flag de lembrar
}
```

### Idiomas Suportados:
- `pt` - Português (padrão)
- `en` - English
- `es` - Español
- `fr` - Français
- `de` - Deutsch

---

## ✅ Checklist de Funcionalidades

- [x] Captura idioma atual ao fazer login
- [x] Salva idioma junto com email
- [x] Aplica idioma salvo na tela de login
- [x] Aplica idioma salvo no dashboard
- [x] Sincroniza com localStorage
- [x] Atualiza idioma se usuário mudar
- [x] Remove idioma ao fazer logout
- [x] Logs detalhados de todas as operações
- [x] Compatível com todos os 5 idiomas
- [x] Funciona com login automático

---

## 🎉 Resultado Final

**Experiência do Usuário:**

1. **Primeira vez:**
   - Seleciona idioma preferido
   - Faz login
   - Marca "Lembrar login"

2. **Todas as próximas vezes:**
   - Abre aplicação
   - **Login automático** ✅
   - **Idioma aplicado automaticamente** ✅
   - Dashboard abre no idioma preferido

3. **Sem necessidade de:**
   - ❌ Digitar email novamente
   - ❌ Selecionar idioma novamente
   - ❌ Configurar nada

**Tudo funciona automaticamente!** 🚀

---

## 🔄 Compatibilidade

### Com LocalStorage:
- ✅ Sincroniza com `volatforex_language`
- ✅ Mantém consistência entre sessões
- ✅ Fallback para localStorage se arquivo não existir

### Com Executável Compilado:
- ✅ Arquivo salvo ao lado do .exe
- ✅ Funciona perfeitamente após compilação
- ✅ Persistência garantida

### Com WebView2:
- ✅ LocalStorage funcional
- ✅ Sincronização automática
- ✅ Sem conflitos

---

**Sistema de salvamento de idioma implementado com sucesso!** 🌐✨
