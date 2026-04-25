# Guia de Instalação - Windows 11

## 🚀 Início Rápido

### Opção 1: Inicialização Automática (Recomendado)

1. Abra a pasta da aplicação
2. Clique duas vezes em `iniciar.bat`
3. A aplicação será iniciada automaticamente

Se receber erro sobre Python:
1. Execute `verificar_python.bat`
2. Siga as instruções
3. Tente novamente

---

## 📋 Instalação Manual

### Passo 1: Instalar Python 3.12

#### Windows 11:
1. Acesse: https://www.python.org/downloads/
2. Clique em "Download Python 3.12.x"
3. Execute o instalador
4. **IMPORTANTE**: Marque ✅ "Add Python 3.12 to PATH"
5. Clique em "Install Now"
6. Aguarde a conclusão
7. **Reinicie o computador**

#### Verificar Instalação:
Abra o Prompt de Comando (Win + R, digite `cmd`, Enter):
```bash
python --version
```

Deve mostrar: `Python 3.12.x`

---

### Passo 2: Instalar Dependências

Abra o Prompt de Comando na pasta da aplicação:

```bash
pip install -r requirements.txt
```

Aguarde até que todas as dependências sejam instaladas.

---

### Passo 3: Executar a Aplicação

#### Opção A: Usando o script (Recomendado)
```bash
iniciar.bat
```

#### Opção B: Linha de comando
```bash
python ws7.py
```

---

## 🔧 Solução de Problemas

### Erro: "python3.12.dll não foi encontrado"

**Causa**: Python não está instalado ou não está no PATH

**Solução**:
1. Instale Python 3.12 de https://www.python.org/downloads/
2. **Marque "Add Python to PATH"** durante a instalação
3. Reinicie o computador
4. Tente novamente

---

### Erro: "pip: command not found"

**Causa**: pip não foi instalado com Python

**Solução**:
1. Desinstale Python completamente
2. Reinstale Python 3.12
3. **Marque "pip"** durante a instalação
4. Reinicie o computador

---

### Erro: "ModuleNotFoundError"

**Causa**: Dependências não estão instaladas

**Solução**:
```bash
pip install -r requirements.txt
```

---

### Aplicação não abre

**Solução 1**: Verificar Python
```bash
verificar_python.bat
```

**Solução 2**: Reinstalar dependências
```bash
pip install --upgrade -r requirements.txt
```

**Solução 3**: Limpar cache Python
```bash
python -m pip cache purge
pip install -r requirements.txt
```

---

## 📦 Dependências Principais

A aplicação requer:
- **Python 3.12+**
- **Flask** - Framework web
- **Waitress** - Servidor WSGI
- **Requests** - Cliente HTTP
- **python-dotenv** - Variáveis de ambiente

Todas são instaladas automaticamente via `requirements.txt`

---

## 🌐 Acessar a Aplicação

Após iniciar com sucesso:

1. Abra seu navegador
2. Acesse: `http://localhost:5000`
3. Faça login com suas credenciais

---

## 💾 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na pasta da aplicação:

```env
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=sua_chave_secreta_aqui
```

---

## 🐛 Relatório de Erros

Se o problema persistir:

1. Abra o Prompt de Comando
2. Execute: `python -m pip list`
3. Copie a saída
4. Envie junto com:
   - Versão do Windows 11 (Settings > System > About)
   - Versão do Python (`python --version`)
   - Mensagem de erro completa

---

## ✅ Checklist de Instalação

- [ ] Python 3.12 instalado
- [ ] Python está no PATH
- [ ] Computador foi reiniciado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` configurado (se necessário)
- [ ] Porta 5000 não está em uso
- [ ] Firewall permite acesso local

---

## 🚀 Inicialização Automática no Boot

Para iniciar a aplicação automaticamente quando o Windows inicia:

### Windows 11:
1. Pressione `Win + R`
2. Digite: `shell:startup`
3. Copie `iniciar.bat` para essa pasta
4. A aplicação iniciará automaticamente no próximo boot

---

## 📞 Suporte

Para mais informações, consulte:
- `SOLUCAO_ERRO_WINDOWS11.md` - Soluções de problemas específicos
- `README.md` - Documentação geral

---

**Última atualização:** 20 de Novembro de 2025
**Compatibilidade:** Windows 10, Windows 11
