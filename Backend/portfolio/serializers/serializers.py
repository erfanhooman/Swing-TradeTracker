from rest_framework import serializers

from ..models import BalanceHistory


class ProfitLossSummarySerializer(serializers.Serializer):
    realized_profit_loss = serializers.DecimalField(max_digits=18, decimal_places=8)
    realized_profit_loss_percentage = serializers.DecimalField(max_digits=18, decimal_places=8)
    unrealized_profit_loss = serializers.DecimalField(max_digits=18, decimal_places=8)
    unrealized_profit_loss_percentage = serializers.DecimalField(max_digits=18, decimal_places=8)
    total_profit_loss = serializers.DecimalField(max_digits=18, decimal_places=8)
    total_profit_loss_percentage = serializers.DecimalField(max_digits=18, decimal_places=8)


class BalanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceHistory
        fields = ['usdt_balance', 'coin_balance', 'total_balance', 'timestamp']
