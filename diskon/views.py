from django.shortcuts import render, redirect
from django.http import HttpResponse
from diskon.services.diskon_service import DiscountService
from django.db import IntegrityError
from django.http import JsonResponse
import uuid
from datetime import datetime, timedelta


# Create your views here.


def show_diskon(request):
    voucher = DiscountService.get_all_vouchers()
    promo = DiscountService.get_all_promo()
    metode_bayar = DiscountService.get_all_metode_bayar()
    context = {
        "user": request.user,
        "voucher" : voucher,
        "promo": promo,
        "metode_bayar": metode_bayar,
    }
    return render(request, "show_diskon.html", context)


def beli_voucher(request):
    promo = DiscountService.get_all_promo()
    if request.method == "POST":
        # Ambil data dari form yang dikirim
        kode_voucher = request.POST.get('kode_voucher')
        harga_voucher = float(request.POST.get('harga_voucher'))
        metode_pembayaran_id = request.POST.get('metode_pembayaran')
        kuota_penggunaan = request.POST.get('kuota_penggunaan')
        jml_hari_berlaku = request.POST.get('jml_hari_berlaku')
        tanggal_mulai = datetime.now()  # Tanggal pembelian voucher
        tanggal_akhir = tanggal_mulai + timedelta(days=int(jml_hari_berlaku))  # Hitung tanggal akhir berlaku
        tanggal_akhir_str = tanggal_akhir.strftime('%d/%m/%Y') 

        user_id = str(request.user["id"])  # Ambil ID pengguna yang sedang login
        metode_pembayaran_nama = DiscountService.get_metode_bayar(metode_pembayaran_id)
        if metode_pembayaran_nama == "MyPay":
            # Cek saldo MyPay pengguna
            saldo = DiscountService.check_saldo_mypay(user_id)
            # Cek apakah saldo mencukupi untuk pembelian
            if saldo < harga_voucher:
                # Jika saldo tidak mencukupi, tampilkan modal gagal
                return render(request, 'show_diskon.html', {
                    'status_modal': 'gagal',
                    'message': 'Maaf, saldo Anda tidak cukup untuk membeli voucher ini.',
                    'voucher': DiscountService.get_all_vouchers(),
                    "promo": promo,
                    'metode_bayar': DiscountService.get_all_metode_bayar(),
                })
            # Update saldo MyPay pengguna
            DiscountService.update_saldo_mypay(harga_voucher, user_id)
            # Record pembelian voucher
            # Misalkan ID transaksi voucher dibuat secara otomatis
            # Simulasi ID transaksi, misalnya ID baru dari DB
            id_transaksi_voucher = uuid.uuid4()  # Ganti dengan mekanisme ID transaksi yang sesuai di aplikasi Anda
            id_transaksi_mypay = uuid.uuid4()  # Ganti dengan mekanisme ID transaksi yang sesuai di aplikasi Anda
            DiscountService.record_voucher_purchase(id_transaksi_voucher, 0, user_id, kode_voucher, metode_pembayaran_id)
            DiscountService.record_mypay_purchase(id_transaksi_mypay, user_id, harga_voucher, DiscountService.get_id_category_voucher("Pembelian Voucher"))
            return render(request, 'show_diskon.html', {
                'status_modal': 'sukses',
                'message': f'Selamat! Anda berhasil membeli voucher kode {kode_voucher}. Voucher ini akan berlaku hingga tanggal {tanggal_akhir_str} dengan kuota penggunaan sebanyak {kuota_penggunaan} kali.',
                'voucher': DiscountService.get_all_vouchers(),
                'metode_bayar': DiscountService.get_all_metode_bayar(),
                "promo": promo,
            })
        else:
            id_transaksi_voucher = uuid.uuid4()  # Ganti dengan mekanisme ID transaksi yang sesuai di aplikasi Anda
            DiscountService.record_voucher_purchase(id_transaksi_voucher, 0, user_id, kode_voucher, metode_pembayaran_id)
            return render(request, 'show_diskon.html', {
                'status_modal': 'sukses',
                'message': f'Selamat! Anda berhasil membeli voucher kode {kode_voucher}. Voucher ini akan berlaku hingga tanggal {tanggal_akhir_str} dengan kuota penggunaan sebanyak {kuota_penggunaan} kali.',
                'voucher': DiscountService.get_all_vouchers(),
                'metode_bayar': DiscountService.get_all_metode_bayar(),
                "promo": promo,
            })





