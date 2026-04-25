#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VolatForex Monitor Pro - Launcher com Janela Nativa
Usa WebView2 para criar interface standalone sem navegador externo
"""

import webview
import threading
import time
import sys
import os
import json
from waitress import serve
from ws7 import app

# ==================== CONFIGURAÇÃO DE PERSISTÊNCIA ====================
# Define pasta para dados do WebView2 ANTES de importar qualquer coisa
# Isso garante que localStorage, cookies e cache sejam salvos
WEBVIEW_DATA_FOLDER = os.path.join(os.getcwd(), 'webview_data')

# Cria pasta se não existir
if not os.path.exists(WEBVIEW_DATA_FOLDER):
    os.makedirs(WEBVIEW_DATA_FOLDER)
    print(f"[INIT] 📁 Pasta de dados criada: {WEBVIEW_DATA_FOLDER}")

# Define variável de ambiente para WebView2 usar esta pasta
os.environ['PYWEBVIEW_USERDATA'] = WEBVIEW_DATA_FOLDER
print(f"[INIT] 📁 Pasta de dados configurada: {WEBVIEW_DATA_FOLDER}")

class WindowConfig:
    """Configurações de janela e resolução"""
    
    # Resoluções pré-definidas
    RESOLUTIONS = {
        'hd': (1366, 768),
        'fhd': (1920, 1080),
        'qhd': (2560, 1440),
        '4k': (3840, 2160),
        'auto': None  # Detecta resolução do monitor
    }
    
    def __init__(self):
        # Configuração padrão
        self.width = 1400
        self.height = 900
        self.fullscreen = False
        self.resizable = True
        self.frameless = False  # Sem bordas Windows
        self.on_top = False
        self.minimized = False
        self.maximized = False
        self.x = None  # Posição X (None = centralizado)
        self.y = None  # Posição Y (None = centralizado)
        
    def set_resolution(self, preset='auto', percentage=85):
        """
        Define resolução baseada em preset ou percentual da tela
        
        Args:
            preset: 'hd', 'fhd', 'qhd', '4k', 'auto'
            percentage: % da tela (se preset='auto')
        """
        if preset == 'auto':
            # Detecta resolução do monitor e usa percentual
            try:
                import ctypes
                user32 = ctypes.windll.user32
                screen_width = user32.GetSystemMetrics(0)
                screen_height = user32.GetSystemMetrics(1)
                
                self.width = int(screen_width * percentage / 100)
                self.height = int(screen_height * percentage / 100)
                
                print(f"📐 Monitor detectado: {screen_width}x{screen_height}")
                print(f"📐 Janela configurada: {self.width}x{self.height} ({percentage}%)")
            except Exception as e:
                print(f"⚠️ Erro ao detectar resolução: {e}")
                print(f"📐 Usando resolução padrão: 1400x900")
                self.width = 1400
                self.height = 900
        else:
            resolution = self.RESOLUTIONS.get(preset, (1400, 900))
            self.width, self.height = resolution
            print(f"📐 Resolução preset '{preset}': {self.width}x{self.height}")
    
    def set_custom(self, width, height):
        """Define tamanho customizado"""
        self.width = width
        self.height = height
        print(f"📐 Resolução customizada: {self.width}x{self.height}")
    
    def load_saved_config(self):
        """Carrega configuração salva anteriormente"""
        config_file = 'window_config.json'
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    saved = json.load(f)
                    self.width = saved.get('width', self.width)
                    self.height = saved.get('height', self.height)
                    self.x = saved.get('x')
                    self.y = saved.get('y')
                    print(f"✅ Configuração carregada: {self.width}x{self.height}")
                    if self.x and self.y:
                        print(f"✅ Posição carregada: ({self.x}, {self.y})")
                    return True
        except Exception as e:
            print(f"⚠️ Erro ao carregar configuração: {e}")
        return False
    
    def save_config(self, window):
        """Salva configuração atual da janela"""
        config_file = 'window_config.json'
        try:
            # Obtém tamanho e posição atual
            config = {
                'width': window.width,
                'height': window.height,
                'x': window.x,
                'y': window.y
            }
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"💾 Configuração salva: {config['width']}x{config['height']}")
        except Exception as e:
            print(f"⚠️ Erro ao salvar configuração: {e}")


class FlaskServer:
    """Gerenciador do servidor Flask"""
    
    def __init__(self):
        self.server_thread = None
        self.is_running = False
    
    def start(self):
        """Inicia servidor Flask em thread separada"""
        print("🚀 Iniciando servidor Flask...")
        
        def run_server():
            try:
                serve(app, 
                      host='127.0.0.1', 
                      port=5000,
                      threads=8,
                      connection_limit=1000,
                      cleanup_interval=30,
                      channel_timeout=120,
                      max_request_body_size=1048576,
                      send_bytes=18000,
                      asyncore_use_poll=True)
            except Exception as e:
                print(f"❌ Erro no servidor Flask: {e}")
                self.is_running = False
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True
        
        # Aguarda servidor iniciar
        print("⏳ Aguardando servidor Flask iniciar...")
        time.sleep(2)
        
        # Testa conexão
        if self.test_connection():
            print("✅ Servidor Flask pronto!")
            return True
        else:
            print("❌ Falha ao conectar ao servidor Flask")
            return False
    
    def test_connection(self, max_attempts=5):
        """Testa se servidor está respondendo"""
        import requests
        
        for attempt in range(max_attempts):
            try:
                response = requests.get('http://127.0.0.1:5000', timeout=2)
                if response.status_code in [200, 302, 401, 403]:  # Qualquer resposta válida
                    return True
            except requests.exceptions.RequestException:
                if attempt < max_attempts - 1:
                    print(f"⏳ Tentativa {attempt + 1}/{max_attempts}...")
                    time.sleep(1)
        
        return False


class WindowAPI:
    """API Python exposta para JavaScript"""
    
    def __init__(self, window, config):
        self.window = window
        self.config = config
    
    def minimize_window(self):
        """Minimiza a janela"""
        self.window.minimize()
    
    def maximize_window(self):
        """Maximiza a janela"""
        self.window.maximize()
    
    def restore_window(self):
        """Restaura tamanho normal"""
        self.window.restore()
    
    def toggle_fullscreen(self):
        """Alterna fullscreen"""
        self.window.toggle_fullscreen()
    
    def get_window_size(self):
        """Retorna tamanho atual da janela"""
        return {
            'width': self.window.width,
            'height': self.window.height
        }
    
    def get_screen_size(self):
        """Retorna tamanho da tela"""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            return {
                'width': user32.GetSystemMetrics(0),
                'height': user32.GetSystemMetrics(1)
            }
        except:
            return {'width': 1920, 'height': 1080}


def create_window(config, api):
    """Cria janela WebView2 com configurações"""
    
    window = webview.create_window(
        title='VolatForex Monitor Pro',
        url='http://127.0.0.1:5000',
        width=config.width,
        height=config.height,
        x=config.x,
        y=config.y,
        resizable=config.resizable,
        fullscreen=config.fullscreen,
        frameless=config.frameless,
        on_top=config.on_top,
        minimized=config.minimized,
        confirm_close=True,  # Confirma antes de fechar
        background_color='#1a1a1a',  # Cor de fundo durante carregamento
        js_api=api,  # Expõe API Python para JavaScript
    )
    
    return window


def main():
    """Função principal"""
    print("\n" + "="*70)
    print("🎯 VolatForex Monitor Pro - Versão Standalone")
    print("="*70 + "\n")
    
    # ==================== CONFIGURAÇÃO DE JANELA ====================
    config = WindowConfig()
    
    # Tenta carregar configuração salva
    if not config.load_saved_config():
        # Se não houver configuração salva, usa padrão
        # OPÇÃO 1: Resolução automática (85% da tela) - RECOMENDADO
        config.set_resolution('auto', percentage=85)
        
        # OPÇÃO 2: Preset específico
        # config.set_resolution('fhd')  # 1920x1080
        
        # OPÇÃO 3: Tamanho customizado
        # config.set_custom(1600, 1000)
    
    # Outras opções de janela
    # config.fullscreen = True  # Iniciar em fullscreen
    # config.maximized = True   # Iniciar maximizado
    # config.frameless = True   # Janela sem bordas (estilo moderno)
    # config.on_top = True      # Sempre no topo
    
    print(f"🪟 Configurações da janela:")
    print(f"   - Tamanho: {config.width}x{config.height}")
    print(f"   - Fullscreen: {config.fullscreen}")
    print(f"   - Redimensionável: {config.resizable}")
    print(f"   - Sem bordas: {config.frameless}")
    print()
    
    # ==================== INICIAR SERVIDOR FLASK ====================
    server = FlaskServer()
    if not server.start():
        print("\n❌ Falha ao iniciar servidor. Encerrando...")
        sys.exit(1)
    
    # ==================== CRIAR JANELA ====================
    print("🪟 Criando janela nativa...")
    
    # Cria API para JavaScript
    api = WindowAPI(None, config)  # window será definido depois
    
    # Cria janela
    window = create_window(config, api)
    api.window = window  # Atualiza referência
    
    # ==================== EVENTOS DA JANELA ====================
    def on_closing():
        """Chamado quando usuário tenta fechar a janela"""
        print("\n💾 Salvando configurações...")
        config.save_config(window)
        print("👋 Encerrando aplicação...")
        return True  # Permite fechar
    
    def on_shown():
        """Chamado quando janela é exibida"""
        print("✅ Janela exibida com sucesso!")
    
    def on_loaded():
        """Chamado quando página é carregada"""
        print("✅ Dashboard carregado!")
    
    # Registra eventos
    window.events.closing += on_closing
    window.events.shown += on_shown
    window.events.loaded += on_loaded
    
    # ==================== INICIAR APLICAÇÃO ====================
    print("🚀 Iniciando aplicação...\n")
    print(f"💾 LocalStorage será salvo em: {WEBVIEW_DATA_FOLDER}\n")
    
    try:
        webview.start(
            debug=False,  # True para debug (abre DevTools)
            http_server=False,  # Flask já está rodando
        )
    except KeyboardInterrupt:
        print("\n⚠️ Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro na aplicação: {e}")
    finally:
        print("\n✅ Aplicação encerrada com sucesso")


if __name__ == '__main__':
    main()
