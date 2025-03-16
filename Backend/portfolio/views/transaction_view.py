import logging
from datetime import datetime
from decimal import Decimal

import requests
from django.db import transaction as db_transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from Backend.utils import create_response
from Backend.messages import response_message as mt
from ..models import Box, Transaction, Balance
from ..serializers.transaction_serializers import TransactionSerializer

logger = logging.getLogger('backend')

class TransactionCreateAPIView(APIView):
    """
    API view for creating a new buy/sell transaction with coin validation.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=TransactionSerializer,
        responses={
            201: openapi.Response(
                "Transaction created successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Transaction created successfully"),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "transaction_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=123),
                                "coin_name": openapi.Schema(type=openapi.TYPE_STRING, example="BTC"),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                "Bad request, validation error",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Bad request, validation error"),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "non_field_errors": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(type=openapi.TYPE_STRING, example="This field is required."),
                                ),
                            },
                        ),
                    },
                ),
            ),
            500: openapi.Response(
                "Internal server error",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Something went wrong"),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
                    },
                ),
            ),
        },
        tags=["💼 Transactions"],
    )
    def post(self, request):
        user = request.user
        data = request.data

        try:
            serializer = TransactionSerializer(data=data, context={'request': request})

            if serializer.is_valid():
                validated_data = serializer.validated_data
                transaction_type = validated_data['type']
                coin = validated_data['coin']
                price = validated_data['price']
                amount = validated_data['amount']
                value = validated_data['value']
                transaction_date = validated_data.get('transaction_date',
                                                      datetime.now())
                fee = validated_data['fee']

                box = Box.objects.get(user=user, coin=coin, is_closed=False)

                try:
                    with db_transaction.atomic():
                        transaction = Transaction.objects.create(
                            user=user,
                            box=box,
                            type=transaction_type,
                            price=price,
                            amount=amount,
                            value=value,
                            transaction_date=transaction_date,
                            fee=fee
                        )

                        data = {
                        "transaction_id": transaction.id,
                        "coin_name": coin.name,
                        }
                        logger.info(f"Transaction created for user {user}, data: {data}")

                        return create_response(success=True, message=mt[205],
                                               data=data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    logger.error(f"something went wrong on database changes : {e}")
                    return create_response(success=False, message=mt[400],
                                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return create_response(success=False, message=mt[400],
                                   data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            logger.error(f"requests error happen: {e}")
            return create_response(success=False, message=str(e),
                                   status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError as e:
            msg, data = eval(str(e), {"Decimal": Decimal})
            return create_response(success=False, message=msg, data=data,
                                   status=status.HTTP_400_BAD_REQUEST)


class TransactionDeleteAPIView(APIView):
    @swagger_auto_schema(
        responses={
            204: openapi.Response(
                "Transaction deleted successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Transaction deleted successfully"),
                    },
                ),
            ),
            404: openapi.Response(
                "Transaction not found",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Transaction not found"),
                    },
                ),
            ),
            500: openapi.Response(
                "Internal server error",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example="Something went wrong"),
                    },
                ),
            ),
        },
        tags=["💼 Transactions"],
    )
    def delete(self, request, transaction_id):
        user = request.user

        try:
            transaction = Transaction.objects.get(id=transaction_id, user=user)
            box = transaction.box
            balance = user.balance
            fee_multiplier = Decimal('1') - (transaction.fee / Decimal('100'))

            last_transaction = box.transactions.order_by('-created_at').first()

            if transaction != last_transaction:
                return create_response(success=False, message=mt[408], status=status.HTTP_400_BAD_REQUEST)

            if box.is_closed:
                return create_response(success=False, message=mt[407], status=status.HTTP_400_BAD_REQUEST)

            with db_transaction.atomic():
                if transaction.type == 'buy':

                    balance.deposit((transaction.amount / fee_multiplier) * transaction.price)

                    box.total_amount -= transaction.amount
                    box.total_buy_value -= transaction.value
                    box.total_buy_amount -= transaction.amount

                    if box.total_buy_amount > 0:
                        box.average_buy_price = box.total_buy_value / box.total_buy_amount
                    else:
                        box.average_buy_price = Decimal('0')

                elif transaction.type == 'sell':
                    balance.withdraw(transaction.value * (Decimal('1') - transaction.fee / Decimal('100')))

                    box.total_amount += transaction.amount
                    box.total_sell_value -= transaction.value
                    box.total_sell_amount -= transaction.amount

                    if box.total_sell_amount > 0:
                        box.average_sell_price = box.total_sell_value / box.total_sell_amount
                    else:
                        box.average_sell_price = Decimal('0')

                transaction.delete()
                
                balance.save()
                box.save()

                if not box.transactions.exists():
                    box.delete()

                return create_response(success=True, message=mt[207], status=status.HTTP_204_NO_CONTENT)
        except Transaction.DoesNotExist:
            return create_response(success=False, message=mt[404], status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            return create_response(success=False, message=mt[400], status=status.HTTP_500_INTERNAL_SERVER_ERROR)