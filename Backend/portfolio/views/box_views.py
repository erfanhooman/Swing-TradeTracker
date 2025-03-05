import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from Backend.messages import response_message as mt
from Backend.messages import serializer_response_message as mst
from Backend.utils import create_response
from ..models import Box, Transaction, Coin
from ..serializers.box_serializer import BoxSerializer
from ..serializers.transaction_serializers import TransactionDataSerializer
from ..utils import fetch_multiple_prices

logger = logging.getLogger("backend")

class BoxListAPIView(APIView):
    """Fetch all boxes (open/closed) for the authenticated user."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List Boxes",
        operation_description="Retrieve a list of boxes for the authenticated user.  Can filter by closed status.",
        manual_parameters=[
            openapi.Parameter('closed', in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
                              description='Filter by closed status (true/false)')
        ],
        responses={200: BoxSerializer(many=True)},
        tags=["📦 Boxes"]
    )
    def get(self, request):
        closed = request.query_params.get("closed", "false").lower() == "true"
        boxes = Box.objects.filter(user=request.user, is_closed=closed).order_by("-total_buy_value")

        coin_symbols = list(set(box.coin.symbol for box in boxes))

        price_data = fetch_multiple_prices(coin_symbols)

        serializer = BoxSerializer(boxes, many=True, context={'price_data': price_data})

        return create_response(success=True, message=mt[203],
                               data=serializer.data, status=status.HTTP_200_OK)


class BoxDetailAPIView(APIView):
    """Get transactions of a box for the authenticated user."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Box Transactions",
        operation_description="Retrieve transactions for a specific box, identified by ID or coin name.",
        responses={200: TransactionDataSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('coin_symbol', in_=openapi.IN_PATH, type=openapi.TYPE_STRING,
                              description='Coin name of the box'),
        ],
        tags=["📦 Boxes"]
    )
    def get(self, request, box_id):
        try:
            box = Box.objects.get(user=request.user ,id=box_id)
        except (Coin.DoesNotExist, Box.DoesNotExist):
            logger.warning(f"try to get the box that not exist {request.user}")
            return create_response(success=False, message=mst[12],
                                   data={"box_id": box_id}, status=status.HTTP_400_BAD_REQUEST)

        transactions = Transaction.objects.filter(user=request.user, box=box)
        serializer = TransactionDataSerializer(transactions, many=True)

        return create_response(success=True, message=mt[203],
                               data=serializer.data, status=status.HTTP_200_OK)


class CloseBoxAPIView(APIView):
    """Manually close a box for the authenticated user."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Close Box",
        operation_description="Manually close a box.",
        responses={200: openapi.Response("Box closed successfully")},
        tags=["📦 Boxes"]
    )
    def patch(self, request, box_id):
        try:
            box = Box.objects.get(user=request.user, id=box_id)
        except Box.DoesNotExist:
            logger.warning(f"try to close that not available {request.user}")
            return create_response(success=False, message=mst[10],
                                   data={"box_id": box_id}, status=status.HTTP_400_BAD_REQUEST)

        if box.total_amount == 0:
            box.is_closed = True
            box.save()

            return create_response(success=True, message=mt[206],
                                   data={"box": box.coin.name}, status=status.HTTP_200_OK)

        return create_response(success=False, message=mst[11],
                               data={"amount": box.total_amount}, status=status.HTTP_400_BAD_REQUEST)
