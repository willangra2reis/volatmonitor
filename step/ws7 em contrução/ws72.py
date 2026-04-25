#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Webhook Local para receber dados do EA MetaTrader 5
Salva os dados e serve uma página web para visualização
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
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
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .status {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.2);
            font-weight: bold;
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
        }
        
        .card h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
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
        }
        
        .info-value {
            font-weight: bold;
            color: #2a5298;
        }
        
        .trades-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .trades-wrapper {
            max-height: 400px;
            overflow-y: auto;
            border-radius: 10px;
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
        
        .trades-table td {
            padding: 12px 10px;
            border-bottom: 1px solid #eee;
            background: white;
        }
        
        .trades-table tr:hover td {
            background: #f8f9fa;
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
    <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
</head>
<body>
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
            <h1>Monitor MetaTrader 5</h1>
            <div class="status" id="status">Conectado</div>
        </div>

        <main class="content">
            <!-- Metas e Limites -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card shadow-sm">
                        <div class="card-body">
                            <h5 class="card-title"><i class="fas fa-bullseye me-2"></i>Metas e Limites Diários</h5>
                            <div class="row align-items-end">
                                <div class="col-md-4">
                                    <label for="goal-percent" class="form-label">Meta de Ganho (%)</label>
                                    <input type="number" id="goal-percent" class="form-control" value="2">
                                </div>
                                <div class="col-md-4">
                                    <label for="limit-percent" class="form-label">Limite de Perda (%)</label>
                                    <input type="number" id="limit-percent" class="form-control" value="1">
                                </div>
                                <div class="col-md-4">
                                    <button id="save-goals" class="btn btn-primary w-100">Salvar</button>
                                </div>
                            </div>
                            <div class="progress-container mt-3">
                                <div class="progress-dual">
                                    <div id="goal-progress-bar" class="progress-bar bg-success" role="progressbar" style="width: 0%;"></div>
                                    <div id="limit-progress-bar" class="progress-bar bg-danger" role="progressbar" style="width: 0%;"></div>
                                </div>
                                <div id="progress-text" class="progress-text-center">0%</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Cards de Informação -->
            <div class="row">
                <div class="col-md-6 col-lg-3 mb-4">
                    <div class="card h-100 shadow-sm border-start border-primary border-4">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="card-subtitle text-muted">Saldo Atual</h6>
                                    <h4 class="card-title fw-bold mb-0" id="balance">$0.00</h4>
                                </div>
                                <i class="fas fa-wallet fa-2x text-primary opacity-75"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 col-lg-3 mb-4">
                    <div class="card h-100 shadow-sm border-start border-info border-4">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="card-subtitle text-muted">Patrimônio (Equity)</h6>
                                    <h4 class="card-title fw-bold mb-0" id="equity">$0.00</h4>
                                </div>
                                <i class="fas fa-chart-pie fa-2x text-info opacity-75"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 col-lg-3 mb-4">
                    <div class="card h-100 shadow-sm border-start border-warning border-4">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="card-subtitle text-muted">Lucro/Prejuízo do Dia</h6>
                                    <h4 class="card-title fw-bold mb-0" id="profit">$0.00</h4>
                                </div>
                                <i class="fas fa-dollar-sign fa-2x text-warning opacity-75"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 col-lg-3 mb-4">
                    <div class="card h-100 shadow-sm border-start border-secondary border-4">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="card-subtitle text-muted">Trades no Dia</h6>
                                    <h4 class="card-title fw-bold mb-0" id="trades-today">0</h4>
                                </div>
                                <i class="fas fa-exchange-alt fa-2x text-secondary opacity-75"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Gráficos e Metas -->
            <div class="row">
                <div class="col-12 mb-4">
                    <div class="card h-100 shadow-sm border-light-subtle">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title"><i class="fas fa-chart-line me-2 text-primary"></i>Evolução do Saldo e Equity</h5>
                            <div class="chart-container flex-grow-1">
                                <canvas id="evolutionChart"></canvas>
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
                                     <div class="text-center mt-2 small text-muted" id="monthly-projection">Projeção Mensal: <b>$0.00</b></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Outros Gráficos e Tabela de Trades -->
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
                <div class="col-lg-4 mb-4">
                    <div class="card shadow-sm h-100">
                        <div class="card-header">
                            <h6 class="card-title mb-0"><i class="fas fa-chart-pie me-2"></i>Distribuição de Trades</h6>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="distributionChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4 mb-4">
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
                            <div class="table-responsive">
                                <table class="table table-striped table-hover table-sm mb-0 trade-table">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>#</th>
                                            <th>Ticket</th>
                                            <th>Hora de Abertura</th>
                                            <th>Tipo</th>
                                            <th>Volume</th>
                                            <th>Símbolo</th>
                                            <th>Preço de Abertura</th>
                                            <th>Preço de Fechamento</th>
                                            <th>Lucro</th>
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

        <div class="last-update" id="last-update">
            Última atualização: Aguardando...
        </div>
    </div>

    <script>
        let profitChart = null;
        let symbolChart = null;
        let evolutionChart = null;
        let timeGroupedChart = null; // Gráfico de consolidação por tempo
        let distributionChart = null; // Gráfico de distribuição de trades
        let lastDataHash = '';
        let lastTradesHash = '';
        let isUpdating = false;
        let cachedTradesData = []; // Cache dos trades para evitar problemas de sincronia
        let cachedBalanceHistory = []; // Cache para dados de evolução
        
        // --- Lógica de Metas e Limites ---
        let initialBalance = null;
        let goalReachedToday = false;
        let lossLimitReachedToday = false;
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
            const formatted = formatCurrency(Math.abs(value));
            return value >= 0 ? '+' + formatted : '-' + formatted;
        }
        
        // Função para gerar hash simples dos dados
        function generateHash(data) {
            return JSON.stringify(data).split('').reduce((a, b) => {
                a = ((a << 5) - a) + b.charCodeAt(0);
                return a & a;
            }, 0);
        }
        
        function updateDailyMetrics(accountInfo) {
            if (!accountInfo || typeof accountInfo.account_balance === 'undefined') return;

            if (initialBalance === null) {
                initialBalance = accountInfo.account_balance - accountInfo.account_profit;
            }

            const goalPercentage = parseFloat(dailyGoalInput.value) || 0;
            const lossLimitPercentage = parseFloat(lossLimitInput.value) || 0;
            const dailyProfit = accountInfo.account_profit;

            const goalTarget = initialBalance * (goalPercentage / 100);
            const lossLimitTarget = -initialBalance * (lossLimitPercentage / 100); // Valor negativo

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
            
            if (!evolutionChart) {
                evolutionChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Saldo ($)',
                            data: balanceData,
                            borderColor: 'rgba(40, 167, 69, 1)',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            borderWidth: 3,
                            fill: false,
                            tension: 0.4,
                            pointBackgroundColor: 'rgba(40, 167, 69, 1)',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        }, {
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
                            pointRadius: 4,
                            pointHoverRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: {
                            duration: 750,
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
                                    text: 'Hora'
                                },
                                grid: {
                                    color: 'rgba(0,0,0,0.1)'
                                }
                            },
                            y: {
                                display: true,
                                title: {
                                    display: true,
                                    text: 'Valor ($)'
                                },
                                ticks: {
                                    callback: function(value) {
                                        return '$' + value.toFixed(2);
                                    }
                                },
                                grid: {
                                    color: 'rgba(0,0,0,0.1)'
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top'
                            },
                            tooltip: {
                                callbacks: {
                                    title: function(context) {
                                        // Usa o cache para garantir dados corretos
                                        const index = context[0].dataIndex;
                                        if (cachedBalanceHistory[index]) {
                                            return moment(cachedBalanceHistory[index].timestamp).format('DD/MM/YYYY HH:mm:ss');
                                        }
                                        return '';
                                    },
                                    label: function(context) {
                                        return context.dataset.label + ': $' + context.parsed.y.toFixed(2);
                                    }
                                }
                            }
                        }
                    }
                });
            } else {
                // Atualiza dados existentes e recria callbacks para usar dados atualizados
                evolutionChart.data.labels = labels;
                evolutionChart.data.datasets[0].data = balanceData;
                evolutionChart.data.datasets[1].data = equityData;
                
                // Recria o callback do tooltip com dados atualizados
                evolutionChart.options.plugins.tooltip.callbacks.title = function(context) {
                    const index = context[0].dataIndex;
                    if (cachedBalanceHistory[index]) {
                        return moment(cachedBalanceHistory[index].timestamp).format('DD/MM/YYYY HH:mm:ss');
                    }
                    return '';
                };
                
                evolutionChart.update('none');
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
            const intervalMinutes = parseInt(document.getElementById('time-group-selector').value);
            console.log('Intervalo selecionado:', intervalMinutes); // Debug

            if (!trades || trades.length === 0) {
                if (timeGroupedChart) timeGroupedChart.destroy();
                timeGroupedChart = null;
                return;
            }

            const groupedData = trades.reduce((acc, trade) => {
                const tradeTime = moment(trade.time);
                const roundedTime = tradeTime.startOf('minute').subtract(tradeTime.minute() % intervalMinutes, 'minutes');
                const key = roundedTime.format('YYYY-MM-DD HH:mm');

                if (!acc[key]) {
                    acc[key] = { profit: 0 };
                }
                acc[key].profit += parseFloat(trade.profit);
                return acc;
            }, {});

            const sortedKeys = Object.keys(groupedData).sort((a, b) => moment(a, 'YYYY-MM-DD HH:mm').diff(moment(b, 'YYYY-MM-DD HH:mm')));

            const labels = sortedKeys.map(key => moment(key, 'YYYY-MM-DD HH:mm').format('HH:mm'));
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
            // --- Atualização dos Cards Principais ---
            if (changes.accountInfoChanged) {
                const accountInfo = data.account_info || {};
                document.getElementById('balance').textContent = formatCurrency(accountInfo.account_balance || 0);
                document.getElementById('equity').textContent = formatCurrency(accountInfo.account_equity || 0);
                updateDailyMetrics(accountInfo);
            }

            // --- Atualização da Tabela e Gráficos de Trades ---
            if (changes.tradesChanged) {
                const trades = data.last_trades || [];
                updateTradesTable(trades);
                createProfitChart(trades);
                createSymbolChart(trades);
                // A função updateDistributionChart não foi definida, então a comento para evitar erros.
                // updateDistributionChart(trades);
                updateTimeGroupedChart(trades);
            }

            // --- Atualização do Gráfico de Evolução ---
            if (changes.balanceHistoryChanged) {
                createEvolutionChart(data.balance_history || []);
            }
            
            // --- Atualização dos Cálculos do Dia (baseado em trades ou account_info) ---
            const today = moment(data.timestamp).startOf('day');
            const tradesToday = (data.last_trades || []).filter(trade => moment(trade.time).isSame(today, 'day'));
            const profitToday = tradesToday.reduce((sum, trade) => sum + parseFloat(trade.profit), 0);
            const tradesTodayCount = tradesToday.length;

            const profitElement = document.getElementById('profit');
            profitElement.textContent = formatProfit(profitToday);
            profitElement.classList.toggle('profit-positive', profitToday >= 0);
            profitElement.classList.toggle('profit-negative', profitToday < 0);
            document.getElementById('trades-today').textContent = tradesTodayCount;

            // --- Atualização do Timestamp ---
            document.getElementById('last-update').textContent = 'Última atualização: ' + moment(data.timestamp).format('DD/MM/YYYY HH:mm:ss');
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

            tbody.innerHTML = '';
            trades.forEach((trade, index) => {
                const row = tbody.insertRow();
                row.innerHTML = 
                    `<td>${index + 1}</td>` +
                    `<td>${trade.ticket}</td>` +
                    `<td>${moment(trade.time).format('DD/MM/YY HH:mm:ss')}</td>` +
                    `<td><span style="color: ${trade.type === 'BUY' ? '#28a745' : '#dc3545'}">${trade.type}</span></td>` +
                    `<td>${trade.volume}</td>` +
                    `<td><strong>${trade.symbol}</strong></td>` +
                    `<td>${parseFloat(trade.price).toFixed(5)}</td>` +
                    `<td>${parseFloat(trade.close_price || 0).toFixed(5)}</td>` +
                    `<td class="${trade.profit >= 0 ? 'profit-positive' : 'profit-negative'}">${formatProfit(trade.profit)}</td>`;
            });
        }

        function updateData() {
            if (isUpdating) return;
            isUpdating = true;

            Promise.all([
                fetch('/api/latest').then(r => r.json()),
                fetch('/api/balance-history').then(r => r.json())
            ])
            .then(([latest, history]) => {
                const data = { ...latest, balance_history: history.balance_history };
                
                // Armazena dados para acesso global
                window.lastApiData = data;
                cachedTradesData = data.last_trades || [];
                cachedBalanceHistory = data.balance_history || [];

                const changes = detectChanges(data);
                if (changes.hasChanges) {
                    updateUI(data, changes);
                }
            })
            .catch(error => {
                console.error('Erro ao buscar dados:', error);
                const statusElement = document.getElementById('status');
                statusElement.textContent = '🔴 Desconectado';
                statusElement.style.background = 'rgba(220, 53, 69, 0.3)';
            })
            .finally(() => {
                isUpdating = false;
            });
        }

        document.addEventListener('DOMContentLoaded', function () {
            // Inicializa hashes para detecção de mudanças
            window.lastAccountHash = '';
            window.lastTradesHash = '';
            window.lastBalanceHistoryHash = '';

            setupGoalAndLimitControls();
            updateData();
            setInterval(updateData, 1500);

            document.getElementById('time-group-selector').addEventListener('change', function() {
                console.log('Seletor alterado para:', this.value); // Debug
                if (cachedTradesData && cachedTradesData.length > 0) {
                    updateTimeGroupedChart(cachedTradesData);
                } else {
                    console.log('Nenhum dado de trade em cache para atualizar o gráfico');
                }
            });
        });
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
    return jsonify(list(balance_history))

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

def open_browser():
    """Abre o navegador automaticamente"""
    import time
    time.sleep(1.5)  # Aguarda o servidor iniciar
    webbrowser.open('http://localhost:5001')

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SERVIDOR WEBHOOK LOCAL INICIADO")
    print("=" * 60)
    print(f"📊 Dashboard: http://localhost:5001")
    print(f"🔗 Webhook URL: http://localhost:5001/webhook")
    print(f"📡 API Status: http://localhost:5001/api/status")
    print("=" * 60)
    print("💡 Configure o EA com a URL: http://localhost:5001/webhook")
    print("🌐 O navegador será aberto automaticamente...")
    print("=" * 60)
    
    # Abre o navegador em uma thread separada
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Limpar dados antigos ao iniciar (opcional)
    trade_history.clear()
    balance_history.clear()
    app.run(debug=True, host='0.0.0.0', port=5001)