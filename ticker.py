class Spot:
    def __init__(self, price: float, volume: int):
        self.price = price
        self.volume = volume


class Ticker:
    def __init__(self, symbol: str, name: str, sector: str):
        self.sector = sector
        self.name = name
        self.symbol = symbol
        self.spots = {}

    def add_spot(self, date: str, spot: Spot):
        self.spots[date] = spot
