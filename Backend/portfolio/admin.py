from django.contrib import admin
from .models import Box, Balance, BalanceHistory, Transaction, Coin

admin.site.register(Box)
admin.site.register(Balance)
admin.site.register(BalanceHistory)
admin.site.register(Transaction)
admin.site.register(Coin)
