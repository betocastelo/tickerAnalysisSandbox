import pandas as pd

from ticker import Ticker, Spot


class DataProvider:
    def __init__(self, file_name: str):
        self._data = pd.read_pickle(file_name)
        self._by_ticker = {}
        self._parse_data()

    def _parse_data(self):
        dates = self._data.index
        symbols = set()
        for date in dates:
            date_str = date.date().strftime('%Y-%m-%d')
            if self._has_data(date_str):
                for point in self._data[date.date().strftime('%Y-%m-%d')][0][0]:
                    symbol = point[0]
                    name = point[1]
                    sector = point[2]
                    price = point[4]['raw']
                    volume = point[7]['raw']
                    symbols.add(point[0])

                    if symbol not in self._by_ticker:
                        self._by_ticker[symbol] = Ticker(symbol, name, sector)

                    self._by_ticker.setdefault(symbol, Ticker(symbol, name, sector))\
                        .add_spot(date_str, Spot(price, volume))

    def _has_data(self, date: str):
        return len(self._data[date][0][0]) > 0

    def get_ticker(self, symbol: str):
        if symbol in self._by_ticker:
            return self._by_ticker[symbol]
        else:
            return None

    def get_symbols(self):
        return self._by_ticker.keys()
