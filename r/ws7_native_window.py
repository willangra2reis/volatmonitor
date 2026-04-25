#!/usr/bin/env python3
"""
MT5 Dashboard - Janela Nativa
Aplicação desktop com janela própria usando tkinter e HTML widget embutido
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
import os
from urllib.request import urlopen
import json

# Tentar importar tkinterweb, se não conseguir, usar alternativa
try:
    from tkinterweb import HtmlFrame
    HAS_TKINTERWEB = True
except ImportError:
    HAS_TKINTERWEB = False
    print("⚠️  tkinterweb não encontrado. Usando interface alternativa...")

from ws7 import app

class NativeWindowApp:
    def __init__(self):
        self.flask_thread = None
        self.root = None
        self.html_frame = None
        self.update_thread = None
        self.running = True
        
    def start_flask_server(self):
        """Inicia o servidor Flask em thread separada"""
        try:
            print("🚀 Iniciando servidor Flask...")
            app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor Flask: {e}")
    
    def wait_for_server(self, max_attempts=30):
        """Aguarda o servidor Flask estar pronto"""
        for attempt in range(max_attempts):
            try:
                response = urlopen('http://127.0.0.1:5001', timeout=1)
                if response.getcode() == 200:
                    print("✅ Servidor Flask pronto!")
                    return True
            except:
                pass
            
            print(f"⏳ Aguardando servidor... ({attempt + 1}/{max_attempts})")
            time.sleep(1)
        
        return False
    
    def create_native_window(self):
        """Cria janela nativa com HTML embutido"""
        self.root = tk.Tk()
        self.root.title("MT5 Dashboard - Trading Monitor")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Centralizar janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")
        
        # Configurar ícone (se existir)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        if HAS_TKINTERWEB:
            self.create_html_interface()
        else:
            self.create_fallback_interface()
        
        # Protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_html_interface(self):
        """Cria interface usando HTML widget"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de ferramentas
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Botões da barra de ferramentas
        refresh_btn = ttk.Button(toolbar, text="🔄 Atualizar", command=self.refresh_dashboard)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        fullscreen_btn = ttk.Button(toolbar, text="⛶ Tela Cheia", command=self.toggle_fullscreen)
        fullscreen_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status
        self.status_label = ttk.Label(toolbar, text="🟢 Conectado", foreground="green")
        self.status_label.pack(side=tk.RIGHT)
        
        # Widget HTML
        self.html_frame = HtmlFrame(main_frame)
        self.html_frame.pack(fill=tk.BOTH, expand=True)
        
        # Carregar dashboard
        self.load_dashboard()
        
        # Iniciar atualização automática
        self.start_auto_refresh()
        
    def create_fallback_interface(self):
        """Interface alternativa sem tkinterweb"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="MT5 Dashboard", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(pady=(0, 30))
        
        # Informações
        info_frame = ttk.LabelFrame(main_frame, text="Informações do Sistema", padding="15")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.balance_label = ttk.Label(info_frame, text="Saldo: Carregando...", font=('Arial', 12))
        self.balance_label.pack(anchor=tk.W, pady=2)
        
        self.equity_label = ttk.Label(info_frame, text="Equity: Carregando...", font=('Arial', 12))
        self.equity_label.pack(anchor=tk.W, pady=2)
        
        self.profit_label = ttk.Label(info_frame, text="Lucro do Dia: Carregando...", font=('Arial', 12))
        self.profit_label.pack(anchor=tk.W, pady=2)
        
        self.trades_label = ttk.Label(info_frame, text="Trades Hoje: Carregando...", font=('Arial', 12))
        self.trades_label.pack(anchor=tk.W, pady=2)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        open_browser_btn = ttk.Button(btn_frame, text="🌐 Abrir no Navegador", 
                                     command=self.open_in_browser, width=25)
        open_browser_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = ttk.Button(btn_frame, text="🔄 Atualizar Dados", 
                                command=self.refresh_data, width=25)
        refresh_btn.pack(side=tk.LEFT)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="🟢 Sistema Ativo", 
                                     font=('Arial', 10), foreground="green")
        self.status_label.pack(pady=(20, 0))
        
        # Iniciar atualização de dados
        self.start_data_updates()
        
    def load_dashboard(self):
        """Carrega o dashboard no widget HTML"""
        if self.html_frame:
            self.html_frame.load_url("http://127.0.0.1:5001")
            
    def refresh_dashboard(self):
        """Atualiza o dashboard"""
        if self.html_frame:
            self.html_frame.load_url("http://127.0.0.1:5001")
        else:
            self.refresh_data()
            
    def toggle_fullscreen(self):
        """Alterna tela cheia"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        
    def open_in_browser(self):
        """Abre dashboard no navegador"""
        import webbrowser
        webbrowser.open('http://127.0.0.1:5001')
        
    def start_auto_refresh(self):
        """Inicia atualização automática do HTML"""
        def auto_refresh():
            while self.running:
                time.sleep(30)  # Atualiza a cada 30 segundos
                if self.running and self.html_frame:
                    try:
                        self.root.after(0, self.refresh_dashboard)
                    except:
                        break
                        
        self.update_thread = threading.Thread(target=auto_refresh, daemon=True)
        self.update_thread.start()
        
    def start_data_updates(self):
        """Inicia atualização de dados para interface alternativa"""
        def update_data():
            while self.running:
                try:
                    response = urlopen('http://127.0.0.1:5001/api/latest', timeout=5)
                    data = json.loads(response.read().decode())
                    
                    self.root.after(0, lambda: self.update_labels(data))
                except Exception as e:
                    self.root.after(0, lambda: self.update_status(f"❌ Erro: {str(e)[:50]}"))
                
                time.sleep(5)  # Atualiza a cada 5 segundos
                
        self.update_thread = threading.Thread(target=update_data, daemon=True)
        self.update_thread.start()
        
    def update_labels(self, data):
        """Atualiza labels com dados da API"""
        try:
            account_info = data.get('account_info', {})
            
            balance = account_info.get('account_balance', 0)
            equity = account_info.get('account_equity', 0)
            profit = account_info.get('account_profit', 0)
            
            self.balance_label.config(text=f"Saldo: ${balance:,.2f}")
            self.equity_label.config(text=f"Equity: ${equity:,.2f}")
            
            profit_color = "green" if profit >= 0 else "red"
            profit_text = f"Lucro do Dia: ${profit:+,.2f}"
            self.profit_label.config(text=profit_text, foreground=profit_color)
            
            # Contar trades de hoje
            trades_today = len([t for t in data.get('last_trades', []) 
                              if self.is_today(t.get('time', ''))])
            self.trades_label.config(text=f"Trades Hoje: {trades_today}")
            
            self.status_label.config(text="🟢 Sistema Ativo", foreground="green")
            
        except Exception as e:
            self.status_label.config(text=f"❌ Erro nos dados: {str(e)[:30]}", foreground="red")
            
    def is_today(self, time_str):
        """Verifica se a data é hoje"""
        try:
            from datetime import datetime
            trade_date = datetime.strptime(time_str.split()[0], '%Y-%m-%d')
            today = datetime.now().date()
            return trade_date.date() == today
        except:
            return False
            
    def update_status(self, message):
        """Atualiza status"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message, foreground="red")
            
    def refresh_data(self):
        """Força atualização dos dados"""
        self.update_status("🔄 Atualizando...")
        
    def on_closing(self):
        """Chamado quando a janela é fechada"""
        print("👋 Encerrando aplicação...")
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1)
        self.root.quit()
        sys.exit(0)
    
    def run(self):
        """Executa a aplicação desktop"""
        print("🖥️  Iniciando MT5 Dashboard - Janela Nativa...")
        
        # Inicia Flask em thread separada
        self.flask_thread = threading.Thread(target=self.start_flask_server, daemon=True)
        self.flask_thread.start()
        
        # Aguarda servidor estar pronto
        if not self.wait_for_server():
            print("❌ Falha ao iniciar servidor Flask")
            sys.exit(1)
        
        # Cria janela nativa
        self.create_native_window()
        
        print("🎯 Janela nativa criada")
        print("📊 Dashboard MT5 pronto para uso!")
        
        # Inicia loop da interface
        self.root.mainloop()

def main():
    """Função principal"""
    try:
        desktop_app = NativeWindowApp()
        desktop_app.run()
    except KeyboardInterrupt:
        print("\n⏹️  Aplicação interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
