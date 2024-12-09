import datetime
import uuid
from db.utils.query_helpers import execute_query, fetch_dict_all, fetch_dict_one

class OrderService:
    
    def get_payment_method_details():
        sql = """
        SELECT 
            id, 
            nama 
        FROM SIJARTA.METODE_BAYAR;
        """
        return fetch_dict_all(sql)
    @staticmethod
    def get_booking_view(user_id):
        sql = """
        SELECT 
            tpj.id AS id_pemesanan,
            sb.nama_subkategori AS subkategori,
            sj.sesi AS sesi_layanan,
            tpj.total_biaya AS harga,
            u.nama AS nama_pekerja,
            sp.status AS status
        FROM sijarta.tr_pemesanan_jasa tpj
        JOIN sijarta.sesi_layanan sj ON tpj.id_kategori_jasa = sj.subkategori_id AND tpj.sesi = sj.sesi
        JOIN sijarta.tr_pemesanan_status tps ON tpj.id = tps.id_tr_pemesanan
        JOIN sijarta.status_pesanan sp ON tps.id_status = sp.id
        LEFT JOIN sijarta.pekerja p ON tpj.id_pekerja = p.id
        LEFT JOIN sijarta.user u ON p.id = u.id  
        LEFT JOIN sijarta.subkategori_jasa sb ON sb.id = tpj.id_kategori_jasa
        WHERE tpj.id_pelanggan = %s;
        """
        return fetch_dict_all(sql, [user_id])
    
    @staticmethod
    def check_discount_code(discount_code, user_id):
        sql_promo = """
        SELECT 
            D.kode, 
            D.potongan, 
            D.min_tr_pemesanan,
            'PROMO' AS tipe_diskon
        FROM SIJARTA.DISKON D
        JOIN SIJARTA.PROMO P ON D.kode = P.kode
        WHERE D.kode = %s
        """

        sql_voucher = """
        SELECT 
            D.kode, 
            D.potongan, 
            D.min_tr_pemesanan, 
            'VOUCHER' AS tipe_diskon
        FROM SIJARTA.DISKON D
        JOIN SIJARTA.VOUCHER V ON D.kode = V.kode
        JOIN SIJARTA.TR_PEMBELIAN_VOUCHER TPV ON V.kode = TPV.id_voucher
        WHERE TPV.id_pelanggan = %s
        AND D.kode = %s;
        """

        promo_result = fetch_dict_one(sql_promo, [discount_code])
        if promo_result:
            return promo_result 
        
        voucher_result = fetch_dict_one(sql_voucher, [user_id, discount_code])
        if voucher_result:
            return voucher_result 
        
        return None
    
    @staticmethod
    def create_order(order_id, tgl_pemesanan, total_biaya, id_pelanggan, id_kategori_jasa, sesi, id_diskon, id_metode_bayar):
        if id_diskon:
            sql = """
                INSERT INTO SIJARTA.TR_PEMESANAN_JASA (id, tgl_pemesanan, total_biaya, 
                                                        id_pelanggan, id_kategori_jasa, sesi, id_diskon, id_metode_bayar)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """
            values = [order_id, tgl_pemesanan, total_biaya, id_pelanggan, id_kategori_jasa, sesi, id_diskon, id_metode_bayar]
        else:
            sql = """
                INSERT INTO SIJARTA.TR_PEMESANAN_JASA (id, tgl_pemesanan, total_biaya, 
                                                        id_pelanggan, id_kategori_jasa, sesi, id_metode_bayar)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
            values = [order_id, tgl_pemesanan, total_biaya, id_pelanggan, id_kategori_jasa, sesi, id_metode_bayar]

        execute_query(sql, values)
    
    @staticmethod
    def get_payment_method_name(id_metode_bayar) :
        sql = """
        SELECT nama
        FROM SIJARTA.METODE_BAYAR
        WHERE id = %s;
        """

        result = fetch_dict_one(sql, [id_metode_bayar])
        
        if result:
            return result['nama']
    
    @staticmethod
    def get_status_id_by_name(status_name):
        sql = """
        SELECT id 
        FROM SIJARTA.STATUS_PESANAN
        WHERE status = %s;
        """

        result = fetch_dict_one(sql, [status_name])

        if result:
            return result['id']
        return None
    
    @staticmethod
    def add_order_status(order_id, status_id, tgl_waktu) :
        sql = """
        INSERT INTO SIJARTA.TR_PEMESANAN_STATUS (id_tr_pemesanan, id_status, tgl_waktu)
            VALUES (%s, %s, %s)
        """
        values = [order_id, status_id, tgl_waktu]

        execute_query(sql, values)

    @staticmethod
    def delete_order(id_pemesanan):
        sql_delete_status = """
        DELETE FROM SIJARTA.TR_PEMESANAN_STATUS
        WHERE id_tr_pemesanan = %s;
        """
        execute_query(sql_delete_status, [id_pemesanan])

        sql_delete_jasa = """
        DELETE FROM SIJARTA.TR_PEMESANAN_JASA
        WHERE id = %s;
        """
        execute_query(sql_delete_jasa, [id_pemesanan])
    
    @staticmethod
    def mark_voucher_as_used(kode_voucher, id_pelanggan):
        sql = """
        UPDATE SIJARTA.TR_PEMBELIAN_VOUCHER
        SET telah_digunakan = telah_digunakan + 1
        WHERE id_voucher = %s
        AND id_pelanggan = %s;
        """
        execute_query(sql, [kode_voucher, id_pelanggan])
    
    def check_promo_again(kode_voucher):
        sql_promo = """
        SELECT 
            D.kode, 
            D.potongan, 
            D.min_tr_pemesanan,
            'PROMO' AS tipe_diskon
        FROM SIJARTA.DISKON D
        JOIN SIJARTA.PROMO P ON D.kode = P.kode
        WHERE D.kode = %s
        AND P.tgl_akhir_berlaku >= CURRENT_DATE
        """

        promo_result = fetch_dict_one(sql_promo, [kode_voucher])
        if promo_result:
            return promo_result 
        
        return None
