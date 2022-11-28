import re
from string import Template


# This query will be used if one of source/destination is a port
port_query = lambda port_code: f"""
select code from ports where ports.code = '{port_code}'
"""


# This query will be used if one of source/destination is a region, to fetch all the port codes recursively
region_query = lambda region_code: f"""
with RECURSIVE children AS (
    select slug, name, parent_slug from regions where slug  = '{region_code}'
    union
    select r.slug, r.name, r.parent_slug 
    from regions r inner join children as c 
    on r.parent_slug = c.slug 
)
select p.code from children c
join ports p on p.parent_slug = c.slug
"""


class RateQuery:
    """
        This class provides an abstraction over the rates query that will be used to fetch the prices,
        providing methods to manipulate the query according to filters, ordering and pagination.

        It has two properties, 
          - query: Outputs the final query to fetch the results.
          - counter_query: Outputs the query to find the total_count.

        Example Usage:        
        ```
            rate_query = RateQuery().add_source_destination_filter(
                source="CNGGZ", destination="northern_europe"
            ).add_dates_filter(
                date_from="2016-01-1"
            ).add_pagination_params(
                1, 20
            ).add_ordering(
                'dd'
            )
        ```
        
        Example Query:
        ```
            with base as (                
                select day, (
                    case 
                        when count(*) < 3 then null else round(avg(price))
                    end
                ) as avg_price from prices
                WHERE orig_code in (
                    with RECURSIVE children AS (
                        select slug, name, parent_slug from regions where slug  = 'china_main'
                        union
                        select r.slug, r.name, r.parent_slug 
                        from regions r inner join children as c 
                        on r.parent_slug = c.slug 
                    )
                    select p.code from children c
                    join ports p on p.parent_slug = c.slug
                
                )
                and dest_code in (
                    with RECURSIVE children AS (
                        select slug, name, parent_slug from regions where slug  = 'northern_europe'
                        union
                        select r.slug, r.name, r.parent_slug 
                        from regions r inner join children as c 
                        on r.parent_slug = c.slug 
                    )
                    select p.code from children c
                    join ports p on p.parent_slug = c.slug
                
                )
                group by day
            ),
            min_max_dates as (
                select max(day) as max_date, min(day) as min_date from base
            ),
            date_range as (
                SELECT date_trunc('day', dd):: date as dd
                FROM generate_series((select min_date from min_max_dates)::timestamp , (select max_date from min_max_dates)::timestamp, '1 day'::interval) dd
            )
            select dd, avg_price from base right join date_range on base.day = date_range.dd;
        ```
    """

    code_pattern = r'[A-Z]{5}'
    region_slug_pattern = r'[a-z_]+'

    @classmethod
    def is_port(cls, port_or_region: str):
        return re.match(cls.code_pattern, port_or_region)

    @classmethod
    def is_region(cls, port_or_region: str):
        return re.match(cls.region_slug_pattern, port_or_region)

    def __init__(self) -> None:
        # Base query template, will be subsituted by filtering clause. 
        self._base_query_template = Template(
            f"""
                with base as (                
                    select day, (
                        case 
                            when count(*) < 3 then null else round(avg(price))
                        end
                    ) as avg_price from prices
                    $filter_clause
                    group by day
                ),
                min_max_dates as (
                    select max(day) as max_date, min(day) as min_date from base
                ),
                date_range as (
                    SELECT date_trunc('day', dd):: date as dd
                    FROM generate_series((select min_date from min_max_dates)::timestamp , (select max_date from min_max_dates)::timestamp, '1 day'::interval) dd
                )                              
            """
        )

        # Result query template, will be subsituted by ordering and pagination clauses.
        self._result_query_template = Template("""                
                select dd, avg_price from base right join date_range on base.day = date_range.dd $ordering_clause $pagination_clause;
            """
        )

        # Counter query template, will be subsituted by ordering and pagination clauses.
        self._count_query = "select count(*) from base right join date_range on base.day = date_range.dd";

        # Cached property for result query
        self._query = ''
        
        # Private properties will store filtering, ordering clauses that will be applied later.
        self._filters = []
        self._ordering = []
        self._page = None
        self._page_size = None

    def _finalize(self):
        """
        Method to finalize the result query.
        """
        self._query = self._base_query_template.substitute(
            filter_clause=self.apply_filters(), 
        )
        self._query = self._query + self._result_query_template.substitute(
            ordering_clause=self.apply_ordering(),
            pagination_clause=self.apply_pagination()
        )

        return self

    def apply_filters(self):
        filter_clause=''
        filters = filter(lambda f: f, self._filters)
        if filters:
            filter_clause = 'WHERE  ' + '\nand\n'.join(filters)
        
        return filter_clause

    def apply_ordering(self):
        ordering_clause = ''
        if self._ordering:
            ordering_clause = ' '.join([
                'ORDER BY', 
                ', '.join(
                    [' '.join([order_column, order]) for order_column, order in self._ordering]
                )
            ])
        
        return ordering_clause

    def apply_pagination(self):
        pagination_clause = ''
        if self._page or self._page_size:
            self._page = self._page or 1
            self._page_size = self._page_size or 10
            pagination_clause = f'LIMIT {self._page_size} OFFSET {(self._page - 1) * self._page_size}'
        return pagination_clause

    def add_ordering(self, ordering: str, order: str='ASC'):
        self._ordering.append((ordering, order))
        return self

    def add_source_destination_filter(self, source: str, destination: str):
        source_query = port_query(source) if self.is_port(source) else region_query(source)
        destination_query = port_query(destination) if self.is_port(destination) else region_query(destination)
        
        self._filters.append(f"orig_code in ( {source_query})")

        self._filters.append(f"""dest_code in (
                {destination_query}
            )"""
        )
        return self

    def add_dates_filter(self, date_from: str=None, date_to: str=None):
        query_components = []
        if date_from:
            query_components.append(f"day >= '{date_from}'")
        if date_to:
            query_components.append(f"day <= '{date_to}'")

        self._filters.append(" and ".join(query_components))
        return self

    def add_pagination_params(self, page: int = 1, page_size: int = 10):
        if page:
            self._page = page
        if page_size:
            self._page_size = page_size
        return self     


    @property
    def query(self):
        self._finalize()        
        return self._query

    @property
    def counter_query(self):
        return self._base_query_template.substitute(
            filter_clause=self.apply_filters(), 
        ) + self._count_query