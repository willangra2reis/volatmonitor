# 🔐 Sistema "Lembrar Login" - Documentação

## 📋 Visão Geral

O sistema de "Lembrar Login" permite que o usuário faça login automático sem precisar digitar o email toda vez que abrir a aplicação.

---

## ✅ Como Funciona

### 1. **Primeiro Login**

Quando o usuário faz login pela primeira vez:

1. Digita o email
2. **Marca o checkbox "Lembrar login"** ✅
3. Clica em "Entrar"
4. Sistema valida o email na API Google Apps Script
5. Se aprovado (`PURCHASE_APPROVED`):
   - Email é salvo em arquivo local criptografado
   - Usuário é redirecionado para o dashboard

### 2. **Próximas Aberturas**

Quando o usuário abre a aplicação novamente:

1. Sistema detecta que há email salvo
2. **Faz login automático** (sem mostrar tela de login)
3. Valida o email na API
4. Se ainda aprovado:
   - Redireciona direto para o dashboard
5. Se não aprovado ou email inválido:
   - Remove credenciais salvas
   - Mostra tela de "Acesso Negado" ou "Login"

---

## 📁 Onde São Salvos os Dados?

### Arquivo de Credenciais:
```
user_credentials/
└── saved_login.dat
```

### Conteúdo do Arquivo:
```json
{
  "email": "base64_encoded_email",
  "remember": true
}
```

**Segurança:**
- Email é codificado em Base64 (ofuscação)
- Arquivo é salvo localmente (não vai para nuvem)
- Apenas o email é salvo (sem senha)

---

## 🔄 Fluxo Completo

### Cenário 1: Login com "Lembrar" Marcado

```
1. Usuário digita email
2. Marca "Lembrar login" ✅
3. Clica "Entrar"
   ↓
4. Sistema valida na API
   ↓
5. Se APROVADO:
   - Salva email em arquivo
   - Cria sessão
   - Redireciona para dashboard
   ↓
6. Próxima abertura:
   - Detecta email salvo
   - Login automático
   - Vai direto para dashboard
```

### Cenário 2: Login sem "Lembrar" Marcado

```
1. Usuário digita email
2. NÃO marca "Lembrar login" ❌
3. Clica "Entrar"
   ↓
4. Sistema valida na API
   ↓
5. Se APROVADO:
   - Remove email salvo (se houver)
   - Cria sessão
   - Redireciona para dashboard
   ↓
6. Próxima abertura:
   - Não há email salvo
   - Mostra tela de login
```

### Cenário 3: Usuário Perde Acesso

```
1. Usuário tinha login salvo
2. Abre aplicação
   ↓
3. Sistema tenta login automático
   ↓
4. API retorna: NÃO APROVADO
   ↓
5. Sistema:
   - Remove credenciais salvas
   - Mostra "Acesso Negado"
   ↓
6. Usuário precisa renovar acesso
```

### Cenário 4: Logout Manual

```
1. Usuário clica "Logout"
   ↓
2. Sistema:
   - Limpa sessão
   - Remove credenciais salvas
   - Redireciona para login
   ↓
3. Próxima abertura:
   - Não há login salvo
   - Mostra tela de login
```

---

## 🔒 Segurança

### Validações Implementadas:

1. **Email sempre validado na API**
   - Mesmo com login salvo, valida status atual
   - Não confia cegamente em dados locais

2. **Remoção automática de credenciais inválidas**
   - Se API retornar erro, remove credenciais
   - Se status não for `PURCHASE_APPROVED`, remove

3. **Ofuscação do email**
   - Email é codificado em Base64
   - Dificulta leitura direta do arquivo

4. **Arquivo local**
   - Não envia credenciais para nuvem
   - Dados ficam apenas na máquina do usuário

---

## 📊 Logs do Sistema

### Login com "Lembrar" Marcado:
```
[LOGIN] ✅ user@email.com autenticado - Token: abc123...
[LOGIN] 💾 Email salvo para login automático: user@email.com
[CREDENTIALS] ✅ Credenciais salvas para: user@email.com
```

### Login Automático (Próxima Abertura):
```
[CREDENTIALS] 📧 Credencial carregada: user@email.com
[LOGIN] 🔍 Tentando login automático com: user@email.com
[GOOGLE AUTH] User user@email.com -> PURCHASE_APPROVED
[LOGIN] ✅ Login automático bem-sucedido: user@email.com
```

### Credenciais Inválidas:
```
[CREDENTIALS] 📧 Credencial carregada: user@email.com
[LOGIN] 🔍 Tentando login automático com: user@email.com
[GOOGLE AUTH] User user@email.com -> SUBSCRIPTION_CANCELLED
[LOGIN] ⚠️ Credenciais salvas inválidas - removendo
[CREDENTIALS] 🗑️ Credenciais removidas
```

### Logout:
```
[LOGOUT] 👋 user@email.com desconectado
[LOGOUT] 🗑️ Credenciais de login automático removidas
[CREDENTIALS] 🗑️ Credenciais removidas
```

---

## 🎯 Vantagens

### Para o Usuário:
- ✅ Não precisa digitar email toda vez
- ✅ Experiência mais fluida
- ✅ Login instantâneo ao abrir aplicação
- ✅ Pode desativar quando quiser (não marcar checkbox)

### Para Segurança:
- ✅ Sempre valida status atual na API
- ✅ Remove credenciais se usuário perder acesso
- ✅ Logout limpa tudo
- ✅ Dados salvos localmente (não na nuvem)

---

## 🧪 Como Testar

### Teste 1: Login com "Lembrar"

1. **Abra a aplicação:**
   ```bash
   python ws7_launcher.py
   ```

2. **Faça login:**
   - Digite seu email
   - **Marque "Lembrar login"** ✅
   - Clique "Entrar"

3. **Verifique logs:**
   ```
   [LOGIN] 💾 Email salvo para login automático
   [CREDENTIALS] ✅ Credenciais salvas
   ```

4. **Verifique arquivo criado:**
   ```bash
   dir user_credentials
   # Deve mostrar: saved_login.dat
   ```

5. **Feche a aplicação**

6. **Abra novamente:**
   ```bash
   python ws7_launcher.py
   ```

7. **Resultado esperado:**
   - ✅ Não mostra tela de login
   - ✅ Vai direto para dashboard
   - ✅ Logs mostram "Login automático bem-sucedido"

---

### Teste 2: Login sem "Lembrar"

1. **Faça logout** (se estiver logado)

2. **Faça login:**
   - Digite seu email
   - **NÃO marque "Lembrar login"** ❌
   - Clique "Entrar"

3. **Feche a aplicação**

4. **Abra novamente:**
   ```bash
   python ws7_launcher.py
   ```

5. **Resultado esperado:**
   - ✅ Mostra tela de login
   - ✅ Precisa digitar email novamente

---

### Teste 3: Logout Remove Credenciais

1. **Faça login com "Lembrar" marcado**

2. **Verifique que arquivo existe:**
   ```bash
   dir user_credentials
   ```

3. **Clique em "Logout"**

4. **Verifique logs:**
   ```
   [LOGOUT] 🗑️ Credenciais de login automático removidas
   ```

5. **Verifique que arquivo foi removido:**
   ```bash
   dir user_credentials
   # Pasta vazia ou arquivo não existe
   ```

6. **Abra novamente:**
   - ✅ Mostra tela de login

---

## 🔧 Arquivos Modificados

### 1. **`credentials_manager.py`** (NOVO)
- Gerencia salvamento/carregamento de credenciais
- Codifica/decodifica email
- Funções de conveniência

### 2. **`ws7.py`** (MODIFICADO)
- Importa `credentials_manager`
- Rota `/login`: Salva email se "lembrar" marcado
- Rota `/login` (GET): Tenta login automático
- Rota `/logout`: Remove credenciais salvas

### 3. **`templates/login.html`** (JÁ EXISTENTE)
- Checkbox "Lembrar login" já estava implementado
- Nenhuma modificação necessária

---

## 📦 Estrutura de Arquivos

```
ws7/
├── credentials_manager.py      # ✅ NOVO - Gerencia credenciais
├── ws7.py                       # ✅ MODIFICADO - Usa credentials_manager
├── templates/
│   └── login.html              # ✅ OK - Checkbox já existe
└── user_credentials/           # ✅ CRIADO AUTOMATICAMENTE
    └── saved_login.dat         # Email salvo (criado ao marcar checkbox)
```

---

## 🚀 Compilação

Quando compilar com Nuitka, o sistema funcionará da mesma forma:

```bash
build_nuitka.bat
```

**Resultado:**
```
output/ws7_launcher.dist/
├── ws7_launcher.exe
├── user_credentials/          # ✅ Pasta criada automaticamente
│   └── saved_login.dat        # Credenciais salvas aqui
└── ... (outros arquivos)
```

---

## ✅ Checklist de Funcionalidades

- [x] Checkbox "Lembrar login" no formulário
- [x] Salvar email em arquivo local ao marcar checkbox
- [x] Login automático ao abrir aplicação
- [x] Validar credenciais salvas na API
- [x] Remover credenciais se usuário perder acesso
- [x] Remover credenciais ao fazer logout
- [x] Logs detalhados de todas as operações
- [x] Ofuscação do email (Base64)
- [x] Arquivo salvo localmente (não na nuvem)
- [x] Compatível com executável compilado

---

## 🎉 Resultado Final

**Experiência do Usuário:**

1. **Primeira vez:**
   - Digita email
   - Marca "Lembrar login"
   - Entra no sistema

2. **Todas as próximas vezes:**
   - Abre aplicação
   - **Entra automaticamente** (sem digitar nada)
   - Vai direto para o dashboard

3. **Se perder acesso:**
   - Sistema detecta automaticamente
   - Remove credenciais
   - Mostra "Acesso Negado"

4. **Se fizer logout:**
   - Credenciais são removidas
   - Próxima vez precisa digitar email novamente

---

**Sistema implementado com sucesso!** 🚀
