from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from Backend.messages import serializer_response_message as mst
from ..models import Balance


class BalanceSerializer(serializers.ModelSerializer):
    usdt_balance = serializers.SerializerMethodField()
    coin_balance = serializers.SerializerMethodField()
    total_balance = serializers.SerializerMethodField()

    def format_decimal(self, value):
        """Formats Decimal to a string with fixed 8 decimal places"""
        return f"{value:.8f}"

    def get_usdt_balance(self, obj):
        return self.format_decimal(obj.usdt_balance)

    def get_coin_balance(self, obj):
        return self.format_decimal(obj.get_coin_balance())

    def get_total_balance(self, obj):
        return self.format_decimal(obj.get_total_balance())

    class Meta:
        model = Balance
        fields = ['usdt_balance', 'coin_balance', 'total_balance']


class ModifyBalanceSerializer(serializers.Serializer):
    amount = serializers.CharField()

    def validate_amount(self, amount):

        try:
            float(amount)
            amount = Decimal(amount)
        except (ValueError, TypeError):
            raise serializers.ValidationError(mst[7])

        if amount <= 0:
            raise serializers.ValidationError(mst[8])

        return amount