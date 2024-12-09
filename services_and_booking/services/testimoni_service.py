from db.utils.query_helpers import execute_query, fetch_dict_all, fetch_dict_one

class TestimoniService:
    @staticmethod
    def get_all_testimoni(id_subkategori):
        sql = """
        SELECT 
            T.id_tr_pemesanan, 
            T.tgl, 
            T.teks, 
            T.rating,
            P.id AS id_pelanggan, 
            U.nama AS nama_pelanggan, 
            W.nama AS nama_pekerja,
            TR.id_kategori_jasa AS id_subkategori
        FROM 
            sijarta.testimoni T
        JOIN 
            sijarta.tr_pemesanan_jasa TR ON TR.id = T.id_tr_pemesanan
        JOIN 
            sijarta.pelanggan P ON P.id = TR.id_pelanggan
        JOIN 
            sijarta.user U ON U.id = P.id
        JOIN 
            sijarta.pekerja Pekerja ON Pekerja.id = TR.id_pekerja
        JOIN 
            sijarta.user W ON W.id = Pekerja.id
        WHERE 
            TR.id_kategori_jasa = %s;
        """
        return fetch_dict_all(sql, [id_subkategori])
    
    @staticmethod
    def check_valid_for_testimoni(id_tr_pemesanan):
        sql = """
        SELECT s.status 
        FROM sijarta.tr_pemesanan_jasa trj
        JOIN sijarta.tr_pemesanan_status trs ON trs.id_tr_pemesanan = trj.id
        JOIN sijarta.status_pesanan s ON trs.id_status = s.id
        WHERE trj.id = %s AND s.status = 'Pesanan Selesai';
        """
        result = fetch_dict_one(sql, [id_tr_pemesanan])
        return result['status'] if result else None
    
    @staticmethod
    def create_testimoni(id_tr_pemesanan, teks, rating):
        insert_testimoni_sql = """
        INSERT INTO sijarta.testimoni (id_tr_pemesanan, tgl, teks, rating)
        VALUES (%s, CURRENT_DATE, %s, %s);
        """
        execute_query(insert_testimoni_sql, [id_tr_pemesanan, teks, rating])

    @staticmethod
    def check_existing_testimoni(id_tr_pemesanan):
        # Fungsi untuk memeriksa apakah testimoni sudah ada untuk pemesanan ini
        check_existing_sql = """
        SELECT 1 FROM sijarta.testimoni WHERE id_tr_pemesanan = %s AND tgl = CURRENT_DATE;
        """
        result = fetch_dict_one(check_existing_sql, [id_tr_pemesanan])
        return result is not None  # Mengembalikan True jika testimoni sudah ada, False jika belum
    
    @staticmethod
    def delete_testimoni(id_tr_pemesanan):
        delete_sql = """
        DELETE FROM sijarta.testimoni WHERE id_tr_pemesanan = %s;
        """
        execute_query(delete_sql, [id_tr_pemesanan])
