from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from Backend.messages import response_message as mt
from Backend.utils import create_response
from ..models import BalanceHistory


class BalanceHistoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List Balance History",
        operation_description="Retrieve all saved balance history records.",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'usdt_balance': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'coin_balance': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'total_balance': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                    }
                )
            )
        },
        tags=["📊 Balance History"]
    )
    def get(self, request):
        """List all saved balance history records."""
        history = BalanceHistory.objects.filter(user=request.user).order_by('-timestamp')
        data = [
            {
                "usdt_balance": record.usdt_balance,
                "coin_balance": record.coin_balance,
                "total_balance": record.total_balance,
                "timestamp": record.timestamp,
            }
            for record in history
        ]
        return create_response(success=True, message=mt[203],
                               data=data, status=status.HTTP_200_OK)
