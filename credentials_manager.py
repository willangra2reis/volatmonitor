#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Credenciais Salvas
Salva email do usuário de forma segura para login automático
"""

import os
import json
import base64
from pathlib import Path


class CredentialsManager:
    """Gerencia salvamento e carregamento de credenciais"""
    
    def __init__(self, credentials_folder='user_credentials'):
        """
        Inicializa o gerenciador de credenciais
        
        Args:
            credentials_folder: Pasta onde salvar as credenciais
        """
        self.credentials_folder = credentials_folder
        self.credentials_file = os.path.join(credentials_folder, 'saved_login.dat')
        
        # Cria pasta se não existir
        if not os.path.exists(credentials_folder):
            os.makedirs(credentials_folder)
            print(f"[CREDENTIALS] [INFO] Pasta de credenciais criada: {credentials_folder}")
    
    def _encode(self, text):
        """Codifica texto em base64 (ofuscação simples)"""
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
    
    def _decode(self, encoded_text):
        """Decodifica texto de base64"""
        try:
            return base64.b64decode(encoded_text.encode('utf-8')).decode('utf-8')
        except Exception:
            return None
    
    def save_credentials(self, email, language='pt'):
        """
        Salva email e idioma do usuário
        
        Args:
            email: Email do usuário
            language: Idioma selecionado (pt, en, es, fr, de)
            
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            data = {
                'email': self._encode(email),
                'language': language,
                'remember': True
            }
            
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f)
            
            print(f"[CREDENTIALS] [OK] Credenciais salvas - Email: {email} | Idioma: {language}")
            return True
            
        except Exception as e:
            print(f"[CREDENTIALS] [ERRO] Erro ao salvar credenciais: {e}")
            return False
    
    def load_credentials(self):
        """
        Carrega credenciais salvas
        
        Returns:
            dict: {'email': str, 'language': str, 'remember': bool} ou None se não houver
        """
        try:
            if not os.path.exists(self.credentials_file):
                print("[CREDENTIALS] [INFO] Nenhuma credencial salva encontrada")
                return None
            
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)
            
            # Decodifica email
            email = self._decode(data.get('email', ''))
            
            if not email:
                print("[CREDENTIALS] [AVISO] Credencial corrompida")
                return None
            
            language = data.get('language', 'pt')
            print(f"[CREDENTIALS] [OK] Credencial carregada - Email: {email} | Idioma: {language}")
            
            return {
                'email': email,
                'language': language,
                'remember': data.get('remember', False)
            }
            
        except Exception as e:
            print(f"[CREDENTIALS] [ERRO] Erro ao carregar credenciais: {e}")
            return None
    
    def clear_credentials(self):
        """
        Remove credenciais salvas
        
        Returns:
            bool: True se removeu com sucesso
        """
        try:
            if os.path.exists(self.credentials_file):
                os.remove(self.credentials_file)
                print("[CREDENTIALS] [OK] Credenciais removidas")
                return True
            return False
            
        except Exception as e:
            print(f"[CREDENTIALS] [ERRO] Erro ao remover credenciais: {e}")
            return False
    
    def has_saved_credentials(self):
        """
        Verifica se existem credenciais salvas
        
        Returns:
            bool: True se existem credenciais
        """
        return os.path.exists(self.credentials_file)

    def save_chart_config(self, email, config):
        """
        Salva configuracoes do grafico avancado para um usuario
        
        Args:
            email: Email do usuario
            config: Dicionario com configuracoes do grafico
            
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            config_file = os.path.join(self.credentials_folder, 'chart_configs.json')
            configs = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    configs = json.load(f)
            
            configs[email] = config
            
            with open(config_file, 'w') as f:
                json.dump(configs, f)
            
            print(f"[CREDENTIALS] [OK] Config grafico salva para: {email}")
            return True
        except Exception as e:
            print(f"[CREDENTIALS] [ERRO] Erro ao salvar config grafico: {e}")
            return False

    def load_chart_config(self, email):
        """
        Carrega configuracoes do grafico avancado para um usuario
        
        Args:
            email: Email do usuario
            
        Returns:
            dict: Configuracoes do grafico ou None
        """
        try:
            config_file = os.path.join(self.credentials_folder, 'chart_configs.json')
            if not os.path.exists(config_file):
                return None
            
            with open(config_file, 'r') as f:
                configs = json.load(f)
            
            return configs.get(email, None)
        except Exception as e:
            print(f"[CREDENTIALS] [ERRO] Erro ao carregar config grafico: {e}")
            return None


# Instância global
credentials_manager = CredentialsManager()


# Funções de conveniência
def save_user_credentials(email, language='pt'):
    """
    Salva email e idioma do usuário
    
    Args:
        email: Email do usuário
        language: Idioma selecionado (pt, en, es, fr, de)
    """
    return credentials_manager.save_credentials(email, language)


def get_saved_credentials():
    """
    Retorna credenciais salvas
    
    Returns:
        dict: {'email': str, 'language': str, 'remember': bool} ou None
    """
    return credentials_manager.load_credentials()


def get_saved_email():
    """Retorna email salvo ou None"""
    creds = credentials_manager.load_credentials()
    return creds['email'] if creds else None


def get_saved_language():
    """Retorna idioma salvo ou 'pt' como padrão"""
    creds = credentials_manager.load_credentials()
    return creds['language'] if creds else 'pt'


def clear_saved_credentials():
    """Remove credenciais salvas"""
    return credentials_manager.clear_credentials()


def has_saved_login():
    """Verifica se há login salvo"""
    return credentials_manager.has_saved_credentials()


# Funções para configurações do gráfico avançado
def save_user_chart_config(email, config):
    """
    Salva configurações do gráfico avançado para um usuário
    
    Args:
        email: Email do usuário
        config: Dicionário com configurações
    """
    return credentials_manager.save_chart_config(email, config)

def get_user_chart_config(email):
    """
    Carrega configurações do gráfico avançado para um usuário
    
    Args:
        email: Email do usuário
        
    Returns:
        dict: Configurações salvas ou None
    """
    return credentials_manager.load_chart_config(email)


# Manter compatibilidade com código antigo
save_user_email = save_user_credentials
clear_saved_email = clear_saved_credentials


# Teste
if __name__ == "__main__":
    print("\n=== Teste do Gerenciador de Credenciais ===\n")
    
    # Teste 1: Salvar
    print("1. Salvando email...")
    save_user_email("teste@email.com")
    
    # Teste 2: Carregar
    print("\n2. Carregando email...")
    email = get_saved_email()
    print(f"   Email carregado: {email}")
    
    # Teste 3: Verificar
    print("\n3. Verificando se existe...")
    print(f"   Existe: {has_saved_login()}")
    
    # Teste 4: Limpar
    print("\n4. Limpando...")
    clear_saved_email()
    
    # Teste 5: Verificar novamente
    print("\n5. Verificando após limpar...")
    print(f"   Existe: {has_saved_login()}")
    
    print("\n[OK] Testes concluidos!")
