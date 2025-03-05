from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from Backend.messages import response_message as mt
from Backend.utils import create_response
from ..models import Box
from ..utils import fetch_multiple_prices


class ProfitLossSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get Profit/Loss Summary",
        operation_description="Retrieve realized and unrealized profit/loss for both open and closed boxes.",
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "realized_profit_loss": openapi.Schema(type=openapi.TYPE_NUMBER),
                "realized_profit_loss_percentage": openapi.Schema(type=openapi.TYPE_NUMBER),
                "unrealized_profit_loss": openapi.Schema(type=openapi.TYPE_NUMBER),
                "unrealized_profit_loss_percentage": openapi.Schema(type=openapi.TYPE_NUMBER),
                "total_profit_loss": openapi.Schema(type=openapi.TYPE_NUMBER),
                "total_profit_loss_percentage": openapi.Schema(type=openapi.TYPE_NUMBER),
            },
        )},
        tags=["📈 Profit & Loss"]
    )
    def get(self, request):
        """Calculate realized & unrealized profit/loss for user."""
        user = request.user
        closed_boxes = list(Box.objects.filter(user=user, is_closed=True))
        open_boxes = list(Box.objects.filter(user=user, is_closed=False))
        all_boxes = open_boxes + closed_boxes

        if not all_boxes:
            data = {
                "realized_profit_loss": 0,
                "realized_profit_loss_percentage": 0,
                "unrealized_profit_loss": 0,
                "unrealized_profit_loss_percentage": 0,
                "total_profit_loss": 0,
                "total_profit_loss_percentage": 0,
            }
        else:

            price_data = fetch_multiple_prices(list(set(box.coin.symbol for box in open_boxes)))

            realized_profit_loss = sum((box.total_sell_value - box.total_buy_value) for box in closed_boxes)

            def calculate_profit_loss(box):
                """Calculate profit/loss using pre-fetched price data."""
                current_price = price_data.get(box.coin.symbol, 0)
                box_value = (box.total_amount * current_price) + box.total_sell_value
                return box_value - box.total_buy_value

            unrealized_profit_loss = sum(calculate_profit_loss(box) for box in open_boxes)

            total_profit_loss = realized_profit_loss + unrealized_profit_loss

            # Calculate percentages
            def calculate_percentage(profit_loss, boxes):
                total_buy_value = sum(box.total_buy_value for box in boxes)
                return (profit_loss / total_buy_value * 100) if total_buy_value else 0

            realized_profit_loss_percentage = calculate_percentage(realized_profit_loss, closed_boxes)
            unrealized_profit_loss_percentage = calculate_percentage(unrealized_profit_loss, open_boxes)
            total_profit_loss_percentage = calculate_percentage(total_profit_loss, all_boxes)

            data = {
                "realized_profit_loss": realized_profit_loss,
                "realized_profit_loss_percentage": realized_profit_loss_percentage,
                "unrealized_profit_loss": unrealized_profit_loss,
                "unrealized_profit_loss_percentage": unrealized_profit_loss_percentage,
                "total_profit_loss": total_profit_loss,
                "total_profit_loss_percentage": total_profit_loss_percentage,
            }

        return create_response(success=True, message=mt[203],
                               data=data, status=status.HTTP_200_OK)
