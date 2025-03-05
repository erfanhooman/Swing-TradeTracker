from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Balance, BalanceHistory


@receiver(post_save, sender=User)
def create_user_balance(sender, instance, created, **kwargs):
    if created:
        balance = Balance.objects.create(user=instance)

        BalanceHistory.objects.create(
            user=instance,
            usdt_balance=balance.usdt_balance,
            coin_balance=0,
            total_balance=balance.usdt_balance
        )