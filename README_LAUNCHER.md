# Guia de Uso - ws7 Launcher

## 📋 Visão Geral

A aplicação ws7 agora suporta múltiplas formas de inicialização:
- ✅ **ws7_launcher.exe** - Executável direto (recomendado)
- ✅ **python ws7.py** - Via Python
- ✅ **Scripts .bat** - Automação completa

---

## 🚀 Início Rápido

### Opção 1: Usar o Executável (Mais Fácil)

1. Clique duas vezes em `iniciar.bat`
2. A aplicação detectará automaticamente `ws7_launcher.exe`
3. O navegador abrirá em `http://localhost:5000`

### Opção 2: Verificar e Instalar Requisitos

Se é a primeira vez que usa:

1. Clique duas vezes em `verificar_python.bat`
2. Aguarde a conclusão (pode levar alguns minutos)
3. Depois clique em `iniciar.bat`

### Opção 3: Iniciar Direto o Executável

1. Clique duas vezes em `iniciar_launcher.bat`
2. O executável será iniciado automaticamente

---

## 📁 Arquivos Inclusos

```
ws7/
├── ws7_launcher.exe              ← Executável principal
├── verificar_python.bat          ← Verifica e instala requisitos
├── iniciar.bat                   ← Inicia a aplicação
├── iniciar_launcher.bat          ← Inicia direto o executável
├── requirements.txt              ← Dependências Python
├── INSTALACAO_WINDOWS11.md       ← Guia de instalação
├── SOLUCAO_ERRO_WINDOWS11.md     ← Solução de problemas
└── README_LAUNCHER.md            ← Este arquivo
```

---

## 🔧 Fluxo de Inicialização

### Primeira Vez (Recomendado)

```
1. Executar: verificar_python.bat
   ↓
   - Verifica Python 3.12
   - Atualiza pip
   - Instala/cria requirements.txt
   - Instala todas as dependências
   ↓
2. Executar: iniciar.bat
   ↓
   - Detecta ws7_launcher.exe
   - Inicia a aplicação
   - Abre navegador em http://localhost:5000
```

### Próximas Vezes

```
Executar: iniciar.bat
↓
- Detecta ws7_launcher.exe
- Inicia a aplicação
- Pronto!
```

---

## 📊 O que Cada Script Faz

### `verificar_python.bat`

**Função:** Verificar e preparar o ambiente Python

**Etapas:**
1. ✅ Verifica se Python 3.12 está instalado
2. ✅ Verifica se pip está disponível
3. ✅ Atualiza pip para versão mais recente
4. ✅ Cria `requirements.txt` se não existir
5. ✅ Instala todas as dependências

**Quando usar:**
- Primeira execução
- Após instalar Python
- Se receber erro de dependências

**Tempo:** 2-5 minutos (primeira vez), 30 segundos (próximas)

---

### `iniciar.bat`

**Função:** Iniciar a aplicação de forma inteligente

**Lógica:**
1. Verifica se `ws7_launcher.exe` existe
   - Se sim: inicia o executável
   - Se não: tenta `python ws7.py`
2. Verifica dependências
3. Inicia a aplicação

**Quando usar:**
- Sempre que quiser iniciar a aplicação

**Tempo:** 2-5 segundos

---

### `iniciar_launcher.bat`

**Função:** Iniciar diretamente o executável

**Etapas:**
1. Verifica se `ws7_launcher.exe` existe
2. Verifica se Python está instalado
3. Verifica dependências
4. Inicia `ws7_launcher.exe`

**Quando usar:**
- Se preferir iniciar direto o executável
- Se `iniciar.bat` não funcionar

**Tempo:** 2-5 segundos

---

## ✅ Requisitos Instalados Automaticamente

O script `verificar_python.bat` instala:

```
Flask==3.0.0                  # Framework web
Werkzeug==3.0.1              # WSGI utilities
Waitress==2.1.2              # Servidor WSGI
requests==2.31.0             # Cliente HTTP
python-dotenv==1.0.0         # Variáveis de ambiente
Jinja2==3.1.2                # Template engine
MarkupSafe==2.1.3            # Segurança de templates
click==8.1.7                 # CLI utilities
itsdangerous==2.1.2          # Segurança de dados
```

---

## 🔍 Solução de Problemas

### Problema: "ws7_launcher.exe não foi encontrado"

**Solução:**
1. Verifique se o arquivo existe na pasta
2. Se não existir, use `python ws7.py` ou `iniciar.bat`

---

### Problema: "Python não foi encontrado"

**Solução:**
1. Execute `verificar_python.bat`
2. Instale Python 3.12 de https://www.python.org/downloads/
3. Marque "Add Python to PATH"
4. Reinicie o computador
5. Execute `verificar_python.bat` novamente

---

### Problema: "Erro ao instalar dependências"

**Solução:**
```bash
pip install --upgrade -r requirements.txt
```

Ou execute `verificar_python.bat` novamente.

---

### Problema: "Aplicação não abre no navegador"

**Solução:**
1. Abra manualmente: http://localhost:5000
2. Verifique se a porta 5000 não está em uso
3. Verifique o firewall do Windows

---

## 🌐 Acessar a Aplicação

Após iniciar com sucesso:

1. **Automático:** Navegador abre em `http://localhost:5000`
2. **Manual:** Abra seu navegador e acesse `http://localhost:5000`
3. **Faça login** com suas credenciais

---

## 🛑 Parar a Aplicação

### Se iniciada com `ws7_launcher.exe`
- Feche a janela do executável
- Ou pressione `Ctrl + C` no console

### Se iniciada com `python ws7.py`
- Pressione `Ctrl + C` no console

---

## 📝 Notas Importantes

- ✅ Python 3.12 é obrigatório
- ✅ Primeira execução pode levar 2-5 minutos
- ✅ Próximas execuções são rápidas (2-5 segundos)
- ✅ Requer conexão com internet para instalar dependências
- ✅ Requer permissões de administrador (em alguns casos)

---

## 🔄 Atualizar Dependências

Se precisar atualizar as dependências:

```bash
pip install --upgrade -r requirements.txt
```

Ou execute `verificar_python.bat` novamente.

---

## 📞 Suporte

Se o problema persistir:

1. Consulte `SOLUCAO_ERRO_WINDOWS11.md`
2. Consulte `INSTALACAO_WINDOWS11.md`
3. Verifique se Python 3.12 está instalado
4. Verifique se todas as dependências estão instaladas

---

## 🎯 Fluxograma Completo

```
┌─────────────────────────────────────────┐
│  Clique em iniciar.bat                  │
└────────────┬────────────────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ ws7_launcher.exe   │
    │ existe?            │
    └────┬────────┬──────┘
         │ SIM    │ NÃO
         │        │
         ▼        ▼
    ┌─────────┐  ┌──────────────────┐
    │ Inicia  │  │ Tenta python     │
    │ .exe    │  │ ws7.py           │
    └─────────┘  └──────────────────┘
         │              │
         └──────┬───────┘
                ▼
        ┌───────────────────┐
        │ Verifica Python   │
        └─────────┬─────────┘
                  │
         ┌────────▼────────┐
         │ Python OK?      │
         └────┬────────┬───┘
              │ SIM    │ NÃO
              │        │
              ▼        ▼
         ┌────────┐  ┌──────────────────┐
         │ Inicia │  │ Erro: Execute    │
         │ App    │  │ verificar_python │
         └────────┘  └──────────────────┘
              │
              ▼
        ┌──────────────────┐
        │ Navegador abre   │
        │ localhost:5000   │
        └──────────────────┘
```

---

**Última atualização:** 26 de Novembro de 2025
**Compatibilidade:** Windows 10, Windows 11
