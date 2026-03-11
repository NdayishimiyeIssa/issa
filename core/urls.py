from django.urls import path
from core.views import testing_view, TransactionListView, TransactionDetailView, CategoryListView, CategoryDetailView

urlpatterns = [
    path('testing/', testing_view, name='testing'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<int:id>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:id>/', CategoryDetailView.as_view(), name='category-detail'),
]