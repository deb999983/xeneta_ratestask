import datetime

from django.test import TestCase
from django.db import connection

from app import service as rate_service


class RateQueryTestCase(TestCase):
    
    
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        
        with connection.cursor() as cursor:
            # Create regions table
            cursor.execute("""
                CREATE TABLE regions (
                    slug text NOT NULL,
                    name text NOT NULL,
                    parent_slug text
                );
            """) 

            # Create ports table
            cursor.execute("""
                CREATE TABLE ports (
                    code text NOT NULL,
                    name text NOT NULL,
                    parent_slug text NOT NULL
                );
            """)

            # Create prices table
            cursor.execute("""
                CREATE TABLE prices (
                    orig_code text NOT NULL,
                    dest_code text NOT NULL,
                    day date NOT NULL,
                    price integer NOT NULL
                );
            """)
            
            cursor.execute(
                """
                    INSERT INTO public.regions (slug,"name",parent_slug) VALUES
                    ('china_main','China Main',NULL),
                    ('northern_europe','Northern Europe',NULL),
                    ('scandinavia','Scandinavia','northern_europe'),
                    ('north_europe_sub','North Europe Sub','northern_europe'),
                    ('stockholm_area','Stockholm Area','scandinavia'),
                    ('kattegat','Kattegat','scandinavia'),
                    ('china_east_main','China East Main','china_main'),
                    ('china_south_main','China South Main','china_main');
                """
            )

            cursor.execute(
                """
                INSERT INTO public.ports (code,"name",parent_slug) VALUES
                ('SENRK','Norrköping','stockholm_area'),
                ('SESOE','Södertälje','stockholm_area'),
                ('SEMMA','Malmö','kattegat'),
                ('DKFRC','Fredericia','kattegat'),
                ('NOMAY','Måløy','scandinavia'),
                ('FRANT','Antibes','north_europe_sub'),
                ('CNCWN','Chiwan','china_south_main'),
                ('CNSNZ','Shenzhen','china_south_main'),
                ('CNYAT','Yantai','china_east_main'),
                ('CNNBO','Ningbo','china_east_main');
                """
            )
    
    def test_if_endpoints_are_regions(self):
        """
            Test price info from,
                scandinavia --> china_main,
                stockholm_area --> china_main
        """

        with connection.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO public.prices (orig_code,dest_code,"day",price) VALUES
                    ('SENRK','CNNBO','2016-01-01',1244),
                    ('SENRK','CNYAT','2016-01-01',1044),
                    ('SENRK','CNSNZ','2016-01-01',944),
                    ('SENRK','CNCWN','2016-01-02',1244),
                    ('SENRK','CNCWN','2016-01-02',1044),
                    ('SEMMA','CNYAT','2016-01-02',1224);
                """
            )
        r = rate_service.get_rates('scandinavia', 'china_main')
        self.assertEqual(
            list(r['rates']), [
                {'day': datetime.date(2016, 1, 1), 'average_price': 1077.0}, 
                {'day': datetime.date(2016, 1, 2), 'average_price': 1171.0}
            ]
        )

        r = rate_service.get_rates('stockholm_area', 'china_main')
        self.assertEqual(
            list(r['rates']), [
                {'day': datetime.date(2016, 1, 1), 'average_price': 1077.0}, 
                {'day': datetime.date(2016, 1, 2), 'average_price': None}
            ]
        )        

    def test_if_endpoints_are_ports(self):
        """
            Test price info from,
                SENRK --> CNNBO,
                SENRK --> CNYAT
        """

        with connection.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO public.prices (orig_code,dest_code,"day",price) VALUES
                    ('SENRK','CNNBO','2016-01-01',1244),
                    ('SENRK','CNNBO','2016-01-01',1044),
                    ('SENRK','CNNBO','2016-01-01',944),
                    ('SENRK','CNNBO','2016-01-02',1244),
                    ('SENRK','CNNBO','2016-01-02',1044),
                    ('SENRK','CNNBO','2016-01-02',1044),
                    ('SENRK','CNYAT','2016-01-03',1224);
                """
            )
        r = rate_service.get_rates('SENRK', 'CNNBO')
        self.assertEqual(
            list(r['rates']), [
                {'day': datetime.date(2016, 1, 1), 'average_price': 1077.0}, 
                {'day': datetime.date(2016, 1, 2), 'average_price': 1111.0}
            ]
        )

        r = rate_service.get_rates('SENRK', 'CNYAT')
        self.assertEqual(
            list(r['rates']), [
                {'day': datetime.date(2016, 1, 3), 'average_price': None}
            ]
        )        

    def test_if_one_endpoint_is_region_and_other_is_a_port(self):
        """
            Test price info from,
                scandinavia --> CNNBO,
                stockholm_area --> CNNBO
        """

        with connection.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO public.prices (orig_code,dest_code,"day",price) VALUES
                    ('SENRK','CNNBO','2016-01-01',1244),
                    ('SENRK','CNNBO','2016-01-01',1044),
                    ('SENRK','CNNBO','2016-01-01',944),
                    ('SEMMA','CNNBO','2016-01-02',1244),
                    ('SEMMA','CNNBO','2016-01-02',1044),
                    ('SEMMA','CNNBO','2016-01-02',1044),
                    ('SENRK','CNYAT','2016-01-03',1224);
                """
            )
        r = rate_service.get_rates('scandinavia', 'CNNBO')
        self.assertEqual(
            list(r['rates']), [
                {'day': datetime.date(2016, 1, 1), 'average_price': 1077.0}, 
                {'day': datetime.date(2016, 1, 2), 'average_price': 1111.0}
            ]
        )

        r = rate_service.get_rates('stockholm_area', 'CNNBO')
        self.assertEqual(
            list(r['rates']), [
                {'day': datetime.date(2016, 1, 1), 'average_price': 1077.0}
            ]
        )        
