from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from finances import views

expenses_router = DefaultRouter()
expenses_router.register('items', views.ExpenseItemViewSet, basename='expense-items')
expenses_router.register('categories', views.ExpenseCategoryViewSet, basename='expense-categories')

income_router = DefaultRouter()
income_router.register('items', views.IncomeItemViewSet, basename='income-items')
income_router.register('categories', views.IncomeCategoryViewSet, basename='income-categories')

fees_router = DefaultRouter()
fees_router.register('structures', views.FeeStructureViewSet, base_name='fee-structures')
fees_router.register('challans', views.ChallanViewSet, base_name='fee-challans')

urlpatterns = [
    path('expenses/', include(expenses_router.urls)),
    url(r'^expenses/summary/$', views.ExpenseSummaryAPIView.as_view(),
        name='expense-summary'),
    url(r'^expenses/details/$', views.ExpenseDetailsAPIView.as_view(),
        name='expense-details'),
    url(r'^income/details/$', views.IncomeDetailsAPIView.as_view(),
        name='income-details'),
    url(r'^income/summary/$', views.IncomeSummaryAPIView.as_view(),
        name='income-summary'),
    path('income/', include(income_router.urls)),
    path('fees/', include(fees_router.urls)),
    url(r'^fees/challans/download_csv',
        view=views.download_challans_csv,
        name='challans-download-csv'
    )
]
