# 💾 LocalStorage e Persistência de Dados

## 🔍 Situação Atual

### O Problema:
O **WebView2** (Microsoft Edge WebView) tem comportamento diferente dependendo de como é executado:

1. **Modo Desenvolvimento** (`python ws7_launcher.py`):
   - Pode usar perfil temporário
   - LocalStorage pode não persistir entre sessões
   - Comportamento varia por versão do pywebview

2. **Modo Compilado** (executável Nuitka):
   - Geralmente funciona melhor
   - Perfil de usuário mais estável
   - LocalStorage tende a persistir corretamente

---

## ✅ Solução Implementada

### Configuração Aplicada:

1. **Variável de Ambiente** (linha 28 do `ws7_launcher.py`):
   ```python
   os.environ['PYWEBVIEW_USERDATA'] = WEBVIEW_DATA_FOLDER
   ```

2. **Pasta Persistente**:
   ```
   F:\canectmt5\ws7\webview_data\
   ```

Esta pasta **deve** conter os dados do WebView2 após o uso.

---

## 🧪 Como Verificar se Está Funcionando

### Teste 1: Verificar Pasta de Dados

1. **Execute a aplicação:**
   ```bash
   python ws7_launcher.py
   ```

2. **Faça login e mude idioma**

3. **Feche a aplicação**

4. **Verifique se a pasta foi criada:**
   ```bash
   dir webview_data
   ```

5. **Deve conter arquivos/pastas como:**
   - `EBWebView/` (dados do Edge)
   - `Local Storage/`
   - `Session Storage/`
   - Outros arquivos de cache

### Teste 2: Verificar LocalStorage via DevTools

1. **Execute com debug ativado:**
   
   Edite `ws7_launcher.py` linha 333:
   ```python
   webview.start(debug=True)  # ← Mude para True
   ```

2. **Execute:**
   ```bash
   python ws7_launcher.py
   ```

3. **Pressione F12** (abre DevTools)

4. **Vá em:** Application → Local Storage → http://127.0.0.1:5000

5. **Verifique se há dados salvos:**
   - `language`
   - `theme`
   - `updateFrequency`
   - etc.

6. **Feche e abra novamente**

7. **Verifique se os dados persistiram**

---

## ⚠️ Limitações Conhecidas

### WebView2 em Modo Desenvolvimento:

O pywebview pode ter limitações em modo desenvolvimento devido a:

1. **Perfil Temporário**: Algumas versões usam perfil temporário por padrão
2. **Permissões**: Windows pode bloquear escrita em algumas pastas
3. **Versão do WebView2 Runtime**: Comportamento varia

### ✅ Solução Definitiva:

**Compilar com Nuitka!** O executável compilado geralmente resolve esses problemas porque:

- Tem contexto de execução mais estável
- Perfil de usuário é criado corretamente
- Permissões são mais consistentes

---

## 🔧 Solução Alternativa: Salvar no Backend

Se o localStorage do WebView2 não funcionar de forma confiável, podemos implementar salvamento no backend Flask.

### Implementação:

#### 1. Criar arquivo de preferências do usuário:

**Adicionar em `ws7.py`:**

```python
import json
import os

# Pasta para preferências de usuários
PREFERENCES_FOLDER = 'user_preferences'
if not os.path.exists(PREFERENCES_FOLDER):
    os.makedirs(PREFERENCES_FOLDER)

def get_user_preferences_file(email):
    """Retorna caminho do arquivo de preferências do usuário"""
    # Sanitiza email para nome de arquivo
    safe_email = email.replace('@', '_at_').replace('.', '_')
    return os.path.join(PREFERENCES_FOLDER, f'{safe_email}.json')

@app.route('/api/save-preferences', methods=['POST'])
@api_login_required
def save_preferences():
    """Salva preferências do usuário"""
    user_email = get_current_user()
    data = request.json
    
    prefs_file = get_user_preferences_file(user_email)
    
    try:
        with open(prefs_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({'status': 'ok', 'message': 'Preferências salvas'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/load-preferences')
@api_login_required
def load_preferences():
    """Carrega preferências do usuário"""
    user_email = get_current_user()
    prefs_file = get_user_preferences_file(user_email)
    
    try:
        if os.path.exists(prefs_file):
            with open(prefs_file, 'r') as f:
                prefs = json.load(f)
            return jsonify({'status': 'ok', 'preferences': prefs})
        else:
            # Preferências padrão
            return jsonify({
                'status': 'ok', 
                'preferences': {
                    'language': 'pt',
                    'theme': 'dark',
                    'updateFrequency': '100'
                }
            })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

#### 2. Modificar JavaScript no Dashboard:

**Adicionar no HTML_TEMPLATE de `ws7.py`:**

```javascript
// Salvar preferências no backend
function savePreferences() {
    const prefs = {
        language: localStorage.getItem('language') || 'pt',
        theme: localStorage.getItem('theme') || 'dark',
        updateFrequency: localStorage.getItem('updateFrequency') || '100'
    };
    
    fetch('/api/save-preferences', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(prefs)
    });
}

// Carregar preferências do backend
async function loadPreferences() {
    try {
        const response = await fetch('/api/load-preferences');
        const data = await response.json();
        
        if (data.status === 'ok') {
            const prefs = data.preferences;
            
            // Aplicar preferências
            localStorage.setItem('language', prefs.language);
            localStorage.setItem('theme', prefs.theme);
            localStorage.setItem('updateFrequency', prefs.updateFrequency);
            
            // Aplicar tema
            if (prefs.theme === 'light') {
                document.body.classList.add('light-mode');
            }
            
            // Aplicar idioma
            changeLanguage(prefs.language);
        }
    } catch (error) {
        console.error('Erro ao carregar preferências:', error);
    }
}

// Carregar ao iniciar
document.addEventListener('DOMContentLoaded', loadPreferences);

// Salvar ao mudar
document.getElementById('language-selector')?.addEventListener('change', savePreferences);
document.getElementById('theme-toggle')?.addEventListener('click', savePreferences);
```

---

## 🎯 Recomendação

### Para Agora:

1. **Teste a versão atual:**
   ```bash
   python ws7_launcher.py
   ```

2. **Verifique se a pasta `webview_data/` é criada**

3. **Se NÃO funcionar em desenvolvimento:**
   - **Não se preocupe!** É limitação do WebView2 em modo dev
   - **Compile e teste o executável**

### Para Produção:

1. **Compile com Nuitka:**
   ```bash
   build_nuitka.bat
   ```

2. **Teste o executável:**
   ```bash
   cd output\ws7_launcher.dist
   ws7_launcher.exe
   ```

3. **Se ainda não funcionar:**
   - Implemente a solução alternativa (backend)
   - Ou use cookies de sessão do Flask

---

## 📊 Comparação de Soluções

| Solução | Prós | Contras | Confiabilidade |
|---------|------|---------|----------------|
| **LocalStorage WebView2** | Nativo, rápido | Pode não funcionar em dev | ⭐⭐⭐ |
| **Backend JSON** | 100% confiável | Requer APIs extras | ⭐⭐⭐⭐⭐ |
| **Cookies Flask** | Simples | Expira com sessão | ⭐⭐⭐⭐ |

---

## 🚀 Próximos Passos

1. **Teste atual:**
   ```bash
   python ws7_launcher.py
   ```

2. **Verifique pasta:**
   ```bash
   dir webview_data
   ```

3. **Se não funcionar, compile:**
   ```bash
   build_nuitka.bat
   ```

4. **Teste executável**

5. **Se ainda não funcionar:**
   - Me avise e implemento solução backend

---

## 💡 Dica

**A forma mais confiável é sempre compilar e testar o executável final!**

O modo desenvolvimento (`python ws7_launcher.py`) é útil para testar lógica, mas pode ter limitações de ambiente.
