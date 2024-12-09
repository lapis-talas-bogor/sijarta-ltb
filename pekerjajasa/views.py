from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from pekerjajasa.services.pekerjajasa_servise import PekerjaJasaService
from users.utils.decorators import only_pekerja

@only_pekerja
def pekerjajasa_view(request):
    '''
    Berfungsi untuk menangani view kelola pekerjaan saya.
    Di view ini pekerja bisa mengambil pekerjaan yang belum ada pekerjanya
    atau dengan kata lain yang status pemesanannya masih 'mencari pekerja terdekat.
    Bisa filter bedasarkan kategori dan sub kategori melalui dropdown.
    '''
    pekerja_id = str(request.user['id'])

    # deklarasi variabel untuk filter
    nama_kategori = None
    nama_subkategori = None

    # ketika tombol filter ditekan, akan mengirim request POST
    if request.method == "POST" :
        nama_kategori = request.POST.get("nama_kategori")
        nama_subkategori = request.POST.get("nama_subkategori")
 
    # fetch semua pesanan yang belum ada pekerja
    kerjaan = PekerjaJasaService.get_pesanan_with_no_pekerja(pekerja_id,nama_kategori, nama_subkategori)

    # fetch data untuk drop down
    sub_kategori = PekerjaJasaService.get_kategori_pekerjaan(pekerja_id)
    subkategori_dropdown = PekerjaJasaService.to_key_list(sub_kategori) # ubah ke dict <key, [value]>

    context = {
        "user": request.user,
        "kerjaan" : kerjaan,
        "dropdown_data" : subkategori_dropdown
    }

    return render(request, "show_pekerjajasa.html", context)

@only_pekerja
def status_view(request):
    '''
    Berfungsi untuk menangani kelola status pekerjaan.
    Di view ini pekerja melakukan update terhadap pekerjaan yang sedang dilakukan.
    Ada filter melalui search atau drop down
    '''
    pekerja_id = str(request.user['id'])
    statuses = PekerjaJasaService.get_statuses_for_pekerja() # fetch data pekerjaan yang sedang dilakukan oleh pejera

    # deklarasi
    match = None
    status = None

    # ketika tombol filter ditekan, akan mengirim request POST
    if request.method == "POST" :
        match = request.POST.get("match")    
        status = request.POST.get("status")

    # fetch semua pesanan yang sedang/telah dilakukan oleh pekerja
    pekerjaan = PekerjaJasaService.get_tr_pemesanan_jasa_by_pekerja(pekerja_id, match, status)

    context = {
        "user": request.user,
        "pekerjaan" : pekerjaan,
        'statuses' : statuses
    }
    
    return render(request, "show_status.html", context)

@only_pekerja
def update_status(request):
    '''
    Berfungsi untuk update status
    Via button jadi seharusnya minim validasi
    '''
    if request.method == "POST" :
        id_pemesanan = str(request.POST.get("id"))
        PekerjaJasaService.update_status(id_pemesanan)
        return redirect('pekerjajasa:status_view')
    
    return JsonResponse({"message": "Invalid request method"}, status=405)

@only_pekerja
def ambil_pekerjaan(request):
    '''
    Berfungsi untuk ambil pemesanan yang 'id_pekerja' nya masih null
    Via button jadi seharusnya minim validasi
    '''
    if request.method == "POST" :
        pekerja_id = str(request.user['id'])
        id_kerjaan = request.POST.get("id_kerjaan")
        PekerjaJasaService.kerjakan_pekerjaan(pekerja_id, id_kerjaan)
        return redirect('pekerjajasa:pekerjajasa_view')
    
    return JsonResponse({"message": "Invalid request method"}, status=405)

@only_pekerja
def get_subcategories(request) :
    '''
    Fungsi ini mengembalikan json dari dictionary dengan key kategori pekerja
    dengan value berupa list yang berisi subkategorinya
    '''
    pekerja_id = str(request.user['id'])
    kerjaan = PekerjaJasaService.get_kategori_pekerjaan(pekerja_id) ## fetch dict

    return JsonResponse(PekerjaJasaService.to_key_list(kerjaan))