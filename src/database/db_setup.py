from sqlalchemy import create_engine, Column, String, DateTime, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Create the base class for declarative models
Base = declarative_base()

# Define the Stock model
class Stock(Base):
    __tablename__ = 'stocks'
    
    symbol = Column(String(10), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Price information
    current_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    
    # Financial metrics
    pe_ratio = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)
    dcf = Column(Float, nullable=True)
    
    # New fields from CSV
    analysis_date = Column(DateTime, nullable=True)
    analyst_ratings_buy = Column(Integer, nullable=True)
    analyst_ratings_hold = Column(Integer, nullable=True)
    analyst_ratings_sell = Column(Integer, nullable=True)
    analyst_ratings_strong_sell = Column(Integer, nullable=True)
    analyst_ratings_strong_buy = Column(Integer, nullable=True)
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    beta = Column(Float, nullable=True)
    
    # Buffet scores (normalized values)
    pe_score = Column(Float, nullable=True)
    roe_score = Column(Float, nullable=True)
    dcf_score = Column(Float, nullable=True)
    total_score = Column(Float, nullable=True)

    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}')>"

# Create database engine
DATABASE_URL = "sqlite:///stocks.db"
engine = create_engine(DATABASE_URL)

# Create all tables
Base.metadata.create_all(engine)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 