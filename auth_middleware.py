from functools import wraps
from flask import redirect, url_for, session, request, jsonify, make_response
import secrets
import time
import re

# Armazena tokens de sessão válidos (em memória)
# Formato: {session_token: {"created_at": timestamp, "email": email}}
_valid_session_tokens = {}

# Configurações de sessão
TOKEN_EXPIRATION = 24 * 60 * 60  # 24 horas de inatividade

def is_valid_email(email: str) -> bool:
    """Valida formato básico de email"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

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

def update_token_validation(token, email):
    """Atualiza o timestamp de última validação do token"""
    if token in _valid_session_tokens:
        _valid_session_tokens[token]["last_validated"] = time.time()
        _valid_session_tokens[token]["email"] = email

def login_required(f):
    """Decorator para verificar se o usuário está logado (login local simples)
    
    Usa token de sessão único para segurança local.
    Previne acesso via cache do navegador ou botão voltar.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verifica se há um token de sessão válido
            session_token = session.get('session_token')
            if not session_token or not is_session_valid(session_token):
                session.clear()
                return redirect(url_for('login'))
            
            # Verifica se há um email na sessão
            user_email = session.get('user_email')
            if not user_email:
                session.clear()
                return redirect(url_for('login'))
            
            # Adiciona headers para prevenir cache do navegador
            response = make_response(f(*args, **kwargs))
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
            
        except Exception as e:
            print(f"[AUTH] Erro na verificação: {e}")
            session.clear()
            return redirect(url_for('login'))
    
    return decorated_function

def check_purchase_approved(email: str) -> bool:
    """
    Verifica se o usuário está logado (login local simples)
    Sempre retorna True se houver sessão ativa
    """
    session_token = session.get('session_token')
    return session_token and is_session_valid(session_token) and session.get('user_email') == email

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
    
    Login local simples - verifica apenas se há sessão ativa
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verifica se há um token de sessão válido
            session_token = session.get('session_token')
            if not session_token or not is_session_valid(session_token):
                return jsonify({
                    'status': 'error',
                    'message': 'Não autenticado',
                    'code': 'NOT_AUTHENTICATED'
                }), 401
            
            # Verifica se há um email na sessão
            user_email = session.get('user_email')
            if not user_email:
                return jsonify({
                    'status': 'error',
                    'message': 'Sessão incompleta',
                    'code': 'INCOMPLETE_SESSION'
                }), 401
            
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
