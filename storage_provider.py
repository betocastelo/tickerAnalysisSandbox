import os
import sqlite3 as sql

from ticker import Ticker, Spot


class StorageProvider:
    def __init__(self, database: str = None):
        if database is None:
            self._db_file = 'data/storage.sqlite'
        else:
            self._db_file = database

        self._symbols = set()
        self._load_db()
        self._index_value_is_dirty = True

    def _load_db(self):
        if not os.path.isfile(self._db_file):
            self._create_database()

        self._load_symbols()

    def _create_database(self):
        self._create_symbols_table()
        self._create_tickers_table()
        self._create_index_value_table()

    def _create_symbols_table(self):
        connection = sql.Connection(self._db_file)
        cursor = connection.cursor()
        cursor.execute(
            'create table symbols (id integer not null constraint symbols_pk primary key autoincrement, '
            'symbol text not null, name text, sector text)'
        )
        cursor.execute('create unique index symbols_symbol_uindex on symbols (symbol)')
        connection.commit()
        connection.close()

    def _create_tickers_table(self):
        connection = sql.Connection(self._db_file)
        cursor = connection.cursor()
        cursor.execute(
            'create table tickers (date date not null, symbol_id integer not null references symbols, '
            'price numeric not null, volume integer);'
        )
        cursor.execute('create index tickers_date_index on tickers (date)')
        connection.commit()
        connection.close()

    def _create_index_value_table(self):
        connection = sql.Connection(self._db_file)
        cursor = connection.cursor()
        cursor.execute('create table index_value(date date not null, price numeric not null)')
        cursor.execute('create unique index index_value_date_uindex on index_value (date)')
        connection.commit()
        connection.close()

    def _load_symbols(self):
        connection = sql.Connection(self._db_file)
        cursor = connection.cursor()

        for symbol in cursor.execute('select symbol from symbols'):
            self._symbols.add(symbol[0])

        connection.close()

    def insert_ticker(self, ticker: Ticker):
        connection = sql.Connection(self._db_file)
        cursor = connection.cursor()
        symbol_id = self._get_symbol_id(cursor, ticker)

        spots_list = []
        for date, spot in ticker.spots.items():
            spots_list.append((date, symbol_id, spot.price, spot.volume))

        cursor.executemany('insert into tickers values (?, ?, ?, ?)', spots_list)
        connection.commit()
        connection.close()
        self._index_value_is_dirty = True

    def _get_symbol_id(self, cursor: sql.Cursor, ticker: Ticker):
        if ticker.symbol not in self._symbols:
            cursor.execute('insert into symbols (symbol, name, sector) values (?, ?, ?)',
                           (ticker.symbol, ticker.name, ticker.sector))
            self._symbols.add(ticker.symbol)

        return cursor.execute('select id from symbols where symbol = ?', [ticker.symbol]).fetchone()[0]

    def insert_spot(self, date: str, ticker: Ticker, spot: Spot):
        connection = sql.Connection(self._db_file)
        cursor = connection.cursor()
        symbol_id = self._get_symbol_id(cursor, ticker)
        cursor.execute('insert into tickers values(date(?), ?, ?, ?)', (date, symbol_id, spot.price, spot.volume))
        connection.commit()
        connection.close()
        self._index_value_is_dirty = True

    def get_last_index_value_at_date(self, date: str):
        if self._index_value_is_dirty:
            self._repopulate_index_value()

        connection = sql.Connection(self._db_file)
        cursor = connection.cursor()
        value = cursor.execute('select price from index_value where date <= date(?) order by date desc',
                               [date]).fetchone()[0]
        connection.close()
        return value

    def _repopulate_index_value(self):
        connection = sql.Connection(self._db_file)
        cursor = connection.cursor()
        cursor.execute('delete from index_value')
        cursor.execute('insert into index_value select date, avg(price) from tickers group by date')
        connection.commit()
        connection.close()
        self._index_value_is_dirty = False

    def get_all_symbols(self):
        connection = sql.Connection(self._db_file)
        cursor = connection.cursor()
        symbols = cursor.execute('select symbol from main.symbols order by symbol asc').fetchall()
        return [symbol[0] for symbol in symbols]

    def get_ticker_history(self, symbol: str):
        connection = sql.Connection(self._db_file)
        cursor = connection.cursor()
        history = cursor.execute('select date, price from symbols s, tickers t '
                                 'where s.id = t.symbol_id and s.symbol = ? order by date',
                                 [symbol]).fetchall()
        connection.close()
        return history

    def get_sector_value_data(self):
        connection = sql.Connection(self._db_file)
        cursor = connection.cursor()
        sector_data = cursor.execute(
            'select sector, date, avg(price) from tickers t, symbols s '
            'where t.symbol_id = s.id group by sector, date order by sector'
        ).fetchall()
        connection.close()
        return sector_data

    def get_relative_sector_distribution(self, date: str):
        connection = sql.Connection(self._db_file)
        cursor = connection.cursor()
        closest_earlier_date_inclusive = cursor.execute('select date from tickers '
                                                        'where date <= date(?) order by date desc',
                                                        [date]).fetchone()[0]

        if closest_earlier_date_inclusive is None:
            return None

        sector_counts = cursor.execute('select sector, count(symbol) from tickers t, symbols s '
                                       'where t.symbol_id = s.id and date = ? group by sector',
                                       [closest_earlier_date_inclusive]).fetchall()

        total_count = sum(sector[1] for sector in sector_counts)
        sector_distributions = {}
        for sector, count in sector_counts:
            sector_distributions[sector] = count/total_count

        return sector_distributions
