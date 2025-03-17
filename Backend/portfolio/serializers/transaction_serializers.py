import logging
from decimal import Decimal

import requests
from datetime import datetime
from django.conf import settings
from rest_framework import serializers

from Backend.messages import response_message as mt
from Backend.messages import serializer_response_message as smt
from ..models import Box, Transaction, Balance, Coin
from ..utils import fetch_multiple_prices

logger = logging.getLogger("backend")

class TransactionSerializer(serializers.Serializer):
    coin_symbol = serializers.CharField(max_length=10, write_only=True)
    type = serializers.ChoiceField(choices=Transaction.TYPE_CHOICES)
    price = serializers.DecimalField(max_digits=18, decimal_places=8)
    amount = serializers.DecimalField(max_digits=18, decimal_places=8)
    fee = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, default=Decimal('0.02'))
    transaction_date = serializers.DateTimeField(required=True)

    def validate_fee_percentage(self, value):
        """Ensure fee percentage is within a valid range (0% to 5%)."""
        if value < Decimal('0') or value > Decimal('5'):
            raise serializers.ValidationError(smt[10])  # Replace with a meaningful error message
        return value

    def validate_transaction_datetime(self, value):
        """
        Validate transaction datetime format and return a datetime object.

        Expected format: 'YYYY-MM-DD HH:MM:SS'
        Example: '2024-02-04 15:30:00'
        """
        try:
            parsed_datetime = datetime.strptime(str(value), "%Y-%m-%d %H:%M")
            return parsed_datetime
        except ValueError:
            raise serializers.ValidationError(smt[13])

    def validate_coin(self, coin_symbol):
        """Calls the microservice to validate the coin symbol."""
        url = f"{settings.FETCH_PRICE_MICRO_SERVICE}/validate_coin/{coin_symbol}"
        try:
            logger.debug(f"send request to fetch validation {url}")
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"response of validation request to {url}: {data}")
            if not data["success"]:
                raise serializers.ValidationError(
                    {"coin_symbol": data.get("data")}
                )

            coin_name = data.get("data")
            if not coin_name:
                raise serializers.ValidationError(
                    {"coin_name": smt[9]}
                )

            return coin_symbol.upper(), coin_name
        except requests.RequestException as e:
            logger.error(f"went wrong on sending request: {e} to the {url}")
            raise requests.RequestException(mt[500])

    def validate(self, data):
        """Validate the transaction and calculate the missing field."""
        user = self.context['request'].user
        coin_symbol = data.get('coin_symbol')
        transaction_type = data.get('type')
        fee_percentage = data.get('fee', Decimal('0.02'))

        validated_coin_symbol, coin_name = self.validate_coin(coin_symbol)

        try:
            data['price'] = Decimal(data['price'])
        except ValueError:
            raise serializers.ValidationError({"price": smt[3]})
        try:
            data['amount'] = Decimal(data['amount'])
        except ValueError:
            raise serializers.ValidationError({"amount": smt[3]})

        data["value"] = data['amount'] * data['price']

        balance = Balance.objects.get(user=user)
        if transaction_type == "buy" and balance.usdt_balance < data['value']:
            raise ValueError(smt[4], {"balance": balance.usdt_balance,
                                      "value": data['value']})

        logger.debug("create or get a new box for the given transaction")
        coin, created = Coin.objects.get_or_create(symbol=validated_coin_symbol, name=coin_name)

        if created:
            logger.info(f"new coin created: {coin}")

        try:
            box = Box.objects.get(user=user, coin=coin, is_closed=False)

            if transaction_type == "sell" and box.total_amount < data['amount']:
                raise ValueError(smt[5], {"balance": box.total_amount,
                                          "value": data['value']})

        except Box.DoesNotExist:
            if transaction_type == "sell":
                raise ValueError(smt[5], {"balance": 0,
                                           "value": data['value']})

            box = Box.objects.create(user=user, coin=coin, is_closed=False)
            logger.info(f"new box created: {box} for {user}")

        data['coin'] = coin
        data['fee'] = fee_percentage

        return data


class TransactionDataSerializer(serializers.ModelSerializer):
    profit_loss_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ["id", "type" ,"amount", "value", "price", "profit_loss_value", "profit_loss_percentage",
                  "transaction_date"]


    def get_profit_loss_percentage(self, obj):
        """Calculate profit/loss percentage based on current price for 'buy' transactions.
        If it's a 'sell' transaction, return the stored value from the database.
        """

        if obj.type == "buy":
            try:
                current_price = fetch_multiple_prices([obj.box.coin.symbol])
                logger.debug(f"try to fetch the % for the {obj.box.coin.name}-{obj.id} with the price of {current_price}")
                if current_price == 0:
                    return 0
                if current_price and obj.price > 0:
                    return ((Decimal(current_price[obj.box.coin.symbol]) - obj.price) / obj.price) * 100
            except Exception as e:
                logger.error(f"Something went wrong on fetching detail: {e}")
                return None
        elif obj.type == "sell":
            return obj.profit_loss_percentage

        return None