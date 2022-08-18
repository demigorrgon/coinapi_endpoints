import os
from json.decoder import JSONDecodeError

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, ORJSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

load_dotenv()
# r = httpx.get('')
BASE_URL_COINAPI_PROD = "https://rest.coinapi.io"
BASE_URL_COINAPI_SANDBOX = "https://rest-sandbox.coinapi.io"


def httpx_client() -> httpx.Client:
    headers = {
        "Accept": "application/json",
        "X-CoinAPI-Key": os.environ.get("COINAPI_FREE_KEY"),
    }
    client = httpx.Client(headers=headers)
    return client


app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=RedirectResponse)
async def main():
    return "/docs"


@app.get(
    "/list-all-exchanges",
)
async def list_all_exchanges(request: Request):
    """Get a detailed list of exchanges provided by the CoinAPI."""
    URL = "/v1/exchanges"
    client = httpx_client()
    with client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)
    result = response.json()
    # return templates.TemplateResponse(
    #     "pretty_json.html",
    #     {
    #         "request": request,
    #         "json": json.dumps(result, indent=4),
    #         "message": "Get a detailed list of exchanges provided by the CoinAPI.",
    #     },
    # )
    return JSONResponse(result)


@app.get("/list-all-test-assets")
async def list_all_sandbox_assets(request: Request):
    """Get detailed list of assets available in CoinAPI testing environment (sandbox)."""
    URL = "/v1/assets"
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_SANDBOX + URL)
        print(response)
    return ORJSONResponse(response.json())


@app.get("/prod-asset/{asset_id}")
async def get_prod_asset(asset_id: str):
    """Returns production info about single asset, accepts asset_id from /list-all-test-assets, production's assets data is too big and is freezing fastapi documentation as a result.\nExample: asset_id: BTC or btc"""
    URL = f"/v1/assets/{asset_id.lower().upper()}"
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)
        print(response)
    return ORJSONResponse(response.json())


@app.get("/binance-list-symbols")
async def list_all_symbols():
    """List of all symbols available on selected exchange, in this example - Binance. Limit 100 entries"""
    URL = "/v1/symbols/BINANCE"
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)
    big_response = response.json()[:100]

    return JSONResponse(big_response)


@app.get("/{exchange}/list-symbols")
async def list_symbols_by_exchange(exchange: str):
    """List of all symbols available on provided exchange. Param: exchange: exchange_id from /list-all-exchanges. Limit 100 entries."""
    URL = f"/v1/symbols/{exchange.lower().upper()}"
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)
        print(response)
    if len(response.json()) == 0:
        raise HTTPException(404)
    return JSONResponse(response.json()[:100])


@app.get("/get-all-current-btc-rates")
async def get_all_current_rates():
    """Get the current exchange rate between requested asset and all other assets. BTC as example, CoinAPI does not require exchange_id in this case"""
    URL = "/v1/exchangerate/BTC"
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)

    return JSONResponse(response.json())


@app.get("/coinapi-available-time-periods")
async def timeperiods():
    """Get full list of supported time periods available for requesting exchange rates historical timeseries data."""
    URL = "/v1/exchangerate/history/periods"
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)

    return JSONResponse(response.json())


@app.get("/asset-exchange-history")
async def assets_history():
    """BTC/USD exchange history example for 1 second ticks between 17-08-2022 00:00 and 17-08-2022 00:01 (for a minute).\nDev:Minutes are not inclusive"""
    URL = "/v1/exchangerate/BTC/USD/history?period_id=1SEC&time_start=2022-08-17T00:00:00&time_end=2022-08-17T00:02:00"
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)

    return JSONResponse(response.json())


@app.get("/ohlcv-periods")
async def list_ohlcv_periods():
    """Full list of supported time periods available for requesting OHLCV timeseries data"""
    URL = "/v1/ohlcv/periods"

    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)

    return JSONResponse(response.json())


@app.get("/ohlcv-latest-data")
async def ohlcv_latest_data():
    """OHLCV latest timeseries data returned in time descending order. Data can be requested by the period and for the specific symbol eg BINANCE_SPOT_BTC_BUSD. Example: BTC/BUSD pair on Binance, with period of 1 min, limit 100 entries by default, extendable up to 10000, may optionally turn on/off return of the empty data"""
    URL = "/v1/ohlcv/BINANCE_SPOT_BTC_BUSD/latest?period_id=1MIN&limit=100&include_empty_items=true"

    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)

    # return templates.TemplateResponse(
    #     "pretty_json.html",
    #     {
    #         "request": request,
    #         "json": json.dumps(response.json(), indent=4),
    #         "message": "OHLCV latest timeseries data returned in time descending order. Data can be requested by the period and for the specific symbol eg BITSTAMP_SPOT_BTC_USD. Example: BTC/BUSD pair on BinanceUAT, with period of 1 min, limit 100 entries by default, extendable up to 10000",
    #     },
    # )
    return JSONResponse(response.json())


@app.get("/ohlcv-historical-data")
async def ohlcv_historical_data():
    """Example of historical OHLCV data in time period for BTC/BUSD pair on Binance, with period of 1 hour, in between 17-08-2022 and 18-08-2022, limit 100 entries by default, extendable up to 10000"""
    URL = "/v1/ohlcv/BINANCE_SPOT_BTC_BUSD/history?period_id=1HRS&time_start=2022-08-17T00:00:00&time_end=2022-08-18T00:00:00&limit=100&include_empty_items=true"

    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)

    return JSONResponse(response.json())


@app.get("/latest-btc-trades")
async def latest_trades():
    """Get latest trades executed up to 1 minute ago. Latest data is always returned in time descending order. Example: Latest BTC/BUSD trades on Binance, CoinAPI requires exchange(symbol) name and traded pair"""
    URL = "/v1/trades/latest?limit=100&filter_symbol_id=BINANCE_SPOT_BTC_BUSD"

    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)

    return JSONResponse(response.json())


@app.get("/btc-trades-history")
async def trades_history():
    """Get history transactions from specific symbol, returned in time ascending order. Example: Binance BTC/BUSD pair from 16-08-2022 00:00 to 17-08-2022 00:05 with limit of 100 entries.\nNote: Trades history does not seem to return data of current day/day before that. Example: date interval: 17-08-2022 (yesterday) 18-08-2022 (day of writing) returns empty array. Needs further investigation."""
    URL = "/v1/trades/BINANCE_SPOT_BTC_BUSD/history?time_start=2022-08-16T00:00:00&time_end=2022-08-17T00:05:00&limit=100"

    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)
        print(response)

    return JSONResponse(response.json())


@app.get("/list-btc-quotes")
async def list_btc_quotes():
    """Current quotes for BTC/BUSD on binance as example."""
    URL = "/v1/quotes/BINANCE_SPOT_BTC_BUSD/current"
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)
        print(response)

    return JSONResponse(response.json())


# very damn slow
# @app.get("/list-all-quotes")
# async def list_all_quotes():
#     """Get current quotes for all symbols. WARNING: Docs are very slow at processing, might take some time/freeze the page"""
#     URL = "/v1/quotes/current"
#     with httpx_client() as client:
#         response = client.get(BASE_URL_COINAPI_PROD + URL)
#         print(response)

#     return JSONResponse(response.json())


@app.get("/get-latest-quotes")
async def get_latest_quotes():
    """Get latest updates of the quotes up to 1 minute ago. Latest data is always returned in time descending order."""
    URL = "/v1/quotes/latest?limit=100"
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)
        print(response)

    return JSONResponse(response.json())


@app.get("/historical-quote")
async def get_historical_quote():
    """Get historical quote updates within requested time range, returned in time ascending order. Example: Binance BTC/USDT Pair, starting from 01-08-2022 with limit of 100"""

    URL = "/v1/quotes/BINANCE_SPOT_BTC_BUSD/history?time_start=2022-08-01T00:00:00&limit=100"

    try:
        with httpx_client() as client:
            response = client.get(BASE_URL_COINAPI_PROD + URL, timeout=None)
            print(response)

        return JSONResponse(response.json())
    except JSONDecodeError:
        raise HTTPException(408, "CoinAPI failed to respond in time")


@app.get("/btc-current-order-book")
async def get_current_order_book_snapshot():
    """Get current order book snapshot for BTC/USDT on Binance, with limit of 100 levels from each side of the book to include in response"""
    URL = "/v1/orderbooks/BINANCE_SPOT_BTC_USDT/current?limit_levels=100"
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)
        print(response)

    return JSONResponse(response.json())


# You exceeded Concurrency limit (number of maximum allowed concurrent requests per APIKey) for your subscription.
# @app.get("/list-order-books")
# async def list_order_books():
#     URL = "/v1/orderbooks/current?limit_levels=10"
#     with httpx_client() as client:
#         response = client.get(BASE_URL_COINAPI_PROD + URL)
#         print(response)

#     return JSONResponse(response.json())


@app.get("/btc-latest-order-book")
async def get_latest_order_book():
    """Get latest order book snapshots for BTC/USDT pair on Binance, returned in time descending order, with 100 limit levels"""
    URL = "/v1/orderbooks/BINANCE_SPOT_BTC_USDT/current?limit_levels=100"
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)
        print(response)

    return JSONResponse(response.json())


# returns empty list idk
@app.get("/btc-historical-order-book")
async def get_historical_order_book_data():
    """Get historical order book snapshots for a specific symbol within time range, returned in time ascending order. Example: BTC/USDT pair on Binance starting from 16-08-2022, levels limit = 5, limit 100 entries. Note: doesn't seem to return data for current day and day before that, ie date interval: 17-08-2022 (yesterday) 18-08-2022 (day of writing) returns empty array. Needs further investigation."""
    URL = "/v1/orderbooks/BINANCE_SPOT_BTC_USDT/history?time_start=2022-08-16T00:00:00&limit=100&limit_levels=5"
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL, timeout=None)
        print(response.headers)
    return JSONResponse(response.json())


@app.get("/btc-current-order-book-l3")
async def current_order_book_l3():
    """Get current order book snapshot with passive level 3 data for BTC/USDT pair on Binance, with 50 limit levels"""
    URL = (
        "/v1/orderbooks/current?filter_symbol_id=BINANCE_SPOT_BTC_USDT&limit_levels=50"
    )
    with httpx_client() as client:
        response = client.get(BASE_URL_COINAPI_PROD + URL)
        print(response)

    return JSONResponse(response.json())
