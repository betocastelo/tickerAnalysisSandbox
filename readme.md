# Ticker Data Sandbox

Very basic processing and analysis of a pkl file containing roughly monthly price data of a set of indices.

## Main Components

### `class DataProvider`

Opens the pkl file and extracts most of the data.

* `get_ticker(symbol: str)`: If the symbol is present in the given pkl file, returns a Ticker object which contains all
  data relative to the requested symbol.
* `get_symbols()`: returns a list of all ticker symbols available in the dataset.

### `class StorageProvider`

Interacts with a Sqlite db file, creating it if necessary, stores ticker data, and provides some analysis capability.

* `insert_ticker(ticker: Ticker)`: Ingests a Ticker object into the database.
* `insert_spot(date: str, ticker: Ticker, spot: Spot)`: Adds a new spot value for a given ticker.
* `get_last_index_value_at_date(date: str)`: Gets the index value (the weighted value of all assets tracked in
  the database) at a given date (or at the nearest earlier date with data available, if the given date cannot be found).
* `get_sector_value_data()`: returns a list of tuples in the format `(sector, date, average price for the sector)`
* `get_relative_sector_distribution(date: str)`: returns a dictionary in the format `{sector: relative weight}`, for a
  given date (or nearest earlier date). Relative weight is the number of assets in that sector divided by the total
  number of assets in the index.