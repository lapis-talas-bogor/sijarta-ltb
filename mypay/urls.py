from django.urls import path
from mypay.views import mypay_view, transaksi_mypay, topup, transfer, withdrawal, bayar_jasa

app_name = "mypay"

urlpatterns = [
    path("", mypay_view, name="mypay_view"),
    path("transaksi/", transaksi_mypay, name="transaksi_mypay"),
    path('topup/', topup, name='topup'),
    path('withdrawal/', withdrawal, name='withdrawal'),
    path('transfer/', transfer, name='transfer'),
    path('bayar_jasa/', bayar_jasa, name="bayar_jasa")
]
