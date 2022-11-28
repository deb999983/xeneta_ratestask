class ErrorReason:
    ENDPOINT_NOT_FOUND = 10
    INVALID_DATE_FORMAT = 20
    INVALID_DATES = 30
    ENPOINTS_REQUIRED = 30
    INVALID_PAGE = 40
    INVALID_PAGE_SIZE = 50


error_messages = {
    ErrorReason.ENDPOINT_NOT_FOUND: "Endpoint {endpoint} doesn't exist.",
    ErrorReason.INVALID_DATE_FORMAT: "Incorrect data format, should be YYYY-MM-DD",
    ErrorReason.ENPOINTS_REQUIRED: "Both orgin and destination are required to fetch rates",
    ErrorReason.INVALID_DATES: "Invalid dates: `date_from` should be less than `date_to`",
    ErrorReason.INVALID_PAGE: "Invalid page {page}",
    ErrorReason.INVALID_PAGE_SIZE: "Invalid page size {page_size}"
}


def get_message(message, *args, **kwargs):
    return message.format(*args, **kwargs)