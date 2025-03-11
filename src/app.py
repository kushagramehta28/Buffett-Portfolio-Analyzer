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
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
    "expose_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True,
    "send_wildcard": False,
    "max_age": 86400
}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://buffett-portfolio-analyzer-iiitd.vercel.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

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
    
    # Handle OPTIONS preflight request
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200
        
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    print(f"API Key present: {'Yes' if api_key else 'No'}")
    
    if not api_key:
        error_msg = "Alpha Vantage API key not found!"
        print(error_msg)
        return jsonify({'error': error_msg}), 500
    
    db = SessionLocal()
    api = AlphaVantageAPI()
    
    try:
        stocks = db.query(Stock).all()
        print(f"Found {len(stocks)} stocks to analyze")
        
        if not stocks:
            print("No stocks found in database")
            return jsonify({'error': 'No stocks found to analyze'}), 404
            
        results = []
        invalid_stocks = []
        
        for stock in stocks:
            print(f"\n=== Processing {stock.symbol} ===")
            try:
                # Get market data
                metrics = api.get_all_metrics(stock.symbol)
                print(f"Market metrics for {stock.symbol}: {metrics}")
                
                if metrics is None:
                    print(f"No metrics available for {stock.symbol}, marking as invalid")
                    invalid_stocks.append(stock.symbol)
                    db.delete(stock)
                    continue
                
                if metrics.get('current_price') is None:
                    print(f"No price data for {stock.symbol}, marking as invalid")
                    invalid_stocks.append(stock.symbol)
                    db.delete(stock)
                    continue
                
                # Update stock with market metrics
                stock.current_price = metrics['current_price']
                stock.pe_ratio = metrics['pe_ratio']
                stock.roe = metrics['roe']
                print(f"Updated market metrics - price: {stock.current_price}, pe: {stock.pe_ratio}, roe: {stock.roe}")
                
                # Calculate scores
                print(f"\nCalculating scores for {stock.symbol}:")
                
                # PE Score calculation
                if metrics['pe_ratio'] <= 0:  # Handle negative or zero P/E
                    pe_score = 0
                elif metrics['pe_ratio'] <= 10:
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
                
                print(f"PE Score: {pe_score}")
                
                # ROE Score calculation
                if metrics['roe'] <= 0:  # Handle negative ROE
                    roe_score = 0
                elif metrics['roe'] >= 30:
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
                
                print(f"ROE Score: {roe_score}")
                
                # Calculate total score
                total_score = (pe_score + roe_score) / 2
                print(f"Total Score: {total_score}")
                
                # Update stock scores
                stock.pe_score = pe_score
                stock.roe_score = roe_score
                stock.total_score = total_score
                
                # Add to results
                results.append({
                    'symbol': stock.symbol,
                    'current_price': metrics['current_price'],
                    'pe_ratio': metrics['pe_ratio'],
                    'roe': metrics['roe'],
                    'total_score': total_score
                })
                
            except Exception as e:
                print(f"Error processing {stock.symbol}: {str(e)}")
                invalid_stocks.append(stock.symbol)
                db.delete(stock)
        
        print("\nCommitting changes to database...")
        db.commit()
        print("Database updated successfully")
        
        # Prepare response
        response_data = {
            'status': 'success',
            'results': results
        }
        if invalid_stocks:
            response_data['invalid_stocks'] = invalid_stocks
            response_data['message'] = f'Analysis completed. Removed invalid stocks: {", ".join(invalid_stocks)}'
        else:
            response_data['message'] = 'Analysis completed successfully'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        error_msg = f"Error during analysis: {str(e)}"
        print(error_msg)
        db.rollback()
        return jsonify({'error': error_msg, 'status': 'error'}), 500
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