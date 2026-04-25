# Sistema de Autenticação Supabase - VolatForex Monitor Pro

## 📋 Visão Geral

Este sistema implementa autenticação completa via Supabase no VolatForex Monitor Pro, permitindo controle de acesso baseado no campo `PURCHASE_APPROVED` da tabela "perfil de usuarios".

## 🚀 Configuração Inicial

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais do Supabase:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
FLASK_SECRET_KEY=your-secret-key-change-this-in-production
```

### 3. Configurar Supabase

No seu projeto Supabase, certifique-se de que:

1. **Autenticação está habilitada**
2. **Providers OAuth configurados** (GitHub, Google se necessário)
3. **Tabela "perfil de usuarios" existe** com:
   - Campo `id` (UUID, chave primária e estrangeira para auth.users)
   - Campo `PVAR` (text) - deve conter "PURCHASE_APPROVED" para acesso

### 4. Estrutura da Tabela

```sql
-- Estrutura real da tabela "perfil de usuarios"
create table public.perfil de usuarios (
  id uuid not null default gen_random_uuid (),
  created_at timestamp with time zone not null default now(),
  nome text null,
  email text null,
  telefone text null,
  "PVAR" text null,
  "Crypto" text not null default 'vazio'::text,
  "Dolaribov" text null default 'vazio'::text,
  stockbrasil text null default 'vazio'::text,
  stockamerica text null default 'vazio'::text,
  bonus text null,
  boasvindas boolean null default false,
  ref text null,
  data ativa ref text not null default '1'::text,
  constraint perfil de usuarios_pkey primary key (id),
  constraint perfil de usuarios_id_fkey foreign KEY (id) references auth.users (id) on update CASCADE on delete CASCADE
);
```

**IMPORTANTE:** A coluna `PVAR` deve conter o valor `"PURCHASE_APPROVED"` para liberar acesso ao sistema.

## 🔐 Como Funciona

### Fluxo de Autenticação

1. **Usuário acessa o sistema** → Redirecionado para `/login`
2. **Faz login** → Email/senha ou OAuth (GitHub/Google)
3. **Sistema verifica** → Campo `PVAR` na tabela (deve ser "PURCHASE_APPROVED")
4. **Acesso liberado** → Se PVAR = "PURCHASE_APPROVED", acessa o dashboard
5. **Acesso negado** → Se PVAR ≠ "PURCHASE_APPROVED", vai para página de acesso negado

### Rotas Protegidas

Todas as rotas principais estão protegidas com `@login_required`:

- `/` - Dashboard principal
- `/api/latest` - Dados mais recentes
- `/api/balance-history` - Histórico de saldo
- `/api/history` - Histórico de trades
- `/api/close-*` - Comandos de fechamento de ordens

### Rotas Públicas

- `/login` - Página de login
- `/logout` - Logout
- `/callback` - Callback OAuth
- `/access-denied` - Acesso negado
- `/webhook` - Webhook do MT5 (sem autenticação)
- `/api/status` - Status do servidor

## 🛠️ Arquivos Criados

```
ws7/
├── flask_storage.py          # Armazenamento de sessão Flask
├── supabase_client.py        # Cliente Supabase configurado
├── auth_middleware.py        # Middleware de autenticação
├── templates/
│   ├── login.html           # Página de login
│   └── access_denied.html   # Página de acesso negado
├── requirements.txt         # Dependências Python
├── .env.example            # Exemplo de configuração
└── ws7.py                  # Arquivo principal modificado
```

## 🔧 Personalização

### Modificar Verificação de Acesso

Para alterar a lógica de verificação, edite `auth_middleware.py`:

```python
def check_purchase_approved(user_id: str) -> bool:
    # Sua lógica personalizada aqui
    response = supabase.table('perfil de usuarios').select('PVAR').eq('id', user_id).execute()
    pvar_value = response.data[0].get('PVAR', '')
    return pvar_value == 'PURCHASE_APPROVED'
```

### Adicionar Novos Providers OAuth

No `ws7.py`, adicione novas rotas:

```python
@app.route('/signin/provider')
def signin_with_provider():
    res = supabase.auth.sign_in_with_oauth({
        "provider": "provider_name",
        "options": {
            "redirect_to": f"{request.host_url}callback"
        }
    })
    return redirect(res.url)
```

## 🚨 Segurança

### Pontos Importantes

1. **Chave Secreta**: Sempre use uma chave secreta forte em produção
2. **HTTPS**: Use HTTPS em produção
3. **Variáveis de Ambiente**: Nunca commite credenciais no código
4. **RLS**: Configure Row Level Security no Supabase se necessário

### Configuração de Produção

```env
FLASK_SECRET_KEY=uma-chave-muito-segura-e-aleatoria
DEBUG=False
```

## 🧪 Testando o Sistema

### 1. Iniciar o Servidor

```bash
python ws7.py
```

### 2. Acessar as URLs

- **Dashboard**: http://127.0.0.1:5000
- **Login**: http://127.0.0.1:5000/login
- **Status**: http://127.0.0.1:5000/api/status

### 3. Criar Usuário de Teste

1. Registre um usuário no Supabase
2. Adicione entrada na tabela "perfil de usuarios"
3. Defina `PURCHASE_APPROVED = true`
4. Teste o login

## 🐛 Troubleshooting

### Erro: "Módulo não encontrado"
```bash
pip install -r requirements.txt
```

### Erro: "Supabase URL não configurada"
Verifique o arquivo `.env` e as variáveis de ambiente.

### Erro: "Tabela não encontrada"
Certifique-se de que a tabela "perfil de usuarios" existe no Supabase.

### Usuário não consegue acessar
Verifique se `PVAR = 'PURCHASE_APPROVED'` na tabela.

## 📞 Suporte

Para dúvidas sobre a implementação:

1. Verifique os logs do console
2. Confirme configurações do Supabase
3. Teste com usuário de desenvolvimento

## 🔄 Atualizações Futuras

Possíveis melhorias:

- [ ] Sistema de roles mais granular
- [ ] Cache de verificações de acesso
- [ ] Logs de auditoria
- [ ] Interface de administração
- [ ] Renovação automática de tokens
