# 🚀 Guia Completo de Build - VolatForex Monitor Pro

Este guia detalha como compilar sua aplicação Flask em um executável standalone com **Nuitka + WebView2**.

---

## 📋 Pré-requisitos

### 1. Python 3.8 ou superior
```bash
python --version
# Deve retornar: Python 3.8.x ou superior
```

### 2. Visual Studio Build Tools (Compilador C)
**OBRIGATÓRIO para Nuitka funcionar!**

#### Download:
https://visualstudio.microsoft.com/downloads/

#### Instalação:
1. Baixe **"Build Tools for Visual Studio 2022"**
2. Execute o instalador
3. Selecione: **"Desktop development with C++"**
4. Aguarde instalação (~6GB)

#### Verificar instalação:
```bash
# Abra um NOVO terminal após instalar
cl
# Deve mostrar: Microsoft (R) C/C++ Optimizing Compiler
```

### 3. WebView2 Runtime (Windows)
- **Windows 10/11**: Já vem instalado ✅
- **Windows 7/8**: Baixar em https://developer.microsoft.com/microsoft-edge/webview2/

---

## 🔧 Instalação de Dependências

### Passo 1: Instalar dependências de build
```bash
pip install -r requirements_build.txt
```

Isso instalará:
- `nuitka` - Compilador Python → C
- `pywebview` - Janela nativa WebView2
- `flask`, `waitress`, etc. - Dependências runtime

### Passo 2: Verificar instalação
```bash
python -c "import nuitka; print('Nuitka OK')"
python -c "import webview; print('WebView OK')"
```

---

## 🏗️ Compilação

### Opção 1: Standalone (Recomendado)
**Gera pasta com múltiplos arquivos - Startup instantâneo**

```bash
build_nuitka.bat
```

**Resultado:**
```
output/
└── ws7_launcher.dist/
    ├── ws7_launcher.exe (5-10MB) ← Executável principal
    ├── python3.dll
    ├── _internal/ (bibliotecas)
    ├── templates/
    ├── static/
    └── symbol_mapping.json
```

**Tamanho total:** ~50-70MB  
**Startup:** <1 segundo ✅

---

### Opção 2: Onefile
**Gera arquivo único - Startup 2-3s mais lento**

```bash
build_nuitka_onefile.bat
```

**Resultado:**
```
output/
└── ws7_launcher.exe (60-80MB) ← Arquivo único
```

**Tamanho:** ~60-80MB  
**Startup:** 2-3 segundos (extrai em %TEMP%)

---

## ⏱️ Tempo de Compilação

| Compilação | Tempo Estimado |
|------------|----------------|
| Primeira vez | 10-20 minutos |
| Subsequentes | 5-10 minutos |
| Onefile | +30% tempo |

**Dica:** Deixe compilando e vá tomar um café ☕

---

## 🧪 Testando o Executável

### Teste Local (antes de distribuir):

#### Standalone:
```bash
cd output\ws7_launcher.dist
ws7_launcher.exe
```

#### Onefile:
```bash
cd output
ws7_launcher.exe
```

### O que verificar:
- ✅ Janela abre sem erros
- ✅ Login funciona
- ✅ Dashboard carrega
- ✅ Gráficos aparecem
- ✅ APIs respondem
- ✅ LocalStorage funciona (idioma, tema)
- ✅ Fechar janela salva configurações

---

## 📦 Distribuição

### Standalone (Recomendado):
1. Renomeie a pasta:
   ```
   output\ws7_launcher.dist → VolatForexMonitorPro
   ```

2. Compacte em ZIP:
   ```
   VolatForexMonitorPro.zip
   ```

3. Distribua o ZIP

4. Usuário descompacta e executa `ws7_launcher.exe`

### Onefile:
1. Renomeie o executável:
   ```
   output\ws7_launcher.exe → VolatForexMonitorPro.exe
   ```

2. Distribua o arquivo único

---

## 🎨 Configurações de Janela

### Editar `ws7_launcher.py` (antes de compilar):

#### Resolução Automática (padrão):
```python
config.set_resolution('auto', percentage=85)
# Usa 85% da tela do usuário
```

#### Resolução Fixa:
```python
config.set_resolution('fhd')  # 1920x1080
# Opções: 'hd', 'fhd', 'qhd', '4k'
```

#### Tamanho Customizado:
```python
config.set_custom(1600, 1000)
```

#### Fullscreen:
```python
config.fullscreen = True
```

#### Janela Sem Bordas (moderno):
```python
config.frameless = True
config.resizable = False
```

#### Sempre no Topo:
```python
config.on_top = True
```

---

## 🔒 Segurança e Ofuscação

### Nível de Proteção Atual:
- ✅ Código compilado para C nativo
- ✅ Impossível extrair código Python original
- ✅ Descompiladores Python não funcionam
- ✅ Equivalente a C++ compilado

### Ofuscação Adicional (Opcional):

#### 1. Instalar PyArmor:
```bash
pip install pyarmor
```

#### 2. Ofuscar código:
```bash
pyarmor gen --output dist_protected ws7.py auth_middleware.py google_auth.py
```

#### 3. Copiar arquivos protegidos:
```bash
copy dist_protected\*.py .
```

#### 4. Compilar normalmente:
```bash
build_nuitka.bat
```

**Resultado:** Proteção extrema (código ofuscado + compilado)

---

## 🐛 Troubleshooting

### Erro: "cl.exe não encontrado"
**Causa:** Visual Studio Build Tools não instalado  
**Solução:** Instale conforme seção "Pré-requisitos"

### Erro: "WebView2 não encontrado"
**Causa:** WebView2 Runtime não instalado (Windows 7/8)  
**Solução:** Baixe em https://developer.microsoft.com/microsoft-edge/webview2/

### Erro: "Módulo X não encontrado"
**Causa:** Dependência faltando  
**Solução:**
```bash
pip install -r requirements_build.txt
```

### Executável não abre
**Causa:** Antivírus bloqueando  
**Solução:** Adicione exceção no antivírus

### Janela não aparece
**Causa:** Flask não iniciou  
**Solução:** Teste com `debug=True` em `ws7_launcher.py`:
```python
webview.start(debug=True)
```

### Erro ao carregar templates
**Causa:** Arquivos não incluídos  
**Solução:** Verifique se `templates/` e `static/` existem na pasta

---

## 📊 Comparação de Métodos

| Método | Tamanho | Startup | Segurança | Facilidade |
|--------|---------|---------|-----------|------------|
| **Nuitka Standalone** | 50-70MB | <1s | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Nuitka Onefile | 60-80MB | 2-3s | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| PyInstaller | 30-50MB | <1s | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| PyArmor + Nuitka | 55-75MB | <1s | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 Workflow Recomendado

### Desenvolvimento:
```bash
python ws7_launcher.py
# Testa com janela nativa
```

### Build de Teste:
```bash
build_nuitka.bat
# Compila versão standalone
```

### Build Final:
```bash
# 1. Atualizar versão em ws7_launcher.py
# 2. Testar tudo
# 3. Compilar
build_nuitka.bat

# 4. Testar executável
cd output\ws7_launcher.dist
ws7_launcher.exe

# 5. Renomear e distribuir
```

---

## 📝 Checklist de Release

Antes de distribuir:

- [ ] Testado em máquina limpa (sem Python instalado)
- [ ] Login funciona
- [ ] Dashboard carrega
- [ ] Gráficos aparecem
- [ ] APIs respondem
- [ ] LocalStorage funciona
- [ ] Fechar/abrir mantém configurações
- [ ] Ícone aparece corretamente
- [ ] Versão atualizada no executável
- [ ] README para usuário final criado

---

## 🆘 Suporte

### Logs de Debug:

#### Habilitar logs detalhados:
Edite `ws7_launcher.py`:
```python
webview.start(debug=True)  # Abre DevTools
```

#### Logs do Nuitka:
```bash
# Build com logs detalhados
python -m nuitka --show-progress --show-modules ws7_launcher.py
```

---

## 🚀 Próximos Passos

### Criar Instalador (Opcional):

Use **Inno Setup** para criar instalador profissional:

1. Baixe: https://jrsoftware.org/isdl.php
2. Crie script `.iss` (exemplo abaixo)
3. Compile instalador

#### Exemplo `installer.iss`:
```iss
[Setup]
AppName=VolatForex Monitor Pro
AppVersion=1.0
DefaultDirName={pf}\VolatForex
DefaultGroupName=VolatForex
OutputBaseFilename=VolatForex_Setup
Compression=lzma2
SolidCompression=yes
SetupIconFile=VOLAT-removebg.ico

[Files]
Source: "output\ws7_launcher.dist\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\VolatForex Monitor Pro"; Filename: "{app}\ws7_launcher.exe"
Name: "{commondesktop}\VolatForex Monitor Pro"; Filename: "{app}\ws7_launcher.exe"

[Run]
Filename: "{app}\ws7_launcher.exe"; Description: "Iniciar VolatForex"; Flags: postinstall nowait
```

---

## 📚 Recursos Adicionais

- **Nuitka Docs:** https://nuitka.net/doc/user-manual.html
- **PyWebView Docs:** https://pywebview.flowrl.com/
- **WebView2 Docs:** https://developer.microsoft.com/microsoft-edge/webview2/

---

## ✅ Resumo Rápido

```bash
# 1. Instalar dependências
pip install -r requirements_build.txt

# 2. Compilar
build_nuitka.bat

# 3. Testar
cd output\ws7_launcher.dist
ws7_launcher.exe

# 4. Distribuir
# Compacte a pasta ou crie instalador
```

**Pronto! Sua aplicação agora é um executável standalone seguro com janela nativa.** 🎉
