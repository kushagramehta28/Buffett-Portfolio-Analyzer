import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

class AlphaVantageAPI:
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.base_url = 'https://www.alphavantage.co/query'
        self.delay = 12  # Delay between API calls to respect rate limit (5 calls per minute)

    def get_company_overview(self, symbol):
        """Get company overview including P/E ratio and ROE"""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params)
        time.sleep(self.delay)  # Respect API rate limit
        data = response.json()
        
        return {
            'pe_ratio': float(data.get('PERatio', 0)),
            'roe': float(data.get('ReturnOnEquityTTM', 0)) * 100  # Convert to percentage
        }

    def get_daily_prices(self, symbol):
        """Get daily stock prices"""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params)
        time.sleep(self.delay)  # Respect API rate limit
        data = response.json()
        
        # Get the most recent day's data
        latest_day = list(data['Time Series (Daily)'].keys())[0]
        daily_data = data['Time Series (Daily)'][latest_day]
        
        return {
            'current_price': float(daily_data['4. close']),
            'high_price': float(daily_data['2. high']),
            'low_price': float(daily_data['3. low'])
        }

    def calculate_dcf(self, symbol):
        """
        Calculate a simple DCF value using available data
        Note: This is a simplified calculation for demonstration
        """
        # Get income statement data
        params = {
            'function': 'INCOME_STATEMENT',
            'symbol': symbol,
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params)
        time.sleep(self.delay)  # Respect API rate limit
        data = response.json()
        
        try:
            # Get the most recent year's net income
            net_income = float(data['annualReports'][0]['netIncome'])
            # Assume 5% growth rate for 5 years
            growth_rate = 0.05
            discount_rate = 0.10
            
            # Simple DCF calculation
            dcf_value = 0
            for year in range(1, 6):
                projected_cash_flow = net_income * (1 + growth_rate) ** year
                dcf_value += projected_cash_flow / (1 + discount_rate) ** year
            
            return dcf_value
        except (KeyError, IndexError, ValueError):
            return 0

    def get_all_metrics(self, symbol):
        """Get all required metrics for a stock"""
        try:
            # Check if we've hit the API rate limit
            test_params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.api_key
            }
            response = requests.get(self.base_url, params=test_params)
            data = response.json()
            
            # If we get any error or missing data, use demo data
            if 'Note' in data or 'Error Message' in data or 'Time Series (Daily)' not in data:
                print(f"API rate limit reached or error occurred. Using demo data for {symbol}...")
                return self._get_demo_data(symbol)
            
            # If no rate limit, get real data
            daily_prices = self.get_daily_prices(symbol)
            company_data = self.get_company_overview(symbol)
            
            return {
                'current_price': daily_prices['current_price'],
                'high_price': daily_prices['high_price'],
                'low_price': daily_prices['low_price'],
                'pe_ratio': company_data['pe_ratio'],
                'roe': company_data['roe']
            }
            
        except Exception as e:
            print(f"Error fetching metrics for {symbol}, falling back to demo data: {str(e)}")
            return self._get_demo_data(symbol)  # Fall back to demo data on any error 

    def _get_demo_data(self, symbol):
        """Return demo data when API rate limit is reached"""
        # Define known valid stocks with their demo data
        demo_data = {
            'AAPL': {
                'current_price': 181.45,
                'high_price': 182.34,
                'low_price': 180.17,
                'pe_ratio': 28.5,
                'roe': 45.0
            },
            'GOOGL': {
                'current_price': 2789.61,
                'high_price': 2800.12,
                'low_price': 2775.89,
                'pe_ratio': 25.8,
                'roe': 30.5
            },
            'MSFT': {
                'current_price': 378.92,
                'high_price': 380.15,
                'low_price': 377.23,
                'pe_ratio': 32.4,
                'roe': 42.7
            },
            'TSLA': {
                'current_price': 262.67,
                'high_price': 265.12,
                'low_price': 260.89,
                'pe_ratio': 75.2,
                'roe': 25.3
            }
        }
        
        # Only return demo data for known valid stocks
        return demo_data.get(symbol, None) 