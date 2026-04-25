#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de autenticação via Google Apps Script API
Substitui o Supabase para verificação de status PURCHASE_APPROVED
"""

import requests
import time
from typing import Dict, Tuple, Optional

# URL da API do Google Apps Script
GOOGLE_API_URL = "https://script.google.com/macros/s/AKfycbzcSabZea0UrFCGGT-1cayCOrPQwTcqN89fRmgUH96mCzxc1RlO86K81aPmLtZmcgHT/exec"

# Cache para verificações de usuário
# Formato: {email: (user_data, timestamp)}
_user_cache: Dict[str, Tuple[dict, float]] = {}
CACHE_DURATION = 30  # Cache válido por 30 segundos


def check_user_status(email: str) -> Optional[dict]:
    """
    Verifica o status do usuário na API do Google Apps Script
    
    Args:
        email: Email do usuário
        
    Returns:
        dict com dados do usuário se encontrado, None caso contrário
        Formato: {
            "email": str,
            "pnome": str,
            "nomecompleto": str,
            "status": str,
            "data": str
        }
    """
    current_time = time.time()
    
    # Verifica se existe cache válido
    if email in _user_cache:
        user_data, cached_time = _user_cache[email]
        if current_time - cached_time < CACHE_DURATION:
            print(f"[GOOGLE AUTH CACHE] User {email} -> cache hit (válido por {CACHE_DURATION}s)")
            return user_data
    
    # Cache expirado ou não existe, consulta a API
    try:
        print(f"[GOOGLE AUTH] Consultando API para {email}...")
        response = requests.get(
            GOOGLE_API_URL,
            params={"email": email},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success") and data.get("data"):
                user_data = data["data"]
                
                # Atualiza o cache
                _user_cache[email] = (user_data, current_time)
                
                status = user_data.get("status", "UNKNOWN")
                print(f"[GOOGLE AUTH] User {email} -> {status} (cached for {CACHE_DURATION}s)")
                
                return user_data
            else:
                print(f"[GOOGLE AUTH] User {email} -> não encontrado")
                return None
        else:
            print(f"[GOOGLE AUTH] Erro HTTP {response.status_code} ao consultar API")
            return None
            
    except requests.exceptions.Timeout:
        print(f"[GOOGLE AUTH] Timeout ao consultar API para {email}")
        return None
    except Exception as e:
        print(f"[GOOGLE AUTH] Erro ao verificar usuário: {e}")
        return None


def is_purchase_approved(email: str) -> bool:
    """
    Verifica se o usuário tem status PURCHASE_APPROVED
    
    Args:
        email: Email do usuário
        
    Returns:
        True se aprovado, False caso contrário
    """
    user_data = check_user_status(email)
    
    if user_data:
        return user_data.get("status") == "PURCHASE_APPROVED"
    
    return False


def get_user_first_name(email: str) -> Optional[str]:
    """
    Retorna o primeiro nome do usuário
    
    Args:
        email: Email do usuário
        
    Returns:
        Primeiro nome do usuário ou None
    """
    user_data = check_user_status(email)
    
    if user_data:
        return user_data.get("pnome")
    
    return None


def clear_user_cache(email: str):
    """Limpa o cache de um usuário específico"""
    if email in _user_cache:
        del _user_cache[email]
        print(f"[GOOGLE AUTH CACHE] Cache limpo para {email}")


def clear_all_cache():
    """Limpa todo o cache"""
    global _user_cache
    _user_cache.clear()
    print("[GOOGLE AUTH CACHE] Todo cache limpo")


# Função para teste
if __name__ == "__main__":
    # Teste com o email fornecido
    test_email = "jocelio_garcia@hotmail.com"
    print(f"\n=== Testando autenticação Google para {test_email} ===\n")
    
    user_data = check_user_status(test_email)
    if user_data:
        print(f"\n✅ Usuário encontrado:")
        print(f"   Email: {user_data.get('email')}")
        print(f"   Nome: {user_data.get('nomecompleto')}")
        print(f"   Primeiro Nome: {user_data.get('pnome')}")
        print(f"   Status: {user_data.get('status')}")
        print(f"   Aprovado: {'SIM' if is_purchase_approved(test_email) else 'NÃO'}")
    else:
        print(f"\n❌ Usuário não encontrado")
