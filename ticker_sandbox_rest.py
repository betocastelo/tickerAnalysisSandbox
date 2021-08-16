from fastapi import FastAPI

from data_provider import DataProvider
from storage_provider import StorageProvider

app = FastAPI()
pickle = DataProvider('data/constituents_history.pkl')
database = StorageProvider()


@app.post("/load_data")
def load_data():
    """Load the pickle file into the SQLite database file. Note that this operation is not idempotent."""
    for symbol in pickle.get_symbols():
        ticker = pickle.get_ticker(symbol)
        database.insert_ticker(ticker)


@app.get("/symbols")
def get_symbols():
    """Returns all symbols tracked in the source data."""
    symbols = pickle.get_symbols()
    result = {symbol for symbol in symbols}
    return result


@app.get("/symbols/{symbol}")
def get_price_history(symbol: str):
    """Returns all pricing data for the given symbol."""
    history = database.get_ticker_history(symbol)

    results = {}
    for date, price in history:
        results[date] = price

    return results
