#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Webhook Local para receber dados do EA MetaTrader 5
Salva os dados e serve uma página web para visualização
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from waitress import serve
import json
import datetime
import threading
import webbrowser
from collections import deque
import os

app = Flask(__name__)
CORS(app)

# --- Armazenamento de Dados em Memória ---
# Usamos deque para manter um número fixo de registros, descartando os mais antigos.
latest_data = {}
trade_history = deque(maxlen=200)
balance_history = deque(maxlen=100)

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
            right: 20px;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 10px 15px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .theme-toggle:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.05);
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
        
        @media (max-width: 768px) {
            .grid-layout {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;700&family=Rajdhani:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
</head>
<body class="dark-mode">
    <div id="goal-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <span class="close-button">&times;</span>
                <h2>🎉 Parabéns! Meta Atingida! 🎉</h2>
            </div>
            <div class="modal-body">
                <p>Você alcançou sua meta diária de <strong id="modal-goal-value"></strong>!</p>
                <p>Excelente trabalho! Lembre-se que a disciplina é a chave para o sucesso a longo prazo. Considere fazer uma pausa e proteger seus lucros.</p>
                <p><strong>Recomendação:</strong> Pare de operar por hoje e volte amanhã com a mesma disciplina.</p>
            </div>
            <div class="modal-footer">
                <h3>#StopLoss #StopGain #Disciplina</h3>
            </div>
        </div>
    </div>

    <div id="loss-limit-modal" class="modal">
        <div class="modal-content modal-loss">
            <div class="modal-header">
                <span class="close-button loss-close-button">&times;</span>
                <h2>🚨 Atenção! Limite de Perda Atingido! 🚨</h2>
            </div>
            <div class="modal-body">
                <p>Você atingiu seu limite diário de perda de <strong id="modal-loss-limit-value"></strong>.</p>
                <p><strong>Pare de operar imediatamente!</strong> A disciplina é crucial para proteger seu capital e garantir sua sobrevivência no mercado.</p>
                <p><strong>Recomendação:</strong> Feche a plataforma, revise suas operações e volte amanhã com a mente renovada.</p>
            </div>
            <div class="modal-footer">
                <h3>#StopLoss #GerenciamentoDeRisco #Disciplina</h3>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="header">
            <button class="theme-toggle" onclick="toggleTheme()">
                <i class="fas fa-moon" id="theme-icon"></i>
            </button>
            <h1>VolatForex Monitor <span class="pro-text">Pro</span></h1>
            <div class="account-info-header" id="account-info-header" style="margin-top: 10px; font-size: 0.9em; opacity: 0.8;">
                <!-- Informações da conta serão inseridas aqui via JavaScript -->
            </div>
            <div class="d-flex justify-content-between align-items-center mt-3">
                <div class="status" id="status">
                    <div class="status-icon"></div>
                    Conectado
                </div>
                <div class="update-frequency-control">
                    <label for="update-frequency" class="form-label text-white-50 me-2 small">Frequência:</label>
                    <select id="update-frequency" class="form-select form-select-sm opacity-75" style="width: auto; display: inline-block; font-size: 0.8rem;">
                        <option value="100" selected>0.1s</option>
                        <option value="1000">1s</option>
                        <option value="2000">2s</option>
                        <option value="5000">5s</option>
                        <option value="10000">10s</option>
                    </select>
                    <div class="last-update mt-1 small text-white-50 opacity-75" id="last-update">
                        Última atualização: Aguardando...
                    </div>
                </div>
            </div>

        <main class="content">

            <!-- Cards de Informação -->
            <div class="row">
                <div class="col-md-6 col-lg-3 mb-4">
                    <div class="card h-100 shadow-sm border-start border-primary border-4">
                        <div class="card-body py-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="card-subtitle text-muted dark-mode-text">Saldo Atual</h6>
                                    <h4 class="card-title fw-bold mb-0 dark-mode-text" id="balance">$0.00</h4>
                                </div>
                                <i class="fas fa-wallet fa-2x text-primary opacity-75"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 col-lg-3 mb-4">
                    <div class="card h-100 shadow-sm border-start border-info border-4">
                        <div class="card-body py-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <h6 class="card-subtitle text-muted dark-mode-text mb-0">Equity</h6>
                                        <div class="d-flex gap-1 px-2 py-1 rounded" style="background-color: rgba(0,0,0,0.05); margin-left: 8px;" id="equity-result-indicator">
                                            <small class="fw-bold" id="equity-result-value">$0.00</small>
                                        </div>
                                    </div>
                                    <h4 class="card-title fw-bold mb-0 dark-mode-text" id="equity">$0.00</h4>
                                </div>
                                <i class="fas fa-chart-pie fa-2x text-info opacity-75"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 col-lg-3 mb-4">
                    <div class="card h-100 shadow-sm border-start border-warning border-4">
                        <div class="card-body py-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <div class="d-flex align-items-center mb-1">
                                        <h6 class="card-subtitle text-muted dark-mode-text mb-0">L/P do Dia</h6>
                                        <span class="badge bg-secondary ms-2" id="profit-percentage" style="font-size: 1em;">0.00%</span>
                                    </div>
                                    <h4 class="card-title fw-bold mb-0 dark-mode-text" id="profit">$0.00</h4>
                                </div>
                                <i class="fas fa-dollar-sign fa-2x text-warning opacity-75"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 col-lg-3 mb-4">
                    <div class="card h-100 shadow-sm border-start border-secondary border-4">
                        <div class="card-body py-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <h6 class="card-subtitle text-muted dark-mode-text mb-0">Trades Hoje</h6>
                                        <div class="d-flex gap-2 px-2 py-1 rounded" style="background-color: rgba(0,0,0,0.55); margin-left: 8px;">
                                            <small class="text-success fw-bold" id="trades-positive">+0</small>
                                            <small class="text-danger fw-bold" id="trades-negative">-0</small>
                                        </div>
                                    </div>
                                    <h4 class="card-title fw-bold mb-0 dark-mode-text" id="trades-today">0</h4>
                                </div>
                                <i class="fas fa-exchange-alt fa-2x text-secondary opacity-75"></i>
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
                            <h6 class="card-title mb-0"><i class="fas fa-chart-bar me-2"></i>Trades Abertos</h6>
                            <button id="sort-trades-btn" class="btn btn-sm btn-outline-secondary" title="Ordenar por lucro">
                                <i class="fas fa-sort-amount-down" id="sort-icon"></i>
                            </button>
                        </div>
                        <div class="card-body">
                            <!-- Botões de Controle de Fechamento -->
                            <div class="mb-3">
                                <div class="row g-1">
                                    <div class="col-6">
                                        <button id="close-all-btn" class="btn btn-danger btn-sm w-100" title="Fechar todas as ordens">
                                            <i class="fas fa-times-circle me-1"></i>Fechar Todas
                                        </button>
                                    </div>
                                    <div class="col-6">
                                        <button id="close-positive-btn" class="btn btn-success btn-sm w-100" title="Fechar apenas ordens positivas">
                                            <i class="fas fa-plus-circle me-1"></i>Fechar +
                                        </button>
                                    </div>
                                    <div class="col-12 mt-1">
                                        <button id="close-negative-btn" class="btn btn-warning btn-sm w-100" title="Fechar apenas ordens negativas">
                                            <i class="fas fa-minus-circle me-1"></i>Fechar Negativas
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
                                    <p>Nenhum trade aberto no momento</p>
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
                                        <span class="input-group-text">Meta Ganho</span>
                                        <input type="number" class="form-control" id="daily-goal-input" value="2" min="0.1" step="0.1">
                                        <span class="input-group-text">%</span>
                                    </div>
                                    <div class="input-group input-group-sm">
                                        <span class="input-group-text">Limite Perda</span>
                                        <input type="number" class="form-control" id="daily-loss-limit-input" value="1" min="0.1" step="0.1">
                                        <span class="input-group-text">%</span>
                                    </div>
                                </div>
                                <!-- Métricas e Progresso -->
                                <div class="col-lg-9">
                                    <div class="row g-2 mb-2">
                                        <div class="col-md-3">
                                            <div class="metric-box loss-box h-100">
                                                <small>Limite Perda</small>
                                                <strong id="loss-limit-text">$0.00</strong>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="metric-box progress-box h-100">
                                                <small>Progresso Diário</small>
                                                <strong id="daily-progress-text">$0.00</strong>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="metric-box gain-box h-100">
                                                <small>Meta Ganho</small>
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
                                                <span class="text-danger fw-bold">🔻 Limite de perda: 0%</span>
                                            </div>
                                        </div>
                                        <div class="col-6">
                                            <div class="text-end small" id="gain-percentage-text">
                                                <span class="text-success fw-bold">🎯 Meta de ganho: 0%</span>
                                            </div>
                                        </div>
                                    </div>
                                     <div class="text-center mt-2 small text-muted" id="monthly-projection">Projeção Mensal: <b>$0.00</b></div>
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
                            <h5 class="card-title"><i class="fas fa-chart-pie me-2 text-primary"></i>Distribuição por Símbolo</h5>
                            <div class="chart-container flex-grow-1">
                                <canvas id="symbolChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-8 mb-4">
                    <div class="card h-100 shadow-sm border-light-subtle">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title"><i class="fas fa-chart-bar me-2 text-primary"></i>Lucro/Prejuízo (Últimos 15 Trades)</h5>
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
                            <h6 class="card-title mb-0"><i class="fas fa-chart-bar me-2"></i>Resultado Consolidado por Tempo</h6>
                            <div class="col-auto">
                                <select id="time-group-selector" class="form-select form-select-sm">
                                    <option value="5" selected>5 minutos</option>
                                    <option value="15">15 minutos</option>
                                    <option value="30">30 minutos</option>
                                    <option value="60">1 hora</option>
                                    <option value="1440">1 dia</option>
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
                            <h6 class="card-title mb-0"><i class="fas fa-history me-2"></i>Histórico de Trades Recentes</h6>
                        </div>
                        <div class="card-body p-0">
                            <div class="trades-scroll-container" style="height: 400px; overflow-y: scroll !important; border: 1px solid #dee2e6; border-radius: 0.375rem; display: block;">
                                <table class="table table-striped table-hover table-sm mb-0 trade-table" style="width: 100%; table-layout: fixed;">
                                    <thead class="table-dark" style="position: sticky; top: 0; z-index: 10; background-color: #212529 !important;">
                                        <tr>
                                            <th style="width: 5%;">#</th>
                                            <th style="width: 12%;">Ticket</th>
                                            <th style="width: 15%;">Hora de Abertura</th>
                                            <th style="width: 8%;">Tipo</th>
                                            <th style="width: 8%;">Volume</th>
                                            <th style="width: 10%;">Símbolo</th>
                                            <th style="width: 12%;">Preço de Abertura</th>
                                            <th style="width: 15%;">Preço de Fechamento</th>
                                            <th style="width: 15%;">Lucro</th>
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
                        const cleanTime = openTime.replace(/\./g, '-');
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
                        const cleanTime = trade.time.replace(/\./g, '-');
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
                    lossMessage = `🟢 Risco baixo: ${lossPercentage.toFixed(1)}%`;
                } else if (lossPercentage < 50) {
                    lossMessage = `🟡 Atenção: ${lossPercentage.toFixed(1)}%`;
                } else if (lossPercentage < 75) {
                    lossMessage = `🟠 Risco alto: ${lossPercentage.toFixed(1)}%`;
                } else {
                    lossMessage = `🔴 Perigo crítico: ${lossPercentage.toFixed(1)}%`;
                }
                lossPercentageElement.innerHTML = `<span class="text-danger fw-bold">🔻 ${lossMessage}</span>`;
            } else {
                lossPercentageElement.innerHTML = `<span class="text-muted fw-bold">🔻 Limite de perda: 0%</span>`;
            }
            
            if (gainPercentage > 0) {
                let gainMessage = '';
                if (gainPercentage < 25) {
                    gainMessage = `Progredindo: ${gainPercentage.toFixed(1)}%`;
                } else if (gainPercentage < 50) {
                    gainMessage = `Bom ritmo: ${gainPercentage.toFixed(1)}%`;
                } else if (gainPercentage < 75) {
                    gainMessage = `Quase lá: ${gainPercentage.toFixed(1)}%`;
                } else if (gainPercentage < 100) {
                    gainMessage = `Muito perto: ${gainPercentage.toFixed(1)}%`;
                } else {
                    gainMessage = `Meta alcançada: ${gainPercentage.toFixed(1)}%`;
                }
                gainPercentageElement.innerHTML = `<span class="text-success fw-bold">🎯 ${gainMessage}</span>`;
            } else {
                gainPercentageElement.innerHTML = `<span class="text-muted fw-bold">🎯 Meta de ganho: 0%</span>`;
            }

            // Projeção Mensal
            const monthlyProjection = dailyProfit > 0 ? goalTarget * 22 : dailyProfit * 22;
            document.getElementById('monthly-projection').innerHTML = `Projeção Mensal: <b>${formatCurrency(monthlyProjection)}</b>`;

            // Alerta de Meta Atingida
            if (dailyProfit >= goalTarget && goalTarget > 0 && !goalReachedToday) {
                goalReachedToday = true;
                document.getElementById('modal-goal-value').textContent = formatCurrency(goalTarget);
                goalModal.style.display = 'block';
            }

            // Alerta de Limite de Perda Atingido
            if (dailyProfit <= lossLimitTarget && lossLimitTarget < 0 && !lossLimitReachedToday) {
                lossLimitReachedToday = true;
                document.getElementById('modal-loss-limit-value').textContent = formatCurrency(lossLimitTarget);
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
                            label: 'Lucro/Prejuízo ($)',
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
                            label: 'Resultado Consolidado',
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
                    const cleanTime = trade.time.replace(/\./g, '-');
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
            const equityIndicator = document.getElementById('equity-result-indicator');
            
            const currentEquity = accountInfo.account_equity || 0;
            const currentBalance = accountInfo.account_balance || 0;
            
            if (currentBalance > 0) {
                const equityPercentage = ((currentEquity / currentBalance) * 100);
                const percentageDiff = equityPercentage - 100; // Diferença em relação a 100%
                
                equityResultElement.textContent = `${equityPercentage.toFixed(2)}%`;
                
                // Aplicar cor baseada na porcentagem
                if (percentageDiff > 0) {
                    equityResultElement.className = 'fw-bold text-success';
                    equityIndicator.style.backgroundColor = 'rgba(40, 167, 69, 0.1)';
                } else if (percentageDiff < 0) {
                    equityResultElement.className = 'fw-bold text-danger';
                    equityIndicator.style.backgroundColor = 'rgba(220, 53, 69, 0.1)';
                } else {
                    equityResultElement.className = 'fw-bold text-muted';
                    equityIndicator.style.backgroundColor = 'rgba(0,0,0,0.05)';
                }
            } else {
                equityResultElement.textContent = '0.00%';
                equityResultElement.className = 'fw-bold text-muted';
                equityIndicator.style.backgroundColor = 'rgba(0,0,0,0.05)';
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
            document.getElementById('last-update').textContent = 'Última atualização: ' + new Date().toLocaleTimeString('pt-BR');
            const statusElement = document.getElementById('status');
            statusElement.textContent = '🟢 Conectado';
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
                fetch('/api/latest').then(r => r.json()),
                fetch('/api/balance-history').then(r => r.json())
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
                console.error('Erro ao buscar dados:', error);
                const statusElement = document.getElementById('status');
                statusElement.textContent = '🔴 Desconectado';
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
                if (confirm('Tem certeza que deseja fechar TODAS as ordens abertas?')) {
                    closeOrders('all');
                }
            });
            
            document.getElementById('close-positive-btn').addEventListener('click', function() {
                if (confirm('Tem certeza que deseja fechar todas as ordens POSITIVAS?')) {
                    closeOrders('positive');
                }
            });
            
            document.getElementById('close-negative-btn').addEventListener('click', function() {
                if (confirm('Tem certeza que deseja fechar todas as ordens NEGATIVAS?')) {
                    closeOrders('negative');
                }
            });
            
            // Event listener para botões individuais (delegação de eventos)
            document.addEventListener('click', function(e) {
                if (e.target.closest('.close-individual-btn')) {
                    const button = e.target.closest('.close-individual-btn');
                    const ticket = button.getAttribute('data-ticket');
                    if (confirm(`Tem certeza que deseja fechar a ordem #${ticket}?`)) {
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
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            const themeIcon = document.getElementById('theme-icon');
            
            if (isDark) {
                themeIcon.className = 'fas fa-sun';
                localStorage.setItem('theme', 'dark');
            } else {
                themeIcon.className = 'fas fa-moon';
                localStorage.setItem('theme', 'light');
            }
            
            // Atualiza os gráficos para o novo tema
            updateChartsTheme();
        }
        
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
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Serve a página principal do dashboard"""
    return render_template_string(HTML_TEMPLATE)

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
def get_latest_data():
    """API para obter os dados mais recentes"""
    return jsonify(latest_data)

@app.route('/api/balance-history')
def get_balance_history():
    """API para obter histórico de saldo e equity"""
    return jsonify({'balance_history': list(balance_history)})

@app.route('/api/history')
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

@app.route('/api/close-order', methods=['POST'])
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
    print("🚀 SERVIDOR WEBHOOK LOCAL INICIADO")
    print("=" * 60)
    print(f"📊 Dashboard: http://localhost:5000")
    print(f"🔗 Webhook URL: http://localhost:5000/webhook")
    print(f"📡 API Status: http://localhost:5000/api/status")
    print("=" * 60)
    print("💡 Configure o EA com a URL: http://localhost:5000/webhook")
    print("🌐 O navegador será aberto automaticamente...")
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
    
    # Configuração do Waitress para melhor performance e robustez
    print("\n" + "="*60)
    print("🚀 Iniciando servidor Waitress (Produção)")
    print(f"📡 Servidor disponível em: http://127.0.0.1:5000")
    print(f"🌐 Dashboard: http://127.0.0.1:5000")
    print(f"📊 API Status: http://127.0.0.1:5000/api/latest")
    print("⚡ Servidor otimizado para alta performance")
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