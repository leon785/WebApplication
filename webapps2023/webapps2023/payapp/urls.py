from django.urls import path
from . import views

urlpatterns = [
    path('', views.points_transfer, name='points_transfer'),
    path('history/', views.show_history, name='payments_history'),
    path('makerequest/', views.make_request, name='make_request'),
    path('showrequest/', views.show_request, name='past_request'),
    path('showrequestaccepted/', views.button_accept, name='button_accept'),
    path('showrequestdeclined/', views.button_decline, name='button_decline'),
    path('convertcurrency/', views.CurrencyChange.as_view(), name='convert_currency'),
]
