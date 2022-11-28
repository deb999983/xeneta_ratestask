from django.db import connection
from app.queries import RateQuery


class Repository:
    @staticmethod
    def fetch_all(query: str):        
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result

    @staticmethod
    def fetch_one(query: str):
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            return result[-1]

    @staticmethod
    def exists(query: str):
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            return result


class Port:
    @staticmethod
    def exists(port_code: str):
        return Repository.exists(f"select * from ports where code='{port_code}'")
    


class Region:
    @staticmethod
    def exists(region_code: str):
        return Repository.exists(f"select * from regions where slug='{region_code}'")


class Prices:
    @staticmethod
    def fetch_rates(origin: str, destination: str, date_from:str= None, date_to:str=None, page_size: int = 10, page: int = 1):
        rate_query = RateQuery().add_source_destination_filter(
            source=origin, destination=destination
        ).add_dates_filter(
            date_from=date_from, date_to=date_to
        ).add_pagination_params(
            page, page_size
        ).add_ordering(
            'dd'
        )
        return {
            "rates": Repository.fetch_all(
                rate_query.query
            ),
            "count": Prices.count(
                origin, destination, date_from, date_to
            )
        }

    @staticmethod
    def count(origin: str, destination: str, date_from:str= None, date_to:str=None):
        rate_query = RateQuery().add_source_destination_filter(
            source=origin, destination=destination
        ).add_dates_filter(
            date_from=date_from, date_to=date_to
        )
        return Repository.fetch_one(rate_query.counter_query)
