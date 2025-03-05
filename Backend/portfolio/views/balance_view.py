from decimal import Decimal, InvalidOperation
import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Backend.messages import response_message as mt
from Backend.messages import serializer_response_message as mst
from Backend.utils import create_response
from ..models import Balance
from ..serializers.balance_serializer import BalanceSerializer, ModifyBalanceSerializer

logger = logging.getLogger("backend")


class BalanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get user balance",
        operation_description="Retrieve the user's available USDT balance and total balance including coin holdings.",
        tags=["💰 Balance"]
    )
    def get(self, request):
        """Get the user's total balance & USDT balance."""
        balance, _ = Balance.objects.get_or_create(user=request.user)
        serializer = BalanceSerializer(balance)
        logger.debug("")
        return create_response(success=True, message=mt[203],
                               data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Deposit USDT",
        operation_description="Add USDT to the user's balance.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["amount"],
            properties={
                "amount": openapi.Schema(type=openapi.TYPE_NUMBER, description="Amount to deposit (in USDT)")
            },
        ),
        responses={200: openapi.Response("Deposited successfully")},
        tags=["💰 Balance"]
    )
    def post(self, request):
        """Add USDT to balance."""

        serializer = ModifyBalanceSerializer(data=request.data)

        if serializer.is_valid():
            amount = serializer.validated_data["amount"]

            balance, _ = Balance.objects.get_or_create(user=request.user)
            balance.deposit(amount)

            balance.save()
            logger.info(f"user: {request.user}, deposit balance by {amount}")
            return create_response(success=True, message=mt[204],
                                   data = {"new_balance": f"{balance.usdt_balance:.8f}"}, status=status.HTTP_200_OK)

        return create_response(success=False, message=mt[400],
                               data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Withdraw USDT",
        operation_description="Withdraw USDT from the user's balance.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["amount"],
            properties={
                "amount": openapi.Schema(type=openapi.TYPE_NUMBER, description="Amount to withdraw (in USDT)")
            },
        ),
        responses={200: openapi.Response("Withdrawn successfully")},
        tags=["💰 Balance"]
    )
    def delete(self, request):
        """Withdraw USDT from balance."""
        serializer = ModifyBalanceSerializer(data=request.data)

        if serializer.is_valid():
            amount = serializer.validated_data["amount"]

            balance, _ = Balance.objects.get_or_create(user=request.user)

            if not balance.withdraw(amount):
                return create_response(success=False, message=mt[400],
                                       data={"amount": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

            balance.save()
            logger.info(f"user: {request.user}, deposit withdraw by {amount}")
            return create_response(success=True, message=mt[204],
                                   data={"new_balance": f"{balance.usdt_balance:.8f}"}, status=status.HTTP_200_OK)

        return create_response(success=False, message=mt[400],
                               data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)