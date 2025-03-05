from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .views.balance_view import BalanceAPIView
from .views.box_views import CloseBoxAPIView, BoxListAPIView, BoxDetailAPIView
from .views.history_views import BalanceHistoryListAPIView
from .views.summary_view import ProfitLossSummaryAPIView
from .views.transaction_view import TransactionDeleteAPIView, TransactionCreateAPIView

# Swagger Schema View
schema_view = get_schema_view(
    openapi.Info(
        title="Trading Tracker API",
        default_version="v1",
        description="API documentation for the trading tracker system.",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
urlpatterns = [
    # Swagger & Redoc
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Transactions
    path("transactions/", TransactionCreateAPIView.as_view(), name="create-transaction"),
    # path("transactions/<int:transaction_id>/", TransactionDeleteAPIView.as_view(), name="create-transaction"), # Work on it
    # balance
    path("balance/", BalanceAPIView.as_view(), name="user-balance"),
    # Box
    path("boxes/<int:box_id>/close/", CloseBoxAPIView.as_view(), name="close-box"),
    path("boxes/", BoxListAPIView.as_view(), name="box-list"),
    path("boxes/<int:box_id>/transactions/", BoxDetailAPIView.as_view(), name="box-transactions"),
    # Summary
    path("summary/", ProfitLossSummaryAPIView.as_view(), name="profit-loss-summary"),
    # History
    path("balance/history/", BalanceHistoryListAPIView.as_view(), name="balance-history"),
]
