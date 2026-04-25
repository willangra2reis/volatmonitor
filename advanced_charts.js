// ==================== GRÁFICOS AVANÇADOS ====================

let priceChartAdvanced = null;
let zscoreChartGlobal = null;
let rsiChartGlobal = null;
let currentChartSymbol = 'XAUUSD';
let chartUpdateInterval = null;

// Função para abrir modal de gráficos
function openAdvancedChart() {
    const modal = document.getElementById('advanced-chart-modal');
    modal.style.display = 'block';
    
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

// Inicializar gráficos
async function initializeAdvancedCharts() {
    try {
        // Buscar dados
        const priceResponse = await fetch(`/api/price-history/${currentChartSymbol}`);
        const priceData = await priceResponse.json();
        
        const indicatorResponse = await fetch(`/api/indicators/${currentChartSymbol}`);
        const indicatorData = await indicatorResponse.json();
        
        // Criar gráficos
        createPriceChartAdvanced(priceData, indicatorData);
        createZScoreChart(indicatorData);
        
        // Verificar se RSI está ativado
        const rsiCheckbox = document.getElementById('ind-rsi');
        if (rsiCheckbox && rsiCheckbox.checked) {
            document.getElementById('rsi-section').style.display = 'block';
            createRSIChart(indicatorData);
        }
        
        console.log('[CHARTS] Gráficos inicializados com sucesso');
    } catch (error) {
        console.error('[CHARTS] Erro ao inicializar gráficos:', error);
    }
}

// Criar gráfico de preço com indicadores
function createPriceChartAdvanced(priceData, indicatorData) {
    const ctx = document.getElementById('priceChartAdvanced').getContext('2d');
    
    if (!priceData.data || priceData.data.length === 0) {
        console.warn('[CHARTS] Sem dados de preço disponíveis');
        return;
    }
    
    // Preparar dados
    const labels = priceData.data.map(p => moment(p.timestamp).format('HH:mm:ss'));
    const prices = priceData.data.map(p => p.price);
    
    // Datasets
    const datasets = [
        {
            label: 'Preço',
            data: prices,
            borderColor: '#4fc3f7',
            backgroundColor: 'rgba(79, 195, 247, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 5
        }
    ];
    
    // Adicionar Hull MA se ativado
    if (document.getElementById('ind-hull').checked && indicatorData.data && indicatorData.data.hull_ma) {
        datasets.push({
            label: 'Hull MA',
            data: indicatorData.data.hull_ma,
            borderColor: '#4caf50',
            backgroundColor: 'transparent',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 5
        });
    }
    
    // Destruir gráfico anterior se existir
    if (priceChartAdvanced) {
        priceChartAdvanced.destroy();
    }
    
    // Criar novo gráfico
    priceChartAdvanced = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 300
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
                        text: 'Tempo',
                        color: '#aaa'
                    },
                    ticks: {
                        color: '#aaa',
                        maxTicksLimit: 15
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Preço',
                        color: '#aaa'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(2);
                        },
                        color: '#aaa'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#aaa',
                        usePointStyle: true
                    }
                },
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
    
    // Atualizar info panel
    if (prices.length > 0) {
        document.getElementById('chart-last-price').textContent = prices[prices.length - 1].toFixed(2);
    }
}

// Criar gráfico de Z-Score
function createZScoreChart(indicatorData) {
    const ctx = document.getElementById('zscoreChart').getContext('2d');
    
    if (!indicatorData.data || !indicatorData.data.zscore || indicatorData.data.zscore.length === 0) {
        console.warn('[CHARTS] Sem dados de Z-Score disponíveis');
        return;
    }
    
    const labels = indicatorData.data.timestamps.map(t => moment(t).format('HH:mm:ss'));
    const zscores = indicatorData.data.zscore;
    
    // Destruir gráfico anterior se existir
    if (zscoreChartGlobal) {
        zscoreChartGlobal.destroy();
    }
    
    // Criar novo gráfico
    zscoreChartGlobal = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Z-Score',
                data: zscores,
                borderColor: '#f44336',
                backgroundColor: 'rgba(244, 67, 54, 0.1)',
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
            animation: {
                duration: 300
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                x: {
                    display: true,
                    ticks: {
                        color: '#aaa',
                        maxTicksLimit: 15
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Z-Score',
                        color: '#aaa'
                    },
                    ticks: {
                        color: '#aaa'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#aaa'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(244, 67, 54, 0.5)',
                    borderWidth: 1
                }
            }
        }
    });
    
    // Atualizar info panel
    if (zscores.length > 0) {
        const lastZScore = zscores[zscores.length - 1];
        document.getElementById('chart-zscore-value').textContent = lastZScore ? lastZScore.toFixed(4) : '-';
    }
}

// Criar gráfico de RSI
function createRSIChart(indicatorData) {
    const ctx = document.getElementById('rsiChart').getContext('2d');
    
    if (!indicatorData.data || !indicatorData.data.rsi || indicatorData.data.rsi.length === 0) {
        console.warn('[CHARTS] Sem dados de RSI disponíveis');
        return;
    }
    
    const labels = indicatorData.data.timestamps.map(t => moment(t).format('HH:mm:ss'));
    const rsiValues = indicatorData.data.rsi;
    
    // Destruir gráfico anterior se existir
    if (rsiChartGlobal) {
        rsiChartGlobal.destroy();
    }
    
    // Criar novo gráfico
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
            animation: {
                duration: 300
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                x: {
                    display: true,
                    ticks: {
                        color: '#aaa',
                        maxTicksLimit: 15
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'RSI',
                        color: '#aaa'
                    },
                    min: 0,
                    max: 100,
                    ticks: {
                        color: '#aaa'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#aaa'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(156, 39, 176, 0.5)',
                    borderWidth: 1
                }
            }
        }
    });
    
    // Atualizar info panel
    if (rsiValues.length > 0) {
        const lastRSI = rsiValues[rsiValues.length - 1];
        document.getElementById('chart-rsi-value').textContent = lastRSI ? lastRSI.toFixed(2) : '-';
    }
}

// Iniciar atualizações automáticas dos gráficos
function startChartUpdates() {
    chartUpdateInterval = setInterval(async () => {
        try {
            await updateAdvancedCharts();
        } catch (error) {
            console.error('[CHARTS] Erro ao atualizar gráficos:', error);
        }
    }, 2000);
}

// Atualizar gráficos
async function updateAdvancedCharts() {
    try {
        const priceResponse = await fetch(`/api/price-history/${currentChartSymbol}`);
        const priceData = await priceResponse.json();
        
        const indicatorResponse = await fetch(`/api/indicators/${currentChartSymbol}`);
        const indicatorData = await indicatorResponse.json();
        
        if (priceChartAdvanced && priceData.data && priceData.data.length > 0) {
            const labels = priceData.data.map(p => moment(p.timestamp).format('HH:mm:ss'));
            const prices = priceData.data.map(p => p.price);
            
            priceChartAdvanced.data.labels = labels;
            priceChartAdvanced.data.datasets[0].data = prices;
            priceChartAdvanced.update('none');
            
            document.getElementById('chart-last-price').textContent = prices[prices.length - 1].toFixed(2);
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
        
    } catch (error) {
        console.error('[CHARTS] Erro ao atualizar:', error);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = ['ind-hull', 'ind-sma', 'ind-ema', 'ind-bollinger', 'ind-zscore', 'ind-rsi'];
    checkboxes.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                if (id === 'ind-rsi') {
                    const rsiSection = document.getElementById('rsi-section');
                    if (this.checked) {
                        rsiSection.style.display = 'block';
                    } else {
                        rsiSection.style.display = 'none';
                    }
                }
                
                if (document.getElementById('advanced-chart-modal').style.display === 'block') {
                    initializeAdvancedCharts();
                }
            });
        }
    });
});

window.onclick = function(event) {
    const modal = document.getElementById('advanced-chart-modal');
    if (event.target == modal) {
        closeAdvancedChart();
    }
}
