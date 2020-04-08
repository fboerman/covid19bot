from django.conf import settings
from sqlalchemy.exc import ProgrammingError
from tabulate import tabulate
from sqlalchemy import inspect
from sqlalchemy.sql.sqltypes import BIGINT

def _query_cities(cities):
    db = settings.DASHBOARD_DATA_ENGINE
    sql = "select \"" + '","'.join(cities) + "\" from netherlands_cities ORDER BY time DESC LIMIT 2"
    with db.connect() as con:
        try:
            row = con.execute(sql)
        except ProgrammingError:
            return None
    data = list(row)
    diff = [a - b for a, b in zip(data[0], data[1])]
    data_per_city = list(zip(cities, data[0], diff))
    data_per_city.sort(key=lambda x: x[1], reverse=True)

    return data_per_city

def get_latest_rivm_datatable(cities):
    if '' in cities:
        cities.remove('')

    data_per_city = _query_cities(cities)

    return tabulate(data_per_city, headers=['Stad', 'Gevallen', '+/-'])

def validcities():
    db = settings.DASHBOARD_DATA_ENGINE
    inspector = inspect(db)
    columns = inspector.get_columns('netherlands_cities')
    cities = [c['name'] for c in columns if type(c['type']) == BIGINT]
    if 'index' in cities:
        cities.remove('index')
    cities.sort()

    return cities

def get_top20_datatable():
    db = settings.DASHBOARD_DATA_ENGINE

    cities = validcities()
    data_per_city = _query_cities(cities)

    return tabulate(data_per_city[:20], headers=['Stad', 'Gevallen', '+/-'])