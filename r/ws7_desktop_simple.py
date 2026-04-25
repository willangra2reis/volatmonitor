#!/usr/bin/env python3
"""
MT5 Dashboard - Versão Desktop Simplificada
Usando tkinter com webview embutido para máxima compatibilidade
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import webbrowser
import sys
import os
from ws7 import app

class SimpleDesktopApp:
    def __init__(self):
        self.flask_thread = None
        self.root = None
        
    def start_flask_server(self):
        """Inicia o servidor Flask em thread separada"""
        try:
            print("🚀 Iniciando servidor Flask...")
            app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor Flask: {e}")
    
    def wait_for_server(self, max_attempts=30):
        """Aguarda o servidor Flask estar pronto"""
        import requests
        
        for attempt in range(max_attempts):
            try:
                response = requests.get('http://127.0.0.1:5001', timeout=1)
                if response.status_code == 200:
                    print("✅ Servidor Flask pronto!")
                    return True
            except:
                pass
            
            print(f"⏳ Aguardando servidor... ({attempt + 1}/{max_attempts})")
            time.sleep(1)
        
        return False
    
    def open_dashboard(self):
        """Abre o dashboard no navegador padrão"""
        webbrowser.open('http://127.0.0.1:5001')
        print("🌐 Dashboard aberto no navegador")
    
    def create_control_window(self):
        """Cria janela de controle simples"""
        self.root = tk.Tk()
        self.root.title("MT5 Dashboard - Controle")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Centralizar janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"400x300+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="MT5 Dashboard", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="🟢 Servidor Ativo", 
                                     font=('Arial', 10))
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # URL
        url_label = ttk.Label(main_frame, text="URL: http://127.0.0.1:5001", 
                             font=('Arial', 9))
        url_label.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        open_btn = ttk.Button(btn_frame, text="🌐 Abrir Dashboard", 
                             command=self.open_dashboard, width=20)
        open_btn.grid(row=0, column=0, padx=5)
        
        refresh_btn = ttk.Button(btn_frame, text="🔄 Atualizar", 
                                command=self.refresh_dashboard, width=20)
        refresh_btn.grid(row=0, column=1, padx=5)
        
        # Informações
        info_text = tk.Text(main_frame, height=8, width=45, wrap=tk.WORD)
        info_text.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        info_content = """📊 MT5 Dashboard Desktop

✅ Servidor Flask ativo na porta 500
🔗 Acesse via navegador ou clique em "Abrir Dashboard"
📈 Dashboard atualiza automaticamente os dados
⚙️ Configure a frequência de atualização no dashboard

💡 Dica: Mantenha esta janela aberta para controlar o servidor"""
        
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)
        
        # Scrollbar para o texto
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=info_text.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        info_text.config(yscrollcommand=scrollbar.set)
        
        # Protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def refresh_dashboard(self):
        """Atualiza o dashboard"""
        self.open_dashboard()
        
    def on_closing(self):
        """Chamado quando a janela é fechada"""
        print("👋 Encerrando aplicação...")
        self.root.quit()
        sys.exit(0)
    
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
        
        # Cria janela de controle
        self.create_control_window()
        
        print("🎯 Janela de controle criada")
        print("📊 Dashboard MT5 pronto para uso!")
        
        # Abre dashboard automaticamente
        self.open_dashboard()
        
        # Inicia loop da interface
        self.root.mainloop()

def main():
    """Função principal"""
    try:
        desktop_app = SimpleDesktopApp()
        desktop_app.run()
    except KeyboardInterrupt:
        print("\n⏹️  Aplicação interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
