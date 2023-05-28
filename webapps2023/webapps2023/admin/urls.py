from django.urls import path
from . import views

urlpatterns = [
    path('view_accounts/', views.view_all_accounts, name='view_all_accounts'),
    path('view_transactions/', views.view_all_transactions, name='view_all_transactions'),
    path('view_requests/', views.view_all_requests, name='view_all_requests'),
    path('create_new_admin/', views.create_new_admin, name='create_new_admin'),
]
