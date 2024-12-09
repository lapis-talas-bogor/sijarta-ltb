from datetime import datetime
from django.contrib import messages
from uuid import UUID
import uuid
from django.http import JsonResponse
from django.shortcuts import redirect, render
from services_and_booking.services.category_service import CategoryAndSubcategoryService
from services_and_booking.services.order_sevice import OrderService

# Create your views here.
def show_homepage(request):
    categories = CategoryAndSubcategoryService.get_all_categories()

    # Daftar kategori dan subkategori 
    category_subcategory_pairs = []
    for category in categories:
        subcategories = CategoryAndSubcategoryService.get_subcategories_by_category(category['id'])
        category_subcategory_pairs.append({
            'category': category,
            'subcategories': subcategories
        })
    
    search_results = []
    message = ''  
    category_id_filter = request.POST.get('category_filter')
    subcategory_name = request.POST.get('search_subcategory', '').lower()

    if request.method == 'POST':
        # kosongan gaada filter
        if not category_id_filter and not subcategory_name:
            category_subcategory_pairs = [{
                'category': category,
                'subcategories': CategoryAndSubcategoryService.get_subcategories_by_category(category['id'])
            } for category in categories]
            message = ''

        else:
            # Filter berdasarkan kategori jika ada
            if category_id_filter and category_id_filter != "Pilih Kategori...":
                try:
                    category_id_filter = UUID(category_id_filter)
                    category_subcategory_pairs = [{
                        'category': next(cat for cat in categories if cat['id'] == category_id_filter),
                        'subcategories': CategoryAndSubcategoryService.get_subcategories_by_category(category_id_filter)
                    }]
                except ValueError:
                    message = "ID kategori yang dimasukkan tidak valid."
                    category_subcategory_pairs = []

            # filter cuman kategori
            if subcategory_name:
                search_results = []
                for pair in category_subcategory_pairs:
                    filtered_subcategories = [
                        subcategory for subcategory in pair['subcategories'] 
                        if subcategory_name in subcategory['nama_subkategori'].lower()
                    ]
                    if filtered_subcategories:
                        search_results.append({
                            'category': pair['category'],
                            'subcategories': filtered_subcategories
                        })

                # Kalo gaada subkategori yang cocok
                if not search_results:
                    message = "Subkategori yang Anda cari tidak ditemukan."

            # Kalo kategori dan subkategori dicari bersama
            if category_id_filter and subcategory_name:
                search_results = []
                for pair in category_subcategory_pairs:
                    # Filter berdasarkan kategori
                    if pair['category']['id'] == category_id_filter:
                        filtered_subcategories = [
                            subcategory for subcategory in pair['subcategories']
                            if subcategory_name in subcategory['nama_subkategori'].lower()
                        ]
                        # kalo ada subkategori yang cocok
                        if filtered_subcategories:
                            search_results.append({
                                'category': pair['category'],
                                'subcategories': filtered_subcategories
                            })

                if not search_results:
                    message = "Tidak ada hasil yang cocok dengan pencarian Anda."

            # kategori ga di filter, tapi subnya iya
            if not category_id_filter or category_id_filter == "Pilih Kategori...":
                search_results = []
                for pair in category_subcategory_pairs:
                    filtered_subcategories = [
                        subcategory for subcategory in pair['subcategories']
                        if subcategory_name in subcategory['nama_subkategori'].lower()
                    ]
                    if filtered_subcategories:
                        search_results.append({
                            'category': pair['category'],
                            'subcategories': filtered_subcategories
                        })

                if not search_results:
                    message = "Subkategori yang Anda cari tidak ditemukan."

    context = {
        "user": request.user,
        "categories": categories,
        "category_subcategory_pairs": category_subcategory_pairs,
        "search_results": search_results,
        "message": message,
        "category_id_filter": category_id_filter, 
        "subcategory_name": subcategory_name,
    }

    return render(request, "homepage.html", context)


def search_subcategory(request):
    query = request.GET.get('query', '')
    if query:
        search_results = CategoryAndSubcategoryService.search_subcategory_by_name(query)
        results = [{'nama_subkategori': subcategory['subcategory_name']} for subcategory in search_results]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

def show_subkategori(request, subcategory_id):
    subcategory_data = CategoryAndSubcategoryService.get_subcategory_details(subcategory_id)

    category_id = subcategory_data['category_id']
    subcategory_id = subcategory_data['subcategory_id']
    category_name = subcategory_data['nama_kategori']
    subcategory_name = subcategory_data['nama_subkategori']
    subcategory_description = subcategory_data['deskripsi']

    workers = []
    sessions = []
    testimonies = []
    workers = CategoryAndSubcategoryService.get_workers_by_category(category_id)
    sessions = CategoryAndSubcategoryService.get_sessions_by_subcategory(subcategory_id)
    payment_methods = OrderService.get_payment_method_details()

    pekerja_sudah_bergabung = False
    if request.user['is_pengguna'] == False :
        for worker in workers:
            if worker['pekerja_id'] == request.user['id']: 
                pekerja_sudah_bergabung = True
                break

    current_date_no_formatting = datetime.now()
    current_date = datetime.now().strftime('%Y-%m-%d')

    context = {
        'category_name': category_name,
        'subcategory_name': subcategory_name,
        'subcategory_id' : subcategory_id,
        'subcategory_description': subcategory_description,
        'workers': workers,
        'sessions' : sessions,
        'testimonies' : testimonies,
        'pekerja_bergabung' : pekerja_sudah_bergabung,
        'payment_methods' : payment_methods,
        'current_date' : current_date,
        'current_date_no_formatting' : current_date_no_formatting
    }


    return render(request, "subkategori.html", context)

def join_category(request, subcategory_id):
    if request.method == 'POST' :
        subcategory_data = CategoryAndSubcategoryService.get_subcategory_details(subcategory_id)
        category_id = subcategory_data['category_id']
        worker_id = request.user['id']

        CategoryAndSubcategoryService.add_worker_to_category(worker_id, category_id)

        subcategory_data = CategoryAndSubcategoryService.get_subcategory_details(subcategory_id)

        category_id = subcategory_data['category_id']
        subcategory_id = subcategory_data['subcategory_id']
        category_name = subcategory_data['nama_kategori']
        subcategory_name = subcategory_data['nama_subkategori']
        subcategory_description = subcategory_data['deskripsi']

        workers = []
        sessions = []
        testimonies = []
        workers = CategoryAndSubcategoryService.get_workers_by_category(category_id)
        sessions = CategoryAndSubcategoryService.get_sessions_by_subcategory(subcategory_id)


        pekerja_sudah_bergabung = False
        if request.user['is_pengguna'] == False :
            for worker in workers:
                if worker['pekerja_id'] == request.user['id']: 
                    pekerja_sudah_bergabung = True
                    break
        
        context = {
            'category_name': category_name,
            'subcategory_name': subcategory_name,
            'subcategory_id' : subcategory_id,
            'subcategory_description': subcategory_description,
            'workers': workers,
            'sessions' : sessions,
            'testimonies' : testimonies,
            'pekerja_bergabung' : pekerja_sudah_bergabung,
        }

        return render(request, 'subkategori.html', context)

def create_order(request):
    if request.method == 'POST':
        order_id = uuid.uuid4()
        subcategory_id = request.POST.get('subcategory_id')
        session_name = request.POST.get('session_name')
        session_price = float(request.POST.get('session_price'))
        diskon = request.POST.get('diskon')
        metode_bayar = request.POST.get('metode_bayar')
        tanggal_pemesanan = request.POST.get('tanggal_pemesanan')
        pelanggan_id = request.user['id']

        message = None
        if diskon:
            valid_diskon = OrderService.check_discount_code(diskon,pelanggan_id)
            if not valid_diskon or float(valid_diskon['min_tr_pemesanan']) > session_price:
                messages.error(request, "Kode diskon yang Anda masukkan tidak valid atau tidak memenuhi syarat minimal transaksi.")
                return redirect("service:show_subkategori", subcategory_id=subcategory_id)
            else:
                if valid_diskon['tipe_diskon'] == "VOUCHER":
                    try:
                        OrderService.mark_voucher_as_used(valid_diskon['kode'], pelanggan_id)
                    except:
                        messages.error(request, "Voucher telah melewati batas jumlah penggunaan atau batasan hari berlaku.")
                        return redirect("service:show_subkategori", subcategory_id=subcategory_id)
                else:
                    valid_promo = OrderService.check_promo_again(valid_diskon['kode'])
                    if not valid_promo:
                        messages.error(request, "Promo sudah melewati tanggal akhir berlaku")
                        return redirect("service:show_subkategori", subcategory_id=subcategory_id)
                    

                session_price -= float(valid_diskon['potongan'])
        
        if metode_bayar == "Pilih Metode Pembayaran...":
            messages.error(request, "Pilih metode pembayaran anda")
            return redirect("service:show_subkategori", subcategory_id=subcategory_id)
        
        OrderService.create_order(order_id, 
                                tanggal_pemesanan, 
                                session_price, 
                                pelanggan_id, 
                                subcategory_id,
                                session_name,
                                diskon,
                                metode_bayar)
        
        if OrderService.get_payment_method_name(metode_bayar) == "MyPay":
            status_name = "Menunggu Pembayaran"
        else:
            status_name = "Mencari Pekerja Terdekat"
        
        status_id = OrderService.get_status_id_by_name(status_name)

        tgl_waktu =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(status_id)
        OrderService.add_order_status(order_id,
                                      status_id,
                                      tgl_waktu
                                      )
        
        return redirect("service:show_booking_view")


def show_booking_view(request):
    customer_id = request.user['id']

    subkategori_filter = request.POST.get('filter-subkategori')
    status_filter = request.POST.get('filter-status')

    pesanan_list = OrderService.get_booking_view(customer_id)

    subkategori_options = sorted(set(pesanan['subkategori'] for pesanan in pesanan_list))
    status_options = sorted(set(pesanan['status'] for pesanan in pesanan_list))

    if subkategori_filter and subkategori_filter != "Pilih Subkategori":
        pesanan_list = [pesanan for pesanan in pesanan_list if pesanan['subkategori'] == subkategori_filter]

    if status_filter and status_filter != "Pilih Status Pesanan":
        pesanan_list = [pesanan for pesanan in pesanan_list if pesanan['status'] == status_filter]

    for pesanan in pesanan_list:
        pesanan['harga'] = "Rp {:,.0f}".format(pesanan['harga'])

    context = {
        "user": request.user,
        "pesanan_list": pesanan_list,
        "subkategori_filter": subkategori_filter,
        "status_filter": status_filter,
        "subkategori_options": subkategori_options,
        "status_options": status_options
    }

    return render(request, "booking_view.html", context)

def cancel_booking(request):
    if request.method == 'POST':
        id_pemesanan = request.POST.get('pesanan_id')
        OrderService.delete_order(id_pemesanan)
        return redirect('service:show_booking_view')


