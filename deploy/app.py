import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
import streamlit as st
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database.db import engine
from database.models import Asset,LiveMarket,LiveSignal,PriceHistory

Session=sessionmaker(bind=engine)
st.set_page_config(layout="wide")
st.title("HYBRID ENGINE DASHBOARD")

@st.cache_data(ttl=10)
def load_data():
    session=Session()

    market=session.query(
        Asset.symbol,
        LiveMarket.price,
        LiveMarket.volume,
        LiveMarket.change_24h
    ).join(LiveMarket,Asset.id==LiveMarket.asset_id).all()
    signals=session.query(
        Asset.symbol,
        LiveSignal.signal_type,
        LiveSignal.value
    ).join(LiveSignal,Asset.id==LiveSignal.asset_id).all()

    session.close()

    df_market=pd.DataFrame(market,columns=["symbol","price","volume","change_24h"])
    df_signals=pd.DataFrame(signals,columns=["symbol","type","value"])

    score_map={}
    state_map={}

    for _,row in df_signals.iterrows():
        if row["type"]=="score":
            score_map[row["symbol"]]=row["value"]
        elif row["type"]=="state":
            state_map[row["symbol"]]=row["value"]
    df_market["score"]=df_market["symbol"].map(score_map).fillna(0)
    df_market["state"]=df_market["symbol"].map(state_map).fillna(0)

    return df_market

def load_history(symbol):
    session=Session()

    asset=session.query(Asset).filter_by(symbol=symbol).first()

    if not asset:
        return pd.DataFrame()

    prices=session.query(
        PriceHistory.price,
        PriceHistory.collected_at
    ).filter_by(asset_id=asset.id).order_by(PriceHistory.collected_at).all()

    session.close()

    return pd.DataFrame(prices,columns=["price","time"])

df=load_data()

st.subheader("Top Assets by Score")
df_sorted=df.sort_values(by="score",ascending=False)
st.dataframe(df_sorted,use_container_width=True)

st.subheader("Asset Analysis")
symbols=df_sorted["symbol"].unique().tolist()
selected=st.selectbox("Select asset",symbols)

asset_data=df_sorted[df_sorted["symbol"]==selected].iloc[0]
col1,col2,col3,col4=st.columns(4)
col1.metric("Price",f"{asset_data['price']:.4f}")
col2.metric("Volume",f"{asset_data['volume']:.2f}")
col3.metric("Score",f"{asset_data['score']:.3f}")
state_label="NEUTRAL"
if asset_data["state"]==1:
    state_label="BULL"
elif asset_data["state"]==-1:
    state_label="BEAR"
col4.metric("State",state_label)

st.subheader("Price History")
history=load_history(selected)
if not history.empty:
    history=history.set_index("time")
    st.line_chart(history["price"])
else:
    st.warning("No historical data available")
