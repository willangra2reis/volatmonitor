//+------------------------------------------------------------------+
//|                                    VOlatForex WebhookMonitor.mq5 |
//|                        Copyright 2025, VOlatForex Software Corp. |
//|                                       https://www.volatforex.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, VOlatForex Software Corp."
#property link      "https://www.volatforex.com"
#property version   "1.10"
#property description "EA que envia dados de balanço, trades e PREÇOS TICK em tempo real para o Dashboard Volat Monitor & Scalper Pro"
#property description "EA that sends balance, trades and real-time TICK PRICES data to Volat Monitor & Scalper Pro Dashboard"
#property description "EA que envía datos de balance, trades y PRECIOS TICK en tiempo real al Dashboard Volat Monitor & Scalper Pro"
#property description "EA qui envoie les données de solde, trades et PRIX TICK en temps réel au Dashboard Volat Monitor & Scalper Pro"
#property description "EA, der Kontostand-, Trade- und TICK-PREIS-Daten in Echtzeit an das Volat Monitor & Scalper Pro Dashboard sendet"

#include <Trade\Trade.mqh>

//--- Enum para seletor de tempo de envio
enum ENUM_SEND_INTERVAL
{
    INTERVAL_TICK,      // Tick a Tick (tempo real)
    INTERVAL_2SEC,      // 2 segundos
    INTERVAL_5SEC,      // 5 segundos
    INTERVAL_10SEC,     // 10 segundos
    INTERVAL_15SEC,     // 15 segundos
    INTERVAL_30SEC      // 30 segundos
};

//--- Parâmetros de entrada (visíveis)
input string UserEmail = "seu_email@aqui.com"; // Email para verificação de licença
input string MonitoredSymbols = "XAUUSD,EURUSD,GBPUSD"; // Símbolos para monitorar preços (separados por vírgula)
input bool   SendTickData = true; // Enviar dados de preço tick-by-tick
input ENUM_SEND_INTERVAL SendInterval = INTERVAL_TICK; // Tempo de envio de dados

//--- Parâmetros ocultos (pré-configurados)
string WebhookURL = "http://127.0.0.1:5000/webhook";
string CommandURL = "http://127.0.0.1:5000/api/commands";
int    SendIntervalSeconds = 0;
int    CommandCheckIntervalSeconds = 0;
bool   UseGETMethod = false;
bool   DebugMode = true;

//--- Variáveis globais
datetime lastSendTime = 0;
datetime lastCommandCheckTime = 0;
CTrade trade;

//--- Variáveis para o display de status do usuário
string userStatus = "";
string userName = "";
string userFullName = "";
string statusMessage = "";
int displayLabelX = 360;  // Distância da borda direita (largura do painel + margem)
int displayLabelY = 30;

//+------------------------------------------------------------------+
//| Função para converter enum de intervalo para segundos            |
//+------------------------------------------------------------------+
int GetSendIntervalSeconds()
{
    switch(SendInterval)
    {
        case INTERVAL_TICK:  return 0;
        case INTERVAL_2SEC:  return 2;
        case INTERVAL_5SEC:  return 5;
        case INTERVAL_10SEC: return 10;
        case INTERVAL_15SEC: return 15;
        case INTERVAL_30SEC: return 30;
        default: return 0;
    }
}

//+------------------------------------------------------------------+
//| Função para verificar a licença do usuário                       |
//+------------------------------------------------------------------+
bool CheckLicense()
{
    // URL da API de verificação
    string apiUrl = "https://script.google.com/macros/s/AKfycbxxJTPltP3uidGKwsub_81BzH0vzJPy1sgUtinvAt5yA_4pChZlZoNVefCkrzdqeal6/exec?nome=" + UserEmail;
    
    char post[], result[];
    string headers;
    int res;
    
    Print("Verificando licença para o email: ", UserEmail);
    
    // Faz a requisição GET para a API
    res = WebRequest("GET", apiUrl, "", 5000, post, result, headers);
    
    if(res == 200)
    {
        string response = CharArrayToString(result);
        if(DebugMode) Print("Resposta da API de licença: ", response);
        
        // Extrai informações do usuário
        ExtractUserInfo(response);
        
        // Verifica se a resposta contém o status de aprovado
        if(StringFind(response, "\"status\":\"PURCHASE_APPROVED\"") >= 0)
        {
            Print("✓ Licença VÁLIDA. EA autorizado a rodar.");
            return(true);
        }
        else
        {
            Print("✗ Licença INVÁLIDA ou EXPIRADA. O EA não será iniciado.");
            Alert("Licença inválida ou expirada para o email: ", UserEmail, ". O EA não funcionará.");
            return(false);
        }
    }
    else
    {
        Print("✗ Erro ao conectar com o servidor de licença. Código: ", res);
        if(CharArrayToString(result) != "") Print("Resposta: ", CharArrayToString(result));
        Alert("Não foi possível verificar a licença. Verifique sua conexão com a internet ou contate o suporte. Código: ", res);
        return(false);
    }
}

//+------------------------------------------------------------------+
//| Função para extrair informações do usuário da resposta JSON     |
//+------------------------------------------------------------------+
void ExtractUserInfo(string response)
{
    // Extrai o status
    int statusPos = StringFind(response, "\"status\":\"");
    if(statusPos >= 0)
    {
        statusPos += 10;
        int statusEnd = StringFind(response, "\"", statusPos);
        if(statusEnd > statusPos)
        {
            userStatus = StringSubstr(response, statusPos, statusEnd - statusPos);
        }
    }
    
    // Extrai o nome completo (prioridade)
    int fullNamePos = StringFind(response, "\"nomecompleto\":\"");
    if(fullNamePos >= 0)
    {
        fullNamePos += 16;
        int fullNameEnd = StringFind(response, "\"", fullNamePos);
        if(fullNameEnd > fullNamePos)
        {
            userFullName = StringSubstr(response, fullNamePos, fullNameEnd - fullNamePos);
            userName = userFullName; // Usa o nome completo como padrão
        }
    }
    
    // Se não encontrou nome completo, tenta extrair o primeiro nome
    if(userName == "")
    {
        int namePos = StringFind(response, "\"pnome\":\"");
        if(namePos >= 0)
        {
            namePos += 9;
            int nameEnd = StringFind(response, "\"", namePos);
            if(nameEnd > namePos)
            {
                userName = StringSubstr(response, namePos, nameEnd - namePos);
            }
        }
    }
    
    // Define a mensagem de status baseada no status do usuário
    UpdateStatusMessage();
}

//+------------------------------------------------------------------+
//| Função para atualizar a mensagem de status                      |
//+------------------------------------------------------------------+
void UpdateStatusMessage()
{
    // Detecta o idioma do terminal
    string terminalLanguage = TerminalInfoString(TERMINAL_LANGUAGE);
    
    if(userStatus == "PURCHASE_APPROVED")
    {
        if(terminalLanguage == "Portuguese")
            statusMessage = "Seu acesso está aprovado";
        else if(terminalLanguage == "Spanish")
            statusMessage = "Su acceso está aprobado";
        else if(terminalLanguage == "French")
            statusMessage = "Votre accès est approuvé";
        else if(terminalLanguage == "German")
            statusMessage = "Ihr Zugang ist genehmigt";
        else
            statusMessage = "Your access is approved";
    }
    else if(userStatus == "SUBSCRIPTION_CANCELLATION" || userStatus == "PURCHASE_PROTEST")
    {
        if(terminalLanguage == "Portuguese")
            statusMessage = "Você cancelou sua inscrição";
        else if(terminalLanguage == "Spanish")
            statusMessage = "Has cancelado tu suscripción";
        else if(terminalLanguage == "French")
            statusMessage = "Vous avez annulé votre abonnement";
        else if(terminalLanguage == "German")
            statusMessage = "Sie haben Ihr Abonnement gekündigt";
        else
            statusMessage = "You have cancelled your subscription";
    }
    else if(userStatus == "PURCHASE_BILLET_PRINTED")
    {
        if(terminalLanguage == "Portuguese")
            statusMessage = "Seu pagamento está em atraso";
        else if(terminalLanguage == "Spanish")
            statusMessage = "Su pago está atrasado";
        else if(terminalLanguage == "French")
            statusMessage = "Votre paiement est en retard";
        else if(terminalLanguage == "German")
            statusMessage = "Ihre Zahlung ist überfällig";
        else
            statusMessage = "Your payment is overdue";
    }
    else
    {
        if(terminalLanguage == "Portuguese")
            statusMessage = "Status: " + userStatus;
        else if(terminalLanguage == "Spanish")
            statusMessage = "Estado: " + userStatus;
        else if(terminalLanguage == "French")
            statusMessage = "Statut: " + userStatus;
        else if(terminalLanguage == "German")
            statusMessage = "Status: " + userStatus;
        else
            statusMessage = "Status: " + userStatus;
    }
}

//+------------------------------------------------------------------+
//| Função para criar o display de status na tela                   |
//+------------------------------------------------------------------+
void CreateStatusDisplay()
{
    // Remove labels anteriores se existirem
    ObjectDelete(0, "UserStatusLabel");
    ObjectDelete(0, "UserNameLabel");
    ObjectDelete(0, "UserEmailLabel");
    ObjectDelete(0, "StatusMessageLabel");
    ObjectDelete(0, "StatusBackground");
    
    // Cria um retângulo de fundo (lado direito)
    ObjectCreate(0, "StatusBackground", OBJ_RECTANGLE_LABEL, 0, 0, 0);
    ObjectSetInteger(0, "StatusBackground", OBJPROP_XDISTANCE, displayLabelX - 10);
    ObjectSetInteger(0, "StatusBackground", OBJPROP_YDISTANCE, displayLabelY);
    ObjectSetInteger(0, "StatusBackground", OBJPROP_XSIZE, 370);
    ObjectSetInteger(0, "StatusBackground", OBJPROP_YSIZE, 70);
    ObjectSetInteger(0, "StatusBackground", OBJPROP_BGCOLOR, clrBlack);
    ObjectSetInteger(0, "StatusBackground", OBJPROP_BORDER_TYPE, BORDER_FLAT);
    ObjectSetInteger(0, "StatusBackground", OBJPROP_CORNER, CORNER_RIGHT_UPPER);
    ObjectSetInteger(0, "StatusBackground", OBJPROP_COLOR, clrWhite);
    ObjectSetInteger(0, "StatusBackground", OBJPROP_STYLE, STYLE_SOLID);
    ObjectSetInteger(0, "StatusBackground", OBJPROP_WIDTH, 1);
    ObjectSetInteger(0, "StatusBackground", OBJPROP_BACK, true);
    
    // Label do título
    ObjectCreate(0, "UserStatusLabel", OBJ_LABEL, 0, 0, 0);
    ObjectSetInteger(0, "UserStatusLabel", OBJPROP_XDISTANCE, displayLabelX - 5);
    ObjectSetInteger(0, "UserStatusLabel", OBJPROP_YDISTANCE, displayLabelY + 8);
    ObjectSetInteger(0, "UserStatusLabel", OBJPROP_COLOR, clrYellow);
    ObjectSetInteger(0, "UserStatusLabel", OBJPROP_FONTSIZE, 9);
    ObjectSetString(0, "UserStatusLabel", OBJPROP_FONT, "Arial Bold");
    ObjectSetString(0, "UserStatusLabel", OBJPROP_TEXT, "Volat Monitor & Scalper Pro");
    ObjectSetInteger(0, "UserStatusLabel", OBJPROP_CORNER, CORNER_RIGHT_UPPER);
    
    // Label do email do usuário
    ObjectCreate(0, "UserEmailLabel", OBJ_LABEL, 0, 0, 0);
    ObjectSetInteger(0, "UserEmailLabel", OBJPROP_XDISTANCE, displayLabelX - 5);
    ObjectSetInteger(0, "UserEmailLabel", OBJPROP_YDISTANCE, displayLabelY + 28);
    ObjectSetInteger(0, "UserEmailLabel", OBJPROP_COLOR, clrLightGray);
    ObjectSetInteger(0, "UserEmailLabel", OBJPROP_FONTSIZE, 8);
    ObjectSetString(0, "UserEmailLabel", OBJPROP_FONT, "Arial");
    ObjectSetString(0, "UserEmailLabel", OBJPROP_TEXT, UserEmail);
    ObjectSetInteger(0, "UserEmailLabel", OBJPROP_CORNER, CORNER_RIGHT_UPPER);
    
    // Label da mensagem de status
    color statusColor = clrLime;
    if(userStatus == "SUBSCRIPTION_CANCELLATION" || userStatus == "PURCHASE_PROTEST")
        statusColor = clrRed;
    else if(userStatus == "PURCHASE_BILLET_PRINTED")
        statusColor = clrOrange;
    
    ObjectCreate(0, "StatusMessageLabel", OBJ_LABEL, 0, 0, 0);
    ObjectSetInteger(0, "StatusMessageLabel", OBJPROP_XDISTANCE, displayLabelX - 5);
    ObjectSetInteger(0, "StatusMessageLabel", OBJPROP_YDISTANCE, displayLabelY + 46);
    ObjectSetInteger(0, "StatusMessageLabel", OBJPROP_COLOR, statusColor);
    ObjectSetInteger(0, "StatusMessageLabel", OBJPROP_FONTSIZE, 8);
    ObjectSetString(0, "StatusMessageLabel", OBJPROP_FONT, "Arial Bold");
    ObjectSetString(0, "StatusMessageLabel", OBJPROP_TEXT, statusMessage);
    ObjectSetInteger(0, "StatusMessageLabel", OBJPROP_CORNER, CORNER_RIGHT_UPPER);
    
    ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    // Verifica a licença antes de iniciar
    if(!CheckLicense())
    {
        return(INIT_FAILED);
    }

    // Converte o enum para segundos
    SendIntervalSeconds = GetSendIntervalSeconds();

    Print("EA WebhookMonitor iniciado com sucesso");
    Print("URL do Webhook: ", WebhookURL);
    Print("URL de Comandos: ", CommandURL);
    
    if(SendIntervalSeconds == 0)
        Print("Intervalo de envio: Tick a Tick (tempo real)");
    else
        Print("Intervalo de envio: ", SendIntervalSeconds, " segundos");
    
    Print("Intervalo de verificação de comandos: ", CommandCheckIntervalSeconds, " segundos");
    
    if(SendTickData)
    {
        Print("✓ Envio de dados de preço ATIVADO");
        Print("Símbolos monitorados: ", MonitoredSymbols);
    }
    
    // Cria o display de status do usuário na tela
    CreateStatusDisplay();
    
    lastSendTime = TimeCurrent();
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // Remove os objetos da tela
    ObjectDelete(0, "UserStatusLabel");
    ObjectDelete(0, "UserNameLabel");
    ObjectDelete(0, "UserEmailLabel");
    ObjectDelete(0, "StatusMessageLabel");
    ObjectDelete(0, "StatusBackground");
    
    Print("EA WebhookMonitor finalizado");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    datetime currentTime = TimeCurrent();
    
    // Verifica se já passou o tempo necessário para enviar os dados
    // Se SendIntervalSeconds for 0, envia a cada tick
    if(SendIntervalSeconds == 0 || (currentTime - lastSendTime >= SendIntervalSeconds))
    {
        SendDataToWebhook();
        lastSendTime = currentTime;
    }
    
    // Verifica comandos pendentes
    if(CommandCheckIntervalSeconds == 0 || (currentTime - lastCommandCheckTime >= CommandCheckIntervalSeconds))
    {
        CheckForCommands();
        lastCommandCheckTime = currentTime;
    }
}

//+------------------------------------------------------------------+
//| Função para enviar dados para o webhook                          |
//+------------------------------------------------------------------+
void SendDataToWebhook()
{
    string jsonData = PrepareJsonData();
    
    if(jsonData != "")
    {
        char post[], result[];
        string headers;
        int res;
        
        if(UseGETMethod)
        {
            // Método GET com dados na URL (limitado)
            string getUrl = WebhookURL + "?data=" + jsonData;
            res = WebRequest("GET", getUrl, "", 5000, post, result, headers);
        }
        else
        {
            // Método POST com dados no corpo
            StringToCharArray(jsonData, post, 0, WHOLE_ARRAY, CP_UTF8);
            ArrayResize(post, ArraySize(post) - 1);
            
            headers = "Content-Type: application/json\r\n";
            res = WebRequest("POST", WebhookURL, headers, 5000, post, result, headers);
        }
        
        if(DebugMode)
        {
            Print("Tentando enviar dados via ", UseGETMethod ? "GET" : "POST");
            Print("Tamanho dos dados: ", StringLen(jsonData), " caracteres");
        }
        
        if(res == 200)
        {
            Print("✓ Dados enviados com sucesso para o webhook");
            if(DebugMode)
            {
                Print("Resposta: ", CharArrayToString(result));
            }
        }
        else
        {
            Print("✗ Erro ao enviar dados para o webhook. Código: ", res);
            Print("Resposta: ", CharArrayToString(result));
        }
    }
    else
    {
        Print("Erro ao preparar dados JSON");
    }
}

//+------------------------------------------------------------------+
//| NOVA FUNÇÃO: Obter dados de preço (tick) dos símbolos           |
//+------------------------------------------------------------------+
string GetTickDataJson()
{
    if(!SendTickData) return "";
    
    string tickJson = "";
    string symbols[];
    int symbolCount = StringSplit(MonitoredSymbols, ',', symbols);
    
    for(int i = 0; i < symbolCount; i++)
    {
        // Remove espaços em branco
        StringTrimLeft(symbols[i]);
        StringTrimRight(symbols[i]);
        
        string symbol = symbols[i];
        
        // Verifica se o símbolo existe
        if(SymbolSelect(symbol, true))
        {
            if(tickJson != "") tickJson += ",";
            
            double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
            double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
            double last = SymbolInfoDouble(symbol, SYMBOL_LAST);
            double price = (bid + ask) / 2; // Preço médio
            
            tickJson += "\"" + symbol + "\": {";
            tickJson += "\"bid\": " + DoubleToString(bid, _Digits) + ",";
            tickJson += "\"ask\": " + DoubleToString(ask, _Digits) + ",";
            tickJson += "\"last\": " + DoubleToString(last, _Digits) + ",";
            tickJson += "\"price\": " + DoubleToString(price, _Digits) + ",";
            tickJson += "\"time\": \"" + TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + "\"";
            tickJson += "}";
        }
        else
        {
            if(DebugMode) Print("⚠️ Símbolo não encontrado: ", symbol);
        }
    }
    
    return tickJson;
}

//+------------------------------------------------------------------+
//| Função para preparar os dados em formato JSON                    |
//+------------------------------------------------------------------+
string PrepareJsonData()
{
    string json = "{";
    
    // Dados da conta
    json += "\"account_info\": {";
    json += "\"account_number\": " + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN)) + ",";
    json += "\"account_name\": \"" + AccountInfoString(ACCOUNT_NAME) + "\",";
    json += "\"account_server\": \"" + AccountInfoString(ACCOUNT_SERVER) + "\",";
    json += "\"account_currency\": \"" + AccountInfoString(ACCOUNT_CURRENCY) + "\",";
    json += "\"account_balance\": " + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) + ",";
    json += "\"account_equity\": " + DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2) + ",";
    json += "\"account_margin\": " + DoubleToString(AccountInfoDouble(ACCOUNT_MARGIN), 2) + ",";
    json += "\"account_free_margin\": " + DoubleToString(AccountInfoDouble(ACCOUNT_MARGIN_FREE), 2) + ",";
    json += "\"account_profit\": " + DoubleToString(AccountInfoDouble(ACCOUNT_PROFIT), 2);
    json += "},";
    
    // Timestamp
    json += "\"timestamp\": \"" + TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + "\",";
    
    // Últimos 200 trades
    json += "\"last_trades\": [";
    string tradesJson = GetLastTradesJson(200);
    json += tradesJson;
    json += "],";
    
    // Trades abertos (posições atuais)
    json += "\"open_trades\": [";
    string openTradesJson = GetOpenTradesJson();
    json += openTradesJson;
    json += "]";
    
    // NOVO: Adicionar dados de preço (tick)
    if(SendTickData)
    {
        string tickData = GetTickDataJson();
        if(tickData != "")
        {
            json += ",\"tick_data\": {" + tickData + "}";
        }
    }
    
    json += "}";
    
    return json;
}

//+------------------------------------------------------------------+
//| Função para obter os últimos trades fechados em formato JSON    |
//+------------------------------------------------------------------+
string GetLastTradesJson(int maxTrades)
{
    string tradesJson = "";
    int validTrades = 0;
    
    // Seleciona o histórico de negociações
    if(HistorySelect(0, TimeCurrent()))
    {
        int totalDeals = HistoryDealsTotal();
        
        // Percorre do mais recente para o mais antigo
        for(int i = totalDeals - 1; i >= 0 && validTrades < maxTrades; i--)
        {
            ulong ticket = HistoryDealGetTicket(i);
            
            if(ticket > 0)
            {
                ENUM_DEAL_TYPE dealType = (ENUM_DEAL_TYPE)HistoryDealGetInteger(ticket, DEAL_TYPE);
                double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT);
                string symbol = HistoryDealGetString(ticket, DEAL_SYMBOL);
                
                // Filtra apenas trades de BUY/SELL que foram fechados (com lucro/prejuízo diferente de zero)
                if((dealType == DEAL_TYPE_BUY || dealType == DEAL_TYPE_SELL) && 
                   profit != 0.0 &&
                   symbol != "" && StringLen(symbol) > 0)
                {
                    if(tradesJson != "")
                        tradesJson += ",";
                    
                    tradesJson += "{";
                    tradesJson += "\"ticket\": " + IntegerToString(ticket) + ",";
                    tradesJson += "\"symbol\": \"" + symbol + "\",";
                    tradesJson += "\"type\": \"" + DealTypeToString(dealType) + "\",";
                    tradesJson += "\"volume\": " + DoubleToString(HistoryDealGetDouble(ticket, DEAL_VOLUME), 2) + ",";
                    tradesJson += "\"price\": " + DoubleToString(HistoryDealGetDouble(ticket, DEAL_PRICE), 5) + ",";
                    tradesJson += "\"profit\": " + DoubleToString(profit, 2) + ",";
                    tradesJson += "\"swap\": " + DoubleToString(HistoryDealGetDouble(ticket, DEAL_SWAP), 2) + ",";
                    tradesJson += "\"commission\": " + DoubleToString(HistoryDealGetDouble(ticket, DEAL_COMMISSION), 2) + ",";
                    tradesJson += "\"time\": \"" + TimeToString((datetime)HistoryDealGetInteger(ticket, DEAL_TIME), TIME_DATE|TIME_SECONDS) + "\",";
                    tradesJson += "\"comment\": \"" + HistoryDealGetString(ticket, DEAL_COMMENT) + "\"";
                    tradesJson += "}";
                    
                    validTrades++;
                }
            }
        }
    }
    
    return tradesJson;
}

//+------------------------------------------------------------------+
//| Função para obter trades abertos (posições atuais) em JSON     |
//+------------------------------------------------------------------+
string GetOpenTradesJson()
{
    string openTradesJson = "";
    int totalPositions = PositionsTotal();
    
    for(int i = 0; i < totalPositions; i++)
    {
        ulong ticket = PositionGetTicket(i);
        
        if(ticket > 0)
        {
            if(openTradesJson != "")
                openTradesJson += ",";
            
            string symbol = PositionGetString(POSITION_SYMBOL);
            ENUM_POSITION_TYPE posType = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
            double volume = PositionGetDouble(POSITION_VOLUME);
            double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
            double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
            double profit = PositionGetDouble(POSITION_PROFIT);
            double swap = PositionGetDouble(POSITION_SWAP);
            datetime openTime = (datetime)PositionGetInteger(POSITION_TIME);
            string comment = PositionGetString(POSITION_COMMENT);
            
            openTradesJson += "{";
            openTradesJson += "\"ticket\": " + IntegerToString(ticket) + ",";
            openTradesJson += "\"symbol\": \"" + symbol + "\",";
            openTradesJson += "\"type\": \"" + PositionTypeToString(posType) + "\",";
            openTradesJson += "\"volume\": " + DoubleToString(volume, 2) + ",";
            openTradesJson += "\"price\": " + DoubleToString(openPrice, 5) + ",";
            openTradesJson += "\"current_price\": " + DoubleToString(currentPrice, 5) + ",";
            openTradesJson += "\"profit\": " + DoubleToString(profit + swap, 2) + ",";
            openTradesJson += "\"profit_raw\": " + DoubleToString(profit, 2) + ",";
            openTradesJson += "\"swap\": " + DoubleToString(swap, 2) + ",";
            openTradesJson += "\"open_time\": \"" + TimeToString(openTime, TIME_DATE|TIME_SECONDS) + "\",";
            openTradesJson += "\"comment\": \"" + comment + "\"";
            openTradesJson += "}";
        }
    }
    
    return openTradesJson;
}

//+------------------------------------------------------------------+
//| Função auxiliar para converter tipo de posição para string     |
//+------------------------------------------------------------------+
string PositionTypeToString(ENUM_POSITION_TYPE posType)
{
    switch(posType)
    {
        case POSITION_TYPE_BUY: return "BUY";
        case POSITION_TYPE_SELL: return "SELL";
        default: return "UNKNOWN";
    }
}

//+------------------------------------------------------------------+
//| Função auxiliar para converter enum para string                  |
//+------------------------------------------------------------------+
string DealTypeToString(ENUM_DEAL_TYPE dealType)
{
    switch(dealType)
    {
        case DEAL_TYPE_BUY: return "BUY";
        case DEAL_TYPE_SELL: return "SELL";
        case DEAL_TYPE_BALANCE: return "BALANCE";
        case DEAL_TYPE_CREDIT: return "CREDIT";
        case DEAL_TYPE_CHARGE: return "CHARGE";
        case DEAL_TYPE_CORRECTION: return "CORRECTION";
        case DEAL_TYPE_BONUS: return "BONUS";
        case DEAL_TYPE_COMMISSION: return "COMMISSION";
        case DEAL_TYPE_COMMISSION_DAILY: return "COMMISSION_DAILY";
        case DEAL_TYPE_COMMISSION_MONTHLY: return "COMMISSION_MONTHLY";
        case DEAL_TYPE_COMMISSION_AGENT_DAILY: return "COMMISSION_AGENT_DAILY";
        case DEAL_TYPE_COMMISSION_AGENT_MONTHLY: return "COMMISSION_AGENT_MONTHLY";
        case DEAL_TYPE_INTEREST: return "INTEREST";
        case DEAL_TYPE_BUY_CANCELED: return "BUY_CANCELED";
        case DEAL_TYPE_SELL_CANCELED: return "SELL_CANCELED";
        default: return "UNKNOWN";
    }
}

//+------------------------------------------------------------------+
//| Função para verificar comandos pendentes                        |
//+------------------------------------------------------------------+
void CheckForCommands()
{
    char post[], result[];
    string headers;
    int res;
    
    // Faz requisição GET para verificar comandos pendentes
    res = WebRequest("GET", CommandURL, "", 5000, post, result, headers);
    
    if(res == 200)
    {
        string response = CharArrayToString(result);
        
        if(DebugMode)
        {
            Print("✓ Verificação de comandos realizada");
        }
        
        // Processa a resposta JSON
        ProcessCommands(response);
    }
    else if(res != 404) // 404 é normal quando não há comandos
    {
        if(DebugMode)
        {
            Print("✗ Erro ao verificar comandos. Código: ", res);
        }
    }
}

//+------------------------------------------------------------------+
//| Função para processar comandos recebidos                        |
//+------------------------------------------------------------------+
void ProcessCommands(string jsonResponse)
{
    // Parse simples do JSON para extrair comandos
    if(StringFind(jsonResponse, "\"command\":") >= 0)
    {
        // Comando para fechar ordem individual
        if(StringFind(jsonResponse, "\"close_order\"") >= 0)
        {
            string ticket = ExtractTicketFromJson(jsonResponse);
            if(ticket != "")
            {
                CloseOrderByTicket(ticket);
            }
        }
        // Comando para fechar todas as ordens
        else if(StringFind(jsonResponse, "\"close_all\"") >= 0)
        {
            CloseAllOrders();
        }
        // Comando para fechar ordens positivas
        else if(StringFind(jsonResponse, "\"close_positive\"") >= 0)
        {
            ClosePositiveOrders();
        }
        // Comando para fechar ordens negativas
        else if(StringFind(jsonResponse, "\"close_negative\"") >= 0)
        {
            CloseNegativeOrders();
        }
    }
}

//+------------------------------------------------------------------+
//| Função para extrair ticket do JSON                              |
//+------------------------------------------------------------------+
string ExtractTicketFromJson(string json)
{
    int startPos = StringFind(json, "\"ticket\":");
    if(startPos >= 0)
    {
        startPos += 10; // Pula '"ticket":'
        int endPos = StringFind(json, ",", startPos);
        if(endPos < 0) endPos = StringFind(json, "}", startPos);
        
        if(endPos > startPos)
        {
            string ticket = StringSubstr(json, startPos, endPos - startPos);
            StringReplace(ticket, "\"", ""); // Remove aspas
            StringReplace(ticket, " ", ""); // Remove espaços
            return ticket;
        }
    }
    return "";
}

//+------------------------------------------------------------------+
//| Função para fechar ordem por ticket                             |
//+------------------------------------------------------------------+
void CloseOrderByTicket(string ticketStr)
{
    ulong ticket = StringToInteger(ticketStr);
    
    if(PositionSelectByTicket(ticket))
    {
        if(trade.PositionClose(ticket))
        {
            Print("✓ Ordem #", ticket, " fechada com sucesso");
        }
        else
        {
            Print("✗ Erro ao fechar ordem #", ticket, ": ", trade.ResultRetcodeDescription());
        }
    }
    else
    {
        Print("✗ Ordem #", ticket, " não encontrada");
    }
}

//+------------------------------------------------------------------+
//| Função para fechar todas as ordens                              |
//+------------------------------------------------------------------+
void CloseAllOrders()
{
    int totalPositions = PositionsTotal();
    int closedCount = 0;
    
    Print("Iniciando fechamento de todas as ordens (", totalPositions, " ordens)");
    
    for(int i = totalPositions - 1; i >= 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if(ticket > 0)
        {
            if(trade.PositionClose(ticket))
            {
                closedCount++;
                Print("✓ Ordem #", ticket, " fechada");
            }
            else
            {
                Print("✗ Erro ao fechar ordem #", ticket, ": ", trade.ResultRetcodeDescription());
            }
        }
    }
    
    Print("Fechamento concluído: ", closedCount, "/", totalPositions, " ordens fechadas");
}

//+------------------------------------------------------------------+
//| Função para fechar apenas ordens positivas                      |
//+------------------------------------------------------------------+
void ClosePositiveOrders()
{
    int totalPositions = PositionsTotal();
    int closedCount = 0;
    
    Print("Iniciando fechamento de ordens positivas");
    
    for(int i = totalPositions - 1; i >= 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if(ticket > 0)
        {
            double profit = PositionGetDouble(POSITION_PROFIT);
            double swap = PositionGetDouble(POSITION_SWAP);
            double totalProfit = profit + swap;
            
            if(totalProfit > 0)
            {
                if(trade.PositionClose(ticket))
                {
                    closedCount++;
                    Print("✓ Ordem positiva #", ticket, " fechada (Lucro: $", DoubleToString(totalProfit, 2), ")");
                }
                else
                {
                    Print("✗ Erro ao fechar ordem #", ticket, ": ", trade.ResultRetcodeDescription());
                }
            }
        }
    }
    
    Print("Fechamento de ordens positivas concluído: ", closedCount, " ordens fechadas");
}

//+------------------------------------------------------------------+
//| Função para fechar apenas ordens negativas                      |
//+------------------------------------------------------------------+
void CloseNegativeOrders()
{
    int totalPositions = PositionsTotal();
    int closedCount = 0;
    
    Print("Iniciando fechamento de ordens negativas");
    
    for(int i = totalPositions - 1; i >= 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if(ticket > 0)
        {
            double profit = PositionGetDouble(POSITION_PROFIT);
            double swap = PositionGetDouble(POSITION_SWAP);
            double totalProfit = profit + swap;
            
            if(totalProfit < 0)
            {
                if(trade.PositionClose(ticket))
                {
                    closedCount++;
                    Print("✓ Ordem negativa #", ticket, " fechada (Prejuízo: $", DoubleToString(totalProfit, 2), ")");
                }
                else
                {
                    Print("✗ Erro ao fechar ordem #", ticket, ": ", trade.ResultRetcodeDescription());
                }
            }
        }
    }
    
    Print("Fechamento de ordens negativas concluído: ", closedCount, " ordens fechadas");
}
