# Opções de Inicialização - ws7 Launcher

## 🎯 Modos de Inicialização

### 1️⃣ Modo Maximizado (Padrão)

**Comando:**
```batch
start "" /MAX "ws7_launcher.exe"
```

**Resultado:**
- ✅ Aplicação abre em tela cheia
- ✅ Janela maximizada automaticamente
- ✅ Melhor aproveitamento do espaço

**Scripts que usam:**
- `iniciar.bat` ✅
- `iniciar_launcher.bat` ✅

---

### 2️⃣ Modo Normal (Janela Padrão)

**Comando:**
```batch
start "" "ws7_launcher.exe"
```

**Resultado:**
- ✅ Aplicação abre em tamanho padrão
- ⚠️ Pode aparecer minimizada em alguns sistemas

---

### 3️⃣ Modo Minimizado

**Comando:**
```batch
start "" /MIN "ws7_launcher.exe"
```

**Resultado:**
- ✅ Aplicação inicia na barra de tarefas
- ✅ Não ocupa espaço na tela
- ⚠️ Precisa clicar na barra para visualizar

---

## 🔧 Parâmetros do Comando `start`

| Parâmetro | Efeito | Uso |
|-----------|--------|-----|
| `/MAX` | Maximiza a janela | Recomendado |
| `/MIN` | Minimiza a janela | Execução em background |
| (nenhum) | Tamanho padrão | Padrão do Windows |
| `/B` | Não abre nova janela | Execução silenciosa |
| `/W` | Aguarda conclusão | Espera o programa fechar |

---

## 📋 Sintaxe Completa

```batch
start [título] [/D caminho] [/I] [/MIN|/MAX] [/SEPARATE|/SHARED] 
       [/LOW|/NORMAL|/HIGH|/REALTIME] [/WAIT] [/B] programa [parâmetros]
```

### Exemplos:

**Maximizado (Atual):**
```batch
start "" /MAX "ws7_launcher.exe"
```

**Minimizado:**
```batch
start "" /MIN "ws7_launcher.exe"
```

**Normal com título:**
```batch
start "ws7 Monitor" "ws7_launcher.exe"
```

**Maximizado com prioridade alta:**
```batch
start "" /MAX /HIGH "ws7_launcher.exe"
```

---

## ✅ Configuração Atual

### `iniciar.bat`
```batch
start "" /MAX "ws7_launcher.exe"
```
- ✅ Inicia maximizado
- ✅ Detecta automaticamente o executável

### `iniciar_launcher.bat`
```batch
start "" /MAX "ws7_launcher.exe"
```
- ✅ Inicia maximizado
- ✅ Verifica Python e dependências

---

## 🎨 Personalizações Possíveis

### Se quiser Minimizado:

Edite `iniciar.bat` linha 26:
```batch
REM Antes:
start "" /MAX "ws7_launcher.exe"

REM Depois:
start "" /MIN "ws7_launcher.exe"
```

### Se quiser Normal (sem maximizar):

Edite `iniciar.bat` linha 26:
```batch
REM Antes:
start "" /MAX "ws7_launcher.exe"

REM Depois:
start "" "ws7_launcher.exe"
```

### Se quiser com Título Customizado:

Edite `iniciar.bat` linha 26:
```batch
REM Antes:
start "" /MAX "ws7_launcher.exe"

REM Depois:
start "ws7 - MT5 Monitor" /MAX "ws7_launcher.exe"
```

---

## 🖥️ Comportamento em Diferentes Sistemas

### Windows 10
- ✅ `/MAX` funciona perfeitamente
- ✅ Janela abre maximizada

### Windows 11
- ✅ `/MAX` funciona perfeitamente
- ✅ Janela abre maximizada
- ⚠️ Pode levar 1-2 segundos a mais

---

## 🔄 Alternativas para Controlar a Janela

### Via VBScript

Crie um arquivo `iniciar_maximizado.vbs`:
```vbscript
Set objShell = CreateObject("WScript.Shell")
objShell.Run "ws7_launcher.exe", 3
```

Parâmetros:
- `0` = Oculto
- `1` = Normal
- `2` = Minimizado
- `3` = Maximizado
- `4` = Normal (sem foco)
- `5` = Foco
- `6` = Minimizado (sem foco)
- `7` = Maximizado (sem foco)

### Via PowerShell

```powershell
$process = Start-Process "ws7_launcher.exe" -PassThru
Start-Sleep -Milliseconds 500
$process.MainWindowHandle | % { [void] [Window]::SetWindowState($_, 3) }
```

---

## 📝 Notas Importantes

- ✅ `/MAX` é o método mais confiável
- ✅ Funciona em Windows 10 e Windows 11
- ✅ Não requer permissões especiais
- ✅ Sem impacto de performance
- ✅ Compatível com todos os tipos de executáveis

---

## 🎯 Recomendação

**Use `/MAX` para:**
- ✅ Melhor experiência do usuário
- ✅ Aproveitar toda a tela
- ✅ Visualizar melhor o dashboard
- ✅ Padrão recomendado

---

**Última atualização:** 26 de Novembro de 2025
