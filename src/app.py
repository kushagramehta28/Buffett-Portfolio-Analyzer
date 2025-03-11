from flask import Flask, jsonify, request
from flask_cors import CORS
from .database.db_setup import SessionLocal, Stock
from .utils.alpha_vantage import AlphaVantageAPI
import re
import os
from .data_sources.manager import DataSourceManager
from .data_sources.alpha_vantage_source import AlphaVantageSource
from .data_sources.analyst_source import AnalystDataSource
from .integration.integration_system import DataIntegrationSystem

# Get the application root directory
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": [
        "https://buffett-portfolio-analyzer-iiitd.vercel.app",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:4173",
        "http://localhost:4174"
    ],
    "methods": ["GET", "POST", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type"],
    "supports_credentials": True
}})

def validate_stock_symbol(symbol):
    """Validate stock symbol format (1-5 uppercase letters)"""
    pattern = r'^[A-Z]{1,5}$'
    return bool(re.match(pattern, symbol))

@app.route('/stocks', methods=['GET'])
def get_stocks():
    print("Received GET request for /stocks")  # Debug log
    db = SessionLocal()
    try:
        print("Querying database...")  # Debug log
        stocks = db.query(Stock).all()
        print(f"Found {len(stocks)} stocks")  # Debug log
        stock_list = []
        for stock in stocks:
            stock_data = {
                'symbol': stock.symbol,
                'current_price': stock.current_price,
                'pe_ratio': stock.pe_ratio,
                'roe': stock.roe,
                'total_score': stock.total_score
            }
            stock_list.append(stock_data)
        print(f"Returning {len(stock_list)} stocks")  # Debug log
        return jsonify(stock_list)
    except Exception as e:
        print(f"Error in /stocks: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/stocks', methods=['POST'])
def add_stock():
    print("\n=== Adding Stock ===")  # Debug log
    data = request.json
    print("Received data:", data)  # Debug log
    
    symbol = data.get('symbol', '').strip().upper()
    print(f"Processing symbol: {symbol}")  # Debug log
    
    if not symbol:
        print("Error: No symbol provided")  # Debug log
        return jsonify({'message': 'Stock symbol is required'}), 400
        
    if not validate_stock_symbol(symbol):
        print(f"Error: Invalid symbol format: {symbol}")  # Debug log
        return jsonify({'message': 'Invalid stock symbol format'}), 400
    
    db = SessionLocal()
    try:
        # Check if symbol already exists
        print(f"Checking if {symbol} exists in database...")  # Debug log
        existing_stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if existing_stock:
            print(f"Stock {symbol} already exists")  # Debug log
            return jsonify({'message': f'Stock {symbol} already exists'}), 400
            
        # Add new stock
        print(f"Adding new stock: {symbol}")  # Debug log
        new_stock = Stock(symbol=symbol)
        db.add(new_stock)
        db.commit()
        print(f"Successfully added stock: {symbol}")  # Debug log
        return jsonify({'message': f'Stock {symbol} added successfully'}), 201
        
    except Exception as e:
        print(f"Error adding stock: {str(e)}")  # Debug log
        db.rollback()
        return jsonify({'message': f'Error adding stock: {str(e)}'}), 500
    finally:
        db.close()

@app.route('/analyze-stocks', methods=['POST'])
def analyze_stocks():
    print("\n=== Starting Stock Analysis ===")
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    print(f"API Key present: {'Yes' if api_key else 'No'}")  # Debug log (don't print the actual key)
    
    if not api_key:
        print("No API key found!")
        return jsonify({'message': 'Alpha Vantage API key not found!'}), 500
    
    db = SessionLocal()
    api = AlphaVantageAPI()
    
    try:
        # Initialize data sources for analyst data
        data_manager = DataSourceManager()
        analyst_data_path = os.path.join(APP_ROOT, 'data', 'analyst_data.csv')
        print(f"Looking for analyst data at: {analyst_data_path}")
        
        if not os.path.exists(analyst_data_path):
            print(f"Warning: Analyst data file not found at {analyst_data_path}")
            # Create an empty analyst source if file doesn't exist
            analyst_source = AnalystDataSource(csv_path=analyst_data_path, create_if_missing=True)
        else:
            analyst_source = AnalystDataSource(csv_path=analyst_data_path)
            
        print(f"Initialized analyst source with path: {analyst_data_path}")
        success = data_manager.register_source(analyst_source)
        print(f"Registered analyst source: {success}")
        
        stocks = db.query(Stock).all()
        print(f"Found {len(stocks)} stocks to analyze")
        
        if not stocks:
            print("No stocks found in database")
            return jsonify({'message': 'No stocks found to analyze'}), 404
            
        results = []
        invalid_stocks = []
        
        for stock in stocks:
            print(f"\n=== Processing {stock.symbol} ===")
            # Get market data
            metrics = api.get_all_metrics(stock.symbol)
            print(f"Market metrics: {metrics}")  # Debug print
            
            # Get analyst data
            analyst_data = analyst_source.execute_query({'symbol': stock.symbol})
            print(f"Raw analyst data: {analyst_data}")  # Debug print
            
            if metrics and metrics.get('current_price') is not None:
                # Update stock with market metrics
                stock.current_price = metrics['current_price']
                stock.pe_ratio = metrics['pe_ratio']
                stock.roe = metrics['roe']
                print(f"Updated market metrics - price: {stock.current_price}, pe: {stock.pe_ratio}, roe: {stock.roe}")
                
                # Update stock with analyst data
                if analyst_data:
                    # Direct access to flat structure
                    stock.analyst_ratings_strong_buy = analyst_data.get('analyst_ratings_strong_buy', 0)
                    stock.analyst_ratings_buy = analyst_data.get('analyst_ratings_buy', 0)
                    stock.analyst_ratings_hold = analyst_data.get('analyst_ratings_hold', 0)
                    stock.analyst_ratings_sell = analyst_data.get('analyst_ratings_sell', 0)
                    stock.analyst_ratings_strong_sell = analyst_data.get('analyst_ratings_strong_sell', 0)
                    
                    # Technical indicators - direct access
                    stock.rsi = analyst_data.get('rsi', 0)
                    stock.macd = analyst_data.get('macd', 0)
                    stock.volatility = analyst_data.get('volatility', 0)
                    stock.sentiment_score = analyst_data.get('sentiment_score', 0)
                    stock.beta = analyst_data.get('beta', 0)
                    
                    print(f"Updated analyst data for {stock.symbol}:")
                    print(f"Ratings: strong_buy={stock.analyst_ratings_strong_buy}, buy={stock.analyst_ratings_buy}")
                    print(f"Technical: rsi={stock.rsi}, macd={stock.macd}")
                else:
                    print(f"No analyst data found for {stock.symbol}")
                
                # Calculate scores
                # PE Score: Lower is better
                print(f"\nCalculating scores for {stock.symbol}:")
                print(f"Raw PE Ratio: {metrics['pe_ratio']}")
                print(f"Raw ROE: {metrics['roe']}")

                # < 10: Excellent (1.0)
                # 10-15: Very Good (0.8)
                # 15-20: Good (0.6)
                # 20-25: Fair (0.4)
                # 25-30: Poor (0.2)
                # > 30: Very Poor (0)
                if metrics['pe_ratio'] <= 10:
                    pe_score = 1.0
                elif metrics['pe_ratio'] <= 15:
                    pe_score = 0.8
                elif metrics['pe_ratio'] <= 20:
                    pe_score = 0.6
                elif metrics['pe_ratio'] <= 25:
                    pe_score = 0.4
                elif metrics['pe_ratio'] <= 30:
                    pe_score = 0.2
                else:
                    pe_score = 0

                print(f"Calculated PE Score: {pe_score}")

                # ROE Score: Higher is better
                # > 30: Excellent (1.0)
                # 25-30: Very Good (0.8)
                # 20-25: Good (0.6)
                # 15-20: Fair (0.4)
                # 10-15: Poor (0.2)
                # < 10: Very Poor (0)
                if metrics['roe'] >= 30:
                    roe_score = 1.0
                elif metrics['roe'] >= 25:
                    roe_score = 0.8
                elif metrics['roe'] >= 20:
                    roe_score = 0.6
                elif metrics['roe'] >= 15:
                    roe_score = 0.4
                elif metrics['roe'] >= 10:
                    roe_score = 0.2
                else:
                    roe_score = 0

                print(f"Calculated ROE Score: {roe_score}")

                # Calculate total score (weighted average)
                total_score = (pe_score + roe_score) / 2
                print(f"Calculated Total Score: {total_score}\n")

                stock.pe_score = pe_score
                stock.roe_score = roe_score
                stock.total_score = total_score
                
                results.append({
                    'symbol': stock.symbol,
                    'current_price': metrics['current_price'],
                    'pe_ratio': metrics['pe_ratio'],
                    'roe': metrics['roe'],
                    'total_score': total_score,
                    # Add analyst data to results
                    'analyst_ratings_strong_buy': stock.analyst_ratings_strong_buy,
                    'analyst_ratings_buy': stock.analyst_ratings_buy,
                    'analyst_ratings_hold': stock.analyst_ratings_hold,
                    'analyst_ratings_sell': stock.analyst_ratings_sell,
                    'analyst_ratings_strong_sell': stock.analyst_ratings_strong_sell,
                    'rsi': stock.rsi,
                    'macd': stock.macd,
                    'volatility': stock.volatility,
                    'sentiment_score': stock.sentiment_score,
                    'beta': stock.beta
                })
            else:
                print(f"Invalid or no metrics returned for {stock.symbol}")
                invalid_stocks.append(stock.symbol)
                # Remove invalid stock from database
                db.delete(stock)
        
        print("\nCommitting changes to database...")
        db.commit()
        print("Database updated successfully")
        
        # If any stocks were invalid, include them in the response
        response_data = {
            'message': 'Analysis completed successfully',
            'results': results
        }
        if invalid_stocks:
            response_data['invalid_stocks'] = invalid_stocks
            response_data['message'] = f'Analysis completed. Removed invalid stocks: {", ".join(invalid_stocks)}'
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        db.rollback()
        return jsonify({'message': f'Error during analysis: {str(e)}'}), 500
    finally:
        db.close()

@app.route('/', methods=['GET'])
def home():
    return "Buffett Analyzer API is running!"  # Add a simple root route

@app.route('/remove-stock/<symbol>', methods=['DELETE'])
def remove_stock(symbol):
    db = SessionLocal()
    try:
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if stock:
            db.delete(stock)
            db.commit()
            return jsonify({'message': f'Stock {symbol} removed successfully'})
        return jsonify({'error': f'Stock {symbol} not found'}), 404
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to remove stock {symbol}'}), 400
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 