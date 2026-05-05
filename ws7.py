#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Webhook Local para receber dados do EA MetaTrader 5
Salva os dados e serve uma página web para visualização
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session, render_template, make_response
from flask_cors import CORS
from waitress import serve
import json
import datetime
import threading
import webbrowser
from collections import deque
import os

# Importações para autenticação via Google Apps Script
from auth_middleware import login_required, api_login_required, check_purchase_approved, clear_user_cache, get_current_user, generate_session_token, _valid_session_tokens
from google_auth import check_user_status, get_user_first_name, get_user_messages, get_user_notifications

# Importação do Gerenciador de Credenciais
from credentials_manager import save_user_credentials, get_saved_credentials, get_saved_email, get_saved_language, clear_saved_credentials, has_saved_login

# Importação do Symbol Mapper
from symbol_mapper import SymbolMapper

# Importação dos Indicadores Técnicos
from technical_indicators import TechnicalIndicators, IndicatorHistory

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')
CORS(app)

# --- Armazenamento de Dados em Memória ---
# Usamos deque para manter um número fixo de registros, descartando os mais antigos.
latest_data = {}
trade_history = deque(maxlen=200)
balance_history = deque(maxlen=100)

# --- Sistema de Mapeamento de Símbolos ---
symbol_mapper = SymbolMapper('symbol_mapping.json')

# --- Histórico de Preços por Símbolo (Tick-by-Tick) ---
# Estrutura: {'XAUUSD': deque([{'timestamp': ..., 'price': ..., 'bid': ..., 'ask': ...}]), ...}
price_history = {}

# --- Histórico de Indicadores Técnicos por Símbolo ---
indicator_history = {}

def init_price_history(symbol):
    """Inicializa histórico de preços para um símbolo"""
    if symbol not in price_history:
        price_history[symbol] = deque(maxlen=500)
        print(f"[PRICE HISTORY] 📊 Inicializado histórico para {symbol}")

def init_indicator_history(symbol):
    """Inicializa histórico de indicadores para um símbolo"""
    if symbol not in indicator_history:
        indicator_history[symbol] = IndicatorHistory(symbol, max_length=500)
        print(f"[INDICATORS] 📈 Inicializado histórico de indicadores para {symbol}")

def add_price_point(symbol, price, bid, ask, timestamp):
    """Adiciona ponto de preço ao histórico e calcula indicadores"""
    init_price_history(symbol)
    init_indicator_history(symbol)
    
    price_point = {
        'timestamp': timestamp,
        'price': price,
        'bid': bid,
        'ask': ask
    }
    
    price_history[symbol].append(price_point)
    
    # Calcular indicadores se houver dados suficientes
    if len(price_history[symbol]) >= 20:
        # Extrair apenas os preços para cálculo
        prices = [p['price'] for p in price_history[symbol]]
        
        # Calcular e armazenar indicadores
        indicator_history[symbol].add_indicators(
            timestamp=timestamp,
            prices=prices,
            hull_period=20,
            sma_period=20,
            ema_period=20,
            zscore_window=20,
            rsi_period=14,
            bb_period=20
        )
    
    # print(f"[PRICE HISTORY] ✅ {symbol}: {price} @ {timestamp}")  # Log detalhado (comentado para não poluir)

# Template HTML para a página de visualização
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitor MT5 - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
            min-height: 100vh;
            transition: all 0.3s ease;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Modo Escuro */
        body.dark-mode {
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
        }
        
        /* Efeito de nuvens animadas */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 200%;
            height: 200%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(40, 167, 69, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(40, 167, 69, 0.2) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(40, 167, 69, 0.1) 0%, transparent 50%);
            animation: floating-clouds 20s ease-in-out infinite;
            z-index: -1;
            pointer-events: none;
        }
        
        body.dark-mode::before {
            background: 
                radial-gradient(circle at 20% 80%, rgba(40, 167, 69, 0.4) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(40, 167, 69, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(40, 167, 69, 0.2) 0%, transparent 50%);
        }
        
        @keyframes floating-clouds {
            0%, 100% {
                transform: translateX(-10%) translateY(-10%) rotate(0deg);
            }
            33% {
                transform: translateX(-5%) translateY(-15%) rotate(1deg);
            }
            66% {
                transform: translateX(-15%) translateY(-5%) rotate(-1deg);
            }
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .dark-mode .container {
            background: rgba(20, 20, 20, 0.95);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }
        
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
            position: relative;
        }
        
        .dark-mode .header {
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        }
        
        .theme-toggle {
            position: absolute;
            top: 20px;
            right: 260px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            z-index: 1000;
        }
        
        .theme-toggle:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.05);
        }
        
        .language-toggle {
            position: absolute;
            top: 20px;
            right: 200px;
            background: rgba(79, 195, 247, 0.1);
            border: 1px solid rgba(79, 195, 247, 0.2);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            z-index: 1000;
            color: #4fc3f7;
        }
        
        .language-toggle:hover {
            background: rgba(79, 195, 247, 0.2);
            transform: scale(1.05);
        }
        
        .chart-toggle {
            position: absolute;
            top: 20px;
            right: 140px;
            background: rgba(76, 175, 80, 0.1);
            border: 1px solid rgba(76, 175, 80, 0.2);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            z-index: 1000;
            color: #4caf50;
        }
        
        .chart-toggle:hover {
            background: rgba(76, 175, 80, 0.2);
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(76, 175, 80, 0.4);
        }
        
        .logout-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(220, 53, 69, 0.2);
            border: 1px solid rgba(220, 53, 69, 0.3);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            z-index: 1000;
            color: #dc3545;
        }
        
        .logout-btn:hover {
            background: rgba(220, 53, 69, 0.3);
            transform: scale(1.05);
            color: white;
        }
        
        /* Botão de Notificação */
        .notification-btn {
            position: absolute;
            top: 20px;
            right: 80px;
            background: rgba(255, 193, 7, 0.2);
            border: 1px solid rgba(255, 193, 7, 0.3);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            z-index: 1000;
            color: #ffc107;
        }
        
        .notification-btn:hover {
            background: rgba(255, 193, 7, 0.3);
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 193, 7, 0.5);
        }
        
        .notification-btn i {
            animation: bellRing 2s ease-in-out infinite;
        }
        
        @keyframes bellRing {
            0%, 100% {
                transform: rotate(0deg);
            }
            10%, 30% {
                transform: rotate(-15deg);
            }
            20%, 40% {
                transform: rotate(15deg);
            }
            50% {
                transform: rotate(0deg);
            }
        }
        
        .notification-badge {
            position: absolute;
            top: 8px;
            right: 8px;
            width: 12px;
            height: 12px;
            background: #ff4444;
            border-radius: 50%;
            border: 2px solid rgba(20, 20, 20, 0.95);
            animation: pulseBadge 1.5s ease-in-out infinite;
        }
        
        @keyframes pulseBadge {
            0%, 100% {
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.2);
                opacity: 0.8;
            }
        }
        
        .header h1 {
            font-family: 'Orbitron', 'Exo 2', 'Rajdhani', sans-serif;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-weight: 700;
            letter-spacing: 2px;
        }
        
        .header h1 .pro-text {
            font-size: 0.6em;
            color: #FFD700;
            font-weight: 400;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
            margin-left: 8px;
        }
        
        /* Mensagem Personalizada */
        .custom-message {
            margin-top: 15px;
            padding: 10px 18px;
            background: linear-gradient(135deg, rgba(79, 195, 247, 0.2) 0%, rgba(79, 195, 247, 0.1) 100%);
            border: 1px solid rgba(79, 195, 247, 0.3);
            border-radius: 10px;
            color: #ffffff;
            font-size: 1.05em;
            font-weight: 500;
            text-align: center;
            animation: fadeInMessage 0.5s ease-in-out;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(79, 195, 247, 0.2);
            display: inline-block;
            max-width: fit-content;
            margin-left: auto;
            margin-right: auto;
        }
        
        .dark-mode .custom-message {
            background: linear-gradient(135deg, rgba(79, 195, 247, 0.15) 0%, rgba(79, 195, 247, 0.05) 100%);
            border-color: rgba(79, 195, 247, 0.4);
            color: #ffffff;
        }
        
        @keyframes fadeInMessage {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .status {
            display: inline-flex;
            align-items: center;
            padding: 6px 12px;
            border-radius: 15px;
            background: rgba(40, 167, 69, 0.3);
            font-weight: bold;
            font-size: 0.85em;
            animation: pulse-glow 2s ease-in-out infinite;
            border: 1px solid rgba(40, 167, 69, 0.5);
        }
        
        .status-icon {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #28a745;
            margin-right: 6px;
            animation: pulse-dot 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse-glow {
            0%, 100% {
                box-shadow: 0 0 5px rgba(40, 167, 69, 0.3);
            }
            50% {
                box-shadow: 0 0 15px rgba(40, 167, 69, 0.6);
            }
        }
        
        @keyframes pulse-dot {
            0%, 100% {
                opacity: 1;
                transform: scale(1);
            }
            50% {
                opacity: 0.7;
                transform: scale(1.2);
            }
        }
        
        .content {
            padding: 30px;
        }
        
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #667eea;
            transition: all 0.3s ease;
        }
        
        .dark-mode .card {
            background: #2a2a2a;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        .card h3 {
            color: #333;
            margin-bottom: 15px;
            transition: color 0.3s ease;
        }
        
        .dark-mode .card h3 {
            color: #ffffff;
        }
        
        .dark-mode-text {
            transition: color 0.3s ease;
        }
        
        .dark-mode .dark-mode-text {
            color: #ffffff !important;
        }
        
        .dark-mode .text-muted {
            color: #aaa !important;
        }
        
        .dark-mode .card-subtitle {
            color: #bbb !important;
        }
        
        .dark-mode .card-title {
            color: #ffffff !important;
        }
        
        .dark-mode .info-item {
            background: #3a3a3a;
        }
        
        .account-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .info-label {
            font-weight: 600;
            color: #555;
            transition: color 0.3s ease;
        }
        
        .dark-mode .info-label {
            color: #ccc;
        }
        
        .info-value {
            font-weight: bold;
            color: #2a5298;
            transition: color 0.3s ease;
        }
        
        .dark-mode .info-value {
            color: #4fc3f7;
        }
        
        .trades-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .dark-mode .trades-table {
            background: #2a2a2a;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .trades-wrapper {
            max-height: 400px;
            overflow-y: auto;
            border-radius: 10px;
        }
        
        .trades-scroll-container {
            scrollbar-width: thin;
            scrollbar-color: #6c757d #f8f9fa;
        }
        
        .trades-scroll-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .trades-scroll-container::-webkit-scrollbar-track {
            background: #f8f9fa;
            border-radius: 4px;
        }
        
        .trades-scroll-container::-webkit-scrollbar-thumb {
            background: #6c757d;
            border-radius: 4px;
        }
        
        .trades-scroll-container::-webkit-scrollbar-thumb:hover {
            background: #495057;
        }
        
        .open-trade-item {
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            background: #f8f9fa;
            transition: all 0.3s ease;
        }
        
        .open-trade-item:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transform: translateY(-1px);
        }
        
        .trade-progress-bar {
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 8px;
        }
        
        .trade-progress-fill {
            height: 100%;
            transition: width 0.5s ease, background-color 0.3s ease;
            border-radius: 3px;
        }
        
        .trade-profit-positive {
            background: linear-gradient(90deg, #28a745, #20c997);
        }
        
        .trade-profit-negative {
            background: linear-gradient(90deg, #dc3545, #e74c3c);
        }
        
        .trades-table th {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 15px 10px;
            font-weight: 600;
            text-align: left;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .dark-mode .trades-table th {
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        }
        
        .trades-table td {
            padding: 12px 10px;
            border-bottom: 1px solid #eee;
            background: white;
            transition: all 0.3s ease;
            color: #333;
        }
        
        .dark-mode .trades-table td {
            background: #2a2a2a;
            border-bottom: 1px solid #444;
            color: #ffffff;
        }
        
        .trades-table tr:hover td {
            background: #f8f9fa;
        }
        
        .dark-mode .trades-table tr:hover td {
            background: #3a3a3a;
        }
        
        .profit-positive {
            color: #28a745;
            font-weight: bold;
        }
        
        .profit-negative {
            color: #dc3545;
            font-weight: bold;
        }
        
        .last-update {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-style: italic;
            transition: color 0.3s ease;
        }
        
        .dark-mode .last-update {
            color: #ccc;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        .updating {
            animation: pulse 1s infinite;
        }
        
        .balance-card {
            border-left-color: #28a745 !important;
        }
        
        .equity-card {
            border-left-color: #17a2b8 !important;
        }
        
        .profit-card {
            border-left-color: #ffc107 !important;
        }
        
        .chart-card {
            border-left-color: #6f42c1 !important;
        }
        
        .evolution-card {
            border-left-color: #e83e8c !important;
        }
        
        .chart-container {
            margin-top: 20px;
            height: 300px;
            position: relative;
        }

        .progress-dual {
            display: flex;
            align-items: center;
            height: 25px;
            background-color: #e9ecef;
            border-radius: .375rem;
            position: relative;
            overflow: hidden;
        }
        .progress-bar-gain {
            background-color: #28a745;
            height: 100%;
            transition: width .6s ease;
            position: absolute;
            left: 50%;
            border-top-right-radius: .375rem;
            border-bottom-right-radius: .375rem;
        }
        .progress-bar-loss {
            background-color: #dc3545;
            height: 100%;
            transition: width .6s ease;
            position: absolute;
            right: 50%;
            border-top-left-radius: .375rem;
            border-bottom-left-radius: .375rem;
        }
        .daily-limit-center-line {
            position: absolute;
            left: 50%;
            width: 4px;
            height: 100%;
            background-color: #fff;
            border-left: 1px solid #ced4da;
            border-right: 1px solid #ced4da;
            transform: translateX(-50%);
            z-index: 1;
        }
        
        .grid-layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .goal-card {
            border-left-color: #fd7e14 !important;
        }

        .goal-input-group {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }

        .goal-input-group input {
            width: 80px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
            text-align: center;
        }

        .goal-status {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 0.9em;
        }

        .metric-box {
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            color: white;
            display: flex;
            flex-direction: column;
        }

        .metric-box small {
            font-size: 0.75em;
            opacity: 0.9;
            text-transform: uppercase;
        }

        .metric-box strong {
            font-size: 1.2em;
            font-weight: 700;
        }

        .loss-box {
            background: #dc3545;
        }

        .gain-box {
            background: #28a745;
        }

        .progress-box {
            background: #0d6efd;
        }

        .progress-bar-container {
            background: #e9ecef;
            border-radius: 20px;
            height: 20px;
            overflow: hidden;
            margin-bottom: 10px;
        }

        .progress-bar {
            background: linear-gradient(135deg, #28a745 0%, #218838 100%);
            height: 100%;
            border-radius: 20px;
            transition: width 0.5s ease-in-out;
            text-align: center;
            color: white;
            font-weight: bold;
            line-height: 20px;
            font-size: 0.8em;
        }
        
        #goal-projection {
            font-size: 0.8em;
            color: #555;
            font-style: italic;
        }

        .modal {
            display: none; 
            position: fixed; 
            z-index: 1000; 
            left: 0;
            top: 0;
            width: 100%; 
            height: 100%; 
            overflow: auto; 
            background-color: rgba(0,0,0,0.6);
            animation: fadeIn 0.5s;
        }

        .modal-content {
            background: white;
            margin: 10% auto;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 500px;
            text-align: center;
            position: relative;
            transform: scale(0.9);
            animation: slideIn 0.5s forwards;
        }

        .modal-header h2 {
            color: #28a745;
            font-size: 2em;
        }

        .modal-body p {
            font-size: 1.1em;
            color: #333;
            margin: 15px 0;
        }

        .modal-footer {
            margin-top: 20px;
            font-weight: bold;
            color: #667eea;
        }

        .close-button {
            color: #aaa;
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }

        @keyframes fadeIn { from {opacity: 0;} to {opacity: 1;} }
        @keyframes slideIn { from {transform: translateY(-50px) scale(0.9);} to {transform: translateY(0) scale(1);} }

        .modal-loss .modal-header h2 {
            color: #dc3545;
        }

        .modal-loss .modal-footer {
            color: #dc3545;
        }
        
        /* Modal de Notificações */
        .notification-modal-content {
            background: linear-gradient(135deg, rgba(79, 195, 247, 0.2) 0%, rgba(79, 195, 247, 0.1) 100%);
            backdrop-filter: blur(20px);
            border: 2px solid rgba(79, 195, 247, 0.4);
            max-width: 600px;
            padding: 40px;
        }
        
        .dark-mode .notification-modal-content {
            background: linear-gradient(135deg, rgba(79, 195, 247, 0.15) 0%, rgba(79, 195, 247, 0.05) 100%);
            border-color: rgba(79, 195, 247, 0.5);
        }
        
        .notification-modal-header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .notification-modal-body {
            padding: 20px 0;
            text-align: center;
        }
        
        .notification-modal-footer {
            text-align: center;
            margin-top: 25px;
        }
        
        .notification-link-button {
            background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
            color: #000;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 193, 7, 0.4);
        }
        
        .notification-link-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 193, 7, 0.6);
            background: linear-gradient(135deg, #ff9800 0%, #ffc107 100%);
        }
        
        .notification-link-button i {
            margin-right: 8px;
        }
        
        /* Modal de Gráficos Avançados */
        #advanced-chart-modal .modal-content {
            width: 98%;
            height: 115vh;
            max-width: none;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            border: 1px solid rgba(76, 175, 80, 0.3);
            display: flex;
            flex-direction: row;
        }
        
        .dark-mode #advanced-chart-modal .modal-content {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        }
        
        /* Sidebar Esquerda */
        .chart-sidebar {
            width: 280px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border-right: 2px solid rgba(76, 175, 80, 0.3);
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }
        
        .dark-mode .chart-sidebar {
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        }
        
        .chart-modal-header {
            padding: 15px 20px;
            border-bottom: 1px solid rgba(76, 175, 80, 0.2);
        }
        
        .chart-modal-header h3 {
            color: #4caf50;
            margin: 0 0 15px 0;
            font-size: 1.5em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(76, 175, 80, 0.5),
                         0 0 20px rgba(76, 175, 80, 0.3),
                         0 0 30px rgba(76, 175, 80, 0.2);
            background: linear-gradient(135deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: titleGlow 3s ease-in-out 1;
            position: relative;
            display: inline-block;
            padding: 5px 0;
        }
        
        .chart-modal-header h3 .pro-text {
            font-size: 0.7em;
            font-weight: 600;
            vertical-align: middle;
            margin-left: 5px;
        }
        
        @keyframes titleGlow {
            0%, 100% {
                filter: brightness(1);
                text-shadow: 0 0 10px rgba(76, 175, 80, 0.5),
                             0 0 20px rgba(76, 175, 80, 0.3);
            }
            50% {
                filter: brightness(1.2);
                text-shadow: 0 0 15px rgba(76, 175, 80, 0.7),
                             0 0 30px rgba(76, 175, 80, 0.5),
                             0 0 45px rgba(76, 175, 80, 0.3);
            }
        }
        
        /* Barra de Progresso de Carregamento */
        .data-loading-container {
            margin-bottom: 20px;
            padding: 15px;
            background: rgba(76, 175, 80, 0.1);
            border-radius: 8px;
            border: 1px solid rgba(76, 175, 80, 0.3);
        }
        
        .loading-text {
            color: #4caf50;
            font-weight: 600;
            font-size: 0.95em;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .progress-bar-container {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 8px;
        }
        
        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #4caf50 0%, #66bb6a 50%, #4caf50 100%);
            background-size: 200% 100%;
            animation: progressAnimation 2s linear infinite, fillProgress 120s linear forwards;
            border-radius: 4px;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
        }
        
        @keyframes progressAnimation {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        @keyframes fillProgress {
            0% { width: 0%; }
            100% { width: 100%; }
        }
        
        .loading-subtitle {
            color: #aaa;
            font-size: 0.8em;
            text-align: center;
            font-style: italic;
        }
        
        .frequency-select {
            background: rgba(40, 40, 40, 0.95);
            border: 1px solid rgba(76, 175, 80, 0.4);
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            width: 100%;
            font-size: 0.9em;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .frequency-select:hover {
            border-color: #4caf50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
        }
        
        .frequency-select:focus {
            outline: none;
            border-color: #4caf50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.4);
        }
        
        .chart-modal-header .close-button:hover {
            color: #4caf50;
            transform: rotate(90deg);
        }
        
        .chart-toolbar {
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            flex: 1;
        }
        
        .chart-toolbar-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
            align-items: flex-start;
        }
        
        .chart-toolbar-group label {
            color: #ddd;
            font-size: 0.9em;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
        }
        
        .chart-toolbar-group label:first-child {
            font-weight: 600;
            color: #4caf50;
            margin-bottom: 5px;
        }
        
        .chart-toolbar-group input[type="checkbox"] {
            width: 16px;
            height: 16px;
            cursor: pointer;
        }
        
        .slider-container {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 8px;
            margin-bottom: 8px;
        }
        
        .period-slider {
            flex: 1;
            height: 6px;
            border-radius: 3px;
            background: rgba(255, 255, 255, 0.1);
            outline: none;
            -webkit-appearance: none;
            cursor: pointer;
        }
        
        .period-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #4caf50;
            cursor: pointer;
            box-shadow: 0 0 5px rgba(76, 175, 80, 0.5);
        }
        
        .period-slider::-moz-range-thumb {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #4caf50;
            cursor: pointer;
            border: none;
            box-shadow: 0 0 5px rgba(76, 175, 80, 0.5);
        }
        
        .period-slider::-webkit-slider-thumb:hover {
            background: #66bb6a;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.8);
        }
        
        .period-slider::-moz-range-thumb:hover {
            background: #66bb6a;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.8);
        }
        
        .slider-value {
            min-width: 35px;
            text-align: center;
            color: #4caf50;
            font-weight: 600;
            font-size: 0.95em;
            background: rgba(76, 175, 80, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
        }
        
        /* Área Principal dos Gráficos */
        .chart-main-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chart-container-wrapper {
            padding: 15px;
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .chart-section {
            background: rgba(20, 20, 20, 0.8);
            border-radius: 10px;
            padding: 10px;
            border: 1px solid rgba(76, 175, 80, 0.2);
            display: flex;
            flex-direction: column;
        }
        
        .chart-section canvas {
            background: rgba(10, 10, 10, 0.5);
            border-radius: 5px;
        }
        
        .symbol-selector {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .symbol-selector label {
            color: #4caf50;
            font-weight: 600;
            font-size: 0.9em;
        }
        
        .symbol-dropdown {
            background: rgba(40, 40, 40, 0.95);
            border: 1px solid rgba(76, 175, 80, 0.4);
            color: white;
            padding: 10px 12px;
            border-radius: 5px;
            width: 100%;
            font-size: 0.9em;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .symbol-dropdown:hover {
            border-color: #4caf50;
            background: rgba(50, 50, 50, 0.95);
        }
        
        .symbol-dropdown:focus {
            outline: none;
            border-color: #4caf50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.4);
        }
        
        .symbol-dropdown option {
            background: #2a2a2a;
            color: white;
            padding: 8px;
        }
        
        .symbol-dropdown optgroup {
            background: #1a1a1a;
            color: #4caf50;
            font-weight: 600;
            font-style: normal;
        }
        
        .custom-symbol-input {
            background: rgba(40, 40, 40, 0.95);
            border: 1px solid rgba(76, 175, 80, 0.4);
            color: white;
            padding: 10px 12px;
            border-radius: 5px;
            width: 100%;
            font-size: 0.9em;
            text-transform: uppercase;
            transition: all 0.3s ease;
        }
        
        .custom-symbol-input:focus {
            outline: none;
            border-color: #4caf50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.4);
        }
        
        .load-symbol-btn {
            background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            width: 100%;
            font-size: 0.9em;
            font-weight: 600;
            cursor: pointer;
            margin-top: 8px;
            transition: all 0.3s ease;
        }
        
        .load-symbol-btn:hover {
            background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
        }
        
        .load-symbol-btn:active {
            transform: translateY(0);
        }
        
        .chart-info-panel {
            background: rgba(30, 30, 30, 0.95);
            padding: 10px 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            border-top: 1px solid rgba(76, 175, 80, 0.2);
            color: #aaa;
            font-size: 0.85em;
        }
        
        .chart-info-panel span {
            white-space: nowrap;
        }
        
        .chart-info-panel strong {
            color: #4caf50;
        }
        
        @media (max-width: 768px) {
            .grid-layout {
                grid-template-columns: 1fr;
            }
            
            #advanced-chart-modal .modal-content {
                width: 100%;
                height: 100vh;
            }
            
            .chart-toolbar {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    </style>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;700&family=Rajdhani:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-annotation/2.1.0/chartjs-plugin-annotation.min.js"></script>
</head>
<body class="dark-mode">
    <div id="goal-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <span class="close-button">&times;</span>
                <h2 data-i18n="goal_reached_title">🎉 Parabéns! Meta Atingida! 🎉</h2>
            </div>
            <div class="modal-body">
                <p id="goal-modal-greeting"></p>
                <p id="goal-modal-message"></p>
                <p id="goal-modal-advice" data-i18n="goal_reached_advice">Excelente trabalho! Lembre-se que a disciplina é a chave para o sucesso a longo prazo. Considere fazer uma pausa e proteger seus lucros.</p>
                <p><strong data-i18n="goal_modal_recommendation_label">Recomendação:</strong> <span data-i18n="goal_recommendation">Pare de operar por hoje e volte amanhã com a mesma disciplina.</span></p>
            </div>
            <div class="modal-footer">
                <h3 data-i18n="goal_hashtags">#StopLoss #StopGain #Disciplina</h3>
            </div>
        </div>
    </div>

    <div id="loss-limit-modal" class="modal">
        <div class="modal-content modal-loss">
            <div class="modal-header">
                <span class="close-button loss-close-button">&times;</span>
                <h2 data-i18n="loss_limit_title">🚨 Atenção! Limite de Perda Atingido! 🚨</h2>
            </div>
            <div class="modal-body">
                <p id="loss-modal-greeting"></p>
                <p id="loss-modal-message"></p>
                <p id="loss-modal-warning" data-i18n="loss_limit_warning"><strong>Pare de operar imediatamente!</strong> A disciplina é crucial para proteger seu capital e garantir sua sobrevivência no mercado.</p>
                <p><strong data-i18n="loss_modal_recommendation_label">Recomendação:</strong> <span data-i18n="loss_recommendation">Feche a plataforma, revise suas operações e volte amanhã com a mente renovada.</span></p>
            </div>
            <div class="modal-footer">
                <h3 data-i18n="loss_hashtags">#StopLoss #GerenciamentoDeRisco #Disciplina</h3>
            </div>
        </div>
    </div>

    <!-- Modal de Notificações -->
    <div id="notification-modal" class="modal">
        <div class="modal-content notification-modal-content">
            <span class="close-button notification-close-button" onclick="closeNotificationModal()">&times;</span>
            <div class="notification-modal-header">
                <i class="fas fa-bell" style="font-size: 2em; color: #ffc107; margin-bottom: 10px;"></i>
                <h2 style="margin: 0; color: #ffffff;"></h2>
            </div>
            <div class="notification-modal-body">
                <p id="notification-info-text" style="color: #ffffff; font-size: 1.1em; line-height: 1.6; text-align: center;">
                    <!-- Texto da notificação será inserido aqui -->
                </p>
            </div>
            <div class="notification-modal-footer">
                <button id="notification-link-btn" class="notification-link-button" onclick="openNotificationLink()">
                    <i class="fas fa-external-link-alt"></i> Download
                </button>
            </div>
        </div>
    </div>

    <!-- Modal de Gráficos Avançados -->
    <div id="advanced-chart-modal" class="modal">
        <div class="modal-content">
            <!-- Botão Fechar (Canto Superior Direito) -->
            <span class="close-button" onclick="closeAdvancedChart()">&times;</span>
            
            <!-- Sidebar Esquerda -->
            <div class="chart-sidebar">
                <!-- Header -->
                <div class="chart-modal-header">
                    <!-- Barra de Progresso (aparece apenas se necessário) -->
                    <div id="data-loading-bar" class="data-loading-container" style="display: none;">
                        <div class="loading-text" data-i18n="loading_data">Coletando dados de mercado...</div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" id="progress-bar-fill"></div>
                        </div>
                        <div class="loading-subtitle" data-i18n="loading_subtitle">Aguarde enquanto reunimos ticks suficientes para análise precisa</div>
                    </div>
                    
                    <h3><span data-i18n="technical_analysis">Volat Scalper</span> <span class="pro-text">Pro</span></h3>
                    <div class="symbol-selector">
                        <label data-i18n="select_asset">Selecionar Ativo:</label>
                        <select id="symbol-dropdown" class="symbol-dropdown">
                            <option value="" data-i18n="select_or_type">-- Selecione ou digite abaixo --</option>
                            <optgroup label="🥇 " data-i18n="metals">Metais</optgroup>
                                <option value="XAUUSD">XAUUSD - Ouro vs Dólar</option>
                                <option value="XAGUSD">XAGUSD - Prata vs Dólar</option>
                            </optgroup>
                            <optgroup label="💱 " data-i18n="forex_major">Forex Principais</optgroup>
                                <option value="EURUSD">EURUSD - Euro vs Dólar</option>
                                <option value="GBPUSD">GBPUSD - Libra vs Dólar</option>
                                <option value="USDJPY">USDJPY - Dólar vs Iene</option>
                                <option value="AUDUSD">AUDUSD - Dólar Australiano</option>
                                <option value="USDCAD">USDCAD - Dólar Canadense</option>
                                <option value="USDCHF">USDCHF - Franco Suíço</option>
                                <option value="NZDUSD">NZDUSD - Dólar Neozelandês</option>
                            </optgroup>
                            <optgroup label="💱 " data-i18n="forex_cross">Forex Cruzados</optgroup>
                                <option value="EURGBP">EURGBP - Euro vs Libra</option>
                                <option value="EURJPY">EURJPY - Euro vs Iene</option>
                                <option value="GBPJPY">GBPJPY - Libra vs Iene</option>
                            </optgroup>
                            <optgroup label="🛢️ " data-i18n="commodities">Commodities</optgroup>
                                <option value="XTIUSD">XTIUSD - Petróleo WTI</option>
                                <option value="XBRUSD">XBRUSD - Petróleo Brent</option>
                            </optgroup>
                            <optgroup label="₿ " data-i18n="crypto">Criptomoedas</optgroup>
                                <option value="BTCUSD">BTCUSD - Bitcoin</option>
                                <option value="ETHUSD">ETHUSD - Ethereum</option>
                            </optgroup>
                            <optgroup label="📊 " data-i18n="indices">Índices</optgroup>
                                <option value="US30">US30 - Dow Jones</option>
                                <option value="US500">US500 - S&P 500</option>
                                <option value="NAS100">NAS100 - NASDAQ 100</option>
                                <option value="GER40">GER40 - DAX 40</option>
                            </optgroup>
                        </select>
                        
                        <label style="margin-top: 10px;" data-i18n="or_type_symbol">Ou digite o símbolo:</label>
                        <input type="text" id="custom-symbol-input" class="custom-symbol-input" placeholder="Ex: AAPL, TSLA, WINFUT..." maxlength="20">
                        <button id="load-custom-symbol" class="load-symbol-btn" data-i18n="load_button">Carregar</button>
                    </div>
                </div>
                
                <!-- Toolbar de Indicadores -->
                <div class="chart-toolbar">
                    <div class="chart-toolbar-group">
                        <label data-i18n="moving_averages">Médias Móveis:</label>
                        <label><input type="checkbox" id="ind-hull"> <span data-i18n="hull_ma">Hull MA</span></label>
                        <div class="slider-container">
                            <input type="range" id="hull-period" min="5" max="250" value="180" class="period-slider">
                            <span class="slider-value" id="hull-period-value">180</span>
                        </div>
                    </div>
                    
                    <div class="chart-toolbar-group">
                        <label data-i18n="oscillators">Osciladores:</label>
                        <label><input type="checkbox" id="ind-zscore" checked> <span data-i18n="zscore">Real Volatility</span></label>
                        <div class="slider-container">
                            <input type="range" id="zscore-period" min="5" max="200" value="150" class="period-slider">
                            <span class="slider-value" id="zscore-period-value">150</span>
                        </div>
                        <label><input type="checkbox" id="ind-rsi"> <span data-i18n="rsi">RSI</span></label>
                        <div class="slider-container">
                            <input type="range" id="rsi-period" min="5" max="70" value="14" class="period-slider">
                            <span class="slider-value" id="rsi-period-value">14</span>
                        </div>
                    </div>
                    
                    <div class="chart-toolbar-group">
                        <label data-i18n="chart_update_frequency">Frequência de Atualização:</label>
                        <select id="chart-update-frequency" class="frequency-select">
                            <option value="100">0.1s</option>
                            <option value="1000">1s</option>
                            <option value="5000" selected>5s</option>
                            <option value="10000">10s</option>
                            <option value="15000">15s</option>
                            <option value="20000">20s</option>
                        </select>
                    </div>
                    
                    <div class="chart-toolbar-group">
                        <label data-i18n="visualization">Visualização:</label>
                        <label><input type="checkbox" id="show-points"> <span data-i18n="show_points">Mostrar Pontos</span></label>
                    </div>
                </div>
            </div>
            
            <!-- Área Principal dos Gráficos -->
            <div class="chart-main-area">
                <!-- Gráficos -->
                <div class="chart-container-wrapper">
                    <!-- Gráfico Principal: Preço + Médias Móveis -->
                    <div class="chart-section" style="min-height: 320px; flex: 2;">
                        <canvas id="priceChartAdvanced" style="height: 320px;"></canvas>
                    </div>
                    
                    <!-- Gráfico Z-Score -->
                    <div class="chart-section" style="min-height: 270px; flex: 1;">
                        <canvas id="zscoreChart" style="height: 270px;"></canvas>
                    </div>
                    
                    <!-- Gráfico RSI (se ativado) -->
                    <div class="chart-section" id="rsi-section" style="min-height: 300px; flex: 1; display: none;">
                        <canvas id="rsiChart" style="height: 300px;"></canvas>
                    </div>
                </div>
                
                <!-- Footer com Informações -->
                <div class="chart-info-panel">
                    <span><span data-i18n="last_price">Último Preço</span>: <strong id="chart-last-price">-</strong></span>
                    <span><span data-i18n="hull_value">Hull MA</span>: <strong id="chart-hull-value">-</strong></span>
                    <span><span data-i18n="zscore_value">Real Volatility</span>: <strong id="chart-zscore-value">-</strong></span>
                    <span><span data-i18n="rsi_value">RSI</span>: <strong id="chart-rsi-value">-</strong></span>
                    <span><span data-i18n="last_update_charts">Atualizado</span>: <strong id="chart-last-update">-</strong></span>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="header">
            <button class="theme-toggle" onclick="toggleTheme()">
                <i class="fas fa-moon" id="theme-icon"></i>
            </button>
            <button class="language-toggle" onclick="showLanguageSelector()" title="Selecionar Idioma">
                <i class="fas fa-globe"></i>
            </button>
            <button class="chart-toggle" onclick="openAdvancedChart()" title="Gráficos Avançados">
                <i class="fas fa-chart-line"></i>
            </button>
            <button id="notification-btn" class="notification-btn" onclick="openNotification()" title="Nova Atualização Disponível" style="display: none;">
                <i class="fas fa-bell"></i>
                <span class="notification-badge"></span>
            </button>
            <button class="logout-btn" onclick="logout()" title="Sair">
                <i class="fas fa-sign-out-alt"></i>
            </button>
            <h1>VolatForex Monitor <span class="pro-text">Pro</span></h1>
            
            <!-- Mensagem Personalizada do Backend -->
            <div style="text-align: center; width: 100%;">
                <div id="custom-message" class="custom-message" style="display: none;">
                    <!-- A mensagem será inserida aqui via JavaScript -->
                </div>
            </div>
            
            <div class="account-info-header" id="account-info-header" style="margin-top: 10px; font-size: 0.9em; opacity: 0.8;">
                <!-- Informações da conta serão inseridas aqui via JavaScript -->
            </div>
            <div class="d-flex justify-content-between align-items-center mt-3">
                <div class="status" id="status">
                    <div class="status-icon"></div>
                    <span data-i18n="connected_status">Conectado</span>
                </div>
                <div class="update-frequency-control">
                    <label for="update-frequency" class="form-label text-white-50 me-2 small" data-i18n="frequency_label">Frequência:</label>
                    <select id="update-frequency" class="form-select form-select-sm opacity-75" style="width: auto; display: inline-block; font-size: 0.8rem;">
                        <option value="100" selected>0.1s</option>
                        <option value="1000">1s</option>
                        <option value="2000">2s</option>
                        <option value="5000">5s</option>
                        <option value="10000">10s</option>
                    </select>
                    <div class="last-update mt-1 small text-white-50 opacity-75" id="last-update">
                        <span data-i18n="last_update">Última atualização:</span> <span data-i18n="waiting">Aguardando...</span>
                    </div>
                </div>
            </div>

        <main class="content">

            <!-- Cards de Informação -->
            <div class="row">
                <div class="col-md-6 col-lg mb-4">
                    <div class="card h-100 shadow-sm border-start border-primary border-1">
                        <div class="card-body py-2 text-center">
                            <h6 class="card-subtitle text-muted dark-mode-text mb-1" data-i18n="current_balance">Saldo Atual</h6>
                            <h4 class="card-title fw-bold mb-0 dark-mode-text" id="balance">$0.00</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 col-lg mb-4">
                    <div class="card h-100 shadow-sm border-start border-info border-1">
                        <div class="card-body py-2 text-center">
                            <h6 class="card-subtitle text-muted dark-mode-text mb-1" data-i18n="equity">Equity</h6>
                            <h4 class="card-title fw-bold mb-1 dark-mode-text" id="equity">$0.00</h4>
                            <div class="d-flex justify-content-center">
                                <span class="badge bg-secondary" id="equity-result-value">0.00%</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 col-lg mb-4">
                    <div class="card h-100 shadow-sm border-start border-success border-1">
                        <div class="card-body py-2 text-center">
                            <h6 class="card-subtitle text-muted dark-mode-text mb-1" data-i18n="open_trades_pl">Abertos L/P</h6>
                            <h4 class="card-title fw-bold mb-1 dark-mode-text" id="open-trades-profit">$0.00</h4>
                            <span class="badge bg-secondary" id="open-trades-percentage">0.00%</span>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 col-lg mb-4">
                    <div class="card h-100 shadow-sm border-start border-warning border-1">
                        <div class="card-body py-2 text-center">
                            <h6 class="card-subtitle text-muted dark-mode-text mb-1" data-i18n="daily_pl">L/P do Dia</h6>
                            <h4 class="card-title fw-bold mb-1 dark-mode-text" id="profit">$0.00</h4>
                            <span class="badge bg-secondary" id="profit-percentage">0.00%</span>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 col-lg mb-4">
                    <div class="card h-100 shadow-sm border-start border-secondary border-1">
                        <div class="card-body py-2 text-center">
                            <h6 class="card-subtitle text-muted dark-mode-text mb-1" data-i18n="trades_today">Trades Hoje</h6>
                            <h4 class="card-title fw-bold mb-1 dark-mode-text" id="trades-today">0</h4>
                            <div class="d-flex justify-content-center gap-2">
                                <span class="badge bg-success" id="trades-positive">+0</span>
                                <span class="badge bg-danger" id="trades-negative">-0</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Gráficos e Metas -->
            <div class="row">
                <div class="col-lg-8 mb-4">
                    <div class="card h-100 shadow-sm border-light-subtle">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title"><i class="fas fa-chart-line me-2 text-primary"></i>Equity</h5>
                            <div class="chart-container flex-grow-1">
                                <canvas id="evolutionChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4 mb-4">
                    <div class="card shadow-sm h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="card-title mb-0"><i class="fas fa-chart-bar me-2"></i><span data-i18n="open_trades">Trades Abertos</span></h6>
                            <button id="sort-trades-btn" class="btn btn-sm btn-outline-secondary" title="Ordenar por lucro">
                                <i class="fas fa-sort-amount-down" id="sort-icon"></i>
                            </button>
                        </div>
                        <div class="card-body">
                            <!-- Botões de Controle de Fechamento -->
                            <div class="mb-3">
                                <div class="row g-1">
                                    <div class="col-6">
                                        <button id="close-negative-btn" class="btn btn-danger btn-sm w-100" title="Fechar apenas ordens negativas">
                                            <i class="fas fa-minus-circle me-1"></i><span data-i18n="close_negative">Fechar Negativas</span>
                                        </button>
                                    </div>
                                    <div class="col-6">
                                        <button id="close-positive-btn" class="btn btn-success btn-sm w-100" title="Fechar apenas ordens positivas">
                                            <i class="fas fa-plus-circle me-1"></i><span data-i18n="close_positive">Fechar Positivas</span>
                                        </button>
                                    </div>
                                    <div class="col-12 mt-1">
                                        <button id="close-all-btn" class="btn btn-warning btn-sm w-100" title="Fechar todas as ordens">
                                            <i class="fas fa-times-circle me-1"></i><span data-i18n="close_all">Fechar Todas</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div id="open-trades-container" style="max-height: 250px; overflow-y: auto; scrollbar-width: none; -ms-overflow-style: none;">
                <style>
                    #open-trades-container::-webkit-scrollbar {
                        display: none;
                    }
                </style>
                                <div class="text-center text-muted py-3">
                                    <i class="fas fa-clock fa-2x mb-2"></i>
                                    <p data-i18n="no_open_trades">Nenhum trade aberto no momento</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Seção de Metas e Limites -->
                <div class="col-12 mb-4">
                    <div class="card shadow-sm border-light-subtle">
                        <div class="card-body">
                            <div class="row">
                                <!-- Controles -->
                                <div class="col-lg-3 border-end">
                                    <h5 class="card-title mb-3"><i class="fas fa-cogs me-2"></i>Controles</h5>
                                    <div class="input-group input-group-sm mb-2">
                                        <span class="input-group-text" data-i18n="profit_goal">Meta Ganho</span>
                                        <input type="number" class="form-control" id="daily-goal-input" value="2" min="0.1" step="0.1">
                                        <span class="input-group-text">%</span>
                                    </div>
                                    <div class="input-group input-group-sm">
                                        <span class="input-group-text" data-i18n="loss_limit">Limite Perda</span>
                                        <input type="number" class="form-control" id="daily-loss-limit-input" value="1" min="0.1" step="0.1">
                                        <span class="input-group-text">%</span>
                                    </div>
                                </div>
                                <!-- Métricas e Progresso -->
                                <div class="col-lg-9">
                                    <div class="row g-2 mb-2">
                                        <div class="col-md-3">
                                            <div class="metric-box loss-box h-100">
                                                <small data-i18n="loss_limit">Limite Perda</small>
                                                <strong id="loss-limit-text">$0.00</strong>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="metric-box progress-box h-100">
                                                <small data-i18n="daily_progress">Progresso Diário</small>
                                                <strong id="daily-progress-text">$0.00</strong>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="metric-box gain-box h-100">
                                                <small data-i18n="profit_goal">Meta Ganho</small>
                                                <strong id="goal-target-text">$0.00</strong>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="progress-dual mt-2">
                                        <div class="progress-bar-loss" id="loss-progress-bar" style="width: 0%;"></div>
                                        <div class="daily-limit-center-line"></div>
                                        <div class="progress-bar-gain" id="gain-progress-bar" style="width: 0%;"></div>
                                    </div>
                                    <div class="row mt-2">
                                        <div class="col-6">
                                            <div class="text-start small" id="loss-percentage-text">
                                                <span class="text-danger fw-bold">🔻 <span data-i18n="loss_limit_text">Limite de perda</span>: 0%</span>
                                            </div>
                                        </div>
                                        <div class="col-6">
                                            <div class="text-end small" id="gain-percentage-text">
                                                <span class="text-success fw-bold">🎯 <span data-i18n="profit_goal_text">Meta de ganho</span>: 0%</span>
                                            </div>
                                        </div>
                                    </div>
                                     <div class="text-center mt-2 small text-muted" id="monthly-projection"><span data-i18n="monthly_projection">Projeção Mensal</span>: <b>$0.00</b></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Outros Gráficos -->
            <div class="row">
                <div class="col-lg-4 mb-4">
                    <div class="card h-100 shadow-sm border-light-subtle">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title"><i class="fas fa-chart-pie me-2 text-primary"></i><span data-i18n="symbol_distribution">Distribuição por Símbolo</span></h5>
                            <div class="chart-container flex-grow-1">
                                <canvas id="symbolChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-8 mb-4">
                    <div class="card h-100 shadow-sm border-light-subtle">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title"><i class="fas fa-chart-bar me-2 text-primary"></i><span data-i18n="profit_loss_chart">Lucro/Prejuízo (Últimos 15 Trades)</span></h5>
                            <div class="chart-container flex-grow-1">
                                <canvas id="profitChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Gráfico de Consolidação por Tempo -->
            <div class="row">
                <div class="col-12 mb-4">
                    <div class="card shadow-sm h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="card-title mb-0"><i class="fas fa-chart-bar me-2"></i><span data-i18n="consolidated_result">Resultado Consolidado por Tempo</span></h6>
                            <div class="col-auto">
                                <select id="time-group-selector" class="form-select form-select-sm">
                                    <option value="5" selected data-i18n="minutes_5">5 minutos</option>
                                    <option value="15" data-i18n="minutes_15">15 minutos</option>
                                    <option value="30" data-i18n="minutes_30">30 minutos</option>
                                    <option value="60" data-i18n="hour_1">1 hora</option>
                                    <option value="1440" data-i18n="day_1">1 dia</option>
                                </select>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="timeGroupedChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tabela de Trades -->
            <div class="row">
                <div class="col-12">
                    <div class="card shadow-sm">
                        <div class="card-header">
                            <h6 class="card-title mb-0"><i class="fas fa-history me-2"></i><span data-i18n="recent_trades_history">Histórico de Trades Recentes</span></h6>
                        </div>
                        <div class="card-body p-0">
                            <div class="trades-scroll-container" style="height: 400px; overflow-y: scroll !important; border: 1px solid #dee2e6; border-radius: 0.375rem; display: block;">
                                <table class="table table-striped table-hover table-sm mb-0 trade-table" style="width: 100%; table-layout: fixed;">
                                    <thead class="table-dark" style="position: sticky; top: 0; z-index: 10; background-color: #212529 !important;">
                                        <tr>
                                            <th style="width: 5%;">#</th>
                                            <th style="width: 12%;" data-i18n="ticket">Ticket</th>
                                            <th style="width: 15%;" data-i18n="time">Hora de Abertura</th>
                                            <th style="width: 8%;" data-i18n="type">Tipo</th>
                                            <th style="width: 8%;" data-i18n="volume">Volume</th>
                                            <th style="width: 10%;" data-i18n="symbol">Símbolo</th>
                                            <th style="width: 12%;" data-i18n="open_price">Preço de Abertura</th>
                                            <th style="width: 15%;" data-i18n="current_price">Preço de Fechamento</th>
                                            <th style="width: 15%;" data-i18n="profit">Lucro</th>
                                        </tr>
                                    </thead>
                                    <tbody id="trades-tbody">
                                        <!-- Dados preenchidos via JS -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>

    </div>

    <script>
        // --- Dados do Usuário (do Backend) ---
        const userFirstName = "{{ user_first_name }}";
        const userMessages = {{ user_messages|safe }};
        const userNotifications = {{ user_notifications|safe }};
        
        // Variável global para armazenar a notificação atual
        let currentNotificationData = null;
        
        // --- Função para obter o idioma atual ---
        function getCurrentLanguage() {
            return localStorage.getItem('volatforex_language') || 'pt';
        }
        
        // --- Processar e Exibir Mensagem Personalizada (Multilíngue) ---
        function displayCustomMessage() {
            const messageContainer = document.getElementById('custom-message');
            const currentLang = getCurrentLanguage();
            
            if (userMessages && userMessages.length > 0) {
                // Filtrar mensagens pelo idioma atual
                const messageData = userMessages.find(msg => msg.idioma === currentLang && msg.onoff === "on");
                
                if (messageData && messageData.frase) {
                    // Substituir "usuario" pelo nome real (case-insensitive)
                    const personalizedMessage = messageData.frase.replace(/usuario/gi, userFirstName);
                    
                    // Exibir mensagem
                    messageContainer.textContent = personalizedMessage;
                    messageContainer.style.display = 'block';
                    
                    console.log('[CUSTOM MESSAGE] Mensagem exibida (', currentLang, '):', personalizedMessage);
                } else {
                    messageContainer.style.display = 'none';
                    console.log('[CUSTOM MESSAGE] Nenhuma mensagem ativa para o idioma:', currentLang);
                }
            } else {
                messageContainer.style.display = 'none';
            }
        }
        
        // --- Processar e Exibir Notificações (Multilíngue) ---
        function displayNotification() {
            const notificationBtn = document.getElementById('notification-btn');
            const currentLang = getCurrentLanguage();
            
            if (userNotifications && userNotifications.length > 0) {
                // Filtrar notificações pelo idioma atual
                const notificationData = userNotifications.find(notif => notif.idioma === currentLang && notif.onoff === "on");
                
                if (notificationData && notificationData.link && notificationData.info) {
                    // Armazenar dados da notificação
                    currentNotificationData = notificationData;
                    
                    // Exibir botão de notificação
                    notificationBtn.style.display = 'flex';
                    
                    console.log('[NOTIFICATION] Notificação ativa (', currentLang, '):', notificationData.info);
                } else {
                    notificationBtn.style.display = 'none';
                    currentNotificationData = null;
                    console.log('[NOTIFICATION] Nenhuma notificação ativa para o idioma:', currentLang);
                }
            } else {
                notificationBtn.style.display = 'none';
                currentNotificationData = null;
            }
        }
        
        // --- Função para abrir o modal de notificação ---
        function openNotification() {
            if (currentNotificationData) {
                const modal = document.getElementById('notification-modal');
                const infoText = document.getElementById('notification-info-text');
                
                // Inserir texto da notificação
                infoText.textContent = currentNotificationData.info;
                
                // Exibir modal
                modal.style.display = 'block';
                
                console.log('[NOTIFICATION MODAL] Modal aberto');
            }
        }
        
        // --- Função para fechar o modal de notificação ---
        function closeNotificationModal() {
            const modal = document.getElementById('notification-modal');
            modal.style.display = 'none';
            console.log('[NOTIFICATION MODAL] Modal fechado');
        }
        
        // --- Função para abrir o link da notificação ---
        function openNotificationLink() {
            if (currentNotificationData && currentNotificationData.link) {
                window.open(currentNotificationData.link, '_blank');
                console.log('[NOTIFICATION] Link aberto:', currentNotificationData.link);
                
                // Fechar modal após abrir link
                closeNotificationModal();
            }
        }
        
        // --- Fechar modal ao clicar fora ---
        window.onclick = function(event) {
            const modal = document.getElementById('notification-modal');
            if (event.target == modal) {
                closeNotificationModal();
            }
        }
        
        // --- Atualizar mensagens e notificações quando o idioma mudar ---
        function updateLanguageContent() {
            displayCustomMessage();
            displayNotification();
        }
        
        // --- Executar ao carregar a página ---
        document.addEventListener('DOMContentLoaded', function() {
            displayCustomMessage();
            displayNotification();
            
            // Observar mudanças no localStorage (quando o idioma mudar em outra aba)
            window.addEventListener('storage', function(e) {
                if (e.key === 'volatforex_language') {
                    updateLanguageContent();
                }
            });
            
            // Escutar evento de mudança de idioma (disparado pelo i18n.js)
            document.addEventListener('languageChanged', function(e) {
                console.log('[LANGUAGE] Idioma alterado para:', e.detail.language);
                updateLanguageContent();
            });
        });
        
        let profitChart = null;
        let symbolChart = null;
        let evolutionChart = null;
        let timeGroupedChart = null; // Gráfico de consolidação por tempo
        let distributionChart = null; // Gráfico de distribuição de trades
        let updateInterval = null;
        let currentUpdateFrequency = 100; // Frequência padrão: 0.1 segundos
        let isUpdating = false;
        let goalReachedToday = false;
        let lossLimitReachedToday = false;
        let cachedBalanceHistory = [];
        let sortTradesDescending = true; // Controle de ordenação dos trades
        
        // --- Lógica de Metas e Limites ---
        let initialBalance = null;
        const goalModal = document.getElementById('goal-modal');
        const lossLimitModal = document.getElementById('loss-limit-modal');
        const closeModalButton = document.querySelector('.close-button');
        const lossCloseModalButton = document.querySelector('.loss-close-button');

        // Novos elementos
        const dailyGoalInput = document.getElementById('daily-goal-input');
        const lossLimitInput = document.getElementById('daily-loss-limit-input');

        function setupGoalAndLimitControls() {
            const savedGoal = localStorage.getItem('dailyGoalPercentage');
            const savedLossLimit = localStorage.getItem('dailyLossLimitPercentage');

            if (savedGoal) dailyGoalInput.value = savedGoal;
            if (savedLossLimit) lossLimitInput.value = savedLossLimit;

            dailyGoalInput.addEventListener('input', (e) => {
                localStorage.setItem('dailyGoalPercentage', e.target.value);
                if (window.latest_data) updateDailyMetrics(window.latest_data.account_info || {});
            });

            lossLimitInput.addEventListener('input', (e) => {
                localStorage.setItem('dailyLossLimitPercentage', e.target.value);
                if (window.latest_data) updateDailyMetrics(window.latest_data.account_info || {});
            });
            window.goalControlsInitialized = true;
        }

        // Fechar modais
        closeModalButton.onclick = () => { goalModal.style.display = 'none'; };
        lossCloseModalButton.onclick = () => { lossLimitModal.style.display = 'none'; };
        window.onclick = (event) => {
            if (event.target == goalModal) goalModal.style.display = 'none';
            if (event.target == lossLimitModal) lossLimitModal.style.display = 'none';
        };
        // --- Fim da Lógica de Metas e Limites ---

        // Controle mais eficiente do scroll
        let scrollPosition = 0;
        let isUserInteracting = false;
        let interactionTimeout = null;
        
        // Detecta interação do usuário (scroll, mouse, touch)
        function detectUserInteraction() {
            isUserInteracting = true;
            scrollPosition = window.scrollY;
            
            if (interactionTimeout) {
                clearTimeout(interactionTimeout);
            }
            
            interactionTimeout = setTimeout(() => {
                isUserInteracting = false;
            }, 3000); // 3 segundos sem interação
        }
        
        window.addEventListener('scroll', detectUserInteraction, { passive: true });
        window.addEventListener('mousedown', detectUserInteraction, { passive: true });
        window.addEventListener('touchstart', detectUserInteraction, { passive: true });
        window.addEventListener('wheel', detectUserInteraction, { passive: true });
        
        function formatCurrency(value) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(value);
        }
        
        function formatProfit(value) {
            const num = parseFloat(value);
            const formatted = num.toFixed(2);
            return num >= 0 ? `+$${formatted}` : `-$${Math.abs(num).toFixed(2)}`;
        }

        function calculateOpenTime(openTime) {
            if (!openTime) return '0h 0m';
            
            try {
                const now = new Date();
                let tradeTime;
                
                console.log('=== DEBUG COMPLETO ===');
                console.log('openTime original:', openTime);
                console.log('Hora atual (now):', now.toISOString());
                console.log('Hora atual local:', now.toString());
                
                // Tentar diferentes formatos de data
                if (typeof openTime === 'string') {
                    // Se contém 'T', é formato ISO
                    if (openTime.includes('T')) {
                        tradeTime = new Date(openTime);
                        console.log('Formato ISO - sem ajuste');
                    } else {
                        // Formato do MT5: "YYYY.MM.DD HH:MM:SS"
                        const cleanTime = openTime.replace(/\\./g, '-');
                        console.log('Formato MT5 convertido:', cleanTime);
                        
                        tradeTime = new Date(cleanTime);
                        console.log('Data parseada ANTES do ajuste:', tradeTime.toISOString());
                        
                        // Ajustar para fuso horário local (subtrair 6 horas)
                        tradeTime.setHours(tradeTime.getHours() - 6);
                        console.log('Data APÓS ajuste de -6h:', tradeTime.toISOString());
                    }
                } else {
                    // Se é timestamp numérico
                    tradeTime = new Date(openTime * 1000);
                    console.log('Timestamp numérico');
                }
                
                // Verificar se a data é válida
                if (isNaN(tradeTime.getTime())) {
                    console.log('Data inválida!');
                    return 'Data inválida';
                }
                
                const diffMs = now - tradeTime;
                const diffMinutes = diffMs / (1000 * 60);
                
                console.log('Diferença em ms:', diffMs);
                console.log('Diferença em minutos:', diffMinutes);
                
                // Verificação de sincronização
                if (diffMs < 0) {
                    console.log('AINDA É NEGATIVO - mostrando Sincronizando...');
                    return 'Sincronizando...';
                }
                
                const totalMinutes = Math.floor(diffMs / (1000 * 60));
                const hours = Math.floor(totalMinutes / 60);
                const minutes = totalMinutes % 60;
                
                const result = `${hours}h ${minutes}m`;
                console.log('Resultado final:', result);
                console.log('=== FIM DEBUG ===');
                
                return result;
                
            } catch (error) {
                console.error('Erro ao calcular tempo do trade:', error, openTime);
                return 'Erro de tempo';
            }
        }
        
        // Função para atualizar informações da conta no cabeçalho
        function updateAccountHeader(accountInfo) {
            const headerElement = document.getElementById('account-info-header');
            if (!headerElement) return;
            
            let accountText = '';
            
            // Formato: "Licenciando para: Nome do usuário, Conta: 123456789"
            if (accountInfo.account_name || accountInfo.account_login || accountInfo.account_number) {
                accountText = 'Licenciando para: ';
                
                // Adicionar nome do usuário se disponível
                if (accountInfo.account_name) {
                    accountText += accountInfo.account_name;
                } else {
                    accountText += 'Usuário';
                }
                
                // Adicionar número da conta se disponível
                if (accountInfo.account_login || accountInfo.account_number) {
                    const accountNumber = accountInfo.account_login || accountInfo.account_number;
                    accountText += `, Conta: ${accountNumber}`;
                }
            }
            
            headerElement.textContent = accountText;
        }
        
        // Função para atualizar porcentagem do lucro/prejuízo
        function updateProfitPercentage(profit, balance) {
            const percentageElement = document.getElementById('profit-percentage');
            if (!percentageElement || balance === 0) return;
            
            const percentage = (profit / balance) * 100;
            const formattedPercentage = percentage.toFixed(2) + '%';
            
            percentageElement.textContent = formattedPercentage;
            
            // Atualizar cor baseada no valor
            percentageElement.className = 'badge ms-2';
            if (percentage > 0) {
                percentageElement.classList.add('bg-success');
            } else if (percentage < 0) {
                percentageElement.classList.add('bg-danger');
            } else {
                percentageElement.classList.add('bg-secondary');
            }
        }
        
        // Função para gerar hash simples dos dados
        function generateHash(data) {
            return JSON.stringify(data).split('').reduce((a, b) => {
                a = ((a << 5) - a) + b.charCodeAt(0);
                return a & a;
            }, 0);
        }
        
        function updateDailyMetrics(accountInfo, calculatedDailyProfit = null) {
            if (!accountInfo || typeof accountInfo.account_balance === 'undefined') return;

            const currentBalance = accountInfo.account_balance;
            const goalPercentage = parseFloat(dailyGoalInput.value) || 0;
            const lossLimitPercentage = parseFloat(lossLimitInput.value) || 0;
            
            // Usar o lucro já calculado se fornecido, senão calcular novamente
            let dailyProfit = calculatedDailyProfit;
            
            if (dailyProfit === null) {
                // Calcular lucro dos trades do dia
                const todayLocal = moment().startOf('day');
                const allTrades = window.latest_data?.last_trades || [];
                const tradesToday = allTrades.filter(trade => {
                    if (!trade.time) return false;
                    
                    let tradeTime;
                    if (typeof trade.time === 'string' && !trade.time.includes('T')) {
                        const cleanTime = trade.time.replace(/\\./g, '-');
                        tradeTime = moment(cleanTime).subtract(6, 'hours');
                    } else {
                        tradeTime = moment(trade.time);
                    }
                    
                    return tradeTime.isSame(todayLocal, 'day');
                });
                
                dailyProfit = tradesToday.reduce((sum, trade) => sum + parseFloat(trade.profit || 0), 0);
            }

            // Calcular metas baseadas no saldo atual
            const goalTarget = currentBalance * (goalPercentage / 100);
            const lossLimitTarget = -currentBalance * (lossLimitPercentage / 100); // Valor negativo

            // Atualiza textos nos boxes de métricas
            document.getElementById('goal-target-text').textContent = formatCurrency(goalTarget);
            document.getElementById('loss-limit-text').textContent = formatCurrency(lossLimitTarget);
            document.getElementById('daily-progress-text').textContent = formatCurrency(dailyProfit);
            
            const gainProgressBar = document.getElementById('gain-progress-bar');
            const lossProgressBar = document.getElementById('loss-progress-bar');

            // Lógica da barra de progresso dupla
            if (dailyProfit > 0) {
                const gainProgress = goalTarget > 0 ? Math.min(100, (dailyProfit / goalTarget) * 100) : 0;
                gainProgressBar.style.width = `${gainProgress / 2}%`; // Ocupa no máximo 50% da barra total
                lossProgressBar.style.width = '0%';
            } else if (dailyProfit < 0) {
                const lossProgress = lossLimitTarget < 0 ? Math.min(100, (dailyProfit / lossLimitTarget) * 100) : 0;
                lossProgressBar.style.width = `${lossProgress / 2}%`; // Ocupa no máximo 50% da barra total
                gainProgressBar.style.width = '0%';
            } else {
                gainProgressBar.style.width = '0%';
                lossProgressBar.style.width = '0%';
            }

            // Calcular porcentagens atuais
            let lossPercentage = 0;
            let gainPercentage = 0;
            
            if (dailyProfit < 0 && lossLimitTarget < 0) {
                lossPercentage = Math.min(100, Math.abs(dailyProfit / lossLimitTarget) * 100);
            }
            
            if (dailyProfit > 0 && goalTarget > 0) {
                gainPercentage = Math.min(100, (dailyProfit / goalTarget) * 100);
            }
            
            // Atualizar textos de porcentagem com frases criativas
            const lossPercentageElement = document.getElementById('loss-percentage-text');
            const gainPercentageElement = document.getElementById('gain-percentage-text');
            
            if (lossPercentage > 0) {
                let lossMessage = '';
                if (lossPercentage < 25) {
                    lossMessage = `🟢 ${t('risk_low')}: ${lossPercentage.toFixed(1)}%`;
                } else if (lossPercentage < 50) {
                    lossMessage = `🟡 ${t('attention')}: ${lossPercentage.toFixed(1)}%`;
                } else if (lossPercentage < 75) {
                    lossMessage = `🟠 ${t('risk_high')}: ${lossPercentage.toFixed(1)}%`;
                } else {
                    lossMessage = `🔴 ${t('critical_danger')}: ${lossPercentage.toFixed(1)}%`;
                }
                lossPercentageElement.innerHTML = `<span class="text-danger fw-bold">🔻 ${lossMessage}</span>`;
            } else {
                lossPercentageElement.innerHTML = `<span class="text-muted fw-bold">🔻 ${t('loss_limit_text')}: 0%</span>`;
            }
            
            if (gainPercentage > 0) {
                let gainMessage = '';
                if (gainPercentage < 25) {
                    gainMessage = `${t('progressing')}: ${gainPercentage.toFixed(1)}%`;
                } else if (gainPercentage < 50) {
                    gainMessage = `${t('good_pace')}: ${gainPercentage.toFixed(1)}%`;
                } else if (gainPercentage < 75) {
                    gainMessage = `${t('almost_there')}: ${gainPercentage.toFixed(1)}%`;
                } else if (gainPercentage < 100) {
                    gainMessage = `${t('very_close')}: ${gainPercentage.toFixed(1)}%`;
                } else {
                    gainMessage = `${t('goal_achieved')}: ${gainPercentage.toFixed(1)}%`;
                }
                gainPercentageElement.innerHTML = `<span class="text-success fw-bold">🎯 ${gainMessage}</span>`;
            } else {
                gainPercentageElement.innerHTML = `<span class="text-muted fw-bold">🎯 ${t('profit_goal_text')}: 0%</span>`;
            }

            // Projeção Mensal
            const monthlyProjection = dailyProfit > 0 ? goalTarget * 22 : dailyProfit * 22;
            document.getElementById('monthly-projection').innerHTML = `${t('monthly_projection')}: <b>${formatCurrency(monthlyProjection)}</b>`;

            // Alerta de Meta Atingida
            if (dailyProfit >= goalTarget && goalTarget > 0 && !goalReachedToday) {
                goalReachedToday = true;
                
                // Preencher modal com nome do usuário e traduções
                const userName = userFirstName || 'Trader';
                document.getElementById('goal-modal-greeting').innerHTML = `<strong>${t('goal_reached_greeting')} ${userName}!</strong>`;
                document.getElementById('goal-modal-message').innerHTML = `${t('goal_reached_message')} <strong>${formatCurrency(goalTarget)}</strong>!`;
                
                goalModal.style.display = 'block';
            }

            // Alerta de Limite de Perda Atingido
            if (dailyProfit <= lossLimitTarget && lossLimitTarget < 0 && !lossLimitReachedToday) {
                lossLimitReachedToday = true;
                
                // Preencher modal com nome do usuário e traduções
                const userName = userFirstName || 'Trader';
                document.getElementById('loss-modal-greeting').innerHTML = `<strong>${t('loss_limit_greeting')} ${userName}!</strong>`;
                document.getElementById('loss-modal-message').innerHTML = `${t('loss_limit_message')} <strong>${formatCurrency(lossLimitTarget)}</strong>.`;
                
                lossLimitModal.style.display = 'block';
            }
        }

        function hasDataChanged(newData) {
            const newHash = generateHash(newData.account_info || {});
            const tradesHash = generateHash(newData.last_trades || []);
            
            const dataChanged = newHash !== lastDataHash;
            const tradesChanged = tradesHash !== lastTradesHash;
            
            if (dataChanged) lastDataHash = newHash;
            if (tradesChanged) {
                lastTradesHash = tradesHash;
                // Atualiza cache dos trades quando mudarem
                cachedTradesData = [...(newData.last_trades || [])];
            }
            
            return { dataChanged, tradesChanged };
        }
        
        function createEvolutionChart(balanceHistory) {
            const ctx = document.getElementById('evolutionChart').getContext('2d');
            
            if (!balanceHistory || balanceHistory.length === 0) {
                if (evolutionChart) {
                    evolutionChart.destroy();
                    evolutionChart = null;
                }
                return;
            }
            
            // Atualiza cache dos dados de evolução
            cachedBalanceHistory = [...balanceHistory];
            
            const labels = balanceHistory.map(item => 
                moment(item.timestamp).format('HH:mm:ss')
            );
            const balanceData = balanceHistory.map(item => item.balance);
            const equityData = balanceHistory.map(item => item.equity);
            
            // Detecta o tema atual
            const isDarkMode = document.body.classList.contains('dark-mode');
            const textColor = isDarkMode ? '#ffffff' : '#333333';
            const gridColor = isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
            
            if (!evolutionChart) {
                evolutionChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Equity ($)',
                            data: equityData,
                            borderColor: 'rgba(23, 162, 184, 1)',
                            backgroundColor: 'rgba(23, 162, 184, 0.1)',
                            borderWidth: 3,
                            fill: false,
                            tension: 0.4,
                            pointBackgroundColor: 'rgba(23, 162, 184, 1)',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointRadius: 0,
                            pointHoverRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: {
                            duration: 950,
                            easing: 'easeInOutQuart'
                        },
                        interaction: {
                            intersect: false,
                            mode: 'index'
                        },
                        scales: {
                            x: {
                                display: true,
                                title: {
                                    display: true,
                                    text: 'Hora',
                                    color: textColor
                                },
                                ticks: {
                                    color: textColor
                                },
                                grid: {
                                    color: gridColor
                                }
                            },
                            y: {
                                display: true,
                                title: {
                                    display: true,
                                    text: 'Valor ($)',
                                    color: textColor
                                },
                                ticks: {
                                    callback: function(value) {
                                        return '$' + value.toFixed(2);
                                    },
                                    color: textColor
                                },
                                grid: {
                                    color: gridColor
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                                labels: {
                                    color: textColor
                                }
                            },
                            tooltip: {
                                mode: 'index',
                                intersect: false,
                                backgroundColor: 'rgba(0,0,0,0.8)',
                                titleColor: 'white',
                                bodyColor: 'white',
                                borderColor: 'rgba(255,255,255,0.2)',
                                borderWidth: 1,
                                callbacks: {
                                    title: function(context) {
                                        const index = context[0].dataIndex;
                                        if (cachedBalanceHistory[index]) {
                                            return moment(cachedBalanceHistory[index].timestamp).format('DD/MM/YYYY HH:mm:ss');
                                        }
                                        return '';
                                    }
                                }
                            }
                        }
                    }
                });
            } else {
                evolutionChart.data.labels = labels;
                evolutionChart.data.datasets[0].data = equityData;
                evolutionChart.update();
            }
        }
        
        function createProfitChart(trades) {
            const ctx = document.getElementById('profitChart').getContext('2d');
            
            // Pega apenas os últimos 15 trades para o gráfico
            const recentTrades = trades.slice(0, 15);
            
            if (recentTrades.length === 0) {
                if (profitChart) {
                    profitChart.destroy();
                    profitChart = null;
                }
                return;
            }
            
            // Inverte a ordem para mostrar da esquerda para direita (mais antigo à esquerda)
            const reversedTrades = [...recentTrades].reverse();
            const labels = reversedTrades.map((trade, index) => '#' + (recentTrades.length - index));
            const profits = reversedTrades.map(trade => parseFloat(trade.profit));
            
            const backgroundColors = profits.map(profit => 
                profit >= 0 ? 'rgba(40, 167, 69, 0.8)' : 'rgba(220, 53, 69, 0.8)'
            );
            
            const borderColors = profits.map(profit => 
                profit >= 0 ? 'rgba(40, 167, 69, 1)' : 'rgba(220, 53, 69, 1)'
            );
            
            // Só recria o gráfico se não existir ou se os dados mudaram significativamente
            if (!profitChart || profitChart.data.datasets[0].data.length !== profits.length) {
                if (profitChart) {
                    profitChart.destroy();
                }
                
                profitChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: window.i18n ? window.i18n.t('profit_loss_label') : 'Lucro/Prejuízo ($)',
                            data: profits,
                            backgroundColor: backgroundColors,
                            borderColor: borderColors,
                            borderWidth: 2,
                            borderRadius: 4,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: function(value) {
                                        return '$' + value.toFixed(2);
                                    }
                                },
                                grid: {
                                    color: 'rgba(0,0,0,0.1)'
                                }
                            },
                            x: {
                                grid: {
                                    display: false
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                callbacks: {
                                    title: function(context) {
                                        // Usa o índice para acessar o trade correto
                                        const tradeIndex = context[0].dataIndex;
                                        const trade = reversedTrades[tradeIndex];
                                        return 'Trade #' + trade.ticket;
                                    },
                                    label: function(context) {
                                        // Usa o índice para acessar informações precisas do trade
                                        const tradeIndex = context.dataIndex;
                                        const trade = reversedTrades[tradeIndex];
                                        return [
                                            'Símbolo: ' + trade.symbol,
                                            'Tipo: ' + trade.type,
                                            'Lucro: $' + context.parsed.y.toFixed(2),
                                            'Data: ' + moment(trade.time).format('DD/MM/YYYY HH:mm:ss')
                                        ];
                                    }
                                }
                            }
                        }
                    }
                });
            } else {
                // Atualiza apenas os dados e recria callbacks com dados atualizados
                profitChart.data.labels = labels;
                profitChart.data.datasets[0].data = profits;
                profitChart.data.datasets[0].backgroundColor = backgroundColors;
                profitChart.data.datasets[0].borderColor = borderColors;
                
                // Recria callbacks do tooltip com dados atualizados
                profitChart.options.plugins.tooltip.callbacks.title = function(context) {
                    const tradeIndex = context[0].dataIndex;
                    const trade = reversedTrades[tradeIndex];
                    return 'Trade #' + trade.ticket;
                };
                
                profitChart.options.plugins.tooltip.callbacks.label = function(context) {
                    const tradeIndex = context.dataIndex;
                    const trade = reversedTrades[tradeIndex];
                    return [
                        'Símbolo: ' + trade.symbol,
                        'Tipo: ' + trade.type,
                        'Lucro: $' + context.parsed.y.toFixed(2),
                        'Data: ' + moment(trade.time).format('DD/MM/YYYY HH:mm:ss')
                    ];
                };
                
                profitChart.update('none');
            }
        }
        
        function createSymbolChart(trades) {
            const ctx = document.getElementById('symbolChart').getContext('2d');
            
            if (trades.length === 0) {
                if (symbolChart) {
                    symbolChart.destroy();
                    symbolChart = null;
                }
                return;
            }
            
            // Agrupa por símbolo e calcula lucro total
            const symbolData = {};
            trades.forEach(trade => {
                if (!symbolData[trade.symbol]) {
                    symbolData[trade.symbol] = {
                        profit: 0,
                        count: 0
                    };
                }
                symbolData[trade.symbol].profit += parseFloat(trade.profit);
                symbolData[trade.symbol].count++;
            });
            
            const symbols = Object.keys(symbolData);
            const profits = symbols.map(symbol => symbolData[symbol].profit);
            
            if (symbols.length === 0) {
                if (symbolChart) {
                    symbolChart.destroy();
                    symbolChart = null;
                }
                return;
            }
            
            const backgroundColors = [
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 99, 132, 0.8)',
                'rgba(255, 205, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)',
                'rgba(153, 102, 255, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(199, 199, 199, 0.8)',
                'rgba(83, 102, 255, 0.8)'
            ];
            
            // Só recria o gráfico se necessário
            if (!symbolChart || symbolChart.data.labels.length !== symbols.length) {
                if (symbolChart) {
                    symbolChart.destroy();
                }
                
                symbolChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: symbols,
                        datasets: [{
                            data: profits.map(p => Math.abs(p)),
                            backgroundColor: backgroundColors.slice(0, symbols.length),
                            borderColor: backgroundColors.slice(0, symbols.length).map(color => 
                                color.replace('0.8', '1')),
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: false,
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: {
                                    generateLabels: function(chart) {
                                        const data = chart.data;
                                        return data.labels.map((label, i) => ({
                                            text: label + ' ($' + profits[i].toFixed(2) + ')',
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            strokeStyle: data.datasets[0].borderColor[i],
                                            lineWidth: data.datasets[0].borderWidth,
                                            index: i
                                        }));
                                    }
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const symbol = symbols[context.dataIndex];
                                        const data = symbolData[symbol];
                                        return [
                                            'Símbolo: ' + symbol,
                                            'Trades: ' + data.count,
                                            'P&L Total: $' + data.profit.toFixed(2)
                                        ];
                                    }
                                }
                            }
                        }
                    }
                });
            } else {
                // Atualiza apenas os dados
                symbolChart.data.labels = symbols;
                symbolChart.data.datasets[0].data = profits.map(p => Math.abs(p));
                
                // Atualiza legendas
                symbolChart.options.plugins.legend.labels.generateLabels = function(chart) {
                    const data = chart.data;
                    return data.labels.map((label, i) => ({
                        text: label + ' ($' + profits[i].toFixed(2) + ')',
                        fillStyle: data.datasets[0].backgroundColor[i],
                        strokeStyle: data.datasets[0].borderColor[i],
                        lineWidth: data.datasets[0].borderWidth,
                        index: i
                    }));
                };
                
                symbolChart.update('none');
            }
        }
        
        function updateTimeGroupedChart(trades) {
            console.log('updateTimeGroupedChart chamada com', trades.length, 'trades'); // Debug
            
            const intervalSelector = document.getElementById('time-group-selector');
            const selectedInterval = parseInt(intervalSelector.value);
            console.log('Intervalo selecionado:', selectedInterval); // Debug

            if (!trades || trades.length === 0) {
                if (timeGroupedChart) timeGroupedChart.destroy();
                timeGroupedChart = null;
                return;
            }

            const groupedData = trades.reduce((acc, trade) => {
                const tradeTime = moment(trade.time);
                let roundedTime, key;
                
                if (selectedInterval === 1440) { // 1 dia
                    roundedTime = tradeTime.startOf('day');
                    key = roundedTime.format('YYYY-MM-DD');
                } else {
                    roundedTime = tradeTime.startOf('minute').subtract(tradeTime.minute() % selectedInterval, 'minutes');
                    key = roundedTime.format('YYYY-MM-DD HH:mm');
                }

                if (!acc[key]) {
                    acc[key] = { profit: 0 };
                }
                acc[key].profit += parseFloat(trade.profit);
                return acc;
            }, {});

            const sortedKeys = Object.keys(groupedData).sort((a, b) => {
                const formatA = selectedInterval === 1440 ? 'YYYY-MM-DD' : 'YYYY-MM-DD HH:mm';
                const formatB = selectedInterval === 1440 ? 'YYYY-MM-DD' : 'YYYY-MM-DD HH:mm';
                return moment(a, formatA).diff(moment(b, formatB));
            });

            const labels = sortedKeys.map(key => {
                if (selectedInterval === 1440) {
                    return moment(key, 'YYYY-MM-DD').format('DD/MM');
                } else {
                    return moment(key, 'YYYY-MM-DD HH:mm').format('HH:mm');
                }
            });
            const profits = sortedKeys.map(key => groupedData[key].profit);
            const backgroundColors = profits.map(p => p >= 0 ? 'rgba(40, 167, 69, 0.7)' : 'rgba(220, 53, 69, 0.7)');
            const borderColors = profits.map(p => p >= 0 ? 'rgba(40, 167, 69, 1)' : 'rgba(220, 53, 69, 1)');

            const ctx = document.getElementById('timeGroupedChart').getContext('2d');
            if (timeGroupedChart) {
                timeGroupedChart.data.labels = labels;
                timeGroupedChart.data.datasets[0].data = profits;
                timeGroupedChart.data.datasets[0].backgroundColor = backgroundColors;
                timeGroupedChart.data.datasets[0].borderColor = borderColors;
                timeGroupedChart.update();
            } else {
                timeGroupedChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: window.i18n ? window.i18n.t('consolidated_result_label') : 'Resultado Consolidado',
                            data: profits,
                            backgroundColor: backgroundColors,
                            borderColor: borderColors,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { callback: value => formatCurrency(value) }
                            }
                        },
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: (context) => `Resultado: ${formatCurrency(context.raw)}`
                                }
                            }
                        }
                    }
                });
            }
        }

        function detectChanges(data) {
            const newAccountHash = generateHash(data.account_info || {});
            const newTradesHash = generateHash(data.last_trades || []);
            const newBalanceHistoryHash = generateHash(data.balance_history || []);

            const changes = {
                hasChanges: false,
                accountInfoChanged: newAccountHash !== window.lastAccountHash,
                tradesChanged: newTradesHash !== window.lastTradesHash,
                balanceHistoryChanged: newBalanceHistoryHash !== window.lastBalanceHistoryHash
            };

            if (changes.accountInfoChanged) window.lastAccountHash = newAccountHash;
            if (changes.tradesChanged) window.lastTradesHash = newTradesHash;
            if (changes.balanceHistoryChanged) window.lastBalanceHistoryHash = newBalanceHistoryHash;

            changes.hasChanges = changes.accountInfoChanged || changes.tradesChanged || changes.balanceHistoryChanged;
            return changes;
        }

        function updateUI(data, changes) {
            // Atualizar informações básicas
            const accountInfo = data.account_info || {};
            document.getElementById('balance').textContent = formatCurrency(accountInfo.account_balance || 0);
            document.getElementById('equity').textContent = formatCurrency(accountInfo.account_equity || 0);
            
            // Usar o lucro do dia calculado pelos trades ao invés do account_profit
            // Considerar fuso horário do MT5 (+6 horas em relação ao PC local)
            const now = new Date();
            const todayLocal = moment().startOf('day');
            const todayMT5 = moment().add(6, 'hours').startOf('day'); // Dia no fuso do MT5
            
            console.log('=== DEBUG FUSO HORÁRIO ===');
            console.log('Hora local atual:', now.toString());
            console.log('Início do dia local:', todayLocal.format('YYYY-MM-DD HH:mm:ss'));
            console.log('Início do dia MT5:', todayMT5.format('YYYY-MM-DD HH:mm:ss'));
            
            const allTrades = data.last_trades || [];
            const tradesToday = allTrades.filter(trade => {
                if (!trade.time) return false;
                
                let tradeTime;
                if (typeof trade.time === 'string' && !trade.time.includes('T')) {
                    // Formato MT5: "YYYY.MM.DD HH:MM:SS" - ajustar para fuso local
                    const cleanTime = trade.time.replace(/\\./g, '-');
                    tradeTime = moment(cleanTime).subtract(6, 'hours'); // Converter MT5 para local
                } else {
                    tradeTime = moment(trade.time);
                }
                
                const isToday = tradeTime.isSame(todayLocal, 'day');
                
                if (isToday) {
                    console.log('Trade do dia encontrado:', {
                        original: trade.time,
                        converted: tradeTime.format('YYYY-MM-DD HH:mm:ss'),
                        profit: trade.profit,
                        symbol: trade.symbol
                    });
                }
                
                return isToday;
            });
            
            console.log('Total de trades encontrados para hoje:', tradesToday.length);
            console.log('=== FIM DEBUG FUSO ===');
            
            const profitToday = tradesToday.reduce((sum, trade) => sum + parseFloat(trade.profit || 0), 0);
            document.getElementById('profit').textContent = formatCurrency(profitToday);
            
            // Calcular e atualizar porcentagem do lucro/prejuízo
            updateProfitPercentage(profitToday, accountInfo.account_balance || 0);
            
            // Atualizar contadores de trades
            const positiveTradesToday = tradesToday.filter(trade => parseFloat(trade.profit || 0) > 0).length;
            const negativeTradesToday = tradesToday.filter(trade => parseFloat(trade.profit || 0) < 0).length;
            
            document.getElementById('trades-today').textContent = tradesToday.length;
            document.getElementById('trades-positive').textContent = `+${positiveTradesToday}`;
            document.getElementById('trades-negative').textContent = `-${negativeTradesToday}`;
            
            // Atualizar indicador de resultado do Equity - mostrar porcentagem do equity sobre saldo
            const equityResultElement = document.getElementById('equity-result-value');
            
            const currentEquity = accountInfo.account_equity || 0;
            const currentBalance = accountInfo.account_balance || 0;
            
            if (currentBalance > 0) {
                const equityPercentage = ((currentEquity / currentBalance) * 100);
                const percentageDiff = equityPercentage - 100; // Diferença em relação a 100%
                
                equityResultElement.textContent = `${equityPercentage.toFixed(2)}%`;
                
                // Aplicar cor baseada na porcentagem
                if (percentageDiff > 0) {
                    equityResultElement.className = 'badge bg-success';
                } else if (percentageDiff < 0) {
                    equityResultElement.className = 'badge bg-danger';
                } else {
                    equityResultElement.className = 'badge bg-secondary';
                }
            } else {
                equityResultElement.textContent = '0.00%';
                equityResultElement.className = 'badge bg-secondary';
            }
            
            // Atualizar card de Trades Abertos L/P (Equity - Balance)
            // Equity > Balance = Lucro (positivo)
            // Equity < Balance = Prejuízo (negativo)
            const openTradesProfit = currentEquity - currentBalance;
            const openTradesProfitElement = document.getElementById('open-trades-profit');
            const openTradesPercentageElement = document.getElementById('open-trades-percentage');
            
            openTradesProfitElement.textContent = formatCurrency(openTradesProfit);
            
            // Calcular porcentagem sobre o saldo
            if (currentBalance > 0) {
                const openTradesPercentage = (openTradesProfit / currentBalance) * 100;
                openTradesPercentageElement.textContent = `${openTradesPercentage.toFixed(2)}%`;
                
                // Aplicar cor baseada no valor
                if (openTradesProfit > 0) {
                    openTradesProfitElement.className = 'card-title fw-bold mb-1 text-success';
                    openTradesPercentageElement.className = 'badge bg-success';
                } else if (openTradesProfit < 0) {
                    openTradesProfitElement.className = 'card-title fw-bold mb-1 text-danger';
                    openTradesPercentageElement.className = 'badge bg-danger';
                } else {
                    openTradesProfitElement.className = 'card-title fw-bold mb-1 dark-mode-text';
                    openTradesPercentageElement.className = 'badge bg-secondary';
                }
            } else {
                openTradesPercentageElement.textContent = '0.00%';
                openTradesProfitElement.className = 'card-title fw-bold mb-1 dark-mode-text';
                openTradesPercentageElement.className = 'badge bg-secondary';
            }
            
            // Passar o lucro calculado para updateDailyMetrics
            updateDailyMetrics(accountInfo, profitToday);

            // --- Atualização da Tabela e Gráficos de Trades ---
            if (changes.tradesChanged) {
                const trades = data.last_trades || [];
                updateTradesTable(trades);
                createProfitChart(trades);
                createSymbolChart(trades);
                updateTimeGroupedChart(trades);
            }
            
            // --- Atualização de Trades Abertos (sempre usar dados simulados se API não tiver) ---
            let openTrades = data.open_trades || [];
            // Se API não retornar trades abertos, usar dados simulados
            if (openTrades.length === 0) {
                openTrades = window.simulatedOpenTrades || [];
                console.log('Usando dados simulados de trades abertos:', openTrades.length, 'trades');
            } else {
                console.log('Usando dados reais de trades abertos:', openTrades.length, 'trades');
            }
            updateOpenTrades(openTrades);

            // --- Atualização do Gráfico de Evolução ---
            if (changes.balanceHistoryChanged) {
                createEvolutionChart(data.balance_history || []);
            }
            
            // Os cálculos do dia já foram feitos na função updateData acima

            // --- Atualização do Timestamp ---
            const updateTime = data.timestamp ? new Date(data.timestamp) : new Date();
            document.getElementById('last-update').innerHTML = `<span data-i18n="last_update">${t('last_update')}</span> ${new Date().toLocaleTimeString()}`;
            const statusElement = document.getElementById('status');
            statusElement.innerHTML = '<div class="status-icon"></div><span data-i18n="connected_status">' + t('connected_status') + '</span>';
            statusElement.style.background = 'rgba(40, 167, 69, 0.3)';
        }

        function updateTradesTable(trades) {
            const tbody = document.getElementById('trades-tbody');
            if (!trades || trades.length === 0) {
                tbody.innerHTML = '<tr><td colspan="9" style="text-align: center;">Nenhum trade fechado encontrado</td></tr>';
                return;
            }

            // Limitar para apenas os 10 trades mais recentes
            const recentTrades = trades.slice(0, 50);

            tbody.innerHTML = '';
            recentTrades.forEach((trade, index) => {
                const row = tbody.insertRow();
                // Corrigir formato de data para moment.js
                const tradeTime = trade.time ? new Date(trade.time) : new Date();
                row.innerHTML = 
                    `<td>${index + 1}</td>` +
                    `<td>${trade.ticket}</td>` +
                    `<td>${moment(tradeTime).format('DD/MM/YY HH:mm:ss')}</td>` +
                    `<td><span style="color: ${trade.type === 'BUY' ? '#28a745' : '#dc3545'}">${trade.type}</span></td>` +
                    `<td>${trade.volume}</td>` +
                    `<td><strong>${trade.symbol}</strong></td>` +
                    `<td>${parseFloat(trade.price).toFixed(5)}</td>` +
                    `<td>${parseFloat(trade.close_price || 0).toFixed(5)}</td>` +
                    `<td class="${trade.profit >= 0 ? 'profit-positive' : 'profit-negative'}">${formatProfit(trade.profit)}</td>`;
            });
        }

        function updateOpenTrades(openTrades) {
            console.log('updateOpenTrades chamada com:', openTrades); // Debug
            const container = document.getElementById('open-trades-container');
            
            if (!openTrades || openTrades.length === 0) {
                console.log('Nenhum trade aberto encontrado'); // Debug
                container.innerHTML = `
                    <div class="text-center text-muted py-3">
                        <i class="fas fa-clock fa-2x mb-2"></i>
                        <p>Nenhum trade aberto no momento</p>
                    </div>
                `;
                return;
            }

            console.log('Renderizando', openTrades.length, 'trades abertos'); // Debug
            
            // Ordenar trades por lucro
            const sortedTrades = [...openTrades].sort((a, b) => {
                const profitA = parseFloat(a.profit || 0);
                const profitB = parseFloat(b.profit || 0);
                return sortTradesDescending ? profitB - profitA : profitA - profitB;
            });
            
            // Separar trades positivos e negativos para calcular porcentagens (usando profit_raw se disponível)
            const positiveTrades = sortedTrades.filter(trade => parseFloat(trade.profit_raw || trade.profit || 0) >= 0);
            const negativeTrades = sortedTrades.filter(trade => parseFloat(trade.profit_raw || trade.profit || 0) < 0);
            
            const totalPositiveProfit = positiveTrades.reduce((sum, trade) => sum + Math.abs(parseFloat(trade.profit_raw || trade.profit || 0)), 0);
            const totalNegativeProfit = negativeTrades.reduce((sum, trade) => sum + Math.abs(parseFloat(trade.profit_raw || trade.profit || 0)), 0);
            
            container.innerHTML = '';
            sortedTrades.forEach((trade, index) => {
                // Usar profit_raw se disponível, senão usar profit
            const profit = parseFloat(trade.profit_raw || trade.profit || 0);
                const isPositive = profit >= 0;
                const absProfit = Math.abs(profit);
                
                // Calcular porcentagem em relação ao grupo (positivo ou negativo)
                let percentage = 0;
                if (isPositive && totalPositiveProfit > 0) {
                    percentage = (absProfit / totalPositiveProfit) * 100;
                } else if (!isPositive && totalNegativeProfit > 0) {
                    percentage = (absProfit / totalNegativeProfit) * 100;
                }
                
                const tradeItem = document.createElement('div');
                tradeItem.className = 'open-trade-item';
                tradeItem.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div>
                            <strong>${trade.symbol}</strong>
                            <span class="badge ${trade.type === 'BUY' ? 'bg-success' : 'bg-danger'} ms-2">${trade.type}</span>
                            <div style="font-size: 1rem; color: #6c757d; margin-top: .50px; text-align: left;">
                                ${calculateOpenTime(trade.open_time)}
                            </div>
                        </div>
                        <div class="text-end">
                            <div class="fw-bold ${isPositive ? 'text-success' : 'text-danger'}">
                                ${formatProfit(profit)}
                            </div>
                            <button class="btn btn-outline-danger btn-sm mt-1 close-individual-btn" 
                                    data-ticket="${trade.ticket}" 
                                    title="Fechar esta ordem">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <div class="trade-progress-bar flex-grow-1 me-2">
                            <div class="trade-progress-fill ${isPositive ? 'trade-profit-positive' : 'trade-profit-negative'}" 
                                 style="width: ${percentage}%"></div>
                        </div>
                        <small class="fw-bold ${isPositive ? 'text-success' : 'text-danger'}">
                            ${percentage.toFixed(1)}%
                        </small>
                    </div>
                `;
                container.appendChild(tradeItem);
            });
        }

        function updateData() {
            if (isUpdating) return;
            isUpdating = true;
            
            const startTime = performance.now();
            console.log(`[${new Date().toLocaleTimeString()}] Iniciando requisição...`);

            Promise.all([
                fetch('/api/latest').then(r => {
                    if (r.status === 401 || r.status === 403) {
                        return r.json().then(data => {
                            throw new Error(data.code || 'UNAUTHORIZED');
                        });
                    }
                    return r.json();
                }),
                fetch('/api/balance-history').then(r => {
                    if (r.status === 401 || r.status === 403) {
                        return r.json().then(data => {
                            throw new Error(data.code || 'UNAUTHORIZED');
                        });
                    }
                    return r.json();
                })
            ])
            .then(([latest, history]) => {
                const fetchTime = performance.now();
                console.log(`[${new Date().toLocaleTimeString()}] Requisições completadas em ${(fetchTime - startTime).toFixed(2)}ms`);
                
                const data = { ...latest, balance_history: history.balance_history };
                
                // Armazena dados para acesso global
                window.lastApiData = data;
                cachedTradesData = data.last_trades || [];
                cachedBalanceHistory = data.balance_history || [];

                const changes = detectChanges(data);
                console.log(`[${new Date().toLocaleTimeString()}] Hash check - Account: ${changes.accountInfoChanged}, Trades: ${changes.tradesChanged}, Balance: ${changes.balanceHistoryChanged}`);
                
                if (changes.hasChanges) {
                    console.log(`[${new Date().toLocaleTimeString()}] Atualizando UI - mudanças detectadas`);
                    updateUI(data, changes);
                    const uiTime = performance.now();
                    console.log(`[${new Date().toLocaleTimeString()}] UI atualizada em ${(uiTime - fetchTime).toFixed(2)}ms`);
                } else {
                    console.log(`[${new Date().toLocaleTimeString()}] Nenhuma mudança detectada - UI não atualizada`);
                    // FORÇA ATUALIZAÇÃO A CADA 10 CICLOS MESMO SEM MUDANÇAS
                    window.forceUpdateCounter = (window.forceUpdateCounter || 0) + 1;
                    if (window.forceUpdateCounter >= 10) {
                        console.log(`[${new Date().toLocaleTimeString()}] FORÇANDO atualização após 10 ciclos sem mudanças`);
                        updateUI(data, {hasChanges: true, accountInfoChanged: true, tradesChanged: true, balanceHistoryChanged: true});
                        window.forceUpdateCounter = 0;
                    }
                }
            })
            .catch(error => {
                // Verifica se é erro de autenticação
                if (error.message === 'SESSION_INVALIDATED' || error.message === 'NOT_AUTHENTICATED' || error.message === 'NOT_APPROVED') {
                    console.error('❌ Sessão invalidada - parando requisições e redirecionando...');
                    
                    // Para todas as requisições
                    if (updateInterval) {
                        clearInterval(updateInterval);
                        updateInterval = null;
                    }
                    
                    // Redireciona para login após 1 segundo
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 1000);
                    
                    return;
                }
                
                console.error('Erro ao buscar dados:', error);
                const statusElement = document.getElementById('status');
                statusElement.innerHTML = '<div class="status-icon"></div><span data-i18n="disconnected_status">' + t('disconnected_status') + '</span>';
                statusElement.style.background = 'rgba(220, 53, 69, 0.3)';
            })
            .finally(() => {
                const totalTime = performance.now();
                console.log(`[${new Date().toLocaleTimeString()}] Ciclo completo em ${(totalTime - startTime).toFixed(2)}ms`);
                isUpdating = false;
            });
        }

        function setupUpdateFrequency() {
            const frequencySelector = document.getElementById('update-frequency');
            
            // Define frequência inicial (0.5 segundos)
            frequencySelector.value = currentUpdateFrequency;
            
            // Event listener para mudança de frequência
            frequencySelector.addEventListener('change', function() {
                currentUpdateFrequency = parseInt(this.value);
                
                // Limpa o interval anterior
                if (updateInterval) {
                    clearInterval(updateInterval);
                }
                
                // Define novo interval
                updateInterval = setInterval(updateData, currentUpdateFrequency);
                
                console.log(`Frequência de atualização alterada para: ${currentUpdateFrequency}ms`);
            });
        }

        // Função para fechar ordens via API
        async function closeOrders(type, ticket = null) {
            try {
                let endpoint = '';
                let body = {};
                
                switch(type) {
                    case 'all':
                        endpoint = '/api/close-all-orders';
                        break;
                    case 'positive':
                        endpoint = '/api/close-positive-orders';
                        break;
                    case 'negative':
                        endpoint = '/api/close-negative-orders';
                        break;
                    case 'individual':
                        endpoint = '/api/close-order';
                        body = { ticket: ticket };
                        break;
                    default:
                        throw new Error('Tipo de fechamento inválido');
                }
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(body)
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    // Mostrar notificação de sucesso
                    showNotification(result.message, 'success');
                    // Atualizar dados após um pequeno delay
                    setTimeout(updateData, 1000);
                } else {
                    showNotification(result.message || 'Erro ao fechar ordem(s)', 'error');
                }
                
            } catch (error) {
                console.error('Erro ao fechar ordem(s):', error);
                showNotification('Erro de conexão ao tentar fechar ordem(s)', 'error');
            }
        }
        
        // Função para mostrar notificações
        function showNotification(message, type = 'info') {
            // Criar elemento de notificação
            const notification = document.createElement('div');
            notification.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} alert-dismissible fade show position-fixed`;
            notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            notification.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.body.appendChild(notification);
            
            // Remover automaticamente após 5 segundos
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 5000);
        }

        document.addEventListener('DOMContentLoaded', function () {
            // Inicializa hashes para detecção de mudanças
            window.lastAccountHash = '';
            window.lastTradesHash = '';
            window.lastBalanceHistoryHash = '';

            setupGoalAndLimitControls();
            setupUpdateFrequency();
            
            // Define dados simulados globalmente para persistir entre atualizações
            window.simulatedOpenTrades = [
                {
                    'ticket': '123456789',
                    'symbol': 'EURUSD',
                    'type': 'BUY',
                    'volume': 0.10,
                    'price': 1.0850,
                    'profit': 15.50
                },
                {
                    'ticket': '123456790',
                    'symbol': 'GBPUSD',
                    'type': 'SELL',
                    'volume': 0.05,
                    'price': 1.2650,
                    'profit': -8.20
                },
                {
                    'ticket': '123456791',
                    'symbol': 'USDJPY',
                    'type': 'BUY',
                    'volume': 0.08,
                    'price': 149.25,
                    'profit': 22.80
                }
            ];
            
            // Chama diretamente para testar
            console.log('Testando trades abertos diretamente...');
            updateOpenTrades(window.simulatedOpenTrades);
            
            // Inicializa tema
            initializeTheme();
            
            // Event listener para botão de ordenação
            document.getElementById('sort-trades-btn').addEventListener('click', function() {
                sortTradesDescending = !sortTradesDescending;
                const icon = document.getElementById('sort-icon');
                icon.className = sortTradesDescending ? 'fas fa-sort-amount-down' : 'fas fa-sort-amount-up';
                
                // Re-renderiza os trades com nova ordenação
                if (window.lastApiData && window.lastApiData.open_trades) {
                    updateOpenTrades(window.lastApiData.open_trades);
                }
            });
            
            // Event listeners para botões de fechamento de ordens
            document.getElementById('close-all-btn').addEventListener('click', function() {
                if (confirm(window.i18n ? window.i18n.t('confirm_close_all') : 'Tem certeza que deseja fechar TODAS as ordens abertas?')) {
                    closeOrders('all');
                }
            });
            
            document.getElementById('close-positive-btn').addEventListener('click', function() {
                if (confirm(window.i18n ? window.i18n.t('confirm_close_positive') : 'Tem certeza que deseja fechar todas as ordens POSITIVAS?')) {
                    closeOrders('positive');
                }
            });
            
            document.getElementById('close-negative-btn').addEventListener('click', function() {
                if (confirm(window.i18n ? window.i18n.t('confirm_close_negative') : 'Tem certeza que deseja fechar todas as ordens NEGATIVAS?')) {
                    closeOrders('negative');
                }
            });
            
            // Event listener para botões individuais (delegação de eventos)
            document.addEventListener('click', function(e) {
                if (e.target.closest('.close-individual-btn')) {
                    const button = e.target.closest('.close-individual-btn');
                    const ticket = button.getAttribute('data-ticket');
                    if (confirm((window.i18n ? window.i18n.t('confirm_close_individual') : 'Tem certeza que deseja fechar a ordem #') + ticket + '?')) {
                        closeOrders('individual', ticket);
                    }
                }
            });
            
            updateData();
            
            // Inicia com a frequência padrão
            updateInterval = setInterval(updateData, currentUpdateFrequency);

            document.getElementById('time-group-selector').addEventListener('change', function() {
                console.log('Seletor alterado para:', this.value); // Debug
                if (cachedTradesData && cachedTradesData.length > 0) {
                    updateTimeGroupedChart(cachedTradesData);
                } else {
                    console.log('Nenhum dado de trade em cache para atualizar o gráfico');
                }
            });
        });
        
        // Função para alternar tema
        function toggleTheme() {
            const body = document.body;
            const themeIcon = document.getElementById('theme-icon');
            
            body.classList.toggle('dark-mode');
            
            if (body.classList.contains('dark-mode')) {
                themeIcon.className = 'fas fa-sun';
                localStorage.setItem('theme', 'dark');
            } else {
                themeIcon.className = 'fas fa-moon';
                localStorage.setItem('theme', 'light');
            }
        }
        
        // Função para logout
        function logout() {
            if (confirm(window.i18n ? window.i18n.t('confirm_logout') : 'Tem certeza que deseja sair?')) {
                window.location.href = '/logout';
            }
        }
        
        // ==================== GRÁFICOS AVANÇADOS ====================
        
        let priceChartAdvanced = null;
        let zscoreChartGlobal = null;
        let rsiChartGlobal = null;
        let currentChartSymbol = 'XAUUSD';
        let chartUpdateInterval = null;
        
        // Verificar se há dados suficientes
        async function checkDataAvailability(symbol) {
            try {
                const response = await fetch(`/api/price-history/${symbol}`);
                const data = await response.json();
                return data.data && data.data.length >= 300; // Precisa de pelo menos 300 pontos
            } catch (error) {
                return false;
            }
        }
        
        // Mostrar/ocultar barra de progresso
        function showLoadingBar() {
            const loadingBar = document.getElementById('data-loading-bar');
            const progressFill = document.getElementById('progress-bar-fill');
            
            if (loadingBar) {
                loadingBar.style.display = 'block';
                
                // Resetar animação
                progressFill.style.animation = 'none';
                setTimeout(() => {
                    progressFill.style.animation = 'progressAnimation 2s linear infinite, fillProgress 120s linear forwards';
                }, 10);
                
                // Esconder após 2 minutos
                setTimeout(() => {
                    loadingBar.style.display = 'none';
                }, 120000); // 120 segundos = 2 minutos
            }
        }
        
        function hideLoadingBar() {
            const loadingBar = document.getElementById('data-loading-bar');
            if (loadingBar) {
                loadingBar.style.display = 'none';
            }
        }
        
        // Função para abrir modal de gráficos
        async function openAdvancedChart() {
            const modal = document.getElementById('advanced-chart-modal');
            modal.style.display = 'block';
            
            // Verificar se há dados suficientes
            const hasEnoughData = await checkDataAvailability(currentChartSymbol);
            
            if (!hasEnoughData) {
                // Mostrar barra de progresso se não houver dados suficientes
                showLoadingBar();
            } else {
                // Esconder barra se já houver dados
                hideLoadingBar();
            }
            
            // Inicializar gráficos
            setTimeout(() => {
                initializeAdvancedCharts();
                startChartUpdates();
            }, 100);
        }
        
        // Função para fechar modal de gráficos
        function closeAdvancedChart() {
            const modal = document.getElementById('advanced-chart-modal');
            modal.style.display = 'none';
            
            // Parar atualizações
            if (chartUpdateInterval) {
                clearInterval(chartUpdateInterval);
                chartUpdateInterval = null;
            }
        }
        
        // Inicializar gráficos avançados
        async function initializeAdvancedCharts() {
            try {
                const priceResponse = await fetch(`/api/price-history/${currentChartSymbol}`);
                const priceData = await priceResponse.json();
                
                // Obter períodos dos sliders
                const hullPeriod = document.getElementById('hull-period')?.value || 20;
                const zscorePeriod = document.getElementById('zscore-period')?.value || 20;
                const rsiPeriod = document.getElementById('rsi-period')?.value || 14;
                
                const indicatorResponse = await fetch(`/api/indicators/${currentChartSymbol}?hull_period=${hullPeriod}&zscore_period=${zscorePeriod}&rsi_period=${rsiPeriod}`);
                const indicatorData = await indicatorResponse.json();
                
                createPriceChartAdvanced(priceData, indicatorData);
                createZScoreChart(indicatorData);
                
                // Atualizar gráfico de RSI se necessário
                const rsiCheckbox = document.getElementById('ind-rsi');
                if (rsiCheckbox && rsiCheckbox.checked) {
                    document.getElementById('rsi-section').style.display = 'block';
                    createRSIChart(indicatorData);
                }
                
                console.log('[CHARTS] Gráficos inicializados');
            } catch (error) {
                console.error('[CHARTS] Erro:', error);
            }
        }
        
        // Criar gráfico de preço
        function createPriceChartAdvanced(priceData, indicatorData) {
            const ctx = document.getElementById('priceChartAdvanced').getContext('2d');
            
            if (!priceData.data || priceData.data.length === 0) {
                console.warn('[CHARTS] Sem dados de preço');
                return;
            }
            
            const labels = priceData.data.map(p => moment(p.timestamp).format('HH:mm:ss'));
            const prices = priceData.data.map(p => p.price);
            
            // Criar array de cores baseado no Z-Score
            let borderColors = [];
            let backgroundColors = [];
            
            if (indicatorData.data && indicatorData.data.zscore) {
                const zscores = indicatorData.data.zscore;
                for (let i = 0; i < prices.length; i++) {
                    const zscore = zscores[i] || 0;
                    if (zscore >= 0) {
                        borderColors.push('#4caf50');  // Verde
                        backgroundColors.push('rgba(76, 175, 80, 0.1)');
                    } else {
                        borderColors.push('#f44336');  // Vermelho
                        backgroundColors.push('rgba(244, 67, 54, 0.1)');
                    }
                }
            } else {
                // Fallback: azul se não houver Z-Score
                borderColors = Array(prices.length).fill('#4fc3f7');
                backgroundColors = Array(prices.length).fill('rgba(79, 195, 247, 0.1)');
            }
            
            // Verificar se deve mostrar pontos
            const showPoints = document.getElementById('show-points') && document.getElementById('show-points').checked;
            
            const datasets = [{
                label: 'Price',
                data: prices,
                borderColor: [...borderColors],  // Cópia do array
                backgroundColor: 'transparent',
                borderWidth: 2,
                fill: false,
                tension: 0.4,
                pointRadius: showPoints ? 3 : 0,
                pointHoverRadius: showPoints ? 5 : 0,
                pointBackgroundColor: [...borderColors],  // Cópia do array
                pointBorderColor: [...borderColors],  // Cópia do array
                segment: {
                    borderColor: (ctx) => {
                        const idx = ctx.p0DataIndex;
                        const dataset = ctx.chart.data.datasets[ctx.datasetIndex];
                        return dataset.borderColor[idx] || '#4fc3f7';
                    }
                }
            }];
            
            if (document.getElementById('ind-hull').checked && indicatorData.data && indicatorData.data.hull_ma) {
                datasets.push({
                    label: 'Hull MA',
                    data: indicatorData.data.hull_ma,
                    borderColor: '#4caf50',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,  // Sempre sem pontos
                    pointHoverRadius: 0  // Sem pontos ao passar mouse
                });
            }
            
            if (priceChartAdvanced) priceChartAdvanced.destroy();
            
            priceChartAdvanced = new Chart(ctx, {
                type: 'line',
                data: { labels: labels, datasets: datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 300 },
                    interaction: { intersect: false, mode: 'index' },
                    scales: {
                        x: {
                            display: true,
                            title: { display: true, text: 'Tempo', color: '#aaa' },
                            ticks: { color: '#aaa', maxTicksLimit: 15 },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        y: {
                            display: true,
                            title: { display: true, text: 'Price', color: '#aaa' },
                            ticks: { callback: function(value) { return value.toFixed(2); }, color: '#aaa' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        }
                    },
                    plugins: {
                        legend: { display: true, position: 'top', labels: { color: '#aaa', usePointStyle: true } },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: 'rgba(76, 175, 80, 0.5)',
                            borderWidth: 1
                        }
                    }
                }
            });
            
            if (prices.length > 0) {
                document.getElementById('chart-last-price').textContent = prices[prices.length - 1].toFixed(2);
            }
        }
        
        // Criar gráfico de Z-Score
        function createZScoreChart(indicatorData) {
            const ctx = document.getElementById('zscoreChart').getContext('2d');
            
            if (!indicatorData.data || !indicatorData.data.zscore || indicatorData.data.zscore.length === 0) {
                console.warn('[CHARTS] Sem dados de Z-Score');
                return;
            }
            
            const labels = indicatorData.data.timestamps.map(t => moment(t).format('HH:mm:ss'));
            const zscores = indicatorData.data.zscore;
            
            if (zscoreChartGlobal) zscoreChartGlobal.destroy();
            
            zscoreChartGlobal = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Real Volatility',
                        data: zscores,
                        borderColor: '#4caf50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 300 },
                    interaction: { intersect: false, mode: 'index' },
                    scales: {
                        x: {
                            display: true,
                            ticks: { color: '#aaa', maxTicksLimit: 15 },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        y: {
                            display: true,
                            title: { display: true, text: 'Real Volatility', color: '#aaa' },
                            ticks: { color: '#aaa' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: 'rgba(76, 175, 80, 0.5)',
                            borderWidth: 1
                        },
                        annotation: {
                            annotations: {
                                zeroLine: {
                                    type: 'line',
                                    yMin: 0,
                                    yMax: 0,
                                    borderColor: 'rgba(255, 255, 255, 0.5)',
                                    borderWidth: 2,
                                    borderDash: [5, 5],
                                    label: {
                                        content: '0',
                                        enabled: true,
                                        position: 'end',
                                        backgroundColor: 'rgba(255, 255, 255, 0.8)',
                                        color: '#000'
                                    }
                                }
                            }
                        }
                    }
                }
            });
            
            if (zscores.length > 0) {
                const lastZScore = zscores[zscores.length - 1];
                document.getElementById('chart-zscore-value').textContent = lastZScore ? lastZScore.toFixed(4) : '-';
            }
        }
        
        // Criar gráfico de RSI
        function createRSIChart(indicatorData) {
            const ctx = document.getElementById('rsiChart').getContext('2d');
            
            if (!indicatorData.data || !indicatorData.data.rsi || indicatorData.data.rsi.length === 0) {
                console.warn('[CHARTS] Sem dados de RSI');
                return;
            }
            
            const labels = indicatorData.data.timestamps.map(t => moment(t).format('HH:mm:ss'));
            const rsiValues = indicatorData.data.rsi;
            
            if (rsiChartGlobal) rsiChartGlobal.destroy();
            
            rsiChartGlobal = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'RSI',
                        data: rsiValues,
                        borderColor: '#9c27b0',
                        backgroundColor: 'rgba(156, 39, 176, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 300 },
                    interaction: { intersect: false, mode: 'index' },
                    scales: {
                        x: {
                            display: true,
                            ticks: { color: '#aaa', maxTicksLimit: 15 },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        y: {
                            display: true,
                            title: { display: true, text: 'RSI', color: '#aaa' },
                            min: 0,
                            max: 100,
                            ticks: { color: '#aaa' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0,0,0,0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: 'rgba(156, 39, 176, 0.5)',
                            borderWidth: 1
                        },
                        annotation: {
                            annotations: {
                                overbought: {
                                    type: 'line',
                                    yMin: 70,
                                    yMax: 70,
                                    borderColor: 'rgba(244, 67, 54, 0.7)',
                                    borderWidth: 2,
                                    borderDash: [5, 5],
                                    label: {
                                        content: '70 (Overbought)',
                                        enabled: true,
                                        position: 'end',
                                        backgroundColor: 'rgba(244, 67, 54, 0.8)',
                                        color: '#fff'
                                    }
                                },
                                oversold: {
                                    type: 'line',
                                    yMin: 20,
                                    yMax: 20,
                                    borderColor: 'rgba(76, 175, 80, 0.7)',
                                    borderWidth: 2,
                                    borderDash: [5, 5],
                                    label: {
                                        content: '20 (Oversold)',
                                        enabled: true,
                                        position: 'end',
                                        backgroundColor: 'rgba(76, 175, 80, 0.8)',
                                        color: '#fff'
                                    }
                                }
                            }
                        }
                    }
                }
            });
            
            if (rsiValues.length > 0) {
                const lastRSI = rsiValues[rsiValues.length - 1];
                document.getElementById('chart-rsi-value').textContent = lastRSI ? lastRSI.toFixed(2) : '-';
            }
        }
        
        // Variável para controle de frequência de atualização dos gráficos
        let chartUpdateFrequency = 5000; // Padrão: 5 segundos
        
        // Iniciar atualizações automáticas
        function startChartUpdates() {
            // Parar intervalo existente se houver
            if (chartUpdateInterval) {
                clearInterval(chartUpdateInterval);
            }
            
            chartUpdateInterval = setInterval(async () => {
                try {
                    await updateAdvancedCharts();
                } catch (error) {
                    console.error('[CHARTS] Erro ao atualizar:', error);
                }
            }, chartUpdateFrequency);
        }
        
        // Atualizar gráficos
        async function updateAdvancedCharts() {
            try {
                const priceResponse = await fetch(`/api/price-history/${currentChartSymbol}`);
                const priceData = await priceResponse.json();
                
                // Obter períodos dos sliders
                const hullPeriod = document.getElementById('hull-period')?.value || 20;
                const zscorePeriod = document.getElementById('zscore-period')?.value || 20;
                const rsiPeriod = document.getElementById('rsi-period')?.value || 14;
                
                const indicatorResponse = await fetch(`/api/indicators/${currentChartSymbol}?hull_period=${hullPeriod}&zscore_period=${zscorePeriod}&rsi_period=${rsiPeriod}`);
                const indicatorData = await indicatorResponse.json();
                
                if (priceChartAdvanced && priceData.data && priceData.data.length > 0) {
                    const labels = priceData.data.map(p => moment(p.timestamp).format('HH:mm:ss'));
                    const prices = priceData.data.map(p => p.price);
                    
                    // Atualizar cores baseadas no Z-Score
                    let borderColors = [];
                    let backgroundColors = [];
                    
                    if (indicatorData.data && indicatorData.data.zscore) {
                        const zscores = indicatorData.data.zscore;
                        for (let i = 0; i < prices.length; i++) {
                            const zscore = zscores[i] || 0;
                            if (zscore >= 0) {
                                borderColors.push('#4caf50');  // Verde
                                backgroundColors.push('rgba(76, 175, 80, 0.1)');
                            } else {
                                borderColors.push('#f44336');  // Vermelho
                                backgroundColors.push('rgba(244, 67, 54, 0.1)');
                            }
                        }
                    } else {
                        borderColors = Array(prices.length).fill('#4fc3f7');
                        backgroundColors = Array(prices.length).fill('rgba(79, 195, 247, 0.1)');
                    }
                    
                    priceChartAdvanced.data.labels = labels;
                    priceChartAdvanced.data.datasets[0].data = prices;
                    
                    // Verificar se deve mostrar pontos
                    const showPoints = document.getElementById('show-points') && document.getElementById('show-points').checked;
                    priceChartAdvanced.data.datasets[0].pointRadius = showPoints ? 3 : 0;
                    priceChartAdvanced.data.datasets[0].pointHoverRadius = showPoints ? 5 : 0;
                    
                    // Limpar e reconstruir arrays de cores (in-place)
                    priceChartAdvanced.data.datasets[0].pointBackgroundColor.length = 0;
                    priceChartAdvanced.data.datasets[0].pointBorderColor.length = 0;
                    priceChartAdvanced.data.datasets[0].borderColor.length = 0;
                    
                    borderColors.forEach(color => {
                        priceChartAdvanced.data.datasets[0].pointBackgroundColor.push(color);
                        priceChartAdvanced.data.datasets[0].pointBorderColor.push(color);
                        priceChartAdvanced.data.datasets[0].borderColor.push(color);
                    });
                    
                    // Atualizar Hull MA se ativado
                    if (document.getElementById('ind-hull').checked && indicatorData.data && indicatorData.data.hull_ma) {
                        if (priceChartAdvanced.data.datasets.length > 1) {
                            priceChartAdvanced.data.datasets[1].data = indicatorData.data.hull_ma;
                        }
                    }
                    
                    priceChartAdvanced.update('active');
                    
                    document.getElementById('chart-last-price').textContent = prices[prices.length - 1].toFixed(2);
                    
                    // Atualizar Hull MA value
                    if (indicatorData.data && indicatorData.data.hull_ma && indicatorData.data.hull_ma.length > 0) {
                        const lastHull = indicatorData.data.hull_ma[indicatorData.data.hull_ma.length - 1];
                        document.getElementById('chart-hull-value').textContent = lastHull ? lastHull.toFixed(2) : '-';
                    }
                    
                    document.getElementById('chart-last-update').textContent = moment().format('HH:mm:ss');
                }
                
                if (zscoreChartGlobal && indicatorData.data && indicatorData.data.zscore) {
                    const labels = indicatorData.data.timestamps.map(t => moment(t).format('HH:mm:ss'));
                    zscoreChartGlobal.data.labels = labels;
                    zscoreChartGlobal.data.datasets[0].data = indicatorData.data.zscore;
                    zscoreChartGlobal.update('none');
                    
                    const lastZScore = indicatorData.data.zscore[indicatorData.data.zscore.length - 1];
                    document.getElementById('chart-zscore-value').textContent = lastZScore ? lastZScore.toFixed(4) : '-';
                }
                
                // Atualizar RSI se ativado
                if (rsiChartGlobal && document.getElementById('ind-rsi').checked && indicatorData.data && indicatorData.data.rsi) {
                    const labels = indicatorData.data.timestamps.map(t => moment(t).format('HH:mm:ss'));
                    rsiChartGlobal.data.labels = labels;
                    rsiChartGlobal.data.datasets[0].data = indicatorData.data.rsi;
                    rsiChartGlobal.update('none');
                    
                    const lastRSI = indicatorData.data.rsi[indicatorData.data.rsi.length - 1];
                    document.getElementById('chart-rsi-value').textContent = lastRSI ? lastRSI.toFixed(2) : '-';
                }
                
            } catch (error) {
                console.error('[CHARTS] Erro ao atualizar:', error);
            }
        }
        
        // Salvar configurações no localStorage
        function saveChartSettings() {
            const settings = {
                symbol: currentChartSymbol,
                hullPeriod: document.getElementById('hull-period')?.value || 20,
                zscorePeriod: document.getElementById('zscore-period')?.value || 20,
                rsiPeriod: document.getElementById('rsi-period')?.value || 14,
                hullEnabled: document.getElementById('ind-hull')?.checked || false,
                zscoreEnabled: document.getElementById('ind-zscore')?.checked || false,
                rsiEnabled: document.getElementById('ind-rsi')?.checked || false,
                showPoints: document.getElementById('show-points')?.checked || false
            };
            localStorage.setItem('chartSettings', JSON.stringify(settings));
            console.log('[CHARTS] Configurações salvas:', settings);
        }
        
        // Carregar configurações do localStorage
        function loadChartSettings() {
            const saved = localStorage.getItem('chartSettings');
            if (saved) {
                try {
                    const settings = JSON.parse(saved);
                    console.log('[CHARTS] Configurações carregadas:', settings);
                    
                    // Restaurar símbolo
                    if (settings.symbol) {
                        currentChartSymbol = settings.symbol;
                        const dropdown = document.getElementById('symbol-dropdown');
                        if (dropdown) {
                            // Tentar selecionar no dropdown
                            const option = Array.from(dropdown.options).find(opt => opt.value === settings.symbol);
                            if (option) {
                                dropdown.value = settings.symbol;
                            } else {
                                // Se não estiver no dropdown, colocar no input customizado
                                const customInput = document.getElementById('custom-symbol-input');
                                if (customInput) customInput.value = settings.symbol;
                            }
                        }
                    }
                    
                    // Restaurar períodos
                    if (settings.hullPeriod) {
                        const hullSlider = document.getElementById('hull-period');
                        const hullValue = document.getElementById('hull-period-value');
                        if (hullSlider) hullSlider.value = settings.hullPeriod;
                        if (hullValue) hullValue.textContent = settings.hullPeriod;
                    }
                    if (settings.zscorePeriod) {
                        const zscoreSlider = document.getElementById('zscore-period');
                        const zscoreValue = document.getElementById('zscore-period-value');
                        if (zscoreSlider) zscoreSlider.value = settings.zscorePeriod;
                        if (zscoreValue) zscoreValue.textContent = settings.zscorePeriod;
                    }
                    if (settings.rsiPeriod) {
                        const rsiSlider = document.getElementById('rsi-period');
                        const rsiValue = document.getElementById('rsi-period-value');
                        if (rsiSlider) rsiSlider.value = settings.rsiPeriod;
                        if (rsiValue) rsiValue.textContent = settings.rsiPeriod;
                    }
                    
                    // Restaurar checkboxes
                    if (document.getElementById('ind-hull')) document.getElementById('ind-hull').checked = settings.hullEnabled;
                    if (document.getElementById('ind-zscore')) document.getElementById('ind-zscore').checked = settings.zscoreEnabled;
                    if (document.getElementById('ind-rsi')) document.getElementById('ind-rsi').checked = settings.rsiEnabled;
                    if (document.getElementById('show-points')) document.getElementById('show-points').checked = settings.showPoints;
                    
                } catch (e) {
                    console.error('[CHARTS] Erro ao carregar configurações:', e);
                }
            }
        }
        
        // Event listeners para checkboxes e sliders
        document.addEventListener('DOMContentLoaded', function() {
            // Carregar configurações salvas
            loadChartSettings();
            
            // Carregar frequência de atualização salva
            const savedFrequency = localStorage.getItem('chartUpdateFrequency');
            if (savedFrequency) {
                chartUpdateFrequency = parseInt(savedFrequency);
                const frequencySelect = document.getElementById('chart-update-frequency');
                if (frequencySelect) {
                    frequencySelect.value = savedFrequency;
                }
            }
            
            // Dropdown de símbolos
            const symbolDropdown = document.getElementById('symbol-dropdown');
            if (symbolDropdown) {
                symbolDropdown.addEventListener('change', function() {
                    if (this.value) {
                        currentChartSymbol = this.value;
                        console.log(`[CHARTS] Mudando para símbolo: ${currentChartSymbol}`);
                        saveChartSettings();
                        
                        if (document.getElementById('advanced-chart-modal').style.display === 'block') {
                            initializeAdvancedCharts();
                        }
                    }
                });
            }
            
            // Símbolo customizado
            const customSymbolInput = document.getElementById('custom-symbol-input');
            const loadCustomBtn = document.getElementById('load-custom-symbol');
            
            if (loadCustomBtn && customSymbolInput) {
                loadCustomBtn.addEventListener('click', function() {
                    const customSymbol = customSymbolInput.value.trim().toUpperCase();
                    if (customSymbol) {
                        currentChartSymbol = customSymbol;
                        console.log(`[CHARTS] Carregando símbolo customizado: ${customSymbol}`);
                        
                        // Limpar dropdown
                        if (symbolDropdown) symbolDropdown.value = '';
                        
                        saveChartSettings();
                        
                        if (document.getElementById('advanced-chart-modal').style.display === 'block') {
                            initializeAdvancedCharts();
                        }
                    }
                });
                
                // Enter no input também carrega
                customSymbolInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        loadCustomBtn.click();
                    }
                });
            }
            
            // Controle de frequência de atualização dos gráficos
            const frequencySelect = document.getElementById('chart-update-frequency');
            if (frequencySelect) {
                frequencySelect.addEventListener('change', function() {
                    const newFrequency = parseInt(this.value);
                    chartUpdateFrequency = newFrequency;
                    
                    // Salvar no localStorage
                    localStorage.setItem('chartUpdateFrequency', newFrequency);
                    
                    console.log(`[CHARTS] Frequência de atualização alterada para: ${newFrequency}ms`);
                    
                    // Reiniciar atualizações com nova frequência
                    if (document.getElementById('advanced-chart-modal').style.display === 'block') {
                        startChartUpdates();
                    }
                });
            }
            
            // Checkboxes de indicadores
            const sliders = [
                { id: 'hull-period', valueId: 'hull-period-value' },
                { id: 'zscore-period', valueId: 'zscore-period-value' },
                { id: 'rsi-period', valueId: 'rsi-period-value' }
            ];
            
            sliders.forEach(slider => {
                const sliderElement = document.getElementById(slider.id);
                const valueElement = document.getElementById(slider.valueId);
                
                if (sliderElement && valueElement) {
                    // Atualizar valor exibido ao mover slider
                    sliderElement.addEventListener('input', function() {
                        valueElement.textContent = this.value;
                    });
                    
                    // Recalcular indicadores ao soltar slider
                    sliderElement.addEventListener('change', function() {
                        if (document.getElementById('advanced-chart-modal').style.display === 'block') {
                            console.log(`[CHARTS] Período alterado: ${slider.id} = ${this.value}`);
                            initializeAdvancedCharts();
                        }
                        // Salvar configurações
                        saveChartSettings();
                    });
                }
            });
        });
        
        // Fechar modal ao clicar fora
        window.addEventListener('click', function(event) {
            const modal = document.getElementById('advanced-chart-modal');
            if (event.target == modal) {
                closeAdvancedChart();
            }
        });
        
        // ==================== FIM GRÁFICOS AVANÇADOS ====================
    
        // Inicializar tema escuro como padrão
        document.addEventListener('DOMContentLoaded', function() {
            const savedTheme = localStorage.getItem('theme');
            if (!savedTheme) {
                localStorage.setItem('theme', 'dark');
                document.getElementById('theme-icon').className = 'fas fa-sun';
            } else if (savedTheme === 'dark') {
                document.getElementById('theme-icon').className = 'fas fa-sun';
            }
        });
        
        // Função para inicializar tema baseado no localStorage
        function initializeTheme() {
            const savedTheme = localStorage.getItem('theme');
            const themeIcon = document.getElementById('theme-icon');
            
            if (savedTheme === 'dark') {
                document.body.classList.add('dark-mode');
                themeIcon.className = 'fas fa-sun';
            } else {
                themeIcon.className = 'fas fa-moon';
            }
        }
        
        // Função para atualizar tema dos gráficos
        function updateChartsTheme() {
            const isDark = document.body.classList.contains('dark-mode');
            
            // Atualiza gráfico de evolução
            if (evolutionChart) {
                evolutionChart.options.scales.x.title.color = isDark ? '#ffffff' : '#333';
                evolutionChart.options.scales.x.ticks.color = isDark ? '#ffffff' : '#333';
                evolutionChart.options.scales.x.grid.color = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
                evolutionChart.options.scales.y.title.color = isDark ? '#ffffff' : '#333';
                evolutionChart.options.scales.y.ticks.color = isDark ? '#ffffff' : '#333';
                evolutionChart.options.scales.y.grid.color = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
                evolutionChart.options.plugins.legend.labels.color = isDark ? '#ffffff' : '#333';
                evolutionChart.update();
            }
            
            // Atualiza gráfico de lucro
            if (profitChart) {
                profitChart.options.scales.x.title.color = isDark ? '#ffffff' : '#333';
                profitChart.options.scales.x.ticks.color = isDark ? '#ffffff' : '#333';
                profitChart.options.scales.x.grid.color = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
                profitChart.options.scales.y.title.color = isDark ? '#ffffff' : '#333';
                profitChart.options.scales.y.ticks.color = isDark ? '#ffffff' : '#333';
                profitChart.options.scales.y.grid.color = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
                profitChart.options.plugins.legend.labels.color = isDark ? '#ffffff' : '#333';
                profitChart.update();
            }
            
            // Atualiza gráfico de símbolos
            if (symbolChart) {
                symbolChart.options.plugins.legend.labels.color = isDark ? '#ffffff' : '#333';
                symbolChart.update();
            }
            
            // Atualiza gráfico de tempo agrupado
            if (timeGroupedChart) {
                timeGroupedChart.options.scales.x.title.color = isDark ? '#ffffff' : '#333';
                timeGroupedChart.options.scales.x.ticks.color = isDark ? '#ffffff' : '#333';
                timeGroupedChart.options.scales.x.grid.color = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
                timeGroupedChart.options.scales.y.title.color = isDark ? '#ffffff' : '#333';
                timeGroupedChart.options.scales.y.ticks.color = isDark ? '#ffffff' : '#333';
                timeGroupedChart.options.scales.y.grid.color = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
                timeGroupedChart.options.plugins.legend.labels.color = isDark ? '#ffffff' : '#333';
                timeGroupedChart.update();
            }
        }
    </script>
    
    <!-- Sistema de Internacionalização -->
    <script>
        // Variável global com idioma do servidor (definida ANTES de carregar i18n.js)
        window.SAVED_LANGUAGE_FROM_SERVER = '{{ session.get("saved_language", "") }}';
        console.log('[IDIOMA INIT] Idioma definido globalmente:', window.SAVED_LANGUAGE_FROM_SERVER);
    </script>
    <script src="{{ url_for('static', filename='js/i18n.js') }}"></script>
    <script>
        // Inicializar sistema de idiomas no dashboard
        document.addEventListener('DOMContentLoaded', function() {
            // Aplicar idioma salvo do login automático (se houver)
            const savedLanguageFromServer = window.SAVED_LANGUAGE_FROM_SERVER || '';
            console.log('[IDIOMA DEBUG] Idioma recebido do servidor:', savedLanguageFromServer);
            console.log('[IDIOMA DEBUG] window.i18n disponível?', typeof window.i18n !== 'undefined');
            
            if (savedLanguageFromServer && savedLanguageFromServer !== '' && savedLanguageFromServer !== 'None') {
                console.log('[IDIOMA] ✅ Aplicando idioma salvo do login automático:', savedLanguageFromServer);
                
                // Aguardar i18n estar disponível
                const applyLanguage = () => {
                    if (window.i18n && window.i18n.setLanguage) {
                        window.i18n.setLanguage(savedLanguageFromServer);
                        console.log('[IDIOMA] ✅ Idioma aplicado com sucesso:', savedLanguageFromServer);
                        
                        // Aplicar traduções imediatamente
                        setTimeout(() => {
                            applyTranslations();
                        }, 50);
                    } else {
                        console.log('[IDIOMA] ⏳ Aguardando i18n.js carregar...');
                        setTimeout(applyLanguage, 50);
                    }
                };
                
                applyLanguage();
            } else {
                console.log('[IDIOMA] ℹ️ Nenhum idioma salvo, usando padrão');
                
                // Aplicar traduções após carregar a página
                setTimeout(() => {
                    applyTranslations();
                }, 100);
            }
            
            // Escutar mudanças de idioma
            document.addEventListener('languageChanged', function(event) {
                applyTranslations();
                
                // Atualizar textos dinâmicos específicos do dashboard
                updateDynamicTexts();
            });
        });
        
        // Função para atualizar textos dinâmicos que não são capturados pelo data-i18n
        function updateDynamicTexts() {
            // Atualizar título da página
            document.title = t('dashboard_title');
            
            // Atualizar tooltips dos botões
            const languageBtn = document.querySelector('.language-toggle');
            if (languageBtn) {
                languageBtn.title = t('select_language');
            }
            
            const logoutBtn = document.querySelector('.logout-btn');
            if (logoutBtn) {
                logoutBtn.title = t('logout_button') || 'Sair';
            }
            
            // Atualizar labels dos gráficos
            if (profitChart && profitChart.data.datasets[0]) {
                profitChart.data.datasets[0].label = t('profit_loss_label');
                profitChart.update();
            }
            
            if (timeGroupedChart && timeGroupedChart.data.datasets[0]) {
                timeGroupedChart.data.datasets[0].label = t('consolidated_result_label');
                timeGroupedChart.update();
            }
            
            // Atualizar opções do seletor de tempo
            const timeSelector = document.getElementById('time-group-selector');
            if (timeSelector) {
                const options = timeSelector.querySelectorAll('option');
                options.forEach(option => {
                    const key = option.getAttribute('data-i18n');
                    if (key) {
                        option.textContent = t(key);
                    }
                });
            }
            
            // Atualizar status de conexão e última atualização
            const statusElement = document.getElementById('status');
            if (statusElement) {
                const currentStatus = statusElement.style.background.includes('40, 167, 69') ? 'connected_status' : 'disconnected_status';
                statusElement.innerHTML = '<div class="status-icon"></div><span data-i18n="' + currentStatus + '">' + t(currentStatus) + '</span>';
            }
            
            const lastUpdateElement = document.getElementById('last-update');
            if (lastUpdateElement) {
                const currentTime = lastUpdateElement.textContent.split(': ')[1] || new Date().toLocaleTimeString();
                lastUpdateElement.innerHTML = `<span data-i18n="last_update">${t('last_update')}</span> ${currentTime}`;
            }
        }
    </script>
    
    <!-- Rodapé com suporte -->
    <footer style="position: fixed; bottom: 0; left: 0; right: 0; background: rgba(20, 20, 20, 0.95); padding: 10px; text-align: center; border-top: 1px solid #333; z-index: 1000;">
        <div style="display: flex; justify-content: center; align-items: center; gap: 20px; font-size: 12px; color: #888;">
            <span>© 2024 VolatForex Monitor & Scalper Pro</span>
            <span>|</span>
            <a href="mailto:support@volatforex.com" style="color: #4fc3f7; text-decoration: none;" title="Contatar Suporte">
                <i class="fas fa-envelope" style="margin-right: 5px;"></i>Suporte
            </a>
        </div>
    </footer>
    
    <style>
        /* Adiciona padding-bottom ao body para não sobrepor o footer */
        body {
            padding-bottom: 50px;
        }
    </style>
    
</body>
</html>
"""

@app.route('/')
@login_required
def dashboard():
    """Serve a página principal do dashboard"""
    # Obter dados do usuário atual
    user_email = get_current_user()
    user_first_name = get_user_first_name(user_email) or "Usuário"
    user_messages = get_user_messages(user_email)
    user_notifications = get_user_notifications(user_email)
    
    # Obter idioma salvo da sessão (se houver)
    saved_language = session.get('saved_language', '')
    print(f"[DASHBOARD] [INFO] Renderizando dashboard - Idioma da sessao: '{saved_language}'")
    
    # Passar dados para o template
    return render_template_string(
        HTML_TEMPLATE,
        user_first_name=user_first_name,
        user_messages=json.dumps(user_messages),
        user_notifications=json.dumps(user_notifications)
    )

@app.route('/webhook', methods=['POST', 'GET'])
def receive_webhook():
    """Recebe os dados do EA MetaTrader"""
    try:
        if request.method == 'POST':
            data = request.get_json()
        else:  # GET
            # Para método GET, constrói dados básicos dos parâmetros
            data = {
                'account_info': {
                    'account_balance': float(request.args.get('balance', 0)),
                    'account_equity': float(request.args.get('equity', 0)),
                    'account_profit': 0,
                    'account_margin': 0,
                    'account_free_margin': 0,
                    'account_number': request.args.get('account', 'N/A'),
                    'account_server': 'Local',
                    'account_currency': 'USD'
                },
                'timestamp': datetime.datetime.now().isoformat(),
                'last_trades': []
            }
        
        if data:
            # Adiciona timestamp de recebimento
            data['received_at'] = datetime.datetime.now().isoformat()
            
            # --- NORMALIZAÇÃO DE SÍMBOLOS (Multi-Corretoras) ---
            broker_name = data.get('account_info', {}).get('account_server', '')
            
            # Normalizar símbolos dos trades fechados
            if 'last_trades' in data:
                for trade in data['last_trades']:
                    original_symbol = trade.get('symbol', '')
                    if original_symbol:
                        trade['symbol_original'] = original_symbol
                        trade['symbol'] = symbol_mapper.normalize(original_symbol)
            
            # Normalizar símbolos dos trades abertos
            if 'open_trades' in data:
                for trade in data['open_trades']:
                    original_symbol = trade.get('symbol', '')
                    if original_symbol:
                        trade['symbol_original'] = original_symbol
                        trade['symbol'] = symbol_mapper.normalize(original_symbol)
            
            # --- PROCESSAR TICK DATA (Preços em Tempo Real) ---
            if 'tick_data' in data:
                for symbol, tick_info in data['tick_data'].items():
                    # Normaliza o símbolo
                    normalized_symbol = symbol_mapper.normalize(symbol)
                    
                    # Extrai dados de preço
                    bid = tick_info.get('bid', 0)
                    ask = tick_info.get('ask', 0)
                    price = tick_info.get('price', (bid + ask) / 2 if bid and ask else 0)
                    
                    # Adiciona ao histórico de preços
                    add_price_point(
                        symbol=normalized_symbol,
                        price=price,
                        bid=bid,
                        ask=ask,
                        timestamp=data['received_at']
                    )
            
            # Armazena histórico de saldo e equity para o gráfico de evolução
            if data.get('account_info'):
                balance_point = {
                    'timestamp': data['received_at'],
                    'balance': data['account_info'].get('account_balance', 0),
                    'equity': data['account_info'].get('account_equity', 0)
                }
                balance_history.append(balance_point)
            
            # Armazena os dados
            trade_history.append(data)
            global latest_data
            latest_data = data
            
            # Log no console
            balance = data.get('account_info', {}).get('account_balance', 0)
            trades_count = len(data.get('last_trades', []))
            tick_count = len(data.get('tick_data', {}))
            
            if tick_count > 0:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Dados recebidos - Saldo: ${balance:.2f} - Trades: {trades_count} - Ticks: {tick_count}")
            else:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Dados recebidos - Saldo: ${balance:.2f} - Trades: {trades_count}")
            
            return jsonify({
                'status': 'success',
                'message': 'Dados recebidos com sucesso',
                'timestamp': datetime.datetime.now().isoformat()
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'Dados inválidos'}), 400
            
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/latest')
@api_login_required
def get_latest_data():
    """API para obter os dados mais recentes"""
    return jsonify(latest_data)

@app.route('/api/balance-history')
@api_login_required
def get_balance_history():
    """API para obter histórico de saldo e equity"""
    return jsonify({'balance_history': list(balance_history)})

@app.route('/api/history')
@api_login_required
def get_history():
    """API para obter histórico de dados"""
    return jsonify(list(trade_history))

@app.route('/api/status')
def get_status():
    """API para verificar status do servidor"""
    return jsonify({
        'status': 'online',
        'data_count': len(trade_history),
        'last_update': latest_data.get('received_at', 'N/A'),
        'server_time': datetime.datetime.now().isoformat()
    })

# ==================== NOVAS ROTAS - GRÁFICOS DE PREÇO ====================

@app.route('/api/price-history/<symbol>')
@api_login_required
def get_price_history(symbol):
    """API para obter histórico de preços de um símbolo"""
    try:
        # Normaliza o símbolo
        normalized_symbol = symbol_mapper.normalize(symbol)
        
        if normalized_symbol not in price_history:
            return jsonify({
                'symbol': normalized_symbol,
                'data': [],
                'message': 'Nenhum dado disponível para este símbolo'
            })
        
        return jsonify({
            'symbol': normalized_symbol,
            'data': list(price_history[normalized_symbol]),
            'count': len(price_history[normalized_symbol])
        })
    except Exception as e:
        print(f"[API] Erro ao obter histórico de preços: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/symbols')
@api_login_required
def get_symbols():
    """API para listar todos os símbolos disponíveis"""
    try:
        symbols = symbol_mapper.list_symbols()
        return jsonify({
            'symbols': [
                {
                    'standard': key,
                    'description': value['description'],
                    'category': value['category'],
                    'aliases': value['aliases']
                }
                for key, value in symbols.items()
            ]
        })
    except Exception as e:
        print(f"[API] Erro ao listar símbolos: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/symbols/categories')
@api_login_required
def get_symbol_categories():
    """API para listar categorias de símbolos"""
    try:
        categories = symbol_mapper.list_categories()
        return jsonify({'categories': categories})
    except Exception as e:
        print(f"[API] Erro ao listar categorias: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/symbols/search')
@api_login_required
def search_symbols():
    """API para buscar símbolos"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'results': []})
        
        results = symbol_mapper.search_symbols(query)
        return jsonify({'results': results})
    except Exception as e:
        print(f"[API] Erro ao buscar símbolos: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/symbols/<symbol>/info')
@api_login_required
def get_symbol_info(symbol):
    """API para obter informações de um símbolo"""
    try:
        info = symbol_mapper.get_symbol_info(symbol)
        return jsonify(info)
    except Exception as e:
        print(f"[API] Erro ao obter informações do símbolo: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== ROTAS - INDICADORES TÉCNICOS ====================

@app.route('/api/indicators/<symbol>')
@api_login_required
def get_indicators(symbol):
    """API para obter todos os indicadores de um símbolo com períodos customizados"""
    try:
        # Normaliza o símbolo
        normalized_symbol = symbol_mapper.normalize(symbol)
        
        # Obter períodos dos parâmetros da query
        hull_period = int(request.args.get('hull_period', 180))
        zscore_period = int(request.args.get('zscore_period', 150))
        rsi_period = int(request.args.get('rsi_period', 14))
        
        # Validar ranges
        hull_period = max(5, min(250, hull_period))
        zscore_period = max(5, min(200, zscore_period))
        rsi_period = max(5, min(70, rsi_period))
        
        if normalized_symbol not in price_history or len(price_history[normalized_symbol]) < max(hull_period, zscore_period, rsi_period):
            return jsonify({
                'symbol': normalized_symbol,
                'message': 'Dados insuficientes para calcular indicadores',
                'data': {}
            })
        
        # Recalcular indicadores com períodos customizados
        prices = [p['price'] for p in price_history[normalized_symbol]]
        timestamps = [p['timestamp'] for p in price_history[normalized_symbol]]
        
        calc = TechnicalIndicators()
        
        # Calcular apenas os últimos N valores para economizar processamento
        history_data = {
            'timestamps': timestamps,
            'hull_ma': [],
            'zscore': [],
            'rsi': []
        }
        
        # Calcular para cada ponto do histórico
        for i in range(len(prices)):
            if i >= max(hull_period, zscore_period, rsi_period):
                prices_slice = prices[:i+1]
                
                hull_value = calc.calculate_hull_ma(prices_slice, hull_period)
                zscore_value = calc.calculate_zscore(prices_slice, zscore_period)
                rsi_value = calc.calculate_rsi(prices_slice, rsi_period)
                
                history_data['hull_ma'].append(hull_value)
                history_data['zscore'].append(zscore_value)
                history_data['rsi'].append(rsi_value)
            else:
                history_data['hull_ma'].append(None)
                history_data['zscore'].append(None)
                history_data['rsi'].append(None)
        
        return jsonify({
            'symbol': normalized_symbol,
            'data': history_data,
            'periods': {
                'hull': hull_period,
                'zscore': zscore_period,
                'rsi': rsi_period
            }
        })
    except Exception as e:
        print(f"[API] Erro ao obter indicadores: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/indicators/<symbol>/latest')
@api_login_required
def get_latest_indicators(symbol):
    """API para obter os últimos valores dos indicadores"""
    try:
        # Normaliza o símbolo
        normalized_symbol = symbol_mapper.normalize(symbol)
        
        if normalized_symbol not in indicator_history:
            return jsonify({
                'symbol': normalized_symbol,
                'message': 'Nenhum indicador disponível para este símbolo',
                'data': {}
            })
        
        # Retorna últimos valores
        latest = indicator_history[normalized_symbol].get_latest()
        
        return jsonify({
            'symbol': normalized_symbol,
            'data': latest
        })
    except Exception as e:
        print(f"[API] Erro ao obter últimos indicadores: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/indicators/<symbol>/<indicator_name>')
@api_login_required
def get_specific_indicator(symbol, indicator_name):
    """API para obter um indicador específico"""
    try:
        # Normaliza o símbolo
        normalized_symbol = symbol_mapper.normalize(symbol)
        
        if normalized_symbol not in indicator_history:
            return jsonify({
                'symbol': normalized_symbol,
                'indicator': indicator_name,
                'message': 'Nenhum dado disponível',
                'data': []
            })
        
        # Obtém histórico completo
        history = indicator_history[normalized_symbol].get_history()
        
        # Verifica se o indicador existe
        if indicator_name not in history:
            return jsonify({
                'symbol': normalized_symbol,
                'indicator': indicator_name,
                'message': 'Indicador não encontrado',
                'available_indicators': list(history.keys())
            }), 404
        
        return jsonify({
            'symbol': normalized_symbol,
            'indicator': indicator_name,
            'timestamps': history['timestamps'],
            'data': history[indicator_name]
        })
    except Exception as e:
        print(f"[API] Erro ao obter indicador específico: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/close-order', methods=['POST'])
@api_login_required
def close_order():
    """API para fechar uma ordem específica"""
    try:
        data = request.get_json()
        ticket = data.get('ticket')
        
        if not ticket:
            return jsonify({'status': 'error', 'message': 'Ticket é obrigatório'}), 400
        
        # Adiciona comando à fila para o MT5 processar
        add_command_to_queue('close_order', ticket)
        print(f"Comando para fechar ordem {ticket} enviado")
        
        return jsonify({
            'status': 'success', 
            'message': f'Comando para fechar ordem {ticket} enviado com sucesso',
            'ticket': ticket
        })
        
    except Exception as e:
        print(f"Erro ao fechar ordem: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/close-all-orders', methods=['POST'])
@api_login_required
def close_all_orders():
    """API para fechar todas as ordens abertas"""
    try:
        # Adiciona comando à fila para o MT5 processar
        add_command_to_queue('close_all')
        print("Comando para fechar todas as ordens enviado")
        
        return jsonify({
            'status': 'success', 
            'message': 'Comando para fechar todas as ordens enviado com sucesso'
        })
        
    except Exception as e:
        print(f"Erro ao fechar todas as ordens: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/close-positive-orders', methods=['POST'])
@api_login_required
def close_positive_orders():
    """API para fechar apenas ordens com lucro positivo"""
    try:
        # Adiciona comando à fila para o MT5 processar
        add_command_to_queue('close_positive')
        print("Comando para fechar ordens positivas enviado")
        
        return jsonify({
            'status': 'success', 
            'message': 'Comando para fechar ordens positivas enviado com sucesso'
        })
        
    except Exception as e:
        print(f"Erro ao fechar ordens positivas: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/close-negative-orders', methods=['POST'])
@api_login_required
def close_negative_orders():
    """API para fechar apenas ordens com lucro negativo"""
    try:
        # Adiciona comando à fila para o MT5 processar
        add_command_to_queue('close_negative')
        print("Comando para fechar ordens negativas enviado")
        
        return jsonify({
            'status': 'success', 
            'message': 'Comando para fechar ordens negativas enviado com sucesso'
        })
        
    except Exception as e:
        print(f"Erro ao fechar ordens negativas: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Fila de comandos para o MT5
command_queue = []

def add_command_to_queue(command_type, ticket=None):
    """Adiciona um comando à fila para ser processado pelo MT5"""
    command = {
        'command': command_type,
        'timestamp': datetime.datetime.now().isoformat()
    }
    if ticket:
        command['ticket'] = ticket
    
    command_queue.append(command)
    print(f"Comando adicionado à fila: {command}")

@app.route('/api/commands', methods=['GET'])
def get_pending_commands():
    """API para o MT5 verificar comandos pendentes"""
    try:
        if command_queue:
            # Retorna o primeiro comando da fila e o remove
            command = command_queue.pop(0)
            print(f"Comando enviado para MT5: {command}")
            return jsonify(command)
        else:
            # Nenhum comando pendente
            return jsonify({'status': 'no_commands'}), 404
            
    except Exception as e:
        print(f"Erro ao obter comandos: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def open_browser():
    """Abre o navegador automaticamente"""
    import time
    time.sleep(0)  # Aguarda o servidor iniciar
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("=" * 60)
    print("[INIT] SERVIDOR WEBHOOK LOCAL INICIADO")
    print("=" * 60)
    print(f"[INIT] Dashboard: http://localhost:5000")
    print(f"[INIT] Webhook URL: http://localhost:5000/webhook")
    print(f"[INIT] API Status: http://localhost:5000/api/status")
    print("=" * 60)
    print("[INIT] Configure o EA com a URL: http://localhost:5000/webhook")
    print("[INIT] O navegador sera aberto automaticamente...")
    print("=" * 60)
    
    # Abre o navegador em uma thread separada
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Limpar dados antigos ao iniciar (opcional)
    trade_history.clear()
    balance_history.clear()
    
    # Adicionar dados iniciais simulados para o gráfico de evolução
    import time
    current_time = datetime.datetime.now()
    initial_balance = 10000.0  # Saldo inicial simulado
    
    # Criar alguns pontos de dados iniciais para demonstração
    for i in range(10):
        timestamp = (current_time - datetime.timedelta(minutes=i*5)).isoformat()
        balance_point = {
            'timestamp': timestamp,
            'balance': initial_balance + (i * 10),  # Pequena variação
            'equity': initial_balance + (i * 8)     # Equity ligeiramente diferente
        }
        balance_history.appendleft(balance_point)  # Adiciona no início para manter ordem cronológica
    
    # Adicionar dados iniciais ao latest_data para garantir que o frontend tenha dados
    latest_data = {
        'account_info': {
            'account_balance': initial_balance + 90,
            'account_equity': initial_balance + 72,
            'account_profit': 90,
            'account_margin': 0,
            'account_free_margin': initial_balance + 72,
            'account_number': 'DEMO123456',
            'account_server': 'Demo Server',
            'account_currency': 'USD'
        },
        'timestamp': current_time.isoformat(),
        'last_trades': [],
        'open_trades': [
            {
                'ticket': '123456789',
                'symbol': 'EURUSD',
                'type': 'BUY',
                'volume': 0.10,
                'price': 1.0850,
                'profit': 15.50,
                'profit_raw': 18.75,
                'swap': -3.25,
                'open_time': (current_time - datetime.timedelta(minutes=5)).isoformat()
            },
            {
                'ticket': '123456790',
                'symbol': 'GBPUSD',
                'type': 'SELL',
                'volume': 0.05,
                'price': 1.2650,
                'profit': -8.20,
                'profit_raw': -5.45,
                'swap': -2.75,
                'open_time': (current_time - datetime.timedelta(minutes=2)).isoformat()
            },
            {
                'ticket': '123456791',
                'symbol': 'USDJPY',
                'type': 'BUY',
                'volume': 0.08,
                'price': 149.25,
                'profit': 22.80,
                'profit_raw': 25.30,
                'swap': -2.50,
                'open_time': (current_time - datetime.timedelta(minutes=8)).isoformat()
            }
        ],
        'received_at': current_time.isoformat()
    }
    
# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login - Autenticação via Google Apps Script API"""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            remember_me = request.form.get('remember_me') == 'on'
            language = request.form.get('language', 'pt')  # Captura idioma do formulário
            
            if not email:
                return render_template('login.html', 
                                     error='Email é obrigatório',
                                     error_key='error_email_required')
            
            # Verifica o usuário na API do Google
            user_data = check_user_status(email)
            
            if user_data:
                # Usuário encontrado - verifica se tem PURCHASE_APPROVED
                if user_data.get('status') == 'PURCHASE_APPROVED':
                    # Gera token único de sessão com timestamps
                    session_token = generate_session_token()
                    import time
                    _valid_session_tokens[session_token] = {
                        "created_at": time.time(),
                        "last_validated": time.time(),
                        "email": email
                    }
                    
                    # Usuário aprovado - salva TODOS os dados na sessão (evita requisições futuras)
                    session['session_token'] = session_token  # Token único para validação
                    session['user_email'] = email
                    session['user_name'] = user_data.get('pnome', '')
                    session['user_full_name'] = user_data.get('nomecompleto', '')
                    session['user_status'] = user_data.get('status')  # Salva status na sessão
                    session['user_data_timestamp'] = user_data.get('data', '')
                    session.permanent = True
                    
                    # Se "lembrar login" estiver marcado, salva email e idioma em arquivo local
                    if remember_me:
                        save_user_credentials(email, language)
                        print(f"[LOGIN] 💾 Credenciais salvas - Email: {email} | Idioma: {language}")
                    else:
                        # Se não marcou, remove credenciais salvas anteriormente
                        clear_saved_credentials()
                    
                    print(f"[LOGIN] ✅ {email} autenticado - Token: {session_token[:16]}... (sessão segura)")
                    return redirect(url_for('dashboard'))
                else:
                    # Usuário existe mas não está aprovado
                    print(f"[LOGIN] ⚠️ {email} não aprovado - Status: {user_data.get('status')}")
                    # Remove credenciais salvas se houver (usuário perdeu acesso)
                    clear_saved_credentials()
                    # Redireciona para página de acesso negado com nome do usuário
                    session['pending_user_name'] = user_data.get('pnome', '')
                    session['pending_user_email'] = email
                    return redirect(url_for('access_denied'))
            else:
                # Usuário não encontrado
                print(f"[LOGIN] ❌ {email} não encontrado no sistema")
                # Remove credenciais salvas se houver
                clear_saved_credentials()
                return render_template('login.html', 
                                     error='Email não encontrado no sistema. Verifique seu email ou adquira o acesso.',
                                     error_key='error_email_not_found')
                
        except Exception as e:
            print(f"[LOGIN] Erro no login: {e}")
            return render_template('login.html', 
                                 error='Erro ao fazer login. Tente novamente.',
                                 error_key='error_login_failed')
    
    # Verifica se há credenciais salvas para login automático
    saved_creds = get_saved_credentials()
    if saved_creds:
        saved_email = saved_creds.get('email')
        saved_language = saved_creds.get('language', 'pt')
        
        try:
            print(f"[LOGIN] 🔍 Tentando login automático - Email: {saved_email} | Idioma: {saved_language}")
            # Tenta fazer login automático (Única requisição à API)
            user_data = check_user_status(saved_email)
            
            if user_data and user_data.get('status') == 'PURCHASE_APPROVED':
                # Gera token único de sessão com timestamps
                session_token = generate_session_token()
                import time
                _valid_session_tokens[session_token] = {
                    "created_at": time.time(),
                    "last_validated": time.time(),
                    "email": saved_email
                }
                
                # Salva TODOS os dados na sessão
                session['session_token'] = session_token
                session['user_email'] = saved_email
                session['user_name'] = user_data.get('pnome', '')
                session['user_full_name'] = user_data.get('nomecompleto', '')
                session['user_status'] = user_data.get('status')
                session['user_data_timestamp'] = user_data.get('data', '')
                session['saved_language'] = saved_language  # Salva idioma na sessão para aplicar no dashboard
                session.permanent = True
                print(f"[LOGIN] [OK] Login automatico bem-sucedido: {saved_email}")
                print(f"[LOGIN] [INFO] Idioma salvo na sessao: {saved_language}")
                return redirect(url_for('dashboard'))
            else:
                # Credenciais salvas não são mais válidas
                print(f"[LOGIN] [AVISO] Credenciais salvas invalidas - removendo")
                clear_saved_credentials()
                # Mostra tela de login com mensagem
                if user_data:
                    # Usuário existe mas não está mais aprovado
                    session['pending_user_name'] = user_data.get('pnome', '')
                    session['pending_user_email'] = saved_email
                    return redirect(url_for('access_denied'))
                else:
                    # Usuário não existe mais
                    return render_template('login.html', 
                                         error='Sua sessão expirou. Faça login novamente.',
                                         error_key='error_session_expired')
        except Exception as e:
            print(f"[LOGIN] ❌ Erro ao fazer login automático: {e}")
            # Remove credenciais corrompidas
            clear_saved_credentials()
            pass  # Se falhar, continua para página de login normal
    
    # Carrega idioma salvo para pré-selecionar na tela de login
    saved_language = get_saved_language()
    return render_template('login.html', saved_language=saved_language)

@app.route('/logout')
def logout():
    """Rota para logout - Invalida sessão completamente"""
    # Limpa o cache do usuário antes de fazer logout
    user_email = get_current_user()
    if user_email:
        clear_user_cache(user_email)
        print(f"[LOGOUT] 👋 {user_email} desconectado")
    
    # Limpa completamente a sessão
    session.clear()
    
    # Remove credenciais salvas (login automático e idioma)
    clear_saved_credentials()
    print("[LOGOUT] 🗑️ Credenciais de login automático removidas (email + idioma)")
    
    # Cria resposta de redirecionamento
    resp = make_response(redirect(url_for('login')))
    
    # Headers para prevenir cache
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    
    return resp

@app.route('/access-denied')
def access_denied():
    """Página de acesso negado com mensagem personalizada"""
    # Obtém o nome do usuário da sessão (se disponível)
    user_name = session.get('pending_user_name', '')
    
    # Limpa as variáveis temporárias da sessão
    session.pop('pending_user_name', None)
    session.pop('pending_user_email', None)
    
    return render_template('access_denied.html', user_name=user_name)

# ==================== INICIALIZAÇÃO DO SERVIDOR ====================

if __name__ == '__main__':
    # Configuração do Waitress para melhor performance e robustez
    print("\n" + "="*60)
    print("[INIT] Iniciando servidor Waitress (Producao)")
    print(f"[INIT] Servidor disponivel em: http://127.0.0.1:5000")
    print(f"[INIT] Dashboard: http://127.0.0.1:5000")
    print(f"[INIT] Login: http://127.0.0.1:5000/login")
    print(f"[INIT] API Status: http://127.0.0.1:5000/api/latest")
    print("[INIT] Servidor otimizado para alta performance")
    print("[INIT] Sistema com autenticacao Google Apps Script ativado")
    print("="*60 + "\n")
    
    # Configurações otimizadas do Waitress
    serve(app, 
          host='127.0.0.1', 
          port=5000,
          threads=8,              # Número de threads para processar requisições
          connection_limit=1000,   # Limite de conexões simultâneas
          cleanup_interval=30,     # Intervalo de limpeza em segundos
          channel_timeout=120,     # Timeout do canal
          max_request_body_size=1048576,  # 1MB max body size
          send_bytes=18000,        # Bytes enviados por vez
          asyncore_use_poll=True   # Usar poll() em vez de select() para melhor performance
    )