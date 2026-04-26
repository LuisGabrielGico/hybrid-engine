import time
import logging
from datetime import datetime
from services.pipeline import run_pipeline
from sqlalchemy.orm import sessionmaker
from database.db import engine
from database.models import LiveSignal,Asset

Session=sessionmaker(bind=engine)

INTERVAL_SECONDS=30

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename="scheduler.log",
    filemode="a"
)

def check_alerts():
    session=Session()

    try:
        signals=session.query(Asset.symbol,LiveSignal.signal_type,LiveSignal.value)\
            .join(LiveSignal,Asset.id==LiveSignal.asset_id)\
            .all()
            
        for symbol,stype,value in signals:
            if stype=="score" and value>1.5:
                logging.info(f"[ALERT] {symbol} strong bullish({value:.2f})")
            elif stype=="score" and value<-1.5:
                logging.info(f"[ALERT] {symbol} strong bullish({value:.2f})")

    finally:
        session.close()

def run_cycle():
    start_time=time.time()

    logging.info("Cycle started")

    try:
        run_pipeline()
        check_alerts()
    except Exception as e:
        logging.error(f"Cycle error: {e}")

    duration=time.time()-start_time
    logging.info(f"Cycle finished in {duration:.2f}s")

def start_scheduler():
    logging.info("Scheduler initialized")

    while True:
        cycle_start=time.time()

        run_cycle()

        elapsed=time.time()-cycle_start
        sleep_time=max(0,INTERVAL_SECONDS-elapsed)

        logging.info(f"Sleeping {sleep_time:.2f}s")
        time.sleep(sleep_time)
