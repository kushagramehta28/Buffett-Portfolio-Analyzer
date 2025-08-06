from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging

class DataIntegrationSystem:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cached_data = {}
        self.cache_timestamp = {}
        self.cache_duration = 3600  # 1 hour cache
        
    async def integrate_stock_data(self, 
                                 symbol: str,
                                 alpha_vantage_source,
                                 analyst_source) -> Dict[str, Any]:
        """
        Integrate data from multiple sources for a given stock symbol
        """
        try:
            # Check cache first
            if self._is_cache_valid(symbol):
                self.logger.info(f"Using cached data for {symbol}")
                return self.cached_data[symbol]

            # Gather data from all sources concurrently
            financial_data = await self._get_financial_data(symbol, alpha_vantage_source)
            analyst_data = await self._get_analyst_data(symbol, analyst_source)
            
            # Integrate the data
            integrated_data = self._merge_data(symbol, financial_data, analyst_data)
            
            # Calculate Buffet criteria scores
            scores = self._calculate_buffet_scores(integrated_data)
            integrated_data['buffet_analysis'] = scores
            
            # Cache the results
            self._cache_data(symbol, integrated_data)
            
            return integrated_data
            
        except Exception as e:
            self.logger.error(f"Error integrating data for {symbol}: {str(e)}")
            return {"error": str(e)}

    async def _get_financial_data(self, 
                                symbol: str, 
                                alpha_vantage_source) -> Dict[str, Any]:
        """
        Get financial data from Alpha Vantage
        """
        try:
            # Execute queries concurrently
            tasks = [
                self._execute_query(alpha_vantage_source, {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol
                }),
                self._execute_query(alpha_vantage_source, {
                    'function': 'OVERVIEW',
                    'symbol': symbol
                })
            ]
            
            results = await asyncio.gather(*tasks)
            
            return {
                'market_data': results[0],
                'company_overview': results[1]
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching financial data: {str(e)}")
            return {}

    async def _get_analyst_data(self, 
                              symbol: str, 
                              analyst_source) -> Dict[str, Any]:
        """
        Get analyst data from CSV source
        """
        try:
            return await self._execute_query(analyst_source, {'symbol': symbol})
        except Exception as e:
            self.logger.error(f"Error fetching analyst data: {str(e)}")
            return {}

    async def _execute_query(self, 
                           source, 
                           query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute query asynchronously
        """
        with ThreadPoolExecutor() as executor:
            return await asyncio.get_event_loop().run_in_executor(
                executor,
                source.execute_query,
                query
            )

    def _merge_data(self, 
                    symbol: str,
                    financial_data: Dict[str, Any],
                    analyst_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge data from different sources
        """
        try:
            # Extract market data
            market_data = financial_data.get('market_data', {}).get('Global Quote', {})
            overview_data = financial_data.get('company_overview', {})
            
            merged_data = {
                'symbol': symbol,
                'last_updated': datetime.now().isoformat(),
                
                # Market Data
                'market_data': {
                    'price': float(market_data.get('05. price', 0)),
                    'volume': int(market_data.get('06. volume', 0)),
                    'high': float(market_data.get('03. high', 0)),
                    'low': float(market_data.get('04. low', 0)),
                    'change_percent': market_data.get('10. change percent', '0%')
                },
                
                # Fundamental Data
                'fundamental_data': {
                    'pe_ratio': float(overview_data.get('PERatio', 0)),
                    'roe': float(overview_data.get('ReturnOnEquityTTM', 0)),
                    'eps': float(overview_data.get('EPS', 0)),
                    'profit_margin': float(overview_data.get('ProfitMargin', 0))
                },
                
                # Analyst Data
                'analyst_data': {
                    'ratings': {
                        'strong_buy': analyst_data.get('analyst_ratings_strong_buy', 0),
                        'buy': analyst_data.get('analyst_ratings_buy', 0),
                        'hold': analyst_data.get('analyst_ratings_hold', 0),
                        'sell': analyst_data.get('analyst_ratings_sell', 0),
                        'strong_sell': analyst_data.get('analyst_ratings_strong_sell', 0)
                    },
                    'technical_indicators': {
                        'rsi': analyst_data.get('rsi', 0),
                        'macd': analyst_data.get('macd', 0),
                        'volatility': analyst_data.get('volatility', 0),
                        'sentiment_score': analyst_data.get('sentiment_score', 0),
                        'beta': analyst_data.get('beta', 0)
                    }
                }
            }
            
            return merged_data
            
        except Exception as e:
            self.logger.error(f"Error merging data: {str(e)}")
            return {}

    def _calculate_buffet_scores(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate Warren Buffet criteria scores
        """
        try:
            fundamental_data = data.get('fundamental_data', {})
            market_data = data.get('market_data', {})
            
            pe_ratio = fundamental_data.get('pe_ratio', 0)
            roe = fundamental_data.get('roe', 0)
            current_price = market_data.get('price', 0)
            
            # Calculate individual scores
            pe_score = 1 / pe_ratio if pe_ratio > 0 else 0
            roe_score = roe / 100 if roe > 0 else 0
            
            # Simple DCF calculation (simplified for demonstration)
            eps = fundamental_data.get('eps', 0)
            growth_rate = 0.05  # Assumed 5% growth
            discount_rate = 0.10  # Assumed 10% discount rate
            
            dcf_value = 0
            for year in range(1, 6):
                dcf_value += (eps * (1 + growth_rate) ** year) / (1 + discount_rate) ** year
            
            dcf_score = (dcf_value - current_price) / current_price if current_price > 0 else 0
            
            # Calculate total score
            total_score = pe_score + roe_score + dcf_score
            
            return {
                'pe_score': round(pe_score, 2),
                'roe_score': round(roe_score, 2),
                'dcf_score': round(dcf_score, 2),
                'total_score': round(total_score, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating Buffet scores: {str(e)}")
            return {}

    def _is_cache_valid(self, symbol: str) -> bool:
        """
        Check if cached data is still valid
        """
        if symbol not in self.cache_timestamp:
            return False
            
        elapsed = (datetime.now() - self.cache_timestamp[symbol]).total_seconds()
        return elapsed < self.cache_duration

    def _cache_data(self, symbol: str, data: Dict[str, Any]):
        """
        Cache integrated data
        """
        self.cached_data[symbol] = data
        self.cache_timestamp[symbol] = datetime.now()

    def get_cached_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data for a symbol
        """
        return self.cached_data.get(symbol) if self._is_cache_valid(symbol) else None 