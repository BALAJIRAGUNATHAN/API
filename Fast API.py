import datetime as dt
from typing import List, Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()
trades_db = {}
class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")
    price: float = Field(description="The price of the Trade.")
    quantity: int = Field(description="The amount of units traded.")

class Trade(BaseModel):
    asset_class: Optional[str] = Field(alias="assetClass", default=None, description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")
    counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with. May not always be available")
    instrument_id: str = Field(alias="instrumentId", description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")
    instrument_name: str = Field(alias="instrumentName", description="The name of the instrument traded.")
    trade_date_time: dt.datetime = Field(alias="tradeDateTime", description="The date-time the Trade was executed")
    trade_details: TradeDetails = Field(alias="tradeDetails", description="The details of the trade, i.e. price, quantity")
    trade_id: str = Field(alias="tradeId", default=None, description="The unique ID of the trade")
    trader: str = Field(description="The name of the Trader")

@app.get("/trades", response_model=List[Trade])
async def get_trades(
    assetClass: Optional[str] = Query(None, description="Asset class of the trade."),
    start: Optional[dt.datetime] = Query(None, description="The minimum date for the tradeDateTime field."),
    end: Optional[dt.datetime] = Query(None, description="The maximum date for the tradeDateTime field."),
    minPrice: Optional[float] = Query(None, description="The minimum value for the tradeDetails.price field."),
    maxPrice: Optional[float] = Query(None, description="The maximum value for the tradeDetails.price field."),
    tradeType: Optional[str] = Query(None, description="The tradeDetails.buySellIndicator is a BUY or SELL"),
):
    filtered_trades = []
    for trade in trades_db.values():
        if (
            (assetClass is None or trade.asset_class == assetClass) and
            (start is None or trade.trade_date_time >= start) and
            (end is None or trade.trade_date_time <= end) and
            (minPrice is None or trade.trade_details.price >= minPrice) and
            (maxPrice is None or trade.trade_details.price <= maxPrice) and
            (tradeType is None or trade.trade_details.buySellIndicator == tradeType)
        ):
            filtered_trades.append(trade)
    return filtered_trades


@app.get("/trades/{trade_id}", response_model=Trade)
async def get_trade_by_id(trade_id: str):
    if trade_id in trades_db:
        return trades_db[trade_id]
    else:
        return {"error": "Trade not found"}


@app.get("/trades/search", response_model=List[Trade])
async def search_trades(search: str):
    search_results = []
    for trade in trades_db.values():
        if (
            search.lower() in trade.counterparty.lower() or
            search.lower() in trade.instrument_id.lower() or
            search.lower() in trade.instrument_name.lower() or
            search.lower() in trade.trader.lower()
        ):
            search_results.append(trade)
    return search_results


@app.post("/trades", response_model=Trade)
async def create_trade(trade: Trade):
    trade.trade_id = str(len(trades_db) + 1)
    trades_db[trade.trade_id] = trade
    return trade
