from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
import datetime

Base=declarative_base()

class Asset(Base):
    __tablename__="assets"

    id=Column(Integer, primary_key=True)
    symbol=Column(String, unique=True)
    name=Column(String)

class PriceHistory(Base):
    __tablename__="price_history"

    id=Column(Integer, primary_key=True)
    asset_id=Column(Integer)
    price=Column(Float)
    collected_at=Column(DateTime, default=datetime.datetime.utcnow)

class MarketData(Base):
    __tablename__="market_data"

    id=Column(Integer, primary_key=True)
    asset_id=Column(Integer)
    market_cap=Column(Float)
    volume=Column(Float)
    change_24h=Column(Float)
    collected_at=Column(DateTime, default=datetime.datetime.utcnow)

class LiveMarket(Base):
    __tablename__="live_market"

    id=Column(Integer, primary_key=True)
    asset_id=Column(Integer)
    price=Column(Float)
    market_cap=Column(Float)
    volume=Column(Float)
    change_24h=Column(Float)
    collected_at=Column(DateTime, default=datetime.datetime.utcnow)

class LiveSignal(Base):
    __tablename__="live_signals"

    id=Column(Integer, primary_key=True)
    asset_id=Column(Integer)
    signal_type=Column(String)
    value=Column(Float)
    created_at=Column(DateTime, default=datetime.datetime.utcnow)