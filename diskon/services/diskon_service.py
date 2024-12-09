from db.utils.query_helpers import execute_query, fetch_dict_all, fetch_dict_one

class DiscountService:
    @staticmethod
    def get_all_vouchers():
        sql = """
        SELECT V.kode, D.potongan, D.min_tr_pemesanan, V.jml_hari_berlaku, V.kuota_penggunaan, V.harga 
        FROM sijarta.voucher V, sijarta.diskon D
        WHERE V.kode = D.kode;
        """
        return fetch_dict_all(sql)
    
    @staticmethod
    def get_all_promo():
        sql = """
        SELECT P.kode, P.tgl_akhir_berlaku
        FROM sijarta.promo P, sijarta.diskon D
        WHERE P.kode = D.kode;
        """
        return fetch_dict_all(sql)
    @staticmethod
    def get_id_category_voucher(nama_kategori):
        sql = """
        SELECT id
        FROM sijarta.kategori_tr_mypay 
        WHERE nama = %s;
        """
        result = fetch_dict_one(sql, [nama_kategori])
        return result['id'] if result else 0
    
    @staticmethod
    def get_metode_bayar(id):
        sql = """
        SELECT nama
        FROM sijarta.metode_bayar
        WHERE id = %s;
        """
        result = fetch_dict_one(sql, [id])
        return result['nama'] if result else 0
    
    @staticmethod
    def get_all_metode_bayar():
        sql = """
        SELECT *
        FROM sijarta.metode_bayar M;
        """
        return fetch_dict_all(sql)
    
    @staticmethod
    def check_saldo_mypay(user_id):
        # Cek saldo MyPay berdasarkan ID pengguna
        sql = """
        SELECT saldo_mypay FROM sijarta.user WHERE id = %s;
        """
        result = fetch_dict_one(sql, [user_id])
        return result['saldo_mypay'] if result else 0
    @staticmethod
    def update_saldo_mypay(harga_voucher, user_id):
        # Update saldo MyPay pengguna setelah pembelian
        sql = """
        UPDATE sijarta.user
        SET saldo_mypay = saldo_mypay - %s
        WHERE id = %s
        """
        execute_query(sql, [harga_voucher, user_id])

    @staticmethod
    def record_voucher_purchase(id_transaksi_voucher, telah_digunakan, id_pelanggan, id_voucher, id_metode_bayar):
        insert_transaksi_sql = """
        INSERT INTO sijarta.tr_pembelian_voucher (id, tgl_awal, tgl_akhir, telah_digunakan, id_pelanggan, id_voucher, id_metode_bayar)
        VALUES (%s, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day' * (SELECT jml_hari_berlaku FROM sijarta.voucher WHERE kode = %s), %s, %s, %s, %s);
        """
        execute_query(insert_transaksi_sql, [id_transaksi_voucher, id_voucher, telah_digunakan, id_pelanggan, id_voucher, id_metode_bayar])
    
    @staticmethod
    def record_mypay_purchase(id_tr_mypay, user_id, nominal, id_kategori):
        insert_transaksi_mypay_sql = """
        INSERT INTO sijarta.tr_mypay (id, user_id, tgl, nominal, kategori_id)
        VALUES (%s, %s, CURRENT_DATE, %s, %s);
        """
        execute_query(insert_transaksi_mypay_sql, [id_tr_mypay, user_id, nominal, id_kategori])