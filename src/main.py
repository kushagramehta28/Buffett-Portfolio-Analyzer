from database.db_setup import SessionLocal, Stock
from utils.alpha_vantage import AlphaVantageAPI
import re
import os
from dotenv import load_dotenv
from utils.csv_loader import AnalystDataLoader
from data_sources.manager import DataSourceManager
from data_sources.alpha_vantage_source import AlphaVantageSource
from data_sources.analyst_source import AnalystDataSource
from typing import Dict, Any, List
from integration.integration_system import DataIntegrationSystem
import asyncio
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
load_dotenv()

def validate_stock_symbol(symbol):
    """
    Validate stock symbol format (1-5 uppercase letters)
    """
    pattern = r'^[A-Z]{1,5}$'
    return bool(re.match(pattern, symbol))

def add_stock_symbols():
    db = SessionLocal()
    print("\nWelcome to Buffet Analyzer!")
    print("Enter stock symbols (1-5 uppercase letters, e.g., AAPL)")
    print("Enter 'done' when finished\n")
    
    while True:
        symbol = input("Enter stock symbol: ").strip().upper()
        
        if symbol.lower() == 'done':
            break
            
        if not validate_stock_symbol(symbol):
            print("Invalid symbol format. Please enter 1-5 uppercase letters.")
            continue
            
        try:
            # Check if symbol already exists
            existing_stock = db.query(Stock).filter(Stock.symbol == symbol).first()
            if existing_stock:
                print(f"Symbol {symbol} already exists in database.")
                continue
                
            # Add new stock to database
            new_stock = Stock(symbol=symbol)
            db.add(new_stock)
            db.commit()
            print(f"Added {symbol} to database.")
            
        except Exception as e:
            db.rollback()
            print(f"Error adding symbol {symbol}: {str(e)}")
    
    # Display all stored symbols
    stocks = db.query(Stock).all()
    print("\nStored stock symbols:")
    for stock in stocks:
        print(f"- {stock.symbol}")
    
    db.close()

def update_stock_metrics():
    """Fetch and update financial metrics for all stocks in database"""
    if not os.getenv('ALPHA_VANTAGE_API_KEY'):
        print("\nError: Alpha Vantage API key not found!")
        print("Please create a .env file with your API key as ALPHA_VANTAGE_API_KEY=your_key_here")
        return
        
    db = SessionLocal()
    api = AlphaVantageAPI()
    
    print("\nFetching financial metrics for stored stocks...")
    stocks = db.query(Stock).all()
    
    for stock in stocks:
        print(f"\nProcessing {stock.symbol}...")
        metrics = api.get_all_metrics(stock.symbol)
        
        if metrics:
            # Update stock with new metrics
            for key, value in metrics.items():
                setattr(stock, key, value)
            
            db.commit()
            print(f"Updated metrics for {stock.symbol}")
            print(f"Current Price: ${metrics['current_price']:.2f}")
            print(f"P/E Ratio: {metrics['pe_ratio']:.2f}")
            print(f"ROE: {metrics['roe']:.2f}%")
            print(f"DCF Value: ${metrics['dcf']:.2f}")
            print(f"Total Buffet Score: {metrics['total_score']:.2f}")
        else:
            print(f"Failed to fetch metrics for {stock.symbol}")
    
    # Display ranked stocks
    print("\nStocks ranked by Buffet Score:")
    ranked_stocks = db.query(Stock).order_by(Stock.total_score.desc()).all()
    
    for i, stock in enumerate(ranked_stocks, 1):
        print(f"\n{i}. {stock.symbol}")
        print(f"   Total Score: {stock.total_score:.2f}")
        print(f"   P/E Score: {stock.pe_score:.2f}")
        print(f"   ROE Score: {stock.roe_score:.2f}")
        print(f"   DCF Score: {stock.dcf_score:.2f}")
    
    db.close()

def load_analyst_data():
    """Load and sync analyst data from CSV file"""
    csv_path = input("\nEnter the path to your CSV file: ")
    if not os.path.exists(csv_path):
        print("Error: File not found!")
        return
        
    loader = AnalystDataLoader(csv_path)
    loader.sync_with_database()

def display_complete_analysis():
    """Display complete analysis including both financial and analyst metrics"""
    db = SessionLocal()
    stocks = db.query(Stock).all()
    
    print("\nComplete Stock Analysis:")
    for stock in stocks:
        print(f"\n{stock.symbol}")
        print("Financial Metrics:")
        print(f"  P/E Ratio: {stock.pe_ratio:.2f}")
        print(f"  ROE: {stock.roe:.2f}%")
        print(f"  Current Price: ${stock.current_price:.2f}")
        
        print("\nAnalyst Metrics:")
        print(f"  Strong Buy: {stock.analyst_ratings_strong_buy}")
        print(f"  Buy: {stock.analyst_ratings_buy}")
        print(f"  Hold: {stock.analyst_ratings_hold}")
        print(f"  Sell: {stock.analyst_ratings_sell}")
        print(f"  Strong Sell: {stock.analyst_ratings_strong_sell}")
        
        print("\nTechnical Indicators:")
        print(f"  RSI: {stock.rsi:.2f}")
        print(f"  MACD: {stock.macd:.2f}")
        print(f"  Volatility: {stock.volatility:.3f}")
        print(f"  Sentiment Score: {stock.sentiment_score:.2f}")
        print(f"  Beta: {stock.beta:.2f}")
        
        print("\nBuffet Analysis Scores:")
        print(f"  P/E Score: {stock.pe_score:.2f}")
        print(f"  ROE Score: {stock.roe_score:.2f}")
        print(f"  DCF Score: {stock.dcf_score:.2f}")
        print(f"  Total Score: {stock.total_score:.2f}")
        
    db.close()

class BuffetAnalyzer:
    def __init__(self):
        self.manager = DataSourceManager()
        self.integration_system = DataIntegrationSystem()
        self.user_stocks = set()  # Store user's selected stocks
        self.setup_data_sources()

    def setup_data_sources(self):
        alpha_vantage = AlphaVantageSource(api_key=os.getenv('ALPHA_VANTAGE_API_KEY'))
        analyst_data = AnalystDataSource(csv_path='analyst_data.csv')
        
        self.manager.register_source(alpha_vantage)
        self.manager.register_source(analyst_data)

    async def validate_stock_symbol(self, symbol: str) -> bool:
        """Validate if stock symbol exists"""
        alpha_vantage = self.manager.get_source("alpha_vantage")
        return await alpha_vantage.validate_symbol(symbol)

    async def add_stocks(self):
        """Add stocks to analyze with improved validation"""
        print("\nEnter stock symbols to analyze (e.g., AAPL, MSFT, GOOGL)")
        print("Enter 'done' when finished")
        
        alpha_vantage = self.manager.get_source("alpha_vantage")
        first_symbol = True
        
        while True:
            symbol = input("Enter stock symbol: ").strip().upper()
            
            if symbol.lower() == 'done':
                break
                
            if not self._validate_symbol_format(symbol):
                print("Invalid symbol format. Please use 1-5 uppercase letters.")
                continue

            # Validate symbol
            is_valid, message = await alpha_vantage.validate_symbol(symbol)
            
            # On first symbol, show the validation method being used
            if first_symbol:
                print(f"\nValidation status: {message}")
                first_symbol = False
            
            if is_valid:
                self.user_stocks.add(symbol)
                print(f"Added {symbol} to analysis list")
            else:
                print(f"Error: {symbol} is not a valid stock symbol")
        
        print("\nCurrent stocks for analysis:", ", ".join(sorted(self.user_stocks)))

    def _validate_symbol_format(self, symbol: str) -> bool:
        """Validate stock symbol format"""
        return bool(re.match(r'^[A-Z]{1,5}$', symbol))

    def remove_stocks(self):
        """Remove stocks from analysis list"""
        if not self.user_stocks:
            print("No stocks in analysis list")
            return
            
        print("\nCurrent stocks:", ", ".join(sorted(self.user_stocks)))
        symbol = input("Enter symbol to remove (or 'cancel'): ").strip().upper()
        
        if symbol.lower() == 'cancel':
            return
            
        if symbol in self.user_stocks:
            self.user_stocks.remove(symbol)
            print(f"Removed {symbol} from analysis list")
        else:
            print(f"{symbol} not found in analysis list")

    async def analyze_stock(self, symbol: str) -> Dict:
        """Analyze a single stock with error handling"""
        try:
            alpha_vantage = self.manager.get_source("alpha_vantage")
            analyst_source = self.manager.get_source("analyst_data")
            
            data = await self.integration_system.integrate_stock_data(
                symbol,
                alpha_vantage,
                analyst_source
            )
            
            if 'error' in data:
                print(f"\nError analyzing {symbol}: {data['error']}")
                return None
                
            return data
            
        except Exception as e:
            print(f"\nError analyzing {symbol}: {str(e)}")
            return None

    async def analyze_all_stocks(self):
        """Analyze all stocks in the list with error handling"""
        if not self.user_stocks:
            print("No stocks to analyze. Please add stocks first.")
            return
        
        print(f"\nAnalyzing {len(self.user_stocks)} stocks...")
        results = []
        failed_symbols = []
        
        for symbol in self.user_stocks:
            print(f"\nAnalyzing {symbol}...")
            data = await self.analyze_stock(symbol)
            
            if data and 'error' not in data:
                results.append(self._extract_comparison_metrics(data))
            else:
                failed_symbols.append(symbol)
        
        if failed_symbols:
            print("\nFailed to analyze the following symbols:")
            for symbol in failed_symbols:
                print(f"- {symbol}")
        
        if results:
            self.display_comparison(results)
        else:
            print("\nNo valid results to display")

    def _extract_comparison_metrics(self, data: Dict) -> Dict:
        """Extract key metrics for comparison"""
        return {
            'symbol': data['symbol'],
            'price': data['market_data']['price'],
            'pe_ratio': data['fundamental_data']['pe_ratio'],
            'roe': data['fundamental_data']['roe'],
            'pe_score': data['buffet_analysis']['pe_score'],
            'roe_score': data['buffet_analysis']['roe_score'],
            'dcf_score': data['buffet_analysis']['dcf_score'],
            'total_score': data['buffet_analysis']['total_score'],
            'analyst_buy_ratings': (
                data['analyst_data']['ratings']['strong_buy'] +
                data['analyst_data']['ratings']['buy']
            ),
            'sentiment_score': data['analyst_data']['technical_indicators']['sentiment_score']
        }

    def display_comparison(self, results: List[Dict]):
        """Display comparison of all analyzed stocks"""
        df = pd.DataFrame(results)
        
        # Sort by total Buffet score
        df_sorted = df.sort_values('total_score', ascending=False)
        
        print("\n=== Stock Comparison (Sorted by Buffet Score) ===")
        print("\nTop Stocks by Buffet Criteria:")
        print(df_sorted[['symbol', 'total_score', 'pe_score', 'roe_score', 'dcf_score']].to_string(index=False))
        
        print("\nFundamental Metrics:")
        print(df_sorted[['symbol', 'price', 'pe_ratio', 'roe']].to_string(index=False))
        
        print("\nAnalyst and Sentiment Metrics:")
        print(df_sorted[['symbol', 'analyst_buy_ratings', 'sentiment_score']].to_string(index=False))
        
        # Save detailed report
        self.save_detailed_report(df_sorted)

    def save_detailed_report(self, df: pd.DataFrame):
        """Save detailed analysis to CSV"""
        filename = 'buffet_analysis_report.csv'
        df.to_csv(filename, index=False)
        print(f"\nDetailed report saved to {filename}")

    def display_detailed_analysis(self, symbol: str):
        """Display detailed analysis for a single stock"""
        cached_data = self.integration_system.get_cached_data(symbol)
        if cached_data:
            self.display_analysis(cached_data)
        else:
            print("No cached data found or cache expired")

    def display_analysis(self, data: Dict):
        """Display detailed analysis for a single stock"""
        if 'error' in data:
            print(f"\nError: {data['error']}")
            return

        print("\n=== Market Data ===")
        market_data = data['market_data']
        print(f"Price: ${market_data['price']:.2f}")
        print(f"Change: {market_data['change_percent']}")
        print(f"Volume: {market_data['volume']:,}")

        print("\n=== Fundamental Analysis ===")
        fundamental_data = data['fundamental_data']
        print(f"P/E Ratio: {fundamental_data['pe_ratio']:.2f}")
        print(f"ROE: {fundamental_data['roe']:.2f}%")
        print(f"EPS: ${fundamental_data['eps']:.2f}")

        print("\n=== Analyst Ratings ===")
        ratings = data['analyst_data']['ratings']
        print(f"Strong Buy: {ratings['strong_buy']}")
        print(f"Buy: {ratings['buy']}")
        print(f"Hold: {ratings['hold']}")
        print(f"Sell: {ratings['sell']}")
        print(f"Strong Sell: {ratings['strong_sell']}")

        print("\n=== Technical Indicators ===")
        tech = data['analyst_data']['technical_indicators']
        print(f"RSI: {tech['rsi']:.2f}")
        print(f"MACD: {tech['macd']:.2f}")
        print(f"Volatility: {tech['volatility']:.3f}")
        print(f"Sentiment: {tech['sentiment_score']:.2f}")
        print(f"Beta: {tech['beta']:.2f}")

        print("\n=== Buffet Analysis ===")
        scores = data['buffet_analysis']
        print(f"P/E Score: {scores['pe_score']:.2f}")
        print(f"ROE Score: {scores['roe_score']:.2f}")
        print(f"DCF Score: {scores['dcf_score']:.2f}")
        print(f"Total Score: {scores['total_score']:.2f}")

async def main():
    analyzer = BuffetAnalyzer()
    
    while True:
        print("\nBuffet Stock Analyzer Menu:")
        print("1. Add stocks to analyze")
        print("2. Remove stocks from analysis")
        print("3. View current stock list")
        print("4. Run analysis on all stocks")
        print("5. View detailed analysis for a stock")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == '1':
            await analyzer.add_stocks()
            
        elif choice == '2':
            analyzer.remove_stocks()
            
        elif choice == '3':
            if analyzer.user_stocks:
                print("\nCurrent stocks for analysis:", ", ".join(sorted(analyzer.user_stocks)))
            else:
                print("\nNo stocks in analysis list")
            
        elif choice == '4':
            await analyzer.analyze_all_stocks()
            
        elif choice == '5':
            if not analyzer.user_stocks:
                print("No stocks in analysis list")
                continue
                
            print("\nAvailable stocks:", ", ".join(sorted(analyzer.user_stocks)))
            symbol = input("Enter symbol for detailed analysis: ").strip().upper()
            if symbol in analyzer.user_stocks:
                analyzer.display_detailed_analysis(symbol)
            else:
                print("Symbol not found in analysis list")
            
        elif choice == '6':
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    asyncio.run(main()) 