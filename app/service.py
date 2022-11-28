from datetime import datetime
import logging
from rest_framework.exceptions import ValidationError

from app.repository import Port, Prices, Region
from app.exception import get_message as _, error_messages, ErrorReason


logger = logging.getLogger(__name__)


def validate_date_format(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError as e:
        raise ValidationError(
            {"message": _(error_messages[ErrorReason.INVALID_DATE_FORMAT]), "code": ErrorReason.INVALID_DATE_FORMAT}   
        )


def check_endpoint_exists(endpoint: str):
    exists = Port.exists(endpoint) or Region.exists(endpoint)
    if not exists:
        raise ValidationError(
            {"message": _(error_messages[ErrorReason.ENDPOINT_NOT_FOUND], endpoint=endpoint), "code": ErrorReason.ENDPOINT_NOT_FOUND}
        )
    return endpoint


def validate_endpoints(request):
    origin = request.query_params.get('origin', None)
    destination = request.query_params.get('destination', None)
    if not (origin and destination):
        raise ValidationError(
            {"message": _(error_messages[ErrorReason.ENPOINTS_REQUIRED]), "code": ErrorReason.ENPOINTS_REQUIRED}
        )

    return check_endpoint_exists(origin), check_endpoint_exists(destination)


def validate_dates(request):
    date_from = request.query_params.get('date_from', None)
    date_to = request.query_params.get('date_to', None)
    if 'date_from' in request.query_params:
        date_from = validate_date_format(date_from)
    
    if 'date_to' in request.query_params:
        date_to = validate_date_format(date_to)

    if (date_from and date_to) and date_from > date_to:
        raise ValidationError(
            {"message": _(error_messages[ErrorReason.INVALID_DATES]), "code": ErrorReason.INVALID_DATES}
        )
    
    return date_from, date_to    


def validate_pagination(request):
    page, page_size = None, None
    if 'page' in request.query_params:
        try:
            page = int(request.query_params['page'])
        except ValueError as e:
            raise ValidationError(
                {"message": _(error_messages[ErrorReason.INVALID_PAGE], page=page), "code": ErrorReason.INVALID_PAGE}
            )
    
    if 'page_size' in request.query_params:
        try:
            page_size = int(request.query_params['page_size'])
        except ValueError as e:
            raise {"message": _(error_messages[ErrorReason.INVALID_PAGE_SIZE], page_size=page_size), "code": ErrorReason.INVALID_PAGE_SIZE}
    
    return page, page_size


def get_rates(
    origin: str, destination: str, date_from:str = None, date_to:str = None, page_size: int = 10, page: int = 1
):    
    rate_info = Prices.fetch_rates(origin, destination, date_from, date_to, page_size, page)
    return {
        "rates": map(
            lambda data: {"day": data[0], "average_price": data[1]},
            rate_info["rates"]
        ),
        "count": rate_info["count"]
    }
    


def get_rates_with_dates_filled(
    rigin: str, destination: str, date_from:str = None, date_to:str = None, page_size: int = 10, page: int = 1
):
    pass

