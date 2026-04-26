from core.collector import fetch_prices
from database.db import engine
from database.models import Asset,PriceHistory,MarketData,LiveMarket,LiveSignal
from sqlalchemy.orm import sessionmaker
from datetime import datetime,timedelta
import statistics
from core.signals import detect_price_signal,detect_volume_spike,detect_volatility

Session=sessionmaker(bind=engine)

def z_score(value,values):
    if not values or len(values)<2:
            return 0
    mean=sum(values)/len(values)
    stdev=statistics.pstdev(values)
    if stdev==0:
        return 0
    return (value-mean)/stdev

def cleanup_live_data(session):
    session.query(LiveSignal).delete()
    session.query(LiveMarket).delete()

def cleanup_history_data(session,days=30):
    limit=datetime.utcnow()-timedelta(days=days)
    session.query(PriceHistory).filter(PriceHistory.collected_at<limit).delete()
    session.query(MarketData).filter(MarketData.collected_at<limit).delete()

def run_pipeline():
    session=Session()
    cleanup_live_data(session)

    data=fetch_prices()

    for item in data:
        asset=session.query(Asset).filter_by(symbol=item["symbol"]).first()

        if not asset:
            asset=Asset(symbol=item["symbol"],name=item["name"])
            session.add(asset)
            session.commit()

        recent_prices=session.query(PriceHistory).filter_by(asset_id=asset.id).order_by(PriceHistory.collected_at.desc()).limit(20).all()
        price_values=[p.price for p in recent_prices]

        recent_market=session.query(MarketData).filter_by(asset_id=asset.id).order_by(MarketData.collected_at.desc()).limit(20).all()
        volume_values=[v.volume for v in recent_market]
        change_values=[v.change_24h for v in recent_market]

        price_z=z_score(item["price"],price_values)
        volume_z=z_score(item["volume"],volume_values)
        volatility_z=z_score(item["change_24h"],change_values)

        score=price_z*0.4+volume_z*0.35+volatility_z*0.25

        if score>1.0:
            state=1
        elif score<-1.0:
            state=-1
        else:
            state=0

        session.add(PriceHistory(asset_id=asset.id,price=item["price"]))
        session.add(MarketData(asset_id=asset.id,market_cap=item["market_cap"],volume=item["volume"],change_24h=item["change_24h"]))
        session.add(LiveMarket(asset_id=asset.id,price=item["price"],market_cap=item["market_cap"],volume=item["volume"],change_24h=item["change_24h"]))
        session.add(LiveSignal(asset_id=asset.id,signal_type="score",value=score))
        session.add(LiveSignal(asset_id=asset.id,signal_type="state",value=state))

    cleanup_history_data(session,days=30)
    session.commit()
    session.close()
