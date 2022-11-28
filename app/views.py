from datetime import datetime
import logging
from app import service
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from drf_spectacular.utils import extend_schema, OpenApiParameter


logger = logging.getLogger(__name__)


class RateSerializer(serializers.Serializer):
    day = serializers.DateField(read_only=True)
    average_price = serializers.FloatField(read_only=True)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='date_from',location=OpenApiParameter.QUERY, description='From date', required=False, type=str
        ),
        OpenApiParameter(
            name='date_to',location=OpenApiParameter.QUERY, description='To date', required=False, type=str
        ),
        OpenApiParameter(
            name='origin',location=OpenApiParameter.QUERY, description='Origin Port/Region', required=True, type=str
        ),
        OpenApiParameter(
            name='destination',location=OpenApiParameter.QUERY, description='Destination Port/Region', required=True, type=str
        ),
        OpenApiParameter(
            name='page',location=OpenApiParameter.QUERY, description='page number', default=1, type=int
        ),
        OpenApiParameter(
            name='page_size', location=OpenApiParameter.QUERY, description='Size of prices to fetch at once', default=10, type=int
        )            
    ],
)
class GetRatesView(APIView):
    serializer_class = RateSerializer

    def validate_parameters(self, request):
        logger.info(f"Got params:: {request.query_params.dict()}")

        params = {}
        # Check endpoints
        params['origin'], params['destination'] = service.validate_endpoints(request)

        # Check dates
        params['date_from'], params['date_to'] = service.validate_dates(request)

        # Add page and page_sizes
        params['page'], params['page_size'] = service.validate_pagination(request)

        return params
        
    def get(self, request, *args, **kwargs):
        try:
            params = self.validate_parameters(request)
            rate_info= service.get_rates(**params)
            serialized = RateSerializer(rate_info["rates"], many=True).data
            return Response(data=serialized, headers={"max_count": rate_info["count"]})
        except Exception as e:
            logger.error(e, exc_info=True)
            raise e
