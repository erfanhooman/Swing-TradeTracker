from django.conf import settings
from rest_framework import serializers

from ..models import Box



class BoxSerializer(serializers.ModelSerializer):
    coin_icon = serializers.SerializerMethodField()
    coin_name = serializers.SerializerMethodField()
    coin_symbol = serializers.SerializerMethodField()
    current_price = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    profit_loss_value = serializers.SerializerMethodField()
    profit_loss_percentage = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    average_sell_price = serializers.SerializerMethodField()
    total_buy_value = serializers.SerializerMethodField()
    total_sell_value = serializers.SerializerMethodField()

    def get_coin_icon(self, obj):
        return settings.MINIO_ACCESS_ENDPOINT+obj.coin.icon_url or ""

    def get_coin_name(self, obj):
        return obj.coin.name

    def get_coin_symbol(self, obj):
        return obj.coin.symbol

    def get_current_price(self, obj):
        """Retrieve the coin price from context instead of calling API per object."""
        price_data = self.context.get("price_data", {})
        current_price = price_data.get(obj.coin.symbol, 0)
        return f"{current_price:.8f}"

    def get_amount(self, obj):
        return f"{obj.total_amount:.8f}"

    def get_value(self, obj):
        """Calculate the total value using pre-fetched price data."""
        price_data = self.context.get("price_data", {})
        current_price = price_data.get(obj.coin.symbol, 0)
        unsold_value = obj.total_amount * current_price
        total_value = unsold_value + obj.total_sell_value
        return f"{total_value:.8f}"

    def get_profit_loss_value(self, obj):
        """Calculate profit/loss using pre-fetched price data."""

        price_data = self.context.get("price_data", {})
        current_price = price_data.get(obj.coin.symbol, 0)

        if current_price == 0:
            return "N/A"

        box_value = (obj.total_amount * current_price) + obj.total_sell_value
        profit_loss_value = box_value - obj.total_buy_value
        return f"{profit_loss_value:.8f}"

    def get_profit_loss_percentage(self, obj):
        """Calculate profit/loss percentage, ensuring division by zero is avoided."""
        price_data = self.context.get("price_data", {})
        current_price = price_data.get(obj.coin.symbol, 0)

        if current_price == 0 :
            return "N/A"

        box_value = (obj.total_amount * current_price) + obj.total_sell_value
        profit_loss_value = box_value - obj.total_buy_value

        profit_loss_percentage = (profit_loss_value / obj.total_buy_value * 100) if obj.total_buy_value > 0 else 0
        return f"{profit_loss_percentage:.8f}"

    def get_age(self, obj):
        return obj.age if obj.age is not None else 0

    def get_average_sell_price(self, obj):
        return obj.average_sell_price

    def get_total_buy_value(self, obj):
        return obj.total_buy_value

    def get_total_sell_value(self, obj):
        return obj.total_sell_value

    class Meta:
        model = Box
        fields = [
            'id', 'coin_icon', 'coin_name', 'coin_symbol', 'current_price', 'amount', 'value',
            'average_buy_price', 'profit_loss_value', 'profit_loss_percentage', 'is_closed', 'age',
            'average_sell_price', 'total_buy_value', 'total_sell_value'
        ]
