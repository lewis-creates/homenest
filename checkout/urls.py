from django.urls import path
from . import views

urlpatterns = [
    path('checkout_success/<order_number>', views.checkout_success, name='checkout_success'),
    path('', views.checkout, name='checkout')
]