from data_provider import DataProvider
from storage_provider import StorageProvider


def load_data(db_file: str = None):
    data = DataProvider('data/constituents_history.pkl')
    db = StorageProvider(db_file)

    for symbol in data.get_symbols():
        ticker = data.get_ticker(symbol)
        db.insert_ticker(ticker)

    return db


if __name__ == '__main__':
    database = load_data()
    index_value = database.get_last_index_value_at_date('2018-01-31')
    sector_value_data = database.get_sector_value_data()
    sector_distribution = database.get_relative_sector_distribution('2018-12-31')
