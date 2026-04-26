from functools import wraps
from flask import redirect, url_for, session, request, jsonify, make_response
import secrets
import time

# Armazena tokens de sessão válidos (em memória)
# Formato: {session_token: {"created_at": timestamp, "last_validated": timestamp, "email": email}}
_valid_session_tokens = {}

# Configurações de revalidação
TOKEN_EXPIRATION = 24 * 60 * 60  # 24 horas de inatividade
REVALIDATION_INTERVAL = 5 * 60  # Revalida status a cada 5 minutos

def generate_session_token():
    """Gera um token único para a sessão"""
    return secrets.token_urlsafe(32)

def invalidate_session_token(token):
    """Invalida um token de sessão"""
    if token and token in _valid_session_tokens:
        del _valid_session_tokens[token]
        print(f"[AUTH] Token de sessão invalidado: {token[:16]}...")

def is_session_valid(token):
    """Verifica se o token de sessão é válido e não expirou"""
    if not token or token not in _valid_session_tokens:
        return False
    
    token_data = _valid_session_tokens[token]
    current_time = time.time()
    
    # Verifica se o token expirou por inatividade
    if current_time - token_data["created_at"] > TOKEN_EXPIRATION:
        print(f"[AUTH] Token expirado por inatividade: {token[:16]}...")
        invalidate_session_token(token)
        return False
    
    return True

def should_revalidate_user(token):
    """Verifica se deve revalidar o status do usuário na API"""
    if not token or token not in _valid_session_tokens:
        return True
    
    token_data = _valid_session_tokens[token]
    current_time = time.time()
    last_validated = token_data.get("last_validated", 0)
    
    # Revalida se passou o intervalo de revalidação
    return (current_time - last_validated) > REVALIDATION_INTERVAL

def update_token_validation(token, email):
    """Atualiza o timestamp de última validação do token"""
    if token in _valid_session_tokens:
        _valid_session_tokens[token]["last_validated"] = time.time()
        _valid_session_tokens[token]["email"] = email

def login_required(f):
    """Decorator para verificar se o usuário está logado e aprovado
    
    Usa token de sessão único + revalidação periódica na API
    Previne acesso via cache do navegador ou botão voltar
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verifica se há um token de sessão válido
            session_token = session.get('session_token')
            if not session_token or not is_session_valid(session_token):
                # Sessão inválida ou expirada - limpa e redireciona
                session.clear()
                return redirect(url_for('login'))
            
            # Verifica se há um email e status na sessão
            user_email = session.get('user_email')
            user_status = session.get('user_status')
            
            if not user_email or not user_status:
                session.clear()
                return redirect(url_for('login'))
            
            # Verifica se a sessão já foi marcada como invalidada (evita múltiplas revalidações)
            if session.get('_session_invalidated'):
                session.clear()
                return redirect(url_for('login'))
            
            # Revalida o status do usuário na API se necessário (a cada 5 minutos)
            if should_revalidate_user(session_token):
                from google_auth import check_user_status
                
                print(f"[AUTH] Revalidando status de {user_email}...")
                user_data = check_user_status(user_email)
                
                if not user_data:
                    # Usuário não encontrado - invalida sessão
                    print(f"[AUTH] ❌ Usuário {user_email} não encontrado na revalidação")
                    invalidate_session_token(session_token)
                    session['_session_invalidated'] = True  # Marca como invalidada
                    session.clear()
                    return redirect(url_for('login'))
                
                new_status = user_data.get('status')
                
                if new_status != 'PURCHASE_APPROVED':
                    # Status mudou - não está mais aprovado
                    print(f"[AUTH] ⚠️ Status de {user_email} mudou para: {new_status} - Sessão invalidada")
                    invalidate_session_token(session_token)
                    
                    # Marca sessão como invalidada ANTES de limpar
                    session['_session_invalidated'] = True
                    session['pending_user_name'] = user_data.get('pnome', '')
                    session['pending_user_email'] = user_email
                    
                    # Limpa dados sensíveis mas mantém flags temporárias
                    session.pop('user_email', None)
                    session.pop('user_status', None)
                    session.pop('session_token', None)
                    
                    return redirect(url_for('access_denied'))
                
                # Status ainda é PURCHASE_APPROVED - atualiza sessão e token
                session['user_status'] = new_status
                session['user_name'] = user_data.get('pnome', '')
                session['user_full_name'] = user_data.get('nomecompleto', '')
                update_token_validation(session_token, user_email)
                print(f"[AUTH] ✅ Status revalidado: {user_email} - PURCHASE_APPROVED")
            
            # Verifica se o status é PURCHASE_APPROVED
            if session.get('user_status') != 'PURCHASE_APPROVED':
                invalidate_session_token(session_token)
                session.clear()
                return redirect(url_for('access_denied'))
            
            # Adiciona headers para prevenir cache do navegador
            response = make_response(f(*args, **kwargs))
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
            
        except Exception as e:
            print(f"Erro na verificação de autenticação: {e}")
            session.clear()
            return redirect(url_for('login'))
    
    return decorated_function

def check_purchase_approved(email: str) -> bool:
    """
    Verifica se o usuário tem PURCHASE_APPROVED usando dados da sessão
    Wrapper para manter compatibilidade com código existente
    """
    return session.get('user_status') == 'PURCHASE_APPROVED'

def clear_user_cache(email: str):
    """Limpa o cache de um usuário específico e invalida token de sessão"""
    session_token = session.get('session_token')
    if session_token:
        invalidate_session_token(session_token)
    print(f"[AUTH] Sessão invalidada para {email}")

def clear_all_cache():
    """Limpa todos os tokens de sessão"""
    global _valid_session_tokens
    count = len(_valid_session_tokens)
    _valid_session_tokens.clear()
    print(f"[AUTH] {count} tokens de sessão invalidados")

def get_current_user():
    """Retorna o email do usuário atual se autenticado"""
    # Verifica se a sessão é válida antes de retornar
    session_token = session.get('session_token')
    if session_token and is_session_valid(session_token):
        return session.get('user_email')
    return None

def api_login_required(f):
    """Decorator para APIs - retorna JSON error em vez de redirect
    
    Evita múltiplas tentativas de revalidação quando sessão já foi invalidada
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verifica se a sessão já foi marcada como invalidada
            if session.get('_session_invalidated'):
                return jsonify({
                    'status': 'error',
                    'message': 'Sessão inválida. Faça login novamente.',
                    'code': 'SESSION_INVALIDATED'
                }), 401
            
            # Verifica se há um token de sessão válido
            session_token = session.get('session_token')
            if not session_token or not is_session_valid(session_token):
                return jsonify({
                    'status': 'error',
                    'message': 'Não autenticado',
                    'code': 'NOT_AUTHENTICATED'
                }), 401
            
            # Verifica se há um email e status na sessão
            user_email = session.get('user_email')
            user_status = session.get('user_status')
            
            if not user_email or not user_status:
                return jsonify({
                    'status': 'error',
                    'message': 'Sessão incompleta',
                    'code': 'INCOMPLETE_SESSION'
                }), 401
            
            # Verifica se o status é PURCHASE_APPROVED (sem revalidar - usa cache)
            if user_status != 'PURCHASE_APPROVED':
                return jsonify({
                    'status': 'error',
                    'message': 'Acesso não autorizado',
                    'code': 'NOT_APPROVED'
                }), 403
            
            # Adiciona headers para prevenir cache
            response = make_response(f(*args, **kwargs))
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
            
        except Exception as e:
            print(f"[API AUTH] Erro na verificação: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Erro de autenticação',
                'code': 'AUTH_ERROR'
            }), 500
    
    return decorated_function
