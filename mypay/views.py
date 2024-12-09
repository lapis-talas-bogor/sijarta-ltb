from django.http import JsonResponse
from django.shortcuts import redirect, render
from mypay.services.mypay_service import MyPayService
from users.utils.decorators import only_pengguna
from users.services.user_service import UserService


def mypay_view(request):
    uid = str(request.user['id'])
    tr_history = MyPayService.get_tr_mypay_from_user_id(uid)
    
    context = {
        "user": request.user,
        "riwayat" : tr_history
               }
    return render(request, "show_mypay.html", context)


def transaksi_mypay(request):
    uid = str(request.user['id'])
    pesanan = MyPayService.get_menunggu_pembayaran_pemesanan_by_user(uid)

    context = {
        "user": request.user,
        "pesanan" : pesanan
        }
    return render(request, "transaksi_mypay.html", context)

def topup(request) :
    """
    Berfungsi untuk memproses topup
    """

    if request.method == "POST":
        nominal = request.POST.get('nominal')
        uid = str(request.user['id'])
        
        # Validasi untuk memastikan bahwa nominal bilangan positif
        # Sudah dihandle di front-end juga
        try:
            nominal = int(nominal)
            if nominal <= 0:
                return JsonResponse({"message": "Nominal harus bilangan positif!"}, status=400)
        except ValueError:
            return JsonResponse({"message": "Format nominal salah!"}, status=400)
        
        try :
            MyPayService.topup(uid, nominal)

        except Exception as e:
            return JsonResponse(
                {"message": "Failed to process the top-up", "error": str(e)}, status=500
            )
        
        return JsonResponse({"status": "success", "redirect_url": "/mypay/transaksi"})
    
    return JsonResponse({"message": "Invalid request method"}, status=405)
    
def withdrawal(request) :
    """
    Berfungsi untuk memproses penarikan dana.
    * Pada formnya sendiri terdapat field untuk melakukan input nama bank dan no rek
    * tetapi kita asumsikan bahwa no rek selalu milik user sehingga tidak diperlukan validasi
    """
    if request.method == "POST":
        nominal = request.POST.get('nominal')
        uid = str(request.user['id'])

        # Memastikan nominal adalah integer positif
        try:
            nominal = int(nominal)
            if nominal <= 0:
                return JsonResponse({"message": "Nominal harus bilangan positif"}, status=400)
        except ValueError:
            return JsonResponse({"message": "Nominal tidak valid"}, status=400)
        
        # Memastikan nominal yang ingin ditarik tidak melebihi saldo mypay pengguna
        if int(request.user['mypay_balance']) < nominal :
            return JsonResponse({"message": "Saldo kurang"}, status=400)
            
        try :
            MyPayService.withdrawal(uid, nominal)
        except Exception as e:
            return JsonResponse(
                {"message": "Failed ", "error": str(e)}, status=500
            )

        return JsonResponse({"status": "success", "redirect_url": "/mypay/transaksi"})
    
    return JsonResponse({"message": "Invalid request method"}, status=405)

def transfer(request) :
    """
    Berfungsi untuk melakukan transfer
    """
    if request.method == "POST" :
        nominal = request.POST.get('nominal')
        no_hp_penerima = request.POST.get('no_hp')
        uid = str(request.user['id'])

        # Validasi jika nomor hp penerima tidak terhubung oleh suatu user
        if not UserService.get_user_by_phone_number(no_hp_penerima) :
            return JsonResponse({"message": "Penerima tidak ditemukan!"}, status=400)

        # Memastikan nominal merupakan integer positif
        try:
            nominal = int(nominal)
            if nominal <= 0:
                return JsonResponse({"message": "Nominal harus berupa bilangan positif!"}, status=400)
        except ValueError:
            return JsonResponse({"message": "Format nominal salah!"}, status=400)

        # Memastikan user tidak melakukan transfer ke mypaynya sendiri
        if no_hp_penerima == request.user['phone_number'] :
            return JsonResponse({"message": "Tidak bisa transfer ke diri sendiri!"}, status=400)

        # Memastikan saldo user cukup
        if int(request.user['mypay_balance']) < nominal :
            return JsonResponse({"message": "Saldo kurang"}, status=400)
        
        try :
            MyPayService.transfer_mypay(uid, no_hp_penerima, nominal)
        except Exception as e:
            return JsonResponse(
                {"message": "Failed to process the transfer ", "error": str(e)}, status=500
            )

        return JsonResponse({"status": "success", "redirect_url": "/mypay/transaksi"})

    return JsonResponse({"message": "Invalid request method"}, status=405)

@only_pengguna
def bayar_jasa(request) :
    """
    Berfungsi untuk membayar jasa
    * Input form pada kasus ini bersifat autofill sesuai pesanan yang dipilih di dropdown
    """
    if request.method == "POST" :
        id_pesanan = request.POST.get('id_pesanan')
        uid = str(request.user['id'])
        harga_pesanan = int(request.POST.get('harga_pesanan'))

        # Memastikan bahwa saldo user mencukupi
        if int(request.user['mypay_balance']) < harga_pesanan :
            return JsonResponse({"message": "Saldo kurang"}, status=400)
        
        try:
            MyPayService.bayar(id_pesanan, uid, harga_pesanan)
        except Exception as e:
            return JsonResponse(
                {"message": "Failed to process the payment", "error": str(e)}, status=500
            )
        
        return JsonResponse({"status": "success", "redirect_url": "/mypay/transaksi"})

    return JsonResponse({"message": "Invalid request method"}, status=405)