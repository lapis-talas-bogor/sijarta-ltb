from django.urls import path

from diskon.views import show_diskon, beli_voucher

app_name = "diskon"

urlpatterns = [
    path('', show_diskon, name="show_diskon"),
    path('beli_voucher/', beli_voucher, name='beli_voucher'),
]
