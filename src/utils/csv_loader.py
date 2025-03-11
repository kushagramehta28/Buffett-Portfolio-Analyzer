import pandas as pd
from database.db_setup import SessionLocal, Stock
from datetime import datetime

class AnalystDataLoader:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        
    def load_data(self):
        """Load analyst data from CSV file"""
        try:
            df = pd.read_csv(self.csv_path)
            # Convert analysis_date to datetime
            df['analysis_date'] = pd.to_datetime(df['analysis_date'])
            print(f"Successfully loaded {len(df)} records from CSV")
            return df
        except Exception as e:
            print(f"Error loading CSV file: {str(e)}")
            return None
            
    def sync_with_database(self):
        """Sync analyst data with existing stock records"""
        df = self.load_data()
        if df is None:
            return
            
        db = SessionLocal()
        try:
            # Get all stock symbols from our database
            existing_stocks = db.query(Stock).all()
            existing_symbols = {stock.symbol for stock in existing_stocks}
            
            # Filter CSV data to only include stocks in our database
            mask = df['symbol'].isin(existing_symbols)
            relevant_data = df[mask]
            
            # Update database with CSV data
            for _, row in relevant_data.iterrows():
                stock = db.query(Stock).filter(Stock.symbol == row['symbol']).first()
                if stock:
                    # Update stock with analyst data
                    stock.analysis_date = row['analysis_date']
                    stock.analyst_ratings_buy = row['analyst_ratings_buy']
                    stock.analyst_ratings_hold = row['analyst_ratings_hold']
                    stock.analyst_ratings_sell = row['analyst_ratings_sell']
                    stock.analyst_ratings_strong_sell = row['analyst_ratings_strong_sell']
                    stock.analyst_ratings_strong_buy = row['analyst_ratings_strong_buy']
                    stock.rsi = row['rsi']
                    stock.macd = row['macd']
                    stock.volatility = row['volatility']
                    stock.sentiment_score = row['sentiment_score']
                    stock.beta = row['beta']
                    
            db.commit()
            print(f"Successfully updated database with analyst data")
            
        except Exception as e:
            db.rollback()
            print(f"Error syncing analyst data: {str(e)}")
        finally:
            db.close()

    def get_analyst_sentiment(self, row):
        """Calculate overall analyst sentiment (-1 to 1)"""
        total_ratings = (row['analyst_ratings_strong_buy'] * 2 +
                        row['analyst_ratings_buy'] * 1 +
                        row['analyst_ratings_hold'] * 0 +
                        row['analyst_ratings_sell'] * -1 +
                        row['analyst_ratings_strong_sell'] * -2)
        total_count = (row['analyst_ratings_strong_buy'] +
                      row['analyst_ratings_buy'] +
                      row['analyst_ratings_hold'] +
                      row['analyst_ratings_sell'] +
                      row['analyst_ratings_strong_sell'])
        return total_ratings / (total_count * 2) if total_count > 0 else 0 