from django.conf import settings
from sqlalchemy.exc import ProgrammingError
from tabulate import tabulate

def get_latest_rivm_datatable(cities):
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

    return tabulate(data_per_city, headers=['Stad', 'Gevallen', '+/-'])