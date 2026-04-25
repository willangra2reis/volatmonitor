# 🧪 Guia de Teste - Antes de Compilar

Antes de compilar com Nuitka (processo longo), teste se tudo funciona corretamente.

---

## 🎯 Teste 1: Launcher com Janela Nativa

### Instalar dependências de teste:
```bash
pip install pywebview requests
```

### Executar launcher:
```bash
python ws7_launcher.py
```

### ✅ Verificações:
- [ ] Janela nativa abre (não abre navegador)
- [ ] Título: "VolatForex Monitor Pro"
- [ ] Tamanho correto (85% da tela)
- [ ] Login aparece
- [ ] Login funciona
- [ ] Dashboard carrega
- [ ] Gráficos aparecem
- [ ] APIs respondem
- [ ] LocalStorage funciona (idioma, tema)
- [ ] Fechar janela salva configurações em `window_config.json`

### ❌ Se der erro:

#### "WebView2 não encontrado"
**Windows 10/11:** Já deveria estar instalado  
**Solução:** Baixe https://developer.microsoft.com/microsoft-edge/webview2/

#### "Porta 5000 já em uso"
**Solução:** Feche outras instâncias do ws7.py

#### "Módulo não encontrado"
**Solução:**
```bash
pip install -r requirements_build.txt
```

---

## 🎯 Teste 2: Verificar Arquivos Necessários

### Checklist de arquivos:
```bash
# Arquivos Python
ws7_launcher.py ✅
ws7.py ✅
auth_middleware.py ✅
google_auth.py ✅
symbol_mapper.py ✅
technical_indicators.py ✅

# Templates
templates/login.html ✅
templates/access_denied.html ✅

# Static
static/js/i18n.js ✅

# Dados
symbol_mapping.json ✅
.env ✅

# Build
requirements_build.txt ✅
build_nuitka.bat ✅
VOLAT-removebg.ico ✅
```

### Verificar:
```bash
dir templates
dir static\js
dir *.py
```

---

## 🎯 Teste 3: Configurações de Janela

### Testar diferentes resoluções:

#### Edite `ws7_launcher.py` (linha ~267):
```python
# Teste 1: Auto 85%
config.set_resolution('auto', percentage=85)
```

Execute e verifique tamanho.

```python
# Teste 2: Fullscreen
config.fullscreen = True
```

Execute e verifique fullscreen.

```python
# Teste 3: Tamanho fixo
config.set_custom(1600, 1000)
```

Execute e verifique tamanho customizado.

### ✅ Verificações:
- [ ] Resolução auto funciona
- [ ] Fullscreen funciona
- [ ] Tamanho customizado funciona
- [ ] Janela é redimensionável
- [ ] Posição é salva em `window_config.json`

---

## 🎯 Teste 4: Funcionalidades do Dashboard

### Com launcher rodando, teste:

#### Login:
- [ ] Email válido aceito
- [ ] Email inválido rejeitado
- [ ] Redirecionamento funciona

#### Dashboard:
- [ ] Cards de saldo aparecem
- [ ] Gráficos carregam
- [ ] Histórico de trades aparece
- [ ] Botões de fechar trades funcionam
- [ ] Seletor de idioma funciona
- [ ] Tema claro/escuro funciona
- [ ] Frequência de atualização funciona

#### APIs:
Abra DevTools (F12) e verifique:
- [ ] `/api/latest` responde
- [ ] `/api/balance-history` responde
- [ ] `/api/history` responde
- [ ] Sem erros 404 ou 500

#### LocalStorage:
No console do DevTools:
```javascript
localStorage.getItem('language')
localStorage.getItem('theme')
localStorage.getItem('updateFrequency')
```
- [ ] Valores são salvos
- [ ] Valores persistem após fechar/abrir

---

## 🎯 Teste 5: Performance

### Verificar uso de recursos:

#### Abra Task Manager (Ctrl+Shift+Esc):
- [ ] CPU: <5% em idle
- [ ] RAM: <200MB
- [ ] Sem memory leaks (RAM não cresce infinitamente)

#### Teste de stress:
1. Deixe rodando por 5 minutos
2. Verifique se RAM estabiliza
3. Verifique se não trava

---

## 🎯 Teste 6: Webhook (Opcional)

Se você tem EA do MT5 enviando dados:

### Configure webhook:
```
URL: http://127.0.0.1:5000/webhook
```

### Verifique:
- [ ] Dados chegam
- [ ] Dashboard atualiza
- [ ] Gráficos atualizam
- [ ] Sem erros no console

---

## ✅ Checklist Final Antes de Compilar

- [ ] Todos os testes acima passaram
- [ ] Nenhum erro no console
- [ ] Performance aceitável
- [ ] LocalStorage funciona
- [ ] Janela salva configurações
- [ ] Ícone `VOLAT-removebg.ico` existe
- [ ] Arquivo `.env` configurado
- [ ] Visual Studio Build Tools instalado

---

## 🚀 Próximo Passo

Se todos os testes passaram:

```bash
# Compilar versão standalone
build_nuitka.bat

# OU compilar versão onefile
build_nuitka_onefile.bat
```

**Tempo estimado:** 10-20 minutos ☕

---

## 🐛 Problemas Comuns

### Janela não abre
**Causa:** WebView2 não instalado  
**Solução:** Instale WebView2 Runtime

### Dashboard não carrega
**Causa:** Flask não iniciou  
**Solução:** Verifique se porta 5000 está livre

### Gráficos não aparecem
**Causa:** Chart.js não carregou  
**Solução:** Verifique conexão internet (CDN)

### LocalStorage não funciona
**Causa:** WebView2 sem permissões  
**Solução:** Execute como administrador (teste)

### Configurações não salvam
**Causa:** Arquivo `window_config.json` sem permissão  
**Solução:** Verifique permissões da pasta

---

## 📝 Log de Testes

Use esta seção para anotar resultados:

```
Data: ___/___/___
Testador: ___________

Teste 1 - Launcher: [ ] OK [ ] FALHOU
Teste 2 - Arquivos: [ ] OK [ ] FALHOU
Teste 3 - Janela: [ ] OK [ ] FALHOU
Teste 4 - Dashboard: [ ] OK [ ] FALHOU
Teste 5 - Performance: [ ] OK [ ] FALHOU
Teste 6 - Webhook: [ ] OK [ ] FALHOU

Observações:
_________________________________
_________________________________
_________________________________

Pronto para compilar? [ ] SIM [ ] NÃO
```

---

**Boa sorte! 🚀**
