from datetime import date, datetime, timedelta
from db.utils.query_helpers import execute_query, fetch_dict_all, fetch_dict_one

class PekerjaJasaService:
    TR_PEMESANAN_JASA_FIELDS = """
    pj.id as id,
    pj.tgl_pemesanan as tanggal_pemesanan,
    pj.tgl_pekerjaan as tanggal_pekerjaan,
    pj.waktu_pekerjaan as waktu_pekerjaan,
    pj.total_biaya as total_biaya,
    pj.id_pelanggan as id_pelanggan,
    pj.id_pekerja as id_pekerja,
    pj.id_kategori_jasa as id_kategori_jasa,
    pj.sesi as sesi,
    pj.id_diskon as id_diskon,
    pj.id_metode_bayar as metode_bayar,
    u.nama as nama_pelanggan,
    s.status as status,
    ps.id_status as id_status,
    sub.nama_subkategori as nama_subkategori,
    kj.nama_kategori as nama_kategori
    """

    @staticmethod
    def get_tr_pemesanan_jasa_by_pekerja(pekerja_id : str, match = None, status = None) -> dict:
        '''Gets pemesanan jasa by id pekerja'''
        where_clause =  "pj.id_pekerja = %s"
        param = [pekerja_id]

        if match :
            match += "%"
            where_clause +=  " AND sub.nama_subkategori LIKE %s"
            param.append(match)
        
        if status :
            where_clause += " AND s.id = %s"
            param.append(status)
        
        sql = f"""
        SELECT
            {PekerjaJasaService.TR_PEMESANAN_JASA_FIELDS}
        FROM sijarta.tr_pemesanan_jasa pj 
            JOIN sijarta.tr_pemesanan_status ps ON(pj.id = ps.id_tr_pemesanan)
            JOIN sijarta.status_pesanan s ON(ps.id_status = s.id)
            JOIN sijarta.user u ON(pj.id_pelanggan = u.id)
            JOIN sijarta.subkategori_jasa sub ON(pj.id_kategori_jasa = sub.id)
            JOIN sijarta.kategori_jasa kj ON(kj.id = sub.kategori_jasa_id)
        WHERE {where_clause} ORDER BY s.id;
        """


        result = fetch_dict_all(sql,param)
        if not result:
            return None
        return result
    
    @staticmethod
    def get_tr_pemesanan_jasa_by_id(id : str) -> dict:
        '''Gets pemesanan jasa by id'''
        sql = f"""
        SELECT
            {PekerjaJasaService.TR_PEMESANAN_JASA_FIELDS}
        FROM sijarta.tr_pemesanan_jasa pj 
            JOIN sijarta.tr_pemesanan_status ps ON(pj.id = ps.id_tr_pemesanan)
            JOIN sijarta.status_pesanan s ON(ps.id_status = s.id)
            JOIN sijarta.user u ON(pj.id_pelanggan = u.id)
            JOIN sijarta.subkategori_jasa sub ON(pj.id_kategori_jasa = sub.id)
            JOIN sijarta.kategori_jasa kj ON(kj.id = sub.kategori_jasa_id)
        WHERE pj.id = %s;
        """

        result = fetch_dict_one(sql,[id])
        if not result:
            return None
        return result
    
    @staticmethod
    def update_status(id_transaksi : str) :
        """Updates status pemesanan"""
        transaksi = PekerjaJasaService.get_tr_pemesanan_jasa_by_id(id_transaksi)
        next_status = PekerjaJasaService.status_cycle(transaksi["id_status"])
        time_stamp = datetime.now()
        
        sql = f"""
            UPDATE sijarta.tr_pemesanan_status
            SET id_status = %s,
                tgl_waktu = %s
            WHERE id_tr_pemesanan = %s;
            """
        
        execute_query(
            sql,[next_status, time_stamp, id_transaksi]
        )


    @staticmethod
    def status_cycle(id_status : str) :
        """Decides which status should be the next based on previous status"""

        mencari_pekerja_terdekat = str(PekerjaJasaService.get_id_by_status("Mencari Pekerja Terdekat"))
        pekerja_dalam_perjalanan = str(PekerjaJasaService.get_id_by_status("Pekerja Dalam Perjalanan"))
        pekerjaan_dimulai = str(PekerjaJasaService.get_id_by_status("Pekerjaan Dimulai"))
        pekerjaan_selesai = str(PekerjaJasaService.get_id_by_status("Pekerjaan Selesai"))

        if str(id_status) == mencari_pekerja_terdekat :
            return pekerja_dalam_perjalanan
        
        if str(id_status) == pekerja_dalam_perjalanan :
            return pekerjaan_dimulai
        
        if str(id_status) == pekerjaan_dimulai :
            return pekerjaan_selesai
        
        return mencari_pekerja_terdekat # sebenernya impossible untuk sampe ke state ini
                                        # karena udah dihandle di view dan template.
                                        # gw balikin ke mencari_pekerja_terdekat karena
                                        # biar ga null aja (atau mendingan null ?)
    
    @staticmethod
    def get_id_by_status(nama : str) -> str :
        """Fetches the order status ID based on the given status name from the database."""
        sql = f"""
        SELECT id FROM sijarta.status_pesanan
        WHERE status LIKE %s;
        """

        result = fetch_dict_one(sql, [nama])
        return str(result['id'])
    

    @staticmethod
    def get_statuses_for_pekerja() -> dict :
        """Fetches all statuses"""
        sql = f"""
        SELECT * FROM sijarta.status_pesanan
        WHERE status NOT IN ('Menunggu Pembayaran','Mencari Pekerja Terdekat','Dibatalkan');
        """

        result = fetch_dict_all(sql)
        return result
    
    @staticmethod
    def get_pesanan_with_no_pekerja(uid: str, kategori = None, subkategori = None) -> dict :
        """Get all available pesanan"""
        today = date.today()
        param = [uid]

        where_clause = """
            pj.id_pekerja IS NULL 
            AND 
            pj.id_kategori_jasa IN 
            (SELECT sub.id FROM sijarta.subkategori_jasa sub 
                JOIN sijarta.pekerja_kategori_jasa pcat ON(pcat.kategori_jasa_id = sub.kategori_jasa_id)
                WHERE pcat.pekerja_id = %s
                )
        """

        if kategori :
            where_clause += " AND kj.nama_kategori = %s "
            param.append(kategori)
        
        if subkategori :
            where_clause += " AND sub.nama_subkategori = %s " 
            param.append(subkategori)


        sql = f"""
        SELECT
            {PekerjaJasaService.TR_PEMESANAN_JASA_FIELDS}
        FROM sijarta.tr_pemesanan_jasa pj 
            JOIN sijarta.tr_pemesanan_status ps ON(pj.id = ps.id_tr_pemesanan)
            JOIN sijarta.status_pesanan s ON(ps.id_status = s.id)
            JOIN sijarta.user u ON(pj.id_pelanggan = u.id)
            JOIN sijarta.subkategori_jasa sub ON(pj.id_kategori_jasa = sub.id)
            JOIN sijarta.kategori_jasa kj ON(kj.id = sub.kategori_jasa_id)
        WHERE {where_clause};
        """

        result = fetch_dict_all(sql,param)
        return result
    
    @staticmethod
    def kerjakan_pekerjaan(uid : str ,id_pemesanan : str) :
        """
        Dipanggil ketika pekerja mengambil pesanan yang belum ada pekerjanya.
        Ubah id_pekerja, tgl_pekerjaan, waktu_pekerjaan untuk baris yang bersesuaian.
        tgl_pekerjaan = tanggal ketika pekerja menekan tombol "Kerjakan pekerjaan"
        waktU_pekerjaan = tgl_pekerjaan + sesi (1 sesi jadi 1 hari)

        Setelah update statusnya dari yang sebelumnya "mencari pekerja terdekat" menjadi
        "Pekerja dalam perjalanan"
        """

        next_status = PekerjaJasaService.get_id_by_status("Pekerja Dalam Perjalanan")
        kerjaan = PekerjaJasaService.get_tr_pemesanan_jasa_by_id(id_pemesanan)
        sesi = int(kerjaan['sesi'])
        
        today = date.today()
        waktu_pekerjaan = datetime.today() + timedelta(days=sesi)

        sql = f"""
            UPDATE sijarta.tr_pemesanan_jasa 
            SET id_pekerja = %s,
                tgl_pekerjaan = %s,
                waktu_pekerjaan = %s
            WHERE id = %s;

            UPDATE sijarta.tr_pemesanan_status
            SET id_status = %s
            WHERE id_tr_pemesanan = %s;
            """
        execute_query(sql, [uid,today,waktu_pekerjaan, id_pemesanan, next_status, id_pemesanan])

    @staticmethod
    def get_kategori_pekerjaan(uid : str) -> dict :
        """Return key value <Kategori, [Subkategori]>"""
        
        fields = """
                kj.id AS id_kategori,
                kj.nama_kategori AS nama_kategori,
                sub.id AS id_subkategori,
                sub.nama_subkategori AS nama_subkategori,
                sub.kategori_jasa_id,
                pk.pekerja_id AS id_pekerja,
                pk.kategori_jasa_id AS kategori_jasa_id
                """
        
        sql = f"""
            SELECT {fields} FROM sijarta.pekerja_kategori_jasa pk
                JOIN sijarta.kategori_jasa KJ ON (KJ.id = pk.kategori_jasa_id)
                JOIN sijarta.subkategori_jasa sub ON (sub.kategori_jasa_id = pk.kategori_jasa_id)
            WHERE pk.pekerja_id = %s;
            """
        
        result = fetch_dict_all(sql, [uid])
        return result

    @staticmethod
    def to_key_list(mydict : list) -> dict :
        """
        Method helper untuk get_kategori_pekerjaan()
        Berfungsi untuk memproses list yang ada di param (list of dicts) menghasilkan pasangan
        <nama_kategori,[sub_kategori]>.
        Jadi kita bisa ngambil list subkategori dengan key kategori.
        """

        new_dict = {}
        for dict in mydict :
            if not new_dict.get(dict["nama_kategori"]):
                new_dict[dict["nama_kategori"]] = []
            new_dict[dict["nama_kategori"]].append((dict["nama_subkategori"], dict["id_subkategori"]))
        
        return new_dict
    