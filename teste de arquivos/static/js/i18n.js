// Sistema de Internacionalização (i18n) para VolatForex Monitor Pro
// Suporte para: Português, Inglês, Espanhol, Francês e Alemão

const translations = {
    'pt': {
        // Login Page
        'login_title': 'Login - VolatForex Monitor Pro',
        'login_subtitle': 'Digite seu email para acessar o sistema',
        'email_label': 'Email:',
        'remember_me': 'Lembrar login',
        'login_button': 'Entrar',
        'or_text': 'ou',
        'acquire_access': 'Adquirir Acesso',
        'restricted_access': 'Acesso restrito apenas para usuários com licença aprovada',
        'security_notice': 'Seus dados MT5 nunca saem da sua máquina. Processamento 100% local, sem armazenamento em nuvem.',
        'need_help': 'Precisa de ajuda?',
        'loading_text': 'Autenticando...',
        'loading_subtext': 'Verificando suas credenciais',
        
        // Language Selector
        'select_language': 'Selecionar Idioma',
        'language_selection': 'Seleção de Idioma',
        'choose_language': 'Escolha seu idioma preferido:',
        'continue_button': 'Continuar',
        
        // Dashboard
        'dashboard_title': 'Monitor MT5 - Dashboard',
        'connected_status': 'Conectado',
        'disconnected_status': 'Desconectado',
        'current_balance': 'Saldo Atual',
        'equity': 'Equity',
        'daily_pl': 'L/P do Dia',
        'trades_today': 'Trades Hoje',
        'open_trades': 'Trades Abertos',
        'close_all': 'Fechar Todas',
        'close_positive': 'Fechar +',
        'close_negative': 'Fechar Negativas',
        'no_open_trades': 'Nenhum trade aberto no momento',
        'frequency_label': 'Frequência:',
        'last_update': 'Última atualização:',
        'waiting': 'Aguardando...',
        'synchronizing': 'Sincronizando...',
        
        // Goal Modal
        'goal_reached_title': '🎉 Parabéns! Meta Atingida! 🎉',
        'goal_reached_message': 'Você alcançou sua meta diária de',
        'goal_reached_advice': 'Excelente trabalho! Lembre-se que a disciplina é a chave para o sucesso a longo prazo. Considere fazer uma pausa e proteger seus lucros.',
        'goal_recommendation': 'Recomendação: Pare de operar por hoje e volte amanhã com a mesma disciplina.',
        'goal_hashtags': '#StopLoss #StopGain #Disciplina',
        
        // Loss Limit Modal
        'loss_limit_title': '🚨 Atenção! Limite de Perda Atingido! 🚨',
        'loss_limit_message': 'Você atingiu seu limite diário de perda de',
        'loss_limit_warning': 'Pare de operar imediatamente! A disciplina é crucial para proteger seu capital e garantir sua sobrevivência no mercado.',
        'loss_recommendation': 'Recomendação: Feche a plataforma, revise suas operações e volte amanhã com a mente renovada.',
        'loss_hashtags': '#StopLoss #GerenciamentoDeRisco #Disciplina',
        
        // Dashboard Sections
        'symbol_distribution': 'Distribuição por Símbolo',
        'profit_loss_chart': 'Lucro/Prejuízo (Últimos 15 Trades)',
        'consolidated_result': 'Resultado Consolidado por Tempo',
        'recent_trades_history': 'Histórico de Trades Recentes',
        'goals_and_limits': 'Metas e Limites',
        'profit_loss_label': 'Lucro/Prejuízo ($)',
        'consolidated_result_label': 'Resultado Consolidado',
        
        // Time intervals
        'minutes_5': '5 minutos',
        'minutes_15': '15 minutos',
        'minutes_30': '30 minutos',
        'hour_1': '1 hora',
        'hours_4': '4 horas',
        'day_1': '1 dia',
        
        // Trade table headers
        'ticket': 'Ticket',
        'symbol': 'Símbolo',
        'type': 'Tipo',
        'volume': 'Volume',
        'open_price': 'Preço Abertura',
        'monthly_projection': 'Projeção Mensal',
        'controls': 'Controles',
        'profit_goal': 'Meta Ganho',
        'loss_limit': 'Limite Perda',
        'daily_progress': 'Progresso Diário',
        'loss_limit_text': 'Limite de perda',
        'profit_goal_text': 'Meta de ganho',
        
        // Progress messages - Loss
        'risk_low': 'Risco baixo',
        'attention': 'Atenção',
        'risk_high': 'Risco alto',
        'critical_danger': 'Perigo crítico',
        
        // Progress messages - Gain
        'progressing': 'Progredindo',
        'good_pace': 'Bom ritmo',
        'almost_there': 'Quase lá',
        'very_close': 'Muito perto',
        'goal_achieved': 'Meta alcançada',
        
        // Confirmation popups
        'confirm_close_all': 'Tem certeza que deseja fechar TODAS as ordens abertas?',
        'confirm_close_positive': 'Tem certeza que deseja fechar todas as ordens POSITIVAS?',
        'confirm_close_negative': 'Tem certeza que deseja fechar todas as ordens NEGATIVAS?',
        'confirm_close_individual': 'Tem certeza que deseja fechar a ordem #',
        'confirm_logout': 'Tem certeza que deseja sair?',
        'time': 'Tempo',
        'swap': 'Swap',
        'commission': 'Comissão',
        
        // Access Denied Page
        'access_denied_title': 'Acesso Negado - VolatForex Monitor Pro',
        'access_denied_header': 'Acesso Negado',
        'access_denied_hello': 'Olá',
        'access_denied_message': 'Identificamos sua conta, mas ela ainda não possui autorização para acessar o',
        'access_denied_message_no_user': 'Sua conta não possui autorização para acessar o',
        'access_denied_to_get_access': 'para obter acesso completo:',
        'access_denied_to_get_access_no_user': 'Para obter acesso completo:',
        'access_denied_reason_1': '✅ Sua assinatura expirou (venceu)',
        'access_denied_reason_2': '⏳ Sua assinatura foi cancelada por falta de pagamento',
        'access_denied_reason_3': '🎯 Adquira o acesso clicando no botão abaixo',
        'access_denied_acquire_button': '🚀 Adquirir o Acesso',
        'access_denied_back_button': '🔄 Voltar ao Login',
        'access_denied_footer': 'Após a compra, seu acesso será liberado automaticamente. Dúvidas?',
        
        // Login Error Messages
        'error_email_not_found': 'Email não encontrado no sistema. Verifique seu email ou adquira o acesso.',
        'error_email_required': 'Email é obrigatório',
        'error_login_failed': 'Erro ao fazer login. Tente novamente.',
        
        // Advanced Charts Modal
        'technical_analysis': 'Volat Scalper Pro',
        'loading_data': 'Coletando dados de mercado...',
        'loading_subtitle': 'Aguarde enquanto reunimos ticks suficientes para análise precisa',
        'select_asset': 'Selecionar Ativo:',
        'select_or_type': '-- Selecione ou digite abaixo --',
        'or_type_symbol': 'Ou digite o símbolo:',
        'load_button': 'Carregar',
        'moving_averages': 'Médias Móveis:',
        'hull_ma': 'Hull MA',
        'oscillators': 'Osciladores:',
        'zscore': 'Z-Score',
        'rsi': 'RSI',
        'visualization': 'Visualização:',
        'show_points': 'Mostrar Pontos',
        'last_price': 'Último Preço',
        'hull_value': 'Hull MA',
        'zscore_value': 'Z-Score',
        'rsi_value': 'RSI',
        'last_update_charts': 'Última Atualização',
        'metals': 'Metais',
        'forex_major': 'Forex Principais',
        'forex_cross': 'Forex Cruzados',
        'commodities': 'Commodities',
        'crypto': 'Criptomoedas',
        'indices': 'Índices'
    },
    
    'en': {
        // Login Page
        'login_title': 'Login - VolatForex Monitor Pro',
        'login_subtitle': 'Enter your email to access the system',
        'email_label': 'Email:',
        'remember_me': 'Remember login',
        'login_button': 'Login',
        'or_text': 'or',
        'acquire_access': 'Get Access',
        'restricted_access': 'Restricted access for licensed users only',
        'security_notice': 'Your MT5 data never leaves your machine. 100% local processing, no cloud storage.',
        'need_help': 'Need help?',
        'loading_text': 'Authenticating...',
        'loading_subtext': 'Verifying your credentials',
        
        // Language Selector
        'select_language': 'Select Language',
        'language_selection': 'Language Selection',
        'choose_language': 'Choose your preferred language:',
        'continue_button': 'Continue',
        
        // Dashboard
        'dashboard_title': 'MT5 Monitor - Dashboard',
        'connected_status': 'Connected',
        'disconnected_status': 'Disconnected',
        'current_balance': 'Current Balance',
        'equity': 'Equity',
        'daily_pl': 'Daily P/L',
        'trades_today': 'Trades Today',
        'open_trades': 'Open Trades',
        'close_all': 'Close All',
        'close_positive': 'Close +',
        'close_negative': 'Close Negative',
        'no_open_trades': 'No open trades at the moment',
        'frequency_label': 'Frequency:',
        'last_update': 'Last update:',
        'waiting': 'Waiting...',
        'synchronizing': 'Synchronizing...',
        
        // Goal Modal
        'goal_reached_title': '🎉 Congratulations! Goal Achieved! 🎉',
        'goal_reached_message': 'You have reached your daily goal of',
        'goal_reached_advice': 'Excellent work! Remember that discipline is the key to long-term success. Consider taking a break and protecting your profits.',
        'goal_recommendation': 'Recommendation: Stop trading for today and come back tomorrow with the same discipline.',
        'goal_hashtags': '#StopLoss #StopGain #Discipline',
        
        // Loss Limit Modal
        'loss_limit_title': '🚨 Warning! Loss Limit Reached! 🚨',
        'loss_limit_message': 'You have reached your daily loss limit of',
        'loss_limit_warning': 'Stop trading immediately! Discipline is crucial to protect your capital and ensure your survival in the market.',
        'loss_recommendation': 'Recommendation: Close the platform, review your trades and come back tomorrow with a renewed mind.',
        'loss_hashtags': '#StopLoss #RiskManagement #Discipline',
        
        // Dashboard Sections
        'symbol_distribution': 'Symbol Distribution',
        'profit_loss_chart': 'Profit/Loss (Last 15 Trades)',
        'consolidated_result': 'Consolidated Result by Time',
        'recent_trades_history': 'Recent Trades History',
        'goals_and_limits': 'Goals and Limits',
        'profit_loss_label': 'Profit/Loss ($)',
        'consolidated_result_label': 'Consolidated Result',
        
        // Time intervals
        'minutes_5': '5 minutes',
        'minutes_15': '15 minutes',
        'minutes_30': '30 minutes',
        'hour_1': '1 hour',
        'hours_4': '4 hours',
        'day_1': '1 day',
        
        // Trade table headers
        'ticket': 'Ticket',
        'symbol': 'Symbol',
        'type': 'Type',
        'volume': 'Volume',
        'open_price': 'Open Price',
        'current_price': 'Current Price',
        'profit': 'Profit',
        'time': 'Time',
        'swap': 'Swap',
        'commission': 'Commission',
        'profit_goal': 'Profit Goal',
        'loss_limit': 'Loss Limit',
        'daily_progress': 'Daily Progress',
        'loss_limit_text': 'Loss limit',
        'profit_goal_text': 'Profit goal',
        
        // Progress messages - Loss
        'risk_low': 'Low risk',
        'attention': 'Attention',
        'risk_high': 'High risk',
        'critical_danger': 'Critical danger',
        
        // Progress messages - Gain
        'progressing': 'Progressing',
        'good_pace': 'Good pace',
        'almost_there': 'Almost there',
        'very_close': 'Very close',
        'goal_achieved': 'Goal achieved',
        
        // Confirmation popups
        'confirm_close_all': 'Are you sure you want to close ALL open orders?',
        'confirm_close_positive': 'Are you sure you want to close all POSITIVE orders?',
        'confirm_close_negative': 'Are you sure you want to close all NEGATIVE orders?',
        'confirm_close_individual': 'Are you sure you want to close order #',
        'confirm_logout': 'Are you sure you want to logout?',
        
        // Access Denied Page
        'access_denied_title': 'Access Denied - VolatForex Monitor Pro',
        'access_denied_header': 'Access Denied',
        'access_denied_hello': 'Hello',
        'access_denied_message': 'We identified your account, but it does not yet have authorization to access',
        'access_denied_message_no_user': 'Your account does not have authorization to access',
        'access_denied_to_get_access': 'to get full access:',
        'access_denied_to_get_access_no_user': 'To get full access:',
        'access_denied_reason_1': '✅ Your subscription has expired',
        'access_denied_reason_2': '⏳ Your subscription was cancelled due to non-payment',
        'access_denied_reason_3': '🎯 Get access by clicking the button below',
        'access_denied_acquire_button': '🚀 Get Access',
        'access_denied_back_button': '🔄 Back to Login',
        'access_denied_footer': 'After purchase, your access will be automatically activated. Questions?',
        
        // Login Error Messages
        'error_email_not_found': 'Email not found in the system. Check your email or get access.',
        'error_email_required': 'Email is required',
        'error_login_failed': 'Login error. Please try again.',
        
        // Advanced Charts Modal
        'technical_analysis': 'Volat Scalper Pro',
        'loading_data': 'Collecting market data...',
        'loading_subtitle': 'Please wait while we gather enough ticks for accurate analysis',
        'select_asset': 'Select Asset:',
        'select_or_type': '-- Select or type below --',
        'or_type_symbol': 'Or type the symbol:',
        'load_button': 'Load',
        'moving_averages': 'Moving Averages:',
        'hull_ma': 'Hull MA',
        'oscillators': 'Oscillators:',
        'zscore': 'Z-Score',
        'rsi': 'RSI',
        'visualization': 'Visualization:',
        'show_points': 'Show Points',
        'last_price': 'Last Price',
        'hull_value': 'Hull MA',
        'zscore_value': 'Z-Score',
        'rsi_value': 'RSI',
        'last_update_charts': 'Last Update',
        'metals': 'Metals',
        'forex_major': 'Major Forex',
        'forex_cross': 'Cross Forex',
        'commodities': 'Commodities',
        'crypto': 'Cryptocurrencies',
        'indices': 'Indices'
    },
    
    'es': {
        // Login Page
        'login_title': 'Iniciar Sesión - VolatForex Monitor Pro',
        'login_subtitle': 'Ingrese su email para acceder al sistema',
        'email_label': 'Email:',
        'remember_me': 'Recordar inicio de sesión',
        'login_button': 'Entrar',
        'or_text': 'o',
        'acquire_access': 'Obtener Acceso',
        'restricted_access': 'Acceso restringido solo para usuarios con licencia aprobada',
        'security_notice': 'Seguridad Total: Tus datos MT5 nunca salen de tu máquina. Procesamiento 100% local, sin almacenamiento en la nube.',
        'need_help': '¿Necesitas ayuda?',
        'loading_text': 'Autenticando...',
        'loading_subtext': 'Verificando tus credenciales',
        
        // Language Selector
        'select_language': 'Seleccionar Idioma',
        'language_selection': 'Selección de Idioma',
        'choose_language': 'Elige tu idioma preferido:',
        'continue_button': 'Continuar',
        
        // Dashboard
        'dashboard_title': 'Monitor MT5 - Panel',
        'connected_status': 'Conectado',
        'disconnected_status': 'Desconectado',
        'current_balance': 'Saldo Actual',
        'equity': 'Patrimonio',
        'daily_pl': 'G/P del Día',
        'trades_today': 'Operaciones Hoy',
        'open_trades': 'Operaciones Abiertas',
        'close_all': 'Cerrar Todas',
        'close_positive': 'Cerrar +',
        'close_negative': 'Cerrar Negativas',
        'no_open_trades': 'No hay operaciones abiertas en este momento',
        'frequency_label': 'Frecuencia:',
        'last_update': 'Última actualización:',
        'waiting': 'Esperando...',
        'synchronizing': 'Sincronizando...',
        
        // Goal Modal
        'goal_reached_title': '🎉 ¡Felicidades! ¡Meta Alcanzada! 🎉',
        'goal_reached_message': 'Has alcanzado tu meta diaria de',
        'goal_reached_advice': '¡Excelente trabajo! Recuerda que la disciplina es la clave del éxito a largo plazo. Considera tomar un descanso y proteger tus ganancias.',
        'goal_recommendation': 'Recomendación: Deja de operar por hoy y vuelve mañana con la misma disciplina.',
        'goal_hashtags': '#StopLoss #StopGain #Disciplina',
        
        // Loss Limit Modal
        'loss_limit_title': '🚨 ¡Atención! ¡Límite de Pérdida Alcanzado! 🚨',
        'loss_limit_message': 'Has alcanzado tu límite diario de pérdida de',
        'loss_limit_warning': '¡Deja de operar inmediatamente! La disciplina es crucial para proteger tu capital y garantizar tu supervivencia en el mercado.',
        'loss_recommendation': 'Recomendación: Cierra la plataforma, revisa tus operaciones y vuelve mañana con la mente renovada.',
        'loss_hashtags': '#StopLoss #GestiónDeRiesgo #Disciplina',
        
        // Dashboard Sections
        'symbol_distribution': 'Distribución por Símbolo',
        'profit_loss_chart': 'Ganancia/Pérdida (Últimos 15 Trades)',
        'consolidated_result': 'Resultado Consolidado por Tiempo',
        'recent_trades_history': 'Historial de Trades Recientes',
        'goals_and_limits': 'Metas y Límites',
        'profit_loss_label': 'Ganancia/Pérdida ($)',
        'consolidated_result_label': 'Resultado Consolidado',
        
        // Time intervals
        'minutes_5': '5 minutos',
        'minutes_15': '15 minutos',
        'minutes_30': '30 minutos',
        'hour_1': '1 hora',
        'hours_4': '4 horas',
        'day_1': '1 día',
        
        // Trade table headers
        'ticket': 'Ticket',
        'symbol': 'Símbolo',
        'type': 'Tipo',
        'volume': 'Volumen',
        'open_price': 'Precio Apertura',
        'current_price': 'Precio Actual',
        'profit': 'Ganancia',
        'time': 'Tiempo',
        'swap': 'Swap',
        'commission': 'Comisión',
        'profit_goal': 'Meta de Ganancia',
        'loss_limit': 'Límite de Pérdida',
        'daily_progress': 'Progreso Diario',
        'loss_limit_text': 'Límite de pérdida',
        'profit_goal_text': 'Meta de ganancia',
        
        // Progress messages - Loss
        'risk_low': 'Riesgo bajo',
        'attention': 'Atención',
        'risk_high': 'Riesgo alto',
        'critical_danger': 'Peligro crítico',
        
        // Progress messages - Gain
        'progressing': 'Progresando',
        'good_pace': 'Buen ritmo',
        'almost_there': 'Casi allí',
        'very_close': 'Muy cerca',
        'goal_achieved': 'Meta alcanzada',
        
        // Confirmation popups
        'confirm_close_all': '¿Está seguro de que desea cerrar TODAS las órdenes abiertas?',
        'confirm_close_positive': '¿Está seguro de que desea cerrar todas las órdenes POSITIVAS?',
        'confirm_close_negative': '¿Está seguro de que desea cerrar todas las órdenes NEGATIVAS?',
        'confirm_close_individual': '¿Está seguro de que desea cerrar la orden #',
        'confirm_logout': '¿Está seguro de que desea cerrar sesión?',
        
        // Access Denied Page
        'access_denied_title': 'Acceso Denegado - VolatForex Monitor Pro',
        'access_denied_header': 'Acceso Denegado',
        'access_denied_hello': 'Hola',
        'access_denied_message': 'Identificamos su cuenta, pero aún no tiene autorización para acceder a',
        'access_denied_message_no_user': 'Su cuenta no tiene autorización para acceder a',
        'access_denied_to_get_access': 'para obtener acceso completo:',
        'access_denied_to_get_access_no_user': 'Para obtener acceso completo:',
        'access_denied_reason_1': '✅ Su suscripción ha expirado (vencida)',
        'access_denied_reason_2': '⏳ Su suscripción fue cancelada por falta de pago',
        'access_denied_reason_3': '🎯 Obtenga acceso haciendo clic en el botón de abajo',
        'access_denied_acquire_button': '🚀 Obtener Acceso',
        'access_denied_back_button': '🔄 Volver al Login',
        'access_denied_footer': 'Después de la compra, su acceso se activará automáticamente. ¿Preguntas?',
        
        // Login Error Messages
        'error_email_not_found': 'Email no encontrado en el sistema. Verifique su email u obtenga acceso.',
        'error_email_required': 'El email es obligatorio',
        'error_login_failed': 'Error al iniciar sesión. Inténtelo de nuevo.',
        
        // Advanced Charts Modal
        'technical_analysis': 'Volat Scalper Pro',
        'loading_data': 'Recopilando datos del mercado...',
        'loading_subtitle': 'Espere mientras reunimos suficientes ticks para un análisis preciso',
        'select_asset': 'Seleccionar Activo:',
        'select_or_type': '-- Seleccione o escriba abajo --',
        'or_type_symbol': 'O escriba el símbolo:',
        'load_button': 'Cargar',
        'moving_averages': 'Medias Móviles:',
        'hull_ma': 'Hull MA',
        'oscillators': 'Osciladores:',
        'zscore': 'Z-Score',
        'rsi': 'RSI',
        'visualization': 'Visualización:',
        'show_points': 'Mostrar Puntos',
        'last_price': 'Último Precio',
        'hull_value': 'Hull MA',
        'zscore_value': 'Z-Score',
        'rsi_value': 'RSI',
        'last_update_charts': 'Última Actualización',
        'metals': 'Metales',
        'forex_major': 'Forex Principales',
        'forex_cross': 'Forex Cruzados',
        'commodities': 'Materias Primas',
        'crypto': 'Criptomonedas',
        'indices': 'Índices'
    },
    
    'fr': {
        // Login Page
        'login_title': 'Connexion - VolatForex Monitor Pro',
        'login_subtitle': 'Entrez votre email pour accéder au système',
        'email_label': 'Email:',
        'remember_me': 'Se souvenir de la connexion',
        'login_button': 'Se connecter',
        'or_text': 'ou',
        'acquire_access': 'Obtenir l\'Accès',
        'restricted_access': 'Accès restreint aux utilisateurs avec licence approuvée uniquement',
        'security_notice': 'Vos données MT5 ne quittent jamais votre machine. Traitement 100% local, aucun stockage cloud.',
        'need_help': 'Besoin d\'aide?',
        'loading_text': 'Authentification...',
        'loading_subtext': 'Vérification de vos identifiants',
        
        // Language Selector
        'select_language': 'Sélectionner la Langue',
        'language_selection': 'Sélection de Langue',
        'choose_language': 'Choisissez votre langue préférée:',
        'continue_button': 'Continuer',
        
        // Dashboard
        'dashboard_title': 'Moniteur MT5 - Tableau de Bord',
        'connected_status': 'Connecté',
        'disconnected_status': 'Déconnecté',
        'current_balance': 'Solde Actuel',
        'equity': 'Équité',
        'daily_pl': 'P/L du Jour',
        'trades_today': 'Trades Aujourd\'hui',
        'open_trades': 'Trades Ouverts',
        'close_all': 'Fermer Tous',
        'close_positive': 'Fermer +',
        'close_negative': 'Fermer Négatifs',
        'no_open_trades': 'Aucun trade ouvert pour le moment',
        'frequency_label': 'Fréquence:',
        'last_update': 'Dernière mise à jour:',
        'waiting': 'En attente...',
        'synchronizing': 'Synchronisation...',
        
        // Goal Modal
        'goal_reached_title': '🎉 Félicitations! Objectif Atteint! 🎉',
        'goal_reached_message': 'Vous avez atteint votre objectif quotidien de',
        'goal_reached_advice': 'Excellent travail! Rappelez-vous que la discipline est la clé du succès à long terme. Considérez faire une pause et protéger vos profits.',
        'goal_recommendation': 'Recommandation: Arrêtez de trader aujourd\'hui et revenez demain avec la même discipline.',
        'goal_hashtags': '#StopLoss #StopGain #Discipline',
        
        // Loss Limit Modal
        'loss_limit_title': '🚨 Attention! Limite de Perte Atteinte! 🚨',
        'loss_limit_message': 'Vous avez atteint votre limite quotidienne de perte de',
        'loss_limit_warning': 'Arrêtez de trader immédiatement! La discipline est cruciale pour protéger votre capital et assurer votre survie sur le marché.',
        'loss_recommendation': 'Recommandation: Fermez la plateforme, révisez vos trades et revenez demain avec un esprit renouvelé.',
        'loss_hashtags': '#StopLoss #GestionDesRisques #Discipline',
        
        // Dashboard Sections
        'symbol_distribution': 'Distribution par Symbole',
        'profit_loss_chart': 'Profit/Perte (15 Derniers Trades)',
        'consolidated_result': 'Résultat Consolidé par Temps',
        'recent_trades_history': 'Historique des Trades Récents',
        'goals_and_limits': 'Objectifs et Limites',
        'profit_loss_label': 'Profit/Perte ($)',
        'consolidated_result_label': 'Résultat Consolidé',
        
        // Time intervals
        'minutes_5': '5 minutes',
        'minutes_15': '15 minutes',
        'minutes_30': '30 minutes',
        'hour_1': '1 heure',
        'hours_4': '4 heures',
        'day_1': '1 jour',
        
        // Trade table headers
        'ticket': 'Ticket',
        'symbol': 'Symbole',
        'type': 'Type',
        'volume': 'Volume',
        'open_price': 'Prix d\'Ouverture',
        'current_price': 'Prix Actuel',
        'profit': 'Profit',
        'time': 'Temps',
        'swap': 'Swap',
        'commission': 'Commission',
        'profit_goal': 'Objectif de Profit',
        'loss_limit': 'Limite de Perte',
        'daily_progress': 'Progrès Quotidien',
        'loss_limit_text': 'Limite de perte',
        'profit_goal_text': 'Objectif de profit',
        
        // Progress messages - Loss
        'risk_low': 'Risque faible',
        'attention': 'Attention',
        'risk_high': 'Risque élevé',
        'critical_danger': 'Danger critique',
        
        // Progress messages - Gain
        'progressing': 'En progression',
        'good_pace': 'Bon rythme',
        'almost_there': 'Presque là',
        'very_close': 'Très proche',
        'goal_achieved': 'Objectif atteint',
        
        // Confirmation popups
        'confirm_close_all': 'Êtes-vous sûr de vouloir fermer TOUS les ordres ouverts?',
        'confirm_close_positive': 'Êtes-vous sûr de vouloir fermer tous les ordres POSITIFS?',
        'confirm_close_negative': 'Êtes-vous sûr de vouloir fermer tous les ordres NÉGATIFS?',
        'confirm_close_individual': 'Êtes-vous sûr de vouloir fermer l\'ordre #',
        'confirm_logout': 'Êtes-vous sûr de vouloir vous déconnecter?',
        
        // Access Denied Page
        'access_denied_title': 'Accès Refusé - VolatForex Monitor Pro',
        'access_denied_header': 'Accès Refusé',
        'access_denied_hello': 'Bonjour',
        'access_denied_message': 'Nous avons identifié votre compte, mais il n\'a pas encore l\'autorisation d\'accéder à',
        'access_denied_message_no_user': 'Votre compte n\'a pas l\'autorisation d\'accéder à',
        'access_denied_to_get_access': 'pour obtenir un accès complet:',
        'access_denied_to_get_access_no_user': 'Pour obtenir un accès complet:',
        'access_denied_reason_1': '✅ Votre abonnement a expiré',
        'access_denied_reason_2': '⏳ Votre abonnement a été annulé pour non-paiement',
        'access_denied_reason_3': '🎯 Obtenez l\'accès en cliquant sur le bouton ci-dessous',
        'access_denied_acquire_button': '🚀 Obtenir l\'Accès',
        'access_denied_back_button': '🔄 Retour à la Connexion',
        'access_denied_footer': 'Après l\'achat, votre accès sera automatiquement activé. Des questions?',
        
        // Login Error Messages
        'error_email_not_found': 'Email introuvable dans le système. Vérifiez votre email ou obtenez l\'accès.',
        'error_email_required': 'L\'email est obligatoire',
        'error_login_failed': 'Erreur de connexion. Veuillez réessayer.',
        
        // Advanced Charts Modal
        'technical_analysis': 'Volat Scalper Pro',
        'loading_data': 'Collecte des données du marché...',
        'loading_subtitle': 'Veuillez patienter pendant que nous rassemblons suffisamment de ticks pour une analyse précise',
        'select_asset': 'Sélectionner l\'Actif:',
        'select_or_type': '-- Sélectionnez ou tapez ci-dessous --',
        'or_type_symbol': 'Ou tapez le symbole:',
        'load_button': 'Charger',
        'moving_averages': 'Moyennes Mobiles:',
        'hull_ma': 'Hull MA',
        'oscillators': 'Oscillateurs:',
        'zscore': 'Z-Score',
        'rsi': 'RSI',
        'visualization': 'Visualisation:',
        'show_points': 'Afficher les Points',
        'last_price': 'Dernier Prix',
        'hull_value': 'Hull MA',
        'zscore_value': 'Z-Score',
        'rsi_value': 'RSI',
        'last_update_charts': 'Dernière Mise à Jour',
        'metals': 'Métaux',
        'forex_major': 'Forex Majeurs',
        'forex_cross': 'Forex Croisés',
        'commodities': 'Matières Premières',
        'crypto': 'Cryptomonnaies',
        'indices': 'Indices'
    },
    
    'de': {
        // Login Page
        'login_title': 'Anmeldung - VolatForex Monitor Pro',
        'login_subtitle': 'Geben Sie Ihre E-Mail ein, um auf das System zuzugreifen',
        'email_label': 'E-Mail:',
        'remember_me': 'Anmeldung merken',
        'login_button': 'Anmelden',
        'or_text': 'oder',
        'acquire_access': 'Zugang Erhalten',
        'restricted_access': 'Beschränkter Zugang nur für Benutzer mit genehmigter Lizenz',
        'security_notice': 'Ihre MT5-Daten verlassen niemals Ihre Maschine. 100% lokale Verarbeitung, keine Cloud-Speicherung.',
        'need_help': 'Brauchen Sie Hilfe?',
        'loading_text': 'Authentifizierung...',
        'loading_subtext': 'Überprüfung Ihrer Anmeldedaten',
        
        // Language Selector
        'select_language': 'Sprache Auswählen',
        'language_selection': 'Sprachauswahl',
        'choose_language': 'Wählen Sie Ihre bevorzugte Sprache:',
        'continue_button': 'Weiter',
        
        // Dashboard
        'dashboard_title': 'MT5 Monitor - Dashboard',
        'connected_status': 'Verbunden',
        'disconnected_status': 'Getrennt',
        'current_balance': 'Aktueller Saldo',
        'equity': 'Eigenkapital',
        'daily_pl': 'Täglicher G/V',
        'trades_today': 'Trades Heute',
        'open_trades': 'Offene Trades',
        'close_all': 'Alle Schließen',
        'close_positive': 'Positive Schließen',
        'close_negative': 'Negative Schließen',
        'no_open_trades': 'Momentan keine offenen Trades',
        'frequency_label': 'Frequenz:',
        'last_update': 'Letzte Aktualisierung:',
        'waiting': 'Warten...',
        'synchronizing': 'Synchronisierung...',
        
        // Goal Modal
        'goal_reached_title': '🎉 Glückwunsch! Ziel Erreicht! 🎉',
        'goal_reached_message': 'Sie haben Ihr Tagesziel von',
        'goal_reached_advice': 'Ausgezeichnete Arbeit! Denken Sie daran, dass Disziplin der Schlüssel zum langfristigen Erfolg ist. Erwägen Sie eine Pause und schützen Sie Ihre Gewinne.',
        'goal_recommendation': 'Empfehlung: Hören Sie heute auf zu handeln und kommen Sie morgen mit derselben Disziplin zurück.',
        'goal_hashtags': '#StopLoss #StopGain #Disziplin',
        
        // Loss Limit Modal
        'loss_limit_title': '🚨 Achtung! Verlustgrenze Erreicht! 🚨',
        'loss_limit_message': 'Sie haben Ihre tägliche Verlustgrenze von',
        'loss_limit_warning': 'Hören Sie sofort auf zu handeln! Disziplin ist entscheidend, um Ihr Kapital zu schützen und Ihr Überleben am Markt zu sichern.',
        'loss_recommendation': 'Empfehlung: Schließen Sie die Plattform, überprüfen Sie Ihre Trades und kommen Sie morgen mit einem erneuerten Geist zurück.',
        'loss_hashtags': '#StopLoss #Risikomanagement #Disziplin',
        
        // Dashboard Sections
        'symbol_distribution': 'Verteilung nach Symbol',
        'profit_loss_chart': 'Gewinn/Verlust (Letzte 15 Trades)',
        'consolidated_result': 'Konsolidiertes Ergebnis nach Zeit',
        'recent_trades_history': 'Verlauf der Letzten Trades',
        'goals_and_limits': 'Ziele und Grenzen',
        'profit_loss_label': 'Gewinn/Verlust ($)',
        'consolidated_result_label': 'Konsolidiertes Ergebnis',
        
        // Time intervals
        'minutes_5': '5 Minuten',
        'minutes_15': '15 Minuten',
        'minutes_30': '30 Minuten',
        'hour_1': '1 Stunde',
        'hours_4': '4 Stunden',
        'day_1': '1 Tag',
        
        // Trade table headers
        'ticket': 'Ticket',
        'symbol': 'Symbol',
        'type': 'Typ',
        'volume': 'Volumen',
        'open_price': 'Eröffnungspreis',
        'current_price': 'Aktueller Preis',
        'profit': 'Gewinn',
        'time': 'Zeit',
        'swap': 'Swap',
        'commission': 'Provision',
        'profit_goal': 'Gewinnziel',
        'loss_limit': 'Verlustgrenze',
        'daily_progress': 'Täglicher Fortschritt',
        'loss_limit_text': 'Verlustgrenze',
        'profit_goal_text': 'Gewinnziel',
        
        // Progress messages - Loss
        'risk_low': 'Niedriges Risiko',
        'attention': 'Achtung',
        'risk_high': 'Hohes Risiko',
        'critical_danger': 'Kritische Gefahr',
        
        // Progress messages - Gain
        'progressing': 'In Bearbeitung',
        'good_pace': 'Gutes Tempo',
        'almost_there': 'Fast da',
        'very_close': 'Sehr nah',
        'goal_achieved': 'Ziel erreicht',
        
        // Confirmation popups
        'confirm_close_all': 'Sind Sie sicher, dass Sie ALLE offenen Orders schließen möchten?',
        'confirm_close_positive': 'Sind Sie sicher, dass Sie alle POSITIVEN Orders schließen möchten?',
        'confirm_close_negative': 'Sind Sie sicher, dass Sie alle NEGATIVEN Orders schließen möchten?',
        'confirm_close_individual': 'Sind Sie sicher, dass Sie Order #',
        'confirm_logout': 'Sind Sie sicher, dass Sie sich abmelden möchten?',
        
        // Access Denied Page
        'access_denied_title': 'Zugriff Verweigert - VolatForex Monitor Pro',
        'access_denied_header': 'Zugriff Verweigert',
        'access_denied_hello': 'Hallo',
        'access_denied_message': 'Wir haben Ihr Konto identifiziert, aber es hat noch keine Berechtigung für den Zugriff auf',
        'access_denied_message_no_user': 'Ihr Konto hat keine Berechtigung für den Zugriff auf',
        'access_denied_to_get_access': 'um vollen Zugriff zu erhalten:',
        'access_denied_to_get_access_no_user': 'Um vollen Zugriff zu erhalten:',
        'access_denied_reason_1': '✅ Ihr Abonnement ist abgelaufen',
        'access_denied_reason_2': '⏳ Ihr Abonnement wurde wegen Nichtzahlung storniert',
        'access_denied_reason_3': '🎯 Erhalten Sie Zugriff, indem Sie auf die Schaltfläche unten klicken',
        'access_denied_acquire_button': '🚀 Zugriff Erhalten',
        'access_denied_back_button': '🔄 Zurück zur Anmeldung',
        'access_denied_footer': 'Nach dem Kauf wird Ihr Zugriff automatisch aktiviert. Fragen?',
        
        // Login Error Messages
        'error_email_not_found': 'E-Mail im System nicht gefunden. Überprüfen Sie Ihre E-Mail oder erhalten Sie Zugriff.',
        'error_email_required': 'E-Mail ist erforderlich',
        'error_login_failed': 'Anmeldefehler. Bitte versuchen Sie es erneut.',
        
        // Advanced Charts Modal
        'technical_analysis': 'Volat Scalper Pro',
        'loading_data': 'Marktdaten werden gesammelt...',
        'loading_subtitle': 'Bitte warten Sie, während wir genügend Ticks für eine genaue Analyse sammeln',
        'select_asset': 'Asset Auswählen:',
        'select_or_type': '-- Wählen oder tippen Sie unten --',
        'or_type_symbol': 'Oder geben Sie das Symbol ein:',
        'load_button': 'Laden',
        'moving_averages': 'Gleitende Durchschnitte:',
        'hull_ma': 'Hull MA',
        'oscillators': 'Oszillatoren:',
        'zscore': 'Z-Score',
        'rsi': 'RSI',
        'visualization': 'Visualisierung:',
        'show_points': 'Punkte Anzeigen',
        'last_price': 'Letzter Preis',
        'hull_value': 'Hull MA',
        'zscore_value': 'Z-Score',
        'rsi_value': 'RSI',
        'last_update_charts': 'Letzte Aktualisierung',
        'metals': 'Metalle',
        'forex_major': 'Haupt-Forex',
        'forex_cross': 'Kreuz-Forex',
        'commodities': 'Rohstoffe',
        'crypto': 'Kryptowährungen',
        'indices': 'Indizes'
    }
};

// Configuração de idiomas disponíveis
const availableLanguages = {
    'pt': { name: 'Português', flag: '🇧🇷' },
    'en': { name: 'English', flag: '🇺🇸' },
    'es': { name: 'Español', flag: '🇪🇸' },
    'fr': { name: 'Français', flag: '🇫🇷' },
    'de': { name: 'Deutsch', flag: '🇩🇪' }
};

// Idioma padrão
let currentLanguage = 'pt';

// Função para obter o idioma salvo no localStorage
function getSavedLanguage() {
    return localStorage.getItem('volatforex_language') || 'pt';
}

// Função para salvar o idioma no localStorage
function saveLanguage(language) {
    localStorage.setItem('volatforex_language', language);
    currentLanguage = language;
}

// Função para obter uma tradução
function t(key) {
    return translations[currentLanguage][key] || translations['pt'][key] || key;
}

// Função para aplicar traduções em elementos com data-i18n
function applyTranslations() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key);
        
        if (element.tagName === 'INPUT' && (element.type === 'submit' || element.type === 'button')) {
            element.value = translation;
        } else if (element.tagName === 'INPUT' && element.placeholder !== undefined) {
            element.placeholder = translation;
        } else {
            element.textContent = translation;
        }
    });
    
    // Atualizar título da página
    const titleElement = document.querySelector('title');
    if (titleElement && titleElement.hasAttribute('data-i18n')) {
        titleElement.textContent = t(titleElement.getAttribute('data-i18n'));
    }
}

// Função para inicializar o sistema de idiomas
function initializeI18n() {
    currentLanguage = getSavedLanguage();
    applyTranslations();
}

// Função para mudar o idioma
function changeLanguage(language) {
    if (availableLanguages[language]) {
        saveLanguage(language);
        applyTranslations();
        
        // Disparar evento personalizado para notificar mudança de idioma
        const event = new CustomEvent('languageChanged', { detail: { language } });
        document.dispatchEvent(event);
    }
}

// Função para criar o popup de seleção de idioma
function createLanguageSelector() {
    const modal = document.createElement('div');
    modal.id = 'language-selector-modal';
    modal.className = 'language-modal';
    modal.innerHTML = `
        <div class="language-modal-content">
            <div class="language-modal-header">
                <h2 data-i18n="language_selection">${t('language_selection')}</h2>
            </div>
            <div class="language-modal-body">
                <p data-i18n="choose_language">${t('choose_language')}</p>
                <div class="language-options">
                    ${Object.entries(availableLanguages).map(([code, info]) => `
                        <button class="language-option" data-language="${code}">
                            <span class="language-flag">${info.flag}</span>
                            <span class="language-name">${info.name}</span>
                        </button>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    // Adicionar estilos CSS
    const style = document.createElement('style');
    style.textContent = `
        .language-modal {
            display: flex;
            position: fixed;
            z-index: 10000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease-in-out;
        }
        
        .language-modal-content {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            text-align: center;
            max-width: 500px;
            width: 90%;
            color: white;
            animation: slideIn 0.3s ease-in-out;
        }
        
        .language-modal-header h2 {
            color: #4fc3f7;
            margin-bottom: 20px;
            font-family: 'Orbitron', sans-serif;
        }
        
        .language-modal-body p {
            color: #ccc;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .language-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .language-option {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 15px 20px;
            border: 2px solid #444;
            border-radius: 12px;
            background: #2a2a2a;
            color: white;
            font-size: 1.1em;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .language-option:hover {
            border-color: #4fc3f7;
            background: #3a3a3a;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(79, 195, 247, 0.3);
        }
        
        .language-option.selected {
            border-color: #28a745;
            background: rgba(40, 167, 69, 0.2);
        }
        
        .language-flag {
            font-size: 1.5em;
        }
        
        .language-name {
            font-weight: 600;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideIn {
            from { transform: translateY(-50px) scale(0.9); opacity: 0; }
            to { transform: translateY(0) scale(1); opacity: 1; }
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(modal);
    
    // Adicionar event listeners
    const languageOptions = modal.querySelectorAll('.language-option');
    languageOptions.forEach(option => {
        const language = option.getAttribute('data-language');
        
        // Marcar idioma atual como selecionado
        if (language === currentLanguage) {
            option.classList.add('selected');
        }
        
        option.addEventListener('click', () => {
            // Remover seleção anterior
            languageOptions.forEach(opt => opt.classList.remove('selected'));
            // Adicionar seleção atual
            option.classList.add('selected');
            
            // Mudar idioma e fechar modal
            changeLanguage(language);
            setTimeout(() => {
                modal.remove();
            }, 300);
        });
    });
    
    return modal;
}

// Função para mostrar o seletor de idioma
function showLanguageSelector() {
    // Remover modal existente se houver
    const existingModal = document.getElementById('language-selector-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    createLanguageSelector();
}

// Inicializar quando o DOM estiver carregado
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeI18n);
} else {
    initializeI18n();
}

// Exportar funções para uso global
window.i18n = {
    t,
    changeLanguage,
    showLanguageSelector,
    getSavedLanguage,
    saveLanguage,
    availableLanguages,
    getCurrentLanguage: () => currentLanguage
};
