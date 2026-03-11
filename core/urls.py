from django.urls import path
from core.views import testing_view, TransactionListView, TransactionDetailView

urlpatterns = [
    path('testing/', testing_view, name='testing'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<int:id>/', TransactionDetailView.as_view(), name='transaction-detail'),
]