# 🔧 Guia: Onde Fazer Alterações na Aplicação

Este guia explica onde modificar o código dependendo do tipo de alteração que você quer fazer.

---

## 📁 Estrutura de Arquivos

```
ws7/
├── ws7.py                    # ⭐ LÓGICA PRINCIPAL DA APLICAÇÃO
├── ws7_launcher.py           # 🪟 CONFIGURAÇÕES DA JANELA NATIVA
├── auth_middleware.py        # 🔐 AUTENTICAÇÃO E SEGURANÇA
├── google_auth.py            # 🌐 INTEGRAÇÃO GOOGLE APPS SCRIPT
├── symbol_mapper.py          # 📊 MAPEAMENTO DE SÍMBOLOS
├── technical_indicators.py   # 📈 INDICADORES TÉCNICOS
├── templates/                # 🎨 TEMPLATES HTML
│   ├── login.html
│   └── access_denied.html
└── static/js/                # 💻 JAVASCRIPT FRONTEND
    └── i18n.js
```

---

## 🎯 Onde Fazer Cada Tipo de Alteração

### 1. ⭐ Lógica de Negócio / Backend (ws7.py)

**Modifique `ws7.py` quando quiser:**

#### Adicionar/Modificar Rotas:
```python
# Exemplo: Nova rota API
@app.route('/api/minha-nova-rota')
@api_login_required
def minha_nova_rota():
    return jsonify({'status': 'ok'})
```

#### Modificar Processamento de Dados:
```python
# Exemplo: Alterar cálculo de lucro
def calcular_lucro(trades):
    # Sua lógica aqui
    return total
```

#### Adicionar Novos Cards/Gráficos no Dashboard:
```python
# No HTML_TEMPLATE dentro de ws7.py
# Adicione novos elementos HTML
```

#### Modificar Webhook:
```python
@app.route('/webhook', methods=['POST'])
def webhook():
    # Modificar processamento de dados do MT5
    pass
```

#### Adicionar Novos Indicadores:
```python
# Importar de technical_indicators.py
from technical_indicators import TechnicalIndicators

# Usar no processamento
indicators = TechnicalIndicators.calculate_rsi(prices)
```

#### Modificar Configurações do Servidor:
```python
# No final do ws7.py
serve(app, 
      host='127.0.0.1', 
      port=5000,  # Mudar porta aqui
      threads=8)
```

---

### 2. 🪟 Configurações de Janela (ws7_launcher.py)

**Modifique `ws7_launcher.py` quando quiser:**

#### Alterar Tamanho/Resolução da Janela:
```python
# Linha ~265
config.set_resolution('auto', percentage=85)  # Mudar percentual
# OU
config.set_custom(1600, 1000)  # Tamanho fixo
```

#### Mudar Estilo da Janela:
```python
# Linha ~276
config.fullscreen = True      # Fullscreen
config.frameless = True       # Sem bordas
config.on_top = True          # Sempre no topo
config.resizable = False      # Não redimensionável
```

#### Alterar Título da Janela:
```python
# Linha ~234
window = webview.create_window(
    title='Seu Novo Título Aqui',  # ← Mudar aqui
    ...
)
```

#### Modificar Cor de Fundo:
```python
# Linha ~246
background_color='#1a1a1a',  # ← Mudar cor aqui
```

#### Adicionar Funcionalidades à API JavaScript:
```python
# Classe WindowAPI (linha ~185)
class WindowAPI:
    def minha_nova_funcao(self):
        """Nova função acessível do JavaScript"""
        return "resultado"
```

---

### 3. 🔐 Autenticação (auth_middleware.py)

**Modifique `auth_middleware.py` quando quiser:**

#### Alterar Tempo de Expiração de Sessão:
```python
TOKEN_EXPIRATION = 24 * 60 * 60  # 24 horas (em segundos)
```

#### Alterar Intervalo de Revalidação:
```python
REVALIDATION_INTERVAL = 5 * 60  # 5 minutos (em segundos)
```

#### Adicionar Novas Verificações de Segurança:
```python
@login_required
def minha_verificacao():
    # Adicionar lógica de segurança
    pass
```

---

### 4. 🌐 Integração Google (google_auth.py)

**Modifique `google_auth.py` quando quiser:**

#### Alterar URL da API:
```python
GOOGLE_API_URL = "https://script.google.com/macros/s/SEU_NOVO_ID/exec"
```

#### Alterar Tempo de Cache:
```python
CACHE_DURATION = 30  # 30 segundos
```

#### Adicionar Novos Campos de Usuário:
```python
def get_user_custom_field(email: str):
    user_data = check_user_status(email)
    return user_data.get("seu_campo_customizado")
```

---

### 5. 🎨 Interface (HTML/CSS/JS)

**Modifique quando quiser:**

#### Alterar Layout do Dashboard:
- **Arquivo:** `ws7.py` (HTML_TEMPLATE)
- **O que:** Adicionar/remover cards, gráficos, botões

#### Alterar Traduções:
- **Arquivo:** `static/js/i18n.js`
- **O que:** Adicionar novos idiomas ou textos

#### Alterar Tela de Login:
- **Arquivo:** `templates/login.html`
- **O que:** Modificar design, adicionar campos

#### Adicionar JavaScript Customizado:
- **Arquivo:** `ws7.py` (dentro do HTML_TEMPLATE)
- **O que:** Adicionar funções JavaScript

---

### 6. 📊 Indicadores Técnicos (technical_indicators.py)

**Modifique `technical_indicators.py` quando quiser:**

#### Adicionar Novo Indicador:
```python
@staticmethod
def calculate_meu_indicador(prices, period=14):
    """Calcula meu indicador customizado"""
    # Sua lógica aqui
    return resultado
```

#### Modificar Indicadores Existentes:
```python
# Alterar cálculo de RSI, Hull MA, etc.
```

---

### 7. 📦 Build/Compilação

**Modifique quando quiser:**

#### Alterar Configurações de Build:
- **Arquivo:** `build_nuitka.bat`
- **O que:** Adicionar/remover packages, mudar ícone

#### Adicionar Novos Arquivos ao Executável:
```batch
--include-data-file=meu_arquivo.json=meu_arquivo.json ^
```

#### Mudar Nome do Executável:
```batch
--product-name="Seu Novo Nome" ^
```

---

## 🔄 Workflow de Alterações

### Para Alterações Simples (Backend/Frontend):

1. **Modificar `ws7.py`**
   ```python
   # Fazer suas alterações
   ```

2. **Testar localmente:**
   ```bash
   python ws7_launcher.py
   ```

3. **Se funcionar, recompilar:**
   ```bash
   build_nuitka.bat
   ```

---

### Para Alterações na Janela:

1. **Modificar `ws7_launcher.py`**
   ```python
   # Alterar configurações de janela
   ```

2. **Testar localmente:**
   ```bash
   python ws7_launcher.py
   ```

3. **Se funcionar, recompilar:**
   ```bash
   build_nuitka.bat
   ```

---

### Para Alterações em Ambos:

1. **Modificar `ws7.py` E `ws7_launcher.py`**

2. **Testar localmente:**
   ```bash
   python ws7_launcher.py
   ```

3. **Recompilar:**
   ```bash
   build_nuitka.bat
   ```

---

## ⚠️ IMPORTANTE: Sempre Teste Antes de Compilar!

```bash
# SEMPRE faça isso antes de compilar:
python ws7_launcher.py

# Verifique:
# ✅ Aplicação abre
# ✅ Funcionalidades funcionam
# ✅ Sem erros no console

# SÓ DEPOIS compile:
build_nuitka.bat
```

**Por quê?** Compilação demora 10-20 minutos. Teste local demora 2 segundos!

---

## 📋 Exemplos Práticos

### Exemplo 1: Adicionar Novo Card no Dashboard

**Arquivo:** `ws7.py`

```python
# Dentro do HTML_TEMPLATE, adicione:
<div class="card">
    <h3>Meu Novo Card</h3>
    <p id="meu-valor">0</p>
</div>

# No JavaScript, atualize o valor:
document.getElementById('meu-valor').textContent = dados.meu_campo;
```

---

### Exemplo 2: Mudar Cor da Janela

**Arquivo:** `ws7_launcher.py`

```python
# Linha ~246
background_color='#2c3e50',  # Azul escuro
```

---

### Exemplo 3: Adicionar Nova Rota API

**Arquivo:** `ws7.py`

```python
@app.route('/api/meus-dados')
@api_login_required
def meus_dados():
    return jsonify({
        'status': 'ok',
        'dados': [1, 2, 3]
    })
```

---

### Exemplo 4: Alterar Porta do Servidor

**Arquivo:** `ws7_launcher.py`

```python
# Linha ~145 (FlaskServer.start)
serve(app, 
      host='127.0.0.1', 
      port=8080,  # ← Mudar de 5000 para 8080
      threads=8)

# E linha ~235 (create_window)
url='http://127.0.0.1:8080',  # ← Mudar aqui também
```

---

## 🎯 Resumo Rápido

| Tipo de Alteração | Arquivo Principal |
|-------------------|-------------------|
| Lógica de negócio | `ws7.py` |
| Rotas/APIs | `ws7.py` |
| Dashboard/HTML | `ws7.py` (HTML_TEMPLATE) |
| Janela/Interface | `ws7_launcher.py` |
| Autenticação | `auth_middleware.py` |
| Google API | `google_auth.py` |
| Indicadores | `technical_indicators.py` |
| Traduções | `static/js/i18n.js` |
| Build | `build_nuitka.bat` |

---

## 💡 Dica Pro

**Sempre mantenha uma cópia de backup antes de alterações grandes!**

```bash
# Backup rápido
xcopy ws7.py ws7.py.backup
xcopy ws7_launcher.py ws7_launcher.py.backup
```

---

**Boa sorte com suas alterações!** 🚀
