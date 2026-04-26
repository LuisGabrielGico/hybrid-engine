from textual.app import App,ComposeResult
from textual.widgets import Header,Footer,DataTable,Static
from textual.containers import Container
from textual.reactive import reactive
from sqlalchemy.orm import sessionmaker
from database.db import engine
from database.models import Asset,LiveMarket,LiveSignal

Session=sessionmaker(bind=engine)

class MarketTable(DataTable):
    def on_mount(self):
        self.add_columns("Symbol","Price","Vol","Score","State","Strength")

    def update_data(self):
        session=Session()
        self.clear()

        score_map={}
        state_map={}

        signals=session.query(Asset.symbol,LiveSignal.signal_type,LiveSignal.value)\
            .join(LiveSignal,Asset.id==LiveSignal.asset_id)\
            .all()

        for symbol,stype,value in signals:
            if stype=="score":
                score_map[symbol]=value
            elif stype=="state":
                state_map[symbol]=value

        data=session.query(Asset.symbol,LiveMarket.price,LiveMarket.volume)\
            .join(LiveMarket,Asset.id==LiveMarket.asset_id)\
            .all()

        enriched=[]

        for symbol,price,volume in data:
            score=score_map.get(symbol,0)
            state=state_map.get(symbol,0)

            if score>1.5:
                strength="STRONG"
            elif score>0.5:
                strength="MEDIUM"
            elif score>-0.5:
                strength="WEAK"
            else:
                strength="NEGATIVE"

            enriched.append((symbol,price,volume,score,state,strength))

        enriched.sort(key=lambda x:x[3],reverse=True)

        for symbol,price,volume,score,state,strength in enriched:

            if state==1:
                state_label="BULL"
            elif state==-1:
                state_label="BEAR"
            else:
                state_label="NEUTRAL"

            self.add_row(
                symbol,
                f"{price:.4f}",
                f"{volume:.2f}",
                f"{score:.3f}",
                state_label,
                strength
            )

        session.close()

class TopSignalsPanel(DataTable):
    def on_mount(self):
        self.add_columns("Symbol","Score","State")

    def update_data(self):
        session=Session()
        self.clear()

        signals=session.query(Asset.symbol,LiveSignal.signal_type,LiveSignal.value)\
            .join(LiveSignal,Asset.id==LiveSignal.asset_id)\
            .all()

        score_map={}
        state_map={}

        for symbol,stype,value in signals:
            if stype=="score":
                score_map[symbol]=value
            elif stype=="state":
                state_map[symbol]=value

        ranked=[]

        for symbol,score in score_map.items():
            ranked.append((symbol,score,state_map.get(symbol,0)))

        ranked.sort(key=lambda x:x[1],reverse=True)

        for symbol,score,state in ranked[:5]:

            if state==1:
                st="BULL"
            elif state==-1:
                st="BEAR"
            else:
                st="NEUTRAL"

            self.add_row(symbol,f"{score:.3f}",st)

        session.close()

class LogPanel(Static):
    logs=reactive("system online\n")

    def add_log(self,msg:str):
        self.logs+=msg+"\n"
        self.update(self.logs)

class Dashboard(App):

    CSS="""
    Screen{layout:vertical}
    #main{layout:grid;grid-size:2 2;height:80%}
    #logs{height:20%;border:solid green}
    DataTable{border:solid #333}
    """

    def compose(self)->ComposeResult:
        yield Header()

        with Container(id="main"):
            self.market=MarketTable()
            self.top=TopSignalsPanel()
            yield self.market
            yield self.top

        self.logs=LogPanel(id="logs")
        yield self.logs
        yield Footer()

    def on_mount(self):
        self.set_interval(30,self.refresh_data)

    def refresh_data(self):
        self.market.update_data()
        self.top.update_data()
        self.logs.add_log("cycle")

if __name__=="__main__":
    Dashboard().run()