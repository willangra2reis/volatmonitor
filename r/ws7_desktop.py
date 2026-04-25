#!/usr/bin/env python3
"""
MT5 Dashboard - Versão Desktop
Aplicação desktop nativa usando webview para exibir o dashboard MT5
"""

import webview
import threading
import time
import sys
import os

# Configurações para evitar conflitos do webview
os.environ['WEBVIEW_GUI'] = 'cef'  # Força uso do CEF
os.environ['CEF_PYTHON_LOG_SEVERITY'] = '3'  # Reduz logs
os.environ['CEF_PYTHON_LOG_FILE'] = ''  # Desabilita arquivo de log

from ws7 import app  # Importa a aplicação Flask existente

class DesktopApp:
    def __init__(self):
        self.flask_thread = None
        self.server_started = False
        
    def start_flask_server(self):
        """Inicia o servidor Flask em thread separada"""
        try:
            print("🚀 Iniciando servidor Flask...")
            app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor Flask: {e}")
    
    def wait_for_server(self, max_attempts=30):
        """Aguarda o servidor Flask estar pronto"""
        import requests
        
        for attempt in range(max_attempts):
            try:
                response = requests.get('http://127.0.0.1:5000', timeout=1)
                if response.status_code == 200:
                    print("✅ Servidor Flask pronto!")
                    return True
            except:
                pass
            
            print(f"⏳ Aguardando servidor... ({attempt + 1}/{max_attempts})")
            time.sleep(1)
        
        return False
    
    def create_desktop_window(self):
        """Cria a janela desktop"""
        # Configurações da janela
        window_config = {
            'title': 'MT5 Dashboard - Trading Monitor',
            'url': 'http://127.0.0.1:5000',
            'width': 1400,
            'height': 900,
            'min_size': (1200, 800),
            'resizable': True,
            'fullscreen': False,
            'minimized': False,
            'on_top': False,
            'shadow': True,
        }
        
        # Criar janela webview
        window = webview.create_window(**window_config)
        
        # Configurações adicionais do webview
        webview.settings = {
            'ALLOW_DOWNLOADS': False,
            'ALLOW_FILE_URLS': False,
            'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,
            'OPEN_DEVTOOLS_IN_DEBUG': False
        }
        
        # Configurações específicas para Windows
        if sys.platform.startswith('win'):
            webview.settings['USE_QT'] = False
        
        return window
    
    def run(self):
        """Executa a aplicação desktop"""
        print("🖥️  Iniciando MT5 Dashboard Desktop...")
        
        # Inicia Flask em thread separada
        self.flask_thread = threading.Thread(target=self.start_flask_server, daemon=True)
        self.flask_thread.start()
        
        # Aguarda servidor estar pronto
        if not self.wait_for_server():
            print("❌ Falha ao iniciar servidor Flask")
            sys.exit(1)
        
        # Cria janela desktop
        window = self.create_desktop_window()
        
        print("🎯 Abrindo janela desktop...")
        print("📊 Dashboard MT5 pronto para uso!")
        
        # Inicia interface desktop (bloqueia até janela ser fechada)
        try:
            webview.start(debug=False, gui='edgechromium')
        except Exception as e:
            print(f"❌ Erro com EdgeChromium, tentando alternativa: {e}")
            try:
                webview.start(debug=False, gui='mshtml')
            except Exception as e2:
                print(f"❌ Erro com MSHTML: {e2}")
                print("💡 Tentando abrir no navegador padrão...")
                import webbrowser
                webbrowser.open('http://127.0.0.1:5000')
                input("Pressione Enter para encerrar...")
        
        print("👋 Aplicação encerrada")

def main():
    """Função principal"""
    try:
        desktop_app = DesktopApp()
        desktop_app.run()
    except KeyboardInterrupt:
        print("\n⏹️  Aplicação interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
