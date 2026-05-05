#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symbol Mapper - Sistema de Normalização de Símbolos Multi-Corretoras
Mapeia símbolos de diferentes corretoras para um formato padrão
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class SymbolMapper:
    """
    Classe para mapear e normalizar símbolos de diferentes corretoras
    """
    
    def __init__(self, config_path: str = 'symbol_mapping.json'):
        """
        Inicializa o mapeador de símbolos
        
        Args:
            config_path: Caminho para o arquivo de configuração JSON
        """
        self.config_path = config_path
        self.mappings: Dict = {}
        self.reverse_mappings: Dict = {}
        self.broker_mappings: Dict = {}
        self.load_config()
    
    def load_config(self) -> bool:
        """
        Carrega configuração de mapeamento do arquivo JSON
        
        Returns:
            True se carregou com sucesso, False caso contrário
        """
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.mappings = config.get('mappings', {})
                    self.broker_mappings = config.get('brokers', {})
                    self._build_reverse_mappings()
                    print(f"[SYMBOL MAPPER] [OK] Configuracao carregada: {len(self.mappings)} simbolos, {len(self.broker_mappings)} corretoras")
                    return True
            else:
                print(f"[SYMBOL MAPPER] [AVISO] Arquivo {self.config_path} nao encontrado")
                return False
        except Exception as e:
            print(f"[SYMBOL MAPPER] [ERRO] Erro ao carregar configuracao: {e}")
            return False
    
    def _build_reverse_mappings(self):
        """
        Constrói mapeamento reverso (alias -> standard) para busca rápida
        """
        self.reverse_mappings = {}
        
        for standard, data in self.mappings.items():
            # O proprio simbolo padrao
            self.reverse_mappings[standard.upper()] = standard
            
            # Todos os aliases
            for alias in data.get('aliases', []):
                self.reverse_mappings[alias.upper()] = standard
        
        print(f"[SYMBOL MAPPER] [INFO] Mapeamento reverso construido: {len(self.reverse_mappings)} entradas")
    
    def normalize(self, symbol: str) -> str:
        """
        Normaliza simbolo para formato padrao
        
        Args:
            symbol: Símbolo a ser normalizado (ex: "GOLD", "XAU/USD", "XAUUSD.a")
        
        Returns:
            Símbolo normalizado (ex: "XAUUSD")
        """
        if not symbol:
            return symbol
        
        symbol_upper = symbol.upper().strip()
        normalized = self.reverse_mappings.get(symbol_upper, symbol)
        
        if normalized != symbol:
            print(f"[SYMBOL MAPPER] 🔄 Normalizado: {symbol} → {normalized}")
        
        return normalized
    
    def get_broker_symbol(self, standard_symbol: str, broker_name: str) -> str:
        """
        Obtém símbolo específico da corretora a partir do símbolo padrão
        
        Args:
            standard_symbol: Símbolo padrão (ex: "XAUUSD")
            broker_name: Nome da corretora (ex: "XM", "IC Markets")
        
        Returns:
            Símbolo da corretora (ex: "GOLD" para XM)
        """
        broker_map = self.broker_mappings.get(broker_name, {})
        return broker_map.get(standard_symbol, standard_symbol)
    
    def get_standard_symbol(self, broker_symbol: str, broker_name: str) -> str:
        """
        Converte símbolo da corretora para padrão
        
        Args:
            broker_symbol: Símbolo da corretora (ex: "GOLD")
            broker_name: Nome da corretora (ex: "XM")
        
        Returns:
            Símbolo padrão (ex: "XAUUSD")
        """
        # Primeiro tenta mapeamento direto da corretora
        broker_map = self.broker_mappings.get(broker_name, {})
        for standard, broker_sym in broker_map.items():
            if broker_sym.upper() == broker_symbol.upper():
                return standard
        
        # Se não encontrar, tenta normalização geral
        return self.normalize(broker_symbol)
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """
        Retorna informações completas do símbolo
        
        Args:
            symbol: Símbolo (pode ser padrão ou alias)
        
        Returns:
            Dicionário com informações do símbolo
        """
        normalized = self.normalize(symbol)
        
        if normalized in self.mappings:
            info = self.mappings[normalized].copy()
            info['standard'] = normalized
            return info
        
        # Se não encontrar, retorna informação básica
        return {
            'standard': normalized,
            'description': normalized,
            'category': 'Outros',
            'aliases': [],
            'digits': 5
        }
    
    def list_symbols(self, category: Optional[str] = None) -> Dict:
        """
        Lista todos os símbolos (opcionalmente por categoria)
        
        Args:
            category: Categoria para filtrar (ex: "Forex", "Metais", "Crypto")
        
        Returns:
            Dicionário de símbolos
        """
        if category:
            return {
                k: v for k, v in self.mappings.items() 
                if v.get('category') == category
            }
        return self.mappings
    
    def list_categories(self) -> List[str]:
        """
        Lista todas as categorias disponíveis
        
        Returns:
            Lista de categorias únicas
        """
        categories = set()
        for data in self.mappings.values():
            categories.add(data.get('category', 'Outros'))
        return sorted(list(categories))
    
    def list_brokers(self) -> List[str]:
        """
        Lista todas as corretoras configuradas
        
        Returns:
            Lista de nomes de corretoras
        """
        return list(self.broker_mappings.keys())
    
    def search_symbols(self, query: str) -> List[Dict]:
        """
        Busca símbolos por nome, alias ou descrição
        
        Args:
            query: Termo de busca
        
        Returns:
            Lista de símbolos encontrados
        """
        query_lower = query.lower().strip()
        results = []
        
        for standard, info in self.mappings.items():
            # Busca no nome padrão
            if query_lower in standard.lower():
                results.append({
                    'standard': standard,
                    'description': info['description'],
                    'category': info['category'],
                    'aliases': info['aliases']
                })
                continue
            
            # Busca nos aliases
            if any(query_lower in alias.lower() for alias in info['aliases']):
                results.append({
                    'standard': standard,
                    'description': info['description'],
                    'category': info['category'],
                    'aliases': info['aliases']
                })
                continue
            
            # Busca na descrição
            if query_lower in info['description'].lower():
                results.append({
                    'standard': standard,
                    'description': info['description'],
                    'category': info['category'],
                    'aliases': info['aliases']
                })
        
        return results
    
    def add_symbol(self, standard: str, aliases: List[str], description: str, 
                   category: str = "Outros", digits: int = 5) -> bool:
        """
        Adiciona um novo símbolo ao mapeamento (runtime only, não salva no arquivo)
        
        Args:
            standard: Símbolo padrão
            aliases: Lista de aliases
            description: Descrição do símbolo
            category: Categoria
            digits: Número de casas decimais
        
        Returns:
            True se adicionou com sucesso
        """
        try:
            self.mappings[standard] = {
                'standard': standard,
                'aliases': aliases,
                'description': description,
                'category': category,
                'digits': digits
            }
            self._build_reverse_mappings()
            print(f"[SYMBOL MAPPER] ➕ Símbolo adicionado: {standard}")
            return True
        except Exception as e:
            print(f"[SYMBOL MAPPER] ❌ Erro ao adicionar símbolo: {e}")
            return False


# Testes unitários (executar apenas se for o script principal)
if __name__ == '__main__':
    print("="*60)
    print("🧪 TESTANDO SYMBOL MAPPER")
    print("="*60)
    
    # Inicializa o mapper
    mapper = SymbolMapper()
    
    # Teste 1: Normalização
    print("\n📋 Teste 1: Normalização de Símbolos")
    test_symbols = [
        "GOLD", "XAU/USD", "XAUUSD.a", "XAUUSD",
        "EUR/USD", "EURUSDm", "EURUSD",
        "WTI", "USOIL", "XTIUSD"
    ]
    
    for symbol in test_symbols:
        normalized = mapper.normalize(symbol)
        print(f"  {symbol:15} → {normalized}")
    
    # Teste 2: Informações do símbolo
    print("\n📊 Teste 2: Informações do Símbolo")
    info = mapper.get_symbol_info("GOLD")
    print(f"  Símbolo: {info['standard']}")
    print(f"  Descrição: {info['description']}")
    print(f"  Categoria: {info['category']}")
    print(f"  Aliases: {', '.join(info['aliases'])}")
    
    # Teste 3: Mapeamento por corretora
    print("\n🏢 Teste 3: Mapeamento por Corretora")
    brokers = ["XM", "IC Markets", "Exness"]
    for broker in brokers:
        symbol = mapper.get_broker_symbol("XAUUSD", broker)
        print(f"  {broker:15} → XAUUSD = {symbol}")
    
    # Teste 4: Busca
    print("\n🔍 Teste 4: Busca de Símbolos")
    results = mapper.search_symbols("ouro")
    for result in results:
        print(f"  {result['standard']:10} - {result['description']}")
    
    # Teste 5: Listar categorias
    print("\n📂 Teste 5: Categorias Disponíveis")
    categories = mapper.list_categories()
    for category in categories:
        symbols = mapper.list_symbols(category)
        print(f"  {category:15} - {len(symbols)} símbolos")
    
    print("\n" + "="*60)
    print("✅ Testes concluídos!")
    print("="*60)
