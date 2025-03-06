from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import default
from django.utils.timezone import now

from Backend.messages import serializer_response_message as mst
from .utils import fetch_coin_icon, fetch_multiple_prices


class Coin(models.Model):
    """Stores details about each cryptocurrency."""
    symbol = models.CharField(max_length=50, unique=True)  # e.g., "BTC", "ETH"
    name = models.CharField(max_length=100)  # e.g., "Bitcoin", "Ethereum"
    icon_url = models.CharField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.icon_url:
            self.icon_url = fetch_coin_icon(self.symbol)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="balance")
    usdt_balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)

    def deposit(self, amount):
        """Increase USDT balance when adding USDT."""
        self.usdt_balance += amount
        self.save()

    def withdraw(self, amount):
        """Decrease USDT balance when making a transaction."""
        if self.usdt_balance >= amount:
            self.usdt_balance -= amount
            self.save()
            return True
        return False  # Insufficient funds

    def get_coin_balance(self):
        """Calculate total value of coins the user holds in USDT."""
        boxes = Box.objects.filter(user=self.user, is_closed=False)

        coin_symbols = list(set(box.coin.symbol for box in boxes))
        coin_prices = fetch_multiple_prices(coin_symbols)

        coin_balance = 0

        for box in boxes:
            box_coin_balance = box.total_amount * coin_prices[box.coin.symbol]
            coin_balance += box_coin_balance

        return coin_balance

    def get_total_balance(self):
        """Total balance = USDT balance + Coin balance."""
        return self.usdt_balance + self.get_coin_balance()

    def get_coin_balance_at_buy_price(self):
        """Calculate total value of all coins held based on their buy price."""

        boxes = Box.objects.filter(user=self.user, is_closed=False)

        total_coin_balance = 0
        for box in boxes:
            total_coin_balance += box.total_amount * box.average_buy_price

        return total_coin_balance

    def __str__(self):
        return f"{self.user.username} - USDT: {self.usdt_balance}, Total: {self.get_total_balance()}"


class BalanceHistory(models.Model):  # TODO: Not Implemented Yet ( Need Taught on it )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="balance_history")
    usdt_balance = models.DecimalField(max_digits=18, decimal_places=8)
    coin_balance = models.DecimalField(max_digits=18, decimal_places=8)
    total_balance = models.DecimalField(max_digits=18, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.total_balance} USDT at {self.timestamp}"


class Box(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boxes")
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE, related_name="boxes")
    total_amount = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    total_buy_amount = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    total_sell_amount = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    total_buy_value = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    total_sell_value = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    average_buy_price = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    average_sell_price = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    is_closed = models.BooleanField(default=False)

    @property
    def age(self):
        """Returns the age of the box in days since the first transaction."""
        first_transaction = self.transactions.order_by("transaction_date").first()
        last_transaction = self.transactions.order_by("transaction_date").last()

        if not first_transaction or not first_transaction.transaction_date:
            return None

        if self.is_closed:
            if last_transaction and last_transaction.transaction_date:
                return (last_transaction.transaction_date - first_transaction.transaction_date ).days
            return None

        return (now().date() - first_transaction.transaction_date.date()).days


    def __str__(self):
        return f"{self.coin.name} (Closed: {self.is_closed})"


class Transaction(models.Model):
    TYPE_CHOICES = [('buy', 'Buy'), ('sell', 'Sell')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    price = models.DecimalField(max_digits=18, decimal_places=8)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    value = models.DecimalField(max_digits=18, decimal_places=8)  # price * amount
    profit_loss_value = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    profit_loss_percentage = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    transaction_date = models.DateTimeField(default=now)
    fee = models.DecimalField(max_digits=18, decimal_places=8, default=0.02)

    def save(self, *args, **kwargs):
        """Handle buy/sell updates when saving the transaction."""

        box = self.box
        balance = self.user.balance

        if self.type == 'buy':
            if not balance.withdraw(self.value):
                raise ValueError(mst[4])

            self.amount *= (Decimal('1') - self.fee / Decimal('100'))
            self.value = self.amount * self.price

            box.total_amount += self.amount
            box.total_buy_value += self.value
            box.total_buy_amount += self.amount
            box.save()

            box.average_buy_price = box.total_buy_value / box.total_buy_amount
            box.save()


        elif self.type == 'sell':

            box.total_amount -= self.amount
            box.total_sell_value += self.value
            box.total_sell_amount += self.amount

            balance.deposit(self.value * (Decimal('1') - self.fee / Decimal('100')))

            box.save()

            box.average_sell_price = box.total_sell_value / box.total_sell_amount
            box.save()

            # Calculate profit/loss for the sell
            self.profit_loss_percentage = ((self.price - box.average_buy_price) / box.average_buy_price) * 100
            self.profit_loss_value = (self.profit_loss_percentage / 100) * self.value

        total_coin_balance = balance.get_coin_balance_at_buy_price()

        BalanceHistory.objects.create(
            user=self.user,
            usdt_balance=balance.usdt_balance,
            coin_balance=total_coin_balance,
            total_balance=balance.usdt_balance + total_coin_balance,
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type.upper()} {self.amount} @ {self.price} ({self.box.coin.name})"
